"""Document Generator agent: Orchestrator JSON -> render-model of blocks.

Reads the binding template at runtime, injects it plus the facts into the
generator prompt, and returns the validated block-model the renderer consumes.
"""

import json

from src.config import ANTHROPIC_MODEL, make_client
from src.examples_loader import build_template_block, load_reference_examples
from src.jsonutil import extract_json_object
from src.prompts.document_generator import build_document_generator_prompt
from src.template_loader import extract_fixed_headings, load_template_markdown


def _style_examples() -> str:
    try:
        return build_template_block(load_reference_examples())
    except FileNotFoundError:
        return ""


def _validate_model(model: dict, required_headings: list[str]) -> None:
    """Enforce shape and the exact-headings mandate at the LLM-output boundary."""
    blocks = model.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("document model 'blocks' must be a list")
    for i, block in enumerate(blocks):
        if not isinstance(block, dict) or "type" not in block:
            raise ValueError(f"block {i} must be an object with a 'type'")

    heading_texts = {
        block.get("text", "").strip()
        for block in blocks
        if block.get("type") == "heading"
    }
    missing = [h for h in required_headings if h not in heading_texts]
    if missing:
        raise ValueError(f"generated document is missing mandatory chapters: {missing}")


def generate_document_model(spec: dict) -> dict:
    """Turn the Orchestrator's spec JSON into a validated renderer block-model."""
    template = load_template_markdown()
    prompt = build_document_generator_prompt(
        template_block=template,
        spec_json=json.dumps(spec, ensure_ascii=False, indent=2),
        style_examples=_style_examples(),
    )
    response = make_client().messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text")
    model = extract_json_object(text)
    _validate_model(model, extract_fixed_headings(template))
    return model
