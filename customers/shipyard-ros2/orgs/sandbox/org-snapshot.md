# Org Snapshot: shipyard-ros2-sandbox

- **Generated:** 2026-04-13T00:00:00Z
- **Org ID:** 00DWF00000C3gOn2AJ
- **Username:** integrations@ohanafy.ros.test
- **Instance:** https://ohanafy-ros2--test.sandbox.my.salesforce.com
- **Org Type:** sandbox
- **Environment:** sandbox
- **Login URL:** https://test.salesforce.com
- **API Version:** 65.0
- **Detected SKUs:** OMS, WMS, REX, PLTFM

## Installed Packages

| Package | Namespace | Version |
|---------|-----------|---------|
| Salesforce Maps | maps | 260.6.0.1 |
| OHFY-Data-Model | ohfy | 0.1.0.1 |
| OHFY-Utilities | ohfy | 0.5.0.3 |
| OHFY-Service-Locator | ohfy | 0.2.0.1 |
| OHFY-PLTFM | ohfy | 0.5.0.1 |
| OHFY-PLTFM-UI | ohfy | 0.2.0.1 |
| OHFY-OMS | ohfy | 0.2.0.1 |
| OHFY-OMS-UI | ohfy | 0.1.0.1 |
| OHFY-WMS | ohfy | 0.2.0.1 |
| OHFY-WMS-UI | ohfy | 0.1.0.1 |
| OHFY-REX | ohfy | 0.1.0.1 |
| OHFY-REX-UI | ohfy | 0.1.0.1 |

## Metadata Summary

| Type | Count |
|------|-------|
| Ohanafy Custom Objects | 78 |
| Ohanafy Apex Classes | 482 |
| Other Managed Apex Classes | 324 |
| Ohanafy Apex Triggers | 34 (all Active) |
| Active Flows | 47 (9 AutoLaunchedFlow) |
| Ohanafy Record Types | 30 |
| VIP Custom Fields Deployed | 30 |
| Transformation_Setting__c Records | 1 |

## Ohanafy Apex Triggers (34)

All triggers are Active:

AccountTrigger, CommitmentTrigger, ContactTrigger, CreditTrigger, DeliveryTrigger,
DepletionTrigger, EquipmentTrigger, EventTrigger, GoalTrackingTrigger, IncentiveTrigger,
InventoryAdjustmentTrigger, InventoryLogGroupTrigger, InventoryLogTrigger,
InventoryReceiptItemTrigger, InventoryReceiptTrigger, InventoryTrigger, InvoiceFeeTrigger,
InvoiceItemTrigger, InvoiceTrigger, ItemTrigger, ItemTypeTrigger, LocationTrigger,
LotCodeTrigger, PricelistItemTrigger, PricelistSettingTrigger, PricelistTrigger,
PromotionItemTrigger, PromotionTrigger, PurchaseOrderItemTrigger, PurchaseOrderTrigger,
TaskTrigger, TierSettingTrigger, TransferGroupTrigger, TransferTrigger

## Ohanafy Record Types (30)

| Object | Record Types |
|--------|-------------|
| Account | Customer, Wholesaler, Vendor/Service, Supplier, Chain Banner |
| ohfy__Item__c | Finished Good, Merchandise, Keg Shell, Packaging, Overhead, Tap Handle, Raw Material |
| ohfy__Item_Type__c | Finished Good, Merchandise, Keg Shell, Packaging, Overhead, Tap Handle, Raw Material |
| ohfy__Invoice__c | E-Commerce, Order |
| ohfy__Delivery__c | Delivery |
| ohfy__Equipment__c | Motorized Vehicle, Equipment |
| ohfy__Credit__c | Credit/Return, Keg Return |
| ohfy__Survey__c | Retailer, Vehicle, Shelf Space Survey |
| ohfy__Pricelist_Setting__c | Pricelist Setting |
| ohfy__Transformation_Setting__c | Weight, Volume |
| ohfy__Inventory_Receipt__c | Inventory Receipt |
| ohfy__Purchase_Order__c | Purchase Order |

## VIP Custom Fields Deployed (29)

| Object | Fields |
|--------|--------|
| Account | VIP_Salesman1__c, VIP_Salesman2__c |
| ohfy__Location__c | VIP_External_ID__c |
| ohfy__Inventory__c | VIP_External_ID__c |
| ohfy__Inventory_History__c | VIP_External_ID__c, VIP_File_Date__c, VIP_From_Date__c, VIP_To_Date__c |
| ohfy__Inventory_Adjustment__c | VIP_External_ID__c, VIP_File_Date__c, VIP_From_Date__c, VIP_To_Date__c |
| ohfy__Item_Type__c | VIP_External_ID__c, VIP_File_Date__c |
| ohfy__Item_Line__c | VIP_External_ID__c, VIP_File_Date__c |
| ohfy__Placement__c | VIP_External_ID__c, VIP_File_Date__c |
| ohfy__Depletion__c | VIP_External_ID__c, VIP_File_Date__c, VIP_From_Date__c, VIP_To_Date__c, VIP_Invoice_Number__c, VIP_Net_Price__c, VIP_Net_Amount__c, VIP_Unit_Quantity__c |
| ohfy__Allocation__c | VIP_External_ID__c, VIP_File_Date__c, VIP_From_Date__c, VIP_To_Date__c |

## VIP SRS Data Load Status (as of 2026-04-13)

148 total VIP records loaded (dist FL01):

| Phase | Object | Prefix | Count | Status |
|-------|--------|--------|-------|--------|
| 1 | Account (Chain Banners) | CHN | 12 | OK |
| 1 | Item_Line__c | ILN | 12 | OK |
| 1 | Item_Type__c | ITY | 12 | OK |
| 1 | Item__c | ITM | 23 | OK |
| 1 | Location__c | LOC | 1 | OK |
| 2 | Account (Outlets) | ACT | 3 | OK |
| 2 | Contact (Buyers) | CON | 0 | BLOCKED |
| 3 | Inventory__c | IVT | 22 | OK |
| 3 | Inventory_History__c | IVH | 48 | OK |
| 3 | Inventory_Adjustment__c | IVA | 2 | OK |
| 4 | Depletion__c | DEP | 5 | OK |
| 4 | Placement__c | PLC | 5 | OK |
| 4 | Allocation__c | ALC | 3 | OK |

**Contact (Buyers):** Blocked by AccountTriggerMethods cascade — ContactTrigger AfterInsert → Account update → missing managed class. See `customers/shipyard-ros2/known-issues.md`.

## Known Blockers

1. **AccountTriggerMethods missing class** — Managed package trigger `AccountTrigger` calls `AccountTriggerMethods` which doesn't exist in this org. Blocks all Account updates AND Contact inserts (cascade via ContactTrigger). Workaround: purge before load (inserts work, updates fail).
2. **Stock_UOM_Sub_Type__c validation** — Validation rule requires `ohfy__Stock_UOM_Sub_Type__c` when `ohfy__Packaging_Type__c` is set on Finished Goods. 1 item enrichment failure per load (Error Code 003).

## Quick Commands

```bash
# Re-retrieve latest metadata
sf project retrieve start --target-org shipyard-ros2-sandbox --manifest ./package.xml

# Run all Apex tests
sf apex run test --target-org shipyard-ros2-sandbox --test-level RunLocalTests --wait 10

# Open the org in browser
sf org open --target-org shipyard-ros2-sandbox

# Query records
sf data query --target-org shipyard-ros2-sandbox --query "SELECT Id, Name FROM Account LIMIT 10"

# VIP verification
cd integrations/vip-srs/scripts && node verify-load.js --config ../config/shipyard.json --spot-checks

# VIP data purge (dry-run)
cd integrations/vip-srs/scripts && bash purge-vip-data.sh --config ../config/shipyard.json

# VIP full pipeline
cd integrations/vip-srs/scripts && node e2e-sandbox-runner.js --dist-id FL01 --file-date 2026-04-13
```
