"""
Agent: tray-discovery

Orchestrates the Tray.io connector discovery pipeline.
Discovers connectors, scores relevance, generates knowledge,
and creates GitHub issues for the team.
"""

import json
import logging
from pathlib import Path

import anthropic

from skills.tray_ai.discovery.commands.run_discovery import run_pipeline

# Load system prompt
SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system.md").read_text()

logger = logging.getLogger(__name__)


class TrayDiscoveryAgent:
    """Orchestrates the Tray.io connector discovery pipeline."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.tools = [
            {
                "name": "run_discovery_pipeline",
                "description": (
                    "Run the full Tray.io connector discovery pipeline. "
                    "Fetches the connector listing, scores each for Ohanafy relevance, "
                    "generates knowledge for high-relevance connectors, and creates "
                    "GitHub issues for medium+ relevance connectors."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "html_content": {
                            "type": "string",
                            "description": "HTML content from the Tray connectors browse page.",
                        }
                    },
                    "required": ["html_content"],
                },
            },
            {
                "name": "list_cataloged_connectors",
                "description": "List all connectors currently in the registry with scores.",
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
                            "description": "Connector name (e.g. 'netsuite', 'shipstation').",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description for better scoring.",
                        },
                    },
                    "required": ["name"],
                },
            },
        ]

    def _handle_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool call and return the result as a string."""
        if tool_name == "run_discovery_pipeline":
            result = run_pipeline(html_content=tool_input["html_content"])
            return json.dumps(result.model_dump(), default=str)

        elif tool_name == "list_cataloged_connectors":
            from skills.tray_ai.discovery.commands.list_connectors import list_connectors
            connectors = list_connectors(category=tool_input.get("category"))
            return json.dumps(connectors, default=str)

        elif tool_name == "assess_single_connector":
            from skills.tray_ai.discovery.skill import assess_relevance, update_registry
            from skills.tray_ai.discovery.schema import TrayConnectorEntry

            connector = TrayConnectorEntry(
                name=tool_input["name"],
                display_name=tool_input["name"].replace("-", " ").title(),
                description=tool_input.get("description", ""),
            )
            assessment = assess_relevance(connector)
            update_registry(connector, assessment)
            return json.dumps(assessment.model_dump(), default=str)

        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def run(self, user_input: str, context: dict | None = None) -> str:
        """Process user input through the discovery pipeline.

        Supports natural language requests like:
        - "Discover all Tray connectors"
        - "Score netsuite for Ohanafy"
        - "What connectors do we have cataloged?"
        """
        messages = [{"role": "user", "content": user_input}]

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=messages,
                tools=self.tools,
            )

            # If no tool use, return the text response
            if response.stop_reason == "end_turn":
                text_blocks = [b.text for b in response.content if hasattr(b, "text")]
                return "\n".join(text_blocks)

            # Process tool calls
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info("Tool call: %s", block.name)
                    result = self._handle_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = TrayDiscoveryAgent()
    print(agent.run("List all cataloged Tray.io connectors."))
