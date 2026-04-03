---
name: ohfy-wms-expert
description: |
  Expert knowledge of the Ohanafy Warehouse Management System (OHFY-WMS). Apply when:
  - Building or debugging warehouse operations (picking, packing, shipping)
  - Working with inventory management, lot tracking, or allocation logic
  - Developing WMS-specific LWC components
  - Integrating external warehouse systems or 3PLs with Ohanafy
  - Understanding inventory lifecycle, location management, and transfer workflows
  Covers: Inventory operations, warehouse workflows, picking/packing/shipping,
  location management, lot tracking, and WMS-specific business logic.
---

# OHFY-WMS Expert Skill

## Source Repositories

**Backend:** `Ohanafy/OHFY-WMS` (Apex, v0.3.0)
**Frontend:** `Ohanafy/OHFY-WMS-UI` (LWC)
**Dependencies:** OHFY-Platform 0.4.0, OHFY-Data-Model 0.1.0, OHFY-Utilities 0.5.0, OHFY-Service-Locator 0.2.0

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-WMS
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

```bash
if [ ! -d /tmp/ohfy-wms ]; then
  gh repo clone Ohanafy/OHFY-WMS /tmp/ohfy-wms -- --depth 1
fi
if [ ! -d /tmp/ohfy-wms-ui ]; then
  gh repo clone Ohanafy/OHFY-WMS-UI /tmp/ohfy-wms-ui -- --depth 1
fi
```

Key paths:
- Apex classes: `/tmp/ohfy-wms/force-app/main/default/classes/`
- Apex triggers: `/tmp/ohfy-wms/force-app/main/default/triggers/`
- LWC components: `/tmp/ohfy-wms-ui/force-app/main/default/lwc/`

## Domain Coverage

- Inventory management and stock levels
- Location management (bins, zones, warehouses)
- Picking workflows and wave management
- Packing and shipping operations
- Lot tracking and expiration management
- Inventory transfers and adjustments
- Allocation and reservation logic
- Integration with OMS for order fulfillment
- 3PL and external warehouse integration

## Delegates To

- **ohfy-platform-expert** — For shared platform services
- **ohfy-data-model-expert** — For object schemas (Location, Inventory, Lot, Allocation)
- **ohfy-core-expert** — For trigger framework and bypass patterns
- **ohfy-oms-expert** — For order fulfillment integration
- **sf-apex** — For Apex coding patterns
- **sf-lwc** — For LWC component development
