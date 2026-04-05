"""
Add a content source (podcast or YouTube channel) to monitoring.

Usage: python -m skills.content_watcher.commands.add_source
"""

import yaml
from pathlib import Path

SOURCES_FILE = Path("registry/content-sources.yaml")

VALID_CATEGORIES = [
    "beverage_industry",
    "product_strategy",
    "salesforce",
    "ai_dev_tools",
]


def resolve_source(url: str) -> dict:
    """Resolve a URL to a monitorable source entry.

    Handles: YouTube channel/playlist URLs, RSS feeds,
    Apple Podcast URLs, Spotify URLs.
    """
    # TODO: Implement URL resolution
    # - YouTube → extract channel ID via Data API v3
    # - Apple → resolve to RSS via Podcast Index API
    # - Spotify → resolve to RSS via Podcast Index API
    # - RSS → validate and store directly
    raise NotImplementedError("Source resolution not yet implemented")


def add_source(url: str, category: str, name: str | None = None) -> dict:
    """Add a source to content-sources.yaml.

    Args:
        url: Source URL (YouTube, RSS, Apple, Spotify)
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
