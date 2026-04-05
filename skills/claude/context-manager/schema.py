"""Pydantic models for the Context Manager skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ContextOperation(str, Enum):
    check_budget = "check_budget"
    record_usage = "record_usage"
    get_usage_report = "get_usage_report"
    trim_context = "trim_context"
    estimate_tokens = "estimate_tokens"


class UsageCategory(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


class ContextManagerInput(BaseModel):
    agent_id: str = Field(..., description="Agent identifier.")
    operation: ContextOperation = Field(..., description="Operation to perform.")
    content: Optional[str] = Field(default=None, description="Content for estimate/record.")
    category: Optional[UsageCategory] = Field(default=None, description="Usage category.")


class UsageBreakdown(BaseModel):
    system: int = 0
    user: int = 0
    assistant: int = 0
    tool: int = 0


class ContextManagerOutput(BaseModel):
    remaining_tokens: int = 0
    total_used: int = 0
    usage_breakdown: UsageBreakdown = Field(default_factory=UsageBreakdown)
    budget_exceeded: bool = False
    token_estimate: Optional[int] = None
