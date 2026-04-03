---
name: ohfy-oms-expert
description: |
  Expert knowledge of the Ohanafy Order Management System (OHFY-OMS). Apply when:
  - Building or debugging order capture, fulfillment, and management features
  - Working with order-related Apex triggers, services, or flows
  - Developing OMS-specific LWC components
  - Integrating external systems with Ohanafy order processing
  - Understanding order lifecycle, status transitions, and validation rules
  Covers: Order creation, fulfillment workflows, order item management,
  pricing calculations, and OMS-specific business logic.
---

# OHFY-OMS Expert Skill

## Source Repositories

**Backend:** `Ohanafy/OHFY-OMS` (Apex, v0.3.0)
**Frontend:** `Ohanafy/OHFY-OMS-UI` (LWC)
**Dependencies:** OHFY-Platform 0.5.0, OHFY-Data-Model 0.1.0, OHFY-Utilities 0.5.0, OHFY-Service-Locator 0.2.0

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-OMS
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

```bash
if [ ! -d /tmp/ohfy-oms ]; then
  gh repo clone Ohanafy/OHFY-OMS /tmp/ohfy-oms -- --depth 1
fi
if [ ! -d /tmp/ohfy-oms-ui ]; then
  gh repo clone Ohanafy/OHFY-OMS-UI /tmp/ohfy-oms-ui -- --depth 1
fi
```

Key paths:
- Apex classes: `/tmp/ohfy-oms/force-app/main/default/classes/`
- Apex triggers: `/tmp/ohfy-oms/force-app/main/default/triggers/`
- LWC components: `/tmp/ohfy-oms-ui/force-app/main/default/lwc/`

## Domain Coverage

- Order creation and capture
- Order item management and line-level operations
- Fulfillment workflows and status transitions
- Pricing calculations and discount application
- Returns and credit processing
- Integration with WMS for warehouse fulfillment
- Integration with Payments for order settlement

## Delegates To

- **ohfy-platform-expert** — For shared platform services
- **ohfy-data-model-expert** — For object schemas
- **ohfy-core-expert** — For trigger framework and bypass patterns
- **ohfy-wms-expert** — For warehouse fulfillment integration
- **ohfy-payments-expert** — For payment processing
- **sf-apex** — For Apex coding patterns
- **sf-lwc** — For LWC component development
