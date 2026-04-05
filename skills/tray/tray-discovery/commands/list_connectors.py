"""
List all cataloged Tray.io connectors from the registry.

Usage: python -m skills.tray_ai.discovery.commands.list_connectors
"""

import yaml
from pathlib import Path

REGISTRY_FILE = Path("registry/tray-connectors.yaml")


def list_connectors(category: str | None = None) -> list[dict]:
    """List all cataloged connectors with their scores and statuses.

    Args:
        category: Optional filter by category.

    Returns:
        List of connector entries from the registry.
    """
    config = yaml.safe_load(REGISTRY_FILE.read_text())
    connectors = config.get("connectors", [])

    if not connectors:
        print("No connectors cataloged yet.")
        print("Run discovery: python -m skills.tray_ai.discovery.commands.run_discovery")
        return []

    if category:
        connectors = [c for c in connectors if c.get("category") == category]

    # Sort by relevance score descending
    connectors.sort(key=lambda c: c.get("relevance_score", 0), reverse=True)

    # Print formatted table
    print(f"{'Name':<25} {'Category':<18} {'Score':>5} {'Usage':<18} {'Opportunity':<20}")
    print("-" * 90)
    for c in connectors:
        print(
            f"{c.get('display_name', c.get('name', '?')):<25} "
            f"{c.get('category', '?'):<18} "
            f"{c.get('relevance_score', 0):>5.2f} "
            f"{c.get('current_usage', '?'):<18} "
            f"{c.get('opportunity_type', '?'):<20}"
        )

    print(f"\nTotal: {len(connectors)} connectors")
    return connectors


if __name__ == "__main__":
    import sys

    cat = sys.argv[1] if len(sys.argv) > 1 else None
    list_connectors(category=cat)
