# OUTDA — Retail Outlets

## Overview

The Retail Outlet file contains distributor-reported account/outlet data — the retail locations where products are sold. Each record represents a single outlet as reported by a specific distributor, with 71 fields covering identification, address, licensing, class of trade, chain affiliation, demographic indicators, and sales rep assignments. This is the highest-column-count integrated file.

## Integration Status

**Integrated** — Script: `05-outda-accounts.js`

## File Naming

- **Pattern:** `OUT{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), WK (weekly), FX (fixed/full), NW (new)
- **Example:** `OUTDA.N04102026`

## Load Method

- **Method:** Add/Update
- **Key:** DISTID + ROACCT (Distributor ID + Account Number)

## Field Layout (Detail Records)

71 fields total. Key fields shown below:

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | N |
| 3 | ROACCT | Account Number | Y | 8 | A |
| 4 | RONAME | Outlet Name | Y | 35 | A |
| 5 | ROADDR | Street Address | N | 35 | A |
| 6 | ROCITY | City | N | 25 | A |
| 7 | ROST | State | N | 2 | A |
| 8 | ROZIP | ZIP Code | N | 10 | A |
| 9 | ROCNTY | County | N | 25 | A |
| 10 | ROPHONE | Phone | N | 10 | A |
| 11 | ROCOD | Class of Trade | Y | 2 | A |
| 12 | ROSTS | Outlet Status (A/I/D) | Y | 1 | A |
| 13 | ROSELL | Sell Type | N | 2 | A |
| 14 | ROPTYPE | Package Type | N | 1 | A |
| 15 | ROLICTYPE | License Type | N | 2 | A |
| 16 | ROLICNBR | License Number | N | 20 | A |
| 17 | ROCHN | Chain Code | N | 10 | A |
| 18 | ROOCC | Patron Occupation | N | 2 | A |
| 19 | ROPAGE | Patron Age | N | 1 | A |
| 20 | ROFWIN | Fine Wine Indicator | N | 1 | A |
| 21 | ROBEV | Beverage Indicator | N | 1 | A |
| 22 | ROPREM | Premise Type | N | 1 | A |
| 23 | RODISP | Display Indicator | N | 1 | A |
| 24 | ROSM1 | Sales Rep 1 Code | N | 8 | A |
| 25 | ROSM2 | Sales Rep 2 Code | N | 8 | A |
| 26 | ROWHSE | Warehouse Code | N | 10 | A |
| 27 | ROPARENT | Parent Distributor ID | N | 8 | A |
| 28 | ROETHN | Patron Ethnicity | N | 2 | A |
| 29 | ROIVOL | Industry Volume | N | 2 | A |
| 30 | ROLIFE | Patron Lifestyle | N | 2 | A |
| 31-71 | ... | Additional fields (lat/long, email, contact, etc.) | N | varies | varies |

## Ohanafy Mapping

Maps to `Account` (outlet accounts) with distributor-specific context:

| VIP Field | Salesforce Field | Notes |
|-----------|-----------------|-------|
| DISTID + ROACCT | Account.VIP_External_ID__c | ACT:{DISTID}:{ROACCT} |
| RONAME | Account.Name | |
| ROADDR/ROCITY/ROST/ROZIP | BillingAddress | |
| ROCOD | Class_of_Trade__c | Decode via SRSVALUE |
| ROSTS | Account active/inactive | A=Active |
| ROCHN | Chain__c lookup | Join to SRSCHAIN |
| ROSELL | Sell_Type__c | Decode via SRSVALUE |
| ROLICTYPE | License_Type__c | Decode via SRSVALUE |
| ROPREM | Premise_Type__c | On/Off premise |

## Cross-References

| File | Relationship |
|------|-------------|
| SRSCHAIN | ROCHN maps to chain reference |
| SRSVALUE | ROCOD, ROSELL, ROPTYPE, ROLICTYPE, ROOCC, ROPAGE, ROSTS decode here |
| DISTDA | DISTID maps to distributor master |
| SLSDA | BSACCT references outlet account number |
| SLM | ROSM1/ROSM2 reference salesperson codes |
| VIPOUT | VIP's own outlet master (75+ fields, superset of OUTDA) |

## Notes

- 71 fields per record — the largest integrated file type.
- ROCOD (Class of Trade) is the primary outlet classification — 30+ valid codes in SRSVALUE.
- One outlet may appear in multiple OUTDA files from different distributors, each with different DISTID. The external ID (ACT:{DISTID}:{ROACCT}) keeps them separate.
- ROSM1/ROSM2 enable rep-level analytics when joined with SLM data.
- ROWHSE identifies which warehouse serves this outlet — critical for depletion warehouse attribution.
- Lat/long fields (in positions 31-71) enable geographic analysis when populated.
- ROFWIN, ROBEV, ROPREM, RODISP are binary indicators (Y/N) for outlet characteristics.
