# ITMDA — Distributor Item Cross-Reference

## Overview

The Distributor Item Cross-Reference maps distributor-specific item codes to the supplier's canonical item codes (from ITM2DA). Each record represents a single distributor's mapping for a specific supplier item, including the distributor's own item code, description, status, and UOM. This is the bridge table that allows transactional files (SLSDA, INVDA) to be joined back to the supplier item master.

## Integration Status

**Integrated** — Script: `04-itmda-enrichment.js`

## File Naming

- **Pattern:** `ITMDA.N{MMDDYYYY}` or `ITM{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), WK (weekly), FX (fixed/full), NW (new)
- **Example:** `ITMDA.N04102026`

## Load Method

- **Method:** Add/Update
- **Key:** DISTID + ITEM (Distributor ID + Supplier Item Code)

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | A |
| 3 | ITEM | Supplier Item Code | Y | 10 | A |
| 4 | DISTITEM | Distributor Item Code | Y | 10 | A |
| 5 | DISTDESC | Distributor Item Description | N | 60 | A |
| 6 | STATUS | Item Status (A=Active, I=Inactive, D=Deleted) | N | 1 | A |
| 7 | UOM | Unit of Measure (C=Case, B=Bottle) | N | 1 | A |
| 8 | DISTPACK | Distributor Pack Size | N | 4 | N |
| 9 | DISTSIZE | Distributor Size | N | 8 | A |
| 10 | DISTPRICE | Distributor Price | N | 9 | S |
| 11 | DISTCOST | Distributor Cost | N | 9 | S |
| 12 | DISTWHSE | Warehouse Code | N | 10 | A |
| 13 | DISTBRAND | Distributor Brand Code | N | 10 | A |
| 14 | DISTCAT | Distributor Category | N | 10 | A |
| 15 | DISTSUBCAT | Distributor Sub-Category | N | 10 | A |
| 16 | DISTPARENT | Parent Distributor ID | N | 8 | A |
| 17 | VARIANT | Extended Data | N | 800 | A |

## Ohanafy Mapping

Maps to Product2 enrichment — adds distributor-specific attributes to the supplier's base product:

| VIP Field | Salesforce Field | Notes |
|-----------|-----------------|-------|
| DISTID | (join to Account) | Distributor account lookup |
| ITEM | Product2.VIP_Item_Code__c | Join to supplier item master |
| DISTITEM | Distributor_Item_Code__c | Distributor's own code |
| DISTDESC | Distributor_Item_Description__c | May differ from supplier desc |
| STATUS | IsActive (derived) | A→true, I/D→false |

## Cross-References

| File | Relationship |
|------|-------------|
| ITM2DA | ITEM maps to supplier item master (Supplier Item Code) |
| DISTDA | DISTID maps to distributor master |
| SLSDA | DISTITEM + DISTID used in sales transactions |
| INVDA | DISTITEM + DISTID used in inventory transactions |
| DIC | Same data structure (DIC is the older file name) |

## Notes

- 17 fields per record.
- ITEM (supplier item code) is the join key back to ITM2DA. DISTITEM is the distributor's own item code.
- STATUS codes: A=Active, I=Inactive, D=Deleted. Only Active items typically appear in current transactions.
- DISTWHSE identifies which warehouse at the distributor carries this item — important for multi-warehouse distributors.
- The VARIANT field (800 chars) contains extended distributor-specific data. Format varies by distributor system.
- DIC file contains identical data with an older naming convention.
- Price and cost fields (DISTPRICE, DISTCOST) are signed — negatives are possible for credit items.
