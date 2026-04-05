# Workflow Anti-Patterns

Common GitHub Actions anti-patterns with detection methods and fix patterns.

## 1. Missing Permissions Block

**Pattern:** Workflow has no top-level `permissions:` key, inheriting repo defaults.

**Detection:**
```bash
for f in .github/workflows/*.{yml,yaml}; do
  if ! grep -q '^permissions:' "$f"; then
    echo "MISSING: $f"
  fi
done
```

**Risk:** Repo default is often `write-all`, violating least privilege.

**Fix:** Add explicit `permissions:` block. For read-only workflows:
```yaml
permissions:
  contents: read
```

---

## 2. CodeQL Without Code Scanning Enabled

**Pattern:** Workflow uses `github/codeql-action/analyze@v4` but code scanning is not enabled in repo settings.

**Detection:**
```bash
# Check if any workflow uses CodeQL
grep -l 'codeql-action' .github/workflows/*.{yml,yaml}

# Check if code scanning is enabled
gh api repos/{owner}/{repo}/code-scanning/alerts --jq 'length' 2>&1
# If returns 403 or "not enabled" error, it's not enabled
```

**Symptoms:** CodeQL Analysis job fails every run with "Code scanning is not enabled for this repository."

**Fix options:**
1. Enable code scanning: Settings > Code security and analysis > Code scanning > Enable
2. Remove the CodeQL job from the workflow if code scanning isn't needed
3. Make the CodeQL job conditional: `if: github.event_name == 'schedule'` (run only on schedule, not push)

---

## 3. Inconsistent Action Versions

**Pattern:** Same action uses different version tags across workflows (e.g., `actions/checkout@v4` in one, `@v6` in another).

**Detection:**
```bash
grep -rn 'uses: actions/checkout@' .github/workflows/ | sort -t@ -k2
```

**Risk:** Different behavior across workflows, harder to maintain.

**Fix:** Standardize to the latest stable version across all workflows.

---

## 4. Shell Injection via Expression Interpolation

**Pattern:** `${{ }}` expressions used directly in `run:` steps with user-controllable values.

**Detection:**
```bash
# Check for dangerous interpolation in run blocks
grep -n '\${{ github\.event\.' .github/workflows/*.{yml,yaml}
grep -n '\${{ steps\.' .github/workflows/*.{yml,yaml} | grep 'run:'
```

**Risk:** Attacker can inject shell commands via PR titles, commit messages, or other user-controlled fields.

**Fix:** Use `env:` to pass values safely:
```yaml
# Before (vulnerable)
run: echo "${{ github.event.pull_request.title }}"

# After (safe)
env:
  TITLE: ${{ github.event.pull_request.title }}
run: echo "$TITLE"
```

---

## 5. Duplicate Work Across Workflows

**Pattern:** Multiple workflows performing the same checks (e.g., shell lint in both CI and a dedicated lint workflow).

**Detection:** Compare step commands across all workflow files. Look for identical `run:` blocks or same tool invocations.

**Fix options:**
1. Remove the duplicate from one workflow
2. Create a reusable workflow (`workflow_call`) and reference it from both
3. Differentiate scope (one does quick lint, other does deep lint)

---

## 6. Missing Caching

**Pattern:** `setup-python` or `setup-node` used without the `cache:` parameter, causing fresh dependency installation on every run.

**Detection:**
```bash
grep -A3 'setup-python@' .github/workflows/*.{yml,yaml} | grep -v 'cache:'
grep -A3 'setup-node@' .github/workflows/*.{yml,yaml} | grep -v 'cache:'
```

**Fix:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
```

---

## 7. Broad Triggers Without Path Filters

**Pattern:** Workflow triggers on all pushes/PRs but only matters for specific file types.

**Detection:** Check if workflow steps only operate on specific file patterns but trigger on everything.

**Fix:**
```yaml
on:
  pull_request:
    paths:
      - '**.py'
      - 'tests/**'
```

---

## 8. continue-on-error Masking Failures

**Pattern:** `continue-on-error: true` on steps that should actually fail the workflow.

**Detection:**
```bash
grep -n 'continue-on-error: true' .github/workflows/*.{yml,yaml}
```

**Risk:** Real issues (security findings, test failures) are silently ignored.

**Fix:** Remove `continue-on-error: true` or replace with explicit conditional handling.

---

## 9. Missing Concurrency Groups

**Pattern:** PR-triggered workflows without `concurrency:` configuration, causing multiple runs to pile up.

**Detection:**
```bash
for f in .github/workflows/*.{yml,yaml}; do
  if grep -q 'pull_request' "$f" && ! grep -q 'concurrency:' "$f"; then
    echo "MISSING CONCURRENCY: $f"
  fi
done
```

**Fix:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

---

## 10. Wasted Runner Startups

**Pattern:** Workflow triggers on broad events but immediately exits via `if:` condition in the job.

**Example:** `dependabot-auto-merge.yml` triggers on all `pull_request` events but first step checks `if: github.actor == 'dependabot[bot]'`.

**Risk:** Runner spins up and tears down for every non-dependabot PR (wasted minutes).

**Fix:** Use event filtering where possible, or accept the trade-off if event filtering isn't expressive enough for the use case.
