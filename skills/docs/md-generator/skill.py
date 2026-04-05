"""Markdown Generator Skill -- Generate MkDocs-compatible markdown docs."""

from __future__ import annotations

from typing import Any

from schema import MdGeneratorInput, MdGeneratorOutput, Section


async def run(input_data: MdGeneratorInput) -> MdGeneratorOutput:
    """Generate a markdown document in MkDocs format."""
    # TODO: Implement markdown generation
    raise NotImplementedError("md-generator skill not yet implemented")


def build_front_matter(title: str, description: str, tags: list[str]) -> str:
    """Build YAML front matter block."""
    tag_str = "\n".join(f"  - {tag}" for tag in tags)
    return f"""---
title: {title}
description: {description}
tags:
{tag_str}
---"""


def build_section(section: Section) -> str:
    """Build a markdown section with heading and content."""
    prefix = "#" * section.level
    return f"{prefix} {section.heading}\n\n{section.content}"


async def validate(input_data: MdGeneratorInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    if not input_data.title:
        errors.append("title is required.")
    if not input_data.sections:
        errors.append("At least one section is required.")
    return errors
