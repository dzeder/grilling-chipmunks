# Org Snapshot: beverage-market-sandbox

- **Generated:** 2026-04-08T12:31:21Z
- **Org Type:** customer
- **Environment:** sandbox
- **Login URL:** https://test.salesforce.com
- **API Version:** 65.0
- **Detected SKUs:** OMS WMS REX Ecom Payments Configure

## Metadata Summary

| Type | Count |
|------|-------|
| Apex Classes | 61 |
| Apex Triggers | 4 |
| Flows | 68 |
| LWC Components | 82 |
| Custom Objects | 71 |
| Validation Rules | 33 |
| Custom Fields | 590 |

## Ohanafy Objects

- **Account**: 88 fields, 1 validation rules
- **Activity**: 6 fields, 0 validation rules
- **Beer_Pricing__c**: 11 fields, 0 validation rules
- **Contact**: 0 fields, 1 validation rules
- **Delivery_Stop__c**: 6 fields, 0 validation rules
- **Deposit_Adjustment__c**: 3 fields, 0 validation rules
- **Deposit__c**: 13 fields, 0 validation rules
- **Fintech_Unload__c**: 1 fields, 0 validation rules
- **MC_Beer_Price__c**: 12 fields, 0 validation rules
- **Mandate_Item__c**: 4 fields, 0 validation rules
- **Mandate__c**: 27 fields, 0 validation rules
- **Route_Check_In__c**: 5 fields, 0 validation rules
- **Route_Check_Out__c**: 5 fields, 0 validation rules
- **Sales_Rep_Home_Config__mdt**: 1 fields, 0 validation rules
- **Sales_Route_Stop__c**: 14 fields, 0 validation rules
- **Sales_Route__c**: 4 fields, 0 validation rules
- **User**: 14 fields, 0 validation rules
- **VIP_SRS_Execution__c**: 13 fields, 0 validation rules
- **VIP_SRS_File_Execution__c**: 13 fields, 0 validation rules
- **VIP_SRS_Reporting_Setup__c**: 6 fields, 4 validation rules
- **maps__Route__c**: 4 fields, 0 validation rules
- **ohfy__Account_Route__c**: 18 fields, 0 validation rules
- **ohfy__Billback__c**: 1 fields, 0 validation rules
- **ohfy__Credit__c**: 12 fields, 3 validation rules
- **ohfy__Delivery__c**: 14 fields, 3 validation rules
- **ohfy__Inventory_Log_Group__c**: 5 fields, 0 validation rules
- **ohfy__Inventory_Receipt__c**: 2 fields, 3 validation rules
- **ohfy__Inventory__c**: 4 fields, 1 validation rules
- **ohfy__Item_Line__c**: 2 fields, 0 validation rules
- **ohfy__Item_Type__c**: 4 fields, 0 validation rules
- **ohfy__Item__c**: 40 fields, 1 validation rules
- **ohfy__Location__c**: 7 fields, 0 validation rules
- **ohfy__Order__c**: 109 fields, 14 validation rules
- **ohfy__Pallet__c**: 2 fields, 0 validation rules
- **ohfy__Pricelist__c**: 1 fields, 0 validation rules
- **ohfy__Promotion_Invoice_Item__c**: 7 fields, 0 validation rules
- **ohfy__Promotion__c**: 3 fields, 0 validation rules
- **ohfy__Purchase_Order__c**: 12 fields, 1 validation rules
- **ohfy__Route__c**: 9 fields, 0 validation rules
- **ohfy__Survey__c**: 88 fields, 0 validation rules
- **ohfy__Transfer_Group__c**: 0 fields, 1 validation rules

## Apex Triggers

- AI_ShortRouteCreator
- InvoiceTrigger
- OrderAutoCheckOut
- OrderAutoCheckOutUpdate

## Flows

- Account_Route_Set_Stop_Cadence_on_Create
- Alert_Sales_Rep_of_New_EDI_Order
- Alert_TBL_of_New_PO
- Cancel_Invoice_Mobile
- Clone_Brand
- Create_DVI_For_Deliveries_Today
- Create_Generic_Keg_Return
- Create_IR_Screen_Flow
- Delete_Abandoned_Draft_Invoices
- Distro_Order_Table_Mobile
- Docly_Print_Flow
- Inventory_Log_Recount_Approval
- Keep_item_deposit_true
- Mavtron_Printing_Screen_Flow
- New_IR_ready_for_completion
- New_Item_Creation_Walk_Through
- Product_Barcode_Mobile
- Recount_Inventory_Count
- Reset_Invoice_Keg_Field_when_a_keg_return_is_deleted
- Route_and_Account_Route_Creation_Flow
- Set_AM_Survey_Status_on_Delivery
- Set_Account_fulfillment_location
- Set_Company_Field_on_New_Location
- Set_DVI_Task_to_Complete_when_Survey_is_Completed
- Set_Dock_Sale
- Set_E_Commerce_Order_Rep_to_Account_Sales_Rep
- Set_Fee_Accounting_Ids_Upon_Creation
- Set_Increase_for_Inner_Distro_Orders
- Set_Item_FOB
- Set_Keg_Deposit
- Set_Lot_Fields
- Set_New_Item_to_Lot_Tracked
- Set_New_Product_to_Active
- Set_Route_Order_Value
- Set_Routes_Deliveries_per_Day
- Set_Sales_Rep_for_Manager_Orders
- Set_Warehouse_Dock_Times
- Set_Wine_Tax_for_Invoices
- Submit_New_Inventory_Log_Group_for_Approval
- Switch_Company_View
- Sync_Customer_Number_to_Fintech
- Task_Alert_for_EDI_Order_Failed
- TrayOnVIPSRS_Reporting_Setu_Z1M2BQr
- TrayOnohfy_Integration_Sync_1gSC0K
- TrayOnohfy_Integration_Sync_1xHwl0
- TrayOnohfy_Integration_Sync_MgrsL
- TrayOnohfy_Integration_Sync_kKtnv
- TrayOnohfy_ItemCreate_ZC6wxY
- TrayOnohfy_ItemCreate_Zv4tJa
- TrayOnohfy_OrderFlow_2hO5kI
- TrayOnohfy_OrderFlow_Z1CJ4u4
- TrayOnohfy_OrderFlow_Z2eUrTK
- TrayOnohfy_OrderFlow_ZkSiT2
- TrayOnohfy_Order_ItemFlow_Z1Gbss7
- TrayOnohfy_PalletFlow_1mB5ax
- TrayOnohfy_Payment_Method_P_1TmTi6
- TrayOnohfy_Payment_Method_P_2jhgpg
- TrayOnohfy_Payment_Method_P_TcH6T
- Unpalletize_Invoice
- Update_Account_on_Waypoint
- Update_Brand_Family_Name
- Update_Delivery_Status_When_All_Invoices_Complete_Cancelled
- Update_IR_Screen_Flow
- Update_PO_s_Dock_Time_when_Event_is_updated
- Update_Status_to_Complete_When_POD_True
- Update_Supplier
- Update_Waypoint_Helper_Field
- Update_Wine_Tax_when_Invoice_is_Updated

## Quick Commands

```bash
# Re-retrieve latest metadata
sf project retrieve start --target-org beverage-market-sandbox --manifest ./package.xml

# Run all Apex tests
sf apex run test --target-org beverage-market-sandbox --test-level RunLocalTests --wait 10

# Open the org in browser
sf org open --target-org beverage-market-sandbox

# Query records
sf data query --target-org beverage-market-sandbox --query "SELECT Id, Name FROM Account LIMIT 10"
```
