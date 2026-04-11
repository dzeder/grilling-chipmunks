# INVDA — Inventory

## Overview

The Inventory file contains distributor-reported inventory transactions and positions. Each record represents a single inventory event — receipt, adjustment, transfer, or position snapshot — at a specific warehouse for a specific item on a specific date. Inventory data can be delivered as daily detail transactions or monthly summaries (see appendices/summary-inventory.md).

## Integration Status

**Integrated** — Script: `06-invda-inventory.js`

## File Naming

- **Pattern:** `INV{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), WK (weekly), MN (monthly), FX (fixed/full)
- **Example:** `INVDA.N04102026`

## Load Method

- **Method:** Append (daily detail) or Drop/Load (monthly summary)
- **Key:** DISTID + INITEM + INDATE + INTRANS + INUOM (composite)

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | N |
| 3 | INITEM | Distributor Item Code | Y | 10 | A |
| 4 | INITEMID | Supplier Item Code | Y | 10 | A |
| 5 | INDATE | Transaction Date (YYYYMMDD) | Y | 8 | N |
| 6 | INTRANS | Transaction Code | Y | 3 | A |
| 7 | INQUAN | Quantity (signed) | Y | 12.2 | S |
| 8 | INUOM | Unit of Measure (C=Case, B=Bottle) | Y | 1 | A |
| 9 | INWHSE | Warehouse Code | N | 10 | A |
| 10 | INCOST | Unit Cost | N | 9.4 | S |
| 11 | INEXTCST | Extended Cost | N | 13.4 | S |
| 12 | INPO | PO Number | N | 25 | A |
| 13 | INDLVDT | Delivery Date (YYYYMMDD) | N | 8 | N |
| 14 | INSLSTM | File Build Start Date (YYYYMMDD) | N | 8 | N |
| 15 | INSLSTMGE | File Build End Date (YYYYMMDD) | N | 8 | N |
| 16 | INPARENT | Parent Distributor ID | N | 8 | A |
| 17 | INDISTITEM | Distributor Item Code (alt) | N | 10 | A |
| 18 | VARIANT | Extended Data | N | 800 | A |
| 19 | - | (Reserved) | N | - | - |

### INTRANS — Inventory Transaction Codes

#### Detail Transaction Codes (Daily)

| Code | Description | Direction | Target |
|------|-------------|-----------|--------|
| REC | Receipt from supplier | + | On-hand |
| ADJ | Adjustment (physical count) | +/- | On-hand |
| TRI | Transfer In (from another warehouse) | + | On-hand |
| TRO | Transfer Out (to another warehouse) | - | On-hand |
| RTN | Return to supplier | - | On-hand |
| BRK | Breakage/Damage | - | On-hand |
| SAM | Sample/Tasting | - | On-hand |
| OTH | Other | +/- | On-hand |

#### Summary/Position Codes (Monthly)

| Code | Description | Direction | Target |
|------|-------------|-----------|--------|
| BOH | Beginning On-Hand | Position | Snapshot |
| EOH | Ending On-Hand | Position | Snapshot |
| TRC | Total Receipts | + | Period summary |
| TDP | Total Depletions | - | Period summary |
| TAD | Total Adjustments | +/- | Period summary |
| TTR | Total Transfers | +/- | Period summary |
| TRT | Total Returns | - | Period summary |

## Ohanafy Mapping

Maps to `Inventory__c` (transactions) and `Inventory_Holding__c` (positions):

| VIP Field | Salesforce Field | Notes |
|-----------|-----------------|-------|
| DISTID + INITEMID + INDATE + INTRANS | Inventory__c.VIP_External_ID__c | IVT:{DISTID}:{INITEMID}:{INDATE}:{INTRANS} |
| INDATE | Inventory__c.Transaction_Date__c | |
| INTRANS | Inventory__c.Transaction_Type__c | Decode via table above |
| INQUAN | Inventory__c.Quantity__c | Signed |
| INUOM | Inventory__c.Unit_of_Measure__c | C or B |
| INWHSE | Inventory__c.Warehouse__c | |

## Cross-References

| File | Relationship |
|------|-------------|
| ITM2DA | INITEMID maps to supplier item master |
| ITMDA | INITEM + DISTID maps to distributor item cross-ref |
| DISTDA | DISTID maps to distributor master |
| CTLDA | Control file for inventory balancing |
| SLSDA | Depletions should reconcile with TDP inventory movements |

## Notes

- 19 fields per record.
- **Daily vs Monthly**: Daily files contain individual transactions (REC, ADJ, TRI, etc.). Monthly files contain summary positions (BOH, EOH, TRC, TDP). Check INTRANS code to determine which type.
- **Position vs Movement**: BOH/EOH are position snapshots (point-in-time quantities). All other codes are movements (quantity changes).
- INQUAN is signed — negative values represent reductions (depletions, breakage, returns).
- INWHSE is critical for multi-warehouse distributors — inventory must be tracked per warehouse.
- **Repack items**: If item has repack conversion, quantities may need case/bottle conversion (see appendices/repack-logic.md).
- Monthly summary relationship: BOH + TRC - TDP +/- TAD +/- TTR - TRT = EOH (should balance).
- The VARIANT field may contain lot numbers, expiration dates, or other warehouse-specific data.
