---
title: "Pricing Models — Beverage Industry"
last_updated: "2026-04-05"
next_review: "2026-10-05"
confidence: high
sources:
  - "American Spirits Exchange Ltd — americanspiritsltd.com"
  - "Beverage Trade Network — beveragetradenetwork.com"
  - "Andavi Solutions — andavisolutions.com (pricing strategy articles)"
  - "NIAAA Alcohol Policy Information System (APIS) — alcoholpolicy.niaaa.nih.gov"
  - "Sensiba — sensiba.com (trade spend accounting)"
  - "Moss Adams — mossadams.com (winery trade spending)"
  - "CT General Assembly — cga.ct.gov (price posting analysis)"
maintained_by: content-watcher
ohanafy_relevance:
  - skills/ohanafy/core
  - skills/ohanafy/oms
  - knowledge-base/beverage-supply-chain/glossary
---

# Pricing Models — Beverage Industry

Pricing in beverage alcohol follows regulated, multi-tier structures unlike most B2B SaaS industries. This file explains the mechanics that Ohanafy's data model must support. See `glossary.md` for term definitions (FOB, depletion, programming, etc.).

## FOB Pricing Mechanics

FOB (Free on Board) is the foundational pricing unit in the 3-tier system. It represents the price the supplier charges the distributor.

### Pricing Flow Through the Three Tiers

```
Tier 1 — Supplier (Ohanafy customer)
  FOB Price = Cost of Production + Supplier Margin
  └─→ Sold to distributor at FOB

Tier 2 — Distributor
  Wholesale Price = FOB + Laid-in Costs + Distributor Margin
    Laid-in costs: excise taxes, shipping, warehouse ops, insurance
  └─→ Sold to retailer at Wholesale (WHSL)

Tier 3 — Retailer / Restaurant
  Shelf / Menu Price = WHSL + Retailer Margin
    On-premise (bars/restaurants): typically 3-4x WHSL
    Off-premise (retail stores): typically 1.25-1.5x WHSL
  └─→ Sold to consumer at SRP (Suggested Retail Price)
```

### FOB vs. Delivered Pricing

- **FOB pricing** (standard): Distributor pays freight from supplier warehouse to their own. Freight cost is part of the distributor's laid-in cost.
- **Delivered pricing**: Supplier includes freight in the price. More common for large suppliers with national distribution.
- **Control state exception**: Control states (where the state IS the distributor) expect pricing based on delivery to the state warehouse, not FOB from the supplier.

### Ohanafy Data Model Mapping

| Pricing Concept | OHFY Object/Field | Notes |
|----------------|-------------------|-------|
| FOB price | `Item__c.FOB_Price__c` (via Core source-index) | Per-SKU base price |
| Pricelist | `Pricelist__c` | Version-controlled price sets |
| Pricelist entry | `Pricelist_Item__c` | Per-item pricing within a list |
| Pricing calculations | `S_PricingAdjustments` (OMS service) | Trigger service handling price logic |
| Market/territory pricing | Territory-specific `Pricelist__c` records | Same SKU, different FOB by market |

---

## State Posting & Price Maintenance Rules

Many states regulate how and when wholesale prices can change. This is one of the most complex compliance areas in beverage pricing.

### Price Posting Requirements

12 of the 38 license states require wholesalers to post (file with the state) their retail prices:

| State | Posting Frequency | Hold Period | Notes |
|-------|------------------|-------------|-------|
| Connecticut | Monthly | Yes — below-cost prohibition | No price discrimination between retailers |
| Delaware | Monthly | Varies | |
| Georgia | Continuous | No fixed period | Updates as changes occur |
| Indiana | Continuous | No fixed period | |
| Maryland | Monthly | Varies | |
| Massachusetts | Bi-monthly | Varies | |
| Missouri | Monthly | Varies | |
| New Jersey | Monthly | Yes | |
| New York | Monthly | Yes | Major market — most complex posting rules |
| Oklahoma | Bi-monthly | Varies | |
| South Dakota | Continuous | No fixed period | |
| West Virginia | Quarterly | Varies | |

### Price Maintenance (Hold) Rules

Some states require that once a price is posted, it cannot be changed for a specified period:

- **Idaho example:** If a posted price is lowered, that price cannot be changed again (up or down) for 6 months.
- **New York:** Monthly posting with mandatory hold periods. Wholesalers must honor posted prices for the full period.
- **Connecticut:** Prohibits selling below cost and prohibits price discrimination between retailers.

### Control States

In control states, the state government acts as the distributor (or sole retailer). Pricing is set by the state:

- 17 control states + Montgomery County, MD
- The state buys from suppliers at a state-set markup and sells to consumers
- Suppliers have less pricing flexibility in control states
- Ohanafy's pricing model needs to distinguish control-state vs. license-state pricing flows

### Ohanafy Implications

- `Pricelist__c` records need state/territory association to enforce posting rules
- Price change timestamps matter for compliance — the system must track when prices were set and when they become effective
- Agents must NEVER auto-generate pricing recommendations for posted-price states without flagging compliance review

> **Compliance warning:** Price posting rules are enforced by state ABC commissions. Violations can result in license suspension. Always escalate pricing compliance questions to a human expert.

---

## Promotional Pricing Structures

Beverage promotional pricing (called "programming" in the industry — see `glossary.md`) is how suppliers incentivize distributors and retailers to push their products.

### Post-Offs

- A temporary price reduction offered by the supplier through the distributor.
- The supplier reduces the FOB price for a defined period (typically 1-3 months).
- The distributor passes some or all of the savings to retailers.
- Most common promotional tool in the industry.
- **OHFY mapping:** `Promotion__c` + `Promotion_Item__c` (OMS module). The promotion record tracks the period, the item record tracks the per-SKU discount.

### Depletion Allowances (Billbacks)

- Volume-based rebates: the supplier pays the distributor a per-case incentive based on sell-through (depletions) to retailers.
- Only triggered when the product actually sells through to the next tier — not on purchases.
- Invoiced by the distributor back to the supplier ("billback").
- Requires depletion data to calculate — direct connection to `Depletion__c` in Ohanafy.
- **OHFY mapping:** Depletion allowance calculations reference `Depletion__c.Volume__c` and `Depletion__c.Report_Period__c`.

### Scan-Backs

- Retailer-level promotions: the supplier pays a per-unit discount based on units scanned at the register (not units purchased by the retailer).
- More performance-based than post-offs — only pays for actual consumer sales.
- Requires POS (point-of-sale) data from retailers, which is harder to obtain than distributor depletion data.
- Growing in popularity because they eliminate "forward-buying" (retailers stocking up at discount prices without increasing consumer sales).

### MDF / Co-Op (Marketing Development Funds)

- Supplier-funded marketing programs executed by distributors or retailers.
- Common uses: end-cap displays, menu features, tasting events, shelf talkers.
- Typically tracked separately from price-based promotions.
- Can be per-account or per-territory.

### Trade Spend Management

Trade spend (the total of all promotional and marketing investment through the channel) is typically 15-25% of a supplier's revenue. Managing it effectively is a major pain point:

- Tracking actual deductions vs. agreed-upon allowances
- Reconciling distributor billbacks against depletion data
- Measuring ROI on promotional programs
- **This is where GreatVines/Andavi has a competitive advantage** — their trade spend analytics are deeper than Ohanafy's current Promotion__c implementation.

---

## E-Commerce Pricing Challenges

DTC and marketplace pricing creates unique friction in the beverage industry.

### Price Consistency Conflicts

- Suppliers selling DTC must price competitively with retail — but retail prices are set by retailers, not suppliers.
- If DTC prices are lower than retail, retailers complain. If higher, DTC doesn't sell.
- The 3-tier system means the supplier doesn't control the final retail price.

### Minimum Advertised Price (MAP)

- Some suppliers enforce MAP policies to prevent undercutting.
- MAP enforcement is harder in beverage because the 3-tier system means the supplier has limited visibility into retail pricing.
- Ohanafy's Ecom module needs to surface pricing comparisons across channels.

### Marketplace Pricing

- Platforms like Drizly (shut down 2024), ReserveBar, Vivino, wine.com each have their own pricing models.
- Some marketplaces use algorithmic pricing that can undercut brick-and-mortar retailers.
- Suppliers need visibility across all channels — another integration opportunity for Ohanafy.

---

## Ohanafy Customer Pricing Patterns

Common pricing configurations by customer type:

### Breweries

- Simpler pricing: fewer SKUs, less vintage complexity
- Heavy use of post-offs and depletion allowances
- Seasonal promotions (summer variety packs, holiday gift packs)
- Keg pricing is separate from package pricing

### Wineries

- Complex pricing: vintage-specific, allocation-based for premium wines
- Multiple pricelists per territory (different FOB by state)
- DTC channel is significant — tasting room, wine club, online
- Trade spend focused on restaurant placements and wine dinners

### Spirits Producers

- Moderate complexity: no vintage, but age statements affect pricing
- Heavy promotional spending (post-offs, display programs)
- On-premise (bar) pricing has different margin structures than off-premise
- Cocktail program support is a growing promotion category
