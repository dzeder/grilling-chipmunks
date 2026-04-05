"""
Agent: content

Monitors content sources (RSS feeds, Reddit, podcasts, YouTube) for insights
relevant to Ohanafy's beverage supply chain operations. Fetches new content,
scores relevance with Claude haiku, extracts insights with Claude sonnet,
and creates GitHub issues for actionable findings.

Entry point for CI: python -m agents.content.agent
"""

import logging
import sys
from pathlib import Path

# Add the content-watcher skill directory to sys.path for imports
_SKILL_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "content-watcher"
sys.path.insert(0, str(_SKILL_DIR))

from monitor.fetch_transcripts import fetch_all_new  # noqa: E402
from monitor.process_insights import process_new_content  # noqa: E402
from github.create_issue import create_issue  # noqa: E402
from schema import InsightAction, RoutedInsight  # noqa: E402

logger = logging.getLogger(__name__)

# Thresholds from relevance-scoring.md
THRESHOLD_AUTO_ISSUE = 0.85
THRESHOLD_TEAM_TRIAGE = 0.65


def route_insight(insight):
    """Determine action based on relevance score."""
    if insight.score >= THRESHOLD_AUTO_ISSUE:
        return InsightAction.auto_issue
    elif insight.score >= THRESHOLD_TEAM_TRIAGE:
        return InsightAction.team_triage
    return InsightAction.log_only


def run_pipeline() -> dict:
    """Run the full content learning pipeline.

    1. Fetch new content from all monitored sources
    2. Normalize and score relevance
    3. Extract insights from high-relevance content
    4. Route insights and create GitHub issues

    Returns:
        Summary dict with counts and any errors.
    """
    # Step 1: Fetch
    logger.info("Starting content pipeline run...")
    items, fetch_result = fetch_all_new()
    logger.info(
        "Fetch complete: %d items from %d sources",
        fetch_result.items_fetched,
        fetch_result.sources_checked,
    )

    if not items:
        logger.info("No new content found. Pipeline complete.")
        return {
            "sources_checked": fetch_result.sources_checked,
            "items_fetched": 0,
            "insights_extracted": 0,
            "issues_created": 0,
            "errors": fetch_result.errors,
        }

    # Step 2-3: Score and extract
    insights = process_new_content(items)
    logger.info("Extracted %d insights from %d items", len(insights), len(items))

    # Step 4: Route and create issues
    issues_created = 0
    routed: list[RoutedInsight] = []

    for insight in insights:
        action = route_insight(insight)

        if action in (InsightAction.auto_issue, InsightAction.team_triage):
            try:
                issue_data = create_issue(insight.model_dump())
                issue_url = issue_data.get("html_url", "")
                routed.append(RoutedInsight(insight=insight, action=action, issue_url=issue_url))
                issues_created += 1
                logger.info("Created issue: %s", issue_url)
            except Exception as e:
                logger.error("Failed to create issue: %s", e)
                routed.append(RoutedInsight(insight=insight, action=action))
        else:
            routed.append(RoutedInsight(insight=insight, action=action))
            logger.debug("Logged (below threshold): %s", insight.insight[:80])

    summary = {
        "sources_checked": fetch_result.sources_checked,
        "items_fetched": fetch_result.items_fetched,
        "insights_extracted": len(insights),
        "issues_created": issues_created,
        "errors": fetch_result.errors,
    }

    logger.info(
        "Pipeline complete: %d sources, %d items, %d insights, %d issues",
        summary["sources_checked"],
        summary["items_fetched"],
        summary["insights_extracted"],
        summary["issues_created"],
    )

    return summary


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    result = run_pipeline()
    print(f"\nPipeline Summary:")
    print(f"  Sources checked:   {result['sources_checked']}")
    print(f"  Items fetched:     {result['items_fetched']}")
    print(f"  Insights extracted:{result['insights_extracted']}")
    print(f"  Issues created:    {result['issues_created']}")
    if result["errors"]:
        print(f"  Errors:            {len(result['errors'])}")
        for e in result["errors"]:
            print(f"    - {e}")
