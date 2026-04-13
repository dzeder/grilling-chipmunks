"""
Score-based routing for the repo-watchers pipeline.

Routes scored items to actions based on thresholds from repos.yaml
and the repo's auto_adopt policy.
"""

import logging

from .schema import AutoAdopt, RouteAction, RoutedItem, ScoredItem, WatchedRepo

logger = logging.getLogger(__name__)

DEFAULT_AUTO_ISSUE_THRESHOLD = 0.85
DEFAULT_NOTIFY_THRESHOLD = 0.60


def route_item(
    scored: ScoredItem,
    repo: WatchedRepo,
    auto_issue_threshold: float = DEFAULT_AUTO_ISSUE_THRESHOLD,
    notify_threshold: float = DEFAULT_NOTIFY_THRESHOLD,
) -> RoutedItem:
    """Route a scored item based on score and auto_adopt policy.

    - score >= auto_issue_threshold AND auto_adopt != false -> auto_issue
    - score >= notify_threshold -> notify (create issue)
    - otherwise -> log_only
    """
    if scored.score >= auto_issue_threshold and repo.auto_adopt != AutoAdopt.false:
        action = RouteAction.auto_issue
    elif scored.score >= notify_threshold:
        action = RouteAction.notify
    else:
        action = RouteAction.log_only

    logger.info(
        "Routed %s/%s: score=%.2f auto_adopt=%s -> %s",
        scored.repo, scored.title[:40], scored.score, repo.auto_adopt.value, action.value,
    )

    return RoutedItem(
        repo=scored.repo,
        item_type=scored.item_type,
        title=scored.title,
        body=scored.body,
        url=scored.url,
        published_at=scored.published_at,
        score=scored.score,
        reason=scored.reason,
        action=action,
        metadata=scored.metadata,
    )
