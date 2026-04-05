# Prompt Loader Examples

## Load and render a prompt

```python
from skills.claude.prompt_loader.skill import run
from skills.claude.prompt_loader.schema import PromptLoaderInput

result = await run(PromptLoaderInput(
    prompt_name="order-classification",
    version="1.2.0",
    variables={
        "company": "Ohanafy",
        "categories": "high, medium, low",
        "order_text": "Urgent order for 500 units...",
    },
))
print(result.rendered_prompt)
print(f"Tokens: ~{result.token_estimate}")
```

## Load latest version

```python
result = await run(PromptLoaderInput(
    prompt_name="order-classification",
    version="latest",
    variables={"company": "Ohanafy", "categories": "high, low", "order_text": "..."},
))
print(f"Loaded version: {result.prompt_version}")
```

## Validate variables before rendering

```python
from skills.claude.prompt_loader.skill import validate

errors = await validate(PromptLoaderInput(
    prompt_name="",  # will fail
))
# errors -> ["prompt_name is required."]
```
