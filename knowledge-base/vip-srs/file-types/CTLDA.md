# CTLDA — Sales Control (Allocations)

## Overview

The Sales Control file provides monthly summarized totals by distributor, supplier item, and period that serve as a balancing checkpoint against the detail sales data in SLSDA. In the Ohanafy integration, CTLDA records are used to create `Allocation__c` records representing monthly quantity commitments or allocations.

## Integration Status

**Integrated** — Script: `08-ctlda-allocations.js`

## File Naming

- **Pattern:** `CTL{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), MN (monthly)
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

## Ohanafy Mapping

Maps to `Allocation__c`:

| VIP Field | Salesforce Field | Notes |
|-----------|-----------------|-------|
| DISTID + CITITEM + CTDATE | Allocation__c.VIP_External_ID__c | ALC:{DISTID}:{CITITEM}:{CTDATE} |
| DISTID | Allocation__c.Account__c | Lookup to distributor account |
| CITITEM | Allocation__c.Product__c | Lookup to Product2 |
| CTQTY | Allocation__c.Quantity__c | Monthly total (signed) |
| CTUM | Allocation__c.Unit_of_Measure__c | C or B |
| CTDATE | Allocation__c.Allocation_Date__c | Period as first of month |

## Cross-References

| File | Relationship |
|------|-------------|
| SLSDA | Primary balancing target — aggregated SLSDA by dist+item+month should match CTLDA |
| DISTDA | DISTID maps to distributor master |
| ITM2DA | CITITEM maps to supplier item master |
| CTLS | Similar file for depletion control (summary depletions balancing) |

## Notes

- 10 fields per record.
- CTQTY uses 10.5 format (10 digits with 5 decimal places) for fractional case quantities.
- CTQTY is signed — negative values are possible for net-return periods.
- CTDATE is YYYYMM (6 digits) — period-level, not daily. Convert to first-of-month date for Salesforce.
- VPBRS field is always blank — reserved for future use.
- **Balancing process**: Aggregate all SLSDA records by DISTID + BSITEMID + month(BSDATE), then compare totals against the corresponding CTLDA record. Mismatches indicate missing or duplicate sales data.
- Drop/Load means the entire control file is replaced each delivery — no incremental updates.
- CTPARENT enables parent-level roll-ups for multi-house distributor networks.
