# SLSLITE — Sales Lite

## Overview

A simplified version of the SLSDA sales file with only 9 fields per record. SLSLITE provides the core depletion data (distributor, item, date, quantity) without the full pricing, warehouse, and rep detail of SLSDA. Designed for suppliers who need basic depletion tracking without the overhead of processing the full 25-field SLSDA file.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Pattern:** `SLSLITE.N{MMDDYYYY}`
- **Example:** `SLSLITE.N04102026`

## Load Method

- **Method:** Append
- **Key:** No natural key — each record is a unique transaction line

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | N |
| 3 | BSACCT | Account Number | Y | 8 | A |
| 4 | BSITEMID | Supplier Item Code | Y | 10 | A |
| 5 | BSDATE | Invoice Date (YYYYMMDD) | Y | 8 | N |
| 6 | BSQTY | Quantity (signed) | Y | 7 | S |
| 7 | BSUOM | Unit of Measure (C=Case, B=Bottle) | Y | 1 | A |
| 8 | BSPARENT | Parent Distributor ID | N | 8 | A |
| 9 | BSDISTITEM | Distributor Item Code | N | 10 | A |

## Cross-References

| File | Relationship |
|------|-------------|
| SLSDA | Full version of this data with 25 fields |
| OUTDA | BSACCT maps to outlet account (ROACCT) |
| ITM2DA | BSITEMID maps to supplier item master |
| DISTDA | DISTID maps to distributor master |

## Potential Ohanafy Mapping

Could map to the same `Depletion__c` object as SLSDA, but with fewer populated fields. Useful for:
- Lightweight depletion tracking for smaller suppliers
- Quick-start integrations before full SLSDA processing is configured
- Backup/validation against full SLSDA data

## Notes

- 9 fields per record — a subset of SLSDA's 25 fields.
- Missing from SLSDA: BSTRTYPE (transaction type), BSPRICE, BSTSLS, BSTEXP, BSWHSE, BSSALREP, BSINV, BSRTE, BSPO, BSDLVDT, BSSLSTM/BSSLSTMGE, VARIANT.
- Without BSTRTYPE, all records are assumed to be standard depletions (type D). Returns/credits may still have negative BSQTY.
- Without BSWHSE, warehouse attribution is not possible from this file alone.
- Grain is one record per distributor + item + date (daily summary), not per invoice line like SLSDA.
- A supplier typically receives either SLSLITE or SLSDA, not both. Check with VIP for which file is configured.
