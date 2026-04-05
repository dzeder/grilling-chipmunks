# {skill-name}

{One-line description of what this skill does.}

## When to Use

- {Condition 1 that triggers this skill}
- {Condition 2 that triggers this skill}

## Interface

```python
from skills.{pillar}.{skill_name}.skill import run

result = run(
    param1="value",
    param2="value",
)
```

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| param1 | str | yes | {description} |
| param2 | str | no | {description} |

## Returns

```python
{
    "status": "success" | "error",
    "data": { ... },
    "error": { "code": "...", "message": "..." }  # only on error
}
```

## Error Handling

See `error-codes.md` for full error reference.
Common errors: {list 2-3 most common errors and what to do}.

## Rate Limits

See `rate-limits.md` for API limits and retry policy.

## Examples

See `examples.md` for real usage examples against Ohanafy data.
