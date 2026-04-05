# Model Router Skill

## Purpose

Route requests to the correct Claude model tier based on task complexity. This enforces cost efficiency and appropriate capability matching across all Ohanafy AI agents.

## Model Tier Policy

| Model | Use Case | Cost Tier |
|-------|----------|-----------|
| **Haiku** | Classification, extraction, simple Q&A, formatting | Low |
| **Sonnet** | Reasoning, analysis, code generation, multi-step tasks | Medium |
| **Opus** | Evaluations only -- human-in-the-loop quality checks | High |

## Constraints

- **Haiku for classification** -- all classification, extraction, and simple routing tasks use Haiku.
- **Sonnet for reasoning** -- analysis, code generation, summarization, and multi-step reasoning use Sonnet.
- **Opus for evals only** -- Opus is reserved for evaluation tasks where an agent's output quality is assessed. Never used for regular workloads.
- **No manual override in production** -- model selection is always determined by the router, not hardcoded.
- **Cost tracking** -- every API call logs model, tokens, and estimated cost.

## Routing Logic

1. Classify the task type from the request metadata.
2. Map task type to model tier.
3. Check rate limits for the selected model.
4. Return the model identifier and configuration.

## Inputs

- `task_type`: The type of task (classification, reasoning, evaluation, etc.).
- `agent_id`: The requesting agent.
- `override_model`: Optional override (disabled in prod).
- `estimated_tokens`: Estimated input + output tokens.

## Outputs

- `model`: The selected model identifier.
- `model_tier`: haiku, sonnet, or opus.
- `estimated_cost_usd`: Estimated cost for this request.
- `rate_limit_remaining`: Remaining requests for this model tier.

## Dependencies

- `context-manager` skill for token budget checks.
