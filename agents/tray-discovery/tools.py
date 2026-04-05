"""
Tools for the tray-discovery agent.

Each tool is a function that the agent can call via Claude's tool use.
Wraps the discovery skill functions for agent consumption.
"""

import json

from skills.tray_ai.discovery.schema import TrayConnectorEntry
from skills.tray_ai.discovery.skill import (
    assess_relevance,
    discover_connectors,
    generate_knowledge,
    detect_opportunities,
    update_registry,
    write_knowledge_file,
)
from skills.tray_ai.discovery.commands.run_discovery import run_pipeline
from skills.tray_ai.discovery.commands.list_connectors import list_connectors


def run_discovery_tool(html_content: str) -> dict:
    """Run the full discovery pipeline with HTML from the Tray connectors page.

    Args:
        html_content: HTML from https://tray.io/documentation/connectors/browse/all/

    Returns:
        Dict with pipeline run summary.
    """
    result = run_pipeline(html_content=html_content)
    return result.model_dump()


def list_connectors_tool(category: str | None = None) -> dict:
    """List all cataloged connectors from the registry.

    Args:
        category: Optional filter by category.

    Returns:
        Dict with list of connector entries.
    """
    connectors = list_connectors(category=category)
    return {"connectors": connectors, "count": len(connectors)}


def assess_connector_tool(name: str, description: str = "") -> dict:
    """Score a single connector for Ohanafy relevance.

    Args:
        name: Connector identifier (e.g. 'netsuite').
        description: Optional description.

    Returns:
        Dict with assessment results.
    """
    connector = TrayConnectorEntry(
        name=name,
        display_name=name.replace("-", " ").title(),
        description=description,
    )
    assessment = assess_relevance(connector)
    update_registry(connector, assessment)
    return assessment.model_dump()


# Tool schemas for Claude tool use
TOOL_SCHEMAS = [
    {
        "name": "run_discovery_pipeline",
        "description": (
            "Run the full Tray.io connector discovery pipeline. "
            "Requires HTML content from the connector browse page."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "html_content": {
                    "type": "string",
                    "description": "HTML from the Tray connectors browse page.",
                }
            },
            "required": ["html_content"],
        },
    },
    {
        "name": "list_cataloged_connectors",
        "description": "List all connectors in the registry with scores and statuses.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category filter.",
                }
            },
        },
    },
    {
        "name": "assess_single_connector",
        "description": "Score a single connector by name for Ohanafy relevance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Connector name (e.g. 'netsuite').",
                },
                "description": {
                    "type": "string",
                    "description": "Optional description for scoring context.",
                },
            },
            "required": ["name"],
        },
    },
]

# Map tool names to implementations
TOOL_HANDLERS = {
    "run_discovery_pipeline": run_discovery_tool,
    "list_cataloged_connectors": list_connectors_tool,
    "assess_single_connector": assess_connector_tool,
}
