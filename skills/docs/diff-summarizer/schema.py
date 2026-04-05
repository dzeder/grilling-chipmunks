"""Pydantic models for the Diff Summarizer skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Audience(str, Enum):
    developer = "developer"
    stakeholder = "stakeholder"
    end_user = "end_user"


class OutputFormat(str, Enum):
    markdown = "markdown"
    plaintext = "plaintext"


class DiffOperation(str, Enum):
    summarize_diff = "summarize_diff"
    summarize_commits = "summarize_commits"
    generate_release_notes = "generate_release_notes"
    detect_breaking_changes = "detect_breaking_changes"


class ChangeCategory(BaseModel):
    features: list[str] = Field(default_factory=list)
    bug_fixes: list[str] = Field(default_factory=list)
    refactoring: list[str] = Field(default_factory=list)
    documentation: list[str] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class DiffSummarizerInput(BaseModel):
    diff_text: Optional[str] = Field(default=None, description="Raw git diff.")
    commit_range: Optional[str] = Field(default=None, description="Git commit range (e.g., v1.0.0..v1.1.0).")
    audience: Audience = Field(default=Audience.developer, description="Target audience.")
    format: OutputFormat = Field(default=OutputFormat.markdown, description="Output format.")
    operation: DiffOperation = Field(default=DiffOperation.summarize_diff)
    repo_path: Optional[str] = Field(default=None, description="Path to git repository.")


class DiffSummarizerOutput(BaseModel):
    summary: str = ""
    categories: ChangeCategory = Field(default_factory=ChangeCategory)
    breaking_changes: list[str] = Field(default_factory=list)
    files_changed: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    secret_warnings: list[str] = Field(default_factory=list)
