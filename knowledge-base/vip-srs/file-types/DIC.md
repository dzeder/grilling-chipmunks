# DIC — Distributor Item Cross-Reference

## Overview

The Distributor Item Cross-Reference file maps distributor-specific item codes to the supplier's canonical item codes. DIC is functionally identical to ITMDA — it contains the same data structure and field layout, just with an older file naming convention. Some distributors or VIP configurations may deliver DIC instead of ITMDA.

## Integration Status

Not currently integrated as a separate file type. The ITMDA variant IS currently integrated (see ITMDA.md).

## File Naming

- **Pattern:** `DIC{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), WK (weekly), FX (fixed/full), NW (new)
- **Example:** `DICDA.N04102026`

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

## Cross-References

| File | Relationship |
|------|-------------|
| ITMDA | Same data — DIC is the older naming convention |
| ITM2DA | ITEM maps to supplier item master |
| DISTDA | DISTID maps to distributor master |

## Notes

- 17 fields per record — identical to ITMDA.
- If a supplier receives both DIC and ITMDA, they contain the same data. Use whichever is configured.
- The ITMDA variant is the preferred/modern naming convention. DIC is maintained for backward compatibility.
- All field descriptions, types, and notes from ITMDA.md apply identically to DIC.
