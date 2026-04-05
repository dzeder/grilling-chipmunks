"""End-to-end tests for the content-watcher pipeline."""

import sys
from pathlib import Path

_skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_skill_dir))

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from schema import (
    ContentSource,
    FetchResult,
    NormalizedContent,
    PipelineRunResult,
    SourceType,
)


MOCK_SOURCES_YAML = """\
version: "1.0"
sources:
  - name: "Test RSS"
    url: "https://example.com/feed.xml"
    source_type: rss
    category: salesforce
    enabled: true
  - name: "r/test"
    url: "https://www.reddit.com/r/test/"
    source_type: reddit
    category: ai_dev_tools
    enabled: true
  - name: "Disabled Source"
    url: "https://example.com/disabled"
    source_type: rss
    category: salesforce
    enabled: false
monitor_job:
  min_relevance_score: 0.65
"""


class TestLoadSources:
    @patch("monitor.fetch_transcripts.SOURCES_FILE")
    def test_loads_enabled_sources(self, mock_file):
        mock_file.read_text.return_value = MOCK_SOURCES_YAML

        from monitor.fetch_transcripts import load_sources

        sources = load_sources()

        assert len(sources) == 2
        assert sources[0].name == "Test RSS"
        assert sources[0].source_type == SourceType.rss
        assert sources[1].name == "r/test"
        assert sources[1].source_type == SourceType.reddit

    @patch("monitor.fetch_transcripts.SOURCES_FILE")
    def test_handles_empty_sources(self, mock_file):
        mock_file.read_text.return_value = "sources: []\n"

        from monitor.fetch_transcripts import load_sources

        sources = load_sources()
        assert sources == []


class TestFetchAllNew:
    @patch("monitor.fetch_transcripts.update_source_timestamp")
    @patch("monitor.fetch_transcripts.get_fetcher")
    @patch("monitor.fetch_transcripts.get_registered_types")
    @patch("monitor.fetch_transcripts.load_sources")
    def test_full_fetch_cycle(self, mock_load, mock_types, mock_get_fetcher, mock_update):
        from monitor.fetch_transcripts import fetch_all_new
        from schema import RawContent

        mock_load.return_value = [
            ContentSource(
                name="Test RSS",
                url="https://example.com/feed.xml",
                source_type=SourceType.rss,
                category="salesforce",
            )
        ]
        mock_types.return_value = [SourceType.rss, SourceType.reddit]

        mock_fetcher = MagicMock()
        raw = RawContent(
            title="Test Post",
            body="Test body content",
            url="https://example.com/post/1",
            source_type=SourceType.rss,
            source_name="Test RSS",
        )
        mock_fetcher.fetch_new.return_value = [raw]
        mock_fetcher.normalize.return_value = NormalizedContent(
            title="Test Post",
            body="Test body content",
            url="https://example.com/post/1",
            source_type=SourceType.rss,
            source_name="Test RSS",
            metadata={},
        )
        mock_get_fetcher.return_value = mock_fetcher

        items, result = fetch_all_new()

        assert len(items) == 1
        assert items[0].title == "Test Post"
        assert result.sources_checked == 1
        assert result.items_fetched == 1
        assert result.errors == []
        mock_update.assert_called_once()

    @patch("monitor.fetch_transcripts.update_source_timestamp")
    @patch("monitor.fetch_transcripts.get_fetcher")
    @patch("monitor.fetch_transcripts.get_registered_types")
    @patch("monitor.fetch_transcripts.load_sources")
    def test_handles_fetcher_error(self, mock_load, mock_types, mock_get_fetcher, mock_update):
        from monitor.fetch_transcripts import fetch_all_new

        mock_load.return_value = [
            ContentSource(
                name="Broken Feed",
                url="https://broken.com/feed",
                source_type=SourceType.rss,
                category="salesforce",
            )
        ]
        mock_types.return_value = [SourceType.rss]

        mock_fetcher = MagicMock()
        mock_fetcher.fetch_new.side_effect = Exception("Connection timeout")
        mock_get_fetcher.return_value = mock_fetcher

        items, result = fetch_all_new()

        assert len(items) == 0
        assert result.sources_checked == 1
        assert len(result.errors) == 1
        assert "Connection timeout" in result.errors[0]

    @patch("monitor.fetch_transcripts.load_sources")
    def test_skips_unregistered_source_types(self, mock_load):
        from monitor.fetch_transcripts import fetch_all_new

        mock_load.return_value = [
            ContentSource(
                name="YouTube Channel",
                url="https://youtube.com/@test",
                source_type=SourceType.youtube,
                category="ai_dev_tools",
            )
        ]

        with patch("monitor.fetch_transcripts.get_registered_types", return_value=[SourceType.rss, SourceType.reddit]):
            items, result = fetch_all_new()

        assert len(items) == 0
        assert len(result.errors) == 1
        assert "No fetcher for youtube" in result.errors[0]
