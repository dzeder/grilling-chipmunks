---
name: github-agent
description: >
  GitHub Actions health audit, CI/CD best practices validation, and repo configuration review
  with 100-point scoring. TRIGGER when: user asks about CI/CD health, GitHub Actions failures,
  workflow optimization, repo configuration audit, or mentions "github", "workflow", "actions",
  "CI failures", "pipeline health". DO NOT TRIGGER when: deploying Salesforce metadata
  (use sf-deploy), running Apex tests (use sf-testing), managing secrets (use security),
  or checking code quality (use health).
metadata:
  version: "1.0.0"
  author: "Daniel Zeder"
  scoring: "100 points across 5 categories"
---

# github-agent: GitHub Actions Health Audit & CI/CD Best Practices

Use this skill when the user needs **GitHub Actions health assessment**: workflow failure diagnosis, CI/CD configuration audit, repo settings validation, workflow efficiency analysis, or best practices enforcement.

## When This Skill Owns the Task

Use `github-agent` when the work involves:
- GitHub Actions workflow failures or debugging
- CI/CD pipeline health checks
- Workflow YAML review and optimization
- Repo configuration audit (branch protection, templates, Dependabot)
- GitHub Actions best practices validation
- Workflow efficiency analysis (caching, concurrency, path filters)
- Action version pinning and security review

Delegate elsewhere when the user is:
- deploying Salesforce metadata -> [sf-deploy](../sf-deploy/SKILL.md)
- managing secrets or credentials -> [security](../security/SKILL.md)
- checking code quality (linting, tests, dead code) -> `/health`
- reviewing a PR diff -> `/review`

## Examples

- "Our CI is failing on the main branch" -- run discovery, diagnose workflow failures, suggest fixes
- "Audit our GitHub repo configuration" -- full 100-point audit across security, correctness, efficiency, config, maintainability
- "Are our GitHub Actions following best practices?" -- analyze workflow YAML files for anti-patterns and improvements

---

## Required Context to Gather First

Before starting the audit:

1. **Detect repo** — Run and parse the owner/repo for use in all subsequent API calls:
   ```bash
   OWNER_REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
   OWNER="${OWNER_REPO%/*}"
   REPO="${OWNER_REPO#*/}"
   DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')
   ```
2. **Verify `gh` auth** — `gh auth status`. If not authenticated, stop and instruct the user to run `gh auth login`
3. **Ask scope** — Full audit or focused area? (workflows only, repo config only, specific workflow)

---

## Recommended Workflow

### 1. Discovery

Gather the full picture before analyzing:

```bash
# Recent workflow runs (last 20)
gh run list --limit 20 --json name,status,conclusion,createdAt,headBranch,event

# All workflow files
ls .github/workflows/*.{yml,yaml}

# Repo settings
gh repo view --json name,defaultBranchRef,hasIssuesEnabled,hasWikiEnabled,hasProjectsEnabled,isPrivate,visibility

# Check branch protection
gh api repos/{owner}/{repo}/branches/{default-branch}/protection 2>/dev/null || echo "No branch protection or insufficient permissions"
```

Read every `.github/workflows/*.{yml,yaml}` file. Also check for:
- `.github/labeler.yml`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`

### 2. Workflow YAML Analysis

For each workflow file, check:

**Security & Permissions:**
- [ ] Has explicit top-level `permissions:` block (not relying on repo defaults)
- [ ] Permissions follow least-privilege principle (only what's needed)
- [ ] No `${{ }}` interpolation in `run:` steps that could enable shell injection
- [ ] No hardcoded secrets or tokens in workflow files
- [ ] Third-party actions pinned to SHA (not just tag)
- [ ] First-party actions (`actions/*`) use consistent versions

**Correctness:**
- [ ] Every workflow has a `name:` field
- [ ] Triggers are intentional and non-overlapping
- [ ] Features used are actually enabled (e.g., CodeQL requires code scanning)
- [ ] `continue-on-error: true` is justified, not masking real failures
- [ ] Job dependencies (`needs:`) are correct
- [ ] Conditional steps (`if:`) are logically sound

**Efficiency:**
- [ ] `concurrency:` groups with `cancel-in-progress: true` on PR workflows
- [ ] `paths:` filters on push/PR triggers where appropriate
- [ ] Caching enabled (`actions/cache`, `setup-*` with `cache:` parameter)
- [ ] No duplicate work across workflows (e.g., same lint in two places)
- [ ] Matrix builds are justified (not running identical configs)

**Maintainability:**
- [ ] Consistent `actions/checkout` version across all workflows
- [ ] Descriptive job and step names
- [ ] No dead or orphaned workflows
- [ ] Scheduled workflows have reasonable cron intervals

### 3. Repo Configuration Audit

```bash
# Branch protection rules
gh api repos/{owner}/{repo}/branches/{default-branch}/protection --jq '{
  required_reviews: .required_pull_request_reviews.required_approving_review_count,
  status_checks: .required_status_checks.contexts,
  enforce_admins: .enforce_admins.enabled,
  linear_history: .required_linear_history.enabled
}' 2>/dev/null

# Code scanning status
gh api repos/{owner}/{repo}/code-scanning/alerts --jq 'length' 2>/dev/null

# Secret scanning
gh api repos/{owner}/{repo}/secret-scanning/alerts --jq 'length' 2>/dev/null

# Dependabot alerts
gh api repos/{owner}/{repo}/dependabot/alerts --jq 'length' 2>/dev/null
```

Check for:
- [ ] Branch protection on default branch
- [ ] Required PR reviews before merge
- [ ] Status checks required before merge
- [ ] Code scanning enabled (if CodeQL workflow exists)
- [ ] CODEOWNERS file present
- [ ] Issue templates configured
- [ ] PR template configured
- [ ] Dependabot configured

### 4. Efficiency Analysis

Look for waste:
- Workflows that run on every push but only matter for specific directories
- Multiple workflows doing overlapping work
- Missing caching that adds minutes to every run
- Workflows triggered by events they immediately filter out (e.g., all PRs but exits if not dependabot)
- Scheduled workflows that could be event-driven instead

### 5. Score & Prioritize

Rate each category 0-20. Deduct points for each finding:

| Category | 20 pts | What it measures |
|---|---|---|
| **Security & Permissions** | 20 | Least-privilege `permissions:`, no shell injection, action pinning |
| **Workflow Correctness** | 20 | Valid triggers, feature prerequisites, no masked failures |
| **Efficiency** | 20 | Caching, concurrency, path filters, no duplicate work |
| **Repo Configuration** | 20 | Branch protection, CODEOWNERS, templates, Dependabot |
| **Maintainability** | 20 | Naming, consistent versions, documentation, no dead workflows |

**Deduction guide:**
- Critical (blocks CI): -5 pts
- High (security risk or significant waste): -3 pts
- Medium (improvement opportunity): -2 pts
- Low (cosmetic or informational): -1 pt

### 6. Report & Fix

Output the health report in this format:

```markdown
# GitHub Health Report

**Repo:** {owner}/{repo}
**Date:** {date}
**Score:** {total}/100

## Scores by Category
| Category | Score | Status |
|---|---|---|
| Security & Permissions | /20 | {status-emoji} |
| Workflow Correctness | /20 | {status-emoji} |
| Efficiency | /20 | {status-emoji} |
| Repo Configuration | /20 | {status-emoji} |
| Maintainability | /20 | {status-emoji} |

## Recent Workflow Status
| Workflow | Last Run | Status | Branch |
|---|---|---|---|

## Findings

### Critical
{numbered list with file:line references}

### High
{numbered list}

### Medium
{numbered list}

### Low
{numbered list}

## Recommended Fixes
{for each automatable fix, describe what would change and offer to apply}
```

After presenting the report, ask if the user wants to apply any of the automatable fixes.

---

## High-Signal Issue Patterns

| Pattern | How to detect | Severity | Fix |
|---|---|---|---|
| Missing `permissions:` | No top-level `permissions:` key in YAML | High | Add explicit block with minimum required permissions |
| CodeQL without code scanning | `codeql-action/analyze` in workflow + API returns 403/404 | Critical | Enable in repo settings OR remove CodeQL job |
| Shell injection via `${{ }}` | `${{ steps.*.outputs.* }}` or `${{ github.event.* }}` in `run:` | High | Use environment variable instead: `env: VAR: ${{ ... }}` then `$VAR` |
| Inconsistent action versions | Different `@v` tags for same action across workflows | Medium | Standardize to latest stable |
| Missing caching | `setup-python`/`setup-node` without `cache:` parameter | Medium | Add `cache: pip` or `cache: npm` |
| Duplicate work | Same checks in multiple workflows | Medium | Consolidate or differentiate scope |
| Broad triggers | `on: push` without `paths:` on non-CI workflows | Low | Add `paths:` filter |
| `continue-on-error: true` | Grep for `continue-on-error: true` | Medium | Remove or replace with conditional `if: failure()` |
| Dead workflows | Workflow file exists but never triggers or always skips | Low | Remove or fix triggers |

---

## Cross-Skill Integration

| Need | Delegate to |
|---|---|
| Secret rotation or .env management | `security` |
| Salesforce deployment pipelines | `sf-deploy` |
| Code quality (lint, test, dead code) | `/health` |
| PR diff review | `/review` |
| Release creation | `release-agent.yml` workflow |
| Upstream dependency monitoring | `check-*-update.yml` workflows |

---

## Reference Map

| Document | Purpose |
|---|---|
| [GitHub Actions Best Practices](references/github-actions-best-practices.md) | Comprehensive best practices reference |
| [Workflow Anti-Patterns](references/workflow-anti-patterns.md) | Common anti-patterns with fix patterns |
| [Repo Health Checklist](references/repo-health-checklist.md) | Structured audit checklist and report template |
| [gh CLI Commands](references/gh-cli-commands.md) | Commands used by this skill with expected outputs |

---

## Score Guide

| Range | Meaning |
|---|---|
| 90-100 | Excellent — minor polish only |
| 75-89 | Good — a few improvements recommended |
| 50-74 | Needs attention — significant issues to address |
| 25-49 | Poor — multiple critical/high findings |
| 0-24 | Critical — CI is broken or seriously misconfigured |
