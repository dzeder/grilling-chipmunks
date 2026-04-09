# Changelog

All notable changes to this project will be documented in this file.

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
