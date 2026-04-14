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

- `integrations/vip-srs/docs/VIP_DATA_DICTIONARY.md` — **Complete field reference** for all 16 SF objects (currency fields, dates, crosswalks, relationships). Use this for reports/dashboards.
- `integrations/vip-srs/docs/VIP_AGENT_HANDOFF.md` — Original mapping spec (STALE in places — scripts are authoritative, see ROADMAP Gotcha #22)
- `integrations/vip-srs/CLAUDE.md` — Technical implementation context
- `integrations/vip-srs/shared/constants.js` — Crosswalk maps and external ID prefixes
- `integrations/vip-srs/scripts/*.js` — Production transform scripts (source of truth for field mappings)

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

## Learned From

### Account/Contact Trigger Cascade (ROS2, 2026-04-13)
- `AccountTriggerMethods` class missing in managed package blocks ALL Account updates AND all Contact inserts
- Contact insert → ContactTrigger AfterInsert → Account update → AccountTriggerMethods → failure
- Workaround: purge before loading (inserts work, updates don't); Contacts have NO workaround
- See: `customers/shipyard/known-issues.md`

### Item Prerequisite Chain for Depletions (ROS2, 2026-04-10)
- Depletion__c.Item__c has a non-optional lookup filter requiring ALL 5:
  1. Item has `Finished_Good` record type
  2. `ohfy__Type__c = 'Finished Good'`
  3. `ohfy__UOM__c` set (e.g., 'US Count')
  4. `ohfy__Packaging_Type__c` set (dependent picklist, e.g., 'Each')
  5. `ohfy__Transformation_Setting__c` record linking Packaging_Type → Volume UOM
- Missing ANY prerequisite → `FIELD_FILTER_VALIDATION_EXCEPTION` on all depletions
- Script 02 sets prerequisites 1-4; Transformation_Setting__c must exist in org

### Managed RT Picklist Targeting (ROS2, 2026-04-14)
- Managed package record types have namespace prefix: `ohfy__Finished_Good`, not `Finished_Good`
- Deploying `Finished_Good.recordType-meta.xml` creates a **new subscriber RT** instead of updating the managed one
- File must be named `ohfy__Finished_Good.recordType-meta.xml` with `<fullName>ohfy__Finished_Good</fullName>`
- The `sobject describe` shows two RTs with the same name — check `NamespacePrefix` to distinguish
- Subscriber RT has `available=False`; managed RT has `available=True`

### Category Crosswalk Pattern (ROS2, 2026-04-14)
- VIP `GenericCat3` values sometimes match Ohanafy picklist values exactly (e.g., "Flavored Vodka")
- Some VIP codes are NOT valid picklist values (e.g., "GENERIC VOL") — need a `CATEGORY_MAP` crosswalk
- GenericCat3 serves dual purpose: Item_Type name AND Category value — mapping must happen at Category assignment, NOT on the source field

### Managed Depletion Fields Don't Exist in ROS2 (2026-04-14)
- `ohfy__Net_Amount__c` and `ohfy__Quantity__c` are documented in knowledge base but DO NOT EXIST in ROS2 sandbox
- `ohfy__Type__c` EXISTS but is a restricted picklist (Cold Box, Draft Line, Menu, Shelf) — NOT transaction types like `Sale`
- Created custom unmanaged `VIP_Net_Amount__c` (Currency 16,2) = Qty × NetPrice for revenue reporting
- **Always verify managed fields via `sf sobject describe` before assuming they exist** — knowledge base may reflect a different org version

### Supplier-as-Config Pattern (ROS2, 2026-04-14)
- Supplier identity comes from customer config JSON (`supplier` block), NOT prompted per-run
- Phase 0 creates Supplier Account before all other phases; external ID: `SUP:{supplierCode}`
- Different customers have different suppliers — config-driven, not hardcoded

### Distributor Account + Contact from DISTDA (ROS2, 2026-04-14)
- Script 03 creates Account (Customer RT) + Contact + Location from DISTDA (not just Location)
- Distributors are the supplier's Customers; external IDs: `DST:{DistId}`, `CON:{DistId}:DIST`
- Contact creation is blocked by AccountTriggerMethods cascade (same root cause)

### Stock_UOM_Sub_Type__c Validation (ROS2, 2026-04-13)
- Managed validation rule requires `ohfy__Stock_UOM_Sub_Type__c` when `ohfy__Packaging_Type__c` is set on Finished Goods
- Script 04 (ITMDA enrichment) hits this; Script 02 (ITM2DA) does not

### Placement__c is the Correct Object (ROS2, 2026-04-10)
- Use `ohfy__Placement__c` (managed, 59+ fields) for Account x Item aggregation
- NOT `Distributor_Placement__c` (stale reference in older docs)
- NOT `Account_Item__c` (exists in source-index but 0 deployed fields)
- Master-detail fields (Account__c, Item__c) are create-only — set via `__r` relationship syntax

### VIP Data is Depletions, Not Invoices (2026-04-10)
- VIP SLSDA = distributor→retailer depletions → `Depletion__c` + `Placement__c`
- Invoice__c is for supplier→distributor billing — different data source, NOT from VIP files

### Supplier vs Distributor Perspective (2026-04-10)
- Account mappings depend on customer role in supply chain
- Supplier (e.g., ROS): Distributors = Customers (RT: Customer), Retailers = Distributed Customers
- ClassOfTrade 06/07/50 = Distributors; all others = Retailers

## Operational Context

### Data Load Procedure
1. Verify org connection: `sf org display --target-org <alias>`
2. Purge existing data: `bash purge-vip-data.sh --dist-id <ID> --include-references --execute`
3. Verify Transformation_Setting__c exists (required for depletions)
4. Run pipeline: `node e2e-sandbox-runner.js --dist-id <ID> --file-date <YYYY-MM-DD>`
5. Verify: SOQL count queries for all 14 object types

### Key Config
- E2E runner: `integrations/vip-srs/scripts/e2e-sandbox-runner.js`
- Customer config: `integrations/vip-srs/config/shipyard.json`
- Purge utility: `integrations/vip-srs/scripts/purge-vip-data.sh`
- Test fixtures: `integrations/vip-srs/tests/fixtures/`

## Related Skills

- **ohfy-core-expert** — Salesforce objects (Account, Product2, Depletion__c, Placement__c, etc.)
- **tray-expert** — Tray.io workflows for data orchestration
- **ohfy-oms-expert** — Order management context

## Delegates To

- **ohfy-core-expert** — SF data model questions
- **tray-expert** — Workflow patterns and Tray architecture
- **salesforce-composite** — API integration patterns
