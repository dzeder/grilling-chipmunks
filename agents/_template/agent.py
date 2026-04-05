"""
Agent: {agent-name}

Template agent implementation. Copy this directory and customize.
See README.md for agent documentation.
"""

import anthropic
from pathlib import Path

# Load system prompt
SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system.md").read_text()


class Agent:
    """Base agent class. Customize for your use case."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.tools = []

    def run(self, user_input: str, context: dict | None = None) -> str:
        """Process user input and return a response."""
        messages = [{"role": "user", "content": user_input}]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=self.tools,
        )

        return response.content[0].text


if __name__ == "__main__":
    agent = Agent()
    print(agent.run("Hello, this is a test."))
