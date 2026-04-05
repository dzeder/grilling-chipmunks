"""Diff Summarizer Skill -- Summarize git diffs into human-readable changelogs."""

from __future__ import annotations

import re
from typing import Any

from schema import DiffSummarizerInput, DiffSummarizerOutput, ChangeCategory


# Patterns that suggest secrets in diffs
SECRET_PATTERNS = re.compile(
    r"(password|secret|api_key|token|credential|private_key)\s*[=:]\s*\S+",
    re.IGNORECASE,
)


async def run(input_data: DiffSummarizerInput) -> DiffSummarizerOutput:
    """Summarize a git diff or commit range."""
    # TODO: Implement diff summarization (uses Claude Sonnet via model-router)
    raise NotImplementedError("diff-summarizer skill not yet implemented")


def detect_secrets(diff_text: str) -> list[str]:
    """Detect potential secrets in diff text. Returns list of flagged lines."""
    flagged: list[str] = []
    for i, line in enumerate(diff_text.splitlines(), 1):
        if line.startswith("+") and SECRET_PATTERNS.search(line):
            flagged.append(f"Line {i}: Potential secret detected")
    return flagged


def count_changes(diff_text: str) -> tuple[int, int, int]:
    """Count files changed, lines added, and lines removed."""
    files = set()
    added = 0
    removed = 0
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            parts = line.split()
            if len(parts) >= 3:
                files.add(parts[2])
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return len(files), added, removed


async def validate(input_data: DiffSummarizerInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    if not input_data.diff_text and not input_data.commit_range:
        errors.append("Either diff_text or commit_range is required.")
    return errors
