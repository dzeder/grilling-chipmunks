"""
Process content and extract insights relevant to Ohanafy.

Uses Claude (haiku for scoring, sonnet for extraction) to analyze content,
score relevance, and generate structured insight summaries.
"""

import json
import logging
from pathlib import Path

import anthropic
import yaml

SOURCES_FILE = Path("registry/content-sources.yaml")
SCORING_CRITERIA_FILE = Path("skills/content-watcher/relevance-scoring.md")
ISSUE_TEMPLATE_FILE = Path("skills/content-watcher/issue-templates.md")

logger = logging.getLogger(__name__)


def _load_scoring_criteria() -> str:
    """Load the relevance scoring criteria from disk."""
    if SCORING_CRITERIA_FILE.exists():
        return SCORING_CRITERIA_FILE.read_text()
    return ""


def _load_issue_template() -> str:
    """Load the issue template from disk."""
    if ISSUE_TEMPLATE_FILE.exists():
        return ISSUE_TEMPLATE_FILE.read_text()
    return ""


def score_relevance(content: str, category: str) -> float:
    """Score content relevance to Ohanafy (0.0 - 1.0).

    Uses Claude haiku for fast classification.
    """
    client = anthropic.Anthropic()
    scoring_criteria = _load_scoring_criteria()

    config = yaml.safe_load(SOURCES_FILE.read_text())
    category_note = config.get("categories", {}).get(category, {}).get("note", "")

    system_prompt = f"""You are a relevance scorer for Ohanafy, a beverage supply chain SaaS platform.

Score the following content for relevance to Ohanafy on a scale of 0.0 to 1.0.

{scoring_criteria}

Category being scored: {category}
Category context: {category_note}

Respond with ONLY a JSON object: {{"score": <float>, "reason": "<one sentence>"}}
Do not include any other text."""

    # Truncate content to avoid token limits (keep first ~8000 chars)
    truncated = content[:8000] if len(content) > 8000 else content

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            system=system_prompt,
            messages=[{"role": "user", "content": truncated}],
        )
        result_text = response.content[0].text.strip()
        parsed = json.loads(result_text)
        score = float(parsed["score"])
        logger.info("Relevance score for category '%s': %.2f — %s", category, score, parsed.get("reason", ""))
        return max(0.0, min(1.0, score))
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error("Failed to parse relevance score: %s", e)
        return 0.0
    except anthropic.APIError as e:
        logger.error("Anthropic API error during scoring: %s", e)
        return 0.0


def extract_insights(content: str, source: dict) -> list[dict]:
    """Extract actionable insights from content.

    Uses Claude sonnet for reasoning and extraction.

    Returns list of insights, each with:
    - source: dict with name, episode, published, link
    - insight: 2-3 sentence plain English description
    - relevance_to_ohanafy: specific connection to Ohanafy
    - what_it_affects: skill, agent, KB section, or product feature
    - recommended_action: what to do about it
    - effort: S/M/L
    - score: 0.0-1.0
    - category: from content-sources.yaml categories
    """
    client = anthropic.Anthropic()
    issue_template = _load_issue_template()

    source_name = source.get("name", "Unknown")
    category = source.get("category", "")

    system_prompt = f"""You are an insight extractor for Ohanafy, a beverage supply chain SaaS platform built on Salesforce.

Extract actionable insights from the content that are relevant to Ohanafy's business, technology, or industry.

Ohanafy's stack: Salesforce (Apex, Flows, LWC), Tray.io (iPaaS), AWS (CDK, Lambda), Claude AI.
Ohanafy's domain: beverage distribution, 3-tier system, order management, warehouse management, retail execution, EDI, payments.

For each insight, provide a JSON object with these exact fields:
- "insight": 2-3 sentence description of what was said
- "relevance_to_ohanafy": specific connection to Ohanafy (not generic)
- "what_it_affects": which skill, agent, KB section, or product feature this affects
- "recommended_action": concrete next step
- "effort": "S" (<2h), "M" (1-2 days), or "L" (sprint+)
- "score": relevance score 0.0-1.0
- "category": "{category}"

Respond with ONLY a JSON array of insight objects. If no relevant insights, return an empty array [].
Do not include any other text.

Issue template for reference:
{issue_template}"""

    # Truncate content to avoid token limits
    truncated = content[:12000] if len(content) > 12000 else content

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Source: {source_name}\n\nContent:\n{truncated}"}],
        )
        result_text = response.content[0].text.strip()
        insights = json.loads(result_text)

        if not isinstance(insights, list):
            insights = [insights]

        # Attach source metadata to each insight
        for insight in insights:
            insight["source"] = {
                "name": source_name,
                "episode": source.get("_episode", ""),
                "published": source.get("_published", ""),
                "link": source.get("_link", ""),
            }
            insight["category"] = category

        logger.info("Extracted %d insights from %s", len(insights), source_name)
        return insights

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error("Failed to parse insights: %s", e)
        return []
    except anthropic.APIError as e:
        logger.error("Anthropic API error during extraction: %s", e)
        return []


def process_new_content(items: list[dict]) -> list[dict]:
    """Process a batch of new content items and return insights.

    Filters by minimum relevance score from content-sources.yaml config.

    Args:
        items: List of {source, episode, content, link, published, fetched_at} dicts
    """
    config = yaml.safe_load(SOURCES_FILE.read_text())
    min_score = config.get("monitor_job", {}).get("min_relevance_score", 0.65)

    insights = []
    for item in items:
        content = item.get("content", "")
        category = item["source"].get("category", "")

        score = score_relevance(content, category)
        if score >= min_score:
            # Attach episode metadata to source for extraction
            enriched_source = {**item["source"]}
            enriched_source["_episode"] = item.get("episode", "")
            enriched_source["_published"] = item.get("published", "")
            enriched_source["_link"] = item.get("link", "")

            extracted = extract_insights(content, enriched_source)
            insights.extend(extracted)
        else:
            logger.info(
                "Skipping '%s' — score %.2f below threshold %.2f",
                item.get("episode", "unknown"),
                score,
                min_score,
            )

    return insights


if __name__ == "__main__":
    print("Run via: python -m agents.content.agent")
