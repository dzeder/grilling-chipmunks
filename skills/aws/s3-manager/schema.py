"""Pydantic models for the S3 Manager skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class S3Operation(str, Enum):
    create_bucket = "create_bucket"
    delete_bucket = "delete_bucket"
    upload_object = "upload_object"
    download_object = "download_object"
    list_objects = "list_objects"
    set_lifecycle = "set_lifecycle"


class S3ManagerInput(BaseModel):
    bucket_purpose: str = Field(..., description="Purpose identifier for naming.")
    environment: Environment = Field(..., description="Target environment.")
    operation: S3Operation = Field(..., description="S3 operation to perform.")
    key: Optional[str] = Field(default=None, description="Object key.")
    body: Optional[bytes] = Field(default=None, description="Object content for uploads.")
    prefix: Optional[str] = Field(default=None, description="Prefix filter for listing.")


class S3ManagerOutput(BaseModel):
    bucket_name: str
    operation_result: str
    object_url: Optional[str] = None
