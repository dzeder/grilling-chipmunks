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

## Ohanafy SKU Repos (Ohanafy GitHub org)

**What:** Source indexes for 20+ Ohanafy product repos (Apex classes, triggers, methods, fields, LWC)
**Indexed to:** `skills/ohfy-*/references/source-index.md` and `references/ohanafy-index/*/source-index.md`
**Sync method:** Agent-driven — agents run `scripts/sync-ohanafy-index.sh` when indexes are stale
**Deep dive fallback:** Clone-on-demand to `/tmp/` for full source access

### Sync commands
```bash
bash scripts/sync-ohanafy-index.sh                    # sync all mapped repos
bash scripts/sync-ohanafy-index.sh --repo OHFY-OMS    # sync single repo
bash scripts/sync-ohanafy-index.sh --discover          # find new repos in org
```

### Mapped repos (20)
Primary: OHFY-Core, OHFY-Data_Model, OHFY-Platform, OHFY-OMS, OHFY-WMS, OHFY-REX, OHFY-Ecom, OHFY-Payments, OHFY-EDI, OHFY-Configure
UI: OHFY-OMS-UI, OHFY-WMS-UI, OHFY-REX-UI, OHFY-PLTFM-UI
Secondary: OHFY-Service_Locator, OHFY-Planogram
Standalone: OHFY-Utilities, OHFY-CICD, OHFY-SF-Perf, OHFY-Workflows

## shanraisshan/claude-code-best-practice

**What:** Claude Code best practices, tips, implementation guides, orchestration patterns
**Vendored to:** `references/claude-code-best-practices/`
**Sync method:** VERSION file (commit hash) + `scripts/update-best-practices.sh`
**Auto-check:** `.github/workflows/check-best-practices-update.yml` (weekly, Wednesdays)

### What we vendor
- `best-practice/` — 7 core docs (skills, subagents, commands, memory, MCP, settings, power-ups)
- `tips/` — Tips from Boris Cherny, Thariq, and others
- `implementation/` — 5 implementation guides
- `orchestration/` — Multi-agent orchestration workflow
- `reports/` — 4 selected reports (monorepo skills, agent memory, tool use, command-skill comparison)

### Manual update
```bash
bash scripts/update-best-practices.sh           # preview
bash scripts/update-best-practices.sh --apply   # apply
```
