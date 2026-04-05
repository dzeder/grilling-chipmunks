"""Pydantic models for the Prompt Loader skill."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PromptLoaderInput(BaseModel):
    prompt_name: str = Field(..., description="Name of the prompt to load.")
    version: str = Field(default="latest", description="Semver version or 'latest'.")
    variables: dict[str, str] = Field(default_factory=dict, description="Template variables.")


class PromptLoaderOutput(BaseModel):
    rendered_prompt: str
    prompt_version: str
    token_estimate: int
    prompt_name: str
