"""Load the binding document structure from SF_Tech_Spec_Template.md.

The template is the single source of truth for the document's structure
(Guardrail #3): it is read at runtime, never hardcoded. Editing the markdown
changes the generated DOCX with no code change.
"""

import re
from pathlib import Path

TEMPLATE_FILENAME = "SF_Tech_Spec_Template.md"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def load_template_markdown() -> str:
    """Return the template markdown with the conventions comment stripped."""
    path = PROJECT_ROOT / TEMPLATE_FILENAME
    if not path.is_file():
        raise FileNotFoundError(f"{TEMPLATE_FILENAME} not found at project root")
    return _HTML_COMMENT.sub("", path.read_text(encoding="utf-8")).strip()


def extract_fixed_headings(template_markdown: str) -> list[str]:
    """The ordered list of mandatory top-level chapters (`## N. ...`).

    Sub-sections (`### ...`) are dynamic/repeatable and excluded. Lines inside
    fenced code blocks are ignored.
    """
    headings: list[str] = []
    in_fence = False
    for line in template_markdown.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## "):
            headings.append(line[3:].strip())
    return headings
