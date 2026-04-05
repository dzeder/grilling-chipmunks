#!/usr/bin/env python3
"""
Fetches all Ohanafy GitHub repos, categorizes with Claude,
writes draft registry/ohanafy-repos.yaml for team review.

Usage: python ci-cd/scripts/discover-repos.py
Requires: GITHUB_TOKEN (org read scope), ANTHROPIC_API_KEY
"""
import os, httpx, yaml, anthropic
from pathlib import Path

ORG = "Ohanafy"


def fetch_all_repos():
    repos, page = [], 1
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
               "Accept": "application/vnd.github+json"}
    while True:
        r = httpx.get(f"https://api.github.com/orgs/{ORG}/repos",
                      headers=headers,
                      params={"per_page": 100, "page": page, "sort": "full_name"})
        r.raise_for_status()
        batch = r.json()
        if not batch: break
        repos.extend(batch)
        page += 1
    print(f"Found {len(repos)} repos")
    return repos


def categorize(repos):
    client = anthropic.Anthropic()
    repo_list = "\n".join([
        f"- {r['name']} | lang:{r.get('language','?')} | "
        f"desc:{r.get('description','') or 'none'} | "
        f"updated:{r['updated_at'][:10]} | archived:{r['archived']}"
        for r in repos
    ])
    prompt = f"""Ohanafy is a beverage supply chain SaaS on Salesforce, AWS, and Tray.ai.
They have many repos split by SKU — separate frontend and backend per product area,
plus shared core repos and a data model repo.

Categorize each repo. For each output a YAML entry with:
- id: slug (lowercase-hyphens)
- name: original repo name
- github_url: https://github.com/Ohanafy/[name]
- type: frontend|backend|core|data-model|shared|salesforce|infrastructure|tooling|archived|unknown
- sku: product SKU or "all" (shared) or "unknown"
- stack: [technologies based on language and name]
- owned_by: "unknown — fill in"
- active: true|false
- notes: one sentence max

Repos:
{repo_list}

Respond with valid YAML list only. No preamble. No markdown fences."""

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8096,
        messages=[{"role": "user", "content": prompt}]
    )
    return yaml.safe_load(resp.content[0].text)


def write_registry(categorized, raw_repos):
    path = Path("registry/ohanafy-repos.yaml")
    path.parent.mkdir(exist_ok=True)
    registry = {
        "version": "1.0",
        "status": "DRAFT — fix owned_by, sku, unknown types before committing",
        "total_repos": len(raw_repos),
        "rules": [
            "Check this registry before any PR in an Ohanafy product repo",
            "Never modify a repo without knowing its owner",
            "frontend and backend repos for the same SKU deploy together",
            "data-model changes require a migration plan before any deploy",
        ],
        "repos": categorized,
    }
    path.write_text(yaml.dump(registry, default_flow_style=False, sort_keys=False))
    print(f"Written to {path}")
    print("Next: fix owned_by fields, correct any sku=unknown, mark deprecated repos active=false")


if __name__ == "__main__":
    raw = fetch_all_repos()
    print("Categorizing with Claude...")
    write_registry(categorize(raw), raw)
