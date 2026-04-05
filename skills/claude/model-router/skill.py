"""Model Router Skill -- Route requests to the correct Claude model tier."""

from __future__ import annotations

from typing import Any

from schema import ModelRouterInput, ModelRouterOutput, ModelTier


# Model identifiers per tier
MODEL_MAP = {
    ModelTier.haiku: "claude-haiku-4-20260401",
    ModelTier.sonnet: "claude-sonnet-4-20250514",
    ModelTier.opus: "claude-opus-4-20250918",
}

# Cost per 1M tokens (input/output)
COST_PER_1M = {
    ModelTier.haiku: {"input": 0.25, "output": 1.25},
    ModelTier.sonnet: {"input": 3.00, "output": 15.00},
    ModelTier.opus: {"input": 15.00, "output": 75.00},
}

# Task type to model tier mapping
TASK_ROUTING = {
    "classification": ModelTier.haiku,
    "extraction": ModelTier.haiku,
    "formatting": ModelTier.haiku,
    "routing": ModelTier.haiku,
    "reasoning": ModelTier.sonnet,
    "analysis": ModelTier.sonnet,
    "code_generation": ModelTier.sonnet,
    "summarization": ModelTier.sonnet,
    "evaluation": ModelTier.opus,
    "quality_check": ModelTier.opus,
}


async def run(input_data: ModelRouterInput) -> ModelRouterOutput:
    """Route a request to the appropriate model tier."""
    tier = TASK_ROUTING.get(input_data.task_type, ModelTier.sonnet)

    if input_data.override_model and input_data.environment != "prod":
        tier = input_data.override_model

    model = MODEL_MAP[tier]
    cost = _estimate_cost(tier, input_data.estimated_tokens)

    return ModelRouterOutput(
        model=model,
        model_tier=tier,
        estimated_cost_usd=cost,
        rate_limit_remaining=-1,  # TODO: Implement rate limit tracking
    )


def _estimate_cost(tier: ModelTier, estimated_tokens: int) -> float:
    """Estimate cost in USD for a request."""
    rates = COST_PER_1M[tier]
    # Assume 50/50 input/output split for estimation
    input_tokens = estimated_tokens * 0.5
    output_tokens = estimated_tokens * 0.5
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


async def validate(input_data: ModelRouterInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    if input_data.task_type not in TASK_ROUTING:
        errors.append(f"Unknown task_type '{input_data.task_type}'. Known: {list(TASK_ROUTING.keys())}")
    if input_data.override_model == ModelTier.opus and input_data.task_type != "evaluation":
        errors.append("Opus is reserved for evaluation tasks only.")
    return errors
