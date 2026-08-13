# Reference Technical Specifications

The Document Generator learns the **structure and style** of the final `.docx`
from the examples listed below — nothing about the output layout is hardcoded.

## How this file is used

- The system parses the table under **Examples** at runtime.
- Each `path` is ingested (PDF / DOCX / TXT supported).
- The combined content becomes the few-shot structural template for generation.
- Add or remove rows to change the template. No code changes required.

## Examples

| enabled | path                                   | notes                              |
| ------- | -------------------------------------- | ---------------------------------- |
| true    | examples/sample-tech-spec.txt          | Baseline structure (headings only) |
| false   | examples/real-spec-billing.docx        | Add your own real spec here        |
| false   | examples/real-spec-integration.pdf     | Add your own real spec here        |

> Set `enabled` to `false` to keep a row for reference without ingesting it.
> Paths are relative to the project root.
