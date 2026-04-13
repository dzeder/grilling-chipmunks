"""
Claude haiku relevance scoring for the repo-watchers pipeline.

Scores each WatchItem for relevance to Ohanafy, injecting repo-specific
context (why, tags, category) into the scoring prompt.
"""

import json
import logging
from pathlib import Path

import anthropic

from .schema import ScoredItem, WatchItem, WatchedRepo

logger = logging.getLogger(__name__)

SCORING_CRITERIA_FILE = Path("agents/watchers/prompts/scoring.md")
SCORING_MODEL = "claude-haiku-4-5-20251001"


def _load_scoring_criteria() -> str:
    if SCORING_CRITERIA_FILE.exists():
        return SCORING_CRITERIA_FILE.read_text()
    return ""


def score_item(
    client: anthropic.Anthropic,
    item: WatchItem,
    repo: WatchedRepo,
) -> ScoredItem:
    """Score a single item for relevance to Ohanafy.

    Returns a ScoredItem with score clamped to [0.0, 1.0].
    Falls back to score=0.0 on any error.
    """
    scoring_criteria = _load_scoring_criteria()

    system_prompt = f"""{scoring_criteria}

## Repo Context
- **Repo:** {repo.url}
- **Category:** {repo.category}
- **Priority:** {repo.priority.value}
- **Why we watch:** {repo.why}
- **Tags:** {', '.join(repo.tags)}
- **Auto-adopt policy:** {repo.auto_adopt.value}"""

    user_content = f"**{item.item_type.value}: {item.title}**\n\n{item.body[:8000]}"

    try:
        response = client.messages.create(
            model=SCORING_MODEL,
            max_tokens=150,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        result_text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        parsed = json.loads(result_text)
        score = max(0.0, min(1.0, float(parsed["score"])))
        reason = parsed.get("reason", "")

        logger.info("Scored %s/%s: %.2f — %s", item.repo, item.title[:40], score, reason)

        return ScoredItem(
            repo=item.repo,
            item_type=item.item_type,
            title=item.title,
            body=item.body,
            url=item.url,
            published_at=item.published_at,
            score=score,
            reason=reason,
            model_used=SCORING_MODEL,
            metadata=item.metadata,
        )

    except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
        logger.error("Failed to parse scoring response for %s: %s", item.title[:60], e)
    except anthropic.APIError as e:
        logger.error("Anthropic API error scoring %s: %s", item.title[:60], e)

    # Fallback: return item with score 0.0
    return ScoredItem(
        repo=item.repo,
        item_type=item.item_type,
        title=item.title,
        body=item.body,
        url=item.url,
        published_at=item.published_at,
        score=0.0,
        reason="Scoring failed",
        model_used=SCORING_MODEL,
        metadata=item.metadata,
    )
