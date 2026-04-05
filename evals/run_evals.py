#!/usr/bin/env python3
"""
Run all eval suites for Ohanafy AI Ops agents and prompts.

Usage: python evals/run_evals.py
Or via pytest: pytest evals/ -v -m eval
"""

import sys
from pathlib import Path


def find_eval_datasets() -> list[Path]:
    """Find all eval dataset files."""
    return list(Path("evals/datasets").glob("*.py"))


def main():
    datasets = find_eval_datasets()
    if not datasets:
        print("No eval datasets found. Run: python ci-cd/scripts/scaffold-evals.py")
        sys.exit(0)

    print(f"Found {len(datasets)} eval datasets")
    for ds in datasets:
        print(f"  - {ds.stem}")

    # TODO: Implement eval runner
    # - Load each dataset
    # - Run eval cases through the agent/prompt
    # - Score with Claude Haiku rubric
    # - Report pass/fail rates
    # - Write results to evals/results/ (append-only, never delete)

    print("\nEval runner not yet implemented. Use pytest: pytest evals/ -v -m eval")


if __name__ == "__main__":
    main()
