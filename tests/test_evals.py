"""Pytest integration for agent evals.

Run with: pytest tests/test_evals.py -v -m eval
"""

from __future__ import annotations

from pathlib import Path

import pytest

from evals.run_evals import find_eval_datasets, get_scorer, load_dataset


def _collect_eval_cases() -> list[tuple[str, dict]]:
    """Discover all eval cases across all datasets that have recorded outputs."""
    cases = []
    for ds_path in find_eval_datasets():
        agent_name, ds_cases = load_dataset(ds_path)
        for case in ds_cases:
            if case.get("recorded_output"):
                cases.append((agent_name, case))
    return cases


# Collect at import time for parametrize
_ALL_CASES = _collect_eval_cases()


@pytest.mark.eval
class TestAgentEvals:
    """Eval suite — scores pre-recorded agent outputs against golden expectations."""

    @pytest.mark.parametrize(
        "agent_name,case",
        _ALL_CASES,
        ids=[f"{agent}::{case['name']}" for agent, case in _ALL_CASES],
    )
    def test_eval_case(self, agent_name: str, case: dict):
        """Each eval case must pass all hard checks (or fail, if expected_pass is False)."""
        scorer = get_scorer(agent_name)
        result = scorer.score_case(
            case=case,
            output=case["recorded_output"],
            haiku_enabled=False,
        )

        expected_pass = case.get("expected_pass", True)

        if not expected_pass:
            # Violation cases: verify the scorer correctly detects failures
            assert not result.passed, (
                f"Case '{case['name']}' was expected to FAIL but passed — "
                f"scorer did not catch the violation"
            )
            return

        # Standard cases: must pass all hard checks
        if not result.passed:
            failed_checks = [c for c in result.hard_checks if not c.passed]
            details = "; ".join(f"[{c.name}] {c.details}" for c in failed_checks)
            pytest.fail(
                f"Case '{case['name']}' failed hard checks: {details}"
            )

        # Also assert above hard fail threshold (75%)
        assert result.total_score >= 0.75, (
            f"Case '{case['name']}' score {result.total_score:.2f} "
            f"below hard fail threshold 0.75"
        )


@pytest.mark.eval
class TestEvalInfrastructure:
    """Meta-tests: verify the eval framework itself works correctly."""

    def test_datasets_discoverable(self):
        """At least one eval dataset exists."""
        datasets = find_eval_datasets()
        assert len(datasets) > 0, "No eval datasets found in evals/datasets/"

    def test_all_datasets_loadable(self):
        """All dataset files can be imported and have EVAL_CASES."""
        for ds_path in find_eval_datasets():
            agent_name, cases = load_dataset(ds_path)
            assert isinstance(cases, list), f"{agent_name}: EVAL_CASES is not a list"

    def test_all_cases_have_required_fields(self):
        """Every eval case has name, input, and recorded_output."""
        for ds_path in find_eval_datasets():
            agent_name, cases = load_dataset(ds_path)
            for case in cases:
                if not case.get("recorded_output"):
                    continue  # Skip stubs
                assert "name" in case, f"{agent_name}: case missing 'name'"
                assert "input" in case, f"{agent_name}/{case.get('name')}: missing 'input'"

    def test_scorer_registry(self):
        """Known agents have dedicated scorers, others get GenericScorer."""
        from evals.scorers.data_harmonizer import DataHarmonizerScorer
        from evals.scorers.generic import GenericScorer

        assert isinstance(get_scorer("data_harmonizer"), DataHarmonizerScorer)
        assert isinstance(get_scorer("unknown_agent"), GenericScorer)
