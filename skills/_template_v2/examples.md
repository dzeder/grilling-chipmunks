# Examples — {skill-name}

Real usage examples against Ohanafy data.

## Example 1: {description}

```python
from skills.{pillar}.{skill_name}.skill import run
from skills.{pillar}.{skill_name}.schema import InputSchema

result = run(InputSchema(
    param1="example_value",
))

# Expected output:
# {"status": "success", "data": {...}}
```

## Example 2: Error case

```python
result = run(InputSchema(
    param1="invalid_value",
))

# Expected output:
# {"status": "error", "error": {"code": "EXAMPLE_ERROR", "message": "..."}}
```
