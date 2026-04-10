# Shipyard Brewing Company — Known Issues

Running log of known issues, workarounds, and resolutions for this customer.

## Open Issues

### AccountTriggerMethods missing in managed package (ROS2)
- **Severity:** High
- **Affected area:** Integration — any Account DML
- **Reported:** 2026-04-10
- **Workaround:** First insert succeeds; only AfterUpdate (re-upsert) fails. Avoid re-upserting Accounts in the same run. In Tray, handle allOrNone=false and log these errors.
- **Description:** `ohfy.AccountTrigger` AfterUpdate fires `ServiceLocator.ServiceLocatorException: Invalid implementation class: AccountTriggerMethods`. The managed package class `AccountTriggerMethods` is not found. This blocks Account updates but not inserts. Ohanafy engineering needs to either deploy the missing class or update the ServiceLocator config in ROS2.

### Integration user missing Finished Good record type on Item__c (ROS2)
- **Severity:** Medium
- **Affected area:** Integration — Item__c upserts
- **Reported:** 2026-04-10
- **Workaround:** Skip `ohfy__Type__c` and `ohfy__Packaging_Type__c` fields in upsert. Items are created without type classification.
- **Description:** The integration user (`integrations@ohanafy.ros.test`) does not have the "Finished Good" record type assigned on `ohfy__Item__c`. The `Packaging_Type__c` restricted picklist only accepts values valid for the Finished Good record type (e.g., "Each"). Without the record type assignment, setting either `Type__c = 'Finished Good'` or any `Packaging_Type__c` value fails. Fix: assign the Finished Good record type to the integration user's profile.

### ~~Integration user missing Customer record type on Account (ROS2)~~ RESOLVED
- **Severity:** Medium
- **Resolved:** 2026-04-10
- **Description:** Customer (`012am0000050BVXAA2`) and Chain_Banner (`012am0000050BVYAA2`) record types were not assigned to integration user. **Fixed by Ohanafy engineering same day.** Both record types now available.

### AccountSource picklist missing 'VIP SRS' value
- **Severity:** Low
- **Affected area:** Integration — all Account upserts
- **Reported:** 2026-04-10
- **Workaround:** AccountSource is not a restricted picklist, so the API accepts 'VIP SRS' as a value. However, it won't appear in picklist dropdowns until added.
- **Description:** The VIP SRS integration sets `AccountSource = 'VIP SRS'` for traceability. The value doesn't exist in the org's picklist. Recommended: add 'VIP SRS' to the AccountSource picklist values via Setup > Object Manager > Account > Fields > Account Source.

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
