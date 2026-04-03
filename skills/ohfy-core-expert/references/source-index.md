# OHFY-Core Source Index
> Last synced: 2026-04-03T12:18:16Z | Commit: fc4299ea | Repo: Ohanafy/OHFY-Core

## Apex Classes (583 production, 10 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| BA_AccountItem_Updater | public | This class is used to update the fields for the Account Item object |
| B_AccountItem_HistoryTracker | public | const map of RI types to the corresponding AI field |
| B_AccountItem_HistoryTracker_T | public |  |
| S_Update_AccountItems | global | This Schedulable class is used to schedule the batch class BA_Accou |
| S_Update_AccountItems_T | public | Test class for S_Update_AccountItems. This class tests that BA_Acco |
| B_Account_AccountBalanceUpdater | global | This class updates the Account Balance field on Account every day w |
| B_Account_AccountBalanceUpdater_T | public |  |
| B_Delivery_LockDeliveries | public | Locks deliveries for tomorrow's date |
| B_Delivery_StatusUpdater | global | This class checks the status of Delivery records each day and updat |
| B_Delivery_StatusUpdater_T | public |  |
| B_Route_DeliveryCreator | global | This class is used to create an deliveries for active routes. |
| B_Route_DeliveryCreator_T | public |  |
| S_Delivery_LockDeliveries | global | Method called on a specific schedule |
| S_Delivery_LockDeliveries_T | public |  |
| B_DisplayItem_Updater | public | This class is used to update the fields for the Display Item object |
| S_Update_DisplayItems | global | This Schedulable class is used to schedule the batch class B_Displa |
| S_Update_DisplayItems_T | public | Test class for S_Update_DisplayItems. This class tests that B_Displ |
| BA_EmailBatcher | public |  |
| BA_EmailBatcher_T | public |  |
| BA_MassEmailDispatch | public |  |
| BA_Inventory_ValueCalculator | public |  |
| B_Inventory_HistoryTracker | global | This class creates an Inventory History record every day to record |
| B_Inventory_HistoryTracker_T | public |  |
| B_Inventory_ValueCalculator | global |  |
| B_Inventory_ValueCalculator_T | public | This test class covers both B_Inventory_ValueCalculator and BA_Inventory_ValueCa |
| B_Invoice_LockInvoices | public | Locks picked invoices for tomorrow's date |
| S_Invoice_LockInvoices | global | Method called on a specific schedule |
| S_Invoice_LockInvoices_T | public |  |
| BA_Location_InventoryCreator | public | Created by alexsomer on 6/27/24. |
| B_Order_MetricUpdater | public | Batch class that gets recently completed invoices and updates the T |
| S_Order_MetricUpdater | global | Schedulable class intended to run nightly. Calls B_Order_MetricUpda |
| S_Order_MetricUpdater_T | public | Test class for S_Order_MetricUpdater. This class tests that B_Order |
| B_Pricelist_FrontLinePromotionSetter | public |  |
| B_Pricelist_FrontLinePromotionSetter_T | public |  |
| B_Pricelist_PricelistSetter | public | Grab all pricelists on their start date and sets them for all rel |
| S_Pricelist_PricelistSetter | global | Schedulable class intended to run each morning.  Calls B_Pricelist |
| S_Pricelist_PricelistSetter_T | public |  |
| S_AccountItem_HistoryTracker | global |  |
| E_Accounts_Offline | public |  |
| E_Adjustment_AccountingKeySetter | public |  |
| E_Forecasting_GetHistoricalRecords | public |  |
| E_Forecasting_GetHistoricalRecords_T | public |  |
| E_Forecasting_GetRecords | public |  |
| E_Forecasting_GetRecords_T | public |  |
| E_Allocations | public | Created by grantrisk on 5/15/24. |
| E_Allocations_T | public | Created by grantrisk on 5/20/24. |
| E_Credits | public | Get all credits for an invoice that are not picked up and are inven |
| E_Credits_T | public |  |
| E_Delivery_Fees | public |  |
| E_Delivery_Fees_T | public |  |
| E_Delivery_FieldUpdater | public | Executable to update the following fields on a Delivery Object |
| E_Delivery_FieldUpdater_T | public |  |
| E_Delivery_Items | public | Get the unsellable quantity for a truck inventory |
| E_Delivery_Items_T | public |  |
| E_Delivery_KanbanBoard | public | Apex method to fetch the updated delivery weight and UOM for a specified deliver |
| E_Delivery_KanbanBoard_T | public |  |
| E_Delivery_Palletization | public |  |
| E_Delivery_Palletization_T | public |  |
| E_Delivery_SalePrice | public |  |
| E_Delivery_SalePrice_T | public |  |
| E_CreateDisplayRun | public |  |
| E_CreateDisplayRun_T | public |  |
| E_GetItemsMap | public | Apex Class responsible for retrieving Items mapping. |
| E_GetItemsMap_T | public |  |
| E_GetPurchaseOrderItems | public |  |
| E_GetPurchaseOrderItems_T | public |  |
| E_LookupController | public | The class is the underlying controller that holds methods in suppor |
| E_LookupController_T | public |  |
| E_FileController | public |  |
| E_FileController_T | public |  |
| E_Goals | public |  |
| E_Goals_T | public |  |
| E_Incentives | public |  |
| E_Incentives_T | public |  |
| E_GetInventoryLevels | public | The class finds the inventory records for the items within the curr |
| E_GetInventoryLevels_T | public |  |
| E_InventoryReceipt_Adjustments | public |  |
| E_InventoryReceipt_Adjustments_T | public |  |
| E_InventoryReceipt_Fees | public |  |
| E_InventoryReceipt_Fees_T | public |  |
| E_InventoryReceipt_Items | public | Returns default inventory locations for items under a warehouse hie |
| E_InventoryReceipt_Items_T | public |  |
| E_InventoryReceipt_PurchasePrice | public |  |
| E_InventoryReceipt_PurchasePrice_T | public |  |
| E_DeliveryInvoice_Invoices | public |  |
| E_DeliveryInvoice_Invoices_T | public |  |
| E_Invoice_Adjustments | public | Order items will either be lot tracked or non lot tracked. The lot tracked items |
| E_Invoice_Adjustments_T | public | This test demonstrates the following |
| E_Invoice_Configuration | public |  |
| E_Invoice_Fees | public |  |
| E_Invoice_Fees_T | public |  |
| E_Invoice_Items | public |  |
| E_Invoice_Items_T | public |  |
| E_Invoice_SalePrice | public |  |
| E_Invoice_SignatureController | public | Created by nickbuono on 7/8/24. |
| E_Invoice_SignatureController_T | public | Created by thomasspangler on 8/5/24. |
| E_Item_ComponentCreator | public |  |
| E_Item_ComponentCreator_T | public | Created by nickbuono on 5/7/24. |
| E_Item_InventoryValueUpdater | public |  |
| E_Item_RelatedRecords | public |  |
| E_Item_RelatedRecords_T | public |  |
| E_LocationHierarchy | public | Created by Cullin Capps on 1/23/24. |
| E_LocationHierarchy_T | public |  |
| E_LocationInventory_Adjustments | public |  |
| E_LocationInventory_Adjustments_T | public |  |
| E_LocationInventory_Inventory | public |  |
| E_LocationInventory_Inventory_T | public |  |
| E_LocationInventory_Items | public |  |
| E_LocationInventory_Items_T | public |  |
| E_Location_Inventory | public | E_Location_Inventory is a class with a single AuraEnabled method, g |
| E_Location_Inventory_T | public |  |
| E_MassCreateOrders | public | Created by BrysonCarroll on 8/29/24. |
| E_MassCreateOrders_T | public | Created by BrysonCarroll on 8/29/24. |
| E_OrderItem_Items | public |  |
| E_OrderItem_Items_T | public | Created by BrysonCarroll on 8/21/24. |
| E_Order_Items | public | This class is used grab all item records selected in the Front-end |
| E_Order_Items_T | public |  |
| E_Order_TableMessages | public | This class is used to set the delivery message on the Order Table a |
| E_Order_TableMessages_T | public |  |
| E_Pallets | public |  |
| E_Pallets_T | public |  |
| E_PricelistGroup_Settings | public |  |
| E_PricelistGroup_Settings_T | public |  |
| E_PricelistGroup_Tiers | public |  |
| E_PricelistGroup_Tiers_T | public |  |
| E_PricelistItem_Items | public |  |
| E_PricelistItem_Items_T | public |  |
| E_Promotions | public |  |
| E_Promotions_T | public |  |
| E_PurchaseOrder_Items | public | This class is used grab all item records selected in the Front-end |
| E_PurchaseOrder_Items_T | public |  |
| MavtronUtilityProcessor | public | Deprecated |
| PrintJob | global | This class is used as the collection for when multiple prints are done. This i |
| P_MerchantController | public | Updates the Merchant Status when a new payments user begins an appl |
| P_MerchantController_T | public | Test the controller with no record ID provided |
| P_ProcessingAgreementController | public |  |
| P_ProcessingAgreementController_T | public |  |
| Q_ProcessInvoice | public |  |
| Q_ProcessInvoice_T | public |  |
| Q_ProcessPicking | public |  |
| Q_ProcessPicking_T | public |  |
| Q_Item_InventoryCreator | public | Class to asynchronously create inventory records for all applicable locations |
| Q_Item_InventoryCreator_T | public |  |
| Q_Location_InventoryCreator | public | Class to asynchronously create inventory records for all applicable non-spirit i |
| Q_Location_InventoryCreator_T | public |  |
| Q_Location_InventoryDeleter | public | Created by nickbuono on 1/30/24. |
| Q_MassPickDelivery | public |  |
| Q_MassPickDelivery_T | public |  |
| Q_CreatePricelistItems | public |  |
| QA_AllocationsTableController | public | Created by BrysonCarroll on 8/1/24. |
| QA_AllocationsTableController_T | public | Created by BrysonCarroll on 8/1/24. |
| QA_AddToTruckController | public | For all credits, if the item associated with the credit does not ha |
| QA_AddToTruckController_T | public |  |
| QA_CreditController | public |  |
| QA_CreditController_T | public |  |
| QA_DeliveryBackfillInvoicesController | public |  |
| QA_DeliveryBackfillInvoicesController_T | public |  |
| QA_DeliveryInvoiceTableController | public |  |
| QA_DeliveryTransferTableController | public | Controller for the Delivery Transfer Table component. This class is |
| QA_DeliveryTransferTableController_T | public |  |
| QA_DeliveryUpdateInvoicesController | public |  |
| QA_DeliveryUpdateInvoicesController_T | public |  |
| QA_TransferToTruckController | public |  |
| QA_TransferToTruckController_T | public |  |
| QA_CreateDisplayRunController | public | Created by Alex-Somer on 10/15/24. |
| QA_CreateDisplayRunController_T | public | Created by Alex-Somer on 10/15/24. |
| QA_AccountGoalCreatorController | public | Created by thomasspangler on 1/20/24. |
| QA_AccountGoalCreatorController_T | public | Created by thomasspangler on 1/21/24. |
| QA_CreateGoalsController | public |  |
| QA_CreateGoalsController_T | public |  |
| QA_IncentiveTableController | public | Created by Brson Carroll (10/23/2024) |
| QA_IncentiveTableController_T | public |  |
| QA_InventoryReceiptTableController | public |  |
| QA_InventoryReceiptTableController_Lot_T | public |  |
| QA_InventoryReceiptTableController_T | public |  |
| QA_UpdateIRITableController | public |  |
| QA_UpdateIRITableController_T | public |  |
| QA_CancelInvoiceController | public |  |
| QA_CancelInvoiceController_T | public |  |
| QA_DeliveryPickingTableController | public | takes in necessary data to adjust invoice items and create inventor |
| QA_DeliveryPickingTableController_T | public |  |
| QA_InvoiceTableController | public | This class is used to create an invoice from the order page. |
| QA_InvoiceTableController_T | public |  |
| QA_UpdateInvoiceController | public |  |
| QA_UpdateInvoiceController_T | public |  |
| QA_AssignTiersController | public | This class assigns tiers to pricelist items. |
| QA_AssignTiersController_T | public |  |
| QA_ItemTransferController | public | Created by masonromant on 10/10/24. |
| QA_ItemTransferController_T | public |  |
| QA_ProductReturnController | public | Created By: Bryson Carroll |
| QA_ProductReturnController_T | public |  |
| QA_LocationInventoryLogTableController | public |  |
| QA_LocationInventoryLogTableController_T | public |  |
| QA_LocationTransferController | public |  |
| QA_LocationTransferController_T | public |  |
| QA_MassCreateOrdersController | public | Created by BrysonCarroll on 8/29/24. |
| QA_MassCreateOrdersController_T | public | Created by BrysonCarroll on 8/29/24. |
| QA_AddOrderItemController | public | Adds an item to an order |
| QA_AddOrderItemController_T | public |  |
| QA_MarkAsUnsoldController | public |  |
| QA_MarkAsUnsoldController_T | public |  |
| QA_OrderItemTableController | public | This class is used to update the order item quantity, discount and |
| QA_OrderItemTableController_T | public |  |
| QA_SellFromTruckController | public |  |
| QA_SellFromTruckController_T | public |  |
| QA_OrderTableController | public | This class is used to create an order from the order table componen |
| QA_OrderTableController_Communities | public | This class is used to create an order from the order table componen |
| QA_OrderTableController_Communities_T | public | Created by cullincapps on 1/12/24. |
| QA_OrderTableController_Distro | public | This class is used to create an order from the order table componen |
| QA_OrderTableController_Distro_T | public |  |
| QA_OrderTableController_T | public |  |
| QA_ManualPalletizationController | public |  |
| QA_ManualPalletizationController_T | public |  |
| QA_CreatePaymentMethod | public |  |
| QA_CreatePaymentMethod_T | public | Created by alexsomer on 3/12/24. |
| QA_CreatePricelistController | public |  |
| QA_CreatePricelistController_T | public |  |
| QA_PricelistCloner | public |  |
| QA_PricelistCloner_T | public |  |
| QA_PricelistItemController | public | Takes a list of Pricelist_Item__c records and updates the price of |
| QA_PricelistItemController_T | public |  |
| QA_ClonePricelistGroup | public |  |
| QA_ClonePricelistGroup_T | public |  |
| QA_PricelistSettingController | public | Takes a list of Pricelist_Setting__c records and updates the price |
| QA_PricelistSettingController_T | public |  |
| QA_CreatePromotionsTableController | public |  |
| QA_CreatePromotionsTableController_T | public |  |
| QA_PromotionsController | public |  |
| QA_PurchaseOrderTableController | public |  |
| QA_PurchaseOrderTableController_T | public |  |
| QA_UpdatePurchaseOrderController | public | This method is used to get the list of purchase order items for a g |
| QA_UpdatePurchaseOrderController_T | public |  |
| S_Accounting | public |  |
| S_Accounting_Delete | public |  |
| S_Accounting_Insert | public |  |
| S_Accounting_Insert_T | public |  |
| S_Accounting_Wrapper | public |  |
| S_Adjustment_Converter | public | This class converts Inventory_Adjustment__c records into a wrapper |
| S_Adjustment_Delete | public | This class is responsible for deleting inventory adjustments based |
| S_Adjustment_Insert | public | This class is responsible for inserting inventory adjustments based |
| S_Adjustment_Update | public | This class is responsible for updating inventory adjustments based |
| S_Adjustment_Wrapper | public | This is a wrapper class for managing inventory adjustments. The Adj |
| S_Adjustments | public | This class is responsible for routing adjustments to the appropriat |
| S_Adjustments_T | public | 🔄 TODO |
| S_Exceptions | public |  |
| S_Deliveries | public | Service class for deliveries to handle crud operations associated w |
| S_Lots | public | This class is used to handle the creation and updating of lots and |
| S_Lots_T | public |  |
| S_Pricelist | public | @author Bryson Carroll |
| S_Pricelist_T | public |  |
| S_PricingAdjustments | public |  |
| S_PricingAdjustments_T | public |  |
| S_Promotions | public |  |
| S_Promotions_T | public |  |
| TA_Account_AI_LostPlacement | public |  |
| TA_Account_AI_LostPlacement_T | public |  |
| TA_Account_AI_OfflineCreationHandler | public |  |
| TA_Account_AI_OfflineCreationHandler_T | public |  |
| TA_Account_AU_InvoiceUpdater | public |  |
| TA_Account_AU_InvoiceUpdater_T | public |  |
| TA_Account_AU_OfflineUpdater | public |  |
| TA_Account_AU_OfflineUpdater_T | public |  |
| TA_Account_BI_OfflineCreationHandler | public |  |
| TA_Account_BI_OfflineCreationHandler_T | public |  |
| TA_Account_BI_ProcessingFeeHandler | public |  |
| TA_Account_BI_ProcessingFeeHandler_T | public |  |
| TA_Account_BU_ProcessingFeeHandler | public |  |
| TA_Account_BU_ProcessingFeeHandler_T | public |  |
| TA_Commitment_AI_OfflineCommitmentItems | public |  |
| TA_Commitment_AI_OfflineCommitment_T | public |  |
| TA_Contact_AI_PrimaryContacts | public |  |
| TA_Contact_AI_PrimaryContacts_T | public |  |
| TA_Contact_AU_PrimaryContacts | public |  |
| TA_Contact_AU_PrimaryContacts_T | public |  |
| TA_Credit_AD_InvoiceUpdater | public |  |
| TA_Credit_AD_InvoiceUpdater_T | public |  |
| TA_Credit_AI_OfflineCreator | public |  |
| TA_Credit_AI_OfflineCreator_T | public |  |
| TA_Credit_AU_CreditAmountUpdater | public |  |
| TA_Credit_AU_CreditAmountUpdater_T | public |  |
| TA_Credit_AU_InvoiceUpdater | public |  |
| TA_Credit_AU_InvoiceUpdater_T | public |  |
| TA_Credit_AU_OfflineAddToTruck | public |  |
| TA_Credit_AU_OfflineAddToTruck_T | public |  |
| TA_Credit_BU_OfflineAddToTruck | public |  |
| TA_Credit_BU_OfflineAddToTruck_T | public |  |
| TA_Delivery_AU_Completer | public |  |
| TA_Delivery_AU_Completer_T | public |  |
| TA_Delivery_AU_DateChanger | public | This trigger updates Date fields on the Order and Invoice that are |
| TA_Delivery_AU_DateChanger_T | public |  |
| TA_Delivery_AU_FieldUpdater | public |  |
| TA_Delivery_BI_DuplicateChecker | public |  |
| TA_Delivery_BI_DuplicateChecker_T | public |  |
| TA_Delivery_BU_InvoiceStatusUpdater | public | This trigger takes a list of updated deliveries and, if the status |
| TA_Delivery_BU_InvoiceStatusUpdater_T | public |  |
| TA_Delivery_BU_NameUpdater | public | This trigger updates the Delivery Name after the Delivery Date fiel |
| TA_Delivery_BU_NameUpdater_T | public |  |
| TA_DistrPlacement_AI_LastOrderDate | public |  |
| TA_DistrPlacement_AI_LastOrderDate_T | public |  |
| TA_Equipment_BI_LocationCreator | public | This trigger action takes a newly inserted equipment record and cre |
| TA_Equipment_BI_LocationCreator_T | public |  |
| TA_Event_AD_GoalActivityDeleter | public |  |
| TA_Event_AD_GoalActivityDeleter_T | public |  |
| TA_Event_AI_GoalActivityCreator | public |  |
| TA_Event_AI_GoalActivityCreator_T | public |  |
| TA_Event_AU_GoalActivityCreator | public |  |
| TA_Event_AU_GoalActivityCreator_T | public |  |
| TA_Event_AU_GoalUpdater | public |  |
| TA_Event_AU_GoalUpdater_T | public |  |
| TA_GoalTracking_AD_JunctionDeleter | public |  |
| TA_GoalTracking_AD_JunctionDeleter_T | public |  |
| TA_GoalTracking_AI_JunctionCreator | public |  |
| TA_GoalTracking_AI_JunctionCreator_T | public |  |
| TA_GoalTracking_AU_IncentiveUpdater | public |  |
| TA_GoalTracking_AU_IncentiveUpdater_T | public |  |
| TA_Incentive_AU_BillBackUpdater | public |  |
| TA_Incentive_AU_BillBackUpdater_T | public |  |
| TA_Incentive_AU_GoalContributionSetter | public |  |
| TA_Incentive_AU_GoalContributionSetter_T | public |  |
| TA_Inventory_AU_QuantityCalculator | public | This class calculates On-Hand, Available, and Value for Inventory r |
| TA_Inventory_AU_QuantityCalculator_T | public |  |
| TA_Inventory_BI_DuplicateChecker | public |  |
| TA_Inventory_BU_DefaultLocationCheck | public |  |
| TA_Inventory_BU_DefaultLocationCheck_T | public |  |
| TA_Inventory_BU_PreventNegInventory_T | public | Created by grantrisk on 2/7/24. |
| TA_Inventory_BU_PreventNegativeInventory | public | Prevents negative inventory quantities during the 'before update' trigger event |
| TA_Inventory_BU_StatusChecker | public |  |
| TA_Adjustment_BI_AccountingKeySetter | public |  |
| TA_Adjustment_BU_AccountingKeySetter | public |  |
| TA_InventoryLog_AU_StatusUpdater | public |  |
| TA_InventoryLog_AU_StatusUpdater_T | public |  |
| TA_InventoryLog_BD_AdjRemover | public |  |
| TA_InventoryLog_BD_AdjRemover_T | public |  |
| TA_InventoryLogGroup_AU_ApproveLogs | public |  |
| TA_InventoryLogGroup_AU_ApproveLogs_T | public |  |
| TA_InventoryReceipt_AU_AdjStUpdater_T | public |  |
| TA_InventoryReceipt_AU_AdjStatusUpdater | public |  |
| TA_InventoryReceipt_AU_Canceller | public |  |
| TA_InventoryReceipt_AU_Canceller_T | public |  |
| TA_InventoryReceipt_AU_KegCalculator | public |  |
| TA_InventoryReceipt_AU_KegCalculator_T | public |  |
| TA_IR_BU_ItemQuantUpdater_T | public |  |
| TA_InventoryReceipt_BU_ItemQuantUpdater | public |  |
| TA_IRItem_AU_AdjUpdater | public |  |
| TA_IRItem_AU_AdjUpdater_T | public |  |
| TA_IRItem_BI_CreationPreventor | public |  |
| TA_IRItem_BI_CreationPreventor_T | public |  |
| TA_Invoice_AD_InvoiceGroupUpdater | public |  |
| TA_Invoice_AD_InvoiceGroupUpdater_T | public |  |
| TA_Order_AD_DeliveryFieldsUpdater | public |  |
| TA_Order_AD_DeliveryFieldsUpdater_T | public |  |
| TA_Invoice_AI_OfflineCreationHandler | public | Passing the whole ii as a key to orderItemToItemID g |
| TA_Invoice_AI_OfflineCreationHandler_T | public |  |
| TA_Order_AI_DeliveryAssociator | public |  |
| TA_Order_AI_DeliveryAssociator_T | public |  |
| TA_Order_AI_GoalInvoiceCreator | public |  |
| TA_Order_AI_GoalInvoiceCreator_T | public |  |
| TA_Invoice_AU_AdjStatusUpdater | public |  |
| TA_Invoice_AU_AdjStatusUpdater_T | public |  |
| TA_Invoice_AU_Canceller | public |  |
| TA_Invoice_AU_Canceller_T | public |  |
| TA_Invoice_AU_Completer | public |  |
| TA_Invoice_AU_Completer_T | public |  |
| TA_Invoice_AU_DeliveryAssociator | public |  |
| TA_Invoice_AU_DeliveryAssociator_T | public |  |
| TA_Invoice_AU_InvoiceAdjustmentUpdater | public |  |
| TA_Invoice_AU_InvoiceAdjustmentUpdater_T | public |  |
| TA_Invoice_AU_InvoiceGroupUpdater | public |  |
| TA_Invoice_AU_InvoiceGroupUpdater_T | public |  |
| TA_Invoice_AU_OfflineUpdateInvoice | public |  |
| TA_Invoice_AU_OfflineUpdateInvoice_T | public |  |
| TA_Invoice_AU_PalletItemUpdater | public |  |
| TA_Invoice_AU_PalletItemUpdater_T | public |  |
| TA_Invoice_AU_SendEmail | public |  |
| TA_Invoice_AU_SendEmail_T | public |  |
| TA_Invoice_AU_TruckLoader | public |  |
| TA_Order_AU_GoalUpdater | public |  |
| TA_Order_AU_GoalUpdater_T | public |  |
| TA_Order_AU_NameSetter | public |  |
| TA_Order_AU_NameSetter_T | public |  |
| TA_Order_AU_PlacementUpdater | public |  |
| TA_Order_AU_PlacementUpdater_T | public |  |
| TA_Order_AU_PromotionUpdater | public |  |
| TA_Order_AU_PromotionUpdater_T | public |  |
| TA_Order_AU_ReorderCloner | public |  |
| TA_Order_AU_ReorderCloner_T | public |  |
| TA_Invoice_BD_AdjDeleter | public | Created by nickbuono on 11/27/23. |
| TA_Invoice_BD_AdjDeleter_T | public |  |
| TA_Order_BD_GoalUpdater | public |  |
| TA_Order_BD_GoalUpdater_T | public |  |
| TA_Order_BD_PromoInvoiceItemDeleter | public |  |
| TA_Order_BD_PromoInvoiceItemDeleter_T | public |  |
| TA_Invoice_BI_OfflineCreationHandler | public |  |
| TA_Invoice_BI_OfflineCreationHandler_T | public |  |
| TA_Invoice_BU_PaymentInfo | public | This trigger is dedicated to keeping the payment due date in sync w |
| TA_Invoice_BU_PaymentInfo_T | public |  |
| TA_Invoice_BU_StatusUpdater | public |  |
| TA_Invoice_BU_StatusUpdater_T | public |  |
| TA_Order_BU_DeliveryAssociator | public |  |
| TA_Order_BU_DeliveryAssociator_T | public |  |
| TA_InvoiceFee_AD_InvoiceUpdater | public |  |
| TA_InvoiceFee_AD_InvoiceUpdater_T | public |  |
| TA_InvoiceFee_AI_InvoiceUpdater | public |  |
| TA_InvoiceFee_AI_InvoiceUpdater_T | public |  |
| TA_InvoiceFee_AU_InvoiceUpdater | public |  |
| TA_InvoiceFee_AU_InvoiceUpdater_T | public |  |
| TA_OrderItem_AD_DeliveryFieldsUpdater | public |  |
| TA_OrderItem_AD_DeliveryFieldsUpdater_T | public |  |
| TA_InvoiceItem_AI_OfflineCreationHandler | public | Passing the whole ii as a key to orderItemToItemID g |
| TA_InvoiceItem_AI_OfflineCreation_T | public |  |
| TA_InvoiceItem_AI_OfflineSellFromTruck | public |  |
| TA_InvoiceItem_AI_OfflineSellFromTruck_T | public |  |
| TA_OrderItem_AI_AccountItems | public |  |
| TA_OrderItem_AI_AccountItems_T | public |  |
| TA_OrderItem_AI_ManualUpdates | public | This class handle manual Order Items being added to an Order throug |
| TA_OrderItem_AI_ManualUpdates_T | public |  |
| TA_InvoiceItem_AU_AdjUpdater | public |  |
| TA_InvoiceItem_AU_AdjUpdater_T | public |  |
| TA_InvoiceItem_AU_KegDepositUpdater | public | This Trigger is used to update the Keg Deposit for the Invoice Item when the Ord |
| TA_InvoiceItem_AU_KegDepositUpdater_T | public |  |
| TA_InvoiceItem_AU_OfflineMarkUnsold | public |  |
| TA_InvoiceItem_AU_OfflineMarkUnsold_T | public |  |
| TA_InvoiceItem_AU_OfflineSellFromTruck | public |  |
| TA_InvoiceItem_AU_OfflineSellFromTruck_T | public |  |
| TA_InvoiceItem_AU_OfflineUpdateInvoice | public |  |
| TA_InvoiceItem_AU_OfflineUpdateInvoice_T | public |  |
| TA_InvoiceItem_BD_AdjDeleter | public | Created by nickbuono on 11/27/23. |
| TA_InvoiceItem_BD_AdjDeleter_T | public |  |
| TA_InvoiceItem_BD_PromotionIIDeleter | public |  |
| TA_InvoiceItem_BD_PromotionIIDeleter_T | public |  |
| TA_InvoiceItem_BI_ApplyAdjustments | public |  |
| TA_InvoiceItem_BI_ApplyAdjustments_T | public |  |
| TA_InvoiceItem_BI_DeliverySetter | public |  |
| TA_InvoiceItem_BI_DeliverySetter_T | public |  |
| TA_InvoiceItem_BI_OfflineCreationHandler | public |  |
| TA_InvoiceItem_BI_OfflineCreation_T | public |  |
| TA_OrderItem_BI_AutoApplyPromotions | public |  |
| TA_OrderItem_BI_AutoApplyPromotions_T | public |  |
| TA_OrderItem_BI_DuplicateChecker | public |  |
| TA_OrderItem_BI_DuplicateChecker_T | public |  |
| TA_InvoiceItem_BU_ApplyAdjustments | public |  |
| TA_InvoiceItem_BU_ApplyAdjustments_T | public |  |
| TA_InvoiceItem_BU_AutoApplyPromotions | public |  |
| TA_InvoiceItem_BU_AutoApplyPromotions_T | public |  |
| TA_Item_AI_InventoryCreator | public |  |
| TA_Item_AI_InventoryCreator_T | public |  |
| TA_Item_AI_PricelistItemCreator | public |  |
| TA_Item_AI_PricelistItemCreator_T | public |  |
| TA_Item_AU_InventoryValueUpdater | public | This class forces the TA_Inventory_AU_InventoryValueUpdater trigger |
| TA_Item_AU_InventoryValueUpdater_T | public |  |
| TA_Item_AU_PricelistItemUpdater | public |  |
| TA_Item_AU_PricelistItemUpdater_T | public |  |
| TA_Item_BD_ChildRemover | public | This class deletes Control State Codes associated to an Item |
| TA_Item_BD_ChildRemover_T | public |  |
| TA_Item_BI_SetUOMConversion | public |  |
| TA_Item_BI_SetUOMConversion_T | public |  |
| TA_Item_BI_ShortNameSetter | public | Created by nickbuono on 9/13/24. |
| TA_Item_BI_ShortNameSetter_T | public | Created by nickbuono on 9/13/24. |
| TA_Item_BU_StatusChecker | public |  |
| TA_Item_BU_StatusChecker_T | public |  |
| TA_Item_BU_UpdateUOMConversion | public |  |
| TA_Item_BU_UpdateUOMConversion_T | public |  |
| TA_ItemTransfer_AI_AdjustmentCreator | public | This trigger action creates an inventory adjustment for each item t |
| TA_ItemTransfer_AI_AdjustmentCreator_T | public |  |
| TA_ItemType_AI_ItemCreator | public |  |
| TA_ItemType_AI_ItemCreator_T | public | There are 6 items |
| TA_ItemType_AI_TierSettingCreator | public | Created by thomasspangler on 2/14/24. |
| TA_ItemType_AI_TierSettingCreator_T | public | Created by thomasspangler on 2/22/24. |
| TA_Location_AI_InventoryCreator | public |  |
| TA_Location_AI_InventoryCreator_T | public |  |
| TA_Location_BD_InventoryDeleter | public | Created by nickbuono on 1/29/24. |
| TA_Location_BD_InventoryDeleter_T | public | Created by nickbuono on 1/29/24. |
| TA_Location_BU_StatusChecker | public |  |
| TA_Lot_AI_LotInventoryCreator | public |  |
| TA_Lot_AI_LotInventoryCreator_T | public |  |
| TA_Lot_AU_CostUpdater | public |  |
| TA_Lot_AU_CostUpdater_T | public |  |
| TA_LotInventory_AU_ParentLotUpdater | public |  |
| TA_LotInventory_AU_ParentLotUpdater_T | public | Tests if `Lot_Inventory__c` records associated with the lot tracked |
| TA_PaymentMethod_BI_DefaultChecker | public |  |
| TA_PaymentMethod_BI_DefaultChecker_T | public |  |
| TA_POItem_AD_AdjRemover | public |  |
| TA_POItem_AD_AdjRemover_T | public |  |
| TA_POItem_AI_AdjUpdater | public |  |
| TA_POItem_AI_AdjUpdater_T | public |  |
| TA_POItem_AU_AdjUpdater | public |  |
| TA_POItem_AU_AdjUpdater_T | public |  |
| TA_POItem_BD_AdjRemover | public |  |
| TA_POItem_BD_AdjRemover_T | public |  |
| TA_POItem_BU_TotalCostUpdater | public |  |
| TA_POItem_BU_TotalCostUpdater_T | public |  |
| TA_Pricelist_AI_PricelistItemCreator | public |  |
| TA_Pricelist_AI_PricelistItemCreator_T | public |  |
| TA_Pricelist_AU_DiscountUpdater | public |  |
| TA_Pricelist_AU_DiscountUpdater_T | public |  |
| TA_PricelistItem_AI_PriceSetter | public |  |
| TA_PricelistItem_AI_PriceSetter_T | public |  |
| TA_PricelistItem_AU_DiscountCalculator | public |  |
| TA_PricelistItem_AU_DiscountCalculator_T | public | Created by BrysonCarroll on 5/10/24. |
| TA_PricelistItem_BI_DuplicateChecker | public |  |
| TA_PricelistItem_BI_DuplicateChecker_T | public |  |
| TA_PricelistItem_AU_SettingsPriceUpdater | public |  |
| TA_PricelistSetting_AI_ItemsUpdater | public |  |
| TA_PricelistSetting_AI_ItemsUpdater_T | public | Created by BrysonCarroll on 5/10/24. |
| TA_PricelistSetting_AU_PricelistItems | public |  |
| TA_PricelistSetting_AU_PricelistItems_T | public |  |
| TA_TierSetting_AI_ItemsUpdater | public |  |
| TA_TierSetting_AI_ItemsUpdater_T | public |  |
| TA_TierSetting_AU_ItemTierUpdater | public |  |
| TA_TierSetting_AU_ItemTierUpdater_T | public |  |
| TA_PromoProduct_AI_FLPromotionSetter_T | public |  |
| TA_PromotionProduct_AI_FLPromotionSetter | public |  |
| TA_Promotion_AU_BillbackTracker | public |  |
| TA_Promotion_AU_BillbackTracker_T | public |  |
| TA_Promotion_AU_FLPromotionSetter | public |  |
| TA_Promotion_AU_FLPromotionSetter_T | public |  |
| TA_Promotion_BU_DuplicateChecker | public |  |
| TA_Promotion_BU_DuplicateChecker_T | public |  |
| TA_PurchaseOrder_AU_AdjStatusUpdater | public |  |
| TA_PurchaseOrder_AU_AdjStatusUpdater_T | public |  |
| TA_PurchaseOrder_AU_Canceller | public |  |
| TA_PurchaseOrder_AU_Canceller_T | public |  |
| TA_PurchaseOrder_AU_NameSetter | public |  |
| TA_PurchaseOrder_AU_NameSetter_T | public |  |
| TA_PurchaseOrder_BD_AdjRemover | public |  |
| TA_PurchaseOrder_BD_AdjRemover_T | public |  |
| TA_PurchaseOrder_BU_Completer | public |  |
| TA_PurchaseOrder_BU_Completer_T | public |  |
| TA_AI_RelatedContactCreator | public |  |
| TA_AI_RelatedContactCreator_T | public |  |
| TA_Task_AD_GoalActivityDeleter | public |  |
| TA_Task_AD_GoalActivityDeleter_T | public |  |
| TA_Task_AI_GoalActivityCreator | public |  |
| TA_Task_AI_GoalActivityCreator_T | public |  |
| TA_Task_AU_GoalActivityCreator | public |  |
| TA_Task_AU_GoalActivityCreator_T | public |  |
| TA_Task_AU_GoalUpdater | public |  |
| TA_Task_AU_GoalUpdater_T | public |  |
| TA_TransferGroup_AU_AdjStatusUpdater | public |  |
| TA_TransferGroup_AU_AdjStatusUpdater_T | public |  |
| U_InvoiceAdjDeleter | public | This class is used to revert Inventory Adjustments back to their or |
| UtilityMethods | public | Created by cullincapps on 9/19/23. |
| MetadataDeploy | public |  |
| MetadataDeploy_T | public | Test the changeConfigPreferenceActiveStatus method |
| MetadataTriggerHandler | global |  |
| U_ConfigurationPreferenceMDT | public |  |
| U_ConfigurationPreferenceMDT_T | public |  |
| U_FieldsetCustomizationMDT | public | A Utility class for interacting with the Fieldset_Customization__md |
| U_FieldsetCustomizationMDT_T | public |  |
| U_UOM_NameTranslationMDT | public | Created by nickbuono on 9/13/24. |
| U_Delivery_Items | public |  |
| U_Delivery_Items_T | public | Created by thomasspangler on 8/5/24. |
| U_SendEmailService | public | - This method sends an email to the specified recipients with the s |
| U_SendEmailService_T | public |  |
| U_ParseErrorMessage | global | A utility class for parsing custom error messages embedded within a larger error |
| U_ParseErrorMessage_T | public |  |
| U_FieldUtility | public | A Utility class for interacting with fields that are in fieldSets. |
| U_FieldUtility_T | public |  |
| U_FilePreviewTableController | public |  |
| U_FilePreviewTableController_T | public |  |
| U_Location_Hierarchy | public | @param itemIds item ids |
| U_Location_Hierarchy_T | public |  |
| U_GlobalDescribeCache | global | Class to handle caching of global describe information. |
| U_ObjectUtility | public | A utility class that is used to obtain records and its fields dynam |
| U_ObjectUtility_T | public |  |
| UtilityMethods | public | Created by cullincapps on 9/19/23. |
| UtilityMethods_T | public |  |
| Ohanafy360Controller | public |  |
| Ohanafy360Controller_T | public |  |
| U_OrderStatusValidationBypass | public | U_OrderStatusValidationBypass is a utility class that holds a static flag used t |
| U_Order_Items | public |  |
| U_Order_Items_T | public |  |
| U_ReturnsAndCreditsUtility | public |  |
| U_ReturnsAndCreditsUtility_T | public |  |
| U_TransformationSettingUtility | public | Utility class for handling unit of measure transformations. |
| U_TransformationSettingUtility_T | public | Created by grantrisk on 10/27/23. |
| FlowTriggerRecord | public |  |
| TriggerAction | global |  |
| TriggerActionFlow | public |  |
| TriggerBase | global |  |
| U_UserUtil | public | Created by cullincapps on 1/5/24. |
| U_UserUtil_T | public |  |
| U_UserUtilityExceptions | public | Created by cullincapps on 1/5/24. |

## Triggers (37)

| Trigger | sObject | Events |
|---------|---------|--------|
| AccountTrigger | Account |  |
| CommitmentTrigger | Commitment__c |  |
| ContactTrigger | Contact |  |
| CreditTrigger | Credit__c |  |
| DeliveryTrigger | Delivery__c |  |
| DistributorPlacementTrigger | Distributor_Placement__c |  |
| EquipmentTrigger | Equipment__c |  |
| EventTrigger | Event |  |
| GoalTrackingTrigger | Goal_Tracking__c |  |
| IncentiveTrigger | Incentive__c |  |
| InventoryAdjustmentTrigger | Inventory_Adjustment__c |  |
| InventoryLogGroupTrigger | Inventory_Log_Group__c |  |
| InventoryLogTrigger | Inventory_Log__c |  |
| InventoryReceiptItemTrigger | Inventory_Receipt_Item__c |  |
| InventoryReceiptTrigger | Inventory_Receipt__c |  |
| InventoryTrigger | Inventory__c |  |
| InvoiceFeeTrigger | Order_Fee__c |  |
| ItemTrigger | Item__c |  |
| ItemTypeTrigger | Item_Type__c |  |
| LocationTrigger | Location__c |  |
| LotInventoryTrigger | Lot_Inventory__c |  |
| LotTrigger | Lot__c |  |
| OrderItemTrigger | Order_Item__c |  |
| OrderTrigger | Order__c |  |
| PaymentMethodTrigger | Payment_Method__c |  |
| PricelistItemTrigger | Pricelist_Item__c |  |
| PricelistSettingTrigger | Pricelist_Setting__c |  |
| PricelistTrigger | Pricelist__c |  |
| PromotionProductTrigger | Promotion_Product__c |  |
| PromotionTrigger | Promotion__c |  |
| PurchaseOrderItemTrigger | Purchase_Order_Item__c |  |
| PurchaseOrderTrigger | Purchase_Order__c |  |
| RelatedAccountTrigger | Related_Account__c |  |
| TaskTrigger | Task |  |
| TierSettingTrigger | Tier_Setting__c |  |
| TransferGroupTrigger | Transfer_Group__c |  |
| TransferTrigger | Transfer__c |  |

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| TA_Account_AI_OfflineCreationHandler | afterInsert | `public static void afterInsert(List<Account> newAccounts) ` |
| TA_Account_BI_OfflineCreationHandler | beforeInsert | `public static void beforeInsert(List<Account> newAccounts) ` |
| TA_Account_BI_ProcessingFeeHandler | beforeInsert | `public static void beforeInsert(List<Account> newList) ` |
| TA_Account_BU_ProcessingFeeHandler | beforeUpdate | `public static void beforeUpdate(List<Account> newList, List<Account> oldList) ` |
| TA_Invoice_AI_OfflineCreationHandler | afterInsert | `public void afterInsert(List<Order__c> newList) ` |
| TA_Invoice_BI_OfflineCreationHandler | beforeInsert | `public void beforeInsert(List<Order__c> newList) ` |
| TA_InvoiceItem_AI_OfflineCreationHandler | afterInsert | `public void afterInsert(List<Order_Item__c> newList) ` |
| TA_InvoiceItem_BI_OfflineCreationHandler | beforeInsert | `public void beforeInsert(List<Order_Item__c> newList) ` |
| MetadataTriggerHandler | beforeInsert | `public void beforeInsert(List<SObject> newList) ` |
| MetadataTriggerHandler | afterInsert | `public void afterInsert(List<SObject> newList) ` |
| MetadataTriggerHandler | beforeUpdate | `public void beforeUpdate(List<SObject> newList, List<SObject> oldList) ` |
| MetadataTriggerHandler | afterUpdate | `public void afterUpdate(List<SObject> newList, List<SObject> oldList) ` |
| MetadataTriggerHandler | beforeDelete | `public void beforeDelete(List<SObject> oldList) ` |
| MetadataTriggerHandler | afterDelete | `public void afterDelete(List<SObject> oldList) ` |
| MetadataTriggerHandler | afterUndelete | `public void afterUndelete(List<SObject> newList) ` |
| MetadataTriggerHandler | bypass | `public static void bypass(String actionName) ` |
| MetadataTriggerHandler | clearBypass | `public static void clearBypass(String actionName) ` |
| MetadataTriggerHandler | isBypassed | `public static Boolean isBypassed(String actionName) ` |
| MetadataTriggerHandler | clearAllBypasses | `public static void clearAllBypasses() ` |
| U_SendEmailService | sendEmailWithTemplate | `public static void sendEmailWithTemplate(String subject, List<String> messages, List<String> recipientEmails) ` |

## Custom Objects & Fields

### Account (183 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABC_License_Expiration_Date__c | Date | false |  |
| ABC_License_Number__c | Text | false |  |
| AccountNumber |  | false |  |
| AccountSource | Picklist | false |  |
| Account_Balance__c | Currency | false |  |
| Account_Sub_Type__c | Picklist | false |  |
| Account_Type__c | Picklist | false |  |
| Active__c | Checkbox | false |  |
| AnnualRevenue |  | false |  |
| Auto_Assigned_Driver__c | Lookup | false | User |
| Auto_Bill__c | Checkbox | false |  |
| Auto_Send_Invoices__c | Checkbox | false |  |
| Average_Case_Equivalents__c | Number | false |  |
| Average_Order_Value__c | Currency | false |  |
| BOL_Tax_Type__c | Picklist | false |  |
| BillingAddress |  | false |  |
| Billing_Contact_Email__c | Text | false |  |
| Billing_Contact__c | Lookup | false | Contact |
| Billing_Street_Address__c | Text | false |  |
| Bond_Number__c | Text | false |  |
| Bypass_Transaction_Fees__c | Checkbox | false |  |
| Chain_Banner_Lookup__c | Lookup | false | Account |
| Channel__c | Picklist | false |  |
| Charge_Processing_Fee__c | Checkbox | false |  |
| Child_Account__c | Checkbox | false |  |
| Classification__c | Picklist | false |  |
| Cluster__c | Number | false |  |
| Company_Name__c | Text | false |  |
| Cooler_Selection__c | MultiselectPicklist | false |  |
| Cuisine_Type__c | MultiselectPicklist | false |  |
| Customer_Acknowledgment_Type__c | Picklist | false |  |
| Customer_Number__c | Text | false |  |
| Customer_Priority__c | Picklist | false |  |
| Customer_Since__c | Date | false |  |
| DUNS_Number__c | Text | false |  |
| DandbCompanyId | Lookup | false |  |
| Days_Since_Last_Activity__c | Number | false |  |
| Days_Since_Last_Order__c | Number | false |  |
| Delivery_Contact__c | Lookup | false | Contact |
| Delivery_Due_Date__c | Date | false |  |
| Delivery_Method__c | Picklist | false |  |
| Delivery_Pickup_Date__c | Date | false |  |
| Description |  | false |  |
| Distributor_Checkbox__c | Checkbox | false |  |
| Distributor_Rep__c | Lookup | false | Contact |
| Distributor_Vendor_ID_Number__c | Text | false |  |
| Distributor__c | Lookup | false | Account |
| Door_Zone__c | MultiselectPicklist | false |  |
| DunsNumber |  | false |  |
| EFT_Customer_ID__c | Text | false |  |
| EFT_Provider__c | Picklist | false |  |
| E_Commerce_Platform__c | Picklist | false |  |
| Email__c | Text | false |  |
| Energy_Provider__c | Checkbox | false |  |
| Event_Primary_Contact__c | Lookup | false | Contact |
| External_ID__c | Text | false |  |
| Fax |  | false |  |
| Federal_Tax_ID__c | Text | false |  |
| First_Sold_Date__c | Date | false |  |
| Fulfilled_From__c | Lookup | false | Location__c |
| GS1_Prefix__c | Text | false |  |
| Has_Been_Sold_To__c | Checkbox | false |  |
| Highest_Stop_Order__c | Summary | false |  |
| Industry | Picklist | false |  |
| Invoice_Notes__c | LongTextArea | false |  |
| Is_Chain_Banner__c | Checkbox | false |  |
| Jigsaw |  | false |  |
| Keg_Deposit_Credit_Amount__c | Currency | false |  |
| Key__c | Text | false |  |
| Last_Order_Date__c | Date | false |  |
| Last_Purchase_Order_Date__c | Date | false |  |
| Lead_Time__c | Number | false |  |
| Legacy_Name__c | Text | false |  |
| Legal_Name__c | Text | false |  |
| License_Expiration_Date__c | Date | false |  |
| Lost_Placement_After_Days__c | Number | false |  |
| Malt_License__c | Checkbox | false |  |
| Mapping_Key__c | Text | false |  |
| Maximum_DOI__c | Number | false |  |
| NaicsCode |  | false |  |
| NaicsDesc |  | false |  |
| Name |  | false |  |
| Notes__c | Html | false |  |
| NumberOfEmployees |  | false |  |
| NumberofLocations__c | Number | false |  |
| Offline_Commitment__c | LongTextArea | false |  |
| Offline_Contact__c | LongTextArea | false |  |
| Offline_Creation_Checkbox__c | Checkbox | false |  |
| Offline_Creation_Commitment_Checkbox__c | Checkbox | false |  |
| Offline_Creation_Contact_Checkbox__c | Checkbox | false |  |
| Offline_Creation_Event_Checkbox__c | Checkbox | false |  |
| Offline_Creation_Task_Checkbox__c | Checkbox | false |  |
| Offline_Event__c | LongTextArea | false |  |
| Offline_Record_Type__c | Text | false |  |
| Offline_Task__c | LongTextArea | false |  |
| Offline_Update_Checkbox__c | Checkbox | false |  |
| Offline_Update_Commitment_Checkbox__c | Checkbox | false |  |
| Offline_Update_Contact_Checkbox__c | Checkbox | false |  |
| Offline_Update_Event_Checkbox__c | Checkbox | false |  |
| Offline_Update_Task_Checkbox__c | Checkbox | false |  |
| Ohanafy_Master_ID__c | Text | false |  |
| Opening_Date__c | Date | false |  |
| Order_Date__c | Date | false |  |
| Orders_Total__c | Summary | false |  |
| OwnerId | Lookup | false |  |
| Ownership | Picklist | false |  |
| ParentId | Hierarchy | false |  |
| Parent_Account_Report_Id__c | Text | false |  |
| Payment_Method_Count__c | Summary | false |  |
| Payment_Method_Global__c | Picklist | false |  |
| Payment_Method__c | Picklist | false |  |
| Payment_Partner__c | Picklist | false |  |
| Payment_Terms_Global__c | Picklist | false |  |
| Payment_Terms__c | Picklist | false |  |
| Permit_Number__c | Text | false |  |
| Phone |  | false |  |
| Premise_Type__c | Picklist | false |  |
| Pricelist__c | Lookup | false | Pricelist__c |
| Priority__c | Picklist | false |  |
| Prospect_Stage__c | Picklist | false |  |
| QuickBooks_Customer_ID__c | Text | false |  |
| Rating | Picklist | false |  |
| Rating__c | Picklist | false |  |
| Retailer_Identification_Number__c | Text | false |  |
| Revenue_Goal__c | Currency | false |  |
| SLAExpirationDate__c | Date | false |  |
| SLASerialNumber__c | Text | false |  |
| SLA__c | Picklist | false |  |
| Sales_Rep__c | Lookup | false | User |
| ShippingAddress |  | false |  |
| Shipping_Address__c | Text | false |  |
| Sic |  | false |  |
| SicDesc |  | false |  |
| Site |  | false |  |
| Special_Instructions__c | Text | false |  |
| Spirits_License__c | Checkbox | false |  |
| Split_Invoice_Criteria__c | Text | false |  |
| Stage__c | Picklist | false |  |
| Star_Rating__c | Text | false |  |
| State_Tax_ID__c | Text | false |  |
| States_To_Exclude__c | Text | false |  |
| Status_Reason__c | Text | false |  |
| Status__c | Picklist | false |  |
| Store_Number__c | Text | false |  |
| Sub_Type__c | Picklist | false |  |
| Subchannel__c | Picklist | false |  |
| Supplier_Item_Types__c | MultiselectPicklist | false |  |
| Supplier_Keg_Deposit__c | Currency | false |  |
| Target_DOI__c | Number | false |  |
| Tax_Exempt__c | Checkbox | false |  |
| Territory__c | Lookup | false | Territory__c |
| TickerSymbol |  | false |  |
| Tier |  | false |  |
| Total_Case_Equivalents__c | Summary | false |  |
| Total_Credits_Applied__c | Summary | false |  |
| Total_Credits_Available__c | Summary | false |  |
| Total_Draft_Lines__c | Number | false |  |
| Total_Invoices__c | Summary | false |  |
| Total_Keg_Deposits__c | Currency | false |  |
| Total_Kegs__c | Number | false |  |
| Total_Order_Value__c | Summary | false |  |
| Total_Remaining_Credits__c | Currency | false |  |
| Tradestyle |  | false |  |
| Type | Picklist | false |  |
| Waive_Item_Deposit__c | Checkbox | false |  |
| WalMart_Customer_Reference_Number__c | Text | false |  |
| Walgreens_Distributor_AP_Number__c | Text | false |  |
| Website |  | false |  |
| Wine_License__c | Checkbox | false |  |
| X1_2_BBL_Deposits__c | Currency | false |  |
| X1_2_BBLs__c | Number | false |  |
| X1_4_BBL_Deposits__c | Currency | false |  |
| X1_4_BBLs__c | Number | false |  |
| X1_6_BBL_Deposits__c | Currency | false |  |
| X1_6_BBLs__c | Number | false |  |
| X20_L_Deposits__c | Currency | false |  |
| X20_Ls__c | Number | false |  |
| X40_L_Deposits__c | Currency | false |  |
| X40_Ls__c | Number | false |  |
| X50_L_Deposits__c | Currency | false |  |
| X50_Ls__c | Number | false |  |
| YearStarted |  | false |  |
| of_Routes__c | Summary | false |  |

### Account_Goal_Breakdown__c (7 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Goal__c | MasterDetail | false | Account_Goal__c |
| Allocation_Percent__c | Percent | false |  |
| Allocation__c | Number | false |  |
| Brand__c | Lookup | false | Item_Type__c |
| Frequency__c | Picklist | false |  |
| Month__c | Picklist | false |  |
| Supplier_Account__c | Lookup | false | Account |

### Account_Goal__c (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account__c | Lookup | false | Account |
| Amount__c | Number | false |  |
| Type__c | Picklist | false |  |
| Year__c | Text | true |  |

### Account_Item__c (58 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account__c | MasterDetail | false | Account |
| Active__c | Checkbox | false |  |
| All_Time_Profit__c | Currency | false |  |
| All_Time_Volume__c | Number | false |  |
| Backroom_Inventory_History__c | LongTextArea | false |  |
| Current_Retail_Price__c | Currency | false |  |
| Customer_Item_Number__c | Text | false |  |
| Days_Since_Last_Order__c | Number | false |  |
| Display_Inventory_History__c | LongTextArea | false |  |
| First_Sold_Date__c | Date | false |  |
| Inactive_When_Ordered__c | Checkbox | false |  |
| Is_New_Placement__c | Checkbox | false |  |
| Item_Sub_Type__c | Text | false |  |
| Item__c | MasterDetail | false | Item__c |
| Last_13_Months_Profit__c | Currency | false |  |
| Last_13_Months_Volume__c | Number | false |  |
| Last_14_Days_Profit__c | Currency | false |  |
| Last_14_Days_Volume__c | Number | false |  |
| Last_180_Days_Profit__c | Currency | false |  |
| Last_180_Days_Volume__c | Number | false |  |
| Last_30_Days_Profit__c | Currency | false |  |
| Last_30_Days_Volume__c | Number | false |  |
| Last_7_Days_Profit__c | Currency | false |  |
| Last_7_Days_Volume__c | Number | false |  |
| Last_90_Days_Profit__c | Currency | false |  |
| Last_90_Days_Volume__c | Number | false |  |
| Last_Inventory_Date__c | Date | false |  |
| Last_Inventory_Quantity__c | Number | false |  |
| Last_Invoice_Price__c | Currency | false |  |
| Last_Purchase_Date__c | Date | false |  |
| Last_Purchase_Quantity__c | Number | false |  |
| Last_Sold_Date__c | Date | false |  |
| Last_Year_Profit__c | Currency | false |  |
| Last_Year_Volume__c | Number | false |  |
| Lead_Time__c | Number | false |  |
| Lost_Placement_After_Days__c | Number | false |  |
| Lost_Placement_Date__c | Date | false |  |
| Overall_Inventory_History__c | LongTextArea | false |  |
| Price__c | Currency | false |  |
| Purchase_History__c | LongTextArea | false |  |
| Retail_Inventory_Quantity__c | Number | false |  |
| Sequence__c | Number | false |  |
| Shelf_Inventory_History__c | LongTextArea | false |  |
| This_Year_Profit__c | Currency | false |  |
| This_Year_Volume__c | Number | false |  |
| Trailing_13_Months_Profit__c | Currency | false |  |
| Trailing_13_Months_Volume__c | Number | false |  |
| Trailing_14_Days_Profit__c | Currency | false |  |
| Trailing_14_Days_Volume__c | Number | false |  |
| Trailing_180_Days_Profit__c | Currency | false |  |
| Trailing_180_Days_Volume__c | Number | false |  |
| Trailing_30_Days_Profit__c | Currency | false |  |
| Trailing_30_Days_Volume__c | Number | false |  |
| Trailing_7_Days_Profit__c | Currency | false |  |
| Trailing_7_Days_Volume__c | Number | false |  |
| Trailing_90_Days_Profit__c | Currency | false |  |
| Trailing_90_Days_Volume__c | Number | false |  |
| Weekly_Sales__c | Number | false |  |

### Account_Route__c (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active_Route__c | Checkbox | false |  |
| Customer__c | MasterDetail | false | Account |
| End_Time__c | Time | false |  |
| Key__c | Text | false |  |
| Mapping_Key__c | Text | false |  |
| Route__c | MasterDetail | false | Route__c |
| Start_Time__c | Time | false |  |
| Stop_Order__c | Number | false |  |

### Accounting_Adjustment__c (35 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Billing_City__c | Text | false |  |
| Account_Billing_Postal_Code__c | Text | false |  |
| Account_Billing_State__c | Text | false |  |
| Account_Billing_Street__c | Text | false |  |
| Account_Phone__c | Text | false |  |
| Account_Quickbooks_Customer_ID__c | Text | false |  |
| Accounting_System_ID__c | Text | false |  |
| Category__c | Picklist | false |  |
| Entry_Type__c | Picklist | false |  |
| Financial_Account__c | Lookup | false | Financial_Account__c |
| ID_Account__c | Text | false |  |
| ID_Invoice_Credit__c | Text | false |  |
| ID_Invoice_Item__c | Text | false |  |
| ID_Invoice__c | Text | false |  |
| ID_Item__c | Text | false |  |
| ID_Item_del__c | Text | false |  |
| Integration_Sync_Date__c | DateTime | false |  |
| Integration_Sync__c | Checkbox | false |  |
| Inventory_Adjustment__c | MasterDetail | false | Inventory_Adjustment__c |
| Item_Name__c | Text | false |  |
| Item_Quantity__c | Number | false |  |
| Item_QuickBooks_Credit_Memo_ID__c | Text | false |  |
| Item_QuickBooks_ID__c | Text | false |  |
| Item_Sub_Total__c | Currency | false |  |
| N_Account_del__c | Text | false |  |
| N_Inventory_Adjustment__c | Text | false |  |
| N_Invoice_Credit__c | Text | false |  |
| N_Invoice_Item__c | Text | false |  |
| N_Invoice__c | Text | false |  |
| N_Item_del__c | Text | false |  |
| Quantity__c | Number | false |  |
| QuickBooks_Adjustment_Type__c | Text | false |  |
| QuickBooks_Customer_ID_del__c | Text | false |  |
| Type__c | Picklist | false |  |
| Value__c | Currency | false |  |

### Accounting_Mapping__mdt (14 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Category__c | Text | false |  |
| Credit_Memo_ID_Company_2__c | Text | false |  |
| Credit_Memo_ID__c | Text | false |  |
| Holding_ID__c | Text | false |  |
| Purchase_ID_Company_2__c | Text | false |  |
| Purchase_ID__c | Text | false |  |
| Return_ID_Company_2__c | Text | false |  |
| Return_ID__c | Text | false |  |
| Sales_ID_Company_2__c | Text | false |  |
| Sales_ID__c | Text | false |  |
| Sub_Type__c | Text | false |  |
| Type__c | Text | false |  |
| Variance_ID__c | Text | false |  |

### Accounting_Setting__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Category__c | Picklist | false |  |
| Count_Bill__c | Summary | false |  |
| Count_Credit_Memo__c | Summary | false |  |
| Count_Customer__c | Summary | false |  |
| Count_Invoice__c | Summary | false |  |
| Count_Journal_Entry__c | Summary | false |  |
| Count_Purchase_Order__c | Summary | false |  |
| Count_Supplier__c | Summary | false |  |
| Key__c | Text | false |  |
| Sub_Type__c | Picklist | false |  |
| Type__c | Picklist | false |  |

### Activity (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Completed__c | Checkbox | false |  |
| Criteria__c | Lookup | false | Criteria__c |
| Role__c | Picklist | false |  |

### Activity_Goal__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Activity_Id__c | Text | false |  |
| Goal_Tracking__c | MasterDetail | false | Goal_Tracking__c |
| Type__c | Picklist | false |  |

### Adjustment__c (14 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Sub_Types__c | MultiselectPicklist | false |  |
| Active__c | Checkbox | false |  |
| Adjustment_Type__c | Picklist | false |  |
| Cost_Type__c | Picklist | false |  |
| Cost__c | Currency | false |  |
| Dollar_Amount__c | Currency | false |  |
| End_Date__c | Date | false |  |
| Packaging_Types__c | MultiselectPicklist | false |  |
| Percent_Amount__c | Percent | false |  |
| Product_Types__c | MultiselectPicklist | false |  |
| Start_Date__c | Date | false |  |
| States__c | MultiselectPicklist | false |  |
| UOM__c | Picklist | false |  |
| Units__c | Number | false |  |

### Allocation__c (10 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Allocated_Amount__c | Number | false |  |
| Amount_Consumed__c | Number | false |  |
| Amount_Remaining__c | Number | false |  |
| Customer__c | Lookup | false | Account |
| End_Date__c | Date | false |  |
| Item__c | Lookup | false | Item__c |
| Location__c | Lookup | false | Location__c |
| Sales_Rep__c | Lookup | false | User |
| Start_Date__c | Date | false |  |

### Benefit__c (1 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Employee__c | MasterDetail | false | Employee__c |

### Billback__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Amount_Revenue__c | Currency | false |  |
| Amount__c | Number | false |  |
| Incentive__c | Lookup | false | Incentive__c |
| Outstanding_Amount__c | Currency | false |  |

### Brand_Territory_Exclusion__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Brand__c | MasterDetail | false | Item_Type__c |
| Territory__c | MasterDetail | false | Territory__c |

### Candidate__c (12 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Name__c | Lookup | false | Account |
| Email__c | Text | false |  |
| Employee__c | Lookup | false | Employee__c |
| Linkedin_URL__c | Url | false |  |
| Mailing_Address__c | Text | false |  |
| Mailing_City__c | Text | false |  |
| Mailing_Country__c | Text | false |  |
| Mailing_State_Province__c | Text | false |  |
| Mailing_Street__c | Text | false |  |
| Mailing_Zip_Postal_Code__c | Text | false |  |
| Phone__c | Phone | false |  |
| Status__c | Picklist | false |  |

### Commitment_Item__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Commitment__c | MasterDetail | false | Commitment__c |
| Product__c | MasterDetail | false | Item__c |
| Quantity__c | Number | false |  |

### Commitment__c (9 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Customer__c | Lookup | false | Account |
| Account_Distributor__c | Lookup | false | Account |
| Contact__c | Text | false |  |
| Date__c | Date | false |  |
| Distributor_Status__c | Picklist | false |  |
| Involved_Sales_Rep__c | Text | false |  |
| Notes__c | Text | false |  |
| Offline_Creation_Checkbox__c | Checkbox | false |  |
| Offline_Items__c | LongTextArea | false |  |

### Compensation__c (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Current_Role__c | Checkbox | false |  |
| Description__c | Text | false |  |
| Employee__c | MasterDetail | false | Employee__c |
| End_Date__c | Date | false |  |
| Job_Title__c | Picklist | false |  |
| Salary_Amount__c | Currency | false |  |
| Start_Date__c | Date | false |  |
| Type__c | Picklist | false |  |

### Configuration_Preference__mdt (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Description__c | Text | false |  |
| Key__c | Text | false |  |
| Value__c | Text | false |  |

### Contact (33 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| AccountId | Lookup | false |  |
| AssistantName |  | false |  |
| AssistantPhone |  | false |  |
| Billing_Contact__c | Checkbox | false |  |
| Birthdate |  | false |  |
| Delivery_Contact__c | Checkbox | false |  |
| Department |  | false |  |
| Description |  | false |  |
| DoNotCall |  | false |  |
| Email |  | false |  |
| Fax |  | false |  |
| GenderIdentity | Picklist | false |  |
| HasOptedOutOfEmail |  | false |  |
| HasOptedOutOfFax |  | false |  |
| HomePhone |  | false |  |
| IndividualId | Lookup | false |  |
| Jigsaw |  | false |  |
| Languages__c | Text | false |  |
| LastCURequestDate |  | false |  |
| LastCUUpdateDate |  | false |  |
| LeadSource | Picklist | false |  |
| Level__c | Picklist | false |  |
| MailingAddress |  | false |  |
| Mapping_Key__c | Text | false |  |
| MobilePhone |  | false |  |
| Name |  | false |  |
| OtherAddress |  | false |  |
| OtherPhone |  | false |  |
| OwnerId | Lookup | false |  |
| Phone |  | false |  |
| Pronouns | Picklist | false |  |
| ReportsToId | Lookup | false |  |
| Title |  | false |  |

### Control_State_Code__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Control_State_Code__c | Text | true |  |
| Issuing_State__c | Text | true |  |
| Item__c | Lookup | false | Item__c |

### Credit__c (43 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account__c | MasterDetail | false | Account |
| Adjustment__c | Currency | false |  |
| Amount__c | Currency | false |  |
| Apply_Amount__c | Currency | false |  |
| Case_Quantity__c | Number | false |  |
| Case_Total__c | Currency | false |  |
| Credit_Date__c | Date | false |  |
| Credit_Type__c | Picklist | false |  |
| Delivery__c | Lookup | false | Delivery__c |
| Individual_Unit_Price__c | Currency | false |  |
| Individual_Unit_Quantity__c | Number | false |  |
| Individual_Unit_Total__c | Currency | false |  |
| Integration_Sync_Date__c | DateTime | false |  |
| Integration_Sync__c | Checkbox | false |  |
| Invoice__c | Lookup | false | Order__c |
| Item__c | Lookup | false | Item__c |
| Keg_Deposit__c | Currency | false |  |
| Location__c | Lookup | false | Location__c |
| Lot__c | Lookup | false | Lot__c |
| Notes__c | LongTextArea | false |  |
| Offline_Add_To_Checkbox__c | Checkbox | false |  |
| Offline_Apply__c | Checkbox | false |  |
| Offline_Code_Date__c | Date | false |  |
| Offline_Creation_Checkbox__c | Checkbox | false |  |
| Offline_Deduct_From_Invoice__c | Checkbox | false |  |
| Offline_Edit_Checkbox__c | Checkbox | false |  |
| Picked_Up__c | Checkbox | false |  |
| Quantity_Formula__c | Number | false |  |
| Quantity__c | Number | false |  |
| Quantity_uom__c | Text | false |  |
| QuickBooks_Class_ID__c | Text | false |  |
| QuickBooks_Credit_Memo_ID_Company_2__c | Text | false |  |
| QuickBooks_Credit_Memo_ID__c | Text | false |  |
| Return_To_Inventory__c | Checkbox | false |  |
| Rollover_Amount__c | Currency | false |  |
| Status__c | Picklist | false |  |
| Total__c | Currency | false |  |
| Type__c | Picklist | false |  |
| Units_Per_Case__c | Number | false |  |
| item_number__c | Picklist | false |  |
| product_description__c | Picklist | false |  |
| quantity_shipped__c | Number | false |  |
| unit_price__c | Currency | false |  |

### Criteria__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Criteria_Formula__c | Text | false |  |
| Field_API_Name__c | Text | false |  |
| Field_Value__c | Text | false |  |
| Operator__c | Picklist | false |  |
| Task_Manager__c | MasterDetail | false | Task_Manager__c |

### Customer_Information__mdt (15 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABC_Number__c | Text | false |  |
| Active__c | Checkbox | false |  |
| Billing_City__c | Text | false |  |
| Billing_County__c | Text | false |  |
| Billing_Postal_Code__c | Text | false |  |
| Billing_State__c | Text | false |  |
| Billing_Street__c | Text | false |  |
| Customer_Legal_Name__c | Text | false |  |
| Division_Id__c | Text | false |  |
| EIN__c | Text | false |  |
| Entity_Type__c | Text | false |  |
| Owner_Name__c | Text | false |  |
| Owner_Title__c | Text | false |  |
| Phone_Number__c | Phone | false |  |
| TTB_Brewery_Number__c | Text | false |  |

### Cycle_Count__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| End_Date__c | Date | false |  |
| Start_Date__c | Date | false |  |

### Deal_Item__c (12 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Customer_Price_PTC__c | Currency | false |  |
| Deal__c | MasterDetail | false | Deal__c |
| Item__c | MasterDetail | false | Item__c |
| Notes__c | Text | false |  |
| Quantity__c | Number | false |  |
| Recurrence__c | Picklist | false |  |
| Retail_Price_PTR__c | Currency | false |  |
| Total_Customer_Price__c | Currency | false |  |
| Total_Retail_Price__c | Currency | false |  |
| Total_Wholesale_Price__c | Currency | false |  |
| Type__c | Picklist | false |  |
| Wholesale_Price_FOB__c | Currency | false |  |

### Deal__c (12 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Actual_Cost__c | Currency | false |  |
| Actual_Value__c | Currency | false |  |
| Deal_Grade__c | Text | false |  |
| End_Date__c | Date | false |  |
| Expected_Value_Customer__c | Currency | false |  |
| Expected_Value_Retail__c | Currency | false |  |
| Expected_Value_Wholesale__c | Currency | false |  |
| Marginal_Value_Retail__c | Percent | false |  |
| Return_On_Investment__c | Percent | false |  |
| Start_Date__c | Date | false |  |
| Status__c | Picklist | false |  |
| Type__c | Picklist | false |  |

### Delivery__c (25 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Appointment_Number__c | Text | false |  |
| Auto_Palletized__c | Checkbox | false |  |
| Cancelled_Reason__c | Text | false |  |
| Day_of_Week__c | Picklist | false |  |
| Delivery_Date__c | Date | false |  |
| Delivery_Locked__c | Checkbox | false |  |
| Delivery_Number__c | AutoNumber | false |  |
| Delivery__c | Lookup | false | Delivery__c |
| Driver__c | Lookup | false | User |
| Products_Returned__c | Checkbox | false |  |
| Revenue_Requirement__c | Currency | false |  |
| Route__c | Lookup | false | Route__c |
| Status__c | Picklist | false |  |
| Total_Backordered__c | Number | false |  |
| Total_Revenue__c | Currency | false |  |
| Total_Weight_UOM__c | Text | false |  |
| Total_Weight__c | Number | false |  |
| Vehicle__c | Lookup | false | Equipment__c |
| of_Cases_Backordered__c | Number | false |  |
| of_Cases__c | Number | false |  |
| of_Invoice_Items__c | Number | false |  |
| of_Invoices__c | Number | false |  |
| of_Kegs_Backordered__c | Number | false |  |
| of_Kegs__c | Number | false |  |
| of_Unique_Customers__c | Number | false |  |

### Device__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Cost__c | Currency | false |  |
| Equipment__c | MasterDetail | false | Equipment__c |
| Notes__c | LongTextArea | false |  |
| Purchase_Date__c | Date | false |  |
| Serial_Number__c | Text | false |  |
| Type__c | Picklist | false |  |

### Display_Item__c (13 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Id__c | Text | false |  |
| Account__c | Text | false |  |
| Display__c | MasterDetail | false | Display__c |
| Product__c | Lookup | false | Item__c |
| Sales_Growth_Before_After__c | Percent | false |  |
| Sales_Growth_Before_During__c | Percent | false |  |
| Sales_Growth_During_After__c | Percent | false |  |
| Total_Case_Equivalents_After_Period__c | Number | false |  |
| Total_Case_Equivalents_Before_Period__c | Number | false |  |
| Total_Case_Equivalents_During_Period__c | Number | false |  |
| Total_Sales_After_Period__c | Currency | false |  |
| Total_Sales_Before_Period__c | Currency | false |  |
| Total_Sales_During_Period__c | Currency | false |  |

### Display_Run__c (16 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active_Displays__c | Summary | false |  |
| Active__c | Checkbox | false |  |
| Chain_Banner__c | MasterDetail | false | Account |
| Display_Compliance__c | Percent | false |  |
| End_Date__c | Date | false |  |
| Start_Date__c | Date | false |  |
| Total_Displays__c | Summary | false |  |
| Total_Item_Case_Equivalents_After__c | Summary | false |  |
| Total_Item_Case_Equivalents_Before__c | Summary | false |  |
| Total_Item_Case_Equivalents_During__c | Summary | false |  |
| Total_Item_Sales_After__c | Summary | false |  |
| Total_Item_Sales_Before__c | Summary | false |  |
| Total_Item_Sales_During__c | Summary | false |  |
| Track_Days_After__c | Number | false |  |
| Track_Days_Before__c | Number | false |  |
| Track_Days_During__c | Number | false |  |

### Display__c (17 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account__c | Lookup | false | Account |
| Active__c | Number | false |  |
| After_Display_End_Date__c | Date | false |  |
| After_Display_Start_Date__c | Date | false |  |
| Before_Display_End_Date__c | Date | false |  |
| Before_Display_Start_Date__c | Date | false |  |
| Days_Until_End__c | Number | false |  |
| Display_Description__c | Text | false |  |
| Display_Run_Active__c | Checkbox | false |  |
| Display_Run__c | MasterDetail | false | Display_Run__c |
| Status__c | Picklist | false |  |
| Total_Item_Case_Equivalents_After__c | Summary | false |  |
| Total_Item_Case_Equivalents_Before__c | Summary | false |  |
| Total_Item_Case_Equivalents_During__c | Summary | false |  |
| Total_Item_Sales_After__c | Summary | false |  |
| Total_Item_Sales_Before__c | Summary | false |  |
| Total_Item_Sales_During__c | Summary | false |  |

### Distributor_Placement__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Customer__c | MasterDetail | false | Account |
| Date__c | Date | false |  |
| Item__c | Lookup | false | Item__c |
| Quantity__c | Number | false |  |
| Type__c | Picklist | false |  |

### Earning__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Employee__c | MasterDetail | false | Employee__c |
| End_Date__c | Date | false |  |
| Gross_Pay_Amount__c | Currency | false |  |
| Net_Pay_Amount__c | Currency | false |  |
| Start_Date__c | Date | false |  |
| Type__c | Picklist | false |  |

### Employee__c (24 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Birthdate_Formula__c | Date | false |  |
| Birthdate__c | Date | false |  |
| Days_Until_License_Expiration__c | Number | false |  |
| Department_Role__c | Picklist | false |  |
| Department__c | Picklist | false |  |
| Email__c | Text | false |  |
| First_Name__c | Text | false |  |
| Gross_Earnings_YTD__c | Summary | false |  |
| Key__c | Text | false |  |
| Last_Name__c | Text | false |  |
| License_Expiration_Date__c | Date | false |  |
| Mailing_Address__c | Text | false |  |
| Mailing_City__c | Text | false |  |
| Mailing_Country__c | Text | false |  |
| Mailing_State_Province__c | Text | false |  |
| Mailing_Street__c | Text | false |  |
| Mailing_Zip_Postal_Code__c | Text | false |  |
| Mapping_Key__c | Text | false |  |
| Net_Earnings_YTD__c | Summary | false |  |
| Phone__c | Text | false |  |
| SSN__c | EncryptedText | false |  |
| Salary_Type__c | Picklist | false |  |
| Total_Compensation__c | Summary | false |  |
| Weeks_Per_Year__c | Number | false |  |

### Equipment__c (19 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Abbreviation__c | Text | false |  |
| Auto_Set_Sanitize__c | Checkbox | false |  |
| Equipment_Cost__c | Currency | false |  |
| Inventory_Bearing__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Location__c | MasterDetail | false | Location__c |
| Mapping_Key__c | Text | false |  |
| Notes__c | LongTextArea | false |  |
| Order__c | Number | false |  |
| Purchase_Date__c | Date | false |  |
| Serial_Number__c | Text | false |  |
| Status__c | Picklist | false |  |
| System__c | Picklist | false |  |
| Tare_Weight__c | Number | false |  |
| Tax_Exempt__c | Checkbox | false |  |
| Truck_Location__c | Lookup | false | Location__c |
| Type__c | Picklist | false |  |
| Vendor__c | Lookup | false | Account |
| Warranty_Expiration_Date__c | Date | false |  |

### Event_Expense__c (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Business_Purpose__c | Text | false |  |
| City_State__c | Text | false |  |
| Comment__c | TextArea | false |  |
| Event__c | MasterDetail | false | Event__c |
| Expense_Type__c | Picklist | false |  |
| Site_Rental__c | Currency | false |  |
| Transaction_Date__c | Date | false |  |
| Vendor_Name__c | Text | false |  |

### Event_Junction__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Criteria__c | MasterDetail | false | Criteria__c |
| Event_Template__c | MasterDetail | false | Event_Template__c |

### Event_MDF__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Agreement_Details__c | LongTextArea | false |  |
| Event__c | MasterDetail | false | Event__c |
| MDF_Amount__c | Currency | false |  |
| MDF_Partner_Account__c | Lookup | false | Account |
| MDF_Partner_Contact__c | Lookup | false | Contact |
| Received_Payment__c | Checkbox | false |  |

### Event_Registration__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Attendee_Email__c | Email | false |  |
| Contact__c | Lookup | false | Contact |
| Dietary_Needs__c | Picklist | false |  |
| Email_Confirmation_Sent__c | Checkbox | false |  |
| Event__c | MasterDetail | false | Event__c |
| Name_on_Badge__c | Text | false |  |
| Primary_Track_of_Interest__c | Lookup | false | Track__c |
| Registration_Type__c | Picklist | false |  |
| Reminder_Date__c | Date | false |  |
| Reminder_Email_Days__c | Number | false |  |
| Title_on_Badge__c | Text | false |  |

### Event_Template__c (9 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| All_Day_Event__c | Checkbox | false |  |
| Days_to_Add__c | Number | false |  |
| Description__c | LongTextArea | false |  |
| End_Date_Time__c | DateTime | false |  |
| Key__c | Text | true |  |
| Location__c | Text | false |  |
| Role__c | Picklist | false |  |
| Start_Date_Time__c | DateTime | false |  |
| Subject__c | Text | false |  |

### Event__c (55 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Budget_Activities__c | Currency | false |  |
| Budget_Catering__c | Currency | false |  |
| Budget_Contingency__c | Currency | false |  |
| Budget_Decor__c | Currency | false |  |
| Budget_Other__c | Currency | false |  |
| Budget_Printing__c | Currency | false |  |
| Budget_Site_Rental__c | Currency | false |  |
| Budget_Total__c | Currency | false |  |
| Budget_Transportation__c | Currency | false |  |
| Capacity_Full__c | Percent | false |  |
| Event_Description__c | TextArea | false |  |
| Event_End_Date__c | DateTime | false |  |
| Event_Evaluation__c | Number | false |  |
| Event_Manager__c | Lookup | false | User |
| Event_Start_Date__c | DateTime | false |  |
| Event_Type__c | Picklist | false |  |
| Event_Vendor_Account__c | Lookup | false | Account |
| Event_Vision__c | Html | false |  |
| Event_Website__c | Url | false |  |
| Expected_vs_Actual_Budget_Currency__c | Currency | false |  |
| Expected_vs_Actual_Budget__c | Percent | false |  |
| Expenses_Activities__c | Summary | false |  |
| Expenses_Catering__c | Summary | false |  |
| Expenses_Decor__c | Summary | false |  |
| Expenses_Other__c | Summary | false |  |
| Expenses_Printing__c | Summary | false |  |
| Expenses_Site_Rental__c | Summary | false |  |
| Expenses_Transportation__c | Summary | false |  |
| Final_Attendance__c | TextArea | false |  |
| Map_to_Venue__c | Text | false |  |
| Maximum_Registration__c | Number | false |  |
| Net_Actual_Cost__c | Currency | false |  |
| Net_Expected_Cost__c | Currency | false |  |
| Online_Meeting_Details__c | LongTextArea | false |  |
| Online_Passcode__c | Text | false |  |
| Parent_Event__c | Lookup | false | Event__c |
| Primary_Vendor_Contact_Phone__c | Text | false |  |
| Primary_Vendor_Contact__c | Lookup | false | Contact |
| Recurrence_End_Date__c | Date | false |  |
| Recurrence__c | Picklist | false |  |
| Registered_Attendees__c | Summary | false |  |
| Send_Email_Confirmation__c | Checkbox | false |  |
| Targeted_Attendance__c | TextArea | false |  |
| Territory__c | Picklist | false |  |
| Total_Actual_MDF__c | Summary | false |  |
| Total_Expected_MDF__c | Summary | false |  |
| Total_Expenses__c | Currency | false |  |
| Venue_City__c | Text | false |  |
| Venue_Country__c | Text | false |  |
| Venue_Postal_Code__c | Text | false |  |
| Venue_State__c | Text | false |  |
| Venue_Status__c | Picklist | false |  |
| Venue_Street_Address_1__c | Text | false |  |
| Venue_Street_Address_2__c | Text | false |  |
| Venue__c | Lookup | false | Venue__c |

### Expense_Report__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Approver__c | Lookup | false | User |
| Employee__c | MasterDetail | false | Employee__c |
| Status__c | Picklist | false |  |
| Total_Value_of_Expenses__c | Summary | false |  |
| Total_of_Expenses__c | Summary | false |  |

### Expense__c (7 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Category__c | Picklist | false |  |
| Date__c | Date | false |  |
| Description__c | Text | false |  |
| Expense_Report__c | MasterDetail | false | Expense_Report__c |
| Merchant__c | Lookup | false | Merchant__c |
| Status__c | Picklist | false |  |
| Total_Amount__c | Currency | false |  |

### Fee__c (13 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Active__c | Checkbox | false |  |
| Allocation_Method__c | Picklist | false |  |
| Amount__c | Currency | false |  |
| Default_Amount__c | Currency | false |  |
| Fee_ID__c | Text | false |  |
| Inventory_Receipt__c | Checkbox | false |  |
| Invoice__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Mapping_Key__c | Text | false |  |
| Quantity__c | Number | false |  |
| Transaction_Fee__c | Checkbox | false |  |
| Type__c | Picklist | false |  |

### Fieldset_Customization__mdt (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Fieldset_Name__c | Text | false |  |
| Fieldset_Purpose__c | Picklist | false |  |
| Object_Name__c | Text | false |  |

### Financial_Account__c (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Detail_Type__c | Picklist | false |  |
| Parent_Account__c | Lookup | false | Financial_Account__c |
| Type__c | Picklist | false |  |

### Goal_Template__c (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Tracking_Object_API__c | Text | false |  |
| Tracking_Object_Field_Value__c | Text | false |  |
| Tracking_Object_Field__c | Text | false |  |

### Goal_Tracking__c (24 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Type__c | Text | false |  |
| Account__c | Lookup | false | Account |
| Active__c | Checkbox | false |  |
| Amount_Revenue__c | Currency | false |  |
| Amount__c | Number | false |  |
| Attainment_Percent__c | Percent | false |  |
| Attainment_Revenue__c | Currency | false |  |
| Attainment__c | Number | false |  |
| Brand__c | Lookup | false | Item_Type__c |
| Completion_Number__c | Number | false |  |
| Contact__c | Lookup | false | Contact |
| End_Date__c | Date | false |  |
| Goal_Template__c | Lookup | false | Goal_Template__c |
| Incentive_Active__c | Checkbox | false |  |
| Incentive__c | Lookup | false | Incentive__c |
| Limit_Per_User__c | Number | false |  |
| Mandate__c | Checkbox | false |  |
| Product__c | Lookup | false | Item__c |
| Start_Date__c | Date | false |  |
| Supplier__c | Lookup | false | Item_Line__c |
| Territory__c | Lookup | false | Territory__c |
| Total_Completion__c | Number | false |  |
| Type__c | Picklist | false |  |
| User__c | Lookup | false | User |

### Incentive__c (23 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Amount_Revenue__c | Currency | false |  |
| Amount__c | Number | false |  |
| Attainment_Percent__c | Percent | false |  |
| Attainment_Revenue__c | Currency | false |  |
| Attainment__c | Number | false |  |
| Billback__c | Lookup | false | Billback__c |
| Brand__c | Lookup | false | Item_Type__c |
| Completion_Amount__c | Number | false |  |
| Completion_Percent__c | Percent | false |  |
| End_Date__c | DateTime | false |  |
| Goal_Template__c | Lookup | true | Goal_Template__c |
| Has_Billback__c | Checkbox | false |  |
| Include_Inactive_Placements__c | Checkbox | false |  |
| Limit_Per_User__c | Number | false |  |
| Limit__c | Number | false |  |
| On_Premises__c | Checkbox | false |  |
| Product__c | Lookup | false | Item__c |
| Reward__c | LongTextArea | false |  |
| Start_Date__c | Date | false |  |
| Supplier__c | Lookup | false | Item_Line__c |
| Team_Incentive__c | Checkbox | false |  |
| Type__c | Picklist | true |  |

### Integration_Sync_Failure__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Failure_Reason__c | LongTextArea | false |  |
| Integration_Sync__c | MasterDetail | false | Integration_Sync__c |
| Link_to_Record__c | Url | false |  |

### Integration_Sync__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Attempted_Record_Count__c | Number | false |  |
| Failure_Record_Count__c | Summary | false |  |
| Integration__c | Picklist | false |  |
| Records_to_Sync__c | MultiselectPicklist | true |  |
| Status__c | Picklist | false |  |
| Succeeded_Record_Count__c | Number | false |  |

### Interview__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Days_Remaining_to_Interview__c | Number | false |  |
| Description__c | LongTextArea | false |  |
| Interview_Date__c | Date | false |  |
| Job_Candidate__c | Lookup | false | Job_Candidate__c |
| Rating__c | Picklist | false |  |
| Stage__c | Picklist | false |  |

### Inventory_Adjustment__c (62 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_Adjustments_Synced__c | Summary | false |  |
| Accounting_Adjustments__c | Summary | false |  |
| Accounting_Key_Calculated__c | LongTextArea | false |  |
| Apex_Class_Name__c | Text | false |  |
| Average_Cost__c | Currency | false |  |
| Category__c | Text | false |  |
| Clean_Keg_Flag__c | Checkbox | false |  |
| Cloned_Adjustment__c | Text | false |  |
| Code_Date_Name__c | Text | false |  |
| Company_Key__c | Text | false |  |
| Cost_Per__c | Currency | false |  |
| Cost__c | Currency | false |  |
| Credit_Return_Flag__c | Checkbox | false |  |
| Credit__c | Lookup | false | Credit__c |
| Date__c | Date | false |  |
| Dirty_Keg_Flag__c | Checkbox | false |  |
| Inventory_Adjustment_Number__c | Number | false |  |
| Inventory_Log_Flag__c | Checkbox | false |  |
| Inventory_Log_Key__c | Text | false |  |
| Inventory_Log__c | Lookup | false | Inventory_Log__c |
| Inventory_Receipt_Flag__c | Checkbox | false |  |
| Inventory_Receipt_Item_Flag__c | Checkbox | false |  |
| Inventory_Receipt_Item__c | Lookup | false | Inventory_Receipt_Item__c |
| Inventory_Receipt__c | Lookup | false | Inventory_Receipt__c |
| Inventory__c | MasterDetail | false | Inventory__c |
| Invoice_Flag__c | Checkbox | false |  |
| Invoice_Item_Flag__c | Checkbox | false |  |
| Invoice_Item_Lookup__c | Lookup | false | Order_Item__c |
| Invoice_Key__c | Text | false |  |
| Invoice_Lookup__c | Lookup | false | Order__c |
| Item_Transfer_Flag__c | Checkbox | false |  |
| Item__c | Text | false |  |
| Location_Name__c | Text | false |  |
| Log_Type_Sub_Type_Key__c | Text | false |  |
| Lot_Inventory__c | Lookup | false | Lot_Inventory__c |
| Lot__c | Lookup | false | Lot__c |
| Manual_Override__c | Checkbox | false |  |
| Notes__c | LongTextArea | false |  |
| Original_Invoice__c | Lookup | false | Order__c |
| Positive_Negative_Key__c | Text | false |  |
| Purchase_Order_Flag__c | Checkbox | false |  |
| Purchase_Order_Item_Flag__c | Checkbox | false |  |
| Purchase_Order_Item__c | Lookup | false | Purchase_Order_Item__c |
| Purchase_Order__c | Lookup | false | Purchase_Order__c |
| Quantity_Change__c | Number | false |  |
| Quantity__c | Number | false |  |
| QuickBooks_Class_ID__c | Text | false |  |
| Reason__c | Picklist | false |  |
| Receipt_Key__c | Text | false |  |
| Return_Key__c | Text | false |  |
| Rollup__c | Checkbox | false |  |
| Status__c | Picklist | false |  |
| Supplier__c | Text | false |  |
| Synced__c | Checkbox | false |  |
| Total_Value__c | Currency | false |  |
| Transfer_Key__c | Text | false |  |
| Transfer__c | Lookup | false | Transfer__c |
| Type__c | Picklist | false |  |
| UOM__c | Text | false |  |
| Unsold_Flag__c | Checkbox | false |  |
| Unsold_Reason__c | Text | false |  |
| Value_Each__c | Currency | false |  |

### Inventory_History__c (7 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Date__c | Date | false |  |
| Inventory_Date__c | Date | false |  |
| Inventory_Value__c | Number | false |  |
| Inventory__c | MasterDetail | false | Inventory__c |
| Item__c | MasterDetail | false | Item__c |
| Quantity_Available__c | Number | false |  |
| Quantity_On_Hand__c | Number | false |  |

### Inventory_Log_Group__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Approved__c | Checkbox | false |  |
| Cycle_Count__c | Checkbox | false |  |
| Location__c | Lookup | false | Location__c |
| Log_Date__c | Date | false |  |
| Recounted__c | Checkbox | false |  |
| Use_Pallets_And_Layers__c | Checkbox | false |  |

### Inventory_Log__c (19 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Cost_Variance__c | Currency | false |  |
| Individual_Quantity__c | Number | false |  |
| Inventory_Log_Group__c | Lookup | false | Inventory_Log_Group__c |
| Inventory__c | MasterDetail | false | Inventory__c |
| Item__c | Text | false |  |
| Key__c | Text | false |  |
| Layer_Quantity__c | Number | false |  |
| Location__c | Lookup | false | Location__c |
| Log_Date__c | Date | false |  |
| Lot_Inventory__c | Lookup | false | Lot_Inventory__c |
| Notes__c | Text | false |  |
| Pallet_Quantity__c | Number | false |  |
| Quantity_Adjustment__c | Number | false |  |
| Reason__c | Picklist | false |  |
| Recounted__c | Checkbox | false |  |
| Status__c | Picklist | false |  |
| Top_Line_Log__c | Checkbox | false |  |
| UOM__c | Text | false |  |
| Unit_Quantity__c | Number | false |  |

### Inventory_Receipt_Fee__c (10 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Allocation_Method__c | Picklist | false |  |
| Amount__c | Currency | false |  |
| Cost_Type__c | Picklist | false |  |
| Description__c | Text | false |  |
| Fee_Name__c | Text | false |  |
| Fee__c | MasterDetail | false | Fee__c |
| Inventory_Receipt__c | MasterDetail | false | Inventory_Receipt__c |
| Quantity__c | Number | false |  |
| Total__c | Currency | false |  |

### Inventory_Receipt_Item__c (33 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_Variance_ID__c | Text | false |  |
| Apex_Class_Name__c | Text | false |  |
| Case_Equivalents__c | Number | false |  |
| Cost_Variance__c | Currency | false |  |
| Fee_Amount__c | Currency | false |  |
| Inventory_Location__c | Lookup | false | Location__c |
| Inventory_Receipt_Item__c | Lookup | false | Inventory_Receipt_Item__c |
| Inventory_Receipt__c | MasterDetail | false | Inventory_Receipt__c |
| Item_Name__c | Text | false |  |
| Item_Quantity_On_Hand__c | Number | false |  |
| Item_SKU__c | Text | false |  |
| Item__c | MasterDetail | false | Item__c |
| Landed_Unit_Price__c | Currency | false |  |
| Last_Purchase_Price__c | Currency | false |  |
| Lot__c | Text | false |  |
| Previous_Average_Landed_Cost__c | Currency | false |  |
| Quantity_Variance__c | Number | false |  |
| Quantity__c | Number | false |  |
| QuickBooks_Class_ID__c | Text | false |  |
| QuickBooks_Holding_ID__c | Text | false |  |
| QuickBooks_Item_ID_Company_2__c | Text | false |  |
| Quickbooks_Item_ID__c | Text | false |  |
| Sales_Tax_Amount_Per_Quantity__c | Currency | false |  |
| Sales_Tax_Amount__c | Currency | false |  |
| Sales_Tax_Rate_Formula__c | Percent | false |  |
| Sales_Tax_Rate__c | Percent | false |  |
| Sales_Tax__c | Currency | false |  |
| Sort_Order__c | Number | false |  |
| Sub_Total__c | Currency | false |  |
| Total__c | Currency | false |  |
| UOM__c | Text | false |  |
| Unit_Price__c | Currency | false |  |
| Weight_UOM__c | Picklist | false |  |

### Inventory_Receipt__c (22 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Apex_Class_Name__c | Text | false |  |
| Bill_Due_Date__c | Date | false |  |
| Bill_Not_Received__c | Checkbox | false |  |
| Bill_Status__c | Picklist | false |  |
| Cancelled_Reason__c | Text | false |  |
| Description__c | LongTextArea | false |  |
| Integration_Sync_Date__c | DateTime | false |  |
| Integration_Sync__c | Checkbox | false |  |
| Inventory_Receipt_Date__c | Date | false |  |
| Invoice_Number__c | Text | false |  |
| Modify_Inventory_Receipt__c | Checkbox | false |  |
| Payment_Status__c | Picklist | false |  |
| Purchase_Order__c | MasterDetail | false | Purchase_Order__c |
| Quantity_Received__c | Summary | false |  |
| Sales_Tax__c | Summary | false |  |
| Status__c | Picklist | false |  |
| Supplier__c | Lookup | false | Account |
| Total_Due__c | Currency | false |  |
| Total_Fees__c | Summary | false |  |
| Total_Item_Cost__c | Summary | false |  |
| Total_Item_Landed_Cost__c | Summary | false |  |

### Inventory__c (46 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Clean_Kegs__c | Summary | false |  |
| Counter_Difference__c | Number | false |  |
| Credit_Returns_Complete__c | Summary | false |  |
| Default_Inventory_Level__c | Number | false |  |
| Default_Location__c | Checkbox | false |  |
| Dirty_Kegs__c | Summary | false |  |
| Force_Update__c | Checkbox | false |  |
| Inventory_Logs__c | Summary | false |  |
| Inventory_Receipt_Complete__c | Summary | false |  |
| Inventory_Receipt_In_Progress__c | Summary | false |  |
| Inventory_Value_Formula__c | Currency | false |  |
| Inventory_Value__c | Currency | false |  |
| Invoice_Complete__c | Summary | false |  |
| Invoice_In_Progress__c | Summary | false |  |
| Invoice_Picked__c | Summary | false |  |
| Invoice_Unsold__c | Summary | false |  |
| Item_Classification__c | Text | false |  |
| Item_Name__c | Text | false |  |
| Item__c | MasterDetail | false | Item__c |
| Layer_Quantity__c | Number | false |  |
| Location_Name__c | Text | false |  |
| Location__c | Lookup | false | Location__c |
| Offline_Creation_Checkbox__c | Checkbox | false |  |
| Offline_Resellable__c | Checkbox | false |  |
| Offline_Sellable_Quantity__c | Number | false |  |
| Pallet_Quantity__c | Number | false |  |
| Parent_Location__c | Text | false |  |
| Purchase_Order_In_Progress__c | Summary | false |  |
| Quantity_Available__c | Number | false |  |
| Quantity_Incoming__c | Number | false |  |
| Quantity_On_Hand__c | Number | false |  |
| Quantity_Reserved__c | Number | false |  |
| Quantity__c | Number | false |  |
| Reason__c | Picklist | false |  |
| Total_Units_Available__c | Number | false |  |
| Total_Units_On_Hand__c | Number | false |  |
| Total_Value__c | Currency | false |  |
| Transfers_Complete__c | Summary | false |  |
| Transfers_In_Progress__c | Summary | false |  |
| Transfers__c | Summary | false |  |
| Type__c | Text | false |  |
| UOM__c | Text | false |  |
| Units_Per_Case__c | Number | false |  |
| Warehouse__c | Text | false |  |
| Weight_UOM__c | Picklist | false |  |

### Invoice_Adjustment__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Adjustment__c | MasterDetail | false | Adjustment__c |
| Invoice__c | MasterDetail | false | Order__c |
| Quantity__c | Number | false |  |
| Total__c | Currency | false |  |
| Unit_Price__c | Currency | false |  |

### Invoice_Goal__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Goal_Tracking__c | MasterDetail | false | Goal_Tracking__c |
| Order__c | MasterDetail | false | Order__c |

### Invoice_Group__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Customer__c | Lookup | true | Account |
| Total_Cost__c | Currency | false |  |
| Total_Units__c | Number | false |  |

### Invoice_LWC_Configuration__mdt (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active_Tile__c | Checkbox | false |  |
| Active__c | Checkbox | false |  |
| Item_Types__c | Text | false |  |
| Product_Types__c | Text | false |  |
| Sort_Order__c | Number | false |  |
| Tile_Label__c | Text | false |  |
| Tile_Name__c | Text | false |  |
| Tile_Order__c | Number | false |  |

### Item_Component__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Child_Item__c | Lookup | false | Item__c |
| Item_Line__c | Text | false |  |
| Key__c | Text | false |  |
| Parent_Item__c | MasterDetail | false | Item__c |
| Quantity__c | Number | false |  |
| UOM__c | Text | false |  |

### Item_Line__c (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Key__c | Text | false |  |
| Mapping_Key__c | Text | false |  |
| Supplier__c | Lookup | false | Account |
| Type__c | Picklist | false |  |

### Item_Type__c (20 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABV__c | Percent | false |  |
| Base_Spirit_Category__c | Picklist | false |  |
| Base_Spirit_Subtype__c | Picklist | false |  |
| Base_Spirit_Type__c | Picklist | false |  |
| Classification__c | Picklist | false |  |
| Color__c | Picklist | false |  |
| Description__c | LongTextArea | false |  |
| Item_Line__c | Lookup | false | Item_Line__c |
| Key__c | Text | false |  |
| Label__c | Checkbox | false |  |
| Mapping_Key__c | Text | false |  |
| Packaging_Styles__c | MultiselectPicklist | false |  |
| Pairs_With__c | MultiselectPicklist | false |  |
| Short_Name__c | Text | false |  |
| Sub_Type__c | Picklist | false |  |
| Supplier_Number__c | Text | false |  |
| Supplier__c | Text | false |  |
| Target_Yield__c | Percent | false |  |
| Tier__c | Picklist | false |  |
| Type__c | Picklist | false |  |

### Item__c (135 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_Variance_ID__c | Text | false |  |
| Active__c | Checkbox | false |  |
| Average_Cost_Counter__c | Number | false |  |
| Average_Cost_Formula__c | Currency | false |  |
| Average_Cost_Total__c | Currency | false |  |
| Average_Cost__c | Currency | false |  |
| Average_Distribution_Cost__c | Currency | false |  |
| Average_FOB_Cost__c | Currency | false |  |
| Average_Production_Cost_Counter__c | Number | false |  |
| Average_Production_Cost_Total__c | Currency | false |  |
| Average_Production_Cost__c | Currency | false |  |
| Average_Purchase_Price__c | Currency | false |  |
| Average_Sale_Cost__c | Currency | false |  |
| Average_Sale_Counter__c | Number | false |  |
| Average_Sale_Price__c | Currency | false |  |
| Average_Sale_Total__c | Currency | false |  |
| Average_Shelf_Life_Days__c | Number | false |  |
| Average_Shipping_Cost__c | Currency | false |  |
| Average_Tax_Cost__c | Currency | false |  |
| Base_Spirit_Subtype__c | Picklist | false |  |
| Base_Spirit_Type__c | Picklist | false |  |
| Base_Spirit__c | Checkbox | false |  |
| Bottle_Size__c | Picklist | false |  |
| Bottles_per_Case__c | Number | false |  |
| Carrier_UPC__c | Text | false |  |
| Case_Dimensions__c | Text | false |  |
| Case_GTIN__c | Text | false |  |
| Case_Size__c | Picklist | false |  |
| Case_UPC__c | Text | false |  |
| Cases_Per_Pack__c | Number | false |  |
| Category__c | Text | false |  |
| Close_Out__c | Checkbox | false |  |
| Credit_Type__c | Text | false |  |
| Current_Incentive__c | Checkbox | false |  |
| Default_Inventory_Level__c | Summary | false |  |
| Default_Location__c | Lookup | false | Location__c |
| Default_Price__c | Currency | false |  |
| Distributor_Product_ID__c | Text | false |  |
| External_ID__c | Text | false |  |
| FinTech_UOM__c | Picklist | false |  |
| GPA_External_ID__c | Text | false |  |
| Height__c | Number | false |  |
| Inventory_Value_Calculated__c | Currency | false |  |
| Item_Line__c | Lookup | false | Item_Line__c |
| Item_Number__c | Text | false |  |
| Item_Purposes__c | MultiselectPicklist | false |  |
| Item_Type_Sub_Type__c | Text | false |  |
| Item_Type__c | Lookup | false | Item_Type__c |
| Keg_Deposit__c | Currency | false |  |
| Key__c | Text | false |  |
| Last_Distributed_Cost__c | Currency | false |  |
| Last_FOB_Cost__c | Currency | false |  |
| Last_Order_Date__c | Date | false |  |
| Last_Production_Cost__c | Currency | false |  |
| Last_Purchase_Price__c | Currency | false |  |
| Last_Sale_Date__c | Date | false |  |
| Last_Sale_Price__c | Currency | false |  |
| Last_Shipping_Cost__c | Currency | false |  |
| Last_Tax_Cost__c | Currency | false |  |
| Last_vs_Average_Cost_Percentage__c | Percent | false |  |
| Last_vs_Average_Cost_Price__c | Currency | false |  |
| Last_vs_Average_Production_2__c | Percent | false |  |
| Last_vs_Average_Production_Percentage__c | Percent | false |  |
| Last_vs_Average_Production__c | Currency | false |  |
| Last_vs_Average_Purchase_2__c | Percent | false |  |
| Last_vs_Average_Purchase__c | Currency | false |  |
| Last_vs_Average_Sale_Percentage__c | Percent | false |  |
| Last_vs_Average_Sale_Price__c | Currency | false |  |
| Layers_Per_Pallet__c | Number | false |  |
| Legacy_Name__c | Text | false |  |
| Length__c | Number | false |  |
| Liters_per_Case__c | Number | false |  |
| Logo_URL__c | LongTextArea | false |  |
| Mapping_Key__c | Text | false |  |
| Margin2__c | Percent | false |  |
| Margin__c | Currency | false |  |
| Margin_per_CE__c | Currency | false |  |
| Mixed_Beverage_Price__c | Currency | false |  |
| NABCA_Prefix_Code__c | Number | false |  |
| NABCA_Suffix_Code__c | Number | false |  |
| Order_Item__c | Checkbox | false |  |
| POS_Item_ID__c | Text | false |  |
| Pack_GTIN__c | Text | false |  |
| Packaging_Sizes__c | Picklist | false |  |
| Pre_Order__c | Checkbox | false |  |
| Priority__c | Picklist | false |  |
| Proof_Gallons__c | Number | false |  |
| Proof__c | Number | false |  |
| Purchase_UOM__c | Picklist | false |  |
| Quantity_Available__c | Summary | false |  |
| Quantity_Incoming__c | Summary | false |  |
| Quantity_On_Hand__c | Summary | false |  |
| Quantity__c | Number | false |  |
| QuickBooks_Credit_Memo_ID_Company_2__c | Text | false |  |
| QuickBooks_Credit_Memo_ID__c | Text | false |  |
| QuickBooks_Holding_ID__c | Text | false |  |
| QuickBooks_Item_ID_Company_2__c | Text | false |  |
| QuickBooks_Purchase_ID_Company_2__c | Text | false |  |
| QuickBooks_Purchase_ID__c | Text | false |  |
| QuickBooks_Return_ID_Company_2__c | Text | false |  |
| QuickBooks_Return_ID__c | Text | false |  |
| Quickbooks_Item_ID__c | Text | false |  |
| RTD__c | Checkbox | false |  |
| Retail_Price__c | Currency | false |  |
| Retail_Units_Per_Case__c | Number | false |  |
| Retailer_UPC__c | Text | false |  |
| SKU_Number__c | Text | false |  |
| Short_Name__c | Text | false |  |
| Short_UOM__c | Text | false |  |
| Size_UOM__c | Text | false |  |
| Sold_In_Units__c | Checkbox | false |  |
| State_Product_Code__c | Text | false |  |
| Stock_UOM_Sub_Type__c | Picklist | false |  |
| Stock_UOM__c | Picklist | false |  |
| Sub_Type__c | Picklist | false |  |
| Supplier_ID__c | Text | false |  |
| Supplier_Number__c | Text | false |  |
| Supplier__c | Text | false |  |
| Tax_Exempt__c | Checkbox | false |  |
| Template__c | Checkbox | false |  |
| Tracked_By_Lots__c | Checkbox | false |  |
| Type__c | Picklist | false |  |
| UOM_In_Fluid_Ounces__c | Number | false |  |
| UPC__c | Text | false |  |
| Unit_GTIN__c | Text | false |  |
| Unit_UPC__c | Text | false |  |
| Units_Per_Case__c | Number | false |  |
| Units_Per_Layer__c | Number | false |  |
| Units_Per_Pallet__c | Number | false |  |
| VIP_External_ID__c | Text | false |  |
| Weekly_Case_Goal__c | Number | false |  |
| Weekly_Revenue_Goal__c | Currency | false |  |
| Weight_UOM__c | Picklist | false |  |
| Weight__c | Number | false |  |
| Width__c | Number | false |  |

### Job_Candidate__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Candidate__c | MasterDetail | false | Candidate__c |
| Hired_Date__c | Date | false |  |
| Job__c | MasterDetail | false | Job__c |
| Open_Date__c | Date | false |  |
| Stage__c | Picklist | false |  |

### Job__c (9 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Department_Role__c | Picklist | false |  |
| Department__c | Picklist | false |  |
| Education__c | Picklist | false |  |
| Employment_Type__c | Picklist | false |  |
| Pay_Frequency__c | Picklist | false |  |
| Pay_Range_High__c | Currency | false |  |
| Pay_Range_Low__c | Currency | false |  |
| Pay_Type__c | Picklist | false |  |
| Stage__c | Picklist | false |  |

### Label__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABV__c | Percent | false |  |
| Approval_Date__c | Date | false |  |
| Category__c | Text | false |  |
| Date_Submitted_for_Approval__c | Date | false |  |
| ItemType__c | Lookup | false | Item_Type__c |
| Item_Type__c | Lookup | false | Item_Type__c |
| Item__c | MasterDetail | false | Item__c |
| Key__c | Text | false |  |
| Mapping_Key__c | Text | false |  |
| Status__c | Picklist | false |  |
| Type__c | Picklist | false |  |

### Location__c (35 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Clean_Kegs__c | Checkbox | false |  |
| Company__c | Picklist | false |  |
| Description__c | Text | false |  |
| Dirty_Kegs__c | Checkbox | false |  |
| Finished_Good__c | Checkbox | false |  |
| Is_Truck__c | Checkbox | false |  |
| Keg_Shell__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Location_City__c | Text | false |  |
| Location_Code__c | Text | false |  |
| Location_County__c | Text | false |  |
| Location_Hierarchy_Dev__c | Text | false |  |
| Location_Hierarchy__c | Text | false |  |
| Location_Number__c | Text | false |  |
| Location_Postal_Code__c | Text | false |  |
| Location_State__c | Text | false |  |
| Location_Street__c | Text | false |  |
| Location__c | Lookup | false | Location__c |
| Mapping_Key__c | Text | false |  |
| Merchandise__c | Checkbox | false |  |
| Notes__c | LongTextArea | false |  |
| POS_Location_ID__c | Text | false |  |
| Phone_Number__c | Phone | false |  |
| QuickBooks_Class_ID__c | Text | false |  |
| QuickBooks_Parent_Class_ID__c | Text | false |  |
| Sellable__c | Checkbox | false |  |
| Shelf_Tag_Enabled__c | Checkbox | false |  |
| Site__c | Lookup | false | Location__c |
| Tap_Handle__c | Checkbox | false |  |
| Tequila__c | Checkbox | false |  |
| Type__c | Picklist | false |  |
| Warehouse_Location_Id__c | Text | false |  |
| Warehouse_Location__c | Text | false |  |
| Warehouse__c | Text | false |  |

### Lot_Adjustment__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Inventory_Adjustment__c | Lookup | false | Inventory_Adjustment__c |
| Lot_Inventory__c | Lookup | false | Lot_Inventory__c |
| Quantity_Change__c | Number | false |  |

### Lot_Inventory_Receipt_Item__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Inventory_Receipt_Item__c | Lookup | true | Inventory_Receipt_Item__c |
| Lot__c | Lookup | true | Lot__c |

### Lot_Inventory__c (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Inventory_Value__c | Currency | false |  |
| Inventory__c | Lookup | true | Inventory__c |
| Lot_Expiration_Date__c | Date | false |  |
| Lot_Inventory_Location__c | Text | false |  |
| Lot_Receipt_Date__c | Date | false |  |
| Lot__c | Lookup | true | Lot__c |
| Quantity_Available__c | Number | false |  |
| Quantity_on_Hand__c | Number | false |  |

### Lot_Invoice_Item__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Invoice_Item_Lookup__c | Lookup | true | Order_Item__c |
| Lot__c | Lookup | true | Lot__c |

### Lot__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Active__c | Checkbox | false |  |
| Cost_per_Unit__c | Currency | false |  |
| Expiration_Date__c | Date | false |  |
| Inventory_Value__c | Currency | false |  |
| Item__c | Lookup | false | Item__c |
| Lot_Identifier__c | Text | false |  |
| Quantity_on_Hand__c | Number | false |  |
| Receipt_Date__c | Date | false |  |
| Sellable__c | Checkbox | false |  |
| Supplier__c | Lookup | false | Account |
| UOM_Type__c | Text | false |  |

### Maintenance__c (9 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Days_out_of_Service__c | Number | false |  |
| Description__c | LongTextArea | false |  |
| Equipment__c | MasterDetail | false | Equipment__c |
| Remove_from_Service__c | Checkbox | false |  |
| Removed_from_Service_Date__c | Date | false |  |
| Return_to_Service_Date__c | Date | false |  |
| Scheduled_Date__c | Date | false |  |
| Service_Provider__c | MasterDetail | false | Account |
| Type__c | Picklist | false |  |

