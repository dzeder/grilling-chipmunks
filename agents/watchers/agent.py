"""
Repo Watchers agent — pipeline orchestrator.

Monitors external GitHub repos for releases and new patterns relevant
to Ohanafy. Scores relevance with Claude haiku, checks skill lineage,
creates GitHub issues, and posts a weekly Slack digest.

Entry point: python -m agents.watchers.agent [--dry-run]
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import yaml

from .fetchers import create_client, fetch_new_files, fetch_releases
from .github_issues import create_issue
from .lineage import find_affected_skills
from .router import route_item
from .schema import (
    AutoAdopt,
    PipelineResult,
    Priority,
    RepoState,
    RouteAction,
    RoutedItem,
    WatchedRepo,
    WatchItem,
    WatchType,
)
from .scorer import score_item
from .slack import post_digest

logger = logging.getLogger(__name__)

REPOS_YAML = Path("watchers/repos.yaml")
STATE_FILE = Path("watchers/state/last_checked.json")


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_config() -> tuple[list[WatchedRepo], dict]:
    """Load and parse watchers/repos.yaml.

    Returns (repos, watcher_job_config).
    """
    raw = yaml.safe_load(REPOS_YAML.read_text())
    watcher_job = raw.pop("watcher_job", {})

    repos: list[WatchedRepo] = []
    for category, entries in raw.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            auto_adopt = entry.get("auto_adopt", False)
            if auto_adopt is False or auto_adopt == "false":
                auto_adopt_enum = AutoAdopt.false
            else:
                auto_adopt_enum = AutoAdopt(auto_adopt)

            repos.append(WatchedRepo(
                url=entry["url"],
                priority=Priority(entry["priority"]),
                watch=WatchType(entry["watch"]),
                why=entry.get("why", ""),
                auto_adopt=auto_adopt_enum,
                tags=entry.get("tags", []),
                category=category,
            ))

    logger.info("Loaded %d repos across %d categories", len(repos), len(raw))
    return repos, watcher_job


def load_state() -> dict[str, RepoState]:
    """Load per-repo state from disk. Returns empty dict on first run."""
    if not STATE_FILE.exists():
        logger.info("No state file found — this is a priming run")
        return {}

    try:
        data = json.loads(STATE_FILE.read_text())
        return {
            url: RepoState(**state_data)
            for url, state_data in data.items()
        }
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Failed to parse state file: %s", e)
        return {}


def save_state(state: dict[str, RepoState]) -> None:
    """Persist per-repo state to disk."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        url: {
            "last_checked_at": s.last_checked_at.isoformat(),
            "last_release_tag": s.last_release_tag,
            "last_commit_sha": s.last_commit_sha,
        }
        for url, s in state.items()
    }

    STATE_FILE.write_text(json.dumps(data, indent=2) + "\n")
    logger.info("Saved state for %d repos", len(state))


def run_pipeline(dry_run: bool = False) -> PipelineResult:
    """Execute the full watcher pipeline."""
    now = datetime.now(timezone.utc)
    repos, watcher_job = load_config()
    state = load_state()
    is_priming = len(state) == 0

    thresholds = watcher_job.get("adoption_thresholds", {})
    auto_issue_threshold = thresholds.get("auto_pr_above", 0.85)
    notify_threshold = thresholds.get("notify_above", 0.60)

    result = PipelineResult(
        timestamp=now,
        repos_checked=len(repos),
        is_priming_run=is_priming,
    )

    # Build lookup from repo URL to WatchedRepo
    repo_lookup: dict[str, WatchedRepo] = {r.url: r for r in repos}

    # --- Phase 1: Fetch ---
    logger.info("=== Phase 1: Fetching from %d repos ===", len(repos))
    all_items: list[WatchItem] = []
    gh_client = create_client()

    for repo in repos:
        repo_state = state.get(repo.url)
        try:
            if repo.watch in (WatchType.releases, WatchType.all):
                all_items.extend(fetch_releases(gh_client, repo, repo_state))
            if repo.watch in (WatchType.new_files, WatchType.all):
                all_items.extend(fetch_new_files(gh_client, repo, repo_state))
        except Exception as e:
            error_msg = f"Fetch error for {repo.url}: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

    gh_client.close()
    result.items_found = len(all_items)
    logger.info("Fetched %d total items", len(all_items))

    # On priming run, set baselines and exit without scoring/issues
    if is_priming:
        logger.info("=== Priming run — setting baselines, no issues will be created ===")
        for repo in repos:
            state[repo.url] = RepoState(last_checked_at=now)

        # Update state with latest tags/shas from fetched items
        for item in all_items:
            if item.repo in state:
                tag = item.metadata.get("tag")
                sha = item.metadata.get("sha")
                if tag:
                    state[item.repo].last_release_tag = tag
                if sha:
                    state[item.repo].last_commit_sha = sha

        save_state(state)

        if not dry_run:
            post_digest(result, [])

        logger.info("Priming run complete — baselines set for %d repos", len(repos))
        return result

    # --- Phase 2: Score ---
    logger.info("=== Phase 2: Scoring %d items ===", len(all_items))
    claude_client = anthropic.Anthropic()
    scored_items = []

    for item in all_items:
        repo = repo_lookup.get(item.repo)
        if not repo:
            continue
        try:
            scored = score_item(claude_client, item, repo)
            scored_items.append(scored)
        except Exception as e:
            error_msg = f"Score error for {item.title[:60]}: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

    result.items_scored = len(scored_items)

    # --- Phase 3: Lineage ---
    logger.info("=== Phase 3: Checking lineage ===")
    lineage_cache: dict[str, list] = {}
    changed_repos = {s.repo for s in scored_items}
    for repo_url in changed_repos:
        lineage_cache[repo_url] = find_affected_skills(repo_url)

    # --- Phase 4: Route ---
    logger.info("=== Phase 4: Routing ===")
    routed_items: list[RoutedItem] = []

    for scored in scored_items:
        repo = repo_lookup.get(scored.repo)
        if not repo:
            continue

        routed = route_item(scored, repo, auto_issue_threshold, notify_threshold)
        routed.affected_skills = lineage_cache.get(scored.repo, [])
        # Attach repo metadata for issue formatting
        routed.metadata["category"] = repo.category
        routed.metadata["priority"] = repo.priority.value
        routed.metadata["auto_adopt"] = repo.auto_adopt.value
        routed_items.append(routed)

    # --- Phase 5: Create Issues ---
    actionable = [r for r in routed_items if r.action != RouteAction.log_only]
    logger.info("=== Phase 5: Creating %d issues ===", len(actionable))

    if not dry_run:
        github_repo = watcher_job.get("github_repo", "dzeder/daniels-ohanafy")
        for item in actionable:
            try:
                item.issue_url = create_issue(item, github_repo)
                if item.issue_url:
                    result.issues_created += 1
            except Exception as e:
                error_msg = f"Issue creation error for {item.title[:60]}: {e}"
                logger.error(error_msg)
                result.errors.append(error_msg)
    else:
        for item in actionable:
            logger.info("[DRY RUN] Would create issue: %s (score=%.2f, action=%s)",
                        item.title[:60], item.score, item.action.value)

    # --- Phase 6: Slack Digest ---
    logger.info("=== Phase 6: Posting digest ===")
    if not dry_run:
        post_digest(result, routed_items)
    else:
        logger.info("[DRY RUN] Would post Slack digest")

    # --- Phase 7: Persist State ---
    logger.info("=== Phase 7: Persisting state ===")
    for repo in repos:
        state[repo.url] = RepoState(last_checked_at=now)

    for item in all_items:
        if item.repo in state:
            tag = item.metadata.get("tag")
            sha = item.metadata.get("sha")
            if tag:
                state[item.repo].last_release_tag = tag
            if sha:
                state[item.repo].last_commit_sha = sha

    save_state(state)

    # --- Summary ---
    logger.info(
        "Pipeline complete: %d repos, %d items, %d scored, %d issues, %d errors",
        result.repos_checked, result.items_found, result.items_scored,
        result.issues_created, len(result.errors),
    )

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Repo Watchers agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and score but skip issue creation and Slack posting",
    )
    args = parser.parse_args()

    _setup_logging()
    result = run_pipeline(dry_run=args.dry_run)

    if result.errors:
        logger.warning("Completed with %d error(s)", len(result.errors))
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
