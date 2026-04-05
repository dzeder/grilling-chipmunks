"""
Create GitHub issues for Tray.io connector discovery opportunities.

Every issue must include all required fields or it is rejected before posting.
See issue-templates.md for the full template.
"""

import os
import logging

import httpx
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

REGISTRY_FILE = Path("registry/tray-connectors.yaml")

REQUIRED_FIELDS = [
    "connector_name",
    "category",
    "opportunity",
    "relevance_to_ohanafy",
    "what_it_affects",
    "recommended_action",
    "effort",
    "score",
    "opportunity_type",
]


def validate_opportunity(data: dict) -> bool:
    """Validate that all required fields are present."""
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return True


def format_issue_body(data: dict) -> str:
    """Format opportunity data into GitHub issue markdown body."""
    return f"""## Connector
- Name: {data['connector_name']}
- Category: {data['category']}
- Documentation: {data.get('documentation_url', 'N/A')}
- Operations Available: {data.get('operation_count', 'unknown')}

## The Opportunity
{data['opportunity']}

## Why It's Relevant to Ohanafy
{data['relevance_to_ohanafy']}

## What It Affects
{data['what_it_affects']}

## Recommended Action
{data['recommended_action']}

## Current Status: {data.get('current_usage', 'not_configured')}
## Relevance Score: {data['score']}
## Category: {data['category']}
## Effort: {data['effort']}
"""


def create_issue(data: dict) -> dict:
    """Create a GitHub issue for a connector opportunity.

    Returns the created issue data from GitHub API.
    """
    validate_opportunity(data)

    config = yaml.safe_load(REGISTRY_FILE.read_text())
    repo = config.get("discovery_job", {}).get("github_repo", "ohanafy/ai-ops")
    category_config = config.get("categories", {}).get(data["category"], {})
    labels = category_config.get("issue_labels", ["tray-discovery"])

    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }

    body = format_issue_body(data)
    title = f"[Tray Discovery] {data['connector_name']} — {data['opportunity_type']}"

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
    result = response.json()
    logger.info("Created issue #%s: %s", result.get("number"), title)
    return result


if __name__ == "__main__":
    print("Run via: python -m skills.tray_ai.discovery.commands.run_discovery")
