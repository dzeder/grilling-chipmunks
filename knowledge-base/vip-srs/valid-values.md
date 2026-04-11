# VIP SRS — Complete Valid Field Values Reference

All coded field values from ISV Spec v6.0 Appendix B. These values decode fields across all VIP file types.

The SRSVALUE file (VAL) delivers these as data rows. This document serves as a static reference.

---

## Class of Trade (OUTCLS / ROCOD)

Used in: OUTDA.ClassOfTrade, VIPOUT.VPCOT

### Off Premise (01-19)

| Code | Description |
|------|-------------|
| 01 | Convenience/Gas |
| 02 | Drug Store |
| 03 | Liquor/Package Store |
| 04 | Military Off-Premise |
| 05 | Small Grocery Store |
| 06 | Non-Retail |
| 07 | Sub-Distributor |
| 08 | Mass Merch/Supercenter |
| 09 | Supermarket |
| 10 | Wholesale Club |
| 11 | Fine Wine Store |
| 12 | State Liquor Store |
| 13 | General Merchandise |
| 14 | Retail-Specialty Services |
| 15 | E-Commerce |
| 16 | Dollar Store |
| 17 | CBD/THC Recreational |
| 18 | CBD/THC Medicinal |
| 19 | Other Off Premise |

### On Premise (21-43)

| Code | Description |
|------|-------------|
| 21 | Adult Entertainment |
| 22 | Transportation |
| 23 | Bar/Tavern |
| 24 | Recreation/Entertainment |
| 25 | Casino/Gaming |
| 26 | Concessionaire |
| 27 | Golf/Country Club |
| 28 | Hotel/Motel |
| 29 | Military On-Premise |
| 30 | Music/Dance Club |
| 31 | Private Club |
| 32 | Restaurant |
| 33 | Special Event/Temp License |
| 34 | Sports Bar |
| 35 | Casual Theme Restaurant |
| 36 | Fine Dining/White Tablecloth |
| 37 | School |
| 38 | Factory/Office |
| 39 | Other On Premise |
| 40 | Health/Hospital |
| 41 | Government/Non-Military |
| 42 | Irish Pub |
| 43 | Tasting Room |

### Other

| Code | Description |
|------|-------------|
| 50 | Direct Distributors |
| 99 | Unassigned |

---

## Patron Occupation (ROOCC)

Used in: OUTDA.Occupation

| Code | Description |
|------|-------------|
| 10 | White Collar |
| 20 | Blue Collar |
| 40 | College |
| 50 | Military |
| 60 | Other |

---

## Patron Age (ROPAGE)

Used in: OUTDA.PatronAge

| Code | Description |
|------|-------------|
| 01 | Young Adult (21-28) |
| 02 | General Population |

---

## Package Type (ROPTYPE)

Used in: OUTDA.PackageType

| Code | Description |
|------|-------------|
| 1 | Draft only |
| 2 | Draft and package |
| 3 | Package only |

---

## Sell Type (ROSELL)

Used in: OUTDA.Sell

| Code | Description |
|------|-------------|
| 1 | Driver Sell |
| 2 | Pre Sell |
| 3 | Tel Sell |
| 4 | House Account (no assigned SM) |
| 6 | Web Sell |
| 7 | EDI Order |

---

## Outlet Status (ROSTS)

Used in: OUTDA.Status

| Code | Description |
|------|-------------|
| A | Active |
| I | Inactive |
| O | Out of business |

---

## Chain Status (ROCSTS)

Used in: OUTDA.ChainStatus

| Code | Description |
|------|-------------|
| C | Chain |
| I | Independent |

---

## Container Type (ITCTYP)

Used in: ITM2DA.ContainerType

| Code | Description |
|------|-------------|
| S | Spirits |
| W | Wine |
| P | Beer Package |
| D | Beer Draft |
| F | FMB (Flavored Malt Beverage) |
| H | Seltzer |
| N | Non-Alcoholic |

---

## Retail Sales Unit of Measure (RSUOM)

Used in: SLSDA.UOM, SLSLITE.UOM

| Code | Description |
|------|-------------|
| C | Case (full case sale — cases or kegs) |
| B | Bottle (partial case sale) |

---

## Inventory Unit of Measure (INUOM)

Used in: INVDA.UnitOfMeasure

| Code | Description |
|------|-------------|
| C | Case |
| B | Bottle |

---

## License Type (ROLICTYPE)

Used in: OUTDA.LicenseType

| Code | Description |
|------|-------------|
| A | Full License |
| B | Malt Only |
| C | Malt/Low Alcohol Only |
| D | Malt/High Alcohol Only |
| E | Malt & Wine |
| F | Malt/High Alcohol & Wine |
| G | Malt 3.2 & Wine Only |
| H | Malt & Wine & Spirits |
| I | Malt 3.2 & Wine & Spirits |
| J | Wine Only |
| K | Wine & Spirits Only |
| L | Spirits Only |
| Z | No License |

---

## Sales Transaction Type (BSTRTYPE)

Used in: SLSDA (via ISV spec field RSTRTYPE)

| Code | Description |
|------|-------------|
| B | Warehouse Breakage |
| C | Credit Memo |
| D | Debit Memo |
| E | Revenue Adjustment — Current Month |
| R | Retail Sales (default) |
| S | Supplier Samples |
| T | Warehouse Distributor Transfer |
| V | Revenue Adjustment — Prior Month |

---

## Detailed Inventory Transaction Codes (INTRANS)

Used in: INVDA.TransCode

### Inventory Position

| Code | Description | Target |
|------|-------------|--------|
| 10 | Ending Inventory | Inventory__c + Inventory_History__c |
| 11 | Committed Inventory | Inventory_History__c only |
| 12 | Saleable Inventory | Inventory_History__c only |

### Detail Transactions

| Code | Description | Direction | Target |
|------|-------------|-----------|--------|
| 20 | Receipts | Addition | Inventory_Adjustment__c |
| 21 | Transfer in from wholesaler | Addition | Inventory_Adjustment__c |
| 22 | Transfer out to wholesaler | Subtraction | Inventory_Adjustment__c |
| 30 | Supplier returns | Subtraction | Inventory_Adjustment__c |
| 40 | Breakage | Subtraction | Inventory_Adjustment__c |
| 41 | Samples | Subtraction | Inventory_Adjustment__c |
| 99 | Miscellaneous adjustments | Addition | Inventory_Adjustment__c |

### Summary (Month-to-Date) Transactions

| Code | Description | Direction | Note |
|------|-------------|-----------|------|
| 50 | MTD Receipts | Addition | Overlaps code 20 — skip if detail exists |
| 51 | MTD Transfers In | Addition | Overlaps code 21 |
| 52 | MTD Transfers Out | Subtraction | Overlaps code 22 |
| 53 | MTD Supplier Returns | Subtraction | Overlaps code 30 |
| 54 | MTD Breakage | Subtraction | Overlaps code 40 |
| 55 | MTD Samples | Subtraction | Overlaps code 41 |
| 59 | MTD Adjustments | Addition | Aggregate — no daily equivalent |

### Special Codes

| Code | Description | Note |
|------|-------------|------|
| 70 | On Order | Future state — not current inventory |
| 80 | In Bond | Future state — not available for sale |

### Not Covered by Transaction Codes

The following inventory movements are NOT represented by transaction codes:
- Sales (captured in daily sales file collection)
- Inventory on-hold (included in on-hand)
- Inventory release
- Dump (use breakage)
- Repack from (use adjustment or breakage)
- Repack to (use adjustment or breakage)

---

## Display Indicator (ROCSP)

Used in: OUTDA.Displays

| Code | Description |
|------|-------------|
| Y | Allows display placements |
| N | Does not allow display placements |

---

## Fine Wine Program (ROFWIN)

Used in: OUTDA.FineWine

| Code | Description |
|------|-------------|
| Y | Has fine wine program |
| N | Does not have fine wine program |

---

## Premise Type (VPPREM)

Used in: VIPOUT.VPPREM

| Code | Description |
|------|-------------|
| P | On Premise |
| O | Off Premise |

---

## VIP Outlet Store Status (VPSTATUS)

Used in: VIPOUT.VPSTATUS

| Code | Description |
|------|-------------|
| A | Active |
| I | Inactive |
| C | Closed |

---

## Beverage Indicators

Used in: VIPOUT.VPMALT, VIPOUT.VPWINE, VIPOUT.VPSHRITS, OUTDA.vpMalt

| Code | Description |
|------|-------------|
| Y | Yes — carries this beverage type |
| N | No — does not carry this beverage type |

---

## Repack Flag (DVRPACK)

Used in: DIC.DVRPACK, SLSDA.Repack, INVDA.Repack

| Code | Description |
|------|-------------|
| A | Active (standard, no repack) |
| Y | Repacked |
| N | Not repacked |
| C | Case Multiple |
| D | Repacked by distributor |
| M | Case Multiply |

---

## Order Mode (ORDCODE)

Used in: ORD.ORDCODE

| Code | Description |
|------|-------------|
| 00 | Pre-Sell (default) |
| 01 | Open |
| 02 | Return |
| 03 | Exchange |

---

## Calendar Record Type (SCTYPE)

Used in: CAL.SCTYPE

| Code | Description |
|------|-------------|
| DOW | Day of Week (standard schedule) |
| EXC | Exception — Closed |
| OPN | Exception — Open |

---

## Non-Reporter File Type (INTYPE)

Used in: NONA.INTYPE

| Code | Description |
|------|-------------|
| SLS | Missing sales data |
| INV | Missing inventory data |

---

## Distributor Item Status (INACT)

Used in: DIC.INACT

| Code | Description |
|------|-------------|
| Y | Active |
| N | Not active |
