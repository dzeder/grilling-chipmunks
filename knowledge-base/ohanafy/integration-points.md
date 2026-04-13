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

## Managed Package Data Loading Constraints

Hard-won lessons from loading data into subscriber orgs with the Ohanafy managed package installed. These apply to ANY integration, not just VIP SRS.

See `knowledge-base/ohanafy/objects/` for per-object details.

### Master-detail fields are create-only

Many managed objects (Inventory__c, Placement__c, Depletion__c) use master-detail relationships. These fields can only be set on INSERT, not UPDATE. Use `__r` relationship syntax in Composite API body. When updating existing records by SF ID, **strip master-detail fields from the PATCH body** or get `INVALID_FIELD_FOR_INSERT_UPDATE`.

### External ID field names vary by object

| Object | External ID Field | Managed? |
|--------|------------------|----------|
| Account | `ohfy__External_ID__c` | Yes |
| Contact | `External_ID__c` | No |
| Item__c | `ohfy__VIP_External_ID__c` | Yes |
| Location__c | `VIP_External_ID__c` | No |
| Inventory__c, History, Adjustment | `VIP_External_ID__c` | No |
| Placement__c | `VIP_External_ID__c` | No |
| Depletion__c | `VIP_External_ID__c` | No |
| Allocation__c | `VIP_External_ID__c` | No |

Never assume consistency — always check the field name per object.

### Validation rules may block upserts

The managed package has validation rules that enforce natural key uniqueness (e.g., Inventory__c blocks duplicate Item+Location combos). Standard upsert by external ID can INSERT when a record already exists under a different key, triggering the validation rule.

**Pre-query pattern:** Query existing records by relationship fields (not external ID), build a map of external ID → SF record ID, then PATCH by SF record ID. Stamp the external ID on existing records so future upserts work normally.

### AccountTrigger / ServiceLocator pattern

`ohfy.AccountTrigger` fires on AfterUpdate and calls `AccountTriggerMethods` via ServiceLocator. If the implementation class is missing in the subscriber org:
- **Inserts work** (first load succeeds)
- **Updates fail** (re-upserts on same data fail with ServiceLocatorException)
- Requires Ohanafy engineering to deploy the missing class

### Restricted picklists vary by org and record type

`ohfy__Market__c`, `ohfy__Packaging_Type__c`, and others are restricted picklists. Always describe the field via API before building crosswalks — values differ between orgs and record types. Generic human-friendly names (e.g., "Bar") fail if the org uses a different label (e.g., "Bars/Clubs/Taverns").

### Item prerequisite chain for Depletion__c

Depletion__c has a mandatory Item lookup filter requiring 5 prerequisites on the Item. See `knowledge-base/ohanafy/objects/depletion.md` for the full chain. This is the most common failure when loading depletions into a new org.

## Key Integration Principles

1. **Tray-first** — always check existing Tray workflows before building new
2. **External ID upserts** — use external IDs for idempotent Salesforce operations
3. **Validate → Transform → Batch → Output** — standard script flow
4. **2000-value chunking** — Salesforce SOQL IN clause limit
5. **Error envelope pattern** — structured success/error responses
6. **Watermark/delta sync** — use Tray Data Storage for tracking last sync point
7. **No credentials in code** — AWS Secrets Manager only
8. **Pre-query before upsert** — when managed validation rules enforce natural key uniqueness, query existing records first
9. **Load order matters** — reference data (Items, Locations) before enrichment before transactions; pre-queries must run after dependencies are stamped
