# The Beverage Market — Notes

Running notes from debugging sessions, design decisions, and gotchas.

<!-- Add entries with dates. Most recent first. -->

## 2026-04-08 — Initial sandbox connection

**Connected to:** Full sandbox (`ohanafy-tbm--full`)
**Username:** integrations@ohanafy.com.tbm.full
**Instance URL:** https://ohanafy-tbm--full.sandbox.my.salesforce.com

### Key findings

- **6 Ohanafy SKUs detected:** OMS, WMS, REX, Ecom, Payments, Configure
- **Data volume:** 3,259 accounts, 1,847 items, 429,650 orders, 469 locations, 548 routes
- **Metadata:** 61 Apex classes, 4 triggers, 68 flows, 82 LWC components, 71 objects, 590 fields, 33 validation rules
- **Heavy Tray.io usage:** 15 Tray-triggered flows found (Integration Sync, Item Create, Order Flow, Order Item, Pallet, Payment Method, VIP SRS)
- **Custom objects of note:** Beer_Pricing__c, MC_Beer_Price__c, Mandate__c/Mandate_Item__c, Deposit__c/Deposit_Adjustment__c, VIP_SRS objects, Fintech_Unload__c, Sales_Route__c, Route_Check_In/Out__c
- **ohfy__Order__c is the heaviest object:** 109 fields, 14 validation rules
- **4 Apex triggers only:** AI_ShortRouteCreator, InvoiceTrigger, OrderAutoCheckOut, OrderAutoCheckOutUpdate — most logic appears to be in Flows
- **maps__Route__c present** — indicates Salesforce Maps is installed
- **VIP SRS integration** — VIP_SRS_Execution__c, VIP_SRS_File_Execution__c, VIP_SRS_Reporting_Setup__c suggest active VIP (legacy ERP) reporting sync
- **Fintech integration** — Fintech_Unload__c + Sync_Customer_Number_to_Fintech flow
- **EDI active** — Alert_Sales_Rep_of_New_EDI_Order and Task_Alert_for_EDI_Order_Failed flows

### Architecture observations

- Flow-heavy architecture (68 flows vs 4 triggers) — business logic primarily in declarative automation
- Multiple Tray.io flows for the same objects (4 Order flows, 4 Integration Sync flows, 3 Payment Method flows) — suggests versioned or phased integration rollouts
- DVI (Driver Vehicle Inspection) workflow present: Create_DVI_For_Deliveries_Today
- Approval processes: Inventory_Log_Recount_Approval, Submit_New_Inventory_Log_Group_for_Approval
- Wine tax handling: Set_Wine_Tax_for_Invoices, Update_Wine_Tax_when_Invoice_is_Updated — distributes wine in addition to beer
