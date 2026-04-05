---
title: "Product Capability Map — Industry Trends × Ohanafy SKUs"
last_updated: "2026-04-05"
next_review: "2026-07-05"
confidence: medium
sources:
  - "Derived from knowledge-base/industry-insights/ files"
  - "OHFY source indexes (core, oms, wms, ecom)"
  - "skills/ohanafy/*/SKILL.md coverage sections"
maintained_by: manual
ohanafy_relevance:
  - skills/ohanafy/core
  - skills/ohanafy/oms
  - skills/ohanafy/wms
  - skills/ohanafy/ecom
  - skills/ohanafy/rex
  - skills/ohanafy/edi
  - skills/ohanafy/payments
---

# Product Capability Map

Maps industry needs to Ohanafy product capabilities and gaps. Use this to understand where Ohanafy is strong, where gaps exist, and where new features should be prioritized.

**Capability levels:**
- **STRONG** — Core functionality, well-implemented, in production
- **PARTIAL** — Functionality exists but incomplete or basic
- **PLANNED** — On roadmap or scaffolded but not implemented
- **GAP** — No capability; would require new development

## Capability Matrix

### Order Management & Fulfillment

| Industry Need | SKU | Level | Key Objects / Components | Notes |
|--------------|-----|-------|------------------------|-------|
| 3-tier order capture | OMS | STRONG | `Order__c`, `Order_Item__c`, `CreateInvoiceController` | DSD-native. Pre-sell + van-sell models |
| Invoice lifecycle | OMS | STRONG | `Invoice__c`, `InvoiceTriggerService` (7 events) | Full status progression: New→Complete |
| Sell from truck | OMS | STRONG | `SellFromTruckController` | On-site order modification during delivery |
| Credit/returns | OMS | STRONG | `Credit__c`, `CreateCreditsController`, `CreditTriggerService` | Damage, short delivery, expiration, pricing errors |
| Promotion management | OMS | STRONG | `Promotion__c`, `Promotion_Item__c`, `createPromotions` LWC | Post-offs, depletion allowances. Duplicate prevention built in |
| Allocation management | OMS | STRONG | `CreateAllocationsController` | Limited product distribution control |
| Delivery metrics | OMS | STRONG | `B_Invoice_MetricUpdater`, `S_Invoice_MetricUpdater` | Nightly batch processing of delivery performance |
| Digital B2B ordering | Ecom | PARTIAL | Tray.io → Shopify/WooCommerce | External platform dependent; no native B2B portal |

### Warehouse Operations

| Industry Need | SKU | Level | Key Objects / Components | Notes |
|--------------|-----|-------|------------------------|-------|
| Picking workflows | WMS | STRONG | `deliveryPicking`, `invoicePicking`, `Q_ProcessMassPicking` | Single, route-based, and mass picking |
| Inventory receiving | WMS | STRONG | `Inventory_Receipt__c`, `createInventoryReceipt` LWC | Full receiving with quantity validation |
| Lot tracking | WMS | STRONG | `Inventory_Receipt_Item__c`, `useLotTracking` API | Expiration dates, lot numbers |
| Keg management | WMS | STRONG | `calculateInventoryReceiptKegs` methods | Deposit tracking, returnable asset management |
| Purchase orders | WMS | STRONG | `Purchase_Order__c`, `createPurchaseOrder` LWC | Full lifecycle with adjustments |
| Location transfers | WMS | STRONG | `Transfer__c`, `Transfer_Group__c`, `locationTransfer` LWC | Between warehouse locations |
| Palletization | WMS | STRONG | `E_Pallet`, `palletization` LWC, `splitPalletItemModal` | Full/mixed/layer pallet operations |
| Partial pick handling | WMS | STRONG | `confirmPartialPick` LWC, `oversold` LWC | When inventory falls short of order |
| Cold chain temp monitoring | WMS | GAP | — | Manual zone assignment only. No sensor integration |
| RFID integration | WMS | GAP | — | No RFID reader integration |
| Voice picking | WMS | GAP | — | No voice-directed picking support |
| Automated picking (AS/RS) | WMS | GAP | — | No robotics integration |

### Retail Execution

| Industry Need | SKU | Level | Key Objects / Components | Notes |
|--------------|-----|-------|------------------------|-------|
| Field sales routes | REX | PARTIAL | `Account_Route__c`, `B_Route_DeliveryCreator` | Basic route assignment and delivery creation |
| Account visit tracking | REX | PARTIAL | REX-UI LWC components | Mobile field data capture |
| Display/shelf tracking | REX | PARTIAL | `Display__c` objects | Manual data entry — no image recognition |
| CV shelf audit | — | GAP | — | No computer vision. See `ai-supply-chain.md` |
| AI route optimization | — | GAP | — | Basic routes only. No AI optimization |
| Share-of-shelf analytics | — | GAP | — | `Display__c` data is manual and sparse |

### E-Commerce & DTC

| Industry Need | SKU | Level | Key Objects / Components | Notes |
|--------------|-----|-------|------------------------|-------|
| Shopify integration | Ecom | PARTIAL | Tray.io connector | Product sync, order capture, fulfillment status |
| WooCommerce integration | Ecom | PARTIAL | Tray.io connector | Similar to Shopify pattern |
| DTC shipping compliance | Ecom | GAP | — | No state eligibility checking. Critical need |
| Age verification | Ecom | GAP | — | Handled by external platform only |
| DTC volume tracking | Ecom | GAP | — | Per-consumer shipping limits not enforced |
| Marketplace integrations | Ecom | GAP | — | No ReserveBar, Vivino, etc. |
| Channel pricing comparison | Ecom | GAP | — | No cross-channel price visibility |
| Tax calculation | Ecom | GAP | — | No Avalara/Sovos integration |

### Data & Analytics

| Industry Need | SKU | Level | Key Objects / Components | Notes |
|--------------|-----|-------|------------------------|-------|
| Depletion tracking | Core | STRONG | `Depletion__c`, `DepletionTriggerService` | Primary demand signal |
| Account performance | Core | STRONG | `Account_Item__c`, `BA_AccountItem_Updater` | Account-level item tracking |
| Account balance tracking | Core | STRONG | `B_Account_AccountBalanceUpdater` | Daily batch financial updates |
| Pricelist management | Core | STRONG | `Pricelist__c`, `Pricelist_Item__c` | Territory-specific, version-controlled |
| Demand forecasting | — | GAP | `Depletion__c` (data available) | Data exists; no ML model. See `ai-supply-chain.md` |
| Trade spend ROI | — | GAP | `Promotion__c` + `Depletion__c` (data available) | Data exists; no analysis tooling |
| Multi-distributor aggregation | — | GAP | — | Single-source depletions only |

### Integration & Connectivity

| Industry Need | SKU | Level | Key Objects / Components | Notes |
|--------------|-----|-------|------------------------|-------|
| EDI (850/810/856) | EDI | STRONG | Kotlin service | B2B interchange with distributors |
| Tray.io iPaaS | Integrations | STRONG | `skills/tray-ai/` | Primary integration platform |
| Payment processing | Payments | STRONG | Payment classes (v0.32.0) | Most mature package |
| Salesforce Agentforce | — | PLANNED | — | See `salesforce/ecosystem-updates.md` |
| Data Cloud integration | — | PLANNED | — | ROI evaluation in progress |

---

## Feature Gap Priorities

### High Priority — Customer-Requested, Competitive Pressure

| Gap | Why Now | Effort | Data Dependency |
|-----|---------|--------|----------------|
| **DTC shipping compliance** | CA spirits DTC pilot opened Jan 2026. Customers asking. Ecom module can't enforce state rules. | L | State regulation database needed |
| **Demand forecasting MVP** | Every competitor talks about AI. Ohanafy has the data (`Depletion__c` + `Promotion__c`). | M | 2+ years depletion history |
| **Trade spend ROI analysis** | GreatVines/Andavi competitive advantage. Ohanafy has `Promotion__c` data but no analysis layer. | M | Promotion + Depletion correlation |

### Medium Priority — Market Differentiation

| Gap | Why Now | Effort | Data Dependency |
|-----|---------|--------|----------------|
| **CV shelf audit integration** | GoSpotCheck/FORM+Trax merger makes integration path clearer. Already on SF AppExchange. | M | GoSpotCheck API access |
| **AI route optimization** | Salesforce Maps integration would give immediate capability. | S | Account geolocation data |
| **Cold chain monitoring** | IoT sensor costs dropping. Mid-market warehouses starting to adopt. | M | Sensor hardware + API |
| **Multi-distributor depletion aggregation** | Diver/DataDive competitive advantage. Supplier pain point during consolidation. | L | Standardized depletion format across distributors |

### Low Priority — Future Market, Early Signal

| Gap | Why Now | Effort | Data Dependency |
|-----|---------|--------|----------------|
| **Marketplace integrations** (ReserveBar, Vivino) | Drizly shutdown consolidated marketplace landscape. New platforms emerging. | M per marketplace | Marketplace API access |
| **Voice picking / RFID** | Mid-market adoption still early. Wait for clearer standards. | L | Hardware investment |
| **Predictive allocation optimization** | Interesting for rare release management but niche use case. | M | Historical allocation + depletion data |
| **Automated territory rebalancing** | Useful during distributor consolidation but complex. | L | Account performance + geographic data |

---

## Trend-to-SKU Cross-Reference

Maps each knowledge-base file's trends to the relevant Ohanafy SKUs and capability status:

| Trend (Source File) | Affected SKUs | Current Capability |
|--------------------|--------------|-------------------|
| DTC expansion (`distribution-trends.md`) | Ecom, OMS | PARTIAL (Shopify via Tray) / GAP (compliance) |
| Distributor consolidation (`distribution-trends.md`) | Core, EDI | STRONG (data model handles it) but territory changes are manual |
| NA beverage growth (`distribution-trends.md`) | Core, OMS | STRONG (data model accommodates) but FDA vs TTB distinction not tracked |
| RTD cocktails growth (`distribution-trends.md`) | WMS, OMS | STRONG but variety pack complexity stresses picking |
| Craft beer contraction (`distribution-trends.md`) | OMS, WMS | STRONG (operational efficiency value prop) |
| FOB pricing mechanics (`pricing-models.md`) | Core, OMS | STRONG (`Pricelist__c`, pricing services) |
| State posting rules (`pricing-models.md`) | Core | PARTIAL (pricelist exists but no posting compliance enforcement) |
| Promotional pricing (`pricing-models.md`) | OMS | STRONG (`Promotion__c`, `Promotion_Item__c`) |
| TTB/COLA compliance (`regulatory-landscape.md`) | Core | PARTIAL (Product2/Item__c exist but no COLA status tracking) |
| Franchise laws (`regulatory-landscape.md`) | Core | PARTIAL (Distributor__c territories but no legal constraint tracking) |
| DSD systems (`technology-landscape.md`) | REX, OMS | PARTIAL (basic routes; competitor DSD tools are deeper) |
| Warehouse automation (`technology-landscape.md`) | WMS | PARTIAL (mobile picking; no voice/RFID/robotics) |
| AI demand forecasting (`ai-supply-chain.md`) | Core (data), — (model) | GAP (data ready, model needed) |
| CV shelf audit (`ai-supply-chain.md`) | REX | GAP (Display__c is manual) |
| Agentforce (`ai-supply-chain.md`, `salesforce/ecosystem-updates.md`) | Platform | PLANNED (evaluating) |
| Connected App deprecation (`salesforce/ecosystem-updates.md`) | All | Action required — ECA migration needed |
