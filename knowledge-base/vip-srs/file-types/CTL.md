# CTL — Sales Control

## Overview

A sales balancing file used to validate the integrity of SLS (Sales) data. CTL provides summarized totals by distributor, supplier item, and period that should match the aggregated totals from the corresponding SLS file. Like CTLS for depletions, this file serves as a quality assurance checkpoint in the data pipeline. This is the same file type as CTLDA, which is currently used in the integration for `Allocation__c` records.

## Integration Status

Not currently integrated as a separate file type. The CTLDA variant IS currently used in the Ohanafy integration for `Allocation__c` records (see CTLDA.md).

## File Naming

- **Pattern:** `CTL{suffix}.N{MMDDYYYY}`
- **Example:** `CTLDA.N04102026`

## Load Method

- **Method:** Drop/Load
- **Balancing Key:** DISTID + CITITEM + CTDATE

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 5 | A |
| 3 | VPBRS | Reserved (blank) | N | 5 | A |
| 4 | DISTM | Distributor Name | N | 40 | A |
| 5 | CITITEM | Supplier Item Code | Y | 10 | A |
| 6 | CTQTY | Quantity (signed) | Y | 10.5 | S |
| 7 | CTUM | Unit of Measure (C=Case, B=Bottle) | Y | 1 | S |
| 8 | CTDATE | Period (YYYYMM) | Y | 6 | N |
| 9 | CTPARENT | Parent Distributor ID | N | 8 | A |
| 10 | CTDISTITEM | Distributor Item Code | N | 10 | A |

## Cross-References

| File | Relationship |
|------|-------------|
| SLSDA | Primary balancing target — aggregated SLSDA should match CTL totals |
| CTLDA | Same file type, currently integrated for Allocation__c |
| DISTDA | DISTID maps to distributor master |
| ITM2DA | CITITEM maps to supplier item master |

## Potential Ohanafy Mapping

Quality assurance and validation only — CTLDA variant is already integrated and maps to `Allocation__c`. The CTL spec documented here covers the formal field definitions that also apply to CTLDA.

## Notes

- 10 fields per record — identical to CTLDA.
- CTQTY uses 10.5 format (10 digits with 5 decimal places) for fractional case quantities.
- CTQTY is signed — negative values possible for net-return periods.
- VPBRS is always blank — reserved for future use.
- **Balancing process**: Aggregate all SLSDA records by DISTID + BSITEMID + month(BSDATE), then compare totals against the corresponding CTL record. Mismatches indicate missing or duplicate sales data.
