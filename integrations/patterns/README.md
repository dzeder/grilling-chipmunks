# Integration Patterns

11 production-tested JavaScript modules extracted from real Ohanafy/DHS integration code. These are **copy-paste reference patterns**, not importable modules — copy the functions you need into your Tray script.

## Usage

1. Start with `script-scaffold.js` for a new Tray script
2. Copy specific functions from the relevant pattern file
3. Adapt to your integration's data model and requirements

## Index

| File | Purpose |
|------|---------|
| `script-scaffold.js` | Full validate-transform-batch-output starter template |
| `soql-query-builder.js` | SELECT/WHERE builder, IN operator, 2000-value chunking |
| `batch-processing.js` | Array chunking, groupBy, dedup, SF Composite batch building |
| `data-mapping.js` | Field rules engine with AND/OR logic, multi-priority resolution |
| `error-handling.js` | SF Composite error extraction, SOAP fault handling |
| `validation.js` | Required fields, type/length/format checks |
| `string-manipulation.js` | Business name normalization, SOQL sanitization |
| `csv-output.js` | Fixed-width formatters, CSV generation |
| `date-time.js` | SF date formats, timezone conversion (no external libs) |
| `lookup-maps.js` | Map/Set factories, status mapper, partitioning |
| `output-structuring.js` | Success/error envelopes, summaries |

## Related

- `docs/integration-guides/SCRIPT_CONSOLIDATION_PATTERNS.md` — Refactoring strategies
- `docs/integration-guides/OHFY_INTEGRATION_MASTER_GUIDE.md` — End-to-end methodology
- `skills/tray-script-generator/` — Skill for generating scripts using these patterns
