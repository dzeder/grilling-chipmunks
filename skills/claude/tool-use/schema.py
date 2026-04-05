"""Pydantic models for the Tool Use skill."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolOperation(str, Enum):
    register_tool = "register_tool"
    validate_input = "validate_input"
    validate_output = "validate_output"
    list_tools = "list_tools"
    get_tool_schema = "get_tool_schema"


class ToolUseInput(BaseModel):
    tool_name: str = Field(..., description="Tool name.")
    operation: ToolOperation = Field(..., description="Operation to perform.")
    input_data: Optional[dict[str, Any]] = Field(default=None, description="Data to validate.")
    output_data: Optional[dict[str, Any]] = Field(default=None, description="Output data to validate.")
    schema_definition: Optional[str] = Field(default=None, description="Pydantic model class path.")
    description: Optional[str] = Field(default=None, description="Tool description.")


class ToolUseOutput(BaseModel):
    valid: Optional[bool] = None
    errors: list[str] = Field(default_factory=list)
    tool_schema: Optional[dict[str, Any]] = None
    registered_tools: list[str] = Field(default_factory=list)
