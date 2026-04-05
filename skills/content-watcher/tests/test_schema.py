"""Tests for content-watcher pipeline schemas."""

import sys
from pathlib import Path

# Add skill directory to sys.path for hyphenated dir imports
_skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_skill_dir))

import pytest
from datetime import datetime, timezone

from schema import (
    ContentSource,
    ExtractedInsight,
    FetchResult,
    InsightAction,
    NormalizedContent,
    PipelineRunResult,
    RawContent,
    RoutedInsight,
    ScoredContent,
    SourceType,
)


class TestSourceType:
    def test_enum_values(self):
        assert SourceType.rss == "rss"
        assert SourceType.reddit == "reddit"
        assert SourceType.youtube == "youtube"
        assert SourceType.web_page == "web_page"
        assert SourceType.podcast == "podcast"

    def test_from_string(self):
        assert SourceType("rss") == SourceType.rss
        assert SourceType("reddit") == SourceType.reddit


class TestContentSource:
    def test_minimal(self):
        source = ContentSource(
            name="Test Feed",
            url="https://example.com/feed",
            source_type=SourceType.rss,
            category="ai_dev_tools",
        )
        assert source.enabled is True
        assert source.last_checked is None
        assert source.etag is None

    def test_full(self):
        now = datetime.now(timezone.utc)
        source = ContentSource(
            name="r/salesforce",
            url="https://www.reddit.com/r/salesforce/",
            source_type=SourceType.reddit,
            category="salesforce",
            enabled=True,
            last_checked=now,
        )
        assert source.last_checked == now


class TestRawContent:
    def test_minimal(self):
        raw = RawContent(
            title="Test Post",
            body="Some content here",
            url="https://example.com/post/1",
            source_type=SourceType.rss,
            source_name="Test Feed",
        )
        assert raw.published_at is None
        assert raw.metadata == {}
        assert raw.guid is None

    def test_with_metadata(self):
        raw = RawContent(
            title="Reddit Post",
            body="Post body",
            url="https://reddit.com/r/test/1",
            source_type=SourceType.reddit,
            source_name="r/test",
            guid="abc123",
            metadata={"score": 42, "num_comments": 5},
        )
        assert raw.metadata["score"] == 42


class TestNormalizedContent:
    def test_truncation_flag(self):
        norm = NormalizedContent(
            title="Test",
            body="Short body",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            token_count=3,
            truncated=False,
        )
        assert norm.truncated is False

    def test_truncated(self):
        norm = NormalizedContent(
            title="Test",
            body="x" * 16000,
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            token_count=4000,
            truncated=True,
        )
        assert norm.truncated is True


class TestScoredContent:
    def test_score_bounds(self):
        scored = ScoredContent(
            title="Test",
            body="Body",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            score=0.87,
            category="salesforce",
            scoring_reasoning="Relevant to SF DevOps",
        )
        assert scored.score == 0.87

    def test_score_too_low(self):
        with pytest.raises(Exception):
            ScoredContent(
                title="Test",
                body="Body",
                url="https://example.com",
                source_type=SourceType.rss,
                source_name="Feed",
                score=-0.1,
                category="salesforce",
            )

    def test_score_too_high(self):
        with pytest.raises(Exception):
            ScoredContent(
                title="Test",
                body="Body",
                url="https://example.com",
                source_type=SourceType.rss,
                source_name="Feed",
                score=1.1,
                category="salesforce",
            )


class TestExtractedInsight:
    def test_all_fields(self):
        insight = ExtractedInsight(
            source={"name": "Test", "episode": "Ep 1", "published": "2026-04-01", "timestamp": "general theme", "link": "https://example.com"},
            insight="Salesforce announced a new Flow feature for batch processing.",
            relevance_to_ohanafy="Directly applicable to OMS order batch processing flows.",
            what_it_affects="skills/salesforce/flow",
            recommended_action="Update supporting MD in skills/salesforce/flow/",
            effort="S",
            score=0.92,
            category="salesforce",
        )
        assert insight.effort == "S"
        assert insight.score == 0.92


class TestInsightAction:
    def test_values(self):
        assert InsightAction.auto_issue == "auto_issue"
        assert InsightAction.team_triage == "team_triage"
        assert InsightAction.log_only == "log_only"


class TestRoutedInsight:
    def test_with_issue(self):
        insight = ExtractedInsight(
            source={"name": "Test"},
            insight="Test insight",
            relevance_to_ohanafy="Test relevance",
            what_it_affects="skills/test",
            recommended_action="No action",
            effort="S",
            score=0.9,
            category="salesforce",
        )
        routed = RoutedInsight(
            insight=insight,
            action=InsightAction.auto_issue,
            issue_url="https://github.com/ohanafy/ai-ops/issues/42",
        )
        assert routed.issue_url is not None


class TestFetchResult:
    def test_defaults(self):
        result = FetchResult(source_name="Test", source_type=SourceType.rss)
        assert result.items_found == 0
        assert result.errors == []


class TestPipelineRunResult:
    def test_defaults(self):
        result = PipelineRunResult()
        assert result.sources_checked == 0
        assert result.items_fetched == 0
        assert result.insights_created == 0
        assert result.issues_created == 0
