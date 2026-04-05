"""DOCX Builder Skill -- Generate DOCX documents from templates using python-docx."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from schema import DocxBuilderInput, DocxBuilderOutput


TEMPLATES_DIR = Path(__file__).parent / "templates"

# Ohanafy brand colors
PRIMARY_COLOR = "0A2342"
ACCENT_COLOR = "E8833A"


async def run(input_data: DocxBuilderInput) -> DocxBuilderOutput:
    """Generate a DOCX document from a template."""
    # TODO: Implement DOCX generation with python-docx
    raise NotImplementedError("docx-builder skill not yet implemented")


def list_templates() -> list[str]:
    """List available DOCX templates."""
    if not TEMPLATES_DIR.exists():
        return []
    return [f.stem for f in TEMPLATES_DIR.glob("*.docx")]


async def validate(input_data: DocxBuilderInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    if not input_data.template_name:
        errors.append("template_name is required.")
    if not input_data.content:
        errors.append("content is required.")
    return errors
