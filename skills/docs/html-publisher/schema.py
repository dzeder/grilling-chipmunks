"""Pydantic models for the HTML Publisher skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DocCategory(str, Enum):
    guides = "guides"
    api = "api"
    tutorials = "tutorials"


class PublishOperation(str, Enum):
    generate_page = "generate_page"
    build = "build"
    publish = "publish"
    validate = "validate"


class HtmlPublisherInput(BaseModel):
    page_title: str = Field(default="", description="Page title.")
    content: str = Field(default="", description="MDX content.")
    slug: str = Field(default="", description="URL slug.")
    category: DocCategory = Field(default=DocCategory.guides, description="Documentation category.")
    operation: PublishOperation = Field(default=PublishOperation.generate_page)
    version: Optional[str] = Field(default=None, description="Documentation version.")


class HtmlPublisherOutput(BaseModel):
    file_path: Optional[str] = None
    build_status: Optional[str] = None
    publish_url: Optional[str] = None
    validation_errors: list[str] = Field(default_factory=list)
