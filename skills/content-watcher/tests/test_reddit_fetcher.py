"""Tests for the Reddit fetcher module."""

import sys
from pathlib import Path

_skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_skill_dir))

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from fetchers.reddit import RedditFetcher
from schema import ContentSource, SourceType


@pytest.fixture
def reddit_fetcher():
    fetcher = RedditFetcher()
    fetcher.min_interval_seconds = 0
    return fetcher


@pytest.fixture
def reddit_source():
    return ContentSource(
        name="r/salesforce",
        url="https://www.reddit.com/r/salesforce/",
        source_type=SourceType.reddit,
        category="salesforce",
    )


@pytest.fixture
def mock_reddit_response():
    """Mock Reddit JSON API response with two posts."""
    return {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "post1",
                        "title": "New Salesforce Flow feature",
                        "selftext": "Has anyone tried the new batch flow feature? It seems great for bulk processing.",
                        "permalink": "/r/salesforce/comments/post1/new_salesforce_flow_feature/",
                        "created_utc": 1743552000.0,  # 2025-04-02 00:00:00 UTC
                        "score": 42,
                        "num_comments": 12,
                        "subreddit": "salesforce",
                        "is_self": True,
                        "url": "https://www.reddit.com/r/salesforce/comments/post1/",
                    }
                },
                {
                    "data": {
                        "id": "post2",
                        "title": "Apex best practices 2026",
                        "selftext": "",
                        "permalink": "/r/salesforce/comments/post2/apex_best_practices/",
                        "created_utc": 1743465600.0,  # 2025-04-01 00:00:00 UTC
                        "score": 15,
                        "num_comments": 3,
                        "subreddit": "salesforce",
                        "is_self": False,
                        "url": "https://blog.example.com/apex-practices",
                    }
                },
            ]
        }
    }


class TestRedditFetcherFetchNew:
    @patch("fetchers.reddit.httpx.get")
    def test_fetches_all_posts_on_first_run(self, mock_get, reddit_fetcher, reddit_source, mock_reddit_response):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_reddit_response
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        items = reddit_fetcher.fetch_new(reddit_source, since=None)

        assert len(items) == 2
        assert items[0].title == "New Salesforce Flow feature"
        assert items[0].source_type == SourceType.reddit
        assert items[0].guid == "post1"
        assert items[0].metadata["score"] == 42

    @patch("fetchers.reddit.httpx.get")
    def test_filters_by_since(self, mock_get, reddit_fetcher, reddit_source, mock_reddit_response):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_reddit_response
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        since = datetime(2025, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
        items = reddit_fetcher.fetch_new(reddit_source, since=since)

        assert len(items) == 1
        assert items[0].title == "New Salesforce Flow feature"

    @patch("fetchers.reddit.httpx.get")
    def test_builds_body_from_selftext(self, mock_get, reddit_fetcher, reddit_source, mock_reddit_response):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_reddit_response
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        items = reddit_fetcher.fetch_new(reddit_source)

        assert "New Salesforce Flow feature" in items[0].body
        assert "batch flow feature" in items[0].body
        assert items[1].body == "Apex best practices 2026"

    @patch("fetchers.reddit.httpx.get")
    def test_constructs_reddit_url(self, mock_get, reddit_fetcher, reddit_source, mock_reddit_response):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_reddit_response
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        items = reddit_fetcher.fetch_new(reddit_source)
        assert items[0].url == "https://www.reddit.com/r/salesforce/comments/post1/new_salesforce_flow_feature/"

    @patch("fetchers.reddit.httpx.get")
    def test_calls_correct_url(self, mock_get, reddit_fetcher, reddit_source, mock_reddit_response):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_reddit_response
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        reddit_fetcher.fetch_new(reddit_source)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://www.reddit.com/r/salesforce/new.json"

    @patch("fetchers.reddit.httpx.get")
    def test_handles_request_error(self, mock_get, reddit_fetcher, reddit_source):
        import httpx as httpx_mod
        mock_get.side_effect = httpx_mod.RequestError("Connection failed")

        items = reddit_fetcher.fetch_new(reddit_source)
        assert items == []

    @patch("fetchers.reddit.httpx.get")
    def test_captures_metadata(self, mock_get, reddit_fetcher, reddit_source, mock_reddit_response):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_reddit_response
        response.raise_for_status = MagicMock()
        mock_get.return_value = response

        items = reddit_fetcher.fetch_new(reddit_source)

        assert items[0].metadata["score"] == 42
        assert items[0].metadata["num_comments"] == 12
        assert items[0].metadata["subreddit"] == "salesforce"
        assert items[0].metadata["is_self"] is True
        assert items[1].metadata["link_url"] == "https://blog.example.com/apex-practices"
