"""
Run the full Tray.io connector discovery pipeline.

Pipeline: discover → diff against registry → score → generate knowledge → create issues → update registry

Usage: python -m skills.tray_ai.discovery.commands.run_discovery
"""

import logging
import uuid
from datetime import datetime

from ..schema import DiscoveryRun
from ..skill import (
    REGISTRY_FILE,
    assess_relevance,
    detect_opportunities,
    discover_connectors,
    generate_knowledge,
    load_registry,
    update_registry,
    write_knowledge_file,
)

logger = logging.getLogger(__name__)


def run_pipeline(html_content: str) -> DiscoveryRun:
    """Execute the full discovery pipeline.

    Args:
        html_content: HTML from the Tray connectors browse page.
            Caller must fetch https://tray.io/documentation/connectors/browse/all/
            via WebFetch and pass the content.

    Returns:
        DiscoveryRun with pipeline execution summary.
    """
    run = DiscoveryRun(run_id=str(uuid.uuid4())[:8])

    # Step 1: Discover connectors from HTML
    try:
        connectors = discover_connectors(html_content=html_content)
        run.connectors_discovered = len(connectors)
    except Exception as exc:
        run.errors.append(f"Discovery failed: {exc}")
        run.completed_at = datetime.utcnow()
        return run

    # Step 2: Diff against existing registry
    registry = load_registry()
    existing_names = {c["name"] for c in registry.get("connectors", [])}
    new_connectors = [c for c in connectors if c.name not in existing_names]
    logger.info(
        "%d total connectors, %d new (not in registry)",
        len(connectors), len(new_connectors),
    )

    # Load thresholds from registry config
    job_config = registry.get("discovery_job", {})
    min_score = job_config.get("min_relevance_score", 0.65)
    auto_knowledge = job_config.get("auto_knowledge_threshold", 0.85)

    # Step 3: Score new connectors
    assessments = []
    for connector in new_connectors:
        try:
            assessment = assess_relevance(connector)
            assessments.append((connector, assessment))
            run.connectors_scored += 1
        except Exception as exc:
            run.errors.append(f"Scoring failed for {connector.name}: {exc}")

    # Step 4: Generate knowledge for high-relevance connectors
    for connector, assessment in assessments:
        if assessment.overall_score >= auto_knowledge:
            try:
                knowledge = generate_knowledge(connector, assessment)
                write_knowledge_file(knowledge)
                run.knowledge_files_generated += 1
                run.high_relevance_count += 1
            except Exception as exc:
                run.errors.append(f"Knowledge gen failed for {connector.name}: {exc}")

    # Step 5: Create GitHub issues for medium+ relevance
    # Import here to avoid circular dependency issues
    for connector, assessment in assessments:
        if assessment.overall_score >= min_score:
            try:
                from ..github import create_issue as issue_module

                issue_data = {
                    "connector_name": connector.display_name,
                    "category": connector.category.value,
                    "documentation_url": connector.documentation_url or "N/A",
                    "operation_count": connector.operation_count,
                    "opportunity": assessment.rationale,
                    "relevance_to_ohanafy": assessment.rationale,
                    "what_it_affects": ", ".join(assessment.ohanafy_use_cases[:3]) or "TBD",
                    "recommended_action": _format_recommended_action(assessment),
                    "effort": _estimate_effort(assessment),
                    "score": assessment.overall_score,
                    "opportunity_type": assessment.opportunity_type.value,
                    "current_usage": assessment.current_usage.value,
                }
                issue_module.create_issue(issue_data)
                run.issues_created += 1
            except Exception as exc:
                run.errors.append(f"Issue creation failed for {connector.name}: {exc}")

    # Step 6: Update registry with all scored connectors
    for connector, assessment in assessments:
        try:
            update_registry(connector, assessment)
        except Exception as exc:
            run.errors.append(f"Registry update failed for {connector.name}: {exc}")

    run.completed_at = datetime.utcnow()
    return run


def _format_recommended_action(assessment) -> str:
    """Generate recommended action checkboxes based on assessment."""
    actions = []
    if assessment.opportunity_type.value == "new_integration":
        actions.append("[ ] Build new Tray workflow using this connector")
    if assessment.opportunity_type.value == "optimize_existing":
        actions.append("[ ] Replace manual process with automated integration")
    if assessment.overall_score >= 0.85:
        actions.append("[x] Add to knowledge-base/tray-platform/ for reference")
    else:
        actions.append("[ ] Evaluate for customer-facing integration")
    return "\n".join(actions) if actions else "[ ] No action — awareness only"


def _estimate_effort(assessment) -> str:
    """Estimate effort based on opportunity type."""
    if assessment.current_usage.value == "active":
        return "S (<2h)"
    if assessment.opportunity_type.value == "optimize_existing":
        return "M (1-2 days)"
    return "L (sprint+)"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Tray Discovery Pipeline")
    print("=" * 40)
    print(
        "This pipeline requires HTML content from the Tray connector browse page."
    )
    print(
        "In production, run via agents/tray-discovery/agent.py which fetches the page."
    )
    print(
        f"\nRegistry: {REGISTRY_FILE}"
    )
