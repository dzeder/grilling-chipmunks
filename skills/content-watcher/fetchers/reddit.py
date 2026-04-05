"""
Reddit fetcher for the content-watcher pipeline.

Uses Reddit's public JSON API (append .json to any URL).
No API key required. Rate limit: ~60 requests/min per IP.
"""

import logging
import time
from datetime import datetime, timezone

import httpx

from fetchers import register
from fetchers.base import BaseFetcher
from schema import ContentSource, RawContent, SourceType

logger = logging.getLogger(__name__)

USER_AGENT = "ohanafy-ai-ops/1.0 (content-learning-pipeline)"
POSTS_PER_REQUEST = 25


@register(SourceType.reddit)
class RedditFetcher(BaseFetcher):
    """Fetches posts from Reddit subreddits via public JSON API."""

    source_type = SourceType.reddit
    min_interval_seconds = 2

    def fetch_new(
        self, source: ContentSource, since: datetime | None = None
    ) -> list[RawContent]:
        """Fetch new posts from a subreddit.

        Uses the /new.json endpoint to get recent posts sorted by time.
        """
        self._rate_limit()

        subreddit_url = source.url.rstrip("/")
        json_url = f"{subreddit_url}/new.json"

        try:
            response = httpx.get(
                json_url,
                params={"limit": POSTS_PER_REQUEST, "raw_json": 1},
                headers={"User-Agent": USER_AGENT},
                timeout=30,
                follow_redirects=True,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self._handle_rate_limit(e.response)
                return []
            logger.error("Reddit API error for %s: %s", source.name, e)
            return []
        except httpx.RequestError as e:
            logger.error("Reddit request failed for %s: %s", source.name, e)
            return []

        data = response.json()
        posts = data.get("data", {}).get("children", [])

        items = []
        for post in posts:
            post_data = post.get("data", {})

            created_utc = post_data.get("created_utc", 0)
            published = datetime.fromtimestamp(created_utc, tz=timezone.utc)

            # Skip posts older than last check
            if since and published <= since:
                continue

            # Build body from title + selftext (for text posts) or title only (for links)
            selftext = post_data.get("selftext", "")
            title = post_data.get("title", "Untitled")

            if selftext:
                body = f"{title}\n\n{selftext}"
            else:
                body = title

            permalink = post_data.get("permalink", "")
            url = f"https://www.reddit.com{permalink}" if permalink else source.url

            items.append(
                RawContent(
                    title=title,
                    body=body,
                    url=url,
                    published_at=published,
                    source_type=SourceType.reddit,
                    source_name=source.name,
                    guid=post_data.get("id", ""),
                    metadata={
                        "score": post_data.get("score", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "subreddit": post_data.get("subreddit", ""),
                        "is_self": post_data.get("is_self", True),
                        "link_url": post_data.get("url", "") if not post_data.get("is_self") else "",
                    },
                )
            )

        logger.info("Fetched %d new posts from %s", len(items), source.name)
        return items

    @staticmethod
    def _handle_rate_limit(response: httpx.Response):
        """Parse Reddit rate limit headers and log wait time."""
        remaining = response.headers.get("X-Ratelimit-Remaining", "?")
        reset = response.headers.get("X-Ratelimit-Reset", "60")
        logger.warning(
            "Reddit rate limited. Remaining: %s, Reset in: %ss",
            remaining,
            reset,
        )
        try:
            wait = min(int(float(reset)), 120)
            time.sleep(wait)
        except (ValueError, TypeError):
            time.sleep(60)
