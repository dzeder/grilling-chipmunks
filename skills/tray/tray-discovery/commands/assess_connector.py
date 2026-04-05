"""
On-demand assessment of a single Tray.io connector by name.

Usage: python -m skills.tray_ai.discovery.commands.assess_connector <name>
"""

import json
import logging
import sys

from ..schema import TrayConnectorEntry
from ..skill import assess_relevance, update_registry

logger = logging.getLogger(__name__)


def assess_single(name: str, description: str = "") -> None:
    """Assess a single connector and update the registry.

    Args:
        name: Connector identifier (e.g. 'netsuite', 'shipstation')
        description: Optional description to improve scoring accuracy
    """
    connector = TrayConnectorEntry(
        name=name,
        display_name=name.replace("-", " ").title(),
        description=description,
    )

    print(f"Scoring: {connector.display_name}")
    assessment = assess_relevance(connector)

    print(f"\nOverall Score: {assessment.overall_score:.3f}")
    print(f"Opportunity: {assessment.opportunity_type.value}")
    print(f"Current Usage: {assessment.current_usage.value}")
    print(f"\nDimensions:")
    for dim in assessment.dimensions:
        bar = "█" * int(dim.score * 20) + "░" * (20 - int(dim.score * 20))
        print(f"  {dim.name:<25} {bar} {dim.score:.2f} (w={dim.weight:.2f})")
        if dim.reasoning:
            print(f"    → {dim.reasoning}")

    print(f"\nRationale: {assessment.rationale}")
    if assessment.ohanafy_use_cases:
        print(f"Use Cases: {', '.join(assessment.ohanafy_use_cases)}")

    # Update registry
    update_registry(connector, assessment)
    print(f"\nRegistry updated for {name}.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print("Usage: python -m skills.tray_ai.discovery.commands.assess_connector <name> [description]")
        sys.exit(1)

    assess_single(
        name=sys.argv[1],
        description=" ".join(sys.argv[2:]) if len(sys.argv) > 2 else "",
    )
