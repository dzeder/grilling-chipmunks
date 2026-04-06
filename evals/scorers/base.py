"""Base scorer framework for agent evaluations.

Provides the core abstractions and template method for scoring eval cases.
Each agent implements a subclass of BaseScorer with agent-specific hard checks.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CheckResult:
    """Result of a single deterministic hard check."""

    name: str
    passed: bool
    score: float  # 0.0 - 1.0
    max_score: float  # typically 1.0
    details: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "max_score": self.max_score,
            "details": self.details,
        }


@dataclass
class EvalCaseResult:
    """Result of evaluating a single test case."""

    case_name: str
    passed: bool
    hard_checks: list[CheckResult]
    rubric_score: float | None  # None if rubric not run
    rubric_details: str | None
    total_score: float
    max_score: float
    duration_ms: int

    def to_dict(self) -> dict:
        return {
            "case_name": self.case_name,
            "passed": self.passed,
            "hard_checks": [c.to_dict() for c in self.hard_checks],
            "rubric_score": self.rubric_score,
            "rubric_details": self.rubric_details,
            "total_score": self.total_score,
            "max_score": self.max_score,
            "duration_ms": self.duration_ms,
        }


@dataclass
class EvalSuiteResult:
    """Aggregate result for an agent's full eval suite."""

    agent_name: str
    timestamp: str  # ISO 8601
    total_cases: int
    passed_cases: int
    pass_rate: float  # 0.0 - 1.0
    meets_target: bool  # >= 0.85
    meets_hard_fail: bool  # >= 0.75
    case_results: list[EvalCaseResult]
    haiku_enabled: bool
    tags_filter: str | None = None

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "timestamp": self.timestamp,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "pass_rate": self.pass_rate,
            "meets_target": self.meets_target,
            "meets_hard_fail": self.meets_hard_fail,
            "haiku_enabled": self.haiku_enabled,
            "tags_filter": self.tags_filter,
            "case_results": [c.to_dict() for c in self.case_results],
        }


# Thresholds from CLAUDE.md
DEFAULT_TARGET = 0.85
DEFAULT_HARD_FAIL = 0.75

# Haiku rubric weight when enabled (hard checks get the remainder)
RUBRIC_WEIGHT = 0.30
HARD_CHECK_WEIGHT_WITH_RUBRIC = 0.70


class BaseScorer(ABC):
    """Abstract base for agent-specific eval scorers.

    Subclasses must implement `hard_checks()` with agent-specific logic.
    The `score_case()` template method orchestrates hard checks + optional
    Haiku rubric scoring.
    """

    agent_name: str = "unknown"

    @abstractmethod
    def hard_checks(self, case: dict, output: dict) -> list[CheckResult]:
        """Run deterministic hard checks against a recorded output.

        Args:
            case: The eval case dict (input, expected_mappings, etc.)
            output: The recorded agent output to evaluate

        Returns:
            List of CheckResult for each check performed.
        """

    def rubric_prompt(self, case: dict, output: dict) -> str | None:
        """Build the prompt for Haiku rubric scoring.

        Override to customize. Returns None to skip rubric scoring even
        when haiku is enabled. Default reads from the agent's eval README.
        """
        return None

    def score_case(
        self,
        case: dict,
        output: dict | None = None,
        haiku_enabled: bool = False,
    ) -> EvalCaseResult:
        """Score a single eval case (template method).

        Args:
            case: The eval case dict from the dataset.
            output: The agent output to score. If None, uses case["recorded_output"].
            haiku_enabled: Whether to run Haiku rubric scoring.

        Returns:
            EvalCaseResult with all check details.
        """
        start = time.monotonic()

        if output is None:
            output = case.get("recorded_output", {})

        checks = self.hard_checks(case, output)

        # Hard check aggregate: average of individual scores
        if checks:
            hard_score = sum(c.score for c in checks) / sum(c.max_score for c in checks)
        else:
            hard_score = 0.0

        all_passed = all(c.passed for c in checks)

        # Optional Haiku rubric
        rubric_score = None
        rubric_details = None
        if haiku_enabled:
            prompt = self.rubric_prompt(case, output)
            if prompt:
                try:
                    from evals.scorers.haiku_rubric import score_with_haiku

                    rubric_score, rubric_details = score_with_haiku(prompt)
                except Exception as e:
                    rubric_details = f"Haiku unavailable: {e}"

        # Compute total score
        if rubric_score is not None:
            total_score = (
                hard_score * HARD_CHECK_WEIGHT_WITH_RUBRIC
                + rubric_score * RUBRIC_WEIGHT
            )
            max_score = 1.0
        else:
            total_score = hard_score
            max_score = 1.0

        duration_ms = int((time.monotonic() - start) * 1000)

        return EvalCaseResult(
            case_name=case.get("name", "unnamed"),
            passed=all_passed,
            hard_checks=checks,
            rubric_score=rubric_score,
            rubric_details=rubric_details,
            total_score=total_score,
            max_score=max_score,
            duration_ms=duration_ms,
        )

    def score_suite(
        self,
        cases: list[dict],
        haiku_enabled: bool = False,
        target: float = DEFAULT_TARGET,
        hard_fail: float = DEFAULT_HARD_FAIL,
        tag_filter: str | None = None,
    ) -> EvalSuiteResult:
        """Score all cases in a dataset.

        Args:
            cases: List of eval case dicts.
            haiku_enabled: Whether to run Haiku rubric.
            target: Pass rate target (default 0.85).
            hard_fail: Hard fail threshold (default 0.75).
            tag_filter: If set, only run cases with this tag.

        Returns:
            EvalSuiteResult with aggregate metrics.
        """
        if tag_filter:
            cases = [c for c in cases if tag_filter in c.get("tags", [])]

        results = []
        for case in cases:
            output = case.get("recorded_output", {})
            result = self.score_case(case, output, haiku_enabled)
            results.append(result)

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        pass_rate = passed / total if total > 0 else 0.0

        return EvalSuiteResult(
            agent_name=self.agent_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_cases=total,
            passed_cases=passed,
            pass_rate=pass_rate,
            meets_target=pass_rate >= target,
            meets_hard_fail=pass_rate >= hard_fail,
            case_results=results,
            haiku_enabled=haiku_enabled,
            tags_filter=tag_filter,
        )
