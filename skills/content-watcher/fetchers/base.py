"""
Base fetcher abstract class for the content-watcher pipeline.

All fetchers inherit from BaseFetcher and implement fetch_new().
Shared normalization (HTML stripping, truncation) lives here.
"""

import html
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime

from schema import (
    ContentSource,
    NormalizedContent,
    RawContent,
    SourceType,
)

# Target ~4000 tokens for scoring, ~1 token ≈ 4 chars
MAX_BODY_CHARS = 16000


class BaseFetcher(ABC):
    """Abstract base class for content fetchers."""

    source_type: SourceType
    min_interval_seconds: int = 5

    def __init__(self):
        self._last_request_time: float = 0.0

    def _rate_limit(self):
        """Enforce minimum interval between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)
        self._last_request_time = time.time()

    @abstractmethod
    def fetch_new(
        self, source: ContentSource, since: datetime | None = None
    ) -> list[RawContent]:
        """Fetch new content items from this source since the given time.

        Args:
            source: The content source configuration.
            since: Only return items published after this time. None = first run, get recent items.

        Returns:
            List of raw content items.
        """
        ...

    def normalize(self, raw: RawContent) -> NormalizedContent:
        """Normalize raw content: strip HTML, truncate, estimate tokens."""
        cleaned = self._strip_html(raw.body)
        truncated = False

        if len(cleaned) > MAX_BODY_CHARS:
            cleaned = cleaned[:MAX_BODY_CHARS]
            truncated = True

        token_count = len(cleaned) // 4  # rough estimate

        return NormalizedContent(
            title=raw.title.strip(),
            body=cleaned,
            url=raw.url,
            published_at=raw.published_at,
            source_type=raw.source_type,
            source_name=raw.source_name,
            guid=raw.guid,
            token_count=token_count,
            truncated=truncated,
            metadata=raw.metadata,
        )

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags and decode entities."""
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
