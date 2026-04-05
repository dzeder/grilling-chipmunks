"""Prompt Loader Skill -- Load and version prompts from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from schema import PromptLoaderInput, PromptLoaderOutput


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


async def run(input_data: PromptLoaderInput) -> PromptLoaderOutput:
    """Load, validate, and render a versioned prompt."""
    # TODO: Implement prompt loading from YAML files
    raise NotImplementedError("prompt-loader skill not yet implemented")


def render_template(template: str, variables: dict[str, str]) -> str:
    """Render a prompt template with the given variables."""
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def estimate_tokens(text: str) -> int:
    """Rough token estimate (4 chars per token)."""
    return len(text) // 4


async def validate(input_data: PromptLoaderInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    if not input_data.prompt_name:
        errors.append("prompt_name is required.")
    return errors
