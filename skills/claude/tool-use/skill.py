"""Tool Use Skill -- Define and validate tool schemas for Claude tool use."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from schema import ToolUseInput, ToolUseOutput


# Registry of tool schemas
_tool_registry: dict[str, type[BaseModel]] = {}


async def run(input_data: ToolUseInput) -> ToolUseOutput:
    """Execute a tool-use management operation."""
    # TODO: Implement tool registration and validation
    raise NotImplementedError("tool-use skill not yet implemented")


def register_tool(tool_name: str, schema_class: type[BaseModel]) -> None:
    """Register a tool with its Pydantic schema."""
    _tool_registry[tool_name] = schema_class


def validate_against_schema(data: dict[str, Any], schema_class: type[BaseModel]) -> list[str]:
    """Validate data against a Pydantic model. Returns list of errors."""
    try:
        schema_class(**data)
        return []
    except Exception as e:
        return [str(e)]


def to_claude_tool_schema(tool_name: str, description: str, schema_class: type[BaseModel]) -> dict[str, Any]:
    """Convert a Pydantic model to Claude API tool schema format."""
    return {
        "name": tool_name,
        "description": description,
        "input_schema": schema_class.model_json_schema(),
    }


async def validate(input_data: ToolUseInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    if not input_data.tool_name:
        errors.append("tool_name is required.")
    return errors
