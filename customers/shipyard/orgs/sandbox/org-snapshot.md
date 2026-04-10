# Org Snapshot: shipyard-sandbox

- **Generated:** 2026-04-09T13:06:59Z
- **Org Type:** sandbox
- **Environment:** sandbox
- **Login URL:** https://test.salesforce.com
- **API Version:** 65.0
- **Detected SKUs:** WMS REX Configure

## Metadata Summary

| Type | Count |
|------|-------|
| Apex Classes | 7 |
| Apex Triggers | 0 |
| Flows | 19 |
| LWC Components | 56 |
| Custom Objects | 87 |
| Validation Rules | 5 |
| Custom Fields | 299 |

## Ohanafy Objects

- **Account**: 48 fields, 1 validation rules
- **Activity**: 2 fields, 0 validation rules
- **Brand_Family_Representative__c**: 2 fields, 0 validation rules
- **External_Account_ID__c**: 4 fields, 0 validation rules
- **External_ID__c**: 6 fields, 0 validation rules
- **External_Item_ID__c**: 4 fields, 0 validation rules
- **User**: 11 fields, 0 validation rules
- **Walkthrough__c**: 5 fields, 0 validation rules
- **maps__Route__c**: 4 fields, 0 validation rules
- **ohfy__Account_Route__c**: 3 fields, 0 validation rules
- **ohfy__Commitment__c**: 4 fields, 0 validation rules
- **ohfy__Delivery__c**: 7 fields, 0 validation rules
- **ohfy__Distributor_Placement__c**: 19 fields, 0 validation rules
- **ohfy__Inventory_Log_Group__c**: 5 fields, 0 validation rules
- **ohfy__Inventory__c**: 1 fields, 0 validation rules
- **ohfy__Item_Line__c**: 3 fields, 0 validation rules
- **ohfy__Item__c**: 23 fields, 0 validation rules
- **ohfy__Order__c**: 60 fields, 4 validation rules
- **ohfy__Purchase_Order__c**: 4 fields, 0 validation rules
- **ohfy__Route__c**: 4 fields, 0 validation rules
- **ohfy__Survey__c**: 80 fields, 0 validation rules

## Apex Triggers



## Flows

- AddToTruckQA
- CreateCreditQA
- Keep_item_deposit_true
- Mark_Child_Location_as_Sellable
- New_IR_ready_for_completion
- New_Item_Creation_Walk_Through
- OrderTableDistroMobileQA
- PickingQA
- Recount_Inventory_Count
- SellFromTruckQA
- Set_Company_on_New_Location
- Set_Latest_Activity_on_Account_Notes
- Set_Lot_Fields
- Set_New_Product_to_Active
- Set_Warehouse_Dock_Times
- Submit_New_Inventory_Log_Group_for_Approval
- Task_Alert_for_EDI_Order_Failed
- UpdateInvoiceQA
- Update_Brand_Family_Name

## Quick Commands

```bash
# Re-retrieve latest metadata
sf project retrieve start --target-org shipyard-sandbox --manifest ./package.xml

# Run all Apex tests
sf apex run test --target-org shipyard-sandbox --test-level RunLocalTests --wait 10

# Open the org in browser
sf org open --target-org shipyard-sandbox

# Query records
sf data query --target-org shipyard-sandbox --query "SELECT Id, Name FROM Account LIMIT 10"
```
