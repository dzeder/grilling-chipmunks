#!/usr/bin/env python3
"""
Run eval suites for Ohanafy AI Ops agents and prompts.

Usage:
    python evals/run_evals.py                          # all agents, hard checks only
    python evals/run_evals.py --agent data_harmonizer   # single agent
    python evals/run_evals.py --with-haiku              # include Haiku rubric scoring
    python evals/run_evals.py --tag basic               # filter by tag
    python evals/run_evals.py --fail-under 0.80         # custom hard fail threshold

Or via pytest:
    pytest tests/test_evals.py -v -m eval
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from evals.scorers.base import BaseScorer, EvalSuiteResult, DEFAULT_TARGET, DEFAULT_HARD_FAIL


# --- Scorer registry ---

SCORER_REGISTRY: dict[str, type[BaseScorer]] = {}


def _register_scorers():
    """Lazy-register known scorers."""
    if SCORER_REGISTRY:
        return

    from evals.scorers.data_harmonizer import DataHarmonizerScorer

    SCORER_REGISTRY["data_harmonizer"] = DataHarmonizerScorer


def get_scorer(agent_name: str) -> BaseScorer:
    """Get the scorer for an agent, falling back to GenericScorer."""
    _register_scorers()

    scorer_cls = SCORER_REGISTRY.get(agent_name)
    if scorer_cls:
        return scorer_cls()

    from evals.scorers.generic import GenericScorer

    return GenericScorer(agent_name=agent_name)


# --- Dataset loading ---

def find_eval_datasets() -> list[Path]:
    """Find all eval dataset files (excluding __init__)."""
    evals_dir = Path(__file__).parent / "datasets"
    return sorted(
        p for p in evals_dir.glob("*.py")
        if p.stem != "__init__" and not p.stem.startswith("_")
    )


def load_dataset(path: Path) -> tuple[str, list[dict]]:
    """Import a dataset module and return (agent_name, cases).

    Args:
        path: Path to the dataset .py file.

    Returns:
        (agent_name derived from filename, list of EVAL_CASES)
    """
    agent_name = path.stem
    spec = importlib.util.spec_from_file_location(f"evals.datasets.{agent_name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    cases = getattr(module, "EVAL_CASES", [])
    return agent_name, cases


# --- Results ---

def write_result(result: EvalSuiteResult):
    """Append result as a new JSON file in evals/results/ (never overwrite)."""
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    filename = f"{result.agent_name}_{ts}.json"
    filepath = results_dir / filename

    with open(filepath, "w") as f:
        json.dump(result.to_dict(), f, indent=2)

    return filepath


# --- Reporting ---

def print_report(results: list[EvalSuiteResult]):
    """Print a terminal-friendly summary table."""
    print("\n" + "=" * 70)
    print("EVAL RESULTS")
    print("=" * 70)

    for result in results:
        status = "PASS" if result.meets_target else ("WARN" if result.meets_hard_fail else "FAIL")
        icon = {"PASS": "+", "WARN": "~", "FAIL": "!"}[status]

        print(f"\n[{icon}] {result.agent_name}")
        print(f"    Pass rate: {result.pass_rate:.0%} ({result.passed_cases}/{result.total_cases})")
        print(f"    Target (85%): {'met' if result.meets_target else 'NOT MET'}")
        print(f"    Hard fail (75%): {'above' if result.meets_hard_fail else 'BELOW — FAILING'}")

        if result.haiku_enabled:
            print(f"    Haiku rubric: enabled")

        if result.tags_filter:
            print(f"    Tag filter: {result.tags_filter}")

        # Show failed cases
        failed = [c for c in result.case_results if not c.passed]
        if failed:
            print(f"    Failed cases:")
            for case in failed:
                print(f"      - {case.case_name} (score: {case.total_score:.2f})")
                for check in case.hard_checks:
                    if not check.passed:
                        print(f"        [{check.name}] {check.details}")

    print("\n" + "-" * 70)

    all_pass = all(r.meets_hard_fail for r in results)
    total_cases = sum(r.total_cases for r in results)
    total_passed = sum(r.passed_cases for r in results)
    overall_rate = total_passed / total_cases if total_cases > 0 else 0

    print(f"Overall: {total_passed}/{total_cases} cases passed ({overall_rate:.0%})")
    print(f"Status: {'ALL PASSING' if all_pass else 'FAILING — below hard fail threshold'}")
    print("=" * 70)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Run Ohanafy agent evals")
    parser.add_argument("--agent", help="Run evals for a specific agent only")
    parser.add_argument("--with-haiku", action="store_true", help="Enable Haiku rubric scoring")
    parser.add_argument("--tag", help="Filter cases by tag")
    parser.add_argument("--fail-under", type=float, default=DEFAULT_HARD_FAIL,
                        help=f"Hard fail threshold (default {DEFAULT_HARD_FAIL})")
    parser.add_argument("--target", type=float, default=DEFAULT_TARGET,
                        help=f"Target threshold (default {DEFAULT_TARGET})")
    parser.add_argument("--no-write", action="store_true", help="Skip writing results to disk")
    args = parser.parse_args()

    datasets = find_eval_datasets()
    if not datasets:
        print("No eval datasets found. Run: python scripts/ci/scaffold-evals.py")
        sys.exit(0)

    # Filter to specific agent if requested
    if args.agent:
        datasets = [d for d in datasets if d.stem == args.agent]
        if not datasets:
            print(f"No dataset found for agent: {args.agent}")
            sys.exit(1)

    results: list[EvalSuiteResult] = []

    for ds_path in datasets:
        agent_name, cases = load_dataset(ds_path)

        if not cases:
            print(f"Skipping {agent_name}: no EVAL_CASES defined")
            continue

        # Skip datasets with no recorded outputs (stubs)
        has_outputs = any(c.get("recorded_output") for c in cases)
        if not has_outputs:
            print(f"Skipping {agent_name}: no recorded_output in cases (stub dataset)")
            continue

        scorer = get_scorer(agent_name)
        result = scorer.score_suite(
            cases=cases,
            haiku_enabled=args.with_haiku,
            target=args.target,
            hard_fail=args.fail_under,
            tag_filter=args.tag,
        )
        results.append(result)

        if not args.no_write:
            filepath = write_result(result)
            print(f"Results written to {filepath}")

    if not results:
        print("No eval suites with recorded outputs found.")
        sys.exit(0)

    print_report(results)

    # Exit code: 1 if any agent below hard fail
    if any(not r.meets_hard_fail for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
