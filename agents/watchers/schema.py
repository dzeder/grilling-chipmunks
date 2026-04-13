"""
Pydantic schemas for the repo-watchers pipeline.

Data flows: fetch → score → lineage → route → issue/digest.
Each stage has a distinct model at its boundary.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class WatchType(str, Enum):
    releases = "releases"
    new_files = "new_files"
    all = "all"


class AutoAdopt(str, Enum):
    false = "false"
    new_patterns = "new_patterns"
    dependency_updates = "dependency_updates"


class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"


class WatchedRepo(BaseModel):
    """A single repo entry from watchers/repos.yaml."""

    url: str = Field(description="GitHub owner/repo (e.g. 'aws/aws-cdk')")
    priority: Priority
    watch: WatchType
    why: str = Field(description="Rationale for tracking this repo")
    auto_adopt: AutoAdopt = AutoAdopt.false
    tags: list[str] = Field(default_factory=list)
    category: str = Field(default="", description="Top-level category from repos.yaml")


class ItemType(str, Enum):
    release = "release"
    new_file = "new_file"


class WatchItem(BaseModel):
    """A single fetched item (release or new file)."""

    repo: str = Field(description="GitHub owner/repo")
    item_type: ItemType
    title: str
    body: str = Field(default="", description="Release body or commit message")
    url: str = Field(description="Direct link to the release or file")
    published_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)


class ScoredItem(BaseModel):
    """An item after Claude haiku relevance scoring."""

    repo: str
    item_type: ItemType
    title: str
    body: str = ""
    url: str
    published_at: datetime | None = None
    score: float = Field(ge=0.0, le=1.0)
    reason: str = Field(default="", description="One-sentence scoring rationale")
    model_used: str = Field(default="claude-haiku-4-5-20251001")
    metadata: dict = Field(default_factory=dict)


class AffectedSkill(BaseModel):
    """A local skill whose learned_from cites a changed repo."""

    skill_path: str = Field(description="Relative path to SKILL.md")
    learned_from_repo: str
    adapted_date: str | None = None


class RouteAction(str, Enum):
    auto_issue = "auto_issue"
    notify = "notify"
    log_only = "log_only"


class RoutedItem(BaseModel):
    """A scored item after routing decision."""

    repo: str
    item_type: ItemType
    title: str
    body: str = ""
    url: str
    published_at: datetime | None = None
    score: float
    reason: str = ""
    action: RouteAction
    affected_skills: list[AffectedSkill] = Field(default_factory=list)
    issue_url: str | None = None
    metadata: dict = Field(default_factory=dict)


class RepoState(BaseModel):
    """Per-repo checkpoint for incremental fetching."""

    last_checked_at: datetime
    last_release_tag: str | None = None
    last_commit_sha: str | None = None


class PipelineResult(BaseModel):
    """Summary of a full pipeline run."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    repos_checked: int = 0
    items_found: int = 0
    items_scored: int = 0
    issues_created: int = 0
    is_priming_run: bool = False
    errors: list[str] = Field(default_factory=list)
