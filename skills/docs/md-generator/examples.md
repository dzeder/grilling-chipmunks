# Markdown Generator Examples

## Generate a new document

```python
from skills.docs.md_generator.skill import run
from skills.docs.md_generator.schema import MdGeneratorInput, Section

result = await run(MdGeneratorInput(
    title="API Reference",
    description="REST API endpoint documentation.",
    sections=[
        Section(heading="Authentication", content="All requests require a Bearer token.", level=2),
        Section(heading="Endpoints", content="See subsections below.", level=2),
        Section(heading="GET /orders", content="Returns a list of orders.", level=3),
    ],
    tags=["api", "reference"],
    output_path="api/reference.md",
))
print(result.markdown_content)
```

## Validate existing markdown

```python
result = await run(MdGeneratorInput(
    title="Test",
    operation="validate",
    sections=[],
))
# result.validation_errors -> ["At least one section is required."]
```

## Generate navigation entry

```python
result = await run(MdGeneratorInput(
    title="API Reference",
    output_path="api/reference.md",
    operation="generate_nav",
))
print(result.nav_entry)
# "- API Reference: api/reference.md"
```
