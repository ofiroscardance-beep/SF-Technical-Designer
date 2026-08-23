# sf-technical-designer (Claude Code plugin)

An autonomous Salesforce architect for Claude Code. Turns a business requirement
into a grounded technical specification (`.docx`) and, after human approval, an
implementation backlog (`.xlsx`). Discovery-first, OOTB-first, bilingual RTL
(Hebrew business logic, English Salesforce terminology).

## Install

From Claude Code, add the marketplace and install:

```
/plugin marketplace add ofiroscardance-beep/SF-Technical-Designer
/plugin install sf-technical-designer@sf-tools
```

(The marketplace repo is private — Claude Code uses your existing git
credentials, same as your terminal.)

## Prerequisites (each teammate, once)

- **Python 3** on `PATH` — the plugin creates its own venv on first run.
- **Salesforce CLI (`sf`)** installed and authenticated to your org. The
  metadata-explorer agent queries it read-only via `--target-org <alias>`.

On the first session after install, a SessionStart hook builds a persistent venv
(in the plugin's data dir) with `python-docx` + `openpyxl`. If it can't reach the
network, it prints the exact `pip install` command to run manually.

## Use

```
/sf-technical-designer:sf-tech-spec build a spec for: <your requirement>
```

The orchestrator runs discovery (metadata-explorer + knowledge-expert),
synthesizes the design, and renders the spec to `output/<slug>.docx`. Then it
**stops** — review and correct the spec. Only after you approve does it lock the
exact API names and generate the implementation backlog `output/<slug>_tasks.xlsx`.

## What's inside

| Component | Role |
| --------- | ---- |
| `agents/metadata-explorer.md` | Read-only org schema discovery via `sf`. |
| `agents/knowledge-expert.md` | Feature/limit verification against official SF docs. |
| `agents/document-generator.md` | Renders the spec `.docx` (`src/renderer.py`). |
| `agents/task-planner.md` | Renders the backlog `.xlsx` (`src/excel_builder.py`), gated on approval. |
| `commands/sf-tech-spec.md` | The orchestration entry point. |
| `hooks/` | SessionStart bootstrap: venv + engine paths. |
| `src/`, `SF_Tech_Spec_Template.md` | RTL render engines and the binding spec structure. |

## Notes

- Generated artifacts land in `output/` in whatever project you're working in.
- The venv lives in the plugin's persistent data dir, so it survives plugin
  updates. Update the plugin with `/plugin` (or a marketplace refresh).
