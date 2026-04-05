---
title: "Regulatory Landscape — Beverage Alcohol"
last_updated: "2026-04-05"
next_review: "2026-07-05"
confidence: medium
sources:
  - "TTB.gov — ttb.gov (processing times, permits, excise tax)"
  - "NABCA — nabca.org (control state directory)"
  - "NIAAA APIS — alcoholpolicy.niaaa.nih.gov"
  - "Sovos ShipCompliant — sovos.com (DTC compliance)"
  - "Buchman Law Firm — buchmanlaw.com (franchise laws)"
  - "McBrayer PLLC — mcbrayerfirm.com (ABC law basics)"
maintained_by: content-watcher
ohanafy_relevance:
  - skills/ohanafy/core
  - skills/ohanafy/oms
  - skills/ohanafy/ecom
  - agents/support
---

# Regulatory Landscape — Beverage Alcohol

> **CRITICAL:** Ohanafy agents must NEVER answer compliance, regulatory, or legal questions directly. Always escalate to a human expert. This document provides context for understanding the regulatory environment — it is NOT legal advice and must NOT be used to auto-generate compliance recommendations. See `glossary.md` for term definitions.

## Federal Regulators

### TTB (Alcohol and Tobacco Tax and Trade Bureau)

The TTB is the primary federal regulator for beverage alcohol. Key functions:

#### Permits

- Every entity producing, importing, or wholesaling alcohol must hold a TTB permit (called a "basic permit").
- Permit types: Distilled Spirits Plant (DSP), Brewery/Brewpub, Bonded Winery, Importer, Wholesaler.
- Application volume: ~1,234 alcohol applications received year-to-date as of March 2026.
- Processing times vary by type — production/manufacturing permits take longer than wholesale permits.
- Permits are public record and searchable on TTB.gov.

#### COLA (Certificate of Label Approval)

- Required before any new alcohol product can be sold in the US.
- Every label (brand + SKU + format combination) needs its own COLA.
- Processing times fluctuate — check TTB's published processing time charts for current estimates.
- The COLA process is a common bottleneck for product launches. Delays of 2-8 weeks are typical; longer for non-standard labels.
- Ohanafy's `Product2` / `Item__c` objects should not be activated until COLA is approved.

#### Excise Tax

- Federal excise tax is levied on all alcohol production.
- **Craft Beverage Modernization Act (CBMA):** Originally temporary, TTB made the reduced excise tax rates permanent in September 2025. This provides significant tax savings for small producers (Ohanafy's core customers).
- Tax rates vary by category (beer, wine, spirits) and production volume.
- Tax returns are filed with TTB on a schedule — 2026 due dates are published on TTB.gov.
- Ohanafy's financial data should track excise tax as a separate cost component, not lumped into COGS.

### FDA (Food and Drug Administration)

The FDA regulates non-alcoholic beverages and certain labeling aspects of alcoholic beverages:

- **Non-alcoholic beverages:** FDA has primary jurisdiction. Different labeling requirements than TTB-regulated products.
- **Nutritional disclosure:** FDA is expanding nutritional labeling requirements to alcoholic beverages, though implementation timelines keep shifting.
- **Functional beverages:** CBD, adaptogen, and functional ingredient beverages face complex dual-jurisdiction issues between FDA and TTB.
- **NA category growth:** As non-alcoholic beverage alternatives grow (see `distribution-trends.md`), the regulatory distinction between FDA and TTB jurisdiction becomes important. An NA "spirit alternative" with <0.5% ABV is FDA-regulated, not TTB-regulated — different labeling, different compliance flow.

---

## State-Level Regulation

### Control States vs. License States

The US has two fundamentally different state regulatory models:

#### Control States (17 + Montgomery County, MD)

In control states, the state government operates as the distributor, retailer, or both:

| State | Control Level | Notes |
|-------|--------------|-------|
| Alabama | Spirits retail | |
| Idaho | Spirits retail + distribution | |
| Iowa | Spirits retail | |
| Maine | Spirits retail | |
| Michigan | Spirits distribution | |
| Mississippi | Spirits retail | |
| Montana | Spirits retail | |
| New Hampshire | Spirits retail + distribution | No sales tax on spirits |
| North Carolina | Spirits retail | |
| Ohio | Spirits retail | |
| Oregon | Spirits retail + distribution | |
| Pennsylvania | Wine + spirits retail | Most restrictive |
| Utah | Wine + spirits retail | |
| Vermont | Spirits retail | |
| Virginia | Spirits retail + distribution | |
| West Virginia | Spirits retail | |
| Wyoming | Spirits distribution | |

**Ohanafy implications for control states:**
- Pricing is set by the state, not negotiated between supplier and distributor
- Orders flow differently — the state purchasing authority is the buyer
- `Distributor__c` records for control states represent the state entity, not a private company
- Depletion data comes from the state system, not a commercial distributor

#### License States (33 + DC)

In license states, private entities hold licenses to distribute and retail alcohol. The state regulates through licensing, not direct participation. This is the standard 3-tier model.

### ABC Commissions

Every state has an Alcoholic Beverage Control (ABC) commission or equivalent that:
- Issues and enforces licenses
- Conducts compliance inspections
- Enforces advertising restrictions
- Manages price posting requirements (see `pricing-models.md`)
- Handles violation penalties (fines, license suspension/revocation)

Each state's ABC has different rules, forms, and enforcement patterns. There is no federal standardization.

### Franchise Laws — Distributor Termination Protection

Most states have franchise laws protecting distributors from arbitrary termination by suppliers. These laws are critical context for Ohanafy customers:

#### How Franchise Laws Work

- A supplier cannot terminate a distributor relationship without establishing **"good cause"** as defined by state statute.
- The supplier must give **advance notice** (typically 30-90 days) before termination.
- The distributor must be given an **opportunity to cure** the issue.
- These statutory protections **supersede any contractual provisions** — even if the distribution agreement says otherwise.
- Franchise law protections vary significantly by state and by product category (beer vs. wine vs. spirits).

#### Impact on Ohanafy Customers

- Suppliers cannot easily switch distributors, even in underperforming territories.
- Territory changes (`Distributor__c.Territory__c` updates) are legally constrained.
- The `Footprint` concept (which distributors carry which brands where) is not just an operational choice — it has legal dimensions.
- Support agents should be aware that "why can't we just drop this distributor?" questions involve legal complexity beyond operational preferences.

---

## Industry Self-Regulation

### DISCUS (Distilled Spirits Council of the United States)

- Voluntary marketing code for spirits producers
- Advertising guidelines (no marketing to minors, responsible consumption messaging)
- Lobbying for spirits DTC shipping expansion

### NBWA (National Beer Wholesalers Association)

- Beer distributor trade association
- Lobbies to preserve the 3-tier system
- Publishes industry data and best practices
- Opposes DTC shipping expansion that bypasses distributors

### Wine Institute / WineAmerica

- Wine producer trade associations
- Advocate for DTC wine shipping expansion
- Publish state-by-state DTC shipping guides

---

## Compliance Data in Ohanafy

The following data points in Ohanafy's data model have regulatory significance:

| Data Element | Object/Field | Regulatory Context |
|-------------|-------------|-------------------|
| Product labels | `Item__c`, `Product2` | Must have COLA before market entry |
| Distribution territories | `Distributor__c.Territory__c` | Subject to franchise laws |
| Pricing | `Pricelist__c` | Subject to state posting rules |
| Excise tax | Financial fields | Federal + state excise obligations |
| Depletion reports | `Depletion__c` | Required for distributor compliance |
| DTC orders | Ecom module | Subject to state shipping laws |
| Age verification | Ecom checkout | Required for all alcohol sales |
| Control state orders | `Order__c` | Different flow than license states |

> **Reminder:** This table maps data to regulatory context for agent awareness. It does NOT constitute a compliance implementation guide. All compliance features require legal review before implementation.
