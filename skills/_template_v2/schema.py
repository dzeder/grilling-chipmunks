"""
Schema definitions for {skill-name} skill.

All input validation and output typing lives here.
"""

from pydantic import BaseModel, Field


class InputSchema(BaseModel):
    """Input parameters for the skill."""

    param1: str = Field(..., description="Required parameter")
    param2: str | None = Field(None, description="Optional parameter")


class OutputSchema(BaseModel):
    """Output format for the skill."""

    status: str = Field(..., description="'success' or 'error'")
    data: dict | None = Field(None, description="Result data on success")
    error: dict | None = Field(None, description="Error details on failure")
