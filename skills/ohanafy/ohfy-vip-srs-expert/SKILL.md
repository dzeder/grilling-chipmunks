---
name: ohfy-vip-srs-expert
description: |
  Expert knowledge of the VIP Supplier Reporting System (VIP SRS). Apply when:
  - Working with VIP beverage distribution data files (SLSDA, OUTDA, INVDA, etc.)
  - Building or debugging VIP-to-Salesforce integrations
  - Understanding VIP file formats, field layouts, or coded values
  - Parsing SFTP-delivered .gz CSV files from Vermont Information Processing
  TRIGGER when: user asks about VIP SRS files, beverage distribution data ingestion,
  SFTP file parsing for distributors, or any of the 22 VIP file type names.
  Covers: All 22 VIP SRS file types, field mappings to Ohanafy, valid value codes,
  inventory transaction logic, repack handling, and depletion warehouse attribution.
---

# OHFY-VIP-SRS Expert Skill

## Source

**Spec:** VIP ISV Interface File Specifications v6.0 (January 2023)
**Publisher:** Vermont Information Processing (VIP)
**Purpose:** Beverage distribution data reporting — sales, inventory, outlets, items

## Knowledge Base

`knowledge-base/vip-srs/` — Complete VIP SRS specification reference

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all knowledge base files,
integration scripts, and Salesforce metadata. Read `references/file-type-index.md`
for all 22 VIP file types at a glance.

## Integration Implementation

`integrations/vip-srs/` — Ohanafy-specific scripts and mappings

- `integrations/vip-srs/docs/VIP_AGENT_HANDOFF.md` — THE source of truth for VIP-to-Ohanafy mapping
- `integrations/vip-srs/CLAUDE.md` — Technical implementation context
- `integrations/vip-srs/shared/constants.js` — Crosswalk maps and external ID prefixes
- `integrations/vip-srs/scripts/*.js` — Production transform scripts

## Domain Coverage

- **22 VIP SRS file types** (9 integrated, 13 reference-only)
- **Valid field values** (class of trade, transaction codes, license types, etc.)
- **File format conventions** (delimited CSV, HEADER/DETAIL/FOOTER, gzip delivery)
- **SFTP delivery and file naming**
- **Inventory transaction processing** (daily detail vs monthly summary, position vs movement)
- **Repack logic** (case/bottle conversion for repacked items)
- **Depletion warehouse attribution** (multi-warehouse distributors)
- **Sales transaction types** (retail, breakage, credit, sample, transfer)
- **Data quality:** Non-reporters, zero sales records, control/balancing files

## Related Skills

- **ohfy-core-expert** — Salesforce objects (Account, Product2, Depletion__c, Placement__c, etc.)
- **tray-expert** — Tray.io workflows for data orchestration
- **ohfy-oms-expert** — Order management context

## Delegates To

- **ohfy-core-expert** — SF data model questions
- **tray-expert** — Workflow patterns and Tray architecture
- **salesforce-composite** — API integration patterns
