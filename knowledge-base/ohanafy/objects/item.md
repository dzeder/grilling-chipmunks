# ohfy__Item__c

Product master record. Represents individual SKUs (items) in the Ohanafy catalog with full product attributes, pricing, and classification data.

## Quick facts

- **Namespace:** ohfy__
- **Field count:** 135+ — never use `SELECT *` in SOQL queries
- **Triggers:** 9 trigger actions (TA_Item_* classes)
- **Parent lookups:** Item_Line__c, Item_Type__c

## Record type gating

`ohfy__Packaging_Type__c` is a dependent picklist that accepts different values per record type. This has critical integration implications:

- **Integration user must have "Finished Good" record type assigned** on their profile
- **Composite API body must include `RecordTypeId`** — without it, the default Master record type is used, which rejects valid Finished Good picklist values
- Record type can be looked up dynamically: `SELECT Id FROM RecordType WHERE SObjectType = 'ohfy__Item__c' AND DeveloperName = 'Finished_Good'`

## Load order

Items depend on parent records being loaded first:

```
1. Item_Line__c (product line/brand) — no upsert key, creates only
2. Item_Type__c (product type/category)
3. Item__c (references Item_Line__r and Item_Type__r)
```

### Item_Line__c has no upsert key

`ohfy__Item_Line__c` records are created via `sf data create record` — there is no external ID field for upsert. **Re-runs create duplicates.** For production pipelines, add a pre-check query or dedup step.

## Restricted picklists

These fields require exact org values — always `sf sobject describe` before building crosswalks:

| Field | Example values | Notes |
|-------|---------------|-------|
| `ohfy__Packaging_Type__c` | `Each`, `Case`, `Keg` | Dependent on UOM__c, gated by record type |
| `ohfy__UOM__c` | `US Count` | Controls which Packaging_Type values are available |
| `ohfy__Type__c` | `Finished Good` | Required for Depletion__c Item lookup filter |

## External ID patterns

External ID field names vary by integration:
- VIP SRS: `ohfy__VIP_External_ID__c` (managed, on Item__c)
- Other integrations may use different fields — check per-object metadata

## Discovered in

- VIP SRS Phase 1 (2026-04-09): Packaging_Type dependent picklist discovered during E2E
- VIP SRS Phase 5c (2026-04-10): Finished Good RT + 5 prerequisites required for Depletion Item filter
