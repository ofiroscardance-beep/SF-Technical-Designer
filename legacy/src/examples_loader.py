"""Dynamic template learning (Guardrail #3).

Reads examples_config.md, ingests every enabled reference spec (TXT / PDF /
DOCX), and returns their combined text to be injected as the few-shot
structural template. Nothing about the output layout is hardcoded — change the
config file and the template changes.
"""

from dataclasses import dataclass
from pathlib import Path

from docx import Document
from pypdf import PdfReader

CONFIG_FILENAME = "examples_config.md"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ReferenceExample:
    path: Path
    text: str


def _parse_config_rows(config_text: str) -> list[Path]:
    """Extract enabled example paths from the markdown table.

    A data row looks like: | true | examples/foo.txt | notes |
    Only rows whose first cell is exactly `true` are ingested.
    """
    paths: list[Path] = []
    for line in config_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        enabled, raw_path = cells[0].lower(), cells[1]
        if enabled != "true":
            continue
        if raw_path.lower() in ("path", "") or set(raw_path) <= {"-", ":"}:
            continue  # header or separator row
        paths.append(PROJECT_ROOT / raw_path)
    return paths


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_docx(path: Path) -> str:
    document = Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)


_READERS = {".txt": _read_txt, ".pdf": _read_pdf, ".docx": _read_docx}


def _ingest(path: Path) -> ReferenceExample:
    reader = _READERS.get(path.suffix.lower())
    if reader is None:
        raise ValueError(f"unsupported example type: {path.suffix} ({path.name})")
    if not path.is_file():
        raise FileNotFoundError(f"example not found: {path}")
    return ReferenceExample(path=path, text=reader(path).strip())


def load_reference_examples() -> list[ReferenceExample]:
    """Load every enabled example. Skips unreadable files with a note rather
    than aborting the whole run — a bad reference shouldn't block generation."""
    config_path = PROJECT_ROOT / CONFIG_FILENAME
    if not config_path.is_file():
        raise FileNotFoundError(f"{CONFIG_FILENAME} not found at project root")

    examples: list[ReferenceExample] = []
    for path in _parse_config_rows(config_path.read_text(encoding="utf-8")):
        try:
            example = _ingest(path)
        except (ValueError, FileNotFoundError) as exc:
            print(f"[examples_loader] skipping: {exc}")
            continue
        if example.text:
            examples.append(example)
    return examples


def build_template_block(examples: list[ReferenceExample]) -> str:
    """Format ingested examples as a single few-shot block for the prompt."""
    if not examples:
        return "(no reference examples configured)"
    parts = []
    for i, ex in enumerate(examples, 1):
        parts.append(
            f"--- REFERENCE EXAMPLE {i}: {ex.path.name} ---\n{ex.text}"
        )
    return "\n\n".join(parts)
