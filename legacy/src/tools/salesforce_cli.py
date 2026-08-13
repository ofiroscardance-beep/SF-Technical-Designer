"""Metadata Explorer tool: a hardened wrapper around the Salesforce CLI.

Runs read-only SOQL (default via the Tooling API) against the connected org so
the Orchestrator can discover the org's actual state. All failures are returned
as ToolResult data; nothing raises across the boundary, and every call is
subject to the shared retry limit.
"""

import json
import re
import shutil
import subprocess

from src.config import SF_CLI_TIMEOUT_SECONDS, SF_TARGET_ORG
from src.tools.result import ToolResult, with_retries

# Defense-in-depth read-only guard. Scanned only after string literals are
# stripped, so DML words inside a WHERE literal (e.g. 'please update me') do not
# false-positive — no standard/custom SF API name is a reserved DML keyword.
_DML_KEYWORDS = re.compile(
    r"\b(insert|update|delete|upsert|undelete|merge)\b", re.IGNORECASE
)
_SOQL_STRING_LITERAL = re.compile(r"'(?:[^'\\]|\\.)*'")


def _validate_soql(soql: str) -> str:
    """Reject anything that isn't a single read-only SELECT.

    `sf data query` is a query-only endpoint; SELECT-prefix, a no-stacked-
    statements check (no `;`), and a DML-keyword scan (outside string literals)
    together keep this tool strictly read-only.
    """
    stripped = soql.strip()
    if not stripped:
        raise ValueError("empty SOQL query")
    if not stripped.lower().startswith("select"):
        raise ValueError("only SELECT queries are permitted")
    if ";" in stripped:
        raise ValueError("SOQL must be a single statement (no ';')")

    without_literals = _SOQL_STRING_LITERAL.sub("''", stripped)
    dml = _DML_KEYWORDS.search(without_literals)
    if dml:
        raise ValueError(f"forbidden DML keyword outside a literal: {dml.group(1)!r}")
    return stripped


def _run_sf(args: list[str]) -> ToolResult:
    """Invoke `sf` with a fixed argv list (never a shell string)."""
    exe = shutil.which("sf")
    if not exe:
        return ToolResult(ok=False, error="`sf` CLI not found on PATH")

    try:
        proc = subprocess.run(
            [exe, *args],
            capture_output=True,
            text=True,
            timeout=SF_CLI_TIMEOUT_SECONDS,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(
            ok=False, error=f"sf timed out after {SF_CLI_TIMEOUT_SECONDS}s"
        )

    # `sf ... --json` returns JSON on both success and failure.
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return ToolResult(
            ok=False,
            error=f"non-JSON output (exit {proc.returncode}): "
            f"{(proc.stderr or proc.stdout or '').strip()[:500]}",
        )

    if proc.returncode != 0 or payload.get("status", 0) != 0:
        message = payload.get("message") or payload.get("name")
        if not message:
            message = (proc.stderr or "").strip()[:500] or "unknown sf error"
        return ToolResult(ok=False, error=f"sf error: {message}")

    return ToolResult(ok=True, data=payload.get("result", payload))


def run_soql(soql: str, *, use_tooling_api: bool = True) -> ToolResult:
    """Run a read-only SOQL query against the target org.

    Tooling API is the default so metadata objects like EntityDefinition and
    FieldDefinition resolve correctly. Retries are bounded by the shared limit.
    """
    if not SF_TARGET_ORG:
        return ToolResult(ok=False, error="SF_TARGET_ORG is not set in the environment")

    try:
        query = _validate_soql(soql)
    except ValueError as exc:
        return ToolResult(ok=False, error=f"invalid SOQL: {exc}")

    args = [
        "data",
        "query",
        "--query",
        query,
        "--target-org",
        SF_TARGET_ORG,
        "--json",
    ]
    if use_tooling_api:
        args.append("--use-tooling-api")

    result = with_retries(lambda: _run_sf(args), label="sf data query")
    if result.ok and isinstance(result.data, dict):
        records = result.data.get("records", [])
        result.meta["record_count"] = len(records)
        result.data = records
    return result
