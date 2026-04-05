"""
Tools for {agent-name} agent.

Each tool is a function that the agent can call via Claude's tool use.
Define tool schemas and implementations here.
"""


def example_tool(query: str) -> dict:
    """Example tool — replace with real implementation.

    Args:
        query: The input query to process.

    Returns:
        Dict with tool results.
    """
    return {"result": f"Processed: {query}"}


# Tool schemas for Claude tool use
TOOL_SCHEMAS = [
    {
        "name": "example_tool",
        "description": "Example tool — replace with real implementation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The input query to process.",
                }
            },
            "required": ["query"],
        },
    }
]

# Map tool names to implementations
TOOL_HANDLERS = {
    "example_tool": example_tool,
}
