"""
Add a content source (podcast, YouTube, web, or Reddit) to monitoring.

Usage: python -m skills.content_watcher.commands.add_source <url> <category> [name]
"""

import re
from urllib.parse import urlparse

import feedparser
import yaml
from pathlib import Path

SOURCES_FILE = Path("registry/content-sources.yaml")

VALID_CATEGORIES = [
    "beverage_industry",
    "product_strategy",
    "salesforce",
    "ai_dev_tools",
    "tray_platform",
    "integration",
]


def resolve_source(url: str) -> dict:
    """Resolve a URL to a monitorable source entry.

    Handles: YouTube channel/playlist URLs, RSS feeds,
    Apple Podcast URLs, Spotify URLs, Reddit RSS, web/blog RSS.

    Returns dict with: url, type, and any resolved metadata.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    # YouTube channel or playlist
    if "youtube.com" in hostname or "youtu.be" in hostname:
        return {"url": url, "type": "youtube"}

    # Reddit RSS feed
    if "reddit.com" in hostname:
        # Ensure it ends with .rss
        if not url.endswith(".rss"):
            url = url.rstrip("/") + "/.rss"
        return {"url": url, "type": "reddit"}

    # Apple Podcasts — resolve to RSS via Podcast Index API
    if "podcasts.apple.com" in hostname:
        # Extract podcast ID from URL like /podcast/name/id123456
        match = re.search(r"/id(\d+)", parsed.path)
        if match:
            return {
                "url": url,
                "type": "podcast",
                "apple_id": match.group(1),
                "note": "Resolved via Podcast Index API at runtime",
            }
        return {"url": url, "type": "podcast"}

    # Spotify
    if "open.spotify.com" in hostname:
        return {
            "url": url,
            "type": "podcast",
            "note": "Resolved via Podcast Index API at runtime (~80% success)",
        }

    # Try to detect RSS feed
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            # Check if it has audio enclosures (podcast)
            has_audio = any(
                enc.get("type", "").startswith("audio/")
                for entry in feed.entries[:3]
                for enc in entry.get("enclosures", [])
            )
            if has_audio:
                return {"url": url, "type": "podcast"}
            else:
                return {"url": url, "type": "web"}
    except Exception:
        pass

    # Default to web type for unrecognized URLs
    return {"url": url, "type": "web"}


def add_source(url: str, category: str, name: str | None = None) -> dict:
    """Add a source to content-sources.yaml.

    Args:
        url: Source URL (YouTube, RSS, Apple, Spotify, Reddit, web)
        category: One of VALID_CATEGORIES
        name: Optional display name

    Returns:
        The created source entry

    Raises:
        ValueError: If category is invalid or source already exists
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")

    config = yaml.safe_load(SOURCES_FILE.read_text())

    # Check for duplicates
    for existing in config.get("sources", []):
        if existing.get("url") == url:
            raise ValueError(f"SourceAlreadyExists: {url}")

    source = resolve_source(url)
    source["category"] = category
    if name:
        source["name"] = name

    config.setdefault("sources", []).append(source)
    SOURCES_FILE.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))

    return source


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m skills.content_watcher.commands.add_source <url> <category> [name]")
        sys.exit(1)

    result = add_source(
        url=sys.argv[1],
        category=sys.argv[2],
        name=sys.argv[3] if len(sys.argv) > 3 else None,
    )
    print(f"Added: {result}")
