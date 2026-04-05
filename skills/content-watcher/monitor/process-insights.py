"""
Process transcripts and extract insights relevant to Ohanafy.

Uses Claude (sonnet tier) to analyze transcripts, score relevance,
and generate structured insight summaries.
"""

import anthropic
import yaml
from pathlib import Path

SOURCES_FILE = Path("registry/content-sources.yaml")


def score_relevance(transcript: str, category: str) -> float:
    """Score transcript relevance to Ohanafy (0.0 - 1.0).

    Uses Claude haiku for fast classification.
    """
    client = anthropic.Anthropic()
    # TODO: Implement relevance scoring
    # - Load category context from content-sources.yaml
    # - Score against Ohanafy's domain (beverage supply chain, SF, AWS, AI)
    raise NotImplementedError


def extract_insights(transcript: str, source: dict) -> list[dict]:
    """Extract actionable insights from a transcript.

    Uses Claude sonnet for reasoning and extraction.

    Returns list of insights, each with:
    - summary: 2-3 sentence plain English description
    - relevance_to_ohanafy: specific connection to Ohanafy
    - what_it_affects: skill, agent, KB section, or product feature
    - recommended_action: what to do about it
    - effort: S/M/L
    - score: 0.0-1.0
    - category: from content-sources.yaml categories
    """
    client = anthropic.Anthropic()
    # TODO: Implement insight extraction
    raise NotImplementedError


def process_new_transcripts(transcripts: list[dict]) -> list[dict]:
    """Process a batch of new transcripts and return insights.

    Filters by minimum relevance score from content-sources.yaml config.
    """
    config = yaml.safe_load(SOURCES_FILE.read_text())
    min_score = config.get("monitor_job", {}).get("min_relevance_score", 0.65)

    insights = []
    for t in transcripts:
        score = score_relevance(t["transcript"], t["source"].get("category", ""))
        if score >= min_score:
            extracted = extract_insights(t["transcript"], t["source"])
            insights.extend(extracted)

    return insights


if __name__ == "__main__":
    print("Run via: python -m agents.content.agent")
