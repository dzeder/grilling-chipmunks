# Ohanafy Integration Points

<!-- Synthesized from integration guides, tray skills, and ohfy-*-expert skills -->

## Integration Architecture

```
                    ┌─────────────┐
                    │   Tray.io   │  ← Primary iPaaS
                    │   (iPaaS)   │
                    └──────┬──────┘
                           │
    ┌──────────┬───────────┼───────────┬──────────┐
    │          │           │           │          │
    ▼          ▼           ▼           ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Salesforce│ │  ERP   │ │  HCM  │ │ Cloud  │ │External│
│(Ohanafy)│ │(Encomp)│ │ (UKG) │ │ (AWS)  │ │ APIs   │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

## Active Integration Projects

| Project | Source → Target | Pattern | Status |
|---------|----------------|---------|--------|
| **ohanafy-core** | Tray ↔ Salesforce | Bi-directional sync | Active |
| **netsuite-ohanafy** | NetSuite ↔ Salesforce | Batch sync via Tray | Active |
| **qbo-ohanafy** | QuickBooks Online ↔ Salesforce | Accounting sync via Tray | Active |
| **xero-ohanafy** | Xero ↔ Salesforce | Accounting sync via Tray | Active |
| **rehrig-ohanafy** | Rehrig ↔ Salesforce | Asset tracking sync | Active |
| **UKG → Ohanafy** | UKG Pro ↔ Salesforce | Employee/schedule sync | Customer-specific |

## Integration by System

### Salesforce (Ohanafy)
- **Role:** System of record for operational planning, CRM, task management
- **API:** REST API v62.0+, Composite API for batch operations
- **Connector:** Tray Salesforce connector v8.6
- **Key operations:** create_record, update_record, upsert_record (via external ID), find_records, bulk_upsert
- **Pattern:** Validate → Transform → Batch → Output (see `integrations/patterns/script-scaffold.js`)

### ERP (Encompass / VIP)
- **Role:** System of record for route accounting, warehouse, inventory, pricing
- **Challenge:** Progress/OpenEdge legacy with limited APIs
- **Integration pattern:** Typically flat file export → Tray processing → Salesforce upsert
- **Data flows:** Customer master, product master, order history, AR balances, pricing

### HCM (UKG)
- **Role:** System of record for employees, schedules, time-off, payroll
- **API:** UKG Pro REST API, UKG Pro WFM API
- **Data flows:** Employee roster, schedule data, time-off records, status changes
- **Pattern:** Polling-based sync (every 15 min for schedules, daily for roster)

### Cloud (AWS)
- **Services used:** S3 (file staging), Lambda (processing), Secrets Manager (credentials)
- **Pattern:** S3 as staging area for EDI files, Lambda for transformation processing
- **IaC:** CDK TypeScript in `skills/aws/cdk/`

### Accounting Systems
- **QuickBooks Online:** Invoice sync, payment sync, customer sync
- **NetSuite:** Full ERP sync for larger customers
- **Xero:** Invoice and payment sync for international customers

### E-Commerce
- **Shopify:** Product catalog, order capture, inventory sync
- **WooCommerce:** Product catalog, order capture

### EDI Partners
- **Standard:** X12 850 (purchase order), 810 (invoice), 856 (ASN)
- **Platforms:** OpenText, Transcepta
- **Pattern:** S3 → parse → validate → Salesforce → S3 output → Slack notification

## Integration Patterns Library

11 production-tested JavaScript modules in `integrations/patterns/`:

| Module | Purpose |
|--------|---------|
| `script-scaffold.js` | Full validate-transform-batch-output template |
| `soql-query-builder.js` | SOQL construction with 2000-value chunking |
| `batch-processing.js` | Array chunking, groupBy, dedup, Composite batches |
| `data-mapping.js` | Field rules engine with AND/OR logic |
| `error-handling.js` | Salesforce Composite error extraction |
| `validation.js` | Type/length/format checks |
| `string-manipulation.js` | Name normalization, SOQL sanitization |
| `csv-output.js` | Fixed-width and CSV generation |
| `date-time.js` | Salesforce date formats, timezone conversion |
| `lookup-maps.js` | Map/Set factories, status mapping |
| `output-structuring.js` | Success/error envelopes, summaries |

## Key Integration Principles

1. **Tray-first** — always check existing Tray workflows before building new
2. **External ID upserts** — use external IDs for idempotent Salesforce operations
3. **Validate → Transform → Batch → Output** — standard script flow
4. **2000-value chunking** — Salesforce SOQL IN clause limit
5. **Error envelope pattern** — structured success/error responses
6. **Watermark/delta sync** — use Tray Data Storage for tracking last sync point
7. **No credentials in code** — AWS Secrets Manager only
