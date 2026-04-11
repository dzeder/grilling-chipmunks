# DISTDA — Distributor Master

## Overview

The Distributor Master file contains the reference data for all distributors in the supplier's network. Each record represents a single distributor with contact information, organizational hierarchy (division, area, market), certification status, and rep assignments. This is the foundational account file that all transactional records (sales, inventory, outlets) reference via DistID.

## File Naming

- **Pattern:** `DISTDA.N{MMDDYYYY}`
- **Suffixes:** DA (daily), WK (weekly), FX (fixed/full), NW (new)
- **Example:** `DISTDA.N04102026`

## Load Method

- **Method:** Add/Update
- **Key:** DISTID (Distributor ID)

## Field Layout (Detail Records)

| # | Field | Description | Req | Type |
|---|-------|-------------|-----|------|
| 1 | RecordType | Record type identifier | Y | A |
| 2 | SupplierID | Supplier identifier | Y | A |
| 3 | DistributorID | Distributor ID — **PRIMARY KEY** | Y | A |
| 4 | Name | Distributor name | Y | A |
| 5 | Street | Street address | N | A |
| 6 | City | City | N | A |
| 7 | State | State code | N | A |
| 8 | Zip | ZIP/postal code | N | A |
| 9 | Phone | Phone number | N | A |
| 10 | Contact1Name | Primary contact name | N | A |
| 11 | Contact1Email | Primary contact email | N | A |
| 12 | ParentDistID | Parent distributor ID (for roll-ups) | N | A |
| 13 | DistRepEmail | Distributor rep email | N | A |
| 14 | ISVName | ISV (Independent Software Vendor) name | N | A |
| 15 | Rank | Distributor rank/tier | N | A |
| 16 | CertificationStatus | VIP certification status | N | A |
| 17 | Phase | Implementation phase | N | A |
| 18 | LastAuditMonthEOM | Last audit month (end of month) | N | A |
| 19 | LastAuditUser | Last audit user | N | A |
| 20 | DivisionCode | Division code | N | A |
| 21 | DivisionDesc | Division description | N | A |
| 22 | AreaCode | Area code | N | A |
| 23 | AreaDesc | Area description | N | A |
| 24 | MarketCode | Market code | N | A |
| 25 | MarketDesc | Market description | N | A |
| 26 | RepCode | Rep code | N | A |
| 27 | RepDesc | Rep description | N | A |

## Cross-References

| File | Relationship |
|------|-------------|
| OUTDA | Outlet DistID references this file |
| SLSDA | Sales DistID references this file |
| INVDA | Inventory DistID references this file |
| CTLDA | Control DistID and ParentDistID reference this file |
| ITMDA | Item mapping DistID references this file |

## Notes

- DistributorID is the universal distributor key across all VIP SRS transactional files.
- ParentDistID enables hierarchical roll-ups (e.g., regional parent distributor aggregating child distributors).
- Division/Area/Market hierarchy provides the supplier's organizational view of their distributor network.
- CertificationStatus and Phase track the distributor's VIP SRS onboarding progress.
- File suffixes indicate delivery cadence: DA=daily, WK=weekly, FX=fixed/full extract, NW=new distributors only.
- ISVName identifies the distributor's ERP/DSD system vendor (relevant for data format expectations).
