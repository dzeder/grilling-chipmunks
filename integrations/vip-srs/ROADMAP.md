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
- [x] `09-cleanup-stale.js` — SOQL generators for stale record deletion (4 objects)
- [x] `10-run-summary.js` — Aggregates per-script results

### ROS2 Sandbox Field Deployment
- [x] 22 custom fields deployed across 7 objects (Depletion, Location, Inventory, History, Adjustment, Allocation, Contact)
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
- [ ] Verify stale cleanup queries (Script 09) return expected records after multi-file run

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

## Next Up

### Phase 6: Tray.io Project Build
- [ ] Create Tray project with daily schedule trigger
- [ ] SFTP connector: pickup + decompress .gz files
- [ ] CSV parser step per file type
- [ ] Script connectors wired to each transform script (01-10)
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
