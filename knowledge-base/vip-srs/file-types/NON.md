# NON — Non-Reporters

## Overview

Missing data tracking file that identifies distributors who failed to report data for specific dates. The NON file includes distributor rank and average daily sales to help prioritize follow-up — a missed day from a high-volume distributor has more impact on data completeness. An enhanced variant (NONA) adds file type and territory information.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Standard:** `NON{suffix}.N{MMDDYYYY}`
- **Enhanced:** `NONA{suffix}.N{MMDDYYYY}`
- **Example:** `NONDA.N04102026`, `NONADA.N04102026`

## Load Method

- **Method:** Drop/Load
- **Key:** DISTID + NODT (Distributor ID + Missing Date)

## Field Layout — NON (Standard, 4 fields)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | DISTID | Distributor ID | Y | 8 | A |
| 2 | DISTNM | Distributor Name | Y | 30 | A |
| 3 | NODT | Missing Date (YYYYMMDD) | Y | 8 | A |
| 4 | INRANK | Rank / Average Daily Sales | N | 13 | A |

## Field Layout — NONA (Enhanced, 6 fields)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | DISTID | Distributor ID | Y | 8 | A |
| 2 | DISTNM | Distributor Name | Y | 30 | A |
| 3 | NODT | Missing Date (YYYYMMDD) | Y | 8 | A |
| 4 | INTYPE | File Type (SLS or INV) | Y | 3 | A |
| 5 | INTERR | Territory Number | N | 2 | N |
| 6 | INTERRDESC | Territory Description | N | 30 | A |

## Cross-References

| File | Relationship |
|------|-------------|
| DISTDA | DISTID maps to distributor master |

## Potential Ohanafy Mapping

Could feed a `Data_Quality__c` or `Integration_Alert__c` custom object for monitoring data completeness. The rank field enables automated prioritization. NONA territory fields could trigger territory-specific alerts.

## Notes

- NON has 4 fields; NONA has 6 fields.
- INRANK is alphanumeric (13 chars) — may contain formatted rank or average daily sales figures. Parse carefully.
- NONA's INTYPE distinguishes Sales (SLS) vs Inventory (INV) missing data — helps target follow-up.
- NONA territory fields (INTERR/INTERRDESC) enable geographic routing of follow-up actions.
- High-rank distributor non-reporting = high-priority data quality issue.
- Drop/Load method — represents current non-reporting status, replaced each delivery.
