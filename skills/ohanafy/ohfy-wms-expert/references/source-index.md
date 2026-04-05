# OHFY-WMS Source Index
> Last synced: 2026-04-03T12:18:51Z | Commit: e0c873e | Repo: Ohanafy/OHFY-WMS

## Apex Classes (64 production, 0 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| BackfillController | public | Controller for the backfill LWC component. Handles backfilling invo |
| BackfillController_T | public |  |
| OversoldController | public | Controller for the oversold LWC component. Handles updating invoice |
| OversoldController_T | public |  |
| CreateInventoryReceiptController | public | Controller for the create inventory receipt LWC component. Handles |
| CreateInventoryReceiptController_T | public |  |
| UpdateInventoryReceiptController | public | Controller for the update inventory receipt LWC component. Handles |
| UpdateInventoryReceiptController_T | public |  |
| MassPickingController | public | Controller for the mass picking LWC component. Handles picking mult |
| MassPickingController_T | public |  |
| PickingController | public | Controller for the picking LWC component. Handles the process of pi |
| PickingController_T | public |  |
| ItemReturnController | public | Controller for the item return LWC component. Handles returning pro |
| ItemReturnController_T | public |  |
| PalletizationController | public | Controller for the palletization LWC component. Handles creating an |
| PalletizationController_T | public |  |
| CreatePurchaseOrderController | public | Controller for the create purchase order LWC component. Handles cre |
| CreatePurchaseOrderController_T | public |  |
| UpdatePurchaseOrderController | public | Controller for the update purchase order LWC component. Handles upd |
| UpdatePurchaseOrderController_T | public |  |
| LocationTransferController | public | Controller for the location transfer LWC component. Handles creatin |
| LocationTransferController_T | public |  |
| TransferToTruckController | public | Controller for the transfer to truck LWC component. Handles transfe |
| TransferToTruckController_T | public |  |
| E_Delivery_ItemReturn | public | Executable class for delivery item return operations. Provides meth |
| E_Delivery_ItemReturn_T | public |  |
| E_InventoryReceipt | public | Executable class for inventory receipt operations. Provides methods |
| E_InventoryReceipt_Adjustments | public | Executable class for inventory receipt adjustments. Handles creatin |
| E_InventoryReceipt_Adjustments_T | public |  |
| E_InventoryReceipt_PurchasePrice | public |  |
| E_InventoryReceipt_PurchasePrice_T | public |  |
| E_InventoryReceipt_T | public |  |
| E_Invoice_Items | public | Executable class for invoice item operations. Provides methods for |
| E_Invoice_Items_T | public |  |
| E_Pallet | public | Executable class for pallet operations. Provides methods for retrie |
| E_Pallet_T | public |  |
| E_PurchaseOrder | public | Executable class for purchase order operations. Provides methods fo |
| E_PurchaseOrder_T | public |  |
| Q_ProcessMassPicking | public | Queueable class for processing mass picking operations asynchronous |
| Q_ProcessMassPicking_T | public |  |
| Q_ProcessPicking | public | Queueable class for processing picking operations asynchronously. W |
| Q_ProcessPicking_T | public |  |
| InventoryReceiptTriggerService | public |  |
| InventoryReceipt_AU_AdjStatusUpdater_T | public |  |
| InventoryReceipt_AU_CalculateKegs_T | public |  |
| InventoryReceipt_AU_Canceller_T | public |  |
| InventoryReceipt_BU_ItemQuantUpdater_T | public |  |
| InventoryReceiptItemTriggerService | public |  |
| InventoryReceiptItem_AU_AdjUpdater_T | public |  |
| PurchaseOrderTriggerService | public |  |
| PurchaseOrder_AU_AdjStatusUpdater_T | public |  |
| PurchaseOrder_AU_Canceller_T | public |  |
| PurchaseOrder_AU_NameSetter_T | public |  |
| PurchaseOrder_BD_AdjRemover_T | public |  |
| PurchaseOrder_BU_Completer_T | public |  |
| PurchaseOrderItemTriggerService | public |  |
| PurchaseOrderItem_AI_AdjCreator_T | public |  |
| PurchaseOrderItem_AU_AdjUpdater_T | public |  |
| PurchaseOrderItem_BD_AdjRemover_T | public |  |
| PurchaseOrderItem_BU_TotalCostUpdater_T | public |  |
| TransferTriggerService | public |  |
| Transfer_AI_T | public |  |
| TransferGroupTriggerService | public |  |
| TransferGroup_AU_T | public |  |

## Triggers (6)

| Trigger | sObject | Events |
|---------|---------|--------|
| InventoryReceiptItemTrigger | Inventory_Receipt_Item__c |  |
| InventoryReceiptTrigger | Inventory_Receipt__c |  |
| PurchaseOrderItemTrigger | Purchase_Order_Item__c |  |
| PurchaseOrderTrigger | Purchase_Order__c |  |
| TransferGroupTrigger | Transfer_Group__c |  |
| TransferTrigger | Transfer__c |  |

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| InventoryReceiptTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InventoryReceiptTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InventoryReceiptTriggerService | beforeUpdate | `public void beforeUpdate(` |
| InventoryReceiptTriggerService | afterUpdate | `public void afterUpdate(` |
| InventoryReceiptTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InventoryReceiptTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InventoryReceiptTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| InventoryReceiptTriggerService | calculateInventoryReceiptKegs | `public void calculateInventoryReceiptKegs(` |
| InventoryReceiptTriggerService | cancelInventoryReceipt | `public void cancelInventoryReceipt(` |
| InventoryReceiptTriggerService | updateInventoryReceiptAdjustments | `public void updateInventoryReceiptAdjustments(` |
| InventoryReceiptTriggerService | updateInventoryReceiptItemQuantities | `public void updateInventoryReceiptItemQuantities(` |
| InventoryReceiptTriggerService | calculateInventoryReceiptKegsOnInsert | `public void calculateInventoryReceiptKegsOnInsert(` |
| InventoryReceiptItemTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InventoryReceiptItemTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InventoryReceiptItemTriggerService | beforeUpdate | `public void beforeUpdate(` |
| InventoryReceiptItemTriggerService | afterUpdate | `public void afterUpdate(` |
| InventoryReceiptItemTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InventoryReceiptItemTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InventoryReceiptItemTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| InventoryReceiptItemTriggerService | updateInventoryReceiptItemAdjustments | `public void updateInventoryReceiptItemAdjustments(` |
| PurchaseOrderTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PurchaseOrderTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PurchaseOrderTriggerService | beforeUpdate | `public void beforeUpdate(` |
| PurchaseOrderTriggerService | afterUpdate | `public void afterUpdate(` |
| PurchaseOrderTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PurchaseOrderTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PurchaseOrderTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| PurchaseOrderTriggerService | cancelPurchaseOrder | `public void cancelPurchaseOrder(` |
| PurchaseOrderTriggerService | completePurchaseOrder | `public void completePurchaseOrder(` |
| PurchaseOrderTriggerService | removePurchaseOrderAdjustments | `public void removePurchaseOrderAdjustments(List<Purchase_Order__c> oldPurchaseOrders) ` |
| PurchaseOrderTriggerService | setPurchaseOrderName | `public void setPurchaseOrderName(` |
| PurchaseOrderTriggerService | updatePurchaseOrderAdjustments | `public void updatePurchaseOrderAdjustments(` |
| PurchaseOrderItemTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PurchaseOrderItemTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PurchaseOrderItemTriggerService | beforeUpdate | `public void beforeUpdate(` |
| PurchaseOrderItemTriggerService | afterUpdate | `public void afterUpdate(` |
| PurchaseOrderItemTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PurchaseOrderItemTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PurchaseOrderItemTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| PurchaseOrderItemTriggerService | createPurchaseOrderItemAdjustments | `public void createPurchaseOrderItemAdjustments(` |
| PurchaseOrderItemTriggerService | removePurchaseOrderItemAdjustments | `public void removePurchaseOrderItemAdjustments(` |
| PurchaseOrderItemTriggerService | updatePurchaseOrderItemAdjustments | `public void updatePurchaseOrderItemAdjustments(` |
| PurchaseOrderItemTriggerService | updatePurchaseOrderItemTotalCost | `public void updatePurchaseOrderItemTotalCost(` |
| TransferTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| TransferTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| TransferTriggerService | beforeUpdate | `public void beforeUpdate(` |
| TransferTriggerService | afterUpdate | `public void afterUpdate(` |
| TransferTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| TransferTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| TransferTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| TransferGroupTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| TransferGroupTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| TransferGroupTriggerService | beforeUpdate | `public void beforeUpdate(` |
| TransferGroupTriggerService | afterUpdate | `public void afterUpdate(` |
| TransferGroupTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| TransferGroupTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| TransferGroupTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| TransferGroupTriggerService | updateTransferAdjustments | `public void updateTransferAdjustments(` |

## Custom Objects & Fields

_No custom objects found._


## Frontend: OHFY-WMS-UI

## LWC Components (17)

| Component | Public API (@api) | Description |
|-----------|-------------------|-------------|
| backfill |  | handles the changing of the delivery date to filter which in |
| confirmPartialPick | itemsToConfirm, isMobile |  |
| createInventoryReceipt | btnToggle, totalItemCost, useLotTracking, recordId | Safely extracts a human-readable message from any error shap |
| createPurchaseOrder | btnToggle, recordId | This component is used to create a purchase order for a give |
| deliveryPicking | recordId, selectedOrderIds, btnToggle | This method handles toggling the error row and partial row h |
| deliveryPickingSelection |  |  |
| invoicePicking | recordId, btnToggle | This component is used to create an invoice for the order. |
| itemReturn |  | Safely extracts a human-readable message from any error shap |
| locationTransfer | recordId, objectApiName, locationId, btnToggle, locationHasBeenSelected, emptyInventoryList | This function is used to get the inventory records from the  |
| oversold |  | handles the changing of the delivery date to filter which in |
| palletization |  | Retrieve all pallets and pallet items for the delivery and p |
| productRateOfSales | itemId, customerId, rateOfSales,  | Public API method that can be called from parent LWC to relo |
| sendPODocument |  |  |
| splitPalletItemModal | item, maxQty, description |  |
| transferToTruck |  | Safely extracts a human-readable message from any error shap |
| updateInventoryReceipt | recordId, btnDisabled | Safely extracts a human-readable message from any error shap |
| updatePurchaseOrder | btnToggle, recordId | Safely extracts a human-readable message from any error shap |

