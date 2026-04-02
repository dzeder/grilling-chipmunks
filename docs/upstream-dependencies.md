# Upstream Dependencies

How to keep vendored dependencies up to date.

## gstack (garrytan/gstack)

**Location:** `.claude/skills/gstack/`
**Upstream:** https://github.com/garrytan/gstack
**Strategy:** Vendored copy, updated via script or automated PR

### Manual update

Preview what changed:
```bash
bash scripts/update-gstack.sh
```

Apply the update:
```bash
bash scripts/update-gstack.sh --apply
cd .claude/skills/gstack && ./setup    # rebuild browser binary
git add .claude/skills/gstack
git commit -m "chore: update gstack to <version>"
```

### Automated updates

A GitHub Action (`.github/workflows/check-gstack-update.yml`) runs every Monday:
1. Compares your `VERSION` file against upstream
2. If different, copies the update into a branch
3. Opens a PR for you to review

You review the PR, check for breaking changes, merge, then rebuild locally.

### Why not git subtree or submodule?

| Approach | Pros | Cons |
|----------|------|------|
| **Vendored copy (current)** | Simple, full control, can review before updating | Manual sync, no git history from upstream |
| **Git subtree** | Preserves upstream history, can push changes back | Complex commands, messy merge conflicts |
| **Git submodule** | Clean separation, always points to exact commit | Detached HEAD pain, everyone needs access, forgotten updates |

We chose vendored copy because:
- gstack moves fast (multiple releases per week)
- We don't modify gstack ourselves — we just consume it
- The update script + automated PR gives us control over when to adopt changes
- No git submodule headaches for the team

### If you want to switch to git subtree later

```bash
# Remove vendored copy
git rm -r .claude/skills/gstack
git commit -m "Remove vendored gstack (switching to subtree)"

# Add as subtree
git subtree add --prefix=.claude/skills/gstack https://github.com/garrytan/gstack.git main --squash

# Future updates
git subtree pull --prefix=.claude/skills/gstack https://github.com/garrytan/gstack.git main --squash
```

This preserves upstream commit messages and handles merges better, but the commands are harder to remember.

## sf-skills (davis-v1)

**Location:** `skills/sf-*`, `agents/fde-*`, `agents/ps-*`, `shared/`, `tools/`, `tests/`
**Upstream:** The original sf-skills repo (ask Jag for the URL)
**Strategy:** Cherry-pick improvements you want

Since you've restructured sf-skills into this monorepo, there's no 1:1 sync. When the upstream author releases improvements:

```bash
# Add as remote
git remote add sf-skills-upstream <url>
git fetch sf-skills-upstream

# Cherry-pick specific commits
git cherry-pick <commit-sha>

# Or diff and manually apply
git diff sf-skills-upstream/main -- skills/sf-apex/SKILL.md
```

## dhsOhanafy/Integrations

**Location:** `skills/tray-*`, `skills/ohfy-*`, `agents/edi-*`, `integrations/patterns/`
**Upstream:** https://github.com/dhsOhanafy/Integrations
**Strategy:** Coordinate with your coworker — he updates skills here, or you cherry-pick from his repo

Since you're both building this monorepo together, the simplest approach is:
- Both contribute directly to daniels-ohanafy
- His Integrations repo becomes the reference/archive
- New skills and patterns go into daniels-ohanafy first
