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

## Next Up

### Phase 5: End-to-End Sandbox Validation
- [ ] Run Script 01 output through real SF Composite API against ROS2
- [ ] Run Scripts 02-03 (reference data must exist before enrichment)
- [ ] Run Scripts 04-05 (enrichment — depends on items + chains existing)
- [ ] Run Scripts 06-08 (inventory + depletions + allocations — depends on items, locations, accounts)
- [ ] Verify record counts via SOQL: `SELECT COUNT(Id) FROM ohfy__Depletion__c WHERE VIP_External_ID__c LIKE 'DEP:FL01:%'`
- [ ] Verify stale cleanup queries (Script 09) return expected records after multi-file run

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
