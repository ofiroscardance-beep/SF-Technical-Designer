"""LangGraph wiring: state, nodes, edges, and the layered loop breakers.

Three independent limits (Guardrail #2):
  1. `loop_count` in state caps Orchestrator reason/act turns at ORCHESTRATOR_MAX_LOOPS.
  2. Each sub-agent has its own step budget (see subagents.py).
  3. `recursion_limit` at invoke time is the final backstop against runaway routing.
"""

import json
import re
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from src.config import (
    ANTHROPIC_MODEL,
    GRAPH_RECURSION_LIMIT,
    ORCHESTRATOR_MAX_LOOPS,
    make_client,
)
from src.prompts.orchestrator import ORCHESTRATOR_SYSTEM
from src.subagents import ORCHESTRATOR_TOOLS, dispatch_orchestrator_tool

_FINALIZE_SUFFIX = (
    "\n\n## Budget exhausted\nYou have used your full investigation budget. Do NOT "
    "request tools. Emit the final JSON now using the findings you already have."
)
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


class ArchitectState(TypedDict):
    requirement: str
    messages: list[dict]
    loop_count: int
    final_json: Optional[dict]
    error: Optional[str]


def _extract_json(text: str) -> tuple[Optional[dict], Optional[str]]:
    body = text.strip()
    fenced = _FENCE.search(body)
    if fenced:
        body = fenced.group(1).strip()
    start, end = body.find("{"), body.rfind("}")
    if start == -1 or end <= start:
        return None, f"no JSON object in orchestrator output: {text[:200]!r}"
    try:
        return json.loads(body[start : end + 1]), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON from orchestrator: {exc}"


def orchestrator_node(state: ArchitectState) -> dict:
    loop = state["loop_count"]
    over_budget = loop >= ORCHESTRATOR_MAX_LOOPS

    request = dict(
        model=ANTHROPIC_MODEL,
        max_tokens=2500,
        system=ORCHESTRATOR_SYSTEM + (_FINALIZE_SUFFIX if over_budget else ""),
        messages=state["messages"],
    )
    if not over_budget:
        request["tools"] = ORCHESTRATOR_TOOLS

    response = make_client().messages.create(**request)
    messages = state["messages"] + [{"role": "assistant", "content": response.content}]
    tool_uses = [b for b in response.content if getattr(b, "type", None) == "tool_use"]

    if tool_uses and not over_budget:
        return {"messages": messages, "loop_count": loop + 1}

    text = "\n".join(b.text for b in response.content if getattr(b, "type", None) == "text")
    final_json, error = _extract_json(text)
    return {"messages": messages, "loop_count": loop + 1, "final_json": final_json, "error": error}


def tools_node(state: ArchitectState) -> dict:
    last_content = state["messages"][-1]["content"]
    tool_uses = [b for b in last_content if getattr(b, "type", None) == "tool_use"]
    results = [
        {
            "type": "tool_result",
            "tool_use_id": tu.id,
            "content": dispatch_orchestrator_tool(tu.name, tu.input)[:8000],
        }
        for tu in tool_uses
    ]
    return {"messages": state["messages"] + [{"role": "user", "content": results}]}


def _route_after_orchestrator(state: ArchitectState) -> str:
    if state.get("final_json") is not None or state.get("error"):
        return "finish"
    return "tools"


def build_graph():
    graph = StateGraph(ArchitectState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("tools", tools_node)
    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator", _route_after_orchestrator, {"tools": "tools", "finish": END}
    )
    graph.add_edge("tools", "orchestrator")
    return graph.compile()


def run_architect(requirement: str) -> ArchitectState:
    """Run the full architect graph for one business requirement."""
    initial: ArchitectState = {
        "requirement": requirement,
        "messages": [{"role": "user", "content": requirement}],
        "loop_count": 0,
        "final_json": None,
        "error": None,
    }
    return build_graph().invoke(
        initial, config={"recursion_limit": GRAPH_RECURSION_LIMIT}
    )
