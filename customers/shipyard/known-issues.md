# Shipyard Brewing Company — Known Issues

Running log of known issues, workarounds, and resolutions for this customer.

## Open Issues

### AccountTriggerMethods missing in managed package (ROS2)
- **Severity:** High
- **Affected area:** Integration — any Account DML
- **Reported:** 2026-04-10
- **Workaround:** First insert succeeds; only AfterUpdate (re-upsert) fails. Avoid re-upserting Accounts in the same run. In Tray, handle allOrNone=false and log these errors.
- **Description:** `ohfy.AccountTrigger` AfterUpdate fires `ServiceLocator.ServiceLocatorException: Invalid implementation class: AccountTriggerMethods`. The managed package class `AccountTriggerMethods` is not found. This blocks Account updates but not inserts. Ohanafy engineering needs to either deploy the missing class or update the ServiceLocator config in ROS2.

### Item lookup filter chain on Depletion__c.Item__c
- **Severity:** High
- **Affected area:** Integration — Depletion__c upserts
- **Reported:** 2026-04-10
- **Workaround:** Manually set all 5 prerequisites on each Item before loading depletions. Script 02 should be updated to handle this automatically.
- **Description:** `Depletion__c.ohfy__Item__c` has a non-optional lookup filter requiring the Item to have ALL of: (1) Finished Good record type, (2) `Type__c = 'Finished Good'`, (3) `UOM__c` set (e.g., 'US Count'), (4) `Packaging_Type__c` set (dependent on UOM, e.g., 'Each'), and (5) a `Transformation_Setting__c` record linking the Packaging_Type to a Volume UOM. Missing ANY prerequisite causes `FIELD_FILTER_VALIDATION_EXCEPTION`. The dependency chain is: RecordType → Type__c → UOM__c → Packaging_Type__c (dependent picklist) → Transformation_Setting__c. This was undocumented and discovered during E2E testing. For production: Script 02 needs to ensure items meet all prerequisites, and Transformation_Setting__c records need to exist for all item packaging types.

### ~~Integration user missing Finished Good record type on Item__c (ROS2)~~ RESOLVED
- **Severity:** Medium
- **Resolved:** 2026-04-10
- **Description:** The integration user (`integrations@ohanafy.ros.test`) did not have the "Finished Good" record type assigned on `ohfy__Item__c`. Fixed by manually assigning RecordTypeId during E2E testing. For production: assign the Finished Good record type to the integration user's profile via Setup.

### ~~Integration user missing Customer record type on Account (ROS2)~~ RESOLVED
- **Severity:** Medium
- **Resolved:** 2026-04-10
- **Description:** Customer (`012am0000050BVXAA2`) and Chain_Banner (`012am0000050BVYAA2`) record types were not assigned to integration user. **Fixed by Ohanafy engineering same day.** Both record types now available.

### Contact DML blocked by AccountTriggerMethods cascade (ROS2)
- **Severity:** High
- **Affected area:** Integration — all Contact inserts (Script 05, OUTDA buyers)
- **Reported:** 2026-04-13
- **Workaround:** None — Contact inserts cannot succeed until AccountTriggerMethods is fixed. Skip Contact loading or accept 100% failure on contacts.
- **Description:** Contact inserts trigger `ohfy.ContactTrigger` AfterInsert, which performs a DML update on the parent Account. That Account update fires `ohfy.AccountTrigger` AfterUpdate, which hits the same `ServiceLocatorException: Invalid implementation class: AccountTriggerMethods`. This means ALL Contact DML is blocked in ROS2, not just Account re-upserts. The cascade path is: Contact INSERT → ContactTrigger AfterInsert → Account UPDATE → AccountTrigger AfterUpdate → AccountTriggerMethods missing. This is the same root cause as the Account update blocker but with a wider blast radius.

### Stock_UOM_Sub_Type__c validation rule on Item enrichment (ROS2)
- **Severity:** Medium
- **Affected area:** Integration — Item enrichment (Script 04, ITMDA)
- **Reported:** 2026-04-13
- **Workaround:** Skip `Packaging_Type__c` during enrichment, or set `Stock_UOM_Sub_Type__c` alongside it.
- **Description:** A managed validation rule requires `ohfy__Stock_UOM_Sub_Type__c` to be set when `ohfy__Packaging_Type__c` is present on Finished Good items (Error Code: 003). Script 04 (ITMDA enrichment) sets `Packaging_Type_Short_Name__c` but doesn't set `Stock_UOM_Sub_Type__c`, causing 1 item enrichment failure per run. Script 02 (ITM2DA) doesn't hit this because it sets `Packaging_Type__c` via a different code path. Need to either map `Stock_UOM_Sub_Type__c` from VIP data or skip the field in enrichment.

### AccountSource picklist missing 'VIP SRS' value
- **Severity:** Low
- **Affected area:** Integration — all Account upserts
- **Reported:** 2026-04-10
- **Workaround:** AccountSource is not a restricted picklist, so the API accepts 'VIP SRS' as a value. However, it won't appear in picklist dropdowns until added.
- **Description:** The VIP SRS integration sets `AccountSource = 'VIP SRS'` for traceability. The value doesn't exist in the org's picklist. Recommended: add 'VIP SRS' to the AccountSource picklist values via Setup > Object Manager > Account > Fields > Account Source.

### ~~Inventory "Duplicate Record Blocked" validation rule (ROS2)~~ RESOLVED
- **Severity:** High
- **Resolved:** 2026-04-13
- **Fix:** Three-layer pre-query pattern implemented in `e2e-sandbox-runner.js` + `06-invda-inventory.js`:
  1. **Lazy pre-query:** Runs after Phase 1 (not at startup) so Items have VIP_External_ID__c stamped. Queries existing Inventory by Item/Location relationships, builds VIP key → SF record ID map.
  2. **Batch-stamp:** PATCHes VIP_External_ID__c on ALL 264 existing Inventory records so History/Adjustment children can reference any of them by external ID.
  3. **Master-detail strip:** When PATCHing existing records by SF ID, removes `ohfy__Item__r` and `ohfy__Location__r` from body (master-detail, read-only on update).
- **Result:** 264 stamped, 12 inventory updated, 489 history created, 8 adjustments created — 0 failures.
- **For Tray (Phase 6):** Pre-query becomes a SOQL connector step before the Script 06 connector. Same pattern, Tray-native.

### ohfy__Market__c restricted picklist gaps
- **Severity:** Low
- **Affected area:** Integration — Account (Outlet) upserts
- **Reported:** 2026-04-10
- **Workaround:** 14 VIP Class of Trade codes map to `null` (skipped) because no matching picklist value exists. Premise_Type__c is still set.
- **Description:** The VIP SRS data has 46 Class of Trade values. The `ohfy__Market__c` restricted picklist only has 22 values. 14 VIP codes have no match (Military, Non-Retail, Retail Specialty, E-Commerce, Dollar Store, CBD/THC, School, Office, Hospital, Government, Tasting Room, Other On/Off Premise, Unassigned). These accounts are created but without a Market value. Could request Ohanafy add missing picklist values if needed.

## Resolved Issues

<!-- Move issues here when resolved. Add resolution date and what fixed it. -->

## Recurring Patterns

<!-- Issues that keep coming back. Document the pattern so agents recognize it faster. -->
