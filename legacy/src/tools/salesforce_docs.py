"""Knowledge Expert tool: documentation search restricted to official domains.

Uses the Anthropic server-side `web_search` tool with `allowed_domains`, so the
domain restriction is enforced at the API layer — Claude cannot return results
from anywhere other than the official Salesforce documentation sites. Retries
are bounded by the shared limit; failures return as ToolResult data.
"""

from anthropic import Anthropic

from src.config import ALLOWED_DOC_DOMAINS, ANTHROPIC_MODEL, DOCS_MAX_SEARCHES, make_client
from src.prompts.knowledge_expert import KNOWLEDGE_EXPERT_SYSTEM
from src.tools.result import ToolResult, with_retries


def _search_once(client: Anthropic, question: str) -> ToolResult:
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1500,
        system=KNOWLEDGE_EXPERT_SYSTEM,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": DOCS_MAX_SEARCHES,
                "allowed_domains": list(ALLOWED_DOC_DOMAINS),
            }
        ],
        messages=[{"role": "user", "content": question}],
    )

    text_parts: list[str] = []
    citations: list[str] = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)
            for citation in getattr(block, "citations", None) or []:
                url = getattr(citation, "url", None)
                if url:
                    citations.append(url)

    answer = "\n".join(part for part in text_parts if part).strip()
    if not answer:
        return ToolResult(ok=False, error="docs search returned no text answer")

    return ToolResult(
        ok=True,
        data={"answer": answer, "citations": sorted(set(citations))},
        meta={"stop_reason": response.stop_reason},
    )


def search_docs(question: str) -> ToolResult:
    """Answer a question strictly from official Salesforce documentation."""
    if not question.strip():
        return ToolResult(ok=False, error="empty documentation question")

    try:
        client = make_client()
    except RuntimeError as exc:
        return ToolResult(ok=False, error=str(exc))

    return with_retries(lambda: _search_once(client, question), label="docs search")
