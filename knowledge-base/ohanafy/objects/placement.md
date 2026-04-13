# ohfy__Placement__c

Account-by-Item tracking object. One record per Account+Item combination, aggregated from transaction data. Used for new placement detection, reorder alerts, and volume tracking.

## Quick facts

- **Namespace:** ohfy__
- **Field count:** 59+ (managed)
- **Key relationships:** Master-detail to Account, Master-detail to Item__c
- **NOT custom:** This is a managed package object, not ohfy__Account_Item__c (which exists in source-index but has 0 deployed fields)

## Master-detail fields (create-only)

`ohfy__Account__c` and `ohfy__Item__c` are master-detail and can only be set on initial create (updateable=false):
- **Create:** Use `__r` relationship syntax in Composite API body
- **Update:** API silently ignores these fields — the record stays parented to the original Account and Item
- **External ID pattern:** `PLC:{DistId}:{AcctNbr}:{SuppItem}` — one per Account+Item, not per transaction

## Key input fields

| Field | Type | Notes |
|-------|------|-------|
| `ohfy__Is_New_Placement__c` | Checkbox | Set `true` on every upsert (placement has recent activity) |
| `ohfy__Lost_Placement_After_Days__c` | Number | Reorder alert threshold in days (e.g., 60) |
| `ohfy__First_Sold_Date__c` | Date | Earliest sale date for this Account+Item |
| `ohfy__Last_Sold_Date__c` | Date | Most recent sale date |
| `ohfy__Last_Purchase_Date__c` | Date | Most recent purchase date |
| `ohfy__Last_Purchase_Quantity__c` | Number | Quantity on most recent purchase |
| `ohfy__Last_Invoice_Price__c` | Currency | Price on most recent invoice |
| `ohfy__Is_Active__c` | Checkbox | Active placement flag |

## Formula fields (auto-computed)

These do NOT need to be set by the integration — they compute automatically:

| Field | Formula | Notes |
|-------|---------|-------|
| `ohfy__Days_Since_Last_Order__c` | `TODAY() - Last_Sold_Date__c` | Days since last activity |
| `ohfy__Lost_Placement_Date__c` | `Last_Sold_Date__c + Lost_Placement_After_Days__c` | Date after which placement is "lost" |
| `ohfy__Item_Subtype__c` | `TEXT(Item__r.Package_Type__c)` | Derived from parent Item |

## Volume fields (skip for daily pipeline)

`All_Time_Volume__c`, `Weekly_Sales__c`, `Last_7_Days_Volume__c`, `Last_14_Days_Volume__c`, `Last_30_Days_Volume__c`, `Last_90_Days_Volume__c`, `Last_180_Days_Volume__c` are all updateable but require cumulative rollups across multiple file runs. Better handled by a scheduled Salesforce flow against Depletion__c records, not the daily integration pipeline.

## Placement__c vs Account_Item__c

`ohfy__Account_Item__c` exists in the managed package source-index with similar fields but has 0 deployed fields in the ROS2 sandbox. `ohfy__Placement__c` IS the right object for account-by-item tracking — it has the full field set for CSO features (new placement detection, reorder alerts, volume tracking windows).

## Discovered in

- VIP SRS Phase 5c (2026-04-10): Built placement integration from SLSDA invoice lines
- VIP SRS Phase 5e (2026-04-13): Added Is_New_Placement + Lost_Placement_After_Days, verified formula fields auto-compute
