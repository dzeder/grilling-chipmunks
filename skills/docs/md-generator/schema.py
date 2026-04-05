"""Pydantic models for the Markdown Generator skill."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Section(BaseModel):
    heading: str = Field(..., description="Section heading text.")
    content: str = Field(..., description="Section body content in markdown.")
    level: int = Field(default=2, ge=1, le=6, description="Heading level (1-6).")


class MdGeneratorInput(BaseModel):
    title: str = Field(..., description="Document title.")
    description: str = Field(default="", description="Brief description for front matter.")
    sections: list[Section] = Field(default_factory=list, description="Document sections.")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization.")
    output_path: Optional[str] = Field(default=None, description="Relative path under docs/.")
    operation: str = Field(default="generate", description="generate, update, validate, generate_nav.")


class MdGeneratorOutput(BaseModel):
    markdown_content: str = ""
    file_path: Optional[str] = None
    nav_entry: Optional[str] = None
    validation_errors: list[str] = Field(default_factory=list)
