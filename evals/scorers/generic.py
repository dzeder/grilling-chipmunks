"""Generic scorer — structural checks only.

Fallback for agents without a custom scorer. Checks that the recorded output
exists and has the expected structure, but performs no agent-specific validation.
"""

from __future__ import annotations

from evals.scorers.base import BaseScorer, CheckResult


class GenericScorer(BaseScorer):
    """Structural scorer for agents without custom hard checks."""

    def __init__(self, agent_name: str = "generic"):
        self.agent_name = agent_name

    def hard_checks(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []

        # Check 1: recorded_output exists and is non-empty
        has_output = bool(output)
        checks.append(CheckResult(
            name="output_exists",
            passed=has_output,
            score=1.0 if has_output else 0.0,
            max_score=1.0,
            details="Output present" if has_output else "No recorded_output in case",
        ))

        if not has_output:
            return checks

        # Check 2: output is a dict (not a string or list)
        is_dict = isinstance(output, dict)
        checks.append(CheckResult(
            name="output_is_dict",
            passed=is_dict,
            score=1.0 if is_dict else 0.0,
            max_score=1.0,
            details=f"Output type: {type(output).__name__}",
        ))

        # Check 3: case has required fields (name, input)
        has_name = bool(case.get("name"))
        has_input = bool(case.get("input"))
        has_required = has_name and has_input
        missing = []
        if not has_name:
            missing.append("name")
        if not has_input:
            missing.append("input")
        checks.append(CheckResult(
            name="case_structure",
            passed=has_required,
            score=1.0 if has_required else 0.0,
            max_score=1.0,
            details="All required fields present" if has_required else f"Missing: {', '.join(missing)}",
        ))

        return checks
