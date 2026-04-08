# The Beverage Market — Integration Inventory

External systems connected to this customer's Ohanafy instance.

## Active Integrations

| Integration | Direction | Method | Frequency | Status |
|-------------|-----------|--------|-----------|--------|
| Tray.io (VIP SRS Reporting) | Inbound | Tray.io → SF Flows | On-demand | Active |
| Tray.io (Integration Sync) | Bidirectional | Tray.io → SF Flows | Real-time | Active |
| Tray.io (Item Sync) | Inbound | Tray.io → SF Flows | On-demand | Active |
| Tray.io (Order Flow) | Bidirectional | Tray.io → SF Flows | Real-time | Active |
| Tray.io (Order Item Flow) | Inbound | Tray.io → SF Flows | Real-time | Active |
| Tray.io (Pallet Flow) | Inbound | Tray.io → SF Flows | On-demand | Active |
| Tray.io (Payment Method) | Inbound | Tray.io → SF Flows | On-demand | Active |
| Fintech | Outbound | Sync_Customer_Number_to_Fintech flow | On-demand | Active |
| EDI | Inbound | Alert_Sales_Rep_of_New_EDI_Order flow | On-demand | Active |

<!-- Direction: Inbound (to SF), Outbound (from SF), Bidirectional -->
<!-- Method: Tray.io, SF Connect, REST API, SFTP, Manual -->
<!-- Frequency: Real-time, Hourly, Daily, Weekly, On-demand -->

## Tray.io Flows Detected in Org

15 Tray-triggered Flows found in the sandbox:

| Flow Name | Trigger Object | Purpose |
|-----------|---------------|---------|
| TrayOnVIPSRS_Reporting_Setu_Z1M2BQr | VIP_SRS_Reporting_Setup__c | VIP SRS reporting sync |
| TrayOnohfy_Integration_Sync_1gSC0K | ohfy__Integration_Sync__c | Integration sync |
| TrayOnohfy_Integration_Sync_1xHwl0 | ohfy__Integration_Sync__c | Integration sync |
| TrayOnohfy_Integration_Sync_MgrsL | ohfy__Integration_Sync__c | Integration sync |
| TrayOnohfy_Integration_Sync_kKtnv | ohfy__Integration_Sync__c | Integration sync |
| TrayOnohfy_ItemCreate_ZC6wxY | ohfy__Item__c | Item creation sync |
| TrayOnohfy_ItemCreate_Zv4tJa | ohfy__Item__c | Item creation sync |
| TrayOnohfy_OrderFlow_2hO5kI | ohfy__Order__c | Order flow sync |
| TrayOnohfy_OrderFlow_Z1CJ4u4 | ohfy__Order__c | Order flow sync |
| TrayOnohfy_OrderFlow_Z2eUrTK | ohfy__Order__c | Order flow sync |
| TrayOnohfy_OrderFlow_ZkSiT2 | ohfy__Order__c | Order flow sync |
| TrayOnohfy_Order_ItemFlow_Z1Gbss7 | ohfy__Order_Item__c | Order item sync |
| TrayOnohfy_PalletFlow_1mB5ax | ohfy__Pallet__c | Pallet sync |
| TrayOnohfy_Payment_Method_P_1TmTi6 | ohfy__Payment_Method_Pmt__c | Payment method sync |
| TrayOnohfy_Payment_Method_P_2jhgpg | ohfy__Payment_Method_Pmt__c | Payment method sync |
| TrayOnohfy_Payment_Method_P_TcH6T | ohfy__Payment_Method_Pmt__c | Payment method sync |

## Credentials & Authentication

| System | Auth Method | Named Credential | Notes |
|--------|-------------|-----------------|-------|
| Tray.io | SF Connected App | <!-- check --> | Multiple Tray-triggered flows active |
| Fintech | <!-- check --> | <!-- check --> | Fintech_Unload__c object + sync flow |

## Integration Patterns Used

<!-- Reference integration patterns from integrations/patterns/ that this customer uses -->

## Sync Patterns

<!-- Describe each integration's data flow, mapping approach, and error handling -->

## Known Integration Issues

<!-- Running log of integration-specific problems and their resolutions -->
