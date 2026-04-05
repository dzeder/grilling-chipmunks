"""
RSS/Atom feed fetcher for the content-watcher pipeline.

Handles standard RSS 2.0, Atom feeds, and Podcasting 2.0 transcript tags.
Uses feedparser with conditional GET (ETag/If-Modified-Since) to avoid
re-fetching unchanged feeds.
"""

import logging
from datetime import datetime, timezone
from time import mktime

import feedparser

from fetchers import register
from fetchers.base import BaseFetcher
from schema import ContentSource, RawContent, SourceType

logger = logging.getLogger(__name__)


@register(SourceType.rss)
class RSSFetcher(BaseFetcher):
    """Fetches content from RSS and Atom feeds."""

    source_type = SourceType.rss
    min_interval_seconds = 2

    def fetch_new(
        self, source: ContentSource, since: datetime | None = None
    ) -> list[RawContent]:
        """Fetch new entries from an RSS/Atom feed.

        Uses conditional GET via ETag and Last-Modified headers to avoid
        re-downloading unchanged feeds.
        """
        self._rate_limit()

        # Build conditional GET headers
        kwargs = {}
        if source.etag:
            kwargs["etag"] = source.etag
        if source.last_modified:
            kwargs["modified"] = source.last_modified

        feed = feedparser.parse(source.url, **kwargs)

        # Check for errors
        if feed.bozo and not feed.entries:
            error_msg = str(feed.bozo_exception) if feed.bozo_exception else "Unknown feed error"
            logger.warning("Feed error for %s: %s", source.name, error_msg)
            return []

        # 304 Not Modified — nothing new
        if feed.status == 304 if hasattr(feed, "status") else False:
            logger.debug("Feed %s not modified since last check", source.name)
            return []

        items = []
        for entry in feed.entries:
            published = self._parse_date(entry)

            # Skip items older than last check
            if since and published and published <= since:
                continue

            body = self._extract_body(entry)
            guid = entry.get("id") or entry.get("link", "")

            metadata = {}
            # Check for podcast enclosure (audio URL)
            if entry.get("enclosures"):
                metadata["enclosure_url"] = entry.enclosures[0].get("href", "")
                metadata["enclosure_type"] = entry.enclosures[0].get("type", "")

            # Check for podcast:transcript tag (Podcasting 2.0)
            transcript_url = self._find_transcript(entry)
            if transcript_url:
                metadata["transcript_url"] = transcript_url

            items.append(
                RawContent(
                    title=entry.get("title", "Untitled"),
                    body=body,
                    url=entry.get("link", source.url),
                    published_at=published,
                    source_type=SourceType.rss,
                    source_name=source.name,
                    guid=guid,
                    metadata=metadata,
                )
            )

        logger.info("Fetched %d new items from %s", len(items), source.name)
        return items

    def get_feed_metadata(self, feed) -> dict:
        """Extract ETag and Last-Modified for storage on the ContentSource."""
        return {
            "etag": getattr(feed, "etag", None),
            "last_modified": getattr(feed, "modified", None),
        }

    @staticmethod
    def _parse_date(entry) -> datetime | None:
        """Parse entry published date to timezone-aware datetime."""
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
        return None

    @staticmethod
    def _extract_body(entry) -> str:
        """Extract the best available body text from an entry."""
        # Prefer content:encoded, then summary, then description
        if entry.get("content"):
            return entry.content[0].get("value", "")
        return entry.get("summary", entry.get("description", ""))

    @staticmethod
    def _find_transcript(entry) -> str | None:
        """Look for podcast:transcript tag in entry."""
        # feedparser exposes namespaced elements via the entry dict
        # Podcasting 2.0 transcript: <podcast:transcript url="..." type="text/plain"/>
        for key in entry:
            if "transcript" in key.lower():
                val = entry[key]
                if isinstance(val, dict) and val.get("url"):
                    return val["url"]
                if isinstance(val, str) and val.startswith("http"):
                    return val
        return None
