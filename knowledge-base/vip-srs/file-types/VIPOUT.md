# VIPOUT — VIP Outlet Master

## Overview

VIP's own consolidated outlet database with 75+ fields per record. Unlike OUTDA (which contains distributor-reported outlet data), VIPOUT is VIP's authoritative master record for each retail outlet, incorporating data from multiple distributors, license databases, and VIP's own validation processes. This is the most field-rich file in the VIP SRS system.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Pattern:** `VIPOUT.N{MMDDYYYY}`
- **Example:** `VIPOUT.N04102026`

## Load Method

- **Method:** Add/Update
- **Key:** VOACCT (VIP Outlet Account Number — VIP's own unique ID)

## Field Layout (Detail Records)

75+ fields. Key fields shown below (grouped by category):

### Identification

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | VOACCT | VIP Outlet Account Number | Y | 10 | A |
| 3 | VONAME | Outlet Name | Y | 40 | A |
| 4 | VODBA | DBA (Doing Business As) | N | 40 | A |

### Address

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 5 | VOADDR | Street Address | N | 40 | A |
| 6 | VOCITY | City | N | 25 | A |
| 7 | VOST | State | N | 2 | A |
| 8 | VOZIP | ZIP Code | N | 10 | A |
| 9 | VOCNTY | County | N | 25 | A |
| 10 | VOPHONE | Phone | N | 10 | A |
| 11 | VOFAX | Fax | N | 10 | A |
| 12 | VOEMAIL | Email | N | 60 | A |
| 13 | VOLAT | Latitude | N | 12 | N |
| 14 | VOLONG | Longitude | N | 12 | N |

### Classification

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 15 | VOCOD | Class of Trade | N | 2 | A |
| 16 | VOSTS | Status (A/I/D) | N | 1 | A |
| 17 | VOSELL | Sell Type | N | 2 | A |
| 18 | VOPTYPE | Package Type | N | 1 | A |
| 19 | VOLICTYPE | License Type | N | 2 | A |
| 20 | VOLICNBR | License Number | N | 20 | A |
| 21 | VOCHN | Chain Code | N | 10 | A |
| 22 | VOPREM | Premise Type | N | 1 | A |
| 23 | VOFWIN | Fine Wine Indicator | N | 1 | A |
| 24 | VOBEV | Beverage Indicator | N | 1 | A |
| 25 | VODISP | Display Indicator | N | 1 | A |

### Demographics

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 26 | VOOCC | Patron Occupation | N | 2 | A |
| 27 | VOPAGE | Patron Age | N | 1 | A |
| 28 | VOETHN | Patron Ethnicity | N | 2 | A |
| 29 | VOIVOL | Industry Volume | N | 2 | A |
| 30 | VOLIFE | Patron Lifestyle | N | 2 | A |

### Additional Fields (31-75+)

Fields 31-75+ include: contact names, owner information, distributor cross-references, VIP internal codes, audit timestamps, data source indicators, match quality scores, and extended classification attributes. The exact count varies as VIP adds new fields over time.

## Cross-References

| File | Relationship |
|------|-------------|
| OUTDA | OUTDA contains distributor-reported versions; VIPOUT is VIP's consolidated master |
| SRSCHAIN | VOCHN maps to chain reference |
| SRSVALUE | VOCOD, VOSELL, VOPTYPE, VOLICTYPE decode here |

## Potential Ohanafy Mapping

Could serve as the authoritative outlet master, replacing or supplementing distributor-reported OUTDA data. VIPOUT's consolidated data (from multiple distributor reports + license databases) is typically higher quality than any single distributor's OUTDA file. Could map to `Account` with a VIP-assigned external ID.

## Notes

- 75+ fields — the most field-rich file in VIP SRS.
- Unlike OUTDA (one record per distributor per outlet), VIPOUT has one record per outlet (VIP's consolidated view).
- VOACCT is VIP's own unique outlet ID — different from distributor-assigned account numbers (ROACCT in OUTDA).
- Lat/long fields enable geographic analysis and map visualization.
- DBA field captures alternate business names (e.g., the franchise name vs the legal entity name).
- VIP adds new fields periodically — always check the latest ISV spec for current field count.
- Match quality scores and data source indicators help assess the reliability of VIP's outlet data.
- Not all suppliers receive VIPOUT — it's an optional premium file from VIP.
