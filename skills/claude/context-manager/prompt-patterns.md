# Context Manager -- Prompt Patterns

## Pattern: Budget-Aware Prompting

Always check remaining budget before constructing prompts. Adjust detail level based on available tokens.

```python
budget = await context_manager.run(ContextManagerInput(
    agent_id="my-agent",
    operation="check_budget",
))

if budget.remaining_tokens > 50_000:
    # Use detailed prompt with examples
    prompt_version = "detailed-v1.0.0"
else:
    # Use concise prompt
    prompt_version = "concise-v1.0.0"
```

## Pattern: Progressive Summarization

When context is running low, summarize older messages instead of dropping them.

1. Keep the last 5 conversation turns verbatim.
2. Summarize turns 6-20 into a single paragraph.
3. Drop turns older than 20.

## Pattern: Category Budgets

Allocate token budgets by category to prevent any single category from dominating.

| Category | Budget Share |
|----------|-------------|
| System | 20% |
| User | 30% |
| Assistant | 30% |
| Tool | 20% |

## Pattern: Tool Result Truncation

Tool results can be large. Truncate to the first 2000 tokens and add a "[truncated]" marker.

## Anti-Patterns

- **Never**: Ignore token budgets and hope for the best.
- **Never**: Send full database query results as context.
- **Never**: Include redundant conversation history.
