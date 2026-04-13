"""
Slack digest posting for the repo-watchers pipeline.

Posts a weekly summary to the configured Slack channel via webhook.
"""

import logging
import os
from datetime import datetime, timezone

import httpx

from .schema import PipelineResult, RouteAction, RoutedItem

logger = logging.getLogger(__name__)

CATEGORY_EMOJI = {
    "ai": ":robot_face:",
    "salesforce": ":cloud:",
    "tray_and_ipaas": ":link:",
    "aws": ":aws:",
    "observability": ":mag:",
    "docs": ":books:",
    "cicd": ":gear:",
    "security": ":lock:",
    "support": ":busts_in_silhouette:",
}


def _build_digest_blocks(
    result: PipelineResult,
    routed_items: list[RoutedItem],
) -> list[dict]:
    """Build Slack Block Kit blocks for the weekly digest."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    blocks: list[dict] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Repo Watcher Weekly Digest — {now}"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{result.repos_checked}* repos checked | "
                    f"*{result.items_found}* changes found | "
                    f"*{result.items_scored}* scored | "
                    f"*{result.issues_created}* issues created"
                ),
            },
        },
    ]

    if result.is_priming_run:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":seedling: *Priming run* — baselines set, no issues created. Next run will detect new changes.",
            },
        })
        return blocks

    # Group actionable items by category
    actionable = [r for r in routed_items if r.action != RouteAction.log_only]
    if not actionable:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "No actionable changes this week. :white_check_mark:"},
        })
        return blocks

    by_category: dict[str, list[RoutedItem]] = {}
    for item in actionable:
        cat = item.metadata.get("category", "unknown")
        by_category.setdefault(cat, []).append(item)

    for category, items in sorted(by_category.items()):
        emoji = CATEGORY_EMOJI.get(category, ":pushpin:")
        lines = []
        for item in sorted(items, key=lambda x: x.score, reverse=True):
            score_bar = ":large_red_square:" if item.score >= 0.85 else ":large_yellow_square:"
            issue_link = f" — <{item.issue_url}|issue>" if item.issue_url else ""
            lines.append(f"{score_bar} `{item.score:.2f}` *{item.repo}* — {item.title[:50]}{issue_link}")

        blocks.append({"type": "divider"})
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{category.replace('_', ' ').title()}*\n" + "\n".join(lines),
            },
        })

    if result.errors:
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":warning: *{len(result.errors)} error(s)* during this run",
            },
        })

    return blocks


def post_digest(
    result: PipelineResult,
    routed_items: list[RoutedItem],
) -> bool:
    """Post the weekly digest to Slack.

    Returns True on success, False on failure.
    """
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set, skipping digest")
        return False

    blocks = _build_digest_blocks(result, routed_items)

    try:
        resp = httpx.post(
            webhook_url,
            json={"blocks": blocks},
            timeout=30.0,
        )
        resp.raise_for_status()
        logger.info("Posted digest to Slack")
        return True
    except httpx.HTTPStatusError as e:
        logger.error("Failed to post Slack digest: %s", e)
        return False
