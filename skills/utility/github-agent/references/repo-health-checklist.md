# Repo Health Checklist

Structured checklist for the github-agent audit. Use this as the scoring rubric and report template.

## Security & Permissions (20 pts)

| Check | Points | Pass criteria |
|---|---|---|
| All workflows have explicit `permissions:` | 5 | Every `.yml` file has top-level `permissions:` |
| Permissions follow least privilege | 3 | No `write-all` or unnecessary write permissions |
| No shell injection vectors | 4 | No `${{ }}` in `run:` with user-controllable values |
| Third-party actions pinned to SHA | 3 | Non-`actions/*` uses full commit SHA |
| No hardcoded secrets in workflow files | 3 | No API keys, tokens, or passwords in YAML |
| Secret scanning enabled | 2 | `gh api` confirms secret scanning is active |

## Workflow Correctness (20 pts)

| Check | Points | Pass criteria |
|---|---|---|
| All workflows have `name:` field | 2 | No workflow shows raw filepath as name |
| Triggers are correct and intentional | 4 | No unintended trigger overlap or orphan triggers |
| Feature prerequisites are met | 5 | CodeQL only if code scanning enabled, etc. |
| `continue-on-error` is justified | 3 | Each usage has a documented reason |
| Job dependencies are correct | 3 | `needs:` chains are logical |
| No dead or orphaned workflows | 3 | All workflows trigger and complete |

## Efficiency (20 pts)

| Check | Points | Pass criteria |
|---|---|---|
| PR workflows have `concurrency:` groups | 4 | Cancel-in-progress enabled |
| Appropriate `paths:` filters | 4 | Workflows don't run on irrelevant changes |
| Package manager caching enabled | 4 | `setup-*` uses `cache:` parameter |
| No duplicate work across workflows | 4 | Same check doesn't run in multiple places |
| No wasted runner startups | 2 | Broad triggers with immediate exit are minimized |
| Scheduled intervals are reasonable | 2 | Not running more often than needed |

## Repo Configuration (20 pts)

| Check | Points | Pass criteria |
|---|---|---|
| Branch protection on default branch | 5 | Exists with reasonable settings |
| Required PR reviews | 3 | At least 1 review required |
| Status checks required | 3 | CI must pass before merge |
| CODEOWNERS file exists | 2 | `.github/CODEOWNERS` present |
| Issue templates configured | 2 | `.github/ISSUE_TEMPLATE/` has templates |
| PR template configured | 2 | `.github/PULL_REQUEST_TEMPLATE.md` exists |
| Dependabot configured | 3 | `.github/dependabot.yml` exists or Dependabot enabled |

## Maintainability (20 pts)

| Check | Points | Pass criteria |
|---|---|---|
| Consistent action versions | 5 | Same action uses same version everywhere |
| Descriptive job and step names | 3 | Names describe what, not how |
| Workflow files are well-organized | 3 | Clear separation of concerns |
| No stale or unmaintained workflows | 3 | All workflows have run recently or are scheduled |
| Setup scripts are parameterized | 3 | No hardcoded repo names or paths |
| Labeler config matches repo structure | 3 | `.github/labeler.yml` covers actual directories |

---

## Report Template

```markdown
# GitHub Health Report

**Repo:** {owner}/{repo}
**Date:** {YYYY-MM-DD}
**Score:** {total}/100

## Scores by Category

| Category | Score | Status |
|---|---|---|
| Security & Permissions | {n}/20 | {emoji} |
| Workflow Correctness | {n}/20 | {emoji} |
| Efficiency | {n}/20 | {emoji} |
| Repo Configuration | {n}/20 | {emoji} |
| Maintainability | {n}/20 | {emoji} |

Status key: 18-20 = green, 14-17 = yellow, 0-13 = red

## Recent Workflow Status

| Workflow | Last Run | Result | Trigger |
|---|---|---|---|
| {name} | {date} | {pass/fail} | {push/pr/schedule} |

## Findings

### Critical (blocks CI)
1. {finding with file:line reference}

### High (security risk or significant waste)
1. {finding}

### Medium (improvement opportunity)
1. {finding}

### Low (cosmetic or informational)
1. {finding}

## Recommended Fixes

### Automatable
For each fix, describe:
- **File:** {path}
- **Change:** {what to modify}
- **Impact:** {what improves}

### Manual (requires repo settings)
- {setting to change in GitHub UI}
```
