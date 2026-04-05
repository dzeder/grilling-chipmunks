"""
Tools for the content learning agent.

These tools can be invoked by the agent via Claude's tool use
when running interactively. The pipeline also calls them directly
when running as a cron job.
"""

import sys
from pathlib import Path

# Add content-watcher skill to sys.path
_SKILL_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "content-watcher"
sys.path.insert(0, str(_SKILL_DIR))

from monitor.fetch_transcripts import fetch_all_new, load_sources  # noqa: E402


def list_sources() -> dict:
    """List all monitored content sources and their status."""
    sources = load_sources()
    return {
        "count": len(sources),
        "sources": [
            {
                "name": s.name,
                "url": s.url,
                "type": s.source_type.value,
                "category": s.category,
                "last_checked": s.last_checked.isoformat() if s.last_checked else "never",
            }
            for s in sources
        ],
    }


def fetch_new_content() -> dict:
    """Fetch new content from all monitored sources."""
    items, result = fetch_all_new()
    return {
        "items_fetched": result.items_fetched,
        "sources_checked": result.sources_checked,
        "errors": result.errors,
        "items": [
            {"title": i.title, "source": i.source_name, "url": i.url}
            for i in items[:10]  # limit preview
        ],
    }


# Tool schemas for Claude tool use
TOOL_SCHEMAS = [
    {
        "name": "list_sources",
        "description": "List all monitored content sources and their last-checked status.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "fetch_new_content",
        "description": "Fetch new content from all monitored sources. Returns items found and any errors.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

TOOL_HANDLERS = {
    "list_sources": list_sources,
    "fetch_new_content": fetch_new_content,
}
