#!/usr/bin/env python3
"""
Scaffold eval files for agents and skills.

Scans agents/ and skills/ directories, creates eval dataset stubs
and scorer stubs for any that are missing.

Usage: python ci-cd/scripts/scaffold-evals.py
"""

from pathlib import Path


def find_agents() -> list[str]:
    """Find all agent directories (excluding _template)."""
    agents_dir = Path("agents")
    return [d.name for d in agents_dir.iterdir() if d.is_dir() and d.name != "_template"]


def find_skills() -> list[tuple[str, str]]:
    """Find all skill directories (excluding _template).
    Returns list of (pillar, skill_name) tuples.
    """
    skills_dir = Path("skills")
    results = []
    for pillar in skills_dir.iterdir():
        if not pillar.is_dir() or pillar.name == "_template":
            continue
        for skill in pillar.iterdir():
            if skill.is_dir() and skill.name != "tests" and skill.name != "workflows":
                results.append((pillar.name, skill.name))
    return results


def scaffold_agent_eval(agent_name: str):
    """Create eval dataset and scorer for an agent."""
    dataset_dir = Path(f"evals/datasets")
    dataset_dir.mkdir(parents=True, exist_ok=True)

    dataset_file = dataset_dir / f"{agent_name}.py"
    if not dataset_file.exists():
        dataset_file.write_text(f'''"""Eval dataset for {agent_name} agent."""

EVAL_CASES = [
    # Add eval cases here. Each case should have:
    # - input: the user query or trigger
    # - expected: expected output or behavior
    # - tags: list of tags for filtering
]
''')
        print(f"  Created {dataset_file}")


def main():
    print("Scaffolding evals...\n")

    agents = find_agents()
    print(f"Found {len(agents)} agents:")
    for agent in agents:
        scaffold_agent_eval(agent)

    skills = find_skills()
    print(f"\nFound {len(skills)} skills")

    print("\nDone.")


if __name__ == "__main__":
    main()
