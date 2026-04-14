# ohfy__Depletion__c

Distributor-to-retailer sales transaction records. Represents sell-through data from distribution, NOT supplier-to-distributor invoices (that's Invoice__c).

## Quick facts

- **Namespace:** ohfy__
- **Triggers:** DepletionTrigger (via DepletionTriggerService — before/after insert, update, delete)
- **Key relationships:** Lookup to Item__c (with mandatory filter), Lookup to Account

## Critical: Item lookup filter chain

`ohfy__Item__c` has a mandatory, non-optional lookup filter. The referenced Item must have ALL of the following:

1. **Finished Good record type** assigned
2. **`ohfy__Type__c = 'Finished Good'`** explicitly set
3. **`ohfy__UOM__c`** set (e.g., `US Count`)
4. **`ohfy__Packaging_Type__c`** set (dependent picklist on UOM, e.g., `Each`)
5. **`ohfy__Transformation_Setting__c`** record exists linking the Packaging_Type to a Volume UOM

Missing ANY prerequisite causes `FIELD_FILTER_VALIDATION_EXCEPTION`. This is the most common failure mode when loading depletions into a new org.

### Transformation_Setting__c setup

- One record needed per Packaging_Type → Volume UOM mapping
- Key field: `ohfy__Key__c` = `{PackagingType}-{VolumeUOM}` (e.g., `Each-Fluid Ounce(s)`)
- Must exist BEFORE any Depletion records can reference the Item
- These are not auto-created — they must be manually or programmatically seeded per org

### Prerequisite load order

```
1. Create Transformation_Setting__c (if missing)
2. Create/update Items with:
   - RecordTypeId = Finished Good RT
   - Type__c = 'Finished Good'
   - UOM__c = 'US Count' (or org-specific value)
   - Packaging_Type__c = 'Each' (or org-specific value)
3. THEN load Depletion records
```

## Key fields

| Field | Notes |
|-------|-------|
| `ohfy__Type__c` | Restricted picklist: Cold Box, Draft Line, Menu, Shelf. NOT transaction types — skip for VIP sales data. |
| `ohfy__Date__c` | Invoice/transaction date |
| `ohfy__Case_Quantity__c` | Case quantity (when UOM=C) |
| `VIP_Unit_Quantity__c` | Bottle quantity (when UOM=B) — custom unmanaged field |
| `VIP_Net_Price__c` | Per-unit net price — custom unmanaged field |
| `VIP_Net_Amount__c` | Extended net amount (Qty × NetPrice) — custom unmanaged field. **Use this for revenue reporting.** |
| `VIP_Invoice_Number__c` | Invoice number from VIP SLSDA |

> **Note:** `ohfy__Net_Amount__c` and `ohfy__Quantity__c` are documented in some knowledge sources but do NOT exist in the ROS2 sandbox as of 2026-04-14. Custom unmanaged fields (`VIP_*`) are used instead.

## Depletion vs Invoice

VIP/distribution data = distributor-to-retailer sales → **Depletion__c** (+ Placement__c for aggregation).
Supplier-to-distributor billing → **Invoice__c / Invoice_Item__c** — completely separate data source, not from VIP files.

## Discovered in

- VIP SRS Phase 5c (2026-04-10): Discovered 5-prerequisite filter chain during E2E testing. Undocumented in managed package.
- Item lookup filter is the #1 blocker when setting up a new customer org for depletion data.
