# CMDT Trigger Bypass Packages

Subscriber-override `ohfy__Trigger_Configuration__mdt` records used to sidestep the
`AccountTriggerMethods missing class` blocker during bulk VIP loads in ROS2.

## Packages

| Dir | Purpose | Effect |
|-----|---------|--------|
| `bypass/` | Pre-load: disable Account After_Update managed trigger methods | `Is_Bypassed__c = true` on `Offline_Update` and `Update_Invoices` |
| `restore/` | Post-load: re-enable them | `Is_Bypassed__c = false` on the same two records |

Only `ohfy__Is_Bypassed__c` is set — including managed fields
(`Method_Name__c`, `Trigger_Context__c`, `sObject_Trigger__c`) triggers
`Cannot modify managed object` deploy errors.

## Deploy

```bash
# enable bypass (before bulk ops)
sf project deploy start --metadata-dir integrations/vip-srs/cmdt/bypass/ --target-org <alias>
# …wait ~8 batches for cache propagation, or sleep 30s…
# run the load
# …
# restore (after bulk ops)
sf project deploy start --metadata-dir integrations/vip-srs/cmdt/restore/ --target-org <alias>
```

## Which CMDT records are toggled

Found via `SELECT DeveloperName, MasterLabel, ohfy__Method_Name__c,
ohfy__sObject_Trigger__r.DeveloperName, ohfy__Trigger_Context__r.DeveloperName,
ohfy__Is_Bypassed__c FROM ohfy__Trigger_Configuration__mdt
WHERE ohfy__sObject_Trigger__r.DeveloperName = 'Account'`:

| DeveloperName | Method | Context | Toggled |
|---|---|---|---|
| Offline_Update | offlineUpdate | After_Update | YES |
| Update_Invoices | updateInvoices | After_Update | YES |
| Offline_Creation | offlineCreation | After_Insert | no |
| Set_Lost_Placement_Days | setLostPlacementDays | Before_Insert | no |
| Set_Offline_Record_Type | setOfflineRecordType | Before_Insert | no |

After_Insert and Before_Insert methods are left alone — the
`AccountTriggerMethods missing class` error surfaces on Account UPDATE, not
insert (`known-issues.md`).

## Cache propagation delay

After deploy, the first ~8 API batches may still use cached CMDT values
(Salesforce platform behavior). Runner/orchestrator accept early batch errors
via `allOrNone=false`.
