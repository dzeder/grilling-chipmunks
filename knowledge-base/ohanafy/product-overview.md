# Ohanafy Product Overview

<!-- Synthesized from ohfy-*-expert skills and beverage-erp-expert agent knowledge -->

## What Ohanafy Does

Ohanafy is a Salesforce-based beverage supply chain SaaS platform. It provides the
**operational planning and CRM layer** that sits alongside a distributor's existing ERP
(typically Encompass or VIP). The ERP handles transactional operations (route accounting,
warehouse management, invoicing, inventory). Ohanafy handles the human coordination layer
(who does what, when, how do we plan it, how do we track it, how do we learn from it).

## Who It Serves

**Primary:** Beverage distributors (beer, wine, spirits, non-alcoholic) across all sizes.
Ohanafy is built for distributors who are already invested in or adopting Salesforce.

**Secondary:** Beverage suppliers/producers who need visibility into their distribution
network's operational performance.

## Platform

- Built on **Salesforce** as a 2GP managed package ecosystem
- Multiple SKU packages that can be installed independently or together
- **Tray.io** as the integration platform connecting to ERP, HCM, and other systems
- **AWS** for supplementary infrastructure (Lambda, S3, CDK)

## Architecture

Ohanafy is composed of multiple managed packages (SKUs):

```
OHFY-Core (foundation)
  ├── OHFY-Platform (shared services)
  ├── OHFY-Data_Model (30+ custom objects, field schemas)
  ├── OHFY-OMS (order management)
  │    └── OHFY-OMS-UI (order UI components)
  ├── OHFY-WMS (warehouse management)
  │    └── OHFY-WMS-UI (warehouse UI components)
  ├── OHFY-REX (retail excellence)
  │    └── OHFY-REX-UI (retail UI components)
  ├── OHFY-EDI (electronic data interchange)
  ├── OHFY-Ecom (e-commerce)
  ├── OHFY-Payments (payment processing)
  └── OHFY-Configure (system configuration)
```

## Key Capabilities

- **Task and activity management** — plan, assign, and track operational tasks
- **Workforce coordination** — know who is available, skilled, and assigned (via UKG integration)
- **Order management** — capture, process, and fulfill orders
- **Warehouse operations** — picking, packing, shipping, inventory management
- **Retail execution** — in-store surveys, display compliance, shelf audits
- **EDI processing** — X12 850 (purchase order), 810 (invoice), 856 (ASN)
- **E-commerce** — Shopify/WooCommerce integration for online ordering
- **Payment processing** — settlement, reconciliation
- **System configuration** — feature flags, customer-specific setup

## Market Position

Ohanafy is **not** a full ERP. It does not handle route accounting, pricing engines,
or invoicing. This is intentional — no distributor wants to rip out their ERP.
Ohanafy fills the gap that ERPs leave: operational planning, workforce coordination,
and modern CRM on the Salesforce platform.

See `knowledge-base/industry-insights/competitive-landscape.md` for full competitor analysis.
