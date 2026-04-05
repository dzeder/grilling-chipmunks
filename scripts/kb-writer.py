#!/usr/bin/env python3
"""
Knowledge Base Writer — automated KB population from approved content insights.

Queries GitHub for issues labeled 'content-insight' + 'kb-approved',
uses Claude to determine the target KB file, synthesizes new content,
and creates a PR with the update.

Usage:
  python scripts/kb-writer.py --issue 123          # Process a specific issue
  python scripts/kb-writer.py --scan               # Find all kb-approved issues
  python scripts/kb-writer.py --dry-run --issue 123 # Preview without creating PR
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import anthropic
import httpx
import yaml

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
SOURCES_FILE = REPO_ROOT / "registry" / "content-sources.yaml"
KB_DIR = REPO_ROOT / "knowledge-base"

# Map categories to their KB target directories
CATEGORY_TARGETS = {
    "beverage_industry": [
        "knowledge-base/industry-insights/pricing-models.md",
        "knowledge-base/industry-insights/distribution-trends.md",
        "knowledge-base/industry-insights/competitive-landscape.md",
        "knowledge-base/beverage-supply-chain/glossary.md",
    ],
    "product_strategy": [
        "knowledge-base/industry-insights/pricing-models.md",
        "knowledge-base/industry-insights/competitive-landscape.md",
        "knowledge-base/ohanafy/product-overview.md",
    ],
    "salesforce": [
        "knowledge-base/salesforce/object-model.md",
        "knowledge-base/salesforce/key-flows.md",
    ],
    "ai_dev_tools": [
        "knowledge-base/ohanafy/integration-points.md",
    ],
    "tray_platform": [
        "knowledge-base/tray/connector-catalog.md",
        "knowledge-base/tray/capability-matrix.md",
    ],
    "integration": [
        "knowledge-base/ohanafy/integration-points.md",
        "knowledge-base/tray/connector-catalog.md",
    ],
}


def get_github_issue(repo: str, issue_number: int) -> dict:
    """Fetch a GitHub issue by number."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = httpx.get(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}",
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def find_approved_issues(repo: str) -> list[dict]:
    """Find all issues with 'content-insight' and 'kb-approved' labels."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = httpx.get(
        f"https://api.github.com/repos/{repo}/issues",
        headers=headers,
        params={"labels": "content-insight,kb-approved", "state": "open"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def determine_target_file(issue_body: str, category: str) -> str:
    """Use Claude to determine which KB file should be updated."""
    client = anthropic.Anthropic()

    candidates = CATEGORY_TARGETS.get(category, [])
    if not candidates:
        # Fall back to all KB files
        candidates = [
            str(p.relative_to(REPO_ROOT))
            for p in KB_DIR.rglob("*.md")
            if p.name != "README.md"
        ]

    # Read candidate file previews
    file_previews = {}
    for path_str in candidates:
        full_path = REPO_ROOT / path_str
        if full_path.exists():
            content = full_path.read_text()
            # First 500 chars as preview
            file_previews[path_str] = content[:500]

    system_prompt = """You are a knowledge base organizer for Ohanafy, a beverage supply chain SaaS platform.

Given a content insight from a GitHub issue, determine which knowledge base file it should be added to.

Candidate files and their current content previews:
"""
    for path, preview in file_previews.items():
        system_prompt += f"\n### {path}\n{preview}\n"

    system_prompt += """

Respond with ONLY the file path (e.g., "knowledge-base/industry-insights/pricing-models.md").
If none of the candidates are appropriate, respond with "SKIP".
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        system=system_prompt,
        messages=[{"role": "user", "content": issue_body}],
    )
    result = response.content[0].text.strip().strip('"')
    return result


def synthesize_update(target_file: str, issue_body: str, issue_title: str) -> str:
    """Use Claude to synthesize the insight into the existing KB content."""
    client = anthropic.Anthropic()

    full_path = REPO_ROOT / target_file
    existing_content = full_path.read_text() if full_path.exists() else ""

    system_prompt = """You are a knowledge base editor for Ohanafy, a beverage supply chain SaaS platform.

Your task: integrate a new insight from a content-watcher issue into an existing knowledge base file.

Rules:
- Preserve the existing structure and formatting
- Add the new information in the most appropriate section
- If no section fits, create a minimal new subsection
- Keep the same markdown style (headers, tables, lists)
- Do not remove or significantly rewrite existing content
- Add a <!-- Source: [issue title] --> comment near the new content for traceability
- Be concise — one paragraph or a few bullet points is usually enough

Return the COMPLETE updated file content (not just the diff)."""

    response = client.messages.create(
        model="claude-sonnet-4-6-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"## Target file: {target_file}\n\n## Current content:\n{existing_content}\n\n## New insight to integrate:\nTitle: {issue_title}\n\n{issue_body}",
            }
        ],
    )
    return response.content[0].text.strip()


def create_pr(target_file: str, new_content: str, issue_number: int, issue_title: str) -> str:
    """Create a PR with the KB update."""
    branch_name = f"kb-update/issue-{issue_number}"

    # Create branch, write file, commit, push, create PR
    subprocess.run(["git", "checkout", "-b", branch_name], check=True, cwd=REPO_ROOT)

    full_path = REPO_ROOT / target_file
    full_path.write_text(new_content)

    subprocess.run(["git", "add", target_file], check=True, cwd=REPO_ROOT)
    subprocess.run(
        ["git", "commit", "-m", f"docs: update {target_file} from content insight #{issue_number}"],
        check=True,
        cwd=REPO_ROOT,
    )
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True, cwd=REPO_ROOT)

    # Create PR
    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"KB: {issue_title[:60]}",
            "--body",
            f"Auto-generated KB update from content insight #{issue_number}.\n\nUpdates: `{target_file}`",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return result.stdout.strip()


def process_issue(issue: dict, dry_run: bool = False) -> None:
    """Process a single content-insight issue."""
    issue_number = issue["number"]
    issue_title = issue["title"]
    issue_body = issue.get("body", "")
    labels = [l["name"] for l in issue.get("labels", [])]

    # Detect category from labels
    category = ""
    for label in labels:
        if label in CATEGORY_TARGETS:
            category = label
            break
    # Fallback: parse from issue body
    if not category:
        for cat in CATEGORY_TARGETS:
            if cat in issue_body.lower():
                category = cat
                break

    logger.info("Processing issue #%d: %s (category: %s)", issue_number, issue_title, category or "unknown")

    # Determine target file
    target_file = determine_target_file(issue_body, category)
    if target_file == "SKIP":
        logger.info("No suitable KB file found for issue #%d, skipping", issue_number)
        return

    logger.info("Target file: %s", target_file)

    if dry_run:
        print(f"[DRY RUN] Issue #{issue_number} → {target_file}")
        print(f"  Title: {issue_title}")
        print(f"  Category: {category}")
        return

    # Synthesize the update
    new_content = synthesize_update(target_file, issue_body, issue_title)

    # Create PR
    pr_url = create_pr(target_file, new_content, issue_number, issue_title)
    logger.info("Created PR: %s", pr_url)
    print(f"Created PR for issue #{issue_number}: {pr_url}")


def main():
    parser = argparse.ArgumentParser(description="Knowledge Base Writer")
    parser.add_argument("--issue", type=int, help="Process a specific issue number")
    parser.add_argument("--scan", action="store_true", help="Find and process all kb-approved issues")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating PRs")
    parser.add_argument("--repo", default="ohanafy/ai-ops", help="GitHub repo (default: ohanafy/ai-ops)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.issue:
        issue = get_github_issue(args.repo, args.issue)
        process_issue(issue, dry_run=args.dry_run)
    elif args.scan:
        issues = find_approved_issues(args.repo)
        if not issues:
            print("No kb-approved issues found.")
            return
        print(f"Found {len(issues)} approved issues")
        for issue in issues:
            process_issue(issue, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
