"""
GitHub API fetchers for the repo-watchers pipeline.

Fetches releases and new files from watched repos using the GitHub REST API.
Supports incremental fetching via RepoState timestamps.
"""

import logging
import os
import time
from datetime import datetime, timezone

import httpx

from .schema import ItemType, RepoState, WatchItem, WatchedRepo

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
MAX_COMMITS_PER_REPO = 30
MAX_RELEASES_PER_REPO = 10


def _github_headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}" if token else "",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _github_get(client: httpx.Client, url: str, params: dict | None = None) -> httpx.Response:
    """Make a GET request to the GitHub API with rate-limit awareness."""
    resp = client.get(url, params=params)

    remaining = int(resp.headers.get("X-RateLimit-Remaining", "100"))
    if remaining < 50:
        reset_at = int(resp.headers.get("X-RateLimit-Reset", "0"))
        wait = max(0, reset_at - int(time.time())) + 1
        logger.warning("GitHub rate limit low (%d remaining), sleeping %ds", remaining, wait)
        time.sleep(min(wait, 60))

    resp.raise_for_status()
    return resp


def fetch_releases(
    client: httpx.Client,
    repo: WatchedRepo,
    state: RepoState | None,
) -> list[WatchItem]:
    """Fetch new releases from a GitHub repo since last check."""
    owner_repo = repo.url
    url = f"{GITHUB_API}/repos/{owner_repo}/releases"

    try:
        resp = _github_get(client, url, params={"per_page": MAX_RELEASES_PER_REPO})
    except httpx.HTTPStatusError as e:
        logger.error("Failed to fetch releases for %s: %s", owner_repo, e)
        return []

    releases = resp.json()
    if not isinstance(releases, list):
        return []

    items = []
    for rel in releases:
        published = rel.get("published_at")
        if not published:
            continue

        pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))

        # On first run (no state), only take the latest release
        if state is None:
            items.append(WatchItem(
                repo=owner_repo,
                item_type=ItemType.release,
                title=f"{rel.get('name') or rel.get('tag_name', 'unknown')}",
                body=(rel.get("body") or "")[:8000],
                url=rel.get("html_url", ""),
                published_at=pub_dt,
                metadata={"tag": rel.get("tag_name", ""), "prerelease": rel.get("prerelease", False)},
            ))
            break  # Only the latest on first run

        # Incremental: only releases after last check
        if pub_dt > state.last_checked_at:
            items.append(WatchItem(
                repo=owner_repo,
                item_type=ItemType.release,
                title=f"{rel.get('name') or rel.get('tag_name', 'unknown')}",
                body=(rel.get("body") or "")[:8000],
                url=rel.get("html_url", ""),
                published_at=pub_dt,
                metadata={"tag": rel.get("tag_name", ""), "prerelease": rel.get("prerelease", False)},
            ))

    logger.info("Fetched %d new release(s) from %s", len(items), owner_repo)
    return items


def fetch_new_files(
    client: httpx.Client,
    repo: WatchedRepo,
    state: RepoState | None,
) -> list[WatchItem]:
    """Fetch newly added files from a GitHub repo since last check."""
    owner_repo = repo.url
    url = f"{GITHUB_API}/repos/{owner_repo}/commits"

    params: dict[str, str | int] = {"per_page": MAX_COMMITS_PER_REPO}
    if state:
        params["since"] = state.last_checked_at.isoformat()

    try:
        resp = _github_get(client, url, params=params)
    except httpx.HTTPStatusError as e:
        logger.error("Failed to fetch commits for %s: %s", owner_repo, e)
        return []

    commits = resp.json()
    if not isinstance(commits, list):
        return []

    # On first run, only check the latest commit
    if state is None:
        commits = commits[:1]

    # Collect added files across commits
    seen_files: set[str] = set()
    items: list[WatchItem] = []

    for commit_summary in commits:
        sha = commit_summary.get("sha", "")
        detail_url = f"{GITHUB_API}/repos/{owner_repo}/commits/{sha}"

        try:
            detail_resp = _github_get(client, detail_url)
        except httpx.HTTPStatusError:
            continue

        detail = detail_resp.json()
        commit_msg = detail.get("commit", {}).get("message", "")
        commit_date_str = detail.get("commit", {}).get("committer", {}).get("date", "")

        for file_info in detail.get("files", []):
            if file_info.get("status") != "added":
                continue

            filepath = file_info.get("filename", "")
            if filepath in seen_files:
                continue
            seen_files.add(filepath)

            commit_dt = None
            if commit_date_str:
                commit_dt = datetime.fromisoformat(commit_date_str.replace("Z", "+00:00"))

            items.append(WatchItem(
                repo=owner_repo,
                item_type=ItemType.new_file,
                title=f"New file: {filepath}",
                body=commit_msg[:4000],
                url=f"https://github.com/{owner_repo}/blob/{sha}/{filepath}",
                published_at=commit_dt,
                metadata={"sha": sha, "filepath": filepath},
            ))

    logger.info("Fetched %d new file(s) from %s", len(items), owner_repo)
    return items


def create_client() -> httpx.Client:
    """Create a configured httpx client for GitHub API calls."""
    return httpx.Client(
        headers=_github_headers(),
        timeout=30.0,
        follow_redirects=True,
    )
