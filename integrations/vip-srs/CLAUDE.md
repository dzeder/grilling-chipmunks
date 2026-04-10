# VIP SRS Integration

## What this is

Daily SFTP-to-Salesforce integration for VIP beverage distribution data. 9 source file types → 14 Ohanafy SF objects via Tray.io Script connectors.

## The spec

THE source of truth is `.context/attachments/VIP_AGENT_HANDOFF.md`. All field mappings, crosswalks, external ID formats, load order, and cleanup logic are defined there.

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

## Testing

```bash
cd tests/
node fixtures/run-test.js scripts/01-srschain-chains.js
```

Sample data from yangon workspace: `/Users/danielzeder/conductor/workspaces/conductor-playground/yangon/data/unzipped/`
