# VIP SRS File Type Index

> Quick-reference for all 22 VIP SRS file types

| Prefix | Name | Columns | Grain | Integrated? | Script |
|--------|------|---------|-------|-------------|--------|
| CHN/SRSCHAIN | Chain Reference | 3 | One per chain | Yes | 01-srschain-chains.js |
| VAL/SRSVALUE | Valid Values | 5 | One per code value | Yes (as transform ref) | -- |
| ITM2/ITM2DA | Supplier Item Master | 66 | One per supplier SKU | Yes | 02-itm2da-items.js |
| DIST/DISTDA | Distributor Master | 27 | One per distributor | Yes | 03-distda-locations.js |
| ITM/ITMDA | Dist Item Cross-Ref | 17 | One per dist+item | Yes | 04-itmda-enrichment.js |
| OUT/OUTDA | Retail Outlets | 71 | One per outlet per dist | Yes | 05-outda-accounts.js |
| INV/INVDA | Inventory | 19 | One per item+date+trans+UOM | Yes | 06-invda-inventory.js |
| SLS/SLSDA | Sales | 25 | One per invoice line | Yes | 07-slsda-depletions.js |
| CTL/CTLDA | Sales Control | 10 | One per dist+item+month | Yes | 08-ctlda-allocations.js |
| SLSLITE | Sales Lite | 9 | One per dist+item+date | No | -- |
| DEPL | Summary Depletions | 39 | One per dist+item+month | No | -- |
| CTLS | Depletions Control | 10 | One per dist+item+month | No | -- |
| ORD | Future Sales/Orders | 25 | One per order line | No | -- |
| SLM | Dist Salesperson | 14 | One per rep per dist | No | -- |
| CAL | Calendar | 7 | One per dist+type+date | No | -- |
| NON/NONA | Non-Reporters | 4-6 | One per dist+missing date | No | -- |
| VIPOUT | VIP Outlet Master | 75+ | One per outlet | No | -- |
| DIC | Dist Item Cross-Ref | 17 | One per dist+item | No (same data as ITMDA) | -- |
