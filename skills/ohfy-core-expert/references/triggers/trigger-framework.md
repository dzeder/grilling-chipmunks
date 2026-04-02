# Trigger Framework

## Overview

OHFY-Core uses a **Metadata-Driven Trigger Framework** based on Google's Apex Trigger Actions Framework. This provides centralized control over trigger execution, bypass capabilities, and organized trigger action management.

## Architecture

### Custom Metadata Types

**sObject_Trigger_Setting__mdt** - Object-level bypass control
- Controls whether triggers fire for entire objects
- Used by `TriggerBase` class for object-level bypass

**Trigger_Action__mdt** - Individual action configuration
- Defines specific trigger actions and their execution context
- Specifies order of execution (Before/After, Insert/Update/Delete)
- Allows granular bypass control via `MetadataTriggerHandler`

### Core Classes

**TriggerBase** - Foundation class for all triggers
- Provides object-level bypass mechanism
- Manages trigger context (Before/After, Insert/Update/Delete/Undelete)
- Delegates to `MetadataTriggerHandler` for action execution

**MetadataTriggerHandler** - Metadata-driven action executor
- Reads `Trigger_Action__mdt` records to determine which actions to execute
- Provides action-level bypass mechanism
- Handles execution order based on metadata configuration

## Trigger Pattern

All triggers in OHFY-Core follow this standard pattern:

```apex
trigger OrderTrigger on Order__c (before insert, before update, before delete,
                                   after insert, after update, after delete, after undelete) {
    new TriggerBase().run();
}
```

The trigger itself contains **no business logic** - all logic is in trigger action classes defined via metadata.

## Active Triggers (37 Total)

| Object | Trigger Name | Contexts |
|--------|--------------|----------|
| Account | AccountTrigger | All |
| Allocation__c | AllocationTrigger | All |
| Delivery__c | DeliveryTrigger | All |
| External_ID__c | ExternalIDTrigger | All |
| Integration_Sync__c | IntegrationSyncTrigger | All |
| Inventory__c | InventoryTrigger | All |
| Inventory_Adjustment__c | InventoryAdjustmentTrigger | All |
| Invoice_Group__c | InvoiceGroupTrigger | All |
| Item__c | ItemTrigger | All |
| Item_Line__c | ItemLineTrigger | All |
| Item_Type__c | ItemTypeTrigger | All |
| Lot__c | LotTrigger | All |
| Lot_Inventory__c | LotInventoryTrigger | All |
| Lot_Invoice_Item__c | LotInvoiceItemTrigger | All |
| Order__c | OrderTrigger | All |
| Order_Item__c | OrderItemTrigger | All |
| Payment__c | PaymentTrigger | All |
| Payment_Method__c | PaymentMethodTrigger | All |
| Pricelist__c | PricelistTrigger | All |
| Pricelist_Item__c | PricelistItemTrigger | All |
| Purchase_Order__c | PurchaseOrderTrigger | All |
| Purchase_Order_Item__c | PurchaseOrderItemTrigger | All |
| Route__c | RouteTrigger | All |
| Vendor__c | VendorTrigger | All |

## Trigger Action Naming Convention

Trigger actions follow this naming pattern:

```
TA_{Object}_{Context}_{Description}
```

Examples:
- `TA_Invoice_BU_StatusUpdater` - Order__c Before Update Status Updater
- `TA_Item_AI_InventoryCreator` - Item__c After Insert Inventory Creator
- `TA_Inventory_BU_PreventNegativeInventory` - Inventory__c Before Update Prevent Negative

Context abbreviations:
- **BI** - Before Insert
- **BU** - Before Update
- **BD** - Before Delete
- **AI** - After Insert
- **AU** - After Update
- **AD** - After Delete
- **AUNDELETE** - After Undelete

## Execution Flow

```
1. DML Operation Initiated
   ↓
2. Trigger Fires (e.g., OrderTrigger)
   ↓
3. TriggerBase.run() called
   ↓
4. Check object-level bypass (sObject_Trigger_Setting__mdt)
   ↓
5. If not bypassed, delegate to MetadataTriggerHandler
   ↓
6. Query Trigger_Action__mdt for active actions
   ↓
7. Execute actions in metadata-defined order
   ↓
8. Check action-level bypass before each action
   ↓
9. Execute action if not bypassed
```

## Benefits

1. **Centralized Control**: All trigger logic managed via metadata
2. **Bypass Flexibility**: Object-level or action-level bypass
3. **Ordered Execution**: Metadata defines action execution order
4. **Testability**: Easy to isolate and test individual actions
5. **Maintainability**: Business logic separated from trigger infrastructure
6. **No Governor Limit Issues**: Single trigger per object prevents "too many triggers" errors

## See Also

- `bypass-patterns.md` - Detailed bypass implementation patterns
- `order-triggers.md` - Order__c specific trigger actions
- `item-triggers.md` - Item__c specific trigger actions
- `inventory-triggers.md` - Inventory__c specific trigger actions
- `common-errors.md` - Trigger-related error messages and solutions
