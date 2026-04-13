# VIP SRS Integration Roadmap

## Completed

### Phase 0: Foundation
- [x] Customer directory (`customers/shipyard/`, `customers/shipyard-ros2/`)
- [x] Integration directory structure (`integrations/vip-srs/`)
- [x] Connected Shipyard ROS2 sandbox (alias: `shipyard-ros2-sandbox`)
- [x] Copied handoff spec + sample data fixtures from yangon workspace

### Phase 1: Reference Data Scripts
- [x] `shared/` modules (constants, external-ids, filters, transforms)
- [x] `01-srschain-chains.js` — Account (Chain Banners)
- [x] `02-itm2da-items.js` — Item_Line__c + Item_Type__c + Item__c
- [x] `03-distda-locations.js` — Location__c

### Phase 2: Enrichment Scripts
- [x] `04-itmda-enrichment.js` — Item__c distributor SKU enrichment
- [x] `05-outda-accounts.js` — Account (Outlets) + Contact (Buyers)

### Phase 3: Inventory + Transaction Scripts
- [x] `06-invda-inventory.js` — Inventory__c + Inventory_History__c + Inventory_Adjustment__c
- [x] `07-slsda-depletions.js` — Depletion__c (VIP SLSDA = distributor-to-retailer depletions)
- [x] `08-ctlda-allocations.js` — Allocation__c

### Phase 4: Cleanup + Summary
- [x] `09-cleanup-stale.js` — SOQL generators for stale record deletion (5 objects including Placement__c)
- [x] `10-run-summary.js` — Aggregates per-script results

### ROS2 Sandbox Field Deployment
- [x] 24 custom fields deployed across 8 objects (Depletion, Placement, Location, Inventory, History, Adjustment, Allocation, Contact)
- [x] Admin profile FLS included in deploy package
- [x] VIP_SRS_Integration Permission Set created and deployed
- [x] Fields verified queryable via SOQL and upsertable via REST API
- [x] Deploy package: `customers/shipyard-ros2/deploy-v2/`

### Test Suite
- [x] Test runner (`tests/test-runner.js`) with CSV parsing
- [x] 8 fixture files from yangon sample data
- [x] All 8 transform scripts pass (48/48 assertions, 0 failures, target dist: FL01)
- [x] Scripts 09-10 verified with mock inputs

### Sandbox Utilities
- [x] `purge-vip-data.sh` — deletes all VIP-created records from sandbox (dry-run by default, reverse dependency order, optional `--dist-id` filter)

### Phase 5: End-to-End Sandbox Validation (2026-04-10)
- [x] `e2e-sandbox-runner.js` — Node.js runner that transforms CSV fixtures and POSTs Composite API batches
- [x] Phase 1: Chains (10 Account CHN:*), Items (9 ITM:* + 3 Item Lines + 2 Item Types), Location (1 LOC:FL01)
- [x] Phase 2: Item enrichment (8), Outlets (9 Account ACT:*), Contacts (6 CON:*)
- [x] Phase 3: Inventory (2 IVT:*), Inventory History (10 IVH:*)
- [x] Phase 4: Allocations (3 ALC:*) — Depletions skipped (SLSDA sample references accounts not in OUTDA fixture)
- [x] Verified record counts via SOQL: 54 total records across 8 objects
- [x] Purge script dry-run confirmed all 54 records detected for cleanup
- [x] **Script fixes applied during E2E:**
  - `02-itm2da`: `Packaging_Type__c` → `Packaging_Type_Short_Name__c` (text field); deferred Type__c + Packaging_Type__c pending record type assignment
  - `03-distda`: `Location_Type__c` → `Type__c`; `Location_Code__c` stores raw dist ID (max 5 chars, not prefixed key)
  - `05-outda`: Full Market crosswalk remapped to match `ohfy__Market__c` restricted picklist values (also synced to shared/constants.js)
- [x] Verify stale cleanup queries (Script 09) return expected records after multi-file run
  - Added Placement__c as 5th cleanup target (simplified query — file date only, no from/to window)
  - Added Placement__c to purge-vip-data.sh
  - Verified against ROS2 sandbox: load with file-date 2026-04-08 → stale queries detect all records; re-load with 2026-04-09 → stale counts drop to 0
  - Note: Each file type has its own from/to window (SLSDA=daily, CTLDA=monthly) — Tray workflow calls Script 09 per file type with matching dates

### Phase 5b: Account Model Refinement (2026-04-10)
- [x] **Supplier perspective clarified:** ROS is a supplier. Distributors/wholesalers = Customers (who the supplier sells to). Retailers = Distributed Customers (who the supplier's customer sells to).
- [x] Script 05 split: Distributors (ClassOfTrade 06/07/50) vs Retailers (all others) with different record types, account types, and field mappings
- [x] Account record types verified and applied:
  - Chain Banners → `Chain_Banner` RT + `Is_Chain_Banner__c = true` + Type = "Chain Banner"
  - Distributors → `Customer` RT + Type = "Customer" + `Retail_Type__c = 'Distributor'`
  - Retailers → `Distributed_Customer` RT + Type = "Distributed Customer" + `Retail_Type__c` from ChainStatus
- [x] All accounts: `AccountSource = 'VIP SRS'`, `Legal_Name__c` defaults to Name, Shipping = Billing address
- [x] Chain Banner RT (`012am0000050BVYAA2`) and Customer RT (`012am0000050BVXAA2`) assigned to integration user (fixed by Ohanafy engineering)
- [x] Script 01 chains: `Type: 'Retail Chain'` → `'Chain Banner'` (actual picklist value)
- [x] **Account updates still blocked** by `AccountTriggerMethods` — inserts work, re-upserts fail. Hard blocker for daily sync.
- [x] Purge script fixed: removed `--no-prompt` flag (not supported by `sf data delete record`)
- [x] Core skill files updated: Account `External_ID__c` → `ohfy__External_ID__c`, Location `Location_Type__c` → `Type__c`, all API versions `v58.0` → `v62.0`

### Phase 5c: Depletions + Placements E2E (2026-04-10)
- [x] Created `slsda-25.csv` — curated 25-row fixture with matching supporting data across all phases (accounts, chains, items)
- [x] Created `outda-depletion-deps.csv` — 5 OUTDA accounts referenced by the 25 depletions
- [x] Loaded chain banner CHN:0000091321 (ABC Discount Wine & Liquor) — referenced by account 13791
- [x] Resolved Item lookup filter chain on Depletion__c.Item__c:
  - Items need Finished Good record type + `Type__c = 'Finished Good'` + `UOM__c` + `Packaging_Type__c` (dependent picklist)
  - Also requires `Transformation_Setting__c` record linking the Packaging_Type to a Volume UOM
  - Created Transformation_Setting__c (Each → Fluid Ounce(s), Volume, Spirit) manually
  - Set all 13 items: Finished Good RT + Type + UOM (US Count) + Packaging_Type (Each)
- [x] 25 depletions → 15 unique records (deduplication via upsert across overlapping file date windows)
- [x] `07b-slsda-placements.js` — new script, aggregates SLSDA invoice lines into Account×Item placements
  - External ID: `PLC:{DistId}:{AcctNbr}:{SuppItem}` (one per Account×Item, not per transaction)
  - Master-detail fields (Account__c, Item__c) are create-only — set via `__r` relationship syntax
  - Maps: First_Sold_Date__c, Last_Sold_Date__c, Last_Purchase_Date__c, Last_Purchase_Quantity__c, Last_Invoice_Price__c, Is_Active__c
  - 25 rows → 8 unique placements
- [x] Deployed `VIP_External_ID__c` + `VIP_File_Date__c` on Placement__c (field + permset + profile FLS)
- [x] **VIP_File_Date__c = date of run** (not derived from file contents). FromDate/ToDate capture the file's reporting window. File date is for stale cleanup: "this record was present in the pipeline run on this date."
- [x] Updated e2e-sandbox-runner.js: placements wired into pipeline (Phase 4), fixtures switched to slsda-25.csv
- [x] All phase 4 objects (Depletions, Placements, Allocations) verified with correct file date

### Phase 5d: Quick Wins + Cleanup Hardening (2026-04-10)
- [x] Script 07 (depletions): Set `ohfy__Type__c = 'Sale'` — depletions now visible in Type-filtered reports
- [x] Script 08 (allocations): Set `ohfy__End_Date__c` (last day of month) + `ohfy__Location__r` (distributor warehouse lookup)
- [x] Script 05 (accounts): Set `ohfy__Fulfillment_Location__r` on retailer accounts (links to `LOC:{DistId}`)
- [x] Script 06 (inventory): Set `ohfy__Status__c = 'Complete'` on Inventory_Adjustment__c records
- [x] Script 09 (cleanup): Added `countQuery` (SELECT COUNT()) per target for sanity check — Tray workflow should compare stale count vs upsert count before deleting; if stale > upserted, skip delete (possible truncated/partial file)
- [x] **Key decision documented:** Invoice__c/Invoice_Item__c is NOT built from VIP data. VIP SLSDA = distributor→retailer depletions (Depletion__c + Placement__c). Invoice objects are for supplier→distributor invoicing — a separate data source entirely.

### Phase 5e: Item_Line / Item_Type Duplicate Fix (2026-04-13)
- [x] Root cause: Script 02 used Name-only creates with no external ID — re-runs without Tray lookup maps created duplicates
- [x] Added `VIP_External_ID__c` (Text 255, unique, external ID) + `VIP_File_Date__c` (Date) to both `Item_Line__c` and `Item_Type__c`
- [x] External ID formats: `ILN:{BrandDesc}` for Item_Line, `ITY:{GenericCat3}` for Item_Type
- [x] Script 02: replaced Name-only create with Composite API PATCH upsert by external ID (same pattern as Item__c)
- [x] Script 09: added Item_Line__c and Item_Type__c to cleanup targets with `perDistributor: false` flag (global reference data, not scoped by distributor)
- [x] Updated permset + Admin profile FLS for 4 new fields
- [x] Added `ITEM_LINE: 'ILN'` and `ITEM_TYPE: 'ITY'` prefixes to shared/constants.js + external-ids.js

## Next Up

### Phase 6: Tray.io Project Build
- [ ] Create Tray project with daily schedule trigger
- [ ] SFTP connector: pickup + decompress .gz files
- [ ] CSV parser step per file type
- [ ] Script connectors wired to each transform script (01-10, including 07b)
- [ ] SF Composite API connector for each batch output
- [ ] Phase-sequenced execution (reference data before enrichment before transactions)
- [ ] Error handling + notification connector (Slack/email)
- [ ] Export project JSON to `dzeder/daniels-ohanafy-artifacts`

### Phase 7: Multi-Day Sequence Test
- [ ] Process 3 consecutive days of sample data (e.g., N20260404, N20260407, N20260408)
- [ ] Verify upsert idempotency (re-running same day = no duplicates)
- [ ] Verify stale cleanup (older file date records deleted within same period)
- [ ] Verify record counts match expected per spec

### Phase 8: Production Readiness
- [ ] **Fix AccountTriggerMethods** — managed package missing class blocks Account AfterUpdate (see `customers/shipyard/known-issues.md`)
- [ ] **Assign Finished Good record type** to integration user on Item__c — enables Type__c + Packaging_Type__c fields
- [ ] Re-enable Type__c + Packaging_Type__c in Script 02 after record type is assigned
- [ ] Make `ohfy__VIP_External_ID__c` unique on Item__c (managed package change — Daniel/Ohanafy)
- [ ] Deploy custom fields to production ROS2 org (using same deploy-v2 package with FLS)
- [ ] Create production Tray project (clone sandbox, update auth + schedule)
- [ ] Configure SFTP credentials in Tray
- [ ] Monitoring: Tray execution alerts, SF record count dashboards

## Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| **Depletion__c** (not Invoice__c) for SLSDA | VIP data = distributor→retailer sales (depletions), not brewery→distributor invoices |
| **Unmanaged VIP_External_ID__c** on each object | Managed `ohfy__External_ID__c` exists on some objects but using consistent unmanaged fields for VIP-specific upsert keys |
| **ohfy__Quantity_On_Hand__c** for inventory | Cases_On_Hand__c and Units_On_Hand__c are formula/rollup fields (not writable) |
| **ohfy__Stamped_Date__c** for history | Inventory_Date__c is non-updatable |
| **Permission Set** for FLS | Easier to assign to any integration user than modifying every profile |
| **Deploy package includes Admin.profile FLS** | SF Metadata API silently fails without it in subscriber orgs |
| **Placement__c keyed by Account×Item** (not per invoice line) | One placement per distributor+account+item. Aggregated from SLSDA rows: earliest/latest sold dates, latest price/qty. External ID: `PLC:{DistId}:{AcctNbr}:{SuppItem}` |
| **No Invoice__c from VIP data** | VIP SLSDA = distributor→retailer depletions (Depletion__c + Placement__c). Invoice__c is for supplier→distributor invoicing — different data source, not from VIP files |
| **VIP_File_Date__c = date of pipeline run** | Not derived from file contents. FromDate/ToDate capture the file's reporting window. File date stamps when a record was last refreshed, enabling stale cleanup. |

## Gotchas

1. **SF Metadata API + managed package objects:** Deploys report "Succeeded" but fields aren't API-accessible unless Admin profile FLS is included in the same package. Always deploy fields + profiles together.
2. **Master-detail fields are set on create only:** Customer__c on Depletion, Item__c on Inventory, etc. Use `__r` relationship syntax in Composite API body, not `__c` field.
3. **Namespace prefix:** All managed package fields need `ohfy__` prefix. Unmanaged custom fields (VIP_*) do NOT get the prefix.
4. **Composite API batch limit:** 25 subrequests max per batch. Scripts chunk accordingly.
5. **DistId filtering:** Scripts filter rows by `targetDistId`. Test fixtures use `FL01`.
6. **Restricted picklists need exact org values:** `ohfy__Market__c`, `ohfy__Packaging_Type__c` are restricted picklists. The script crosswalk must use exact values from the target org — describe the field first. Generic/human-friendly names (e.g., "Bar") will fail if the org uses a different label (e.g., "Bars/Clubs/Taverns").
7. **Record type gates picklist values:** `ohfy__Packaging_Type__c` on Item__c accepts different values per record type. The integration user must have the "Finished Good" record type assigned, and the Composite body must include `RecordTypeId`. Without it, the default Master record type rejects valid Finished Good picklist values.
8. **Location_Code__c max length = 5:** The `ohfy__Location_Code__c` field is only 5 characters. Store the raw dist ID (e.g., `FL01`), not the prefixed external key (`LOC:FL01`).
9. **AccountTriggerMethods missing in ROS2:** The managed package trigger `ohfy.AccountTrigger` fires on AfterUpdate but the `AccountTriggerMethods` class is not found. First insert succeeds; re-upsert (update) fails. This is a managed package configuration issue, not a script bug. **Hard blocker for production daily sync.**
10. **External ID field names vary by object:** Account uses `ohfy__External_ID__c` (managed), Contact uses `External_ID__c` (unmanaged custom), most VIP objects use `VIP_External_ID__c` (unmanaged). Always check the field name per object — don't assume.
11. **Supplier vs Distributor perspective matters:** ROS is a supplier. OUTDA accounts split into two types: distributors/wholesalers (ClassOfTrade 06/07/50) are the supplier's **Customers** (record type Customer); retailers are the distributor's customers → **Distributed Customers**. This affects record type, account type, retail type, and premise type mappings.
12. **SRSCHAIN records are chain banners** even if names seem small (e.g., "Horizon Market"). They're parent accounts that OUTDA outlets link to via `Chain_Banner__r`. The detail (address, market, etc.) lives on the outlets, not the chains.
13. **AccountSource 'VIP SRS' not in picklist:** The field is not restricted so the API accepts it, but the value won't appear in picklist dropdowns until added via Setup.
14. **Item lookup filter chain on Depletion__c.Item__c:** The lookup filter (`optionalFilter: false`) requires the Item to have: (a) Finished Good record type, (b) `Type__c = 'Finished Good'`, (c) `UOM__c` set (e.g., 'US Count'), (d) `Packaging_Type__c` set (dependent on UOM, e.g., 'Each'), and (e) a `Transformation_Setting__c` record linking the Packaging_Type to a Volume UOM (e.g., Each → Fluid Ounce(s)). Missing any of these causes `FIELD_FILTER_VALIDATION_EXCEPTION`. Script 02 must ensure items meet all prerequisites before depletions can load.
15. **Item_Line__c and Item_Type__c need external IDs for upsert:** These lookup objects use `VIP_External_ID__c` with formats `ILN:{BrandDesc}` and `ITY:{GenericCat3}`. Without external IDs, re-running Script 02 creates duplicates. The Tray workflow should still pre-query and pass `existingItemLines`/`existingItemTypes` maps for efficiency, but the upsert provides a safety net.
16. **Placement__c master-detail fields are create-only:** `ohfy__Account__c` and `ohfy__Item__c` are master-detail and can only be set on initial create (updateable=false). Use `__r` relationship syntax in Composite API body. On subsequent upserts, the API silently ignores these fields — the record stays parented to the original Account×Item.
