"""Tests for relevance scoring and insight extraction."""

import sys
from pathlib import Path

_skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_skill_dir))

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from monitor.process_insights import (
    score_relevance,
    extract_insights,
    process_new_content,
    SCORING_MODEL,
    EXTRACTION_MODEL,
)
from schema import NormalizedContent, ScoredContent, SourceType


@pytest.fixture
def sample_content():
    return NormalizedContent(
        title="Salesforce announces new Flow batch processing",
        body="Salesforce has launched a new Flow feature that enables batch processing of up to 50,000 records. "
        "This is particularly useful for ISVs building managed packages with complex data transformations.",
        url="https://developer.salesforce.com/blogs/2026/04/flow-batch",
        published_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        source_type=SourceType.rss,
        source_name="Salesforce Developers Blog",
        token_count=50,
        truncated=False,
        metadata={"category": "salesforce"},
    )


@pytest.fixture
def mock_claude_scoring_response():
    response = MagicMock()
    response.content = [
        MagicMock(text=json.dumps({
            "score": 0.88,
            "category": "salesforce",
            "reasoning": "Directly relevant to Ohanafy's Salesforce managed package architecture.",
        }))
    ]
    return response


@pytest.fixture
def mock_claude_extraction_response():
    insights = [
        {
            "source": {
                "name": "Salesforce Developers Blog",
                "episode": "Flow Batch Processing",
                "published": "2026-04-01",
                "timestamp": "general theme",
                "link": "https://developer.salesforce.com/blogs/2026/04/flow-batch",
            },
            "insight": "Salesforce's new Flow batch processing supports 50K records, enabling managed package ISVs to build complex transformations without Apex.",
            "relevance_to_ohanafy": "Ohanafy's OHFY-Core package could replace Apex batch jobs with declarative Flow batch steps.",
            "what_it_affects": "skills/salesforce/flow",
            "recommended_action": "Update supporting MD in skills/salesforce/flow/",
            "effort": "M",
            "score": 0.88,
            "category": "salesforce",
        }
    ]
    response = MagicMock()
    response.content = [MagicMock(text=json.dumps(insights))]
    return response


class TestScoreRelevance:
    @patch("monitor.process_insights.anthropic.Anthropic")
    def test_scores_content(self, mock_anthropic_cls, sample_content, mock_claude_scoring_response):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_claude_scoring_response
        mock_anthropic_cls.return_value = mock_client

        scored = score_relevance(sample_content, "salesforce")

        assert isinstance(scored, ScoredContent)
        assert scored.score == 0.88
        assert scored.category == "salesforce"
        assert "managed package" in scored.scoring_reasoning

    @patch("monitor.process_insights.anthropic.Anthropic")
    def test_uses_haiku_model(self, mock_anthropic_cls, sample_content, mock_claude_scoring_response):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_claude_scoring_response
        mock_anthropic_cls.return_value = mock_client

        score_relevance(sample_content, "salesforce")

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == SCORING_MODEL

    @patch("monitor.process_insights.anthropic.Anthropic")
    def test_handles_parse_error(self, mock_anthropic_cls, sample_content):
        response = MagicMock()
        response.content = [MagicMock(text="not json")]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = response
        mock_anthropic_cls.return_value = mock_client

        scored = score_relevance(sample_content, "salesforce")
        assert scored.score == 0.0
        assert "Parse error" in scored.scoring_reasoning


class TestExtractInsights:
    @patch("monitor.process_insights.anthropic.Anthropic")
    def test_extracts_insights(self, mock_anthropic_cls, mock_claude_extraction_response):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_claude_extraction_response
        mock_anthropic_cls.return_value = mock_client

        scored = ScoredContent(
            title="Flow Batch Processing",
            body="Content about flow batch processing.",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="SF Blog",
            score=0.88,
            category="salesforce",
        )

        insights = extract_insights(scored)

        assert len(insights) == 1
        assert "50K records" in insights[0].insight
        assert insights[0].effort == "M"
        assert insights[0].category == "salesforce"

    @patch("monitor.process_insights.anthropic.Anthropic")
    def test_uses_sonnet_model(self, mock_anthropic_cls, mock_claude_extraction_response):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_claude_extraction_response
        mock_anthropic_cls.return_value = mock_client

        scored = ScoredContent(
            title="Test",
            body="Test body",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            score=0.9,
            category="salesforce",
        )

        extract_insights(scored)

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == EXTRACTION_MODEL

    @patch("monitor.process_insights.anthropic.Anthropic")
    def test_handles_empty_response(self, mock_anthropic_cls):
        response = MagicMock()
        response.content = [MagicMock(text="[]")]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = response
        mock_anthropic_cls.return_value = mock_client

        scored = ScoredContent(
            title="Irrelevant",
            body="Nothing actionable",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            score=0.7,
            category="salesforce",
        )

        insights = extract_insights(scored)
        assert insights == []


class TestProcessNewContent:
    @patch("monitor.process_insights.extract_insights")
    @patch("monitor.process_insights.score_relevance")
    @patch("monitor.process_insights.SOURCES_FILE")
    def test_filters_by_threshold(self, mock_file, mock_score, mock_extract, sample_content):
        mock_file.read_text.return_value = "monitor_job:\n  min_relevance_score: 0.65"

        high_score = ScoredContent(
            title="High",
            body="High relevance",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            score=0.9,
            category="salesforce",
        )
        low_score = ScoredContent(
            title="Low",
            body="Low relevance",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            score=0.3,
            category="salesforce",
        )

        mock_score.side_effect = [high_score, low_score]
        mock_extract.return_value = []

        low_content = NormalizedContent(
            title="Low relevance",
            body="Not relevant",
            url="https://example.com",
            source_type=SourceType.rss,
            source_name="Feed",
            metadata={"category": "salesforce"},
        )

        process_new_content([sample_content, low_content])

        # extract_insights should only be called for the high-scoring item
        assert mock_extract.call_count == 1
