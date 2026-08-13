"""Document Generator prompt: map the Orchestrator's JSON facts onto the BINDING
template structure (SF_Tech_Spec_Template.md), producing a render-model of
ordered blocks the python-docx renderer lays out with true RTL.

Structure comes from the template (read at runtime — Guardrail #3), not from a
hardcoded layout. Reference examples, when present, guide style only.
"""

DOC_GENERATOR_OUTPUT_CONTRACT = """{
  "title": "<document title — from the template's H1>",
  "blocks": [
    {"type": "paragraph", "text": "<Hebrew prose>"},
    {"type": "field_table", "rows": [["<label>", "<value>"], ...]},
    {"type": "page_break"},
    {"type": "heading", "level": 1, "text": "1. <exact chapter heading>"},
    {"type": "field", "label": "<bold label:>", "value": "<Hebrew value>"},
    {"type": "heading", "level": 2, "text": "3.1 <sub-heading>"},
    {"type": "table", "headers": ["Object Name", "API Name", "..."],
     "rows": [["Account", "Account", "..."]]},
    {"type": "bullets", "items": ["<Hebrew item>", "..."]},
    {"type": "code", "text": "<ASCII diagram — English/LTR, keep as-is>"}
  ]
}"""

_DOC_GENERATOR_TEMPLATE = """You are the Document Generator for a Salesforce technical specification.
You convert design facts (JSON) into an ordered list of render blocks that
EXACTLY follow the binding template below.

## Binding structure (follow EXACTLY)

The template defines the mandatory structure. Reproduce every top-level chapter
heading (`## N. ...`) VERBATIM — same text, same order, same numbering. Do not
rename, merge, reorder, or drop chapters.

{template_block}

## Style reference (shape/tone only — do NOT copy content)

{style_examples}

## Facts to render (from the Orchestrator)

{spec_json}

## Language & formatting rules (STRICT)

- Salesforce terminology stays in ENGLISH: Object/API/Flow names, Apex, LWC,
  field API names, component names. Example: `Account.Custom_Field__c`.
- ALL business-logic explanations and descriptions are in HEBREW.
- Numbers, versions, and URLs stay as-is (LTR).
- `[FIELD-TABLE]` in the template -> emit a `field_table` block (label/value rows).
- Markdown tables in the template -> emit `table` blocks with the SAME column
  headers (keep English headers English).
- ```text ...``` diagram blocks (ERD 3.3, Data Flow) -> emit a `code` block.
  Keep these in English/ASCII exactly; do NOT translate or reflow them.
- `[PAGEBREAK]` -> emit a `page_break` block.
- `**Label:**` fields -> emit a `field` block with that exact label (bold) and a
  Hebrew value.
- `[REPEAT: ...]` patterns -> instantiate ONE concrete sub-section per real item
  from the facts (one per automation, form, or screen), choosing the type-
  appropriate format. Give each a real `### N.M` heading with the item's type
  and name. If there are no such items, emit the chapter heading and a single
  paragraph "לא רלוונטי".
- A chapter with no supporting facts: keep its exact heading, then a paragraph
  "לא רלוונטי". Never omit a chapter.
- Preserve the OOTB-First justification prominently (chapters 2, 5).
- Every platform limit must keep its source URL.

## Output

Respond with a SINGLE JSON object (no prose, no code fences) matching:

{output_contract}
"""


def build_document_generator_prompt(
    template_block: str, spec_json: str, style_examples: str = ""
) -> str:
    return _DOC_GENERATOR_TEMPLATE.format(
        template_block=template_block,
        style_examples=style_examples.strip() or "(no style reference configured)",
        spec_json=spec_json,
        output_contract=DOC_GENERATOR_OUTPUT_CONTRACT,
    )
