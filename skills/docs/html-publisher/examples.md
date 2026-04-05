# HTML Publisher Examples

## Generate a documentation page

```python
from skills.docs.html_publisher.skill import run
from skills.docs.html_publisher.schema import HtmlPublisherInput

result = await run(HtmlPublisherInput(
    page_title="Getting Started",
    content="# Getting Started\n\nWelcome to Ohanafy...",
    slug="getting-started",
    category="guides",
    operation="generate_page",
))
print(f"Created: {result.file_path}")
```

## Build the Docusaurus site

```python
result = await run(HtmlPublisherInput(
    operation="build",
))
print(f"Build status: {result.build_status}")
```

## Publish to S3 + CloudFront

```python
result = await run(HtmlPublisherInput(
    operation="publish",
))
print(f"Published to: {result.publish_url}")
```

## Validate MDX and links

```python
result = await run(HtmlPublisherInput(
    page_title="Test Page",
    content="# Test\n\n[Broken link](/nonexistent)",
    slug="test",
    operation="validate",
))
if result.validation_errors:
    for error in result.validation_errors:
        print(f"Error: {error}")
```
