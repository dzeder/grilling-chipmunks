# Org Snapshot: gulf-production

- **Generated:** 2026-04-06T16:00:00Z (simulated — no live org connection)
- **Org Type:** customer
- **Environment:** production
- **Login URL:** https://ohanafy--gulf.sandbox.my.salesforce.com
- **API Version:** v62.0
- **Detected SKUs:** OMS WMS REX Payments EDI Configure Platform Core Data_Model

> **Note:** This is a simulated snapshot created for E2E validation of the Context Loading Protocol. Real metadata counts are estimated from source indexes and Gulf's profile (9 SKUs, ~8,743 items, ~927 brands). Replace with actual data by running: `bash scripts/connect-org.sh gulf --production --type customer`

## Metadata Summary

| Type | Count |
|------|-------|
| Apex Classes | 723 |
| Apex Triggers | 47 |
| Flows | 32 |
| LWC Components | 89 |
| Custom Objects | 143 |
| Validation Rules | 68 |
| Custom Fields | 2,847 |

## Ohanafy Objects

- **ohfy__Account__c**: 42 fields, 3 validation rules
- **ohfy__Allocation__c**: 18 fields, 1 validation rules
- **ohfy__Brand__c**: 12 fields, 0 validation rules
- **ohfy__Credit__c**: 24 fields, 2 validation rules
- **ohfy__Delivery__c**: 31 fields, 2 validation rules
- **ohfy__Depletion__c**: 19 fields, 1 validation rules
- **ohfy__Display_Item__c**: 15 fields, 0 validation rules
- **ohfy__Inventory__c**: 28 fields, 3 validation rules
- **ohfy__Inventory_Adjustment__c**: 14 fields, 1 validation rules
- **ohfy__Invoice__c**: 38 fields, 4 validation rules
- **ohfy__Invoice_Fee__c**: 11 fields, 1 validation rules
- **ohfy__Invoice_Item__c**: 29 fields, 5 validation rules
- **ohfy__Item__c**: 45 fields, 2 validation rules
- **ohfy__Location__c**: 22 fields, 1 validation rules
- **ohfy__Order__c**: 36 fields, 3 validation rules
- **ohfy__Order_Item__c**: 27 fields, 4 validation rules
- **ohfy__Pallet_Item__c**: 16 fields, 1 validation rules
- **ohfy__Payment__c**: 20 fields, 2 validation rules
- **ohfy__Pick_Ticket__c**: 18 fields, 1 validation rules
- **ohfy__Placement__c**: 14 fields, 0 validation rules
- **ohfy__Price_List__c**: 16 fields, 1 validation rules
- **ohfy__Promotion__c**: 22 fields, 2 validation rules
- **ohfy__Promotion_Item__c**: 13 fields, 1 validation rules
- **ohfy__Route__c**: 19 fields, 1 validation rules
- **ohfy__Warehouse__c**: 17 fields, 1 validation rules

## Invoice_Item__c Validation Rules (5)

| Rule Name | Description |
|-----------|-------------|
| VR_Invoice_Item_Require_Quantity | Quantity must be greater than 0 |
| VR_Invoice_Item_Require_Price | Unit price required when quantity is set |
| VR_Invoice_Item_Prevent_Duplicate | Prevent duplicate items on same invoice |
| VR_Invoice_Item_Mixed_Deposit_Check | Validates keg deposit items against standard items — enforces deposit fee association when item type is Keg and invoice has 10+ line items |
| VR_Invoice_Item_Status_Lock | Prevents edits on completed invoice items |

## Apex Triggers

- AccountTrigger
- AllocationTrigger
- CreditTrigger
- DeliveryTrigger
- DepletionTrigger
- DisplayItemTrigger
- EDI_850_Trigger
- EDI_810_Trigger
- EDI_856_Trigger
- InventoryAdjustmentTrigger
- InventoryTrigger
- InvoiceFeeTrigger
- InvoiceItemTrigger
- InvoiceTrigger
- ItemTrigger
- LocationTrigger
- OrderItemTrigger
- OrderTrigger
- PalletItemTrigger
- PaymentTrigger
- PickTicketTrigger
- PlacementTrigger
- PriceListTrigger
- PromotionItemTrigger
- PromotionTrigger
- RouteTrigger
- WarehouseTrigger
- TA_Account_BI_SetDefaults
- TA_Account_BU_ValidateStatus
- TA_Inventory_BU_PreventNegativeInventory
- TA_Item_BI_SetDefaults
- TA_Item_BU_ValidateStatus
- TA_Order_BI_SetDefaults
- TA_Order_BU_StatusTransition
- TA_OrderItem_BI_DuplicateChecker
- TA_OrderItem_BI_SetPricing
- TA_Invoice_BI_SetDefaults
- TA_Invoice_BU_StatusTransition
- TA_InvoiceItem_BI_SetPricing
- TA_InvoiceItem_BI_DuplicateChecker
- TA_InvoiceItem_BI_MixedDepositValidation
- TA_InvoiceItem_AU_UpdateKegDeposit
- TA_Credit_BI_SetDefaults
- TA_Delivery_BI_SetDefaults
- TA_Delivery_BU_StatusTransition
- TA_Payment_BI_ValidateAmount
- TA_Promotion_BU_PreventDuplicate

## Flows

- Gulf_Auto_Assign_Route
- Gulf_Invoice_Approval_Process
- Gulf_New_Account_Setup
- Gulf_Order_Status_Notification
- Gulf_VIP_Migration_Item_Sync
- OHFY_Account_Status_Handler
- OHFY_Credit_Processing
- OHFY_Delivery_Assignment
- OHFY_Delivery_Completion
- OHFY_Delivery_Route_Assignment
- OHFY_EDI_850_Inbound_Processing
- OHFY_EDI_810_Outbound_Generation
- OHFY_EDI_856_ASN_Generation
- OHFY_Inventory_Adjustment_Handler
- OHFY_Inventory_Recount_Trigger
- OHFY_Invoice_Completion_Handler
- OHFY_Invoice_Email_Notification
- OHFY_Invoice_Status_Handler
- OHFY_Item_Price_Update
- OHFY_Location_Activation
- OHFY_Order_Fulfillment_Pipeline
- OHFY_Order_Status_Handler
- OHFY_Pallet_Build_Automation
- OHFY_Payment_Application
- OHFY_Payment_Settlement
- OHFY_Pick_Ticket_Generation
- OHFY_Placement_Tracking
- OHFY_Promotion_Application
- OHFY_Route_Optimization
- OHFY_Warehouse_Capacity_Check
- OHFY_WMS_Receiving_Handler
- OHFY_WMS_Shipping_Handler

## Quick Commands

```bash
# Re-retrieve latest metadata
sf project retrieve start --target-org gulf-production --manifest ./package.xml

# Run all Apex tests
sf apex run test --target-org gulf-production --test-level RunLocalTests --wait 10

# Open the org in browser
sf org open --target-org gulf-production

# Query records
sf data query --target-org gulf-production --query "SELECT Id, Name FROM Account LIMIT 10"

# Query invoices with mixed item types (debugging)
sf data query --target-org gulf-production --query "SELECT Id, Name, ohfy__Status__c, (SELECT Id, ohfy__Item__r.ohfy__Item_Type__c FROM ohfy__Invoice_Items__r) FROM ohfy__Invoice__c WHERE ohfy__Status__c = 'Draft' LIMIT 20"
```
