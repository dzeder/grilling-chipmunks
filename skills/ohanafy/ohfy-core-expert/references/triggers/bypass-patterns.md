# Bypass Patterns

## Overview

OHFY-Core provides three mechanisms for bypassing trigger logic during bulk operations or specific integration scenarios. Proper use of bypass patterns prevents validation errors and improves performance during data loads.

## Method 1: Object-Level Bypass (TriggerBase)

### Pattern
```apex
TriggerBase.bypass('Order__c');
try {
    // Perform DML operations
    insert orders;
} finally {
    TriggerBase.clearBypass('Order__c');
}
```

### When to Use
- Bypass **all** trigger actions for an entire object
- Bulk data loads where no trigger logic should execute
- Testing scenarios requiring complete trigger bypass

### Example: Bulk Order Creation
```apex
// Bypass all Order__c triggers
TriggerBase.bypass('Order__c');
TriggerBase.bypass('Order_Item__c');

try {
    // Insert orders without any trigger actions firing
    insert orderList;

    // Insert order items without any trigger actions firing
    insert orderItemList;
} finally {
    // Always clear bypass in finally block
    TriggerBase.clearBypass('Order__c');
    TriggerBase.clearBypass('Order_Item__c');
}
```

### Available Objects for Bypass
All OHFY-Core custom objects support TriggerBase bypass:
- `Account`
- `Item__c`
- `Item_Line__c`
- `Item_Type__c`
- `Order__c`
- `Order_Item__c`
- `Inventory__c`
- `Location__c`
- `Payment__c`
- `Payment_Method__c`
- `Purchase_Order__c`
- `Purchase_Order_Item__c`
- And all other objects with triggers

## Method 2: Action-Level Bypass (MetadataTriggerHandler)

### Pattern
```apex
MetadataTriggerHandler.bypass('TA_Invoice_BU_StatusUpdater');
try {
    // Perform DML operations
    update invoices;
} finally {
    MetadataTriggerHandler.clearBypass('TA_Invoice_BU_StatusUpdater');
}
```

### When to Use
- Bypass **specific** trigger action(s) while allowing others to execute
- Need granular control over which business logic runs
- Temporarily disable problematic trigger action during fix

### Example: Bypass Status Validation Only
```apex
// Bypass only status validation, allow other Order__c triggers to execute
MetadataTriggerHandler.bypass('TA_Invoice_BU_StatusUpdater');
MetadataTriggerHandler.bypass('TA_Invoice_AU_StatusHistoryLogger');

try {
    // Update invoices - status validation bypassed, but other logic runs
    update invoiceList;
} finally {
    MetadataTriggerHandler.clearBypass('TA_Invoice_BU_StatusUpdater');
    MetadataTriggerHandler.clearBypass('TA_Invoice_AU_StatusHistoryLogger');
}
```

### Common Trigger Actions to Bypass

**Order__c (Invoice)**:
- `TA_Invoice_BU_StatusUpdater` - Status progression validation
- `TA_Invoice_AU_Completer` - Auto-completion logic
- `TA_Invoice_AU_Canceller` - Cancellation processing
- `TA_Order_AI_DeliveryAssociator` - Delivery route association
- `TA_Order_AU_GoalUpdater` - Sales goal updates

**Item__c (Product)**:
- `TA_Item_AI_InventoryCreator` - Auto-create inventory records
- `TA_Item_AI_PricelistItemCreator` - Auto-create pricelist items
- `TA_Item_BU_StatusChecker` - Active status validation

**Inventory__c**:
- `TA_Inventory_BU_PreventNegativeInventory` - Negative quantity check

**Order_Item__c (Invoice Item)**:
- `TA_OrderItem_BI_DuplicateChecker` - Duplicate item validation
- `TA_InvoiceItem_BD_AdjDeleter` - Adjustment deletion on item delete

### Clear All Bypasses
```apex
MetadataTriggerHandler.clearAllBypasses();
```

Use this to reset all action-level bypasses at once.

## Method 3: Validation Utility Bypass

### Pattern
```apex
U_OrderStatusValidationBypass.isBypassEnabled = true;
try {
    // Perform status updates
    invoiceRecord.Status__c = 'Loaded';
    update invoiceRecord;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
}
```

### When to Use
- Bypass **specific validation logic** without disabling entire trigger action
- Allow non-sequential status transitions during data migrations
- Fine-grained control over specific validation rules

### Available Validation Utilities

**U_OrderStatusValidationBypass**:
- Controls status progression validation for Order__c
- Allows skipping status steps (e.g., New → Loaded without Picking)
- Used during bulk imports or status corrections

### Example: Non-Sequential Status Update
```apex
// Allow jumping directly to Loaded status
U_OrderStatusValidationBypass.isBypassEnabled = true;

try {
    // Normally this would fail: must progress through Picking first
    invoiceRecord.Status__c = 'Loaded';
    update invoiceRecord;

    // Multiple records
    for (Order__c inv : invoiceList) {
        inv.Status__c = 'Complete';
    }
    update invoiceList;
} finally {
    // Always reset bypass
    U_OrderStatusValidationBypass.isBypassEnabled = false;
}
```

## Combined Bypass Strategy

For complex integrations, combine multiple bypass methods:

```apex
// Example: Bulk order creation with selective bypass
U_OrderStatusValidationBypass.isBypassEnabled = true;
MetadataTriggerHandler.bypass('TA_Order_AI_DeliveryAssociator');
MetadataTriggerHandler.bypass('TA_Order_AU_GoalUpdater');

try {
    // Create orders with non-standard statuses, no delivery association, no goal updates
    for (Order__c order : orderList) {
        order.Status__c = 'Complete'; // Normally requires progression
    }
    insert orderList;

    // Create order items (still runs duplicate check and other validations)
    insert orderItemList;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
    MetadataTriggerHandler.clearAllBypasses();
}
```

## Best Practices

### 1. Always Use try-finally
```apex
// CORRECT
TriggerBase.bypass('Order__c');
try {
    insert orders;
} finally {
    TriggerBase.clearBypass('Order__c');
}

// WRONG - bypass not cleared if exception occurs
TriggerBase.bypass('Order__c');
insert orders;
TriggerBase.clearBypass('Order__c');
```

### 2. Minimize Bypass Scope
```apex
// BETTER - bypass only specific action
MetadataTriggerHandler.bypass('TA_Invoice_BU_StatusUpdater');

// WORSE - bypasses all triggers
TriggerBase.bypass('Order__c');
```

### 3. Document Why Bypassing
```apex
// Bypass status validation because migrating legacy orders
// that don't follow standard progression
U_OrderStatusValidationBypass.isBypassEnabled = true;
```

### 4. Clear Bypasses Immediately
```apex
// CORRECT - clear after operation
insert orders;
TriggerBase.clearBypass('Order__c');

// WRONG - bypass still active for subsequent code
insert orders;
// ... more code ...
TriggerBase.clearBypass('Order__c'); // Too late!
```

### 5. Test Without Bypass First
Verify trigger logic works correctly before adding bypass. Only bypass when you've confirmed triggers cause legitimate issues for your use case.

## Common Bypass Scenarios

### Bulk Order Import
```apex
U_OrderStatusValidationBypass.isBypassEnabled = true;
MetadataTriggerHandler.bypass('TA_Order_AI_DeliveryAssociator');

try {
    insert orderList;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
    MetadataTriggerHandler.clearAllBypasses();
}
```

### Bulk Item Import
```apex
MetadataTriggerHandler.bypass('TA_Item_AI_InventoryCreator');
MetadataTriggerHandler.bypass('TA_Item_AI_PricelistItemCreator');

try {
    insert itemList;
    // Handle inventory/pricelist creation separately if needed
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

### Emergency Status Correction
```apex
U_OrderStatusValidationBypass.isBypassEnabled = true;
try {
    invoice.Status__c = 'New'; // Normally can't move backward
    update invoice;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
}
```

## Risks and Warnings

### ⚠️ Data Integrity
Bypassing triggers can compromise data integrity:
- Missing inventory adjustments
- Incomplete audit trails
- Broken relationships
- Invalid status progressions

### ⚠️ Business Logic Gaps
Bypassed logic won't execute:
- Automated calculations won't run
- Notifications won't send
- Dependent records won't create
- Validations won't enforce

### ⚠️ Testing Required
Always test with bypass enabled:
- Verify data integrity maintained
- Check for missing dependent records
- Validate business rules still enforced elsewhere
- Ensure system state remains consistent

## See Also

- `trigger-framework.md` - Overall trigger framework architecture
- `order-triggers.md` - Specific Order__c trigger actions
- `item-triggers.md` - Specific Item__c trigger actions
- `common-errors.md` - Errors that may require bypass
- `../integration-patterns/safe-bypass-patterns.md` - Recommended patterns
