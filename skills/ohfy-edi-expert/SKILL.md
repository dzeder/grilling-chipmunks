---
name: ohfy-edi-expert
description: |
  Expert knowledge of the Ohanafy EDI system (OHFY-EDI). Apply when:
  - Working with Electronic Data Interchange (X12 850/810/856)
  - Integrating B2B partners via OpenText, Transcepta, or Orderful
  - Debugging EDI document parsing or generation
  - Understanding EDI workflows and trading partner management
  Covers: ANSI X12 document processing, B2B data interchange, trading partner
  configuration, and EDI-to-Salesforce data mapping.
---

# OHFY-EDI Expert Skill

## Source Repository

**Repo:** `Ohanafy/OHFY-EDI`
**Language:** Kotlin
**Purpose:** B2B Electronic Data Interchange

### Accessing Current Source

```bash
if [ ! -d /tmp/ohfy-edi ]; then
  gh repo clone Ohanafy/OHFY-EDI /tmp/ohfy-edi -- --depth 1
fi
```

## Domain Coverage

- ANSI X12 document types:
  - **850** — Purchase Orders
  - **810** — Invoices
  - **856** — Advance Ship Notices
- Trading partner management
- EDI document parsing and generation
- B2B connector integration (OpenText/TBM, Transcepta, Orderful)
- EDI-to-Salesforce data mapping
- Error handling and acknowledgments (997)
- AS2 transport protocol

## Related Skills

The `edi-processing-specialist` agent has deep expertise in EDI patterns.
Reference `docs/integration-guides/` for scenario examples involving EDI.

## Delegates To

- **edi-processing-specialist** (agent) — For EDI-specific implementation
- **ohfy-core-expert** — For Salesforce-side data mapping
- **tray-architecture** — For Tray.io EDI workflow patterns
- **salesforce-composite** — For API integration patterns
