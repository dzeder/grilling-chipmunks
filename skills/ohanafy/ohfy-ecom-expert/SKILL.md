---
name: ohfy-ecom-expert
description: |
  Expert knowledge of the Ohanafy E-Commerce system (OHFY-Ecom). Apply when:
  - Building or debugging e-commerce features (catalog, cart, checkout)
  - Integrating Shopify, WooCommerce, or other e-commerce platforms
  - Working with online order capture and fulfillment
  - Understanding e-commerce data flows into Ohanafy
  TRIGGER when: user asks about Shopify or WooCommerce integration, e-commerce
  order capture, online catalog sync, or cart/checkout flows in Ohanafy.
  Covers: Online storefront integration, catalog management, cart/checkout,
  e-commerce order processing, and Shopify/WooCommerce connectors.
knowledge_refs:
  - knowledge-base/ohanafy/product-overview.md
  - knowledge-base/ohanafy/feature-matrix.md
---

# OHFY-Ecom Expert Skill

## Source Repository

**Repo:** `Ohanafy/OHFY-Ecom`
**Languages:** Apex, OpenEdge ABL
**Dependencies:** OHFY-Core

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-Ecom
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

```bash
if [ ! -d /tmp/ohfy-ecom ]; then
  gh repo clone Ohanafy/OHFY-Ecom /tmp/ohfy-ecom -- --depth 1
fi
```

## Domain Coverage

- E-commerce platform integration (Shopify, WooCommerce)
- Online catalog management
- Cart and checkout flows
- E-commerce order creation in Ohanafy
- Product sync between platforms
- Pricing and inventory availability
- Customer account linking

## Examples

- "How do Shopify orders get into Ohanafy?" -- explain the Shopify-to-Ohanafy sync flow and connector patterns
- "Debug a WooCommerce product sync failure" -- check External_ID mapping, API payloads, and sync status
- "Set up a new e-commerce channel integration" -- walk through catalog sync, order capture, and fulfillment hooks

## Related Integration Projects

Reference the Tray workflow exports for active e-commerce integrations:
- Shopify connector workflows (in dhsOhanafy/Integrations)
- WooCommerce connector workflows
- CSV upload for bulk product management

## Delegates To

- **ohfy-core-expert** — For Salesforce-side order processing
- **ohfy-oms-expert** — For order fulfillment after capture
- **tray-expert** — For Tray.io workflow patterns and architecture
- **salesforce-composite** — For API integration patterns
