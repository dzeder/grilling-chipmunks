# ORD — Future Sales/Orders

## Overview

Pre-sold orders and open orders from distributors. The ORD file captures order-level detail including order mode (pre-sell, open, return, exchange), line items with pricing, warehouse assignment, and sales rep attribution. This file provides forward-looking demand signals that complement the historical sales data in SLSDA.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Pattern:** `ORD{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), MN (monthly)
- **Example:** `ORDDA.N04102026`

## Load Method

- **Method:** Drop/Load
- **Key:** DISTID + ORCODE + ORDLNSE (Distributor + Order Code + Line Sequence)

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | N |
| 3 | ORCODE | Order Code | Y | 25 | A |
| 4 | ORDLNSE | Line Sequence | Y | 5 | N |
| 5 | ORDDATE | Order Date (YYYYMMDD) | Y | 8 | N |
| 6 | ORDACCT | Account Code | Y | 8 | A |
| 7 | ORDITEM | Distributor Item Code | Y | 10 | A |
| 8 | ORDITEMID | Supplier Item Code | Y | 10 | A |
| 9 | ORDSALREPID | Sales Rep ID | N | 10 | A |
| 10 | ORDWHSE | Warehouse Code | N | 10 | A |
| 11 | ORDMODE | Order Mode | Y | 2 | A |
| 12 | ORDSYSTYPE | System Transaction Type | N | 2 | A |
| 13 | ORDTYPE | Invoice Transaction Type | N | 1 | A |
| 14 | ORDTRX | Invoice Number | N | 25 | A |
| 15 | ORDTXDT | Invoice Date (YYYYMMDD) | N | 8 | N |
| 16 | ORDAVAIL | Available Flag | N | 1 | A |
| 17 | ORDQTY | Quantity (signed) | Y | 7 | S |
| 18 | ORDQUOM | Unit of Measure (C=Case, B=Bottle) | Y | 1 | A |
| 19 | ORDPRICE | Distributor Price (signed) | N | 9.4 | S |
| 20 | ORDTSLS | Extended Net Price (signed) | N | 13.4 | S |
| 21 | ORDTEXP | Extended Deposit (signed) | N | 13.4 | S |
| 22 | ORDSLSTM | File Build Start Date (YYYYMMDD) | N | 8 | N |
| 23 | ORDSLSTMGE | File Build End Date (YYYYMMDD) | N | 8 | N |
| 24 | VARIANT | Extended Data | N | 800 | A |
| 25 | - | (Reserved) | N | - | - |

### Order Mode Values (ORDMODE)

| Code | Description |
|------|-------------|
| 00 | Pre-Sell |
| 01 | Open Order |
| 02 | Return |
| 03 | Exchange |

## Cross-References

| File | Relationship |
|------|-------------|
| DISTDA | DISTID maps to distributor master |
| OUTDA | ORDACCT maps to outlet account (ROACCT) |
| ITM2DA | ORDITEMID maps to supplier item master |
| SLM | ORDSALREPID maps to salesperson master |

## Potential Ohanafy Mapping

Could map to Ohanafy Order objects or a `VIP_Order__c` custom object. Pre-sell orders (ORDMODE=00) provide demand forecasting data. Open orders (ORDMODE=01) represent committed but unfulfilled demand. Returns and exchanges (02/03) could feed reverse logistics tracking.

## Notes

- 25 fields per record — same field count as SLSDA.
- ORDQTY, ORDPRICE, ORDTSLS, and ORDTEXP are signed — negatives indicate returns or credits.
- The VARIANT field (800 chars) contains extended data that varies by distributor system.
- ORDSLSTM/ORDSLSTMGE define the date range the file build covers, not individual order dates.
- Drop/Load method — the entire order file is replaced each delivery (represents current open orders).
- DA suffix = daily delivery, MN = monthly delivery.
