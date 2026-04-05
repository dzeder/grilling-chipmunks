---
title: "Technology Landscape — Beverage Distribution"
last_updated: "2026-04-05"
next_review: "2026-07-05"
confidence: medium
sources:
  - "NBWA — nbwa.org (warehouse automation for beverage)"
  - "Gartner Peer Insights — gartner.com/reviews (DSD software)"
  - "SimplyDepo — simplydepo.com (DSD software comparison)"
  - "Route4Me — route4me.com (route optimization)"
  - "Locus — locus.sh (DSD delivery optimization)"
  - "Globe Newswire — warehouse automation market 2025-2034"
  - "Food Logistics — foodlogistics.com"
  - "Toyota Automated Logistics — food & beverage automation"
maintained_by: content-watcher
ohanafy_relevance:
  - skills/ohanafy/wms
  - skills/ohanafy/oms
  - skills/ohanafy/rex
  - skills/integrations
---

# Technology Landscape — Beverage Distribution

Technology adoption in beverage distribution spans from fully automated large-distributor warehouses to small suppliers still running on spreadsheets. This file maps the technology landscape and identifies where Ohanafy fits — and where integration opportunities exist.

## DSD (Direct Store Delivery) Systems

DSD is the dominant delivery model in beverage — products go directly from distributor warehouse to retail store shelf, bypassing traditional warehousing at the retailer. The trend in 2025-2026 is a shift from basic delivery apps to complete platforms that handle orders, pricing, inventory, merchandising, and payments in one system.

### Key DSD Platforms

| Platform | Focus | Target Market | Notes |
|----------|-------|---------------|-------|
| Encompass Distribution Cloud | Full distributor ERP | Mid-to-large distributors | Market leader; see `competitive-landscape.md` |
| eoStar | Route accounting | Mid-market DSD | Strong in beer distribution |
| LaceUp Solutions | Route accounting | Mid-market DSD | Pre-sell and delivery models |
| Prism Visual Software | DSD distribution | Beverage-specific | Smaller player |
| Verial | Cloud ERP + DSD | Mid-market distributors | Mobile route sales, real-time invoicing |
| Mixpoint | Cloud ERP + DSD | Mid-market distributors | Specialized tools for chains, depots, promotions |
| ProspectMX (Prospect Solutions) | Distribution ERP | Mid-market distributors | Route accounting, mobile order entry |
| NGS ICE | Wholesale ERP | Mid-to-large distributors | Multi-location warehouse, complex pricing |
| inSitu Sales | DSD mobile | Small-mid distributors | Real-time inventory + route accounting |
| Route4Me | Route optimization | General delivery | Plans optimized routes, integrates with OMS |
| Locus | Logistics platform | General DSD | Route planning, fleet assignment, real-time monitoring |

### DSD vs. Ohanafy

Ohanafy serves **suppliers** — the companies sending product to distributors. DSD systems serve **distributors** — the companies delivering product to retailers. They are complementary:

- Ohanafy's OMS creates orders that flow into a distributor's DSD system
- Ohanafy's EDI module communicates with distributor DSD systems (850/810/856 transactions)
- Ohanafy's REX module handles the **supplier's** retail execution (distinct from the distributor's DSD delivery)
- Integration between Ohanafy and DSD systems (via Tray.io or direct API) is a common implementation pattern

---

## Route Optimization

Route planning and delivery optimization tools are increasingly AI-powered.

### Current Tools

| Tool | Approach | Beverage Relevance |
|------|----------|-------------------|
| Salesforce Maps (formerly MapAnything) | CRM-native route planning | Direct Salesforce integration — most relevant for Ohanafy |
| Badger Maps | Field sales route planning | Popular with beverage reps |
| Route4Me | Algorithmic route optimization | Supports DSD delivery patterns |
| Locus | AI-driven logistics | Fleet management + delivery optimization |
| OptimoRoute | Delivery route optimization | Handles time windows, vehicle capacity |

### Ohanafy Opportunity

- Ohanafy has `Account_Route__c` and `Delivery__c` objects in the REX module that support basic route planning.
- Current implementation supports route assignment and delivery scheduling but lacks AI optimization.
- **Integration opportunity:** Connect Salesforce Maps or Route4Me to Ohanafy's account/delivery data for optimized routing.
- See `ai-supply-chain.md` for the AI-driven route optimization roadmap.

---

## Warehouse Automation

The warehouse automation market is projected to reach $55 billion by 2030. For beverage, the unique challenges are temperature requirements, heavy products, and high SKU variety.

### Automation Tiers

#### Tier 1: Basic Digital (Most mid-market — Ohanafy WMS target)

- **Mobile device-based picking:** Replacing paper pick lists with mobile scanners/phones
- **Barcode scanning:** SKU verification at pick, pack, and ship stages
- **Basic WMS software:** Location tracking, inventory counts, FIFO enforcement
- **Ohanafy WMS covers this tier.** The WMS LWC components (`createInventoryReceipt`, picking workflows) digitize these operations.

#### Tier 2: Semi-Automated (Large distributors)

- **Pick-to-light systems:** Light indicators on shelving guide pickers to correct locations. Improve speed 30-50% over paper-based picking.
- **Voice-picking (voice-directed):** Hands-free, eyes-free picking via headset instructions. Common in beer distribution warehouses. Improves accuracy to 99.9%+.
- **Conveyor systems:** Automated transport between warehouse zones.
- **Integration opportunity:** Ohanafy WMS could feed pick lists to voice-picking or pick-to-light systems via API.

#### Tier 3: Fully Automated (Largest distributors only)

- **AGVs/AMRs (Autonomous Guided/Mobile Robots):** Transport pallets between zones. Engineered for temperature zones (ambient to freezer).
- **Robotic palletizers:** Automated pallet building for outbound shipments.
- **AS/RS (Automated Storage and Retrieval):** High-density automated storage.
- **Drone inventory scanning:** RFID/barcode scanning for cycle counts.
- **Rare in beverage** due to product variety, mixed-temperature requirements, and variable pallet configurations.

### Cold Chain Specifics

Beverage warehousing has unique temperature requirements:

| Category | Storage Temp | Notes |
|----------|-------------|-------|
| Beer | 38-45°F (3-7°C) | Freshness-sensitive; warm storage degrades quality |
| Wine | 55-58°F (13-14°C) | Stable temp critical; humidity control needed |
| Spirits | Ambient | Less sensitive, but temperature swings affect quality |
| Non-alcoholic | Varies | Refrigerated for RTD, ambient for shelf-stable |

- Automated systems must operate across temperature zones — AGVs/AMRs rated for cold storage.
- Automated FEFO (First Expired, First Out) rotation eliminates human errors in lot management.
- Temperature logging and traceability are compliance requirements in some jurisdictions.
- **Ohanafy WMS** handles lot tracking and FIFO through the `Inventory_Receipt__c` object and LWC picking workflows. Temperature monitoring would require sensor integration (currently a gap).

### RFID and IoT

- RFID tags on pallets/cases enable real-time inventory visibility without manual scanning.
- IoT sensors monitor temperature, humidity, and door openings in cold storage zones.
- Still early adoption in mid-market beverage — cost per tag and infrastructure investment remain barriers.
- **Ohanafy opportunity:** RFID integration would enhance the WMS inventory accuracy. IoT temperature data could feed into compliance reporting.

---

## Mobile Platforms

Field sales and delivery teams are the primary mobile users in beverage distribution.

### Field Sales Requirements

- **Offline-first:** Many retail accounts lack reliable connectivity. Mobile apps must work offline and sync when connected.
- **Barcode/QR scanning:** SKU lookup, inventory checks, shelf audit data capture.
- **Photo capture:** Display compliance, shelf conditions, competitor activity.
- **Order entry:** Create orders from the field, applied against current pricelist and inventory.
- **GPS/geolocation:** Route tracking, account visit verification, territory mapping.

### Ohanafy's Mobile Position

- Ohanafy's REX module has LWC components designed for mobile (REX-UI repo).
- OMS-UI has mobile order entry capabilities.
- WMS-UI supports mobile picking and receiving.
- **Challenge:** Salesforce mobile (Salesforce Mobile App / LWC mobile) competes with dedicated mobile-first tools (GoSpotCheck, Repsly, GreatVines mobile) that are purpose-built for field execution.
- **Advantage:** Single platform — field data flows directly into CRM, orders, and analytics without middleware.

---

## Integration Middleware

How systems connect in the beverage technology ecosystem.

### Ohanafy's Integration Stack

| Tool | Role | Reference |
|------|------|-----------|
| Tray.io | Primary iPaaS | `skills/tray-ai/` — Ohanafy's main integration platform |
| Salesforce Connect | External data | For real-time external object access |
| Salesforce Flows | Internal automation | Process orchestration within SF |
| MuleSoft | Enterprise iPaaS | Alternative for larger customers |
| EDI (Kotlin service) | B2B interchange | `skills/ohanafy/edi/` — 850/810/856 transactions |

### Common Integration Patterns

See `skills/integrations/` for detailed integration patterns. The most common beverage integrations:

1. **Supplier → Distributor:** Orders, invoices, pricing via EDI or API
2. **Distributor → Supplier:** Depletion reports, inventory levels, POS data
3. **Supplier → E-commerce:** Product catalog, pricing, inventory, orders (Shopify, WooCommerce via Tray)
4. **Supplier → Accounting:** Revenue, COGS, trade spend, excise tax (QuickBooks, NetSuite, Xero)
5. **Supplier → Warehouse:** Picking orders, receiving, inventory adjustments (Ohanafy WMS or external)

### Alternative iPaaS Platforms

| Platform | Relevance |
|----------|-----------|
| Workato | Enterprise iPaaS; good Salesforce connector |
| Celigo | NetSuite-focused; relevant for accounting integrations |
| Boomi (Dell) | Enterprise middleware; less common in mid-market |
| n8n | Open-source; developer-focused; lower cost |

See `distribution-trends.md` (Technology Adoption section) and `competitive-landscape.md` for how these tools fit the competitive landscape.
