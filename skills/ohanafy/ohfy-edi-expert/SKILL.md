---
name: ohfy-edi-expert
description: |
  Expert knowledge of the Ohanafy EDI system (OHFY-EDI). Apply when:
  - Working with Electronic Data Interchange (X12 850/810/856)
  - Working with MillerCoors UFF (Universal Flat File) invoices
  - Integrating B2B partners via OpenText/GXS, Transcepta, or Orderful
  - Debugging EDI document parsing, generation, or rejections
  - Understanding EDI workflows and trading partner management
  TRIGGER when: user asks about EDI documents (810/850/856), UFF, MillerCoors invoicing,
  B2B interchange, trading partner setup, OpenText/GXS errors, or EDI-to-Salesforce mapping.
  Covers: ANSI X12 document processing, UFF fixed-width invoicing, B2B data interchange,
  trading partner configuration, and EDI-to-Salesforce data mapping.
knowledge_refs:
  - knowledge-base/edi/uff-format.md
  - knowledge-base/edi/uff-retailer-requirements.md
  - knowledge-base/edi/uff-to-x12-810-mapping.md
---

# OHFY-EDI Expert Skill

## Source Repository

**Repo:** `Ohanafy/OHFY-EDI`
**Language:** Kotlin
**Purpose:** B2B Electronic Data Interchange

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-EDI
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

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
- **UFF — Universal Flat File** (MillerCoors fixed-width 810 format)
  - Full format spec: `knowledge-base/edi/uff-format.md`
  - Per-retailer requirements (7-Eleven, Walmart): `knowledge-base/edi/uff-retailer-requirements.md`
  - UFF → X12 810 translation mapping: `knowledge-base/edi/uff-to-x12-810-mapping.md`
- Trading partner management
- EDI document parsing and generation
- B2B connector integration (OpenText/GXS, Transcepta, Orderful)
- EDI-to-Salesforce data mapping
- Error handling and acknowledgments (997)
- AS2 transport protocol

## UFF Rejection Triage

When a UFF file is rejected by OpenText or a retailer, follow this order. Full methodology in `knowledge-base/edi/uff-format.md` § Diagnosing rejections.

0. **Diff against last-known-working version of the generator.** If the integration was working recently and now rejects every file, this step alone usually exposes the regression. A 5-second `diff` beats a 30-minute spec walk.
1. **Decode the X12 error tag** — `<SEGMENT>_<ELEMENT>_<DATA_ELEMENT>` (e.g., `BIG_01_373`). Translate to UFF positions using `knowledge-base/edi/uff-to-x12-810-mapping.md`.
2. **Walk every mandatory UFF position** that feeds the named X12 segment — not just the literal element. OpenText error tags often anchor on the first element when a *later* mandatory element is missing.
3. **Cross-ref retailer requirements** — see `knowledge-base/edi/uff-retailer-requirements.md`. UPC level, line-level tax, and required-field flags vary by partner.
4. **Reproduce with a test harness** for systemic bugs (pattern: `.context/uff-test/run.js`). Re-run after proposed fix to confirm.
5. **Record findings** in `customers/<name>/known-issues.md` and move resolved blockers to the "Resolved Issues" section with a diagnostic timeline.

**Common gotchas:**
- `BIG_01_373` typically means **missing Invoice Number (BIG02)** at UFF 77–98, not a date problem.
- JavaScript `null + ''` coercion produces literal `"null"` strings in alpha fields. If a UFF field shows `NULL` (uppercased), look for unguarded concatenation in the generator.
- Hardcoded `''` defaults in field mappings produce blank mandatory fields silently. The format step pads them to the right width with spaces.

## Case studies

- **2026-04-23 Beverage Market:** 7-Eleven batch rejected with `BIG_01_373`. Root cause was a one-line regression in the Tray script's `getInvoiceNumber` default initializer. Diagnostic timeline + latent bugs uncovered: `customers/beverage-market/edi/rejection-2026-04-23.md`.

## Related Skills

The `edi-processing-specialist` agent has deep expertise in EDI patterns.
Reference `docs/integration-guides/` for scenario examples involving EDI.

## Delegates To

- **edi-processing-specialist** (agent) — For EDI-specific implementation
- **ohfy-core-expert** — For Salesforce-side data mapping
- **tray-expert** — For Tray.io EDI workflow patterns and architecture
- **salesforce-composite** — For API integration patterns
