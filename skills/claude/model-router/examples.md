# Model Router Examples

## Route a classification task

```python
from skills.claude.model_router.skill import run
from skills.claude.model_router.schema import ModelRouterInput

result = await run(ModelRouterInput(
    task_type="classification",
    agent_id="order-classifier",
    estimated_tokens=500,
))
# result.model_tier -> "haiku"
# result.model -> "claude-haiku-4-20260401"
```

## Route a reasoning task

```python
result = await run(ModelRouterInput(
    task_type="reasoning",
    agent_id="data-analyst",
    estimated_tokens=5000,
))
# result.model_tier -> "sonnet"
```

## Route an evaluation task

```python
result = await run(ModelRouterInput(
    task_type="evaluation",
    agent_id="quality-checker",
    estimated_tokens=10000,
))
# result.model_tier -> "opus"
```

## Override model in dev (not allowed in prod)

```python
result = await run(ModelRouterInput(
    task_type="classification",
    agent_id="test-agent",
    override_model="sonnet",
    environment="dev",
))
# result.model_tier -> "sonnet" (override accepted in dev)
```
