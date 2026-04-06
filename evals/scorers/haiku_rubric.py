"""Optional Haiku rubric scoring for qualitative eval assessment.

Gated on ANTHROPIC_API_KEY. Not run in CI — use --with-haiku flag locally.
Uses claude-haiku-4-5-20251001 per model routing policy (haiku for scoring).
"""

from __future__ import annotations

import json
import os


def score_with_haiku(prompt: str) -> tuple[float | None, str]:
    """Score agent output using Claude Haiku against a rubric.

    Args:
        prompt: The full rubric prompt including expected/actual output.

    Returns:
        (score, details) where score is 0.0-1.0, details is explanation.
        Returns (None, error_msg) on failure.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "Haiku unavailable: ANTHROPIC_API_KEY not set"

    try:
        import anthropic
    except ImportError:
        return None, "Haiku unavailable: anthropic package not installed"

    try:
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=(
                "You are an eval scorer. Score the agent output against the rubric. "
                "Respond with JSON: {\"score\": <1-5>, \"explanation\": \"<brief reason>\"} "
                "where 1=poor, 2=below expectations, 3=meets expectations, 4=good, 5=excellent."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()

        # Parse JSON response
        parsed = json.loads(text)
        raw_score = parsed.get("score", 3)
        explanation = parsed.get("explanation", "No explanation provided")

        # Normalize 1-5 to 0.0-1.0
        normalized = (raw_score - 1) / 4.0

        return normalized, explanation

    except json.JSONDecodeError:
        return None, f"Haiku returned non-JSON: {text[:200]}"
    except Exception as e:
        return None, f"Haiku error: {e}"
