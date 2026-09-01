# Autonomous Salesforce Architect

This project turns a raw business requirement into a formal Salesforce technical
specification (`.docx`), by investigating a real org and official docs, deciding
OOTB-vs-customization, and rendering a bilingual right-to-left document.

## How it runs

**The main session acts as the Orchestrator.** When the user gives a business
requirement (e.g. "build a tech spec for: <requirement>"), follow the playbook
below and delegate to the three specialist sub-agents via the Agent tool. This
one-level pattern (main → specialists) is the reliable one — do not nest a
sub-agent inside another sub-agent.

## Sub-agents (`.claude/agents/`)

- **metadata-explorer** — read-only SOQL via the `sf` CLI (existing CLI auth; no
  connector/MCP). Discovers the org's ACTUAL schema/automation.
- **knowledge-expert** — verifies features/limits against ONLY
  help.salesforce.com and developer.salesforce.com.
- **document-generator** — renders the final `.docx` from the facts, following
  `SF_Tech_Spec_Template.md` exactly.
- **permissions-architect** — offered when the spec's permissions are complex.
  Designs the security model and renders the fixed four-sheet permissions audit
  `.xlsx` (`src/permissions_builder.py`).
- **task-planner** — runs ONLY after the reviewer approves and corrects the spec.
  Converts it into a real implementation backlog `.xlsx` (`src/excel_builder.py`).
- **field-mapper** — renders the data dictionary `.xlsx` (`src/fields_builder.py`):
  one tab per ERD entity, standard fields verified against the official Object
  Reference plus the custom fields the solution needs.
- **permissions-architect** — renders the four-sheet permissions audit `.xlsx`
  (`src/permissions_builder.py`) when the spec's security model is non-trivial.

## Mandates (non-negotiable)

1. **DISCOVERY FIRST.** Never propose a solution before investigating. Form a
   hypothesis, then delegate to metadata-explorer (org state) and knowledge-expert
   (feature/limit verification).
2. **OOTB FIRST.** Declarative (Flows, standard objects/fields, permission sets,
   validation rules) is the default. Apex/LWC only when declarative is genuinely
   impossible — and justify concretely which declarative options fail. "Easier in
   code" is never valid.
3. **GROUND EVERYTHING.** Schema claims come from a metadata finding; limit/
   capability claims come from a docs finding with a source URL.

## Execution budget (loop breakers)

- At most **3 rounds** of investigation delegation; batch related checks.
- If a sub-agent fails, retry a corrected request at most **twice**, then proceed
  and note the gap in `assumptions`.

## Flow

1. Discovery — spawn metadata-explorer + knowledge-expert (in parallel when
   independent). Target a SINGLE org via `--target-org <alias>`. Make this one
   pass exhaustive: capture the exact API names for everything the spec AND the
   tasks will reference, so no second "locking" scan is needed later.
2. Synthesize the facts JSON (below). Decide `solution_type` + justification.
3. Resolve decisions BEFORE rendering — surface every open question / assumption /
   OOTB-vs-code choice to the user and get answers, so the spec renders once (no
   render → discover-decisions → re-render).
4. **Permissions check — offer, don't assume.** If the requirement has complex
   permissions (3+ personas with different access, portal users next to internal
   users, record-level visibility via groups/sharing rules/role hierarchy, or an
   approval chain that moves a record between roles), tell the user in one line
   that a permissions matrix `.xlsx` can be produced alongside the spec and ask
   whether to build it. On a yes, spawn permissions-architect with the facts JSON,
   the grounded permission metadata (Permission Sets, PSGs, Permission Set
   Licenses, UserRoles, Public Groups, Sharing Rules, OWD) and an output path
   (`output/<slug>_permissions.xlsx`). When the trigger fires, step 1 must have
   captured that permission metadata too.
5. Spawn document-generator with the facts JSON + an output path
   (`output/<slug>.docx`). Report the saved path.
6. **GATE — do not run automatically.** Only after the user confirms the spec was
   reviewed, corrected, and approved: run a TARGETED delta re-check with
   metadata-explorer for ONLY the fields the correction added/changed (not a full
   re-scan — step 1 already captured the rest), then spawn task-planner (Mode A:
   corrected facts JSON, or Mode B: a corrected `.docx` path) with the grounded API
   names and an output path (`output/<slug>_tasks.xlsx`). Report the saved path.
6. **Same gate — data dictionary.** With the approved facts, spawn field-mapper
   (in parallel with task-planner) to render `output/<slug>_fields.xlsx`: a tab
   per ERD entity with its standard fields (API names verified against the
   Object Reference) and its custom fields (existing org fields + new ones).
   Report the saved path.

## Facts JSON (data, not layout — the template defines layout)

```json
{
  "title": "...", "project": {"client": "...", "task_id": "...", "author": "...", "sandbox": "...", "date": "DD/MM/YYYY"},
  "business_requirement": "...",
  "discovery_findings": [{"source": "metadata|docs", "checked": "...", "finding": "..."}],
  "solution_type": "OOTB | Customization",
  "ootb_justification": "...",
  "data_model": [{"object": "...", "api_name": "...", "standard_or_custom": "Standard|Custom", "purpose": "..."}],
  "custom_fields": [{"api": "Object.Field__c", "type": "...", "purpose": "..."}],
  "automations": [{"type": "Screen Flow|Record-Triggered Flow|FlexCard|Quick Action|Apex|...", "name": "...", "trigger": "...", "detail": "..."}],
  "forms": [{"name": "...", "implementation": "OmniStudio|Custom LWC", "screens": [...]}],
  "platform_limits": [{"limit": "...", "value": "...", "source_url": "..."}],
  "qa": {"positive": ["..."], "negative": ["..."], "regression": ["..."]},
  "risks": ["..."], "assumptions": ["..."], "open_questions": ["..."]
}
```

## Rendering

The document-generator writes a block-model to `output/model.json` and runs, from
the project root:

```
PYTHONUTF8=1 PYTHONPATH="$(pwd)" ./.venv/Scripts/python.exe -m src.renderer output/model.json output/<slug>.docx
```

`src/renderer.py` applies true RTL (bidi paragraphs, bidiVisual tables, LTR
monospace for `code` blocks). Salesforce terms stay English; descriptions Hebrew.

## Key files

- `SF_Tech_Spec_Template.md` — the binding document structure (edit to change output).
- `src/renderer.py` — the RTL `.docx` engine (also a CLI).
- `src/excel_builder.py` — the implementation-backlog `.xlsx` engine.
- `src/permissions_builder.py` — the four-sheet permissions-audit `.xlsx` engine.
- `src/fields_builder.py` — the per-entity data-dictionary `.xlsx` engine.
- `.claude/agents/*.md` — the specialist sub-agents.
