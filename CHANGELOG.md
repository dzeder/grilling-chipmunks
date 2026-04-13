# Changelog

All notable changes to this project will be documented in this file.

## [0.0.7.4] - 2026-04-13

### Changed
- Gstack upgrade workflow now auto-merges non-breaking (patch/minor) version bumps — no more manual PR review for routine updates
- Auto-merge waits for CI checks to pass before merging (`--auto` flag) and skips on push-triggered workflow runs
- Manual override available via `skip_auto_merge` input on workflow dispatch

## [0.0.7.3] - 2026-04-13

### Added
- Shipyard (ROS) CSO requirements captured in customer notes: sales rep territory tracking, new placement detection, flexible commission structures, and cross-sell/reorder alerts — all sourced from VIP SRS data

## [0.0.7.2] - 2026-04-10

### Added
- `/kickoff` skill — guided workspace setup wizard that asks what integration and which customer, then writes `.context/workspace.md` so all downstream skills know the working context automatically
- Context-loading protocol now checks `.context/workspace.md` first before falling back to branch-name parsing
- Workspace setup handoffs added to skill routing matrix (kickoff → org-connect, tray-expert, investigate)

## [0.0.7.1] - 2026-04-10

### Added
- SFBen YouTube channel (`@OfficialSFBen`) added to content watcher — Salesforce ecosystem videos now auto-scored and surfaced as insights
- Daily digest GitHub issue created after each pipeline run — one scannable summary per day in `ohanafy/ai-ops` with all insights grouped by category, scores, effort, and links to individual issues
- Quiet days labeled `(quiet day)` in the digest title so you know the pipeline ran but found nothing

## [0.0.7.0] - 2026-04-10

### Changed
- Synced 22 Salesforce skills from upstream `Jaganpro/sf-skills` (commits `a34ff34`, `11d9cf0`)
- `sf agent preview` CLI commands now use correct syntax for authoring bundles: explicit `--simulate-actions` or `--use-live-actions` required, `-o TARGET_ORG` on send/end
- External Client App metadata directories documented correctly: 6 separate top-level source directories with accurate file suffixes
- New "Right-Size Determinism" guidance for Agent Script: when to use Agent Script vs Flow/Apex, "Deterministic Sandwich" pattern, routing heuristics
- New decision trees: Tool Selection Preflight, Routing Quick Rules, Control Placement Cheat Sheet
- Agent testing coverage analysis now includes routing collision, turn-2 pivot, and gate bypass test templates
- Context placement rules and retrieval storage heuristics added to grounding/multiagent reference

### Source
Upstream: [Jaganpro/sf-skills](https://github.com/Jaganpro/sf-skills) `a64b0d1..11d9cf0`. Closes #72.

## [0.0.6.0] - 2026-04-09

### Added
- New `observability` skill pillar with `datadog-expert` skill — three modes: Q&A, Build (dashboard/monitor/SLO design as Terraform), Review (audit existing DD config with 6-dimension scoring)
- `datadog-expert-guide.md` knowledge base covering Ohanafy's DD architecture, beverage supply chain dashboards, Terraform patterns, and integration setup for AWS/Salesforce/Tray
- New `observability` category in `watchers/repos.yaml` tracking 4 Datadog repos: `shelfio/datadog-mcp` (critical), `DataDog/datadog-agent`, `DataDog/integrations-core`, `DataDog/datadog-lambda-python`
- `datadog-expert` registered in skills-registry.json with discovery keywords and intent patterns

## [0.0.5.0] - 2026-04-09

### Added
- `skills/simplify/SKILL.md` — new skill for behavior-preserving code simplification (5 principles, Chesterton's Fence, structured process)
- `skills/deprecation/SKILL.md` — new skill for deprecation decisions and migration planning (5-question decision tree, strangler/adapter/feature-flag patterns)
- `skills/idea-refine/SKILL.md` — new skill for structured ideation (3-phase divergent→convergent→sharpen process, 7 lenses, one-pager output)
- `docs/SECURITY_CHECKLIST.md` — pre-commit and OWASP security reference with Ohanafy-specific checks (SF FLS, Tray HMAC, AWS, LLM trust)
- `docs/TESTING_PATTERNS.md` — testing patterns reference with Ohanafy-specific patterns (SF API mocking, Tray webhook simulation, Apex testing)

### Changed
- `skills/review/SKILL.md` — enriched with 5-axis review framework, severity labels, Ohanafy-specific security checks
- `skills/ship/SKILL.md` — enriched with pre-ship checklist, rollback decision tree, post-deploy verification
- `skills/claude/context-manager/SKILL.md` — enriched with context hierarchy diagram, trust levels, anti-patterns table

### Source
All patterns adapted from `references/agent-skills/` (addyosmani/agent-skills), tracked via `learned_from` frontmatter in each skill.

## [0.0.4.0] - 2026-04-09

### Changed
- CLAUDE.md slimmed from 490 to 143 lines — every conversation now loads ~350 fewer irrelevant tokens
- Skill catalog, agent roster, integration patterns, and context loading extracted into dedicated files that lazy-load only when relevant
- Skill routing quick reference expanded to 15 routes (was 8)
- Customer Salesforce read-only rule now lists explicit prohibited CLI commands

### Added
- `.claude/rules/` with 3 glob-scoped rules: context-loading, integration-patterns, skill-routing
- `docs/SKILL_CATALOG.md` — full 114-skill catalog organized by pillar
- `agents/README.md` — agent roster with team groupings and selection guide
- `integrations/CLAUDE.md` — pattern module index with Tray-First reminder
- `references/README.md` — upstream mirror documentation (prevents agents from editing vendored content)
- `docs/README.md` — documentation index by category
- `scripts/validate-context.sh` — CI-ready context health checker (CLAUDE.md size, rules, indexes, freshness)
- `.claude/settings.local.json` added to `.gitignore` (security hygiene)

## [0.0.3.0] - 2026-04-08

### Added
- Draft Order Item Cleanup Tray project export: nightly 7pm EST scheduled workflow that finds orphaned draft order items (draft item on non-draft order with future delivery date), batch-updates them to non-draft, and Slack DMs results with success count or failure details including log URL
- Error handler workflow with alerting trigger that Slack DMs on any project error
- Extracted JavaScript transform script with test fixture directory

## [0.0.2.0] - 2026-04-08

### Added
- Draft Order Item Cleanup Tray project: importable JSON with nightly scheduled workflow that queries stale draft order items, batch-updates them via Salesforce, and Slack DMs results. Includes error alerting workflow.
- `tray-project` skill: generate importable Tray.io project JSON exports with authoritative spec covering flat UI format, typed values, auth objects, and all common step patterns
- Extracted script and test fixtures for the cleanup workflow's JavaScript transform step

### Changed
- CLAUDE.md: registered tray-project as the 16th integration skill
- Tray-AI-Project-JSON-Structure-Guide: added accuracy banner pointing to the authoritative spec for JSON generation
- gstack updated to 0.16.0.0

## [0.0.1.0] - 2026-04-08

### Added
- First customer sandbox connection workflow: connect to a Salesforce sandbox, retrieve metadata, auto-detect Ohanafy SKUs, and generate an org snapshot
- Customer directory for The Beverage Market with full documentation (profile, integrations, known issues, notes, org snapshot)
- Per-object Ohanafy knowledge base (`knowledge-base/ohanafy/objects/`) with field-level gotchas, status lifecycles, and relationship maps for `ohfy__Order__c` and `ohfy__Order_Item__c`
- Gitignore for customer directories to prevent raw Salesforce metadata (force-app, package.xml) from being committed
