# Shipyard Brewing Company — Notes

Running notes from debugging sessions, design decisions, and gotchas.

<!-- Add entries with dates. Most recent first. -->

## 2026-04-13 — E2E Data Load + Three Enhancements

Re-ran full VIP SRS E2E pipeline against ROS2 sandbox with `--file-date 2026-04-13`. Implemented three enhancements and fixed the Inventory duplicate validation blocker.

**Prerequisites:**
- Finished Good RT exists (`012am0000050BVKAA2`)
- Transformation_Setting__c recreated: Each → Fluid Ounce(s), Volume, Beer (`a1FWF000001SLXB2A4`)

**Enhancements implemented:**
1. **Placement fields:** Added `Is_New_Placement__c = true` + `Lost_Placement_After_Days__c = 60` to Script 07b. Formula fields auto-compute: Days_Since_Last_Order (10), Lost_Placement_Date (2026-06-02).
2. **Account rep codes:** Deployed `VIP_Salesman1__c` + `VIP_Salesman2__c` (Text(8)) to ROS2. Mapped in Script 05, filtering `999`/`HOUSE`. These are distributor rep codes (ROSM1/ROSM2), NOT supplier reps.
3. **Inventory fix:** Three-layer pre-query pattern (see below).

**Final results (after all fixes):**

| Phase | Object | Count | Status |
|-------|--------|-------|--------|
| 1 | Account (Chains CHN:*) | 12 | ✅ create / ❌ update (AccountTrigger) |
| 1 | Item (ITM:*) | 63 | ✅ |
| 1 | Location (LOC:*) | 12 | ✅ |
| 2 | Item Enrichment | 95 | ✅ |
| 2 | Account (Outlets ACT:*) | 27 | ✅ VIP_Salesman1__c populated |
| 2 | Contact (CON:*) | 25 | ✅ |
| 3 | Inventory stamp | 264 | ✅ VIP_External_ID__c batch-stamped |
| 3 | Inventory (IVT:*) | 12 | ✅ updated via PATCH-by-ID |
| 3 | Inventory History (IVH:*) | 485 | ✅ |
| 3 | Inventory Adjustments (IVA:*) | 5 | ✅ |
| 4 | Depletion (DEP:*) | 40 | ✅ |
| 4 | Placement (PLC:*) | 40 | ✅ Is_New_Placement + Lost_Placement_After_Days |
| 4 | Allocation (ALC:*) | 23 | ✅ |

- **Phase 3+4 total: 612 succeeded, 0 failures**
- Phase 1 Chain Banner UPDATES fail (AccountTriggerMethods — pre-existing known issue). Creates work fine.

**Inventory fix: Three-layer pre-query pattern**
The managed package has a "Duplicate Record Blocked" validation rule on Inventory__c. ROS2 has 264 pre-existing records. Fix:
1. **Lazy pre-query** — runs after Phase 1 stamps VIP_External_ID__c on Items (not at startup, where it finds 0)
2. **Batch-stamp** — PATCHes VIP_External_ID__c on all 264 existing records so History/Adjustments can reference them
3. **Master-detail strip** — removes Item__r/Location__r from PATCH body (read-only on update)

**Key decision: ohfy__Placement__c IS the right object**
- Managed object with 59+ fields including formula fields for CSO features (new placement detection, reorder alerts, volume tracking)
- `ohfy__Account_Item__c` exists in source-index but has 0 deployed fields in ROS2 — not the right choice
- CSO rep/territory/commission features (Territory__c, Goal__c, Goal_Tracking__c) exist as managed objects — may be leveraged later

## 2026-04-13 — CSO Requirements: Sales Rep Tracking & Commission System

Email from ROS chief sales officer outlining core requirements for a rep tracking and commission system built on VIP data.

- **Rep territory management:** Reps assigned by geography (counties and zip codes). New placements and ongoing monthly sales tracked within those defined territories.
- **New placement detection:** Identify new points of distribution (accounts that did not exist before a defined timeline), classify as new sellers, and assign to the appropriate rep.
- **Data source:** Reps do not place orders — distributors handle all ordering and fulfillment. All sales data originates from distributor activity accessed through VIP SRS. This is the sole data source for tracking and reporting.
- **Commission reporting:** Must support flexible commission structures:
  - Case volume-based (set case targets)
  - Revenue per case based on distributor FOB pricing (not retail)
- **Sales opportunity alerts:**
  - Cross-sell: identify accounts that bought one product but not another (e.g., bought Shipyard but not Ice Pik)
  - Reorder alerts: flag accounts that purchase but do not reorder within a 60-day window
- **Takeaway:** This maps directly to Placement__c (new distribution tracking), Depletion__c (monthly sales by rep territory), and a new rep/territory assignment model. Commission structures imply a custom object or flexible metadata. The 60-day reorder alert is a time-based flow or scheduled job against Placement__c.Last_Purchase_Date__c.

## 2026-04-10 — Depletions, Placements, and File Date Logic (evening session)

- Loaded curated 25-row SLSDA fixture with all supporting data (accounts, chains, items, transformation settings)
- **Item lookup filter chain discovered:** Depletion__c.Item__c has a non-optional filter requiring Finished Good RT + Type__c + UOM__c + Packaging_Type__c + Transformation_Setting__c. All 5 prerequisites must be met or FIELD_FILTER_VALIDATION_EXCEPTION. This was undocumented.
- Created Transformation_Setting__c (Each → Fluid Ounce(s), Volume, Spirit) to satisfy the filter
- Set all 13 items to Finished Good RT + UOM (US Count) + Packaging_Type (Each)
- 25 depletion rows → 15 unique records (deduplication via upsert across overlapping file date windows)
- **Built Placement__c integration (script 07b):**
  - Aggregates SLSDA by Account×Item → one placement per pair
  - External ID: `PLC:{DistId}:{AcctNbr}:{SuppItem}` (changed from spec's DPL: per-invoice-line format)
  - Maps: First_Sold_Date__c, Last_Sold_Date__c, Last_Purchase_Date__c, Last_Purchase_Quantity__c, Last_Invoice_Price__c, Is_Active__c
  - Master-detail fields (Account__c, Item__c) are create-only — set via relationship syntax
  - Deployed VIP_External_ID__c + VIP_File_Date__c on Placement__c
- **Fixed VIP_File_Date__c semantics:** File date = date of pipeline run (today), not derived from file contents. FromDate/ToDate already capture the file's reporting window. Stale cleanup needs "when was this record last refreshed" = run date.
- Updated shared/constants.js PREFIX.PLACEMENT from DPL to PLC
- Updated shared/external-ids.js placementKey() to match implementation (3 components, not 5)
- All sandbox data cleared after verification

## 2026-04-10 — Account Model Refinement (afternoon session)

- ROS is a supplier → clarified the account classification model:
  - **Distributors/Wholesalers** (ClassOfTrade 06/07/50): Type=Customer, RT=Customer, Retail_Type=Distributor, no Premise_Type
  - **Retailers** (all other ClassOfTrade): Type=Distributed Customer, RT=Distributed_Customer, Retail_Type from ChainStatus (Chain/Independent), Premise_Type from crosswalk
  - **Chain Banners** (SRSCHAIN): Type=Chain Banner, RT=Chain_Banner, Is_Chain_Banner=true — thin parent records (name only), outlets link via Chain_Banner__r
- All accounts: AccountSource='VIP SRS', Legal_Name defaults to Name, Shipping=Billing address
- Ohanafy engineering fixed record type assignment same day: Customer + Chain_Banner RTs now available to integration user
- AccountTriggerMethods still missing — inserts work, updates 100% fail. **Hard blocker for daily sync / upsert idempotency.**
- Purge script `--no-prompt` flag removed (not supported by sf CLI)
- Core skill files corrected: Account External_ID namespace, Location field name, API versions v58→v62
- All VIP data purged from sandbox after verification

## 2026-04-10 — E2E Sandbox Validation

- Ran all 8 transform scripts against ROS2 sandbox via Composite API
- 54 records created across 8 objects (CHN:10, ACT:9, CON:6, ITM:13, LOC:1, IVT:2, IVH:10, ALC:3)
- Depletions (DEP) skipped — sample SLSDA references accounts not in the 10-row OUTDA fixture (data gap, not script bug)
- Three script fixes needed:
  1. `02-itm2da`: `Packaging_Type__c` is a restricted picklist gated by record type. Moved human-readable size to `Packaging_Type_Short_Name__c` (text). Type__c + Packaging_Type__c deferred until integration user gets Finished Good record type.
  2. `03-distda`: Field is `ohfy__Type__c` not `ohfy__Location_Type__c`. Also `Location_Code__c` max 5 chars — use raw dist ID, not prefixed key.
  3. `05-outda`: `ohfy__Market__c` restricted picklist values don't match VIP crosswalk labels. Full remap to actual org values (e.g., "Bar" → "Bars/Clubs/Taverns", "Liquor Store" → "Liquor"). 14 of 46 VIP codes have no SF match.
- AccountTriggerMethods missing in managed package — blocks Account AfterUpdate. First insert works, re-upsert fails. Needs Ohanafy fix.
- Created `e2e-sandbox-runner.js` (phases 1-4, dry-run mode, per-phase execution)
- Created `purge-vip-data.sh` (dry-run confirmed all 54 records detected)
- Synced CLASS_OF_TRADE crosswalk between `shared/constants.js` and script 05

## 2026-04-09 — Project kickoff

- VIP SRS integration is the first real project built in the daniels-ohanafy monorepo
- Handoff doc produced in yangon workspace with 11 days of sample data
- Building fresh from spec + pattern library (not adapting existing VIP_Depletions_1GP scripts)
- Key design decision: immutable external IDs using colon-delimited prefix format (CHN:, ACT:, ITM:, etc.)
- Supplier code in sample data: `ARG`
- Data model uses `Placement__c` (not `Distributor_Placement__c` as referenced in some older docs)
