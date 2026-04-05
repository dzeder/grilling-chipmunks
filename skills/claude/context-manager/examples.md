# Context Manager Examples

## Check remaining budget

```python
from skills.claude.context_manager.skill import run
from skills.claude.context_manager.schema import ContextManagerInput

result = await run(ContextManagerInput(
    agent_id="order-classifier-001",
    operation="check_budget",
))
print(f"Remaining: {result.remaining_tokens} tokens")
```

## Record token usage

```python
result = await run(ContextManagerInput(
    agent_id="order-classifier-001",
    operation="record_usage",
    content="You are an order classifier...",
    category="system",
))
```

## Get usage report

```python
result = await run(ContextManagerInput(
    agent_id="order-classifier-001",
    operation="get_usage_report",
))
print(f"System: {result.usage_breakdown.system}")
print(f"User: {result.usage_breakdown.user}")
print(f"Assistant: {result.usage_breakdown.assistant}")
print(f"Tool: {result.usage_breakdown.tool}")
```

## Estimate tokens for content

```python
result = await run(ContextManagerInput(
    agent_id="order-classifier-001",
    operation="estimate_tokens",
    content="A long piece of text to estimate...",
))
print(f"Estimated tokens: {result.token_estimate}")
```
