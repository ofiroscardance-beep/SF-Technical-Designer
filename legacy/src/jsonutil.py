"""Robust extraction of a single JSON object from an LLM text response."""

import json
import re

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json_object(text: str) -> dict:
    """Parse the first JSON object out of `text`, tolerating fences and prose.

    Raises ValueError if no valid object is found.
    """
    body = text.strip()
    fenced = _FENCE.search(body)
    if fenced:
        body = fenced.group(1).strip()
    start, end = body.find("{"), body.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"no JSON object found in response: {text[:200]!r}")
    return json.loads(body[start : end + 1])
