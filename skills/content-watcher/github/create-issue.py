"""
Create GitHub issues for content insights.

Every insight must include all required fields or it is rejected.
See issue-templates.md for the full template.
"""

import os
import httpx
import yaml
from pathlib import Path

SOURCES_FILE = Path("registry/content-sources.yaml")

REQUIRED_FIELDS = [
    "source",
    "insight",
    "relevance_to_ohanafy",
    "what_it_affects",
    "recommended_action",
    "effort",
    "score",
    "category",
]


def validate_insight(insight: dict) -> bool:
    """Validate that all required fields are present."""
    missing = [f for f in REQUIRED_FIELDS if not insight.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return True


def format_issue_body(insight: dict) -> str:
    """Format insight into GitHub issue markdown body."""
    return f"""## Source
- Show/Channel: {insight['source'].get('name', 'Unknown')}
- Episode/Video: {insight['source'].get('episode', 'Unknown')}
- Published: {insight['source'].get('published', 'Unknown')}
- Timestamp: {insight['source'].get('timestamp', 'general theme')}
- Link: {insight['source'].get('link', 'N/A')}

## The Insight
{insight['insight']}

## Why It's Relevant to Ohanafy
{insight['relevance_to_ohanafy']}

## What It Affects
{insight['what_it_affects']}

## Recommended Action
{insight['recommended_action']}

## Effort: {insight['effort']}
## Relevance Score: {insight['score']}
## Category: {insight['category']}
"""


def create_issue(insight: dict) -> dict:
    """Create a GitHub issue for an insight.

    Returns the created issue data from GitHub API.
    """
    validate_insight(insight)

    config = yaml.safe_load(SOURCES_FILE.read_text())
    repo = config.get("monitor_job", {}).get("github_repo", "ohanafy/ai-ops")
    category_config = config.get("categories", {}).get(insight["category"], {})
    labels = category_config.get("issue_labels", ["content-insight"])

    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }

    body = format_issue_body(insight)
    title = f"[Content Insight] {insight['insight'][:80]}"

    response = httpx.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers=headers,
        json={
            "title": title,
            "body": body,
            "labels": labels,
        },
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print("Run via: python -m agents.content.agent")
