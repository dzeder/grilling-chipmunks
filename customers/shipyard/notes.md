# Shipyard Brewing Company — Notes

Running notes from debugging sessions, design decisions, and gotchas.

<!-- Add entries with dates. Most recent first. -->

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
