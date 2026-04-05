# Context Manager Skill

## Purpose

Manage context window budgets per agent. Track token usage across prompts, tool results, and conversation history to prevent context overflow and optimize cost.

## Constraints

- **Per-agent budgets** -- each agent has a configured token budget based on its model tier.
- **Track all token usage** -- system prompts, user messages, assistant responses, and tool results.
- **Budget enforcement** -- reject requests that would exceed the agent's context budget.
- **Sliding window** -- older messages are summarized or dropped when approaching the limit.
- **Cost tracking** -- log estimated cost per agent per session.

## Budget Defaults

| Model | Context Window | Budget (80%) | Reserved for Output |
|-------|---------------|--------------|-------------------|
| Haiku | 200K tokens | 160K | 40K |
| Sonnet | 200K tokens | 160K | 40K |
| Opus | 200K tokens | 140K | 60K |

## Supported Operations

- `check_budget` -- Check remaining token budget for an agent.
- `record_usage` -- Record token usage for a message or tool call.
- `get_usage_report` -- Get a breakdown of token usage by category.
- `trim_context` -- Remove oldest messages to free up budget.
- `estimate_tokens` -- Estimate token count for a string.

## Inputs

- `agent_id`: Identifier for the agent.
- `operation`: The operation to perform.
- `content`: Content to estimate or record (for relevant operations).
- `category`: Usage category (system, user, assistant, tool).

## Outputs

- `remaining_tokens`: Tokens remaining in the budget.
- `total_used`: Total tokens used in the current session.
- `usage_breakdown`: Token usage by category.
- `budget_exceeded`: Boolean flag.

## Dependencies

- `model-router` skill for model-specific budget configuration.
