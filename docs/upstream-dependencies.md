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

## sf-skills (Jaganpro/sf-skills)

**Location:** `skills/sf-*`, `agents/fde-*`, `agents/ps-*`, `shared/`, `tools/`, `tests/`
**Upstream:** https://github.com/Jaganpro/sf-skills
**Version marker:** `skills/.sf-skills-upstream-version` (commit hash of last-reviewed upstream state)
**Strategy:** Preview upstream changes, cherry-pick what you want

Unlike gstack and best-practices, sf-skills is **not auto-applied**. You've restructured the skills into this monorepo and are increasingly customizing them for Ohanafy. The sync tool shows what changed upstream so you can cherry-pick generic Salesforce improvements while skipping things that conflict with your customizations.

### Preview what changed

```bash
bash scripts/update-sf-skills.sh
```

This shows: upstream commit log, per-skill diffs (NEW/CHANGED), agent changes, and shared infrastructure changes. It does not modify any files.

### Cherry-pick improvements

```bash
# Add the remote (first time only)
git remote add sf-skills-upstream https://github.com/Jaganpro/sf-skills.git
git fetch sf-skills-upstream

# Cherry-pick specific commits
git cherry-pick <sha>

# Or diff and manually apply a specific skill
git diff sf-skills-upstream/main -- skills/sf-apex/SKILL.md
```

### Mark as reviewed

After cherry-picking (or deciding to skip), update the version marker so the next run only shows new changes:

```bash
bash scripts/update-sf-skills.sh --mark-reviewed
```

### Automated notifications

A GitHub Action (`.github/workflows/check-sf-skills-update.yml`) runs every Friday:
1. Compares your version marker against upstream HEAD
2. If different and no existing open issue, opens a GitHub Issue with a change summary
3. The issue includes commit log, changed skills, and cherry-pick instructions

Schedule across the week: Monday (gstack), Wednesday (best-practices), Friday (sf-skills).

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

## Ecosystem Watch (external repos)

**What:** Lightweight monitoring of high-value Claude Code ecosystem repos
**Marker files:** `references/ecosystem-watch/*.last-checked`
**Sync method:** Biweekly GitHub Action creates Issues with change digests
**Script:** `scripts/check-ecosystem.sh`

### Monitored repos

| Repo | Why we watch it | What we look for |
|------|-----------------|------------------|
| `anthropics/claude-code` | Official harness | New hook types, CLI features, harness changes |
| `hesreallyhim/awesome-claude-code` | Curated community patterns | Skills/plugins gaining traction |

### What we decided NOT to monitor

After evaluating the Claude Code ecosystem (April 2026), we rejected most external repos:

| Repo | Why rejected |
|------|-------------|
| `wshobson/agents` (112 agents) | Breadth over depth — our 17 coordinated agents with pod structure are more sophisticated |
| `VoltAgent/awesome-claude-code-subagents` | Generic install-script subagents dilute domain expertise |
| `VoltAgent/awesome-agent-skills` | Our domain skills (ohfy-*, sf-*, tray-*) are already more specialized; check for packaging conventions only |
| `ruvnet/ruflo` (agent swarms) | Solves general compute parallelism, not domain-expert coordination |
| `shareAI-lab/learn-claude-code` | Heartbeat/cron patterns interesting but we already have /loop and /schedule |

### Manual check
```bash
bash scripts/check-ecosystem.sh    # show digest of changes
```

### Automated notifications

A GitHub Action (`.github/workflows/check-ecosystem.yml`) runs biweekly (1st and 15th):
1. Checks monitored repos via `git ls-remote`
2. If changes detected and no existing open issue, creates a GitHub Issue
3. Issues are labeled `ecosystem-watch` for easy filtering

Schedule across the month: 1st + 15th (ecosystem), plus weekly Mon/Wed/Fri for gstack/best-practices/sf-skills.
