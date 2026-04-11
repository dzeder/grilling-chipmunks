# SLSDA — Sales (Depletions)

## Overview

The Sales file contains distributor-reported sales transactions — the core depletion data. Each record represents a single invoice line item with quantity, pricing, date, account, item, warehouse, and transaction type. This is the highest-volume VIP file and the primary source for `Depletion__c` and `Placement__c` records in Ohanafy.

## Integration Status

**Integrated** — Script: `07-slsda-depletions.js`

## File Naming

- **Pattern:** `SLS{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), WK (weekly), MN (monthly)
- **Example:** `SLSDA.N04102026`

## Load Method

- **Method:** Append
- **Key:** No natural key — each record is a unique transaction line

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | N |
| 3 | BSACCT | Account Number | Y | 8 | A |
| 4 | BSITEM | Distributor Item Code | Y | 10 | A |
| 5 | BSITEMID | Supplier Item Code | Y | 10 | A |
| 6 | BSDATE | Invoice Date (YYYYMMDD) | Y | 8 | N |
| 7 | BSTRTYPE | Transaction Type | Y | 1 | A |
| 8 | BSSYSTYPE | System Transaction Type | N | 2 | A |
| 9 | BSINV | Invoice Number | N | 25 | A |
| 10 | BSQTY | Quantity (signed) | Y | 7 | S |
| 11 | BSUOM | Unit of Measure (C=Case, B=Bottle) | Y | 1 | A |
| 12 | BSPRICE | Unit Price (signed) | N | 9.4 | S |
| 13 | BSTSLS | Extended Net Sales (signed) | N | 13.4 | S |
| 14 | BSTEXP | Extended Deposit (signed) | N | 13.4 | S |
| 15 | BSWHSE | Warehouse Code | N | 10 | A |
| 16 | BSSALREP | Sales Rep Code | N | 10 | A |
| 17 | BSPARENT | Parent Distributor ID | N | 8 | A |
| 18 | BSDISTITEM | Distributor Item Code (alt) | N | 10 | A |
| 19 | BSSLSTM | File Build Start Date (YYYYMMDD) | N | 8 | N |
| 20 | BSSLSTMGE | File Build End Date (YYYYMMDD) | N | 8 | N |
| 21 | BSRTE | Route Code | N | 10 | A |
| 22 | BSPO | PO Number | N | 25 | A |
| 23 | BSDLVDT | Delivery Date (YYYYMMDD) | N | 8 | N |
| 24 | VARIANT | Extended Data | N | 800 | A |
| 25 | - | (Reserved) | N | - | - |

### BSTRTYPE — Sales Transaction Type Codes

| Code | Description | Direction |
|------|-------------|-----------|
| B | Breakage/Damage | Negative (return) |
| C | Credit/Return | Negative (return) |
| D | Delivery (retail sale) | Positive |
| E | Exchange/Swap | Varies |
| R | Return to Stock | Negative |
| S | Sample/Tasting | Positive (no revenue) |
| T | Transfer (warehouse-to-warehouse) | Neutral |
| V | Void/Reversal | Negative |

## Ohanafy Mapping

Maps to `Depletion__c` and `Placement__c`:

| VIP Field | Salesforce Field | Notes |
|-----------|-----------------|-------|
| DISTID + BSACCT + BSITEMID + BSDATE | Depletion__c.VIP_External_ID__c | DEP:{DISTID}:{BSACCT}:{BSITEMID}:{BSDATE} |
| BSDATE | Depletion__c.Depletion_Date__c | |
| BSQTY | Depletion__c.Quantity__c | Signed — negative for returns |
| BSUOM | Depletion__c.Unit_of_Measure__c | C or B |
| BSTRTYPE | Depletion__c.Transaction_Type__c | Decode via valid values |
| BSTSLS | Depletion__c.Net_Sales__c | Extended net |
| BSWHSE | Depletion__c.Warehouse__c | For multi-warehouse attribution |
| BSACCT | Placement__c (derived) | First sale = placement detection |

## Cross-References

| File | Relationship |
|------|-------------|
| OUTDA | BSACCT maps to outlet account (ROACCT) |
| ITM2DA | BSITEMID maps to supplier item master |
| ITMDA | BSITEM + DISTID maps to distributor item cross-ref |
| DISTDA | DISTID maps to distributor master |
| CTLDA | Balancing file — totals should match aggregated SLSDA |
| SLM | BSSALREP maps to salesperson master |
| DEPL | Monthly summary version of this daily detail data |

## Notes

- 25 fields per record. Highest volume file — can be millions of records per month.
- BSTRTYPE is the most important field for depletion logic:
  - D (Delivery) = standard retail depletion — the vast majority of records
  - C (Credit/Return) = negative quantity, reduces depletion totals
  - S (Sample) = product given away, positive quantity but no revenue
  - T (Transfer) = warehouse movement, not a true depletion
- BSQTY is signed — negative values represent returns/credits regardless of BSTRTYPE.
- BSUOM determines whether BSQTY is in cases (C) or bottles (B). Use ITM2DA.UNITS to convert.
- BSWHSE enables depletion warehouse attribution for multi-warehouse distributors (see appendices/depletion-warehouse.md).
- BSSLSTM/BSSLSTMGE define the date range the file build covers, not individual transaction dates.
- Load method is Append — never drop/reload sales data. Duplicates must be handled by external ID matching.
