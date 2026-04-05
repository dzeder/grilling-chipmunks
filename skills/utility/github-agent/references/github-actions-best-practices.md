# GitHub Actions Best Practices

## 1. Permission Scoping

Always declare explicit `permissions:` at the workflow level. Never rely on repo-wide defaults (which may be `write-all`).

```yaml
# Good: explicit least-privilege
permissions:
  contents: read
  pull-requests: write

# Bad: no permissions block = inherits repo default (often write-all)
```

**Rule:** Every workflow file must have a top-level `permissions:` block. Only request what the workflow actually needs.

Common permission patterns:
| Workflow type | Typical permissions |
|---|---|
| CI (lint + test) | `contents: read` |
| PR review/comment | `contents: read`, `pull-requests: write` |
| Auto-label | `contents: read`, `pull-requests: write` |
| Release creation | `contents: write` |
| Security scan (CodeQL) | `contents: read`, `security-events: write` |
| Issue management | `issues: write` |
| Auto-commit (docs gen) | `contents: write` |

## 2. Action Version Pinning

**Third-party actions:** Pin to full SHA for supply chain security.
```yaml
# Good
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

# Acceptable for first-party (actions/*)
- uses: actions/checkout@v4

# Bad: floating major version on third-party
- uses: some-org/some-action@v2
```

**First-party actions (`actions/*`):** Tag pinning (`@v4`) is acceptable since GitHub controls these. But be **consistent** — don't mix `@v4` and `@v6` for `actions/checkout` across workflows.

## 3. Trigger Hygiene

### Path filters
Workflows that only matter for certain directories should use `paths:` to avoid unnecessary runs:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'tests/**'
  pull_request:
    paths:
      - 'src/**'
      - 'tests/**'
```

### Concurrency groups
All PR-triggered workflows should cancel in-progress runs when new commits are pushed:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Schedule-only workflows
Workflows with only `schedule` and `workflow_dispatch` triggers should not appear in push/PR events. If they do, check for YAML parsing issues or workflow file validation errors.

## 4. Feature Prerequisites

Some actions require repo-level features to be enabled:

| Action | Requires |
|---|---|
| `github/codeql-action/analyze` | Code scanning enabled in Settings > Code security |
| `github/codeql-action/upload-sarif` | Code scanning enabled |
| `actions/dependency-review-action` | Dependency graph enabled |

**If the feature isn't enabled:** The workflow will fail with permission errors. Either enable the feature or remove the action.

## 5. Caching

Always enable caching for package managers:

```yaml
# Python
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'          # <-- this line

# Node.js
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'          # <-- this line
```

For custom caching:
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/some-tool
    key: ${{ runner.os }}-some-tool-${{ hashFiles('**/lockfile') }}
    restore-keys: |
      ${{ runner.os }}-some-tool-
```

## 6. Secret Handling

- Use `${{ secrets.GITHUB_TOKEN }}` (auto-generated, scoped to repo) over custom PATs when possible
- Never echo or log secret values in `run:` steps
- Use `environment:` for deployment secrets that need approval gates
- Reference secrets via `env:` block, not inline in `run:` commands:

```yaml
# Good
env:
  MY_TOKEN: ${{ secrets.CUSTOM_TOKEN }}
run: curl -H "Authorization: Bearer $MY_TOKEN" ...

# Avoid: secret could appear in debug logs if ACTIONS_STEP_DEBUG is enabled
run: curl -H "Authorization: Bearer ${{ secrets.CUSTOM_TOKEN }}" ...
```

## 7. Shell Injection Prevention

Never use `${{ }}` expressions directly in `run:` blocks — they're interpolated before bash runs, enabling injection:

```yaml
# VULNERABLE: attacker can craft a PR title with shell commands
run: echo "PR title is ${{ github.event.pull_request.title }}"

# SAFE: use environment variable
env:
  PR_TITLE: ${{ github.event.pull_request.title }}
run: echo "PR title is $PR_TITLE"
```

This applies to all user-controllable inputs:
- `github.event.pull_request.title`
- `github.event.pull_request.body`
- `github.event.issue.title`
- `github.event.comment.body` (issue/PR comments)
- `github.event.review.body` (PR review body)
- `github.event.discussion.title` and `.body`
- `github.head_ref` (branch name, user-controlled in fork PRs — especially dangerous because it looks safe and is commonly used in concurrency groups)
- `steps.*.outputs.*` (when output comes from user input)
- `github.event.head_commit.message`

## 8. Error Handling

`continue-on-error: true` should be rare and justified. It silently swallows failures.

**When it's OK:**
- Advisory checks that inform but shouldn't block (e.g., optional linting)
- Steps that genuinely might fail on some platforms but aren't critical

**When it's NOT OK:**
- Security scans (a real finding should block or at least be visible)
- Test execution (failures should fail the workflow)

**Better alternative:** Use conditional steps. Note: the step still shows as passing in the UI, but downstream steps can explicitly react to the failure, making it visible in workflow logic rather than silently swallowed:
```yaml
- name: Run optional check
  id: optional
  run: some-check || echo "check_failed=true" >> $GITHUB_OUTPUT

- name: Report optional check failure
  if: steps.optional.outputs.check_failed == 'true'
  run: echo "::warning::Optional check failed"
```

## 9. Workflow Naming

- Every workflow must have a `name:` field (without it, GitHub shows the file path)
- Job names should be descriptive: `name: Unit Tests` not `name: test`
- Step names should describe what they do: `name: Install Python dependencies` not `name: Setup`

## 10. Duplicate Work Prevention

Audit for overlapping work across workflows:
- If `ci.yml` runs lint and `lint-format-agent.yml` also runs lint on PRs, one is redundant
- If multiple workflows checkout and setup the same language, consider a reusable workflow
- Use `workflow_call` for shared job definitions:

```yaml
# .github/workflows/reusable-lint.yml
on:
  workflow_call:
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: ...

# .github/workflows/ci.yml
jobs:
  lint:
    uses: ./.github/workflows/reusable-lint.yml
```
