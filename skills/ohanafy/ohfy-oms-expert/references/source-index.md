# OHFY-OMS Source Index
> Last synced: 2026-04-03T12:18:47Z | Commit: 6e8aab4 | Repo: Ohanafy/OHFY-OMS

## Apex Classes (134 production, 0 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| B_Delivery_LockDeliveries | public | Locks deliveries for tomorrow's date |
| B_Delivery_StatusUpdater | global | This class checks the status of Delivery records each day and updat |
| B_Delivery_StatusUpdater_T | public |  |
| B_Route_DeliveryCreator | global | This class is used to create an deliveries for active routes. |
| B_Route_DeliveryCreator_T | public |  |
| S_Delivery_LockDeliveries | global | Method called on a specific schedule |
| S_Delivery_LockDeliveries_T | public |  |
| B_Invoice_LockInvoices | public | Locks picked invoices for tomorrow's date |
| B_Invoice_MetricUpdater | public | Batch class that gets recently completed invoices and updates the T |
| S_Invoice_LockInvoices | global | Method called on a specific schedule |
| S_Invoice_LockInvoices_T | public |  |
| S_Invoice_MetricUpdater | global | Schedulable class intended to run nightly. Calls B_Order_MetricUpda |
| S_Invoice_MetricUpdater_T | public | Test class for S_Order_MetricUpdater. This class tests that B_Order |
| CreateAllocationsController | public | Controller class for creating allocation records. Provides methods |
| CreateAllocationsController_T | public |  |
| CreateCreditsController | public | Controller class for creating and managing credit records. Provides |
| CreateCreditsController_T | public |  |
| AddToTruckController | public | Controller class for handling operations related to adding credits |
| CancelInvoiceController | public | Controller class for canceling invoices and optionally reassigning |
| CreateInvoiceController | public | Controller class for creating and managing invoice (order) records. |
| InvoiceSignatureController | public |  |
| SellFromTruckController | public | Controller class for processing sales from truck inventory. Handles |
| AddToTruckController_Credits_T | public |  |
| AddToTruckController_InvoiceItems_T | public |  |
| CancelInvoiceController_T | public |  |
| CreateInvoiceController_T | public |  |
| InvoiceSignatureController_T | public |  |
| SellFromTruckController_T | public |  |
| UpdateInvoiceController | public | Controller class for updating invoice items and related records. Pr |
| UpdateInvoiceController_T | public |  |
| CreatePromotionsController | public | Controller class for creating promotion records with complex config |
| CreatePromotionsController_T | public |  |
| E_Allocations | public | Created by grantrisk on 5/15/24. |
| E_Allocations_T | public | Created by grantrisk on 5/20/24. |
| E_Credits | public |  |
| E_Credits_T | public |  |
| E_Delivery_FieldUpdater | public | Executable to update the following fields on a Delivery Object |
| E_Delivery_FieldUpdater_T | public |  |
| E_Delivery_Items | public |  |
| E_Delivery_Items_T | public |  |
| E_InvoiceAdjDeleter | public | This class is used to revert Inventory Adjustments back to their or |
| E_Invoice_StatusValidationBypass | public |  |
| E_Invoicing_Configuration | public |  |
| E_Invoicing_Items | public | This class is used grab all item records selected in the Front-end |
| E_Invoicing_Items_T | public |  |
| E_Invoicing_TableMessages | public | This class is used to set the delivery message on the Order Table a |
| E_Invoicing_TableMessages_T | public |  |
| E_InvoiceItem_Items | public |  |
| E_InvoiceItem_Items_T | public | Created by BrysonCarroll on 8/21/24. |
| E_Promotions | public |  |
| E_Promotions_T | public |  |
| Q_ProcessInvoice | public |  |
| Q_ProcessInvoice_T | public |  |
| S_Deliveries | public | Service class for deliveries to handle crud operations associated w |
| S_PricingAdjustments | public |  |
| S_PricingAdjustments_T | public |  |
| S_Promotions | public |  |
| S_Promotions_T | public |  |
| AccountTriggerMethods | public |  |
| AccountTriggerMethods_T | public |  |
| CreditTriggerService | public | Service class that handles trigger operations for Credit__c objects |
| Credit_AD_T | public |  |
| Credit_AI_T | public |  |
| Credit_AU_OfflineAddToTruck_T | public |  |
| Credit_AU_T | public |  |
| Credit_BU_T | public |  |
| DeliveryTriggerService | public | Service class that handles trigger operations for Delivery__c objec |
| Delivery_AU_T | public |  |
| Delivery_BI_T | public |  |
| Delivery_BU_T | public |  |
| DepletionTriggerService | public | Service class that handles trigger operations for Depletion__c obje |
| Depletion_AI_T | public |  |
| InvoiceTriggerService | public |  |
| Invoice_AD_UpdateDeliveryFields_T | public |  |
| Invoice_AD_UpdateInvoiceGroup_T | public |  |
| Invoice_AI_Goals_T | public |  |
| Invoice_AI_T | public |  |
| Invoice_AU_AssignDelivery_T | public |  |
| Invoice_AU_CancelInvoice_T | public |  |
| Invoice_AU_CompleteInvoice_T | public |  |
| Invoice_AU_CreateOfflineInvoiceItems_T | public |  |
| Invoice_AU_SendEmail_T | public |  |
| Invoice_AU_SetName_T | public |  |
| Invoice_AU_UpdateAdjustmentStatus_T | public |  |
| Invoice_AU_UpdateGoals_T | public |  |
| Invoice_AU_UpdateInvoiceAdjustments_T | public |  |
| Invoice_AU_UpdateInvoiceGroup_T | public |  |
| Invoice_AU_UpdatePalletItems_T | public |  |
| Invoice_AU_UpdatePlacements_T | public |  |
| Invoice_BD_DeleteGoalInvoices_T | public |  |
| Invoice_BD_DeleteInventoryAdjustments_T | public |  |
| Invoice_BD_DeletePromotionInvoiceItems_T | public |  |
| Invoice_BI_T | public |  |
| Invoice_BU_AssociateDelivery_T | public |  |
| Invoice_BU_UpdatePaymentInfo_T | public |  |
| Invoice_BU_UpdateStatus_T | public |  |
| InvoiceAfterDelete | public | Handles after delete trigger operations for Invoice__c records. |
| InvoiceAfterInsert | public | Handles after insert trigger operations for Invoice__c records. |
| InvoiceAfterUpdate | public | Handles after update trigger operations for Invoice__c records. |
| InvoiceBeforeDelete | public | Handles before delete trigger operations for Invoice__c records. |
| InvoiceBeforeInsert | public | Utility class that handles before insert operations for Invoice__c |
| InvoiceBeforeUpdate | public | Handles before update trigger operations for Invoice__c records. |
| InvoiceFeeTriggerService | public | Handles the trigger operations for Invoice_Fee__c records. |
| InvoiceFee_AD_T | public |  |
| InvoiceFee_AI_T | public |  |
| InvoiceFee_AU_T | public |  |
| InvoiceItemTriggerService | public | Trigger service class for Invoice Item that orchestrates trigger op |
| InvoiceItem_AD_UpdateDeliveryFields_T | public |  |
| InvoiceItem_AI_OfflineCreation_T | public |  |
| InvoiceItem_AI_OfflineSellFromTruck_T | public |  |
| InvoiceItem_AI_UpdatePlacements_T | public |  |
| InvoiceItem_AU_OfflineAddIIToTruck_T | public |  |
| InvoiceItem_AU_OfflineSellFromTruck_T | public |  |
| InvoiceItem_AU_UpdateKegDeposit_T | public |  |
| InvoiceItem_BD_DeleteIAs_T | public |  |
| InvoiceItem_BD_DeletePromotionII_T | public |  |
| InvoiceItem_BI_ApplyInvoiceAdjustments_T | public |  |
| InvoiceItem_BI_AssignDelivery_T | public |  |
| InvoiceItem_BI_AutoApplyPromotions_T | public |  |
| InvoiceItem_BI_PreventDuplicateIIs_T | public |  |
| InvoiceItem_BI_SetOfflineFields_T | public |  |
| InvoiceItem_BU_ApplyInvoiceAdjustments_T | public |  |
| InvoiceItem_BU_AutoApplyPromotions_T | public |  |
| InvoiceItemAfterDelete | public | Trigger handler class for Invoice Item after delete operations. |
| InvoiceItemAfterInsert | public | Utility class that handles after insert operations for Invoice_Item |
| InvoiceItemAfterUpdate | public | Trigger handler class for Invoice Item after update operations. |
| InvoiceItemBeforeDelete | public | Trigger handler class for Invoice Item before delete operations. |
| InvoiceItemBeforeInsert | public | Utility class that handles before insert operations for Invoice_Ite |
| InvoiceItemBeforeUpdate | public | Trigger handler class for Invoice Item before update operations. |
| PromotionTriggerService | public | Service class that handles trigger operations for Promotion__c obje |
| Promotion_AU_T | public |  |
| Promotion_BU_T | public |  |
| PromotionItemTriggerService | public | Service class that handles trigger operations for Promotion_Item__c |
| PromotionItem_AI_T | public |  |

## Triggers (8)

| Trigger | sObject | Events |
|---------|---------|--------|
| CreditTrigger | Credit__c |  |
| DeliveryTrigger | Delivery__c |  |
| DepletionTrigger | Depletion__c |  |
| InvoiceFeeTrigger | Invoice_Fee__c |  |
| InvoiceItemTrigger | Invoice_Item__c |  |
| InvoiceTrigger | Invoice__c |  |
| PromotionItemTrigger | Promotion_Item__c |  |
| PromotionTrigger | Promotion__c |  |

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| CreditTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| CreditTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| CreditTriggerService | beforeUpdate | `public void beforeUpdate(` |
| CreditTriggerService | afterUpdate | `public void afterUpdate(` |
| CreditTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| CreditTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| CreditTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| DeliveryTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| DeliveryTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| DeliveryTriggerService | beforeUpdate | `public void beforeUpdate(` |
| DeliveryTriggerService | afterUpdate | `public void afterUpdate(` |
| DeliveryTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| DeliveryTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| DeliveryTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| DepletionTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| DepletionTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| DepletionTriggerService | beforeUpdate | `public void beforeUpdate(` |
| DepletionTriggerService | afterUpdate | `public void afterUpdate(` |
| DepletionTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| DepletionTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| DepletionTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceTriggerService | beforeUpdate | `public void beforeUpdate(` |
| InvoiceTriggerService | afterUpdate | `public void afterUpdate(` |
| InvoiceTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InvoiceTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InvoiceTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceFeeTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceFeeTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceFeeTriggerService | beforeUpdate | `public void beforeUpdate(` |
| InvoiceFeeTriggerService | afterUpdate | `public void afterUpdate(` |
| InvoiceFeeTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InvoiceFeeTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InvoiceFeeTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceItemTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceItemTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| InvoiceItemTriggerService | beforeUpdate | `public void beforeUpdate(` |
| InvoiceItemTriggerService | afterUpdate | `public void afterUpdate(` |
| InvoiceItemTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InvoiceItemTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| InvoiceItemTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| PromotionTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PromotionTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PromotionTriggerService | beforeUpdate | `public void beforeUpdate(` |
| PromotionTriggerService | afterUpdate | `public void afterUpdate(` |
| PromotionTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PromotionTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PromotionTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |
| PromotionTriggerService | preventDuplicatePromotions | `public void preventDuplicatePromotions(` |
| PromotionItemTriggerService | beforeInsert | `public void beforeInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PromotionItemTriggerService | afterInsert | `public void afterInsert(List<SObject> newList, Set<String> enabledMethods) ` |
| PromotionItemTriggerService | beforeUpdate | `public void beforeUpdate(` |
| PromotionItemTriggerService | afterUpdate | `public void afterUpdate(` |
| PromotionItemTriggerService | beforeDelete | `public void beforeDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PromotionItemTriggerService | afterDelete | `public void afterDelete(List<SObject> oldList, Set<String> enabledMethods) ` |
| PromotionItemTriggerService | afterUndelete | `public void afterUndelete(List<SObject> newList, Set<String> enabledMethods) ` |

## Custom Objects & Fields

_No custom objects found._


## Frontend: OHFY-OMS-UI

## LWC Components (21)

| Component | Public API (@api) | Description |
|-----------|-------------------|-------------|
| addPromotionItemsModal | items, rewards, straightLine, totalQuantity, promotion, pricelist | format lineItemsList to be displayed in the table |
| addToTruck |  | Grab all credits that are on the invoice and have a reason c |
| applicablePromotionsModal | promotionsList, items, promotionIdToJunctionsMap, pricelist, isMobile | format lineItemsList to be displayed in the table |
| cancelInvoice |  |  |
| createAllocations |  | Adds a new empty row to the allocations table |
| createCredits | lotTrackingEnabled, isMobile, isAccountPage, isOrderPage, isReturn, disableSubmit, recordName, objectApiName, accountRecordName, orderRecordName, orderRecordStatus, orderRecordDelivery, recordId, recordUrl, isSubmitted, colSpan, creditHasRemainingBalance, creditTotalAmount, creditAmountRemaining, initialCreditAmountRemaining, creditTotalAppliedAmount, creditTypeOptions | Gets information aout record page embedding and sets colSpan |
| createInvoice | recordId, recentOrdersDateFilter | The master list holding all items is this.itemList, this lis |
| createInvoiceMobile | recordId, recentOrdersDateFilter | The master list holding all items is this.itemList, this lis |
| createPromotions | defaultToChainLevel | Change the name of the Promotion |
| deactivatePromotionsModal | duplicatePromotions, promoStartDate, promoEndDate, frontLinePromotion | Format data for display |
| invoiceSignaturePad |  |  |
| itemDetails | isMobile, isOffline, accountId, isPhone, ,  |  |
| itemHistoryTile | accountId, title,  |  |
| itemInfoTile | isMobile, isOffline,  |  |
| promotionsTile | title,  |  |
| purchaseTile | title, ,  |  |
| relatedAllocationsModal | relatedAllocationsList, lookupType | Created by BrysonCarroll on 8/6/24. |
| relatedPromotionsModal | , isMobile | Closes the modal |
| retailInventoryTile | title, isMobile, , , , ,  | Handles the change event for the shelf quantity input. |
| sellFromTruck | recordId, objectApiName |  |
| signaturePad | , , , , , font, nameInputLabel, padLabel, getSignature(includePadColor, clearSignature() |  |

