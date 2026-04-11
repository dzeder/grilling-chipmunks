# CTLS — Depletions Control (Summary)

## Overview

The Depletions Control file is the balancing counterpart to the DEPL (Summary Depletions) file. It provides summarized monthly totals by distributor, supplier item, and period to validate the integrity of depletion summary data. CTLS relates to DEPL the same way CTL/CTLDA relates to SLSDA.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Pattern:** `CTLS{suffix}.N{MMDDYYYY}`
- **Example:** `CTLSDA.N04102026`

## Load Method

- **Method:** Drop/Load
- **Balancing Key:** DISTID + CSITEM + CSDATE

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 5 | A |
| 3 | CSVPBRS | Reserved (blank) | N | 5 | A |
| 4 | CSDISTM | Distributor Name | N | 40 | A |
| 5 | CSITEM | Supplier Item Code | Y | 10 | A |
| 6 | CSQTY | Quantity (signed) | Y | 12.2 | S |
| 7 | CSUM | Unit of Measure (C=Case, B=Bottle) | Y | 1 | A |
| 8 | CSDATE | Period (YYYYMM) | Y | 6 | N |
| 9 | CSPARENT | Parent Distributor ID | N | 8 | A |
| 10 | CSDISTITEM | Distributor Item Code | N | 10 | A |

## Cross-References

| File | Relationship |
|------|-------------|
| DEPL | Primary balancing target — summarized DEPL data should match CTLS totals |
| DISTDA | DISTID maps to distributor master |
| ITM2DA | CSITEM maps to supplier item master |
| CTLDA | Similar structure but balances against SLSDA (daily detail sales) |

## Potential Ohanafy Mapping

Quality assurance only — not loaded to Salesforce as a standalone object. Used to validate DEPL data integrity before or after loading.

## Notes

- 10 fields per record — identical structure to CTLDA.
- CSQTY uses 12.2 format (12 digits with 2 decimal places).
- **Balancing process**: Aggregate all DEPL records by DISTID + DPITEM + DPDATE, then compare totals against the corresponding CTLS record. Mismatches indicate data gaps.
- CSVPBRS is always blank — reserved for future use.
- Drop/Load method — entire file replaced each delivery.
- CSDATE is YYYYMM (6 digits) — monthly period.
