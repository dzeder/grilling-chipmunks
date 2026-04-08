# Changelog

All notable changes to this project will be documented in this file.

## [0.0.1.0] - 2026-04-08

### Added
- First customer sandbox connection workflow: connect to a Salesforce sandbox, retrieve metadata, auto-detect Ohanafy SKUs, and generate an org snapshot
- Customer directory for The Beverage Market with full documentation (profile, integrations, known issues, notes, org snapshot)
- Per-object Ohanafy knowledge base (`knowledge-base/ohanafy/objects/`) with field-level gotchas, status lifecycles, and relationship maps for `ohfy__Order__c` and `ohfy__Order_Item__c`
- Gitignore for customer directories to prevent raw Salesforce metadata (force-app, package.xml) from being committed
