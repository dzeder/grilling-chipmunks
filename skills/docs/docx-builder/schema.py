"""Pydantic models for the DOCX Builder skill."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    author: str = Field(default="Ohanafy", description="Document author.")
    subject: Optional[str] = Field(default=None, description="Document subject.")
    keywords: list[str] = Field(default_factory=list, description="Document keywords.")


class DocxBuilderInput(BaseModel):
    template_name: str = Field(..., description="Template name (without extension).")
    content: dict[str, str] = Field(default_factory=dict, description="Content sections keyed by placeholder.")
    output_filename: str = Field(default="output.docx", description="Output filename.")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    operation: str = Field(default="generate", description="generate, list_templates, validate.")


class DocxBuilderOutput(BaseModel):
    file_path: Optional[str] = None
    page_count: int = 0
    file_size_bytes: int = 0
    templates: list[str] = Field(default_factory=list, description="For list_templates operation.")
