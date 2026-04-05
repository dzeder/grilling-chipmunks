# Tool Use Examples

## Register a tool

```python
from skills.claude.tool_use.skill import run, register_tool
from skills.claude.tool_use.schema import ToolUseInput
from pydantic import BaseModel, Field

class OrderLookupInput(BaseModel):
    order_id: str = Field(..., description="The order ID to look up.")

register_tool("order_lookup", OrderLookupInput)
```

## Get tool schema in Claude API format

```python
from skills.claude.tool_use.skill import to_claude_tool_schema

schema = to_claude_tool_schema(
    tool_name="order_lookup",
    description="Look up an order by ID.",
    schema_class=OrderLookupInput,
)
# Use schema in Claude API tool_use parameter
```

## Validate tool input

```python
result = await run(ToolUseInput(
    tool_name="order_lookup",
    operation="validate_input",
    input_data={"order_id": "ORD-12345"},
))
print(f"Valid: {result.valid}")
```

## List registered tools

```python
result = await run(ToolUseInput(
    tool_name="*",
    operation="list_tools",
))
print(result.registered_tools)
```
