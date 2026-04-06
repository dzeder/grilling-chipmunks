#!/usr/bin/env python3
"""
Scaffold eval files for agents and skills.

Scans agents/ and skills/ directories, creates eval dataset stubs
and scorer stubs for any that are missing.

Usage: python scripts/ci/scaffold-evals.py
"""

from pathlib import Path


def find_agents() -> list[str]:
    """Find all agent directories (excluding _template)."""
    agents_dir = Path("agents")
    if not agents_dir.exists():
        return []
    return sorted(d.name for d in agents_dir.iterdir() if d.is_dir() and d.name != "_template")


def find_skills() -> list[tuple[str, str]]:
    """Find all skill directories (excluding _template).
    Returns list of (pillar, skill_name) tuples.
    """
    skills_dir = Path("skills")
    results = []
    for pillar in sorted(skills_dir.iterdir()):
        if not pillar.is_dir() or pillar.name.startswith("_"):
            continue
        for skill in sorted(pillar.iterdir()):
            if skill.is_dir() and skill.name != "tests" and skill.name != "workflows":
                results.append((pillar.name, skill.name))
    return results


DATASET_TEMPLATE = '''"""Eval dataset for {name} agent.

Add eval cases with recorded outputs to enable scoring.
See evals/datasets/data_harmonizer.py for the reference implementation.
"""

EVAL_CASES = [
    # Each case should have:
    # {{
    #     "name": "case_id",
    #     "description": "What this case tests",
    #     "tags": ["tag1", "tag2"],
    #     "input": {{
    #         "query": "the user request or trigger",
    #     }},
    #     "expected": {{
    #         "key_fields": ["field1", "field2"],  # fields that must be present
    #     }},
    #     "recorded_output": {{
    #         # Pre-recorded agent output to score against expectations.
    #         # Run the agent once, capture output, paste here.
    #     }},
    # }}
]
'''

SCORER_TEMPLATE = '''"""Scorer for {name} agent.

Implement hard_checks() with agent-specific validation logic.
See evals/scorers/data_harmonizer.py for the reference implementation.
"""

from __future__ import annotations

from evals.scorers.base import BaseScorer, CheckResult


class {class_name}Scorer(BaseScorer):
    """Scorer for {name} eval cases."""

    agent_name = "{name}"

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
'''


def scaffold_agent_eval(agent_name: str) -> tuple[bool, bool]:
    """Create eval dataset and scorer stubs for an agent.

    Returns (dataset_created, scorer_created).
    """
    dataset_created = False
    scorer_created = False

    # Dataset
    dataset_dir = Path("evals/datasets")
    dataset_dir.mkdir(parents=True, exist_ok=True)

    dataset_file = dataset_dir / f"{agent_name}.py"
    if not dataset_file.exists():
        dataset_file.write_text(DATASET_TEMPLATE.format(name=agent_name))
        dataset_created = True

    # Scorer
    scorer_dir = Path("evals/scorers")
    scorer_dir.mkdir(parents=True, exist_ok=True)

    scorer_file = scorer_dir / f"{agent_name}.py"
    if not scorer_file.exists():
        # Convert agent-name to ClassName (e.g., "fde-strategist" -> "FdeStrategist")
        class_name = "".join(
            part.capitalize() for part in agent_name.replace("-", "_").split("_")
        )
        scorer_file.write_text(SCORER_TEMPLATE.format(
            name=agent_name,
            class_name=class_name,
        ))
        scorer_created = True

    return dataset_created, scorer_created


def main():
    print("Scaffolding evals...\n")

    agents = find_agents()
    print(f"Found {len(agents)} agents:")
    ds_count = 0
    sc_count = 0
    for agent in agents:
        ds, sc = scaffold_agent_eval(agent)
        status = []
        if ds:
            status.append("dataset")
            ds_count += 1
        if sc:
            status.append("scorer")
            sc_count += 1
        if status:
            print(f"  + {agent}: created {', '.join(status)}")
        else:
            print(f"  . {agent}: already exists")

    skills = find_skills()
    print(f"\nFound {len(skills)} skills (datasets scaffold for agents only)")

    print(f"\nCreated {ds_count} datasets, {sc_count} scorers.")
    print("Done.")


if __name__ == "__main__":
    main()
