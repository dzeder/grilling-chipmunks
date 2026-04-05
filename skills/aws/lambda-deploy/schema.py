"""Pydantic models for the Lambda Deploy skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class Runtime(str, Enum):
    python312 = "python3.12"
    nodejs20 = "nodejs20.x"


class LambdaDeployInput(BaseModel):
    function_name: str = Field(..., description="Lambda function name.")
    runtime: Runtime = Field(..., description="Lambda runtime.")
    handler: str = Field(default="app.handler", description="Function entry point.")
    memory_mb: int = Field(default=256, ge=128, le=3008)
    timeout_seconds: int = Field(default=30, ge=1, le=900)
    environment: Environment = Field(..., description="Target environment.")
    env_vars: dict[str, str] = Field(default_factory=dict)
    layers: list[str] = Field(default_factory=list, description="Lambda Layer ARNs.")


class LambdaDeployOutput(BaseModel):
    function_arn: str
    version: str
    deployment_status: str
    cloudwatch_log_group: str
