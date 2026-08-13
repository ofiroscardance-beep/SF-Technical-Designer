"""Uniform tool result envelope and retry boundary.

Tools never raise across their boundary. They return a ToolResult so the
Orchestrator can reason about failures as data instead of crashing the graph.
"""

from dataclasses import dataclass, field
from typing import Any, Callable

from src.config import TOOL_MAX_RETRIES


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    error: str = ""
    attempts: int = 1
    meta: dict = field(default_factory=dict)


def with_retries(
    operation: Callable[[], ToolResult],
    *,
    max_retries: int = TOOL_MAX_RETRIES,
    label: str = "tool",
) -> ToolResult:
    """Run `operation` up to (1 + max_retries) times, stopping on first success.

    `operation` must return a ToolResult and must not raise; any exception is
    caught here and folded into a failed ToolResult so the caller sees data,
    not a traceback.
    """
    last: ToolResult = ToolResult(ok=False, error=f"{label}: not attempted")
    total_attempts = 1 + max_retries

    for attempt in range(1, total_attempts + 1):
        try:
            result = operation()
        except Exception as exc:  # tool boundary: never propagate
            result = ToolResult(ok=False, error=f"{label}: {type(exc).__name__}: {exc}")

        result.attempts = attempt
        if result.ok:
            return result
        last = result

    last.error = f"{last.error} (gave up after {last.attempts} attempts)"
    return last
