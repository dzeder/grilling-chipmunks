# Competitive Landscape

<!-- Populated by Content Watcher insights, beverage-erp-expert knowledge, and team input -->

## ERP Tier Map

### Tier 1: Enterprise

| System | Owner | Strength | Weakness | Target Market |
|--------|-------|----------|----------|---------------|
| SAP S/4HANA | SAP | Multi-entity, international, deep financials | Extreme cost ($M+), 12-18mo rollout, no beverage DSD modules | >$500M revenue |
| Oracle NetSuite | Oracle | Cloud-native financials, multi-entity | Limited DSD, expensive licensing | Conglomerate subsidiaries |
| Encompass | Roper (Rutherford & Associates) | Purpose-built for beer distribution, dominant market share | Progress/OpenEdge legacy, limited APIs, closed ecosystem | 1-10M case/year beer distributors |

### Tier 2: Mid-Market and Specialized

| System | Owner | Strength | Weakness | Target Market |
|--------|-------|----------|----------|---------------|
| VIP | Roper | Purpose-built for wine/spirits, large SKU handling | Legacy platform (same corporate owner as Encompass) | Wine/spirits distributors |
| GreatVines | GreatVines | Salesforce-native, mobile-first DSD, modern UX | Narrower than Encompass on operational depth | SF-invested distributors |
| 3x/BluJay/E2open | Various | Route optimization, logistics focus | Not full ERP, overlay on existing systems | 50+ route operations |

### Tier 3: Emerging and Niche

| System | Owner | Strength | Weakness | Target Market |
|--------|-------|----------|----------|---------------|
| Ohanafy | Ohanafy | Salesforce platform, operational planning, CRM, extensible | Not a full ERP (no route accounting, warehouse, invoicing) | Any SF-invested distributor |
| Diver (DataDive) | DataDive | BI/analytics on top of ERP data | Not operational, analytics only | Any distributor needing reporting |
| GoSpotCheck | GoSpotCheck | In-market surveys, shelf audits, display compliance | Narrow scope, requires CRM/BI integration | Field execution teams |

## Ohanafy's Positioning

Ohanafy is **not** trying to replace Encompass, VIP, or SAP. It is positioned as the
**operational planning and CRM layer** that sits alongside the existing ERP:

- **ERP handles**: route accounting, warehouse management, invoicing, inventory
- **Ohanafy handles**: who does what, when, how do we plan it, how do we track it

### Why This Positioning Works

1. No distributor wants to rip out their ERP (12-18 month migrations, millions in cost)
2. The operational planning gap is real (most distributors use spreadsheets and whiteboards)
3. Salesforce platform provides unmatched extensibility (Lightning, Flow, Apex, API ecosystem)
4. Integration-first architecture — Ohanafy can connect to any ERP via Tray.io/MuleSoft

### Differentiators vs. GreatVines

GreatVines is the primary Salesforce-native competitor:

| Dimension | GreatVines | Ohanafy |
|-----------|-----------|---------|
| Focus | DSD execution (orders, deliveries, route) | Operational planning, task management, workforce |
| Depth | Deeper on transactional DSD | Broader on planning and coordination |
| Mobile | Strong mobile DSD app | Mobile task and activity management |
| Workforce | No workforce availability feature | UKG integration, availability grid |
| Relationship | Could be competitor, complement, or sequential adoption | |

The UKG workforce availability integration is uniquely Ohanafy's territory — a clear differentiator.

## Adjacent Solutions

### Middleware / iPaaS

| Platform | Fit for Ohanafy | Notes |
|----------|----------------|-------|
| Tray.io | Primary choice | Ohanafy's chosen iPaaS, Salesforce-centric, workflow-based |
| MuleSoft | Enterprise alternative | Salesforce-owned, more powerful but more expensive |
| Dell Boomi | Mid-market alternative | Good connectors, reasonable pricing |
| Custom P2P | Legacy reality | Most existing integrations are fragile, poorly documented custom builds |

### HCM

| Platform | Market Share | Notes |
|----------|-------------|-------|
| UKG Pro + WFM | Dominant | Primary HCM for mid-to-large distributors |
| ADP | #2 | Sometimes paired with UKG (ADP payroll + UKG scheduling) |
| Paycom/Paylocity | Emerging | Lower-cost, sub-200 employee distributors |

### Analytics

| Platform | Use Case | Notes |
|----------|---------|-------|
| Diver (DataDive) | Sales analysis, goal tracking, territory performance | Industry standard |
| Power BI | Modern analytics, dashboard-heavy | Growing adoption |
| Tableau | Visual analytics | Less common in beverage |

## Market Dynamics

- Distributor count declining (~3,000 from ~4,700 in 2000)
- Top 10 distributors control ~40% of volume
- Craft beer growth slowing but still driving SKU proliferation
- Non-alcoholic beverage category growing fastest
- Digital ordering platforms (Provi, LibDib) disrupting order intake
- Every major system vendor is adding API capabilities (slowly)
