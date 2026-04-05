---
title: "Distribution Trends — Beverage Industry"
last_updated: "2026-04-05"
next_review: "2026-07-05"
confidence: medium
sources:
  - "Sovos ShipCompliant — sovos.com/blog/ship"
  - "VinePair — vinepair.com (Reyes/RNDC coverage)"
  - "Shanken News Daily — shankennewsdaily.com"
  - "The Spirits Business — thespiritsbusiness.com"
  - "Brewers Association — brewersassociation.org"
  - "NIQ (NielsenIQ) — nielseniq.com"
  - "Beverage Industry Magazine — bevindustry.com"
  - "Fortune Business Insights, Grand View Research"
maintained_by: content-watcher
ohanafy_relevance:
  - skills/ohanafy/core
  - skills/ohanafy/oms
  - skills/ohanafy/ecom
  - skills/ohanafy/rex
  - knowledge-base/beverage-supply-chain/glossary
---

# Distribution Trends

## DTC (Direct to Consumer) Shipping Expansion

The post-Prohibition 3-tier system (see `glossary.md`) is slowly being bypassed by DTC shipping laws, though progress is uneven and category-specific.

### Wine DTC — Mature but Still Expanding

- Wine DTC shipping has been legal since the 2005 *Granholm v. Heald* Supreme Court decision opened interstate commerce.
- 2025 marked 20 years of DTC wine shipping compliance. The channel is well-established with sophisticated compliance infrastructure.
- **Mississippi** passed a new DTC wine shipping law effective July 2025 — one of the last holdout states.
- **Delaware** passed a DTC wine law in 2025, effective sometime in 2026, but with a critical restriction: wineries cannot sell DTC and at wholesale simultaneously. This makes the law impractical for most wineries. Industry groups are lobbying for amendment.

### Spirits DTC — Emerging Fast

- **California AB 1246** (signed 2025, effective January 1, 2026): Landmark legislation creating a one-year pilot program allowing qualifying out-of-state craft distillers to ship spirits DTC to California consumers.
  - Limit: 2.25 liters per consumer per day
  - Requires adult signature on delivery
  - Annual reporting to CA ABC
  - Pilot expires December 31, 2026 — renewal expected if successful
- California is the largest spirits market in the US. This pilot is a bellwether for other states.
- Currently ~15 states allow some form of spirits DTC shipping, up from ~10 in 2023.

### Beer DTC — Lagging

- DTC beer shipping remains limited. Most states restrict or prohibit it.
- Freshness concerns (unlike wine/spirits, beer has a short shelf life) and lower price points make DTC economics harder.
- Craft breweries with strong club/subscription models are most active in pushing for DTC access.

### Implications for Ohanafy

- Ecom module must support state-by-state compliance rules — this is currently a **gap** (see `competitive-landscape.md`)
- DTC orders use different fulfillment flows than 3-tier orders — the OMS needs to distinguish between DTC and distributor channels
- DTC volume data should feed into the same `Depletion__c` analytics to give suppliers a complete picture
- Integration with shipping compliance platforms (Sovos ShipCompliant) is a near-term need

---

## Distributor Consolidation

The middle tier (distributors) is undergoing rapid consolidation, concentrating market power in fewer, larger companies.

### Reyes Holdings — Expanding into Wine & Spirits

- Reyes Beverage Group (historically the largest US beer distributor) is acquiring distribution operations in **11 RNDC markets**: Arizona, Colorado, Florida, Hawaii, Louisiana, Maryland, Oklahoma, South Carolina, Texas, Virginia, and Washington DC.
- These markets represent ~$6 billion in annual revenue — roughly half of RNDC's total.
- Deal closing targeted by end of May 2026, pending regulatory approval.
- Signals Reyes' push toward becoming a "total beverage" distributor (beer + wine + spirits).

### RNDC — Under Pressure

- Republic National Distributing Company (RNDC), the #2 wine & spirits distributor, has been retrenching:
  - Lost several major supplier relationships in 2024-2025
  - Abruptly exited **California** in 2025 — the largest spirits market — leaving thousands of producers scrambling for new distribution
  - Triggered widespread layoffs across multiple markets
  - The 11-market sale to Reyes reduces RNDC to a regional operator

### Southern Glazer's Wine & Spirits (SGWS)

- SGWS remains the largest wine & spirits distributor in the US.
- Publicly expects "continued consolidation across all tiers" of the beverage industry.
- Benefits from RNDC's struggles — picking up displaced supplier accounts.
- Anheuser-Busch InBev is deepening its "total beverage" partnership with SGWS.

### What Consolidation Means for Ohanafy Customers

- **Smaller suppliers lose leverage.** Fewer distributors means less negotiating power for mid-market suppliers (Ohanafy's core customer).
- **Data integration complexity increases.** As distributors merge, depletion report formats change. Ohanafy's EDI and data integration skills must handle format transitions.
- **Territory disruption.** When distributors merge or exit, supplier territories (`Distributor__c.Territory__c`) need rapid remapping. This is a common support request.
- **Opportunity for Ohanafy:** Suppliers need better tools to manage distributor relationships, track performance across fewer but larger partners, and react quickly to territory changes. The `Footprint` concept (which distributors carry which brands in which territories) becomes critical.

---

## Category Shifts

Consumer preferences are reshaping the beverage landscape. These shifts directly affect what Ohanafy customers produce, sell, and track.

### Non-Alcoholic Beverages — Accelerating Growth

- Non-alcoholic (NA) beverages are "no longer a niche — it's a billion-dollar movement" (NIQ, 2025).
- NA beer, spirits alternatives, and functional beverages are the fastest-growing segment.
- Key brands: Athletic Brewing (NA beer leader), Seedlip (NA spirits), HOP WTR, Curious Elixirs.
- The global non-alcoholic RTD market: $805B in 2025, projected $1.41T by 2034 (6.6% CAGR).
- **Ohanafy impact:** NA products use the same distribution channels but may have different regulatory treatment (FDA vs. TTB). The `Brand__c` and `Product2` objects need to accommodate NA categorization. Some NA products don't require COLA approval, changing the product launch timeline.

### RTD Cocktails — Strong Growth Continues

- Ready-to-drink cocktails grew ~20% in volume in 2025 while traditional spirits declined ~6%.
- US RTD cocktail market projected to grow at 14% CAGR through 2033.
- RTDs are stealing share from traditional spirits — combined total spirits grew only ~1%.
- Cans dominate (78.2% of RTD format in 2025).
- **Ohanafy impact:** RTD SKUs have different packaging configurations (multi-packs, variety packs) that stress the WMS pallet/picking logic. Promotion structures differ from traditional spirits. The `Item__c` object needs to handle variety pack parent-child relationships.

### Hard Seltzer — Post-Peak Normalization

- Hard seltzer peaked in 2021 and has been declining since.
- Category dollar sales down ~5% in Q1 2025 (Boston Beer Co. data).
- UK volumes down 1.1% in 2025 (improving from -5.8% and -7.8% in prior years).
- Seltzer launches fell from 1-in-3 RTD launches (2021) to 1-in-9 (2024).
- Despite decline, global market still $19B (2024), projected $75B by 2034 at 15% CAGR — the category isn't dying, it's maturing.
- **Ohanafy impact:** Customers who over-invested in seltzer SKUs are rationalizing their portfolios. Support agents should expect questions about archiving SKUs and adjusting forecasts.

### Craft Beer — Contraction Era

- 2024 was the first year in 20 years where US craft brewery closures exceeded openings: 501 closures vs. 434 openings.
- 2025 continued the trend: 434 closures vs. 268 openings.
- Craft beer production declined 4% in 2024.
- Causes: rising costs, market saturation, competition from RTDs and cannabis beverages.
- The Brewers Association describes this as a "painful period of rationalization."
- **Ohanafy impact:** Craft brewery customers may be downsizing or consolidating. Support agents should be sensitive to this context. Ohanafy's value proposition for craft becomes operational efficiency — doing more with less. The WMS module's picking optimization and the OMS module's fulfillment workflows help reduce operating costs.

---

## Technology Adoption

How quickly the beverage distribution channel is adopting new technology.

### Digital Ordering

- Digital ordering platforms are growing but penetration varies dramatically by distributor size.
- Large distributors (Reyes, SGWS) have sophisticated B2B ordering portals.
- Mid-market and independent distributors often still accept orders by phone, fax, or email.
- Ohanafy's OMS and the Ecom module bridge this gap for suppliers selling through both channels.

### Warehouse Automation

- Pick-to-light, voice picking, and RFID adoption is concentrated in large distributors.
- Mid-market warehouses (Ohanafy's WMS target) are primarily upgrading from paper-based to mobile-device-based picking.
- Full warehouse automation (AS/RS, robotic palletization) remains rare in beverage — the product variety and temperature requirements make automation harder than in general logistics.

### Mobile-First Field Sales

- Field sales is the most digitized workflow — mobile CRM and route planning tools are standard.
- GoSpotCheck/FORM, Repsly, and GreatVines all compete for the mobile field execution layer.
- Ohanafy's REX LWC components serve this need but compete with specialized mobile-first tools.

### AI / ML Adoption

- Early stage across the industry. Most suppliers use spreadsheet-based forecasting.
- Demand forecasting and trade promotion optimization are the most-discussed AI use cases.
- See `ai-supply-chain.md` for detailed analysis.
