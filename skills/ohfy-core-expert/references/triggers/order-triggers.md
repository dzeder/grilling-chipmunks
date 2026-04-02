# Order__c Trigger Actions

## Overview

Order__c (Invoice) has **19 trigger actions** that handle status validation, delivery association, goal tracking, promotions, email notifications, and order completion logic.

## BEFORE INSERT

### TA_Invoice_BI_OfflineCreationHandler

**Purpose**: Handle offline invoice creation from mobile app

**When It Fires**: When Order__c created with offline flag

**What It Does**:
- Validates offline creation data
- Sets up initial invoice state for offline orders
- Prepares invoice for sync with online system

**Integration Impact**: Low - only affects mobile offline orders

---

## BEFORE UPDATE

### TA_Invoice_BU_StatusUpdater

**Purpose**: Validate status progression rules

**When It Fires**: When Status__c field changes

**What It Does**:
- Validates status can only move forward (New → Picking → Loaded → etc.)
- Throws error: "Cannot move to a previous status"
- Prevents skipping required status steps

**Integration Impact**: HIGH - Most common integration blocker

**Valid Progressions**:
```
New (1) → Scheduled (1) → In Progress (1) → Picking (2) → Loaded (3) →
Out For Delivery (4) → Delivered (5) → Complete (6)
                                        ↓
                                   Cancelled (7)
```

**Bypass**:
```apex
U_OrderStatusValidationBypass.isBypassEnabled = true;
```

**See Also**: `../validations/status-transitions.md`

---

### TA_Invoice_BU_PaymentInfo

**Purpose**: Update payment-related fields on invoice

**When It Fires**: When payment fields change

**What It Does**:
- Calculates payment status
- Updates payment method information
- Validates payment amounts

**Integration Impact**: Medium - affects payment integrations

---

### TA_Order_BU_DeliveryAssociator

**Purpose**: Validate delivery route before certain statuses

**When It Fires**: When Status__c changes to delivery-required status

**What It Does**:
- Checks if Delivery__c (route) is set
- Throws error if moving to delivery status without route
- Error: "Order must have delivery route before completion"

**Integration Impact**: Medium - order-to-delivery workflow

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Order_BU_DeliveryAssociator');
```

---

## BEFORE DELETE

### TA_Order_BD_PromoInvoiceItemDeleter

**Purpose**: Delete promotional items when order deleted

**When It Fires**: When Order__c is deleted

**What It Does**:
- Finds associated promotional Order_Item__c records
- Deletes promotional items automatically
- Cleans up promotion-related data

**Integration Impact**: Low - automatic cleanup

---

### TA_Order_BD_GoalUpdater

**Purpose**: Update sales goals when order deleted

**When It Fires**: When Order__c is deleted

**What It Does**:
- Recalculates sales goal progress
- Removes order contribution from goal totals
- Updates goal achievement status

**Integration Impact**: Low - affects reporting only

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Order_BD_GoalUpdater');
```

---

### TA_Invoice_BD_AdjDeleter

**Purpose**: Delete adjustments when order deleted

**When It Fires**: When Order__c is deleted

**What It Does**:
- Deletes related Invoice_Adjustment__c records
- Prevents orphaned adjustment records
- Maintains data integrity

**Integration Impact**: Low - automatic cleanup

---

## AFTER INSERT

### TA_Order_AI_DeliveryAssociator

**Purpose**: Auto-associate order with delivery route

**When It Fires**: When Order__c is created

**What It Does**:
- Attempts to find matching Delivery__c (route)
- Associates order with route based on customer/date
- Sets Delivery__c field automatically

**Integration Impact**: Medium - delivery workflow

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Order_AI_DeliveryAssociator');
```

**Use Case**: Bypass when creating orders without delivery routes (pickup orders, future orders, etc.)

---

### TA_Order_AI_GoalInvoiceCreator

**Purpose**: Create Goal_Invoice__c junction record

**When It Fires**: When Order__c is created

**What It Does**:
- Links order to active sales goal
- Creates Goal_Invoice__c record
- Tracks order toward goal achievement

**Integration Impact**: Low - affects reporting only

---

### TA_Invoice_AI_OfflineCreationHandler

**Purpose**: Complete offline invoice creation setup

**When It Fires**: When Order__c created with offline flag

**What It Does**:
- Finalizes offline invoice setup
- Syncs with online system
- Generates invoice number

**Integration Impact**: Low - only affects mobile offline orders

---

## AFTER UPDATE

### TA_Invoice_AU_Completer

**Purpose**: Execute completion logic when order completes

**When It Fires**: When Status__c changes to "Complete"

**What It Does**:
- Finalizes order totals
- Triggers completion workflows
- Locks order from further changes
- May trigger inventory adjustments

**Integration Impact**: HIGH - completion workflow

**Related Triggers**:
- May trigger inventory allocation
- May trigger payment processing
- May trigger notifications

---

### TA_Invoice_AU_Canceller

**Purpose**: Execute cancellation logic

**When It Fires**: When Status__c changes to "Cancelled"

**What It Does**:
- Releases inventory allocations
- Reverses any applied adjustments
- Updates related records
- Prevents further modifications

**Integration Impact**: HIGH - cancellation workflow

**Related Effects**:
- Inventory returned to available
- Promotions reversed
- Payments may be refunded

---

### TA_Invoice_AU_StatusHistoryLogger

**Purpose**: Log status change history

**When It Fires**: When Status__c changes

**What It Does**:
- Creates audit trail of status changes
- Records who changed status and when
- Maintains status history timeline

**Integration Impact**: Low - audit only

---

### TA_Invoice_AU_SendEmail

**Purpose**: Send email notifications on status change

**When It Fires**: When Status__c changes to specific values

**What It Does**:
- Sends order confirmation emails
- Sends delivery notifications
- Sends completion receipts
- Uses email templates

**Integration Impact**: Medium - customer notifications

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Invoice_AU_SendEmail');
```

**Use Case**: Bypass during bulk imports or testing to prevent spam

---

### TA_Order_AU_GoalUpdater

**Purpose**: Update sales goal progress

**When It Fires**: When order total or status changes

**What It Does**:
- Recalculates goal achievement
- Updates goal progress percentages
- Triggers goal completion alerts

**Integration Impact**: Low - affects reporting only

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Order_AU_GoalUpdater');
```

**Use Case**: Bypass during bulk data loads to improve performance

---

### TA_Order_AU_PlacementUpdater

**Purpose**: Update distributor placement records

**When It Fires**: When order status or items change

**What It Does**:
- Updates Distributor_Placement__c records
- Tracks placement fulfillment
- Updates placement status

**Integration Impact**: Medium - GPA integration workflow

---

### TA_Order_AU_PromotionUpdater

**Purpose**: Recalculate promotional items and discounts

**When It Fires**: When order items or totals change

**What It Does**:
- Evaluates active promotions
- Applies/removes promotional items
- Recalculates discounts
- Updates order totals

**Integration Impact**: HIGH - pricing and promotions

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Order_AU_PromotionUpdater');
```

**Use Case**: Bypass when importing historical orders that shouldn't trigger promotions

---

### TA_Order_AU_ReorderCloner

**Purpose**: Clone order when reorder requested

**When It Fires**: When Reorder__c checkbox = true

**What It Does**:
- Creates copy of order
- Copies all order items
- Resets status to "New"
- Links to original order

**Integration Impact**: Medium - reorder functionality

---

### TA_Order_AU_NameSetter

**Purpose**: Auto-generate order name/number

**When It Fires**: When order created or key fields change

**What It Does**:
- Generates unique order number
- Sets Name field to formatted value
- May use auto-number sequence

**Integration Impact**: Low - auto-naming only

---

### TA_Invoice_AU_InvoiceGroupUpdater

**Purpose**: Update Invoice_Group__c aggregate data

**When It Fires**: When order added to/removed from group

**What It Does**:
- Recalculates group totals
- Updates group status
- Maintains group integrity

**Integration Impact**: Low - invoice grouping feature

---

### TA_Invoice_AU_DeliveryAssociator

**Purpose**: Associate order with delivery after update

**When It Fires**: When delivery-related fields change

**What It Does**:
- Updates Delivery__c association
- Recalculates delivery totals
- Updates delivery status

**Integration Impact**: Medium - delivery workflow

---

### TA_Invoice_AU_InvoiceAdjustmentUpdater

**Purpose**: Update related Invoice_Adjustment__c records

**When It Fires**: When order totals or status change

**What It Does**:
- Recalculates adjustment amounts
- Updates adjustment status
- Applies/removes adjustments

**Integration Impact**: Medium - order adjustments

---

### TA_Invoice_AU_AdjStatusUpdater

**Purpose**: Update adjustment statuses based on invoice status

**When It Fires**: When Status__c changes

**What It Does**:
- Syncs adjustment status with invoice status
- Locks/unlocks adjustments
- Validates adjustment states

**Integration Impact**: Low - adjustment workflow

---

### TA_Invoice_AU_OfflineUpdateInvoice

**Purpose**: Sync offline invoice changes

**When It Fires**: When offline invoice syncs with online system

**What It Does**:
- Merges offline changes
- Resolves conflicts
- Updates invoice state

**Integration Impact**: Low - mobile offline only

---

### TA_Invoice_AU_PalletItemUpdater

**Purpose**: Update pallet items when invoice changes

**When It Fires**: When pallet-related fields change

**What It Does**:
- Recalculates pallet counts
- Updates pallet items
- Maintains pallet integrity

**Integration Impact**: Low - pallet management feature

---

### TA_Invoice_AU_TruckLoader

**Purpose**: Handle truck loading workflow

**When It Fires**: When Status__c changes to "Loaded"

**What It Does**:
- Associates invoice with truck
- Updates truck inventory
- Prepares for delivery

**Integration Impact**: Medium - truck loading workflow

---

## AFTER DELETE

### TA_Order_AD_DeliveryFieldsUpdater

**Purpose**: Update delivery when order deleted

**When It Fires**: When Order__c is deleted

**What It Does**:
- Recalculates delivery totals
- Updates delivery status
- Removes order from delivery

**Integration Impact**: Medium - delivery workflow

---

### TA_Invoice_AD_InvoiceGroupUpdater

**Purpose**: Update group when invoice deleted

**When It Fires**: When Order__c is deleted

**What It Does**:
- Recalculates group totals
- Updates group status
- Maintains group integrity

**Integration Impact**: Low - invoice grouping feature

---

## Common Integration Patterns

### Create Order with Items (No Triggers)

```apex
// Bypass all triggers for bulk import
TriggerBase.bypass('Order__c');
TriggerBase.bypass('Order_Item__c');
try {
    insert orders;
    insert orderItems;
} finally {
    TriggerBase.clearBypass('Order__c');
    TriggerBase.clearBypass('Order_Item__c');
}
```

---

### Create Order with Selective Bypass

```apex
// Allow most triggers, bypass only problematic ones
MetadataTriggerHandler.bypass('TA_Order_AI_DeliveryAssociator');
MetadataTriggerHandler.bypass('TA_Order_AU_GoalUpdater');
MetadataTriggerHandler.bypass('TA_Invoice_AU_SendEmail');

try {
    insert orders;
    insert orderItems;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

---

### Update Order Status

```apex
// Skip status validation for bulk update
U_OrderStatusValidationBypass.isBypassEnabled = true;
try {
    for (Order__c order : orders) {
        order.Status__c = 'Complete';
    }
    update orders;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
}
```

---

## Trigger Performance Notes

**Heavy Triggers** (may impact bulk operations):
- `TA_Invoice_AU_Completer` - Complex completion logic
- `TA_Invoice_AU_Canceller` - Reverses many changes
- `TA_Order_AU_PromotionUpdater` - Evaluates all promotions
- `TA_Order_AU_ReorderCloner` - Clones entire order

**Light Triggers** (minimal impact):
- `TA_Order_AU_NameSetter` - Simple field update
- `TA_Invoice_AU_StatusHistoryLogger` - Insert audit record
- `TA_Invoice_BU_PaymentInfo` - Field calculations

---

## See Also

- `bypass-patterns.md` - How to bypass specific triggers
- `common-errors.md` - Error messages from these triggers
- `../validations/status-transitions.md` - Status progression rules
- `../integration-patterns/bulk-order-creation.md` - Bulk creation patterns
