# DOCX Builder Examples

## Generate a proposal document

```python
from skills.docs.docx_builder.skill import run
from skills.docs.docx_builder.schema import DocxBuilderInput, DocumentMetadata

result = await run(DocxBuilderInput(
    template_name="proposal",
    content={
        "title": "Q2 Partnership Proposal",
        "executive_summary": "We propose a strategic partnership...",
        "scope": "The engagement covers...",
        "timeline": "Phase 1: Discovery (2 weeks)...",
        "pricing": "Total investment: $50,000",
    },
    output_filename="q2-partnership-proposal.docx",
    metadata=DocumentMetadata(
        author="Sales Team",
        subject="Partnership Proposal",
        keywords=["proposal", "partnership", "Q2"],
    ),
))
print(f"Generated: {result.file_path} ({result.file_size_bytes} bytes)")
```

## List available templates

```python
from skills.docs.docx_builder.skill import list_templates

templates = list_templates()
# ["proposal", "report", "invoice", "letter"]
```

## Validate content before generating

```python
result = await run(DocxBuilderInput(
    template_name="proposal",
    content={},  # will fail validation
    operation="validate",
))
```
