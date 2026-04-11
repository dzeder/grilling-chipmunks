# DEPL — Summary Depletions

## Overview

Monthly summary depletion data aggregated by distributor, supplier item, and month. DEPL provides the same core depletion information as SLSDA but pre-aggregated to the monthly grain with 39 fields including quantity, revenue, cost, and various statistical measures. This file is useful for trend analysis and reporting where daily detail is not needed.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Pattern:** `DEPL{suffix}.N{MMDDYYYY}`
- **Suffixes:** MN (monthly)
- **Example:** `DEPLMN.N04102026`

## Load Method

- **Method:** Drop/Load
- **Key:** DISTID + DPITEM + DPDATE (Distributor + Supplier Item + Period)

## Field Layout (Detail Records)

39 fields total. Key fields shown below:

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | N |
| 3 | DPITEM | Supplier Item Code | Y | 10 | A |
| 4 | DPDATE | Period (YYYYMM) | Y | 6 | N |
| 5 | DPQTYC | Quantity in Cases (signed) | Y | 12.2 | S |
| 6 | DPQTYB | Quantity in Bottles (signed) | N | 12.2 | S |
| 7 | DPREV | Revenue (signed) | N | 13.4 | S |
| 8 | DPCOST | Cost (signed) | N | 13.4 | S |
| 9 | DPACCTS | Number of Accounts Sold | N | 8 | N |
| 10 | DPDLVS | Number of Deliveries | N | 8 | N |
| 11 | DPWHSE | Warehouse Code | N | 10 | A |
| 12 | DPPARENT | Parent Distributor ID | N | 8 | A |
| 13-39 | ... | Additional statistical/summary fields | N | varies | varies |

## Cross-References

| File | Relationship |
|------|-------------|
| SLSDA | Daily detail version — DEPL is a monthly aggregation of SLSDA |
| CTLS | Depletions control file for balancing against DEPL |
| DISTDA | DISTID maps to distributor master |
| ITM2DA | DPITEM maps to supplier item master |

## Potential Ohanafy Mapping

Could map to a `Monthly_Depletion_Summary__c` custom object or be used as a validation source for aggregated `Depletion__c` records. Fields like DPACCTS (accounts sold) and DPDLVS (deliveries) provide metrics not available from raw SLSDA data.

## Notes

- 39 fields per record — significantly more fields than SLSLITE but at monthly grain.
- Provides BOTH case and bottle quantities (DPQTYC, DPQTYB) — no UOM conversion needed.
- DPACCTS (accounts sold) is a unique count metric not derivable from SLSDA without distinct aggregation.
- DPDATE is YYYYMM (6 digits) — monthly period, not daily.
- Revenue and cost fields enable margin analysis at the monthly summary level.
- DPWHSE enables warehouse-level monthly summaries for multi-warehouse distributors.
- Drop/Load method — entire file is replaced each delivery.
- Fields 13-39 include additional breakdowns (by transaction type, by package type, year-ago comparisons, etc.).
