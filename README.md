# SF Technical Designer

An autonomous Salesforce architect. It turns a raw business requirement into a
formal, grounded Salesforce **technical specification** (`.docx`), and — once a
human approves it — into a ready-to-execute **implementation backlog** (`.xlsx`).

Both documents are true right-to-left (RTL): business logic is written in Hebrew,
Salesforce terminology (Object/API/Flow/Apex/LWC names) stays in English.

## How it works

The main Claude Code session acts as the **orchestrator**. It never guesses — it
investigates a real org and the official docs, decides OOTB-vs-customization, and
delegates rendering to specialist sub-agents. Layout lives in the Python engines;
the sub-agents produce data (JSON) only.

```
business requirement
        │
        ▼
 ┌──────────────────────── discovery ────────────────────────┐
 │  metadata-explorer   →  the org's ACTUAL schema/automation │
 │  knowledge-expert    →  feature/limit verification (docs)  │
 └────────────────────────────────────────────────────────────┘
        │
        ▼
 permissions-architect →  permissions matrix (output/<slug>_permissions.xlsx)
        │            ← offered when the security model is complex
        ▼
 document-generator  →  technical spec  (output/<slug>.docx)
        │
        ▼
   ◇ human review, correction & approval ◇   ← gate: not automatic
        │
        ├──────────────────────────┐
        ▼                          ▼
 task-planner                field-mapper
 implementation backlog      data dictionary
 output/<slug>_tasks.xlsx    output/<slug>_fields.xlsx
```

## Sub-agents (`.claude/agents/`)

| Agent | Role |
| ----- | ---- |
| **metadata-explorer** | Read-only SOQL / Tooling API via the `sf` CLI. Discovers which standard/custom objects, fields, record types, and automation actually exist. Never modifies the org. |
| **knowledge-expert** | Verifies features, limits, and API behaviour against **only** help.salesforce.com and developer.salesforce.com. |
| **permissions-architect** | Offered when the spec's permissions are complex (several personas, portal + internal users, record-level visibility). Designs the security model and renders the fixed four-sheet permissions audit `.xlsx`. |
| **document-generator** | Renders the final spec `.docx` from the design facts, following `SF_Tech_Spec_Template.md` exactly. |
| **task-planner** | Runs **only after** the reviewer approves and corrects the spec. Decomposes it into OOTB-first implementation tasks — each with a readable build prompt and grounded API names — as a three-sheet RTL `.xlsx`. |
| **field-mapper** | Runs at the same gate. Builds the data dictionary: one tab per ERD entity, standard fields verified against the official Object Reference (with source URLs), custom fields split into "already in the org" and "to create". |

## Mandates

1. **Discovery first** — never propose a solution before investigating.
2. **OOTB first** — declarative (Flows, standard fields, permission sets,
   validation rules) is the default; Apex/LWC only when declarative genuinely
   fails, with a concrete justification.
3. **Ground everything** — schema claims come from a metadata finding; limit/
   capability claims come from an official docs finding with a source URL.

## The task backlog (`.xlsx`)

`task-planner` produces three RTL sheets:

- **מקרא ורקע** — intro, epic colour legend, status legend, object → API map.
- **משימות ליישום** — one row per task: id, epic (colour-coded), work type,
  description, exact API objects/fields, a step-by-step build prompt,
  dependencies, and a colour-coded status. Open questions become `GAP-N` rows.
- **פערים עסקיים** — business gaps to clarify with the client before build.

## The permissions matrix (`.xlsx`)

`permissions-architect` produces four RTL sheets in a fixed audit format:

- **1-תפקידים בתהליך** — every role, grouped by process stage.
- **2-מטריצת אובייקטים** — role × object CRUD matrix, colour-coded
  (`CRUD` / `CRU` / `R` / `—` / `להגדיר`), with the object API names beneath the
  business labels.
- **3-קבוצות ושיתוף** — the record-visibility model, widest exposure tier first.
- **4- טכני (לארכיטקט)** — channel, user license, Permission Set Licenses,
  Permission Set Group, direct Permission Sets, public groups, and build status.

## The data dictionary (`.xlsx`)

`field-mapper` produces one RTL index sheet plus a tab per ERD entity:

- **מקרא ישויות** — every entity in the spec's ERD: business name, API name,
  Standard/Custom, its role in the solution, its ERD relationships, a
  colour-coded status, and the source URL.
- **one tab per entity** — `1. Standard Fields` then `2. Custom Fields`, in the
  columns `# | Source Field Name | Display Name | Salesforce Field | API Name |
  Data Type | Mandatory | Notes / Mapping Rules | מקור | Source URL | הערות סוקר`,
  plus picklist value tables where the requirement defines them.
- **the מקור column is colour-coded** — `קיים OOTB` (verified in the Object
  Reference), `קיים בסביבה` (already in the target org), `להקמה` (this solution
  creates it), `לאימות` (unconfirmed — raised as a gap). A standard field with no
  source URL is not considered verified.

## Setup

Requires Python 3 and the Salesforce `sf` CLI (already authenticated).

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## Rendering (CLI)

The engines are also standalone CLIs. Run from the project root:

```bash
# spec .docx
PYTHONUTF8=1 PYTHONPATH="$(pwd)" ./.venv/Scripts/python.exe -m src.renderer output/model.json output/<slug>.docx

# task backlog .xlsx
PYTHONUTF8=1 PYTHONPATH="$(pwd)" ./.venv/Scripts/python.exe -m src.excel_builder output/tasks.json output/<slug>_tasks.xlsx

# permissions matrix .xlsx
PYTHONUTF8=1 PYTHONPATH="$(pwd)" ./.venv/Scripts/python.exe -m src.permissions_builder output/permissions.json output/<slug>_permissions.xlsx

# data dictionary .xlsx
PYTHONUTF8=1 PYTHONPATH="$(pwd)" ./.venv/Scripts/python.exe -m src.fields_builder output/fields.json output/<slug>_fields.xlsx
```

## Key files

| Path | Purpose |
| ---- | ------- |
| `CLAUDE.md` | Orchestrator playbook, mandates, execution budget, facts-JSON schema. |
| `SF_Tech_Spec_Template.md` | Binding structure of the spec document. Edit it to change the output. |
| `src/renderer.py` | True-RTL `.docx` engine (also a CLI). |
| `src/excel_builder.py` | True-RTL three-sheet `.xlsx` backlog engine (also a CLI). |
| `src/permissions_builder.py` | True-RTL four-sheet permissions-audit `.xlsx` engine (also a CLI). |
| `src/fields_builder.py` | True-RTL data-dictionary `.xlsx` engine — index sheet + a tab per entity (also a CLI). |
| `.claude/agents/*.md` | The six specialist sub-agents. |
| `legacy/` | Retired standalone Python/LangGraph app, kept for reference. |

Generated artifacts land in `output/` and are git-ignored.
