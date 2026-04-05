"""Pydantic models for the CDK Deploy skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class CdkDeployInput(BaseModel):
    stack_name: str = Field(..., description="CDK stack name (ohanafy-{env}-{service}-stack).")
    environment: Environment = Field(..., description="Target environment.")
    context_overrides: dict[str, str] = Field(default_factory=dict)
    skip_diff: bool = Field(default=False, description="Skip cdk diff step.")


class CheckovFinding(BaseModel):
    check_id: str
    resource: str
    severity: str
    status: str
    guideline: Optional[str] = None


class CdkDeployOutput(BaseModel):
    stack_arn: str
    deployment_status: str
    checkov_report: list[CheckovFinding] = Field(default_factory=list)
    diff_output: Optional[str] = None
