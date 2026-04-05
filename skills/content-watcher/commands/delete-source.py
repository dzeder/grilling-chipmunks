"""
Delete a content source from monitoring.

Usage: python -m skills.content_watcher.commands.delete_source <url>
"""

import yaml
from pathlib import Path

SOURCES_FILE = Path("registry/content-sources.yaml")


def delete_source(url: str) -> bool:
    """Remove a source from content-sources.yaml.

    Args:
        url: URL of the source to remove

    Returns:
        True if removed, False if not found

    Raises:
        ValueError: If source not found
    """
    config = yaml.safe_load(SOURCES_FILE.read_text())
    sources = config.get("sources", [])

    original_count = len(sources)
    config["sources"] = [s for s in sources if s.get("url") != url]

    if len(config["sources"]) == original_count:
        raise ValueError(f"SourceNotFound: {url}")

    SOURCES_FILE.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m skills.content_watcher.commands.delete_source <url>")
        sys.exit(1)

    delete_source(sys.argv[1])
    print(f"Removed: {sys.argv[1]}")
