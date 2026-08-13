"""Central configuration and execution limits.

Every guardrail number lives here so the limits are auditable in one place and
cannot drift between the tools, the agents, and the graph.
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# --- Secrets / environment -------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
SF_TARGET_ORG = os.environ.get("SF_TARGET_ORG", "")

# --- Execution limits (Guardrail #2) ---------------------------------------

# Orchestrator: max reason/act loops per request.
ORCHESTRATOR_MAX_LOOPS = 3

# Every tool call may retry at most this many times AFTER the first attempt.
# Total attempts = 1 + TOOL_MAX_RETRIES.
TOOL_MAX_RETRIES = 2

# Backstop for the whole LangGraph run, passed as `recursion_limit` at invoke
# time. Sized above the orchestrator budget so the state-based loop breaker
# trips first and this only catches genuine runaway routing.
GRAPH_RECURSION_LIMIT = 15

# Max internal reason/act steps a sub-agent (Metadata Explorer) may take before
# it is forced to summarize. Its own strict iteration limit (Guardrail #2).
SUBAGENT_MAX_STEPS = 4

# --- Tool boundaries -------------------------------------------------------

# Hard allow-list for the Knowledge Expert. No other domain may ever be queried.
ALLOWED_DOC_DOMAINS = ("help.salesforce.com", "developer.salesforce.com")

# Seconds before a single `sf` CLI invocation is killed.
SF_CLI_TIMEOUT_SECONDS = 120

# Max web searches Claude may perform per Knowledge Expert call.
DOCS_MAX_SEARCHES = 3


def require_api_key() -> str:
    """Return the API key or fail loudly at the boundary."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return ANTHROPIC_API_KEY


def make_client() -> Anthropic:
    """Single source of truth for constructing the Anthropic client."""
    return Anthropic(api_key=require_api_key())
