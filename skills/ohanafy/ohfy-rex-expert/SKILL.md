---
name: ohfy-rex-expert
description: |
  Expert knowledge of the Ohanafy Retail Excellence system (OHFY-REX). Apply when:
  - Building or debugging retail/POS features
  - Working with in-store execution (displays, equipment, planograms)
  - Developing REX-specific LWC components
  - Integrating retail data with Ohanafy platform
  - Understanding retail workflows, route accounting, and field operations
  TRIGGER when: user asks about retail execution, POS operations, display
  management, route accounting, or REX-specific Apex/LWC components.
  Covers: Point of sale, retail execution, display management, equipment tracking,
  route operations, and retail-specific business logic.
---

# OHFY-REX Expert Skill

## Source Repositories

**Backend:** `Ohanafy/OHFY-REX` (Apex, v0.2.0)
**Frontend:** `Ohanafy/OHFY-REX-UI` (LWC)
**Dependencies:** OHFY-Platform 0.5.0, OHFY-Data-Model 0.1.0, OHFY-Utilities 0.5.0, OHFY-Service-Locator 0.2.0

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-REX
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

```bash
if [ ! -d /tmp/ohfy-rex ]; then
  gh repo clone Ohanafy/OHFY-REX /tmp/ohfy-rex -- --depth 1
fi
if [ ! -d /tmp/ohfy-rex-ui ]; then
  gh repo clone Ohanafy/OHFY-REX-UI /tmp/ohfy-rex-ui -- --depth 1
fi
```

Key paths:
- Apex classes: `/tmp/ohfy-rex/force-app/main/default/classes/`
- LWC components: `/tmp/ohfy-rex-ui/force-app/main/default/lwc/`

## Examples

- "How are display runs tracked in Ohanafy?" -- explain Display, Display_Run objects and retail execution workflows
- "Build an LWC component for route accounting" -- reference REX-UI components and Account_Route data model
- "Debug a planogram compliance trigger error" -- check trigger actions, field validations, and bypass patterns

## Domain Coverage

- Point of sale operations
- Retail execution and in-store activities
- Display management (Display, Display_Run)
- Equipment tracking and maintenance
- Route accounting and DSD operations
- Field team operations and mobile workflows
- Planogram compliance
- Retail analytics and reporting

## Delegates To

- **ohfy-platform-expert** — For shared platform services
- **ohfy-data-model-expert** — For object schemas (Display, Equipment, Account_Route)
- **ohfy-core-expert** — For trigger framework
- **sf-apex** — For Apex coding patterns
- **sf-lwc** — For LWC component development
