# VIP SRS Integration

## What this is

Daily SFTP-to-Salesforce integration for VIP beverage distribution data. 9 of 22 VIP file types are currently integrated → 14 Ohanafy SF objects via Tray.io Script connectors.

## The spec

THE source of truth for **Ohanafy field mappings** is `docs/VIP_AGENT_HANDOFF.md`. All field mappings, crosswalks, external ID formats, load order, and cleanup logic are defined there.

For the **complete VIP SRS specification** (all 22 file types, valid values, appendices), see `knowledge-base/vip-srs/`. This covers:
- All 22 VIP file types with complete field layouts
- Complete valid field value reference (Appendix B)
- ISV Spec v6.0 conventions (file format, naming, SFTP delivery)
- Appendices: repack logic, zero sales, summary inventory, depletion warehouse, retroactive discounts

The VIP SRS expert skill (`skills/ohanafy/ohfy-vip-srs-expert/SKILL.md`) routes agents to the right knowledge.

## Script structure

Every script in `scripts/` follows `integrations/patterns/script-scaffold.js`:

```
CONFIG → FIELD_MAPPINGS → VALIDATION_RULES → validate → transform → batch → output
```

Scripts are designed for Tray.io Script connectors:
- No `require()` — all dependencies are inlined
- Shared code from `shared/` is concatenated at build time
- `exports.step = function(input) { ... }` is the entry point
- Input comes from Tray variables (rows, lookups, config)
- Output is `{ batches, batchCount, records, recordCount, errors, errorCount, summary }`

## Shared modules

- `shared/constants.js` — Prefixes, crosswalk maps, trans codes
- `shared/external-ids.js` — Key generators for all 12 object types
- `shared/filters.js` — DistId filtering, control record detection
- `shared/transforms.js` — Date, phone, string transforms

These are source files for development/testing. For Tray deployment, inline the needed functions into each script.

## Key constraints

- SF Composite API: max 25 subrequests per batch
- Tray Script connector: memory limits — chunk large files (OUTDA ~36K rows)
- External IDs: only immutable business identifiers, colon-delimited, prefixed
- Load order: Phase 1 (references) → Phase 2 (enrichment) → Phase 3 (inventory) → Phase 4 (transactions)
- Namespace: `ohfy__` prefix on all managed package fields
- **VIP_File_Date__c = date of pipeline run** (not from file contents). FromDate/ToDate capture the reporting window. File date is for stale cleanup.
- **Placement__c** is Account×Item (not per transaction). External ID: `PLC:{DistId}:{AcctNbr}:{SuppItem}`. Master-detail fields are create-only.
- **Item lookup filter on Depletion__c.Item__c**: Items need Finished Good RT + Type__c + UOM__c + Packaging_Type__c + Transformation_Setting__c record. See ROADMAP.md Gotcha #14.

## Data Dictionary

`docs/VIP_DATA_DICTIONARY.md` — comprehensive field reference for report/dashboard builders. Covers all 16 SF objects, currency fields, date fields, crosswalks, relationships, and unmapped SLSDA fields. **Use this when building reports or answering "what data do we have?" questions.**

## Reports & Dashboards

Shared Salesforce reports and dashboards for VIP data live in `metadata/`. See `metadata/README.md` for the full catalog.

- Report types define object joins (e.g., Depletions with Items)
- Reports and dashboards deploy into a `VIP Data` folder in Salesforce
- Includes both supplier metrics (depletions, placements, inventory) and dirty data reports (orphans, stale records, missing fields)
- Development workflow: build in sandbox UI → retrieve → commit here → deploy to any VIP customer org

## Testing

```bash
cd tests/
node fixtures/run-test.js scripts/01-srschain-chains.js
```

Sample data from yangon workspace: `/Users/danielzeder/conductor/workspaces/conductor-playground/yangon/data/unzipped/`
