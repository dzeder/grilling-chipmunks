---
name: ohfy-platform-expert
description: |
  Expert knowledge of the Ohanafy Platform package (OHFY-Platform). Apply when:
  - Working on shared platform services used by OMS, WMS, and REX
  - Understanding the service locator and dependency injection patterns
  - Debugging cross-package behavior or shared infrastructure
  - Building features that need to work across multiple SKUs
  Covers: Platform-level Apex services, shared LWC components, and
  infrastructure that all product SKUs depend on.
---

# OHFY-Platform Expert Skill

## Source Repository

**Repo:** `Ohanafy/OHFY-Platform`
**Version:** 0.6.0
**Namespace:** ohfy
**API Version:** 65.0
**Dependencies:** OHFY-Data-Model 0.1.0, OHFY-Utilities 0.5.0, OHFY-Service-Locator 0.1.0

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-Platform
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

```bash
if [ ! -d /tmp/ohfy-platform ]; then
  gh repo clone Ohanafy/OHFY-Platform /tmp/ohfy-platform -- --depth 1
fi
```

Key paths to read:
- Apex classes: `force-app/main/default/classes/`
- Apex triggers: `force-app/main/default/triggers/`
- LWC components: `force-app/main/default/lwc/`
- Custom metadata: `force-app/main/default/customMetadata/`

## Role in Architecture

OHFY-Platform sits between the foundation packages (Core, Data-Model, Utilities) and the product SKUs (OMS, WMS, REX). It provides:

- Shared platform services consumed by all SKUs
- Common UI components used across product interfaces
- Cross-cutting concerns (logging, error handling, configuration)
- Service registration via OHFY-Service-Locator

## Delegates To

- **ohfy-data-model-expert** — For object schema questions
- **ohfy-core-expert** — For trigger/service layer behavior
- **sf-apex** — For Apex coding patterns
- **sf-lwc** — For LWC component development
