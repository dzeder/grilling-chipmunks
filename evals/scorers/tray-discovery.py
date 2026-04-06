"""Scorer for tray-discovery agent.

Implement hard_checks() with agent-specific validation logic.
See evals/scorers/data_harmonizer.py for the reference implementation.
"""

from __future__ import annotations

from evals.scorers.base import BaseScorer, CheckResult


class TrayDiscoveryScorer(BaseScorer):
    """Scorer for tray-discovery eval cases."""

    agent_name = "tray-discovery"

    def hard_checks(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []

        # TODO: Add agent-specific hard checks here.
        # Example:
        # checks.append(CheckResult(
        #     name="output_has_key_field",
        #     passed="key_field" in output,
        #     score=1.0 if "key_field" in output else 0.0,
        #     max_score=1.0,
        #     details="key_field present" if "key_field" in output else "key_field missing",
        # ))

        return checks
