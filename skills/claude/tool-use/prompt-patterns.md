# Tool Use -- Prompt Patterns

## Pattern: Tool Definition in System Prompt

Always describe tool capabilities in the system prompt so the model knows what is available.

```
You have access to the following tools:
- order_lookup: Look up an order by ID. Returns order details.
- inventory_check: Check inventory levels for a product SKU.

Use tools when you need factual data. Do not guess.
```

## Pattern: Prefer Tool Use Over JSON

Instead of asking Claude to output JSON:
```
# BAD - freeform JSON
"Return a JSON object with fields: name, quantity, priority"
```

Use native tool use:
```python
# GOOD - structured tool use
tools = [to_claude_tool_schema("extract_order", "Extract order details.", OrderSchema)]
```

## Pattern: Error Recovery

When a tool call fails, provide the error back to the model so it can retry or adjust.

```python
if not result.valid:
    # Return error to model as tool_result with is_error=True
    tool_result = {"type": "tool_result", "is_error": True, "content": str(result.errors)}
```

## Pattern: Chained Tool Calls

Allow the model to make multiple sequential tool calls to gather information before responding.

## Anti-Patterns

- **Never**: Parse freeform JSON from Claude when tool use is available.
- **Never**: Allow unvalidated tool inputs to reach the tool implementation.
- **Never**: Swallow tool errors silently.
