# Safe Bypass Patterns

## Overview

Recommended bypass patterns for common integration scenarios. Use bypasses judiciously to avoid data integrity issues.

---

## Bulk Historical Data Load

### Scenario
Loading historical orders that don't need business logic (emails, goals, delivery association).

### Safe Bypass
```apex
// Bypass non-critical triggers
MetadataTriggerHandler.bypass('TA_Order_AI_DeliveryAssociator');
MetadataTriggerHandler.bypass('TA_Order_AU_GoalUpdater');
MetadataTriggerHandler.bypass('TA_Invoice_AU_SendEmail');
U_OrderStatusValidationBypass.isBypassEnabled = true;

try {
    insert historicalOrders;
    insert historicalOrderItems;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
    MetadataTriggerHandler.clearAllBypasses();
}
```

### Why Safe
- No customer impact (historical data)
- No business process disruption
- Improves performance significantly

### Risks
- Missing delivery associations
- Missing goal tracking
- No audit emails sent

---

## Bulk Item Import

### Scenario
Importing products without creating inventory/pricelist records automatically.

### Safe Bypass
```apex
// Bypass auto-creation triggers
MetadataTriggerHandler.bypass('TA_Item_AI_InventoryCreator');
MetadataTriggerHandler.bypass('TA_Item_AI_PricelistItemCreator');

try {
    insert items;

    // Manually create inventory/pricelists as needed
    insert customInventoryRecords;
    insert customPricelistItems;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

### Why Safe
- Allows custom inventory setup
- Avoids mass creation of unnecessary records
- Controlled data creation

### Risks
- Must manually create inventory and pricelists
- Items may be missing inventory records

---

## Status Correction

### Scenario
Correcting order status due to data error (moving backward).

### Safe Bypass
```apex
// Bypass status validation for correction
U_OrderStatusValidationBypass.isBypassEnabled = true;

try {
    order.ohfy__Status__c = 'New';  // Correcting back to New
    update order;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
}
```

### Why Safe
- Temporary bypass for specific correction
- Immediately cleared after use
- Single record update (not bulk)

### Risks
- Could allow invalid status changes if not careful
- Bypasses business logic

---

## Inventory Audit Correction

### Scenario
Physical inventory count reveals discrepancy requiring negative adjustment.

### Safe Bypass
```apex
// Document reason clearly
Inventory_Adjustment__c adj = new Inventory_Adjustment__c(
    ohfy__Inventory__c = 'invId',
    ohfy__Adjustment_Type__c = 'Physical Count',
    ohfy__Quantity__c = -50,
    ohfy__Reason__c = 'Annual physical count - found damaged units'
);
insert adj;

// Bypass negative inventory check for correction
MetadataTriggerHandler.bypass('TA_Inventory_BU_PreventNegativeInventory');

try {
    inventory.ohfy__Quantity__c = 0;  // Correcting to actual count
    inventory.ohfy__Damaged_Quantity__c = 50;
    update inventory;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

### Why Safe
- Creates audit trail (Inventory_Adjustment__c)
- Documents reason
- Single correction, not bulk operation

### Risks
- Could allow inventory to go negative if not careful

---

## Duplicate Item Emergency Fix

### Scenario
Duplicate order items created due to integration error - need to bypass duplicate check to fix.

### Safe Bypass
```apex
// Query duplicate items
List<Order_Item__c> duplicates = [
    SELECT Id, ohfy__Order__c, ohfy__Item__c, ohfy__Quantity__c
    FROM Order_Item__c
    WHERE ohfy__Order__c = 'orderId'
    AND ohfy__Item__c = 'itemId'
];

// Combine quantities
Decimal totalQty = 0;
for (Order_Item__c item : duplicates) {
    totalQty += item.ohfy__Quantity__c;
}

// Keep first, delete rest
duplicates[0].ohfy__Quantity__c = totalQty;
update duplicates[0];

List<Order_Item__c> toDelete = new List<Order_Item__c>();
for (Integer i = 1; i < duplicates.size(); i++) {
    toDelete.add(duplicates[i]);
}

delete toDelete;
```

### Why Safe
- Fixes data integrity issue
- No bypass needed (using standard operations)
- Combines quantities properly

---

## UNSAFE Bypass Patterns (Avoid)

### ❌ Bypass All Triggers for All Operations

**NEVER DO THIS**:
```apex
// WRONG - bypasses all business logic
TriggerBase.bypass('Order__c');
TriggerBase.bypass('Order_Item__c');
TriggerBase.bypass('Item__c');
TriggerBase.bypass('Inventory__c');

// ... all operations ...

// May forget to clear bypasses!
```

**Why Unsafe**:
- Loses all data validation
- No audit trail
- Risk of data corruption
- May forget to clear bypasses

---

### ❌ Bypass Without try-finally

**NEVER DO THIS**:
```apex
// WRONG - if error occurs, bypass never cleared
MetadataTriggerHandler.bypass('TA_Invoice_BU_StatusUpdater');
update orders;  // If this fails, bypass remains active!
MetadataTriggerHandler.clearBypass('TA_Invoice_BU_StatusUpdater');
```

**Why Unsafe**:
- If operation fails, bypass remains active
- Affects subsequent operations
- Hard to debug

**CORRECT**:
```apex
MetadataTriggerHandler.bypass('TA_Invoice_BU_StatusUpdater');
try {
    update orders;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

---

### ❌ Bypass in Production Without Testing

**NEVER DO THIS**:
- Bypass triggers in production without testing in sandbox first
- Assume bypass has no side effects
- Use bypass as "default" integration pattern

**Why Unsafe**:
- Unknown side effects
- Data integrity risks
- Customer impact

---

## Bypass Decision Checklist

Before using bypass, ask:

1. **Is there another way?**
   - Can I use upsert instead of bypassing duplicate check?
   - Can I fix the data instead of bypassing validation?

2. **What business logic am I losing?**
   - Email notifications?
   - Audit trail?
   - Automated calculations?
   - Data integrity checks?

3. **Is this temporary?**
   - One-time data migration? ✓ Bypass OK
   - Ongoing integration? ✗ Find another solution

4. **Can I handle side effects?**
   - Will I manually create dependent records?
   - Will I fix data afterward?
   - Will I document what I bypassed?

5. **Have I tested in sandbox?**
   - With representative data volume?
   - With error scenarios?
   - Verified data integrity after?

---

## Recommended Safe Bypasses

| Scenario | Safe to Bypass | Keep Active |
|----------|----------------|-------------|
| Historical data load | Delivery association, Goal tracking, Emails | Status validation, Duplicate checks |
| Bulk item import | Auto-inventory creation, Auto-pricelist creation | Status validation |
| Status correction | Status progression validation | All other triggers |
| Inventory audit | Negative inventory check (with audit record) | All other triggers |
| Testing | Most triggers (in sandbox only) | Critical validations |

---

## See Also

- `../triggers/bypass-patterns.md` - Complete bypass documentation
- `../triggers/trigger-framework.md` - Trigger architecture
- `bulk-order-creation.md` - Bulk operation patterns
- `inventory-sync.md` - Inventory sync patterns
