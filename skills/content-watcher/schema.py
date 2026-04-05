"""
Pydantic schemas for the content-watcher pipeline.

Data flows: fetch → normalize → score → route → store.
Each stage has a distinct model at its boundary.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Supported content source types."""

    rss = "rss"
    youtube = "youtube"
    reddit = "reddit"
    web_page = "web_page"
    podcast = "podcast"


class ContentSource(BaseModel):
    """A single entry in registry/content-sources.yaml."""

    name: str = Field(description="Display name for the source")
    url: str = Field(description="Source URL (RSS feed, subreddit, YouTube channel, etc.)")
    source_type: SourceType = Field(description="Type of source")
    category: str = Field(description="Category from content-sources.yaml (beverage_industry, salesforce, etc.)")
    enabled: bool = Field(default=True, description="Whether this source is actively monitored")
    last_checked: datetime | None = Field(default=None, description="When this source was last fetched")
    etag: str | None = Field(default=None, description="HTTP ETag for conditional GET (RSS)")
    last_modified: str | None = Field(default=None, description="HTTP Last-Modified for conditional GET (RSS)")


class RawContent(BaseModel):
    """Raw content fetched from a source, before normalization."""

    title: str = Field(description="Title of the content item")
    body: str = Field(description="Full text body, transcript, or post content")
    url: str = Field(description="Direct link to the content item")
    published_at: datetime | None = Field(default=None, description="When the content was published")
    source_type: SourceType = Field(description="Type of source this came from")
    source_name: str = Field(description="Name of the source")
    guid: str | None = Field(default=None, description="Unique ID for deduplication (RSS GUID, Reddit ID, etc.)")
    metadata: dict = Field(default_factory=dict, description="Source-specific metadata (score, comments, enclosure, etc.)")


class NormalizedContent(BaseModel):
    """Content after HTML stripping, truncation, and timestamp normalization."""

    title: str
    body: str = Field(description="Cleaned text body, truncated to token budget")
    url: str
    published_at: datetime | None = None
    source_type: SourceType
    source_name: str
    guid: str | None = None
    token_count: int = Field(default=0, description="Estimated token count of the body")
    truncated: bool = Field(default=False, description="Whether body was truncated to fit token budget")
    metadata: dict = Field(default_factory=dict)


class ScoredContent(BaseModel):
    """Content after Claude haiku relevance scoring."""

    title: str
    body: str
    url: str
    published_at: datetime | None = None
    source_type: SourceType
    source_name: str
    guid: str | None = None
    score: float = Field(ge=0.0, le=1.0, description="Relevance score from Claude haiku")
    category: str = Field(description="Matched category from content-sources.yaml")
    scoring_reasoning: str = Field(default="", description="Why Claude scored it this way")
    model_used: str = Field(default="claude-haiku-4-5-20251001", description="Model used for scoring")
    metadata: dict = Field(default_factory=dict)


class InsightAction(str, Enum):
    """Routing action based on relevance score."""

    auto_issue = "auto_issue"
    team_triage = "team_triage"
    log_only = "log_only"


class ExtractedInsight(BaseModel):
    """A structured insight extracted from high-relevance content."""

    source: dict = Field(description="Source metadata: name, episode, published, timestamp, link")
    insight: str = Field(description="2-3 sentence plain English description of the insight")
    relevance_to_ohanafy: str = Field(description="Specific connection to Ohanafy")
    what_it_affects: str = Field(description="Specific skill, agent, KB section, or product feature")
    recommended_action: str = Field(description="What to do about it")
    effort: str = Field(description="S (<2h) / M (1-2 days) / L (sprint+)")
    score: float = Field(ge=0.0, le=1.0)
    category: str


class RoutedInsight(BaseModel):
    """An insight after routing decision."""

    insight: ExtractedInsight
    action: InsightAction
    issue_url: str | None = Field(default=None, description="GitHub issue URL if created")


class FetchResult(BaseModel):
    """Result of fetching from a single source."""

    source_name: str
    source_type: SourceType
    items_found: int = 0
    items_new: int = 0
    errors: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0


class PipelineRunResult(BaseModel):
    """Result of a full pipeline run across all sources."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources_checked: int = 0
    items_fetched: int = 0
    insights_created: int = 0
    issues_created: int = 0
    errors: list[str] = Field(default_factory=list)
    fetch_results: list[FetchResult] = Field(default_factory=list)
