# Changelog

All notable changes to this project will be documented in this file.

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
