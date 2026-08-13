"""Sub-agents exposed to the Orchestrator as high-level tools.

- Metadata Explorer: a bounded reason/act loop over the read-only `run_soql`
  tool, with its own strict step limit (Guardrail #2).
- Knowledge Expert: wraps the domain-restricted `search_docs` tool.

Each returns a plain string the Orchestrator consumes as a tool result.
"""

import json

from src.config import ANTHROPIC_MODEL, SUBAGENT_MAX_STEPS, make_client
from src.prompts.metadata_explorer import METADATA_EXPLORER_SYSTEM
from src.tools.salesforce_cli import run_soql
from src.tools.salesforce_docs import search_docs

_RUN_SOQL_TOOL = {
    "name": "run_soql",
    "description": (
        "Run a single read-only SOQL SELECT against the target org. Uses the "
        "Tooling API by default for metadata objects (EntityDefinition, "
        "FieldDefinition, ...). Returns JSON records or an error string."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "soql": {"type": "string", "description": "A single read-only SELECT."},
            "use_tooling_api": {
                "type": "boolean",
                "description": "Query the Tooling API (default true).",
            },
        },
        "required": ["soql"],
    },
}


def _text_of(response) -> str:
    return "\n".join(
        b.text for b in response.content if getattr(b, "type", None) == "text"
    ).strip()


def _soql_tool_result(tool_use) -> dict:
    result = run_soql(
        tool_use.input.get("soql", ""),
        use_tooling_api=tool_use.input.get("use_tooling_api", True),
    )
    content = json.dumps(result.data)[:6000] if result.ok else f"ERROR: {result.error}"
    return {
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": content,
        "is_error": not result.ok,
    }


def run_metadata_explorer(request: str) -> str:
    """Investigate the org's actual metadata within a strict step budget."""
    client = make_client()
    messages = [{"role": "user", "content": request}]

    for _ in range(SUBAGENT_MAX_STEPS):
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1500,
            system=METADATA_EXPLORER_SYSTEM,
            tools=[_RUN_SOQL_TOOL],
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        tool_uses = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            return _text_of(response)
        messages.append(
            {"role": "user", "content": [_soql_tool_result(tu) for tu in tool_uses]}
        )

    # Step budget exhausted: force a tool-free summary (finalize via system, so
    # message-role alternation stays valid).
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1000,
        system=METADATA_EXPLORER_SYSTEM
        + "\n\nStep budget exhausted. Summarize your metadata findings now as "
        "concise facts. Do not request more queries.",
        messages=messages,
    )
    return _text_of(response) or "(metadata explorer produced no findings)"


def run_knowledge_expert(question: str) -> str:
    """Verify a claim against official documentation."""
    result = search_docs(question)
    if not result.ok:
        return f"ERROR consulting documentation: {result.error}"
    citations = "\n".join(f"- {url}" for url in result.data["citations"])
    answer = result.data["answer"]
    return f"{answer}\n\nSources:\n{citations}" if citations else answer


ORCHESTRATOR_TOOLS = [
    {
        "name": "investigate_metadata",
        "description": (
            "Investigate the connected Salesforce org's ACTUAL schema/metadata to "
            "confirm or refute a discovery hypothesis. Describe in natural language "
            "what to check (objects, fields, automation)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"request": {"type": "string"}},
            "required": ["request"],
        },
    },
    {
        "name": "consult_documentation",
        "description": (
            "Verify a Salesforce feature, standard capability, or platform/governor "
            "limit against OFFICIAL documentation. Ask one specific question."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"],
        },
    },
]

_DISPATCH = {
    "investigate_metadata": lambda i: run_metadata_explorer(i.get("request", "")),
    "consult_documentation": lambda i: run_knowledge_expert(i.get("question", "")),
}


def dispatch_orchestrator_tool(name: str, tool_input: dict) -> str:
    handler = _DISPATCH.get(name)
    if handler is None:
        return f"ERROR: unknown tool {name!r}"
    return handler(tool_input)
