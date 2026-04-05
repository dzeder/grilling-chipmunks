# Inventory Objects

## Overview

Inventory objects manage warehouse locations, inventory quantities, lot tracking, and inventory allocations.

---

## Location__c (Warehouse)

**Purpose**: Warehouse/storage locations

**API Name**: `ohfy__Location__c`

**Critical Fields**:
- `Name` - Location name/identifier
- `Location_Type__c` - Warehouse, Store, Truck, etc.
- `Active__c` - Boolean
- `Is_Default__c` - Default location flag
- `Address__c` - Physical address

**Relationships**:
```
Location__c
  └── Inventory__c (1:M) - Inventory per location
```

**Triggers**:
- `TA_Location_AI_InventoryCreator` - Auto-creates Inventory__c for all active Item__c when location created
- `TA_Location_BD_InventoryDeleter` - Deletes Inventory__c when location deleted

**Integration Pattern**:
```javascript
{
    "method": "POST",
    "url": "/services/data/v58.0/sobjects/ohfy__Location__c",
    "body": {
        "Name": "Warehouse A",
        "ohfy__Location_Type__c": "Warehouse",
        "ohfy__Active__c": true
    }
}
```

---

## Inventory__c (Stock)

**Purpose**: Inventory quantity per item per location

**API Name**: `ohfy__Inventory__c`

**Critical Fields**:
- `Item__c` - Product (lookup, **REQUIRED**)
- `Location__c` - Warehouse (lookup, **REQUIRED**)
- `Quantity__c` - Total quantity (cannot be negative)
- `Available_Quantity__c` - Available for sale (calculated)
- `Allocated_Quantity__c` - Reserved for orders
- `Reserved_Quantity__c` - Pre-reserved
- `Damaged_Quantity__c` - Damaged goods
- `Expired_Quantity__c` - Expired goods
- `Status__c` - Available, Reserved, Allocated, Depleted

**Unique Constraint**: One Inventory__c per Item__c + Location__c combination

**Relationships**:
```
Inventory__c
  ├── Item__c (M:1) - Product [REQUIRED]
  ├── Location__c (M:1) - Warehouse [REQUIRED]
  └── Allocation__c (1:M) - Order allocations
```

**Triggers**:
- `TA_Inventory_BU_PreventNegativeInventory` - Prevents Quantity__c < 0
- `TA_Inventory_BI_DuplicateChecker` - Prevents duplicate Item__c + Location__c
- `TA_Inventory_AU_QuantityCalculator` - Calculates Available_Quantity__c

**Integration Pattern**:
```javascript
// Upsert via Item__c + Location__c composite key
{
    "method": "PATCH",
    "url": "/services/data/v58.0/sobjects/ohfy__Inventory__c/ohfy__Item__c,ohfy__Location__c/itemId,locationId",
    "body": {
        "ohfy__Quantity__c": 100
    }
}
```

**Available Quantity Formula**:
```
Available_Quantity__c = Quantity__c
                      - Allocated_Quantity__c
                      - Reserved_Quantity__c
                      - Damaged_Quantity__c
                      - Expired_Quantity__c
```

---

## Allocation__c (Inventory Reservation)

**Purpose**: Reserve inventory for orders

**API Name**: `ohfy__Allocation__c`

**Critical Fields**:
- `Inventory__c` - Inventory record (lookup, **REQUIRED**)
- `Quantity__c` - Allocated quantity
- `Order__c` - Order (lookup)
- `Order_Item__c` - Order item (lookup)
- `Type__c` - Reserved, Allocated, Fulfilled
- `Allocation_Date__c` - Date allocated
- `Fulfilled_Date__c` - Date fulfilled

**Relationships**:
```
Allocation__c
  ├── Inventory__c (M:1) - Inventory record [REQUIRED]
  ├── Order__c (M:1) - Parent order
  └── Order_Item__c (M:1) - Order line item
```

**Workflow**:
```
1. Create Allocation (Type = "Reserved")
   → Inventory.Reserved_Quantity__c increases

2. Update Allocation (Type = "Allocated")
   → Reserved_Quantity__c decreases
   → Allocated_Quantity__c increases

3. Delete Allocation (order fulfilled)
   → Allocated_Quantity__c decreases
   → Quantity__c decreases
```

**Integration Pattern**:
```javascript
// Create allocation
{
    "method": "POST",
    "url": "/services/data/v58.0/sobjects/ohfy__Allocation__c",
    "body": {
        "ohfy__Inventory__c": "invId",
        "ohfy__Quantity__c": 15,
        "ohfy__Order__c": "orderId",
        "ohfy__Type__c": "Reserved"
    }
}
```

---

## Lot__c (Lot/Serial Number)

**Purpose**: Track lot numbers and serial numbers

**API Name**: `ohfy__Lot__c`

**Critical Fields**:
- `Name` - Lot number
- `Item__c` - Product (lookup, **REQUIRED**)
- `Expiration_Date__c` - Expiration date
- `Manufacture_Date__c` - Manufacture date
- `Status__c` - Active, Expired, Recalled

**Relationships**:
```
Lot__c
  ├── Item__c (M:1) - Product [REQUIRED]
  ├── Lot_Inventory__c (1:M) - Lot inventory per location
  └── Lot_Invoice_Item__c (1:M) - Lot assignments to orders
```

**Integration Pattern**:
```javascript
{
    "method": "POST",
    "url": "/services/data/v58.0/sobjects/ohfy__Lot__c",
    "body": {
        "Name": "LOT-2025-001",
        "ohfy__Item__c": "itemId",
        "ohfy__Expiration_Date__c": "2026-01-15",
        "ohfy__Status__c": "Active"
    }
}
```

---

## Lot_Inventory__c (Lot Quantity)

**Purpose**: Lot quantity per location

**API Name**: `ohfy__Lot_Inventory__c`

**Critical Fields**:
- `Lot__c` - Lot number (lookup, **REQUIRED**)
- `Location__c` - Warehouse (lookup, **REQUIRED**)
- `Quantity__c` - Quantity in lot

**Relationships**:
```
Lot_Inventory__c
  ├── Lot__c (M:1) - Lot number [REQUIRED]
  └── Location__c (M:1) - Warehouse [REQUIRED]
```

---

## Lot_Invoice_Item__c (Lot Assignment)

**Purpose**: Track which lots were used for order items

**API Name**: `ohfy__Lot_Invoice_Item__c`

**Critical Fields**:
- `Order_Item__c` - Order item (Master-Detail, **REQUIRED**)
- `Lot__c` - Lot number (lookup, **REQUIRED**)
- `Quantity__c` - Quantity from lot

**Relationships**:
```
Lot_Invoice_Item__c
  ├── Order_Item__c (M:1) - Order item [Master-Detail, REQUIRED]
  └── Lot__c (M:1) - Lot number [REQUIRED]
```

---

## Inventory_Adjustment__c (Audit Trail)

**Purpose**: Track inventory adjustments and corrections

**API Name**: `ohfy__Inventory_Adjustment__c`

**Critical Fields**:
- `Inventory__c` - Inventory record (lookup, **REQUIRED**)
- `Adjustment_Type__c` - Physical Count, Damage, Expiration, etc.
- `Quantity__c` - Adjustment amount (+/-)
- `Reason__c` - Adjustment reason
- `Adjusted_By__c` - User who made adjustment
- `Adjustment_Date__c` - Date of adjustment

**Integration Pattern**:
```javascript
{
    "method": "POST",
    "url": "/services/data/v58.0/sobjects/ohfy__Inventory_Adjustment__c",
    "body": {
        "ohfy__Inventory__c": "invId",
        "ohfy__Adjustment_Type__c": "Physical Count",
        "ohfy__Quantity__c": -10,
        "ohfy__Reason__c": "Found damaged units during cycle count"
    }
}
```

---

## Common Inventory Patterns

### Check Inventory Availability
```javascript
const inventory = await sf.query({
    query: `SELECT Available_Quantity__c
            FROM ohfy__Inventory__c
            WHERE ohfy__Item__c = 'itemId'
            AND ohfy__Location__c = 'locationId'`
});

const available = inventory[0].ohfy__Available_Quantity__c;
if (available >= requestedQty) {
    // Proceed with allocation
}
```

### Create Allocation
```javascript
// Step 1: Check availability
// Step 2: Create allocation
{
    "ohfy__Inventory__c": "invId",
    "ohfy__Quantity__c": 15,
    "ohfy__Order__c": "orderId",
    "ohfy__Type__c": "Reserved"
}
// Trigger updates Reserved_Quantity__c automatically
```

### Adjust Inventory
```javascript
// Step 1: Create adjustment record
{
    "ohfy__Inventory__c": "invId",
    "ohfy__Adjustment_Type__c": "Damage",
    "ohfy__Quantity__c": -5,
    "ohfy__Reason__c": "Damaged in transit"
}

// Step 2: Update inventory
{
    "Id": "invId",
    "ohfy__Quantity__c": 95,  // was 100
    "ohfy__Damaged_Quantity__c": 5
}
```

---

## See Also

- `core-objects.md` - Item__c and Order__c objects
- `../triggers/inventory-triggers.md` - Inventory trigger actions
- `../integration-patterns/inventory-sync.md` - Sync patterns
- `../validations/required-dependencies.md` - Data dependencies
