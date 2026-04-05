"""
List all monitored content sources and their status.

Usage: python -m skills.content_watcher.commands.list_sources
"""

import yaml
from pathlib import Path

SOURCES_FILE = Path("registry/content-sources.yaml")


def list_sources() -> list[dict]:
    """List all monitored sources with last-checked status."""
    config = yaml.safe_load(SOURCES_FILE.read_text())
    sources = config.get("sources", [])

    if not sources:
        print("No sources configured. Add one with: python -m skills.content_watcher.commands.add_source")
        return []

    for s in sources:
        status = s.get("last_checked", "never")
        print(f"  [{s.get('category', '?')}] {s.get('name', s.get('url'))} — last checked: {status}")

    return sources


if __name__ == "__main__":
    list_sources()
