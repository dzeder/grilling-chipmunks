# Integrations

Tray patterns, marketplace UI, and workflow artifacts for Ohanafy integrations.

## Tray-First Rule

Before building anything new in Tray, check existing workflows. Never duplicate. Extend or reference existing workflows.

## Pattern Modules

11 production-tested JS modules in `patterns/`:

| Module | Purpose |
|--------|---------|
| `script-scaffold.js` | Full validate-transform-batch-output starter — **always use as template** |
| `soql-query-builder.js` | SELECT/WHERE builder, IN operator, 2000-value chunking |
| `batch-processing.js` | Array chunking, groupBy, dedup, SF Composite batches |
| `data-mapping.js` | Field rules engine with AND/OR logic, multi-priority resolution |
| `error-handling.js` | SF Composite error extraction, SOAP fault handling |
| `validation.js` | Required fields, type/length/format checks |
| `string-manipulation.js` | Business name normalization, SOQL sanitization |
| `csv-output.js` | Fixed-width formatters, CSV generation |
| `date-time.js` | SF date formats, timezone conversion (no external libs) |
| `lookup-maps.js` | Map/Set factories, status mapper, partitioning |
| `output-structuring.js` | Success/error envelopes, summaries |

## Workflow

1. Start from `script-scaffold.js`
2. Import needed pattern modules
3. Follow validate → transform → batch → output flow
4. Test with `/test-script` skill before committing

## Artifact Routing

Built artifacts (Tray exports, SF metadata, deliverables) go to `dzeder/daniels-ohanafy-artifacts` — never commit to this repo.

## Deep Dives

- Integration methodology: `docs/integration-guides/OHFY_INTEGRATION_MASTER_GUIDE.md`
- Business logic: `docs/integration-guides/OHFY_BUSINESS_LOGIC_LIBRARY.md`
- Tray connector ops: `docs/integration-guides/TRAY_CONNECTOR_OPERATIONS.md`
- Tray JSON structure: `docs/integration-guides/Tray-AI-Project-JSON-Structure-Guide.md`
