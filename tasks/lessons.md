# Lessons

## Clarify the agent RUNTIME before building (2026-08)

The brief said "multi-agent system in Python using LangGraph." We built the full
LangGraph app (Phases 1–4) — but the user actually wanted a **native Claude Code
agent with sub-agents** (`.claude/agents/`), not an external Python app and not a
single Skill.

**Why it happened:** "multi-agent" + "LangGraph" read as "external framework app."
**How to apply:** When a brief mentions agents/multi-agent, confirm the runtime
early — native Claude Code agents vs an external framework — before writing code.

## Reliable orchestration pattern

The **main session is the Orchestrator** and spawns the three specialist
sub-agents (one level: main → specialists). A sub-agent generally cannot spawn
its own sub-agents (nesting limit), so keep orchestration at the top level. The
Orchestrator playbook lives in `CLAUDE.md`.

Also: custom `.claude/agents/*.md` created mid-session are NOT available as
`subagent_type` until Claude Code is reloaded.

## Salesforce CLI specifics (Windows)

- Use the **existing `sf` CLI auth** via Bash — no connector/MCP/OAuth.
- On Windows/Git Bash, `sf data query --query "..."` breaks on quoting; use
  `--file <path.soql>` instead.
- `FieldDefinition` Tooling queries reject `OR` ("Disjunctions not supported") —
  split into separate queries or filter client-side.
