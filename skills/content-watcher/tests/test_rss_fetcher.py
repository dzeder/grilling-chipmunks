"""Tests for the RSS fetcher module."""

import sys
from pathlib import Path

_skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_skill_dir))

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from fetchers.rss import RSSFetcher
from schema import ContentSource, RawContent, SourceType


@pytest.fixture
def rss_fetcher():
    fetcher = RSSFetcher()
    fetcher.min_interval_seconds = 0  # disable rate limiting in tests
    return fetcher


@pytest.fixture
def rss_source():
    return ContentSource(
        name="Test RSS Feed",
        url="https://example.com/feed.xml",
        source_type=SourceType.rss,
        category="ai_dev_tools",
    )


@pytest.fixture
def mock_feed_response():
    """A mock feedparser result with two entries."""
    feed = MagicMock()
    feed.bozo = False
    feed.status = 200
    feed.feed = {"title": "Test Feed"}
    feed.etag = "abc123"
    feed.modified = "Sat, 01 Apr 2026 00:00:00 GMT"

    entry1 = {
        "title": "First Post",
        "link": "https://example.com/post/1",
        "id": "guid-1",
        "summary": "Summary of the first post with <b>HTML</b>.",
        "published_parsed": (2026, 4, 1, 12, 0, 0, 0, 91, 0),
    }
    entry2 = {
        "title": "Second Post",
        "link": "https://example.com/post/2",
        "id": "guid-2",
        "summary": "Summary of the second post.",
        "published_parsed": (2026, 4, 2, 12, 0, 0, 0, 92, 0),
    }

    feed.entries = [entry1, entry2]
    return feed


class TestRSSFetcherFetchNew:
    @patch("fetchers.rss.feedparser.parse")
    def test_fetches_all_entries_on_first_run(self, mock_parse, rss_fetcher, rss_source, mock_feed_response):
        mock_parse.return_value = mock_feed_response

        items = rss_fetcher.fetch_new(rss_source, since=None)

        assert len(items) == 2
        assert items[0].title == "First Post"
        assert items[1].title == "Second Post"
        assert items[0].source_type == SourceType.rss
        assert items[0].source_name == "Test RSS Feed"

    @patch("fetchers.rss.feedparser.parse")
    def test_filters_by_since(self, mock_parse, rss_fetcher, rss_source, mock_feed_response):
        mock_parse.return_value = mock_feed_response

        since = datetime(2026, 4, 1, 23, 0, 0, tzinfo=timezone.utc)
        items = rss_fetcher.fetch_new(rss_source, since=since)

        assert len(items) == 1
        assert items[0].title == "Second Post"

    @patch("fetchers.rss.feedparser.parse")
    def test_uses_conditional_get(self, mock_parse, rss_fetcher, mock_feed_response):
        source = ContentSource(
            name="Cached Feed",
            url="https://example.com/feed.xml",
            source_type=SourceType.rss,
            category="salesforce",
            etag="old-etag",
            last_modified="Fri, 31 Mar 2026 00:00:00 GMT",
        )

        mock_parse.return_value = mock_feed_response
        rss_fetcher.fetch_new(source)

        mock_parse.assert_called_once_with(
            "https://example.com/feed.xml",
            etag="old-etag",
            modified="Fri, 31 Mar 2026 00:00:00 GMT",
        )

    @patch("fetchers.rss.feedparser.parse")
    def test_handles_304_not_modified(self, mock_parse, rss_fetcher, rss_source):
        feed = MagicMock()
        feed.bozo = False
        feed.status = 304
        feed.entries = []
        mock_parse.return_value = feed

        items = rss_fetcher.fetch_new(rss_source)
        assert items == []

    @patch("fetchers.rss.feedparser.parse")
    def test_handles_bozo_feed(self, mock_parse, rss_fetcher, rss_source):
        feed = MagicMock()
        feed.bozo = True
        feed.bozo_exception = Exception("Malformed XML")
        feed.entries = []
        mock_parse.return_value = feed

        items = rss_fetcher.fetch_new(rss_source)
        assert items == []

    @patch("fetchers.rss.feedparser.parse")
    def test_extracts_guid(self, mock_parse, rss_fetcher, rss_source, mock_feed_response):
        mock_parse.return_value = mock_feed_response

        items = rss_fetcher.fetch_new(rss_source)
        assert items[0].guid == "guid-1"
        assert items[1].guid == "guid-2"

    @patch("fetchers.rss.feedparser.parse")
    def test_extracts_podcast_enclosure(self, mock_parse, rss_fetcher, rss_source):
        feed = MagicMock()
        feed.bozo = False
        feed.status = 200
        feed.feed = {"title": "Podcast Feed"}

        entry = {
            "title": "Episode 42",
            "link": "https://example.com/ep42",
            "id": "ep42",
            "summary": "Episode description",
            "published_parsed": (2026, 4, 1, 12, 0, 0, 0, 91, 0),
            "enclosures": [{"href": "https://example.com/ep42.mp3", "type": "audio/mpeg"}],
        }
        feed.entries = [entry]
        mock_parse.return_value = feed

        items = rss_fetcher.fetch_new(rss_source)
        assert items[0].metadata["enclosure_url"] == "https://example.com/ep42.mp3"
        assert items[0].metadata["enclosure_type"] == "audio/mpeg"


class TestRSSFetcherNormalize:
    def test_strips_html(self, rss_fetcher):
        raw = RawContent(
            title="  Test Title  ",
            body="<p>Hello <b>world</b>!</p>",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
        )

        normalized = rss_fetcher.normalize(raw)
        assert normalized.title == "Test Title"
        assert "<" not in normalized.body
        assert "Hello" in normalized.body
        assert "world" in normalized.body

    def test_truncates_long_body(self, rss_fetcher):
        raw = RawContent(
            title="Long Post",
            body="x" * 20000,
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
        )

        normalized = rss_fetcher.normalize(raw)
        assert normalized.truncated is True
        assert len(normalized.body) == 16000
        assert normalized.token_count == 4000
