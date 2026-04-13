"""
Lineage tracking for the repo-watchers pipeline.

Scans skills/**/SKILL.md for learned_from frontmatter that cites
a watched repo. When upstream changes are detected, the affected
local skills are flagged for review.
"""

import logging
import re
from pathlib import Path

import yaml

from .schema import AffectedSkill

logger = logging.getLogger(__name__)

SKILLS_ROOT = Path("skills")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def find_affected_skills(repo_url: str) -> list[AffectedSkill]:
    """Find local skills whose learned_from cites the given repo.

    Args:
        repo_url: GitHub owner/repo string (e.g. 'addyosmani/agent-skills')

    Returns:
        List of AffectedSkill with paths to skills that cite this repo.
    """
    affected = []

    if not SKILLS_ROOT.exists():
        return affected

    for skill_file in SKILLS_ROOT.glob("**/SKILL.md"):
        try:
            text = skill_file.read_text()
        except OSError:
            continue

        fm = _parse_frontmatter(text)
        learned_from = fm.get("learned_from")
        if not learned_from or not isinstance(learned_from, list):
            continue

        for entry in learned_from:
            if not isinstance(entry, dict):
                continue
            entry_repo = entry.get("repo", "")
            if entry_repo == repo_url or entry_repo.rstrip("/") == repo_url.rstrip("/"):
                affected.append(AffectedSkill(
                    skill_path=str(skill_file.relative_to(".")),
                    learned_from_repo=repo_url,
                    adapted_date=entry.get("adapted"),
                ))

    if affected:
        logger.info("Found %d skill(s) citing %s via learned_from", len(affected), repo_url)

    return affected
