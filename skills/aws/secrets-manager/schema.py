"""Pydantic models for the Secrets Manager skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class SecretOperation(str, Enum):
    create_secret = "create_secret"
    get_secret = "get_secret"
    update_secret = "update_secret"
    delete_secret = "delete_secret"
    rotate_secret = "rotate_secret"
    list_secrets = "list_secrets"


class SecretsManagerInput(BaseModel):
    service: str = Field(..., description="Service name for the secret path.")
    secret_name: str = Field(..., description="Secret identifier.")
    environment: Environment = Field(..., description="Target environment.")
    operation: SecretOperation = Field(..., description="Operation to perform.")
    secret_value: Optional[str] = Field(default=None, description="Secret value for create/update.")
    rotation_days: int = Field(default=30, ge=1, le=365, description="Rotation period in days.")


class SecretsManagerOutput(BaseModel):
    secret_arn: str
    version_id: Optional[str] = None
    operation_result: str
    secret_names: list[str] = Field(default_factory=list, description="For list operations.")
