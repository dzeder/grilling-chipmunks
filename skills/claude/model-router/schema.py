"""Pydantic models for the Model Router skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ModelTier(str, Enum):
    haiku = "haiku"
    sonnet = "sonnet"
    opus = "opus"


class ModelRouterInput(BaseModel):
    task_type: str = Field(..., description="Task type (classification, reasoning, evaluation, etc.).")
    agent_id: str = Field(..., description="Requesting agent identifier.")
    override_model: Optional[ModelTier] = Field(default=None, description="Manual override (disabled in prod).")
    estimated_tokens: int = Field(default=1000, description="Estimated total tokens.")
    environment: str = Field(default="dev", description="Current environment.")


class ModelRouterOutput(BaseModel):
    model: str = Field(..., description="Model identifier for the API call.")
    model_tier: ModelTier
    estimated_cost_usd: float
    rate_limit_remaining: int
