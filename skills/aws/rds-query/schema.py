"""Pydantic models for the RDS Query skill."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class RdsOperation(str, Enum):
    execute_query = "execute_query"
    describe_table = "describe_table"
    list_tables = "list_tables"
    explain_query = "explain_query"


class RdsQueryInput(BaseModel):
    database: str = Field(..., description="Database name.")
    query: str = Field(default="", description="SQL query (SELECT only).")
    environment: Environment = Field(..., description="Target environment.")
    operation: RdsOperation = Field(default=RdsOperation.execute_query)
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    max_rows: int = Field(default=1000, ge=1, le=10000)
    table_name: Optional[str] = Field(default=None, description="Table name for describe/list.")


class ColumnInfo(BaseModel):
    name: str
    data_type: str


class RdsQueryOutput(BaseModel):
    rows: list[dict[str, Any]] = Field(default_factory=list)
    columns: list[ColumnInfo] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
