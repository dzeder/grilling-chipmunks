# Inventory__c Trigger Actions

## Overview

Inventory__c has **5 trigger actions** that prevent negative inventory, validate default locations, check duplicate inventory records, and calculate available quantities.

## BEFORE INSERT

### TA_Inventory_BI_DuplicateChecker

**Purpose**: Prevent duplicate inventory records for same item/location

**When It Fires**: When Inventory__c is created

**What It Does**:
- Checks if Inventory__c already exists for Item__c + Location__c combination
- Throws error if duplicate found
- Ensures one inventory record per item per location

**Integration Impact**: HIGH - Prevents duplicate inventory

**Error**: `"Duplicate inventory record for this item and location"`

**Solutions**:

1. **Use upsert via composite External_ID**:
```javascript
// Tray Salesforce composite request
{
    "method": "PATCH",
    "url": "/services/data/v58.0/sobjects/Inventory__c/Item__c,Location__c/itemId,locationId",
    "body": {
        "Quantity__c": 100
    }
}
```

2. **Query first to check existence**:
```javascript
// Check if exists before attempting insert
const existing = await sf.query({
    query: "SELECT Id FROM Inventory__c WHERE Item__c = 'itemId' AND Location__c = 'locationId'"
});

if (existing.length > 0) {
    // Update existing
    update existing[0];
} else {
    // Insert new
    insert newInventory;
}
```

3. **Bypass for special cases**:
```apex
MetadataTriggerHandler.bypass('TA_Inventory_BI_DuplicateChecker');
```

---

## BEFORE UPDATE

### TA_Inventory_BU_PreventNegativeInventory

**Purpose**: Prevent inventory quantity from going negative

**When It Fires**: When Quantity__c field changes

**What It Does**:
- Validates Quantity__c >= 0
- Throws error: "You cannot remove more inventory than is available"
- Protects against overselling and data integrity issues

**Integration Impact**: HIGH - Most common inventory integration blocker

**Error Example**:
```javascript
// Current inventory: 10 units
{
    "Inventory__c": "invId",
    "Quantity__c": -5 // ERROR - can't be negative
}
```

**Solutions**:

1. **Check inventory before update** (RECOMMENDED):
```javascript
// Query current inventory
const currentQty = await sf.query({
    query: "SELECT Quantity__c FROM Inventory__c WHERE Id = 'invId'"
});

const requested = 15;
const available = currentQty[0].Quantity__c; // 10

if (available >= requested) {
    // Safe to reduce inventory
    await sf.update({
        Id: "invId",
        Quantity__c: available - requested  // 10 - 15 = -5 (would fail)
    });
} else {
    // Insufficient inventory
    throw new Error(`Only ${available} units available, ${requested} requested`);
}
```

2. **Use Allocation__c pattern** (RECOMMENDED):
```javascript
// Create allocation record instead of direct decrement
{
    "Inventory__c": "invId",
    "Quantity__c": 15,
    "Order__c": "orderId",
    "Type__c": "Reserved"
}
// Trigger handles inventory reduction safely with validation
```

3. **Bypass for corrections** (USE WITH CAUTION):
```apex
MetadataTriggerHandler.bypass('TA_Inventory_BU_PreventNegativeInventory');
try {
    inventory.Quantity__c = -5; // Correction for audit
    update inventory;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

**Warning**: Bypassing this trigger can cause serious data integrity issues!

---

### TA_Inventory_BU_DefaultLocationCheck

**Purpose**: Validate default location rules

**When It Fires**: When Is_Default__c field changes

**What It Does**:
- Ensures only one default location per organization/warehouse
- Validates location hierarchy
- Maintains default location integrity

**Integration Impact**: Low - affects warehouse configuration

---

### TA_Inventory_BU_StatusChecker

**Purpose**: Validate inventory status transitions

**When It Fires**: When Status__c field changes

**What It Does**:
- Validates status progression (Available → Reserved → Allocated → Depleted)
- Prevents invalid status changes
- Maintains inventory state integrity

**Integration Impact**: Medium - affects inventory workflow

**Valid Status Progression**:
```
Available → Reserved → Allocated → Depleted
          ↓          ↓
      Damaged    Expired
```

---

## AFTER UPDATE

### TA_Inventory_AU_QuantityCalculator

**Purpose**: Recalculate available quantity based on allocations

**When It Fires**: When Quantity__c or allocation fields change

**What It Does**:
- Calculates Available_Quantity__c = Quantity__c - Allocated_Quantity__c - Reserved_Quantity__c
- Updates dependent quantity fields
- Maintains accurate available inventory

**Integration Impact**: HIGH - Affects inventory availability

**Formula**:
```
Available_Quantity__c = Quantity__c
                      - Allocated_Quantity__c
                      - Reserved_Quantity__c
                      - Damaged_Quantity__c
                      - Expired_Quantity__c
```

**Example**:
```javascript
// Update inventory quantity
{
    "Inventory__c": "invId",
    "Quantity__c": 100,
    "Allocated_Quantity__c": 20,
    "Reserved_Quantity__c": 15
}

// Trigger calculates:
// Available_Quantity__c = 100 - 20 - 15 = 65
```

---

## Common Integration Patterns

### Safe Inventory Decrement

```javascript
// Option 1: Use Allocation (RECOMMENDED)
{
    "Allocation__c": {
        "Inventory__c": "invId",
        "Quantity__c": 15,
        "Order__c": "orderId"
    }
}
// Trigger validates and decrements safely

// Option 2: Check first, then update
const current = await sf.query({
    query: "SELECT Quantity__c FROM Inventory__c WHERE Id = 'invId'"
});

if (current[0].Quantity__c >= 15) {
    await sf.update({
        Id: "invId",
        Quantity__c: current[0].Quantity__c - 15
    });
}
```

---

### Bulk Inventory Sync

```apex
// For bulk sync from external system
Map<String, Inventory__c> inventoryMap = new Map<String, Inventory__c>();

// Query existing inventory
for (Inventory__c inv : [
    SELECT Id, Item__c, Location__c, Quantity__c
    FROM Inventory__c
]) {
    String key = inv.Item__c + '_' + inv.Location__c;
    inventoryMap.put(key, inv);
}

// Process external inventory data
List<Inventory__c> toUpdate = new List<Inventory__c>();
List<Inventory__c> toInsert = new List<Inventory__c>();

for (ExternalInventory ext : externalData) {
    String key = ext.itemId + '_' + ext.locationId;

    if (inventoryMap.containsKey(key)) {
        // Update existing
        Inventory__c inv = inventoryMap.get(key);
        inv.Quantity__c = ext.quantity;
        toUpdate.add(inv);
    } else {
        // Create new
        toInsert.add(new Inventory__c(
            Item__c = ext.itemId,
            Location__c = ext.locationId,
            Quantity__c = ext.quantity
        ));
    }
}

update toUpdate;
insert toInsert;
```

---

### Inventory Adjustment Pattern

```apex
// Create adjustment record to track inventory changes
Inventory_Adjustment__c adj = new Inventory_Adjustment__c(
    Inventory__c = 'invId',
    Adjustment_Type__c = 'Manual Correction',
    Quantity__c = -10,  // Remove 10 units
    Reason__c = 'Damaged goods',
    Adjusted_By__c = UserInfo.getUserId()
);
insert adj;

// Update inventory (with trigger validation)
Inventory__c inv = [SELECT Id, Quantity__c FROM Inventory__c WHERE Id = 'invId'];
inv.Quantity__c -= 10;
inv.Damaged_Quantity__c += 10;
update inv;
```

---

### Create Inventory for New Item/Location

```javascript
// Check if inventory exists
const existing = await sf.query({
    query: `SELECT Id FROM Inventory__c
            WHERE Item__c = 'itemId'
            AND Location__c = 'locationId'`
});

if (existing.length === 0) {
    // Create new inventory record
    await sf.create({
        sobject: "Inventory__c",
        Item__c: "itemId",
        Location__c: "locationId",
        Quantity__c: 0,
        Available_Quantity__c: 0,
        Status__c: "Available"
    });
} else {
    // Already exists - update if needed
    await sf.update({
        Id: existing[0].Id,
        Quantity__c: 100
    });
}
```

---

## Allocation Workflow

### Standard Allocation Process

1. **Reserve Inventory** (Create Allocation__c):
```javascript
{
    "Inventory__c": "invId",
    "Quantity__c": 15,
    "Order__c": "orderId",
    "Type__c": "Reserved"
}
```

2. **Allocate for Picking** (Update Allocation__c):
```javascript
{
    "Allocation__c": "allocationId",
    "Type__c": "Allocated"
}
// Moves from Reserved_Quantity__c to Allocated_Quantity__c
```

3. **Complete Allocation** (Delete or Update Allocation__c):
```javascript
// Option 1: Delete allocation (inventory decremented)
DELETE /Allocation__c/allocationId

// Option 2: Mark as fulfilled
{
    "Allocation__c": "allocationId",
    "Type__c": "Fulfilled",
    "Fulfilled_Date__c": "2025-01-15"
}
```

---

## Inventory Fields

### Quantity Fields
- **Quantity__c** - Total physical quantity
- **Available_Quantity__c** - Available for sale (calculated)
- **Allocated_Quantity__c** - Reserved for orders
- **Reserved_Quantity__c** - Pre-reserved (quotes, holds)
- **Damaged_Quantity__c** - Damaged inventory
- **Expired_Quantity__c** - Expired inventory

### Status Values
- **Available** - Ready for sale
- **Reserved** - Pre-reserved for order
- **Allocated** - Assigned to specific order
- **Depleted** - Out of stock
- **Damaged** - Damaged goods
- **Expired** - Past expiration date

---

## Trigger Performance Notes

**Heavy Triggers** (may impact bulk operations):
- `TA_Inventory_AU_QuantityCalculator` - Recalculates multiple fields
- `TA_Inventory_BI_DuplicateChecker` - Queries existing records

**Light Triggers** (minimal impact):
- `TA_Inventory_BU_PreventNegativeInventory` - Simple validation
- `TA_Inventory_BU_StatusChecker` - Status validation
- `TA_Inventory_BU_DefaultLocationCheck` - Validation query

---

## Common Errors and Solutions

### "You cannot remove more inventory than is available"

**Cause**: Trying to set Quantity__c negative or reduce below allocated amount

**Solutions**:
1. Check available quantity before update
2. Use Allocation__c pattern
3. Adjust allocation first, then quantity
4. Bypass trigger for corrections (use with caution)

---

### "Duplicate inventory record for this item and location"

**Cause**: Trying to create second Inventory__c for same Item__c + Location__c

**Solutions**:
1. Query first to check existence
2. Use upsert operation
3. Update existing inventory instead of creating new
4. Bypass trigger for special cases (use with caution)

---

### Insufficient Inventory

**Prevention**:
```javascript
// Always check before allocating
const available = await sf.query({
    query: `SELECT Available_Quantity__c
            FROM Inventory__c
            WHERE Id = 'invId'`
});

const requested = 15;
if (available[0].Available_Quantity__c >= requested) {
    // Safe to proceed
    createAllocation(invId, requested);
} else {
    // Insufficient inventory
    throw new Error(
        `Only ${available[0].Available_Quantity__c} units available`
    );
}
```

---

## See Also

- `bypass-patterns.md` - How to bypass inventory triggers
- `common-errors.md` - Error messages from these triggers
- `../data-model/inventory-objects.md` - Inventory object structure
- `../integration-patterns/inventory-sync.md` - Sync patterns
- `../validations/required-dependencies.md` - Data dependencies
