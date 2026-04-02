# Item__c Trigger Actions

## Overview

Item__c (Product) has **9 trigger actions** that handle UOM conversion setup, inventory creation, pricelist management, status validation, and child record cleanup.

## BEFORE INSERT

### TA_Item_BI_SetUOMConversion

**Purpose**: Set up unit of measure conversion factors

**When It Fires**: When Item__c is created with Unit_of_Measure__c

**What It Does**:
- Looks up Transformation_Setting__c for UOM conversion
- Sets conversion factor fields
- Enables EA ↔ CS (each ↔ case) conversions
- Error: "No transformation setting found for UOM conversion"

**Integration Impact**: HIGH - Required for multi-UOM items

**Example**:
```javascript
// Item with "CS" (case) UOM
{
    "Item__c": "itemId",
    "Unit_of_Measure__c": "CS"
}
// Trigger looks up CS → EA transformation (e.g., 12 EA per CS)
```

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Item_BI_SetUOMConversion');
```

**Use Case**: Bypass when importing items that don't need UOM conversion

---

### TA_Item_BI_ShortNameSetter

**Purpose**: Generate short name for mobile/compact display

**When It Fires**: When Item__c is created

**What It Does**:
- Creates abbreviated name from full Name field
- Truncates to character limit
- Sets Short_Name__c field

**Integration Impact**: Low - display only

---

## BEFORE UPDATE

### TA_Item_BU_StatusChecker

**Purpose**: Prevent deactivation of items with inventory

**When It Fires**: When Active__c field changes to false

**What It Does**:
- Queries associated Inventory__c records
- Checks if any have Quantity__c > 0
- Throws error: "Cannot deactivate item with existing inventory"
- Prevents deactivation if inventory exists

**Integration Impact**: HIGH - Item deactivation blocker

**Error Example**:
```javascript
// Item has 50 units in warehouse
{
    "Item__c": "itemId",
    "Active__c": false // ERROR - must zero inventory first
}
```

**Solutions**:

1. **Zero inventory first**:
```javascript
// Step 1: Adjust inventory to zero
{
    "Inventory__c": "invId",
    "Quantity__c": 0
}

// Step 2: Deactivate item
{
    "Item__c": "itemId",
    "Active__c": false
}
```

2. **Bypass for special cases**:
```apex
MetadataTriggerHandler.bypass('TA_Item_BU_StatusChecker');
```

---

### TA_Item_BU_UpdateUOMConversion

**Purpose**: Update UOM conversion when Unit_of_Measure__c changes

**When It Fires**: When Unit_of_Measure__c field changes

**What It Does**:
- Recalculates conversion factors
- Updates transformation settings
- Validates UOM compatibility

**Integration Impact**: Medium - UOM changes

---

## BEFORE DELETE

### TA_Item_BD_ChildRemover

**Purpose**: Delete child records when item deleted

**When It Fires**: When Item__c is deleted

**What It Does**:
- Deletes associated Inventory__c records
- Deletes associated Pricelist_Item__c records
- Deletes other dependent child records
- Prevents orphaned data

**Integration Impact**: HIGH - Cascading deletes

**Warning**: This will delete all inventory and pricing data for the item!

---

## AFTER INSERT

### TA_Item_AI_InventoryCreator

**Purpose**: Auto-create inventory records for new items

**When It Fires**: When Item__c is created

**What It Does**:
- Creates Inventory__c record for each active Location__c
- Sets initial Quantity__c = 0
- Links inventory to item and location
- Enables inventory tracking immediately

**Integration Impact**: HIGH - Auto-creates related records

**Example**:
```javascript
// Insert Item
{ "Item__c": "newItem", "Name": "Product A" }

// Trigger auto-creates:
[
    { "Item__c": "newItem", "Location__c": "warehouse1", "Quantity__c": 0 },
    { "Item__c": "newItem", "Location__c": "warehouse2", "Quantity__c": 0 },
    { "Item__c": "newItem", "Location__c": "warehouse3", "Quantity__c": 0 }
]
```

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Item_AI_InventoryCreator');
```

**Use Case**: Bypass during bulk item imports when inventory will be loaded separately

**Performance Impact**: Creates N Inventory__c records (N = number of active locations)

---

### TA_Item_AI_PricelistItemCreator

**Purpose**: Auto-create pricelist items for new products

**When It Fires**: When Item__c is created

**What It Does**:
- Creates Pricelist_Item__c record for each active Pricelist__c
- Sets initial price (may be 0 or default price)
- Links item to all pricelists
- Enables pricing immediately

**Integration Impact**: HIGH - Auto-creates related records

**Example**:
```javascript
// Insert Item
{ "Item__c": "newItem", "Name": "Product A", "Base_Price__c": 10.00 }

// Trigger auto-creates:
[
    { "Item__c": "newItem", "Pricelist__c": "retail", "Price__c": 10.00 },
    { "Item__c": "newItem", "Pricelist__c": "wholesale", "Price__c": 8.00 },
    { "Item__c": "newItem", "Pricelist__c": "distributor", "Price__c": 6.00 }
]
```

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Item_AI_PricelistItemCreator');
```

**Use Case**: Bypass during bulk item imports when prices will be loaded separately

**Performance Impact**: Creates M Pricelist_Item__c records (M = number of active pricelists)

---

## AFTER UPDATE

### TA_Item_AU_InventoryValueUpdater

**Purpose**: Recalculate inventory value when item cost changes

**When It Fires**: When Cost__c or other pricing fields change

**What It Does**:
- Queries all Inventory__c records for item
- Recalculates Inventory_Value__c = Quantity__c × Cost__c
- Updates all inventory records
- Maintains accurate inventory valuation

**Integration Impact**: Medium - Affects inventory valuation

**Performance Impact**: Updates all inventory records for item (N updates where N = number of locations)

---

### TA_Item_AU_PricelistItemUpdater

**Purpose**: Update pricelist items when item price changes

**When It Fires**: When Base_Price__c or other pricing fields change

**What It Does**:
- Queries all Pricelist_Item__c records for item
- Applies pricing rules and margins
- Updates prices across all pricelists
- Maintains pricing consistency

**Integration Impact**: HIGH - Affects all prices

**Performance Impact**: Updates all pricelist items for item (M updates where M = number of pricelists)

**Example**:
```javascript
// Update item base price
{ "Item__c": "itemId", "Base_Price__c": 12.00 } // was 10.00

// Trigger updates all pricelists:
// Retail: 12.00 (100% of base)
// Wholesale: 9.60 (80% of base)
// Distributor: 7.20 (60% of base)
```

---

## Common Integration Patterns

### Create Item Without Auto-Children

```apex
// Bypass auto-creation of inventory and pricelist items
MetadataTriggerHandler.bypass('TA_Item_AI_InventoryCreator');
MetadataTriggerHandler.bypass('TA_Item_AI_PricelistItemCreator');

try {
    insert items;

    // Manually create inventory/pricing as needed
    insert customInventoryRecords;
    insert customPricelistRecords;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

---

### Bulk Item Import

```apex
// For best performance during bulk import
MetadataTriggerHandler.bypass('TA_Item_AI_InventoryCreator');
MetadataTriggerHandler.bypass('TA_Item_AI_PricelistItemCreator');
MetadataTriggerHandler.bypass('TA_Item_BI_ShortNameSetter');

try {
    insert itemList; // No triggers fire

    // Load inventory separately after all items created
    insert inventoryList;
    insert pricelistItemList;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

---

### Deactivate Item with Inventory

```apex
// Option 1: Zero inventory first (RECOMMENDED)
inventory.Quantity__c = 0;
update inventory;

item.Active__c = false;
update item;

// Option 2: Bypass status checker (USE WITH CAUTION)
MetadataTriggerHandler.bypass('TA_Item_BU_StatusChecker');
try {
    item.Active__c = false;
    update item;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

---

### Update Item Price

```javascript
// Update will cascade to all pricelists via TA_Item_AU_PricelistItemUpdater
{
    "Item__c": "itemId",
    "Base_Price__c": 15.00
}
// All Pricelist_Item__c records auto-updated
```

---

## Trigger Performance Notes

**Heavy Triggers** (may impact bulk operations):
- `TA_Item_AI_InventoryCreator` - Creates N records (N = locations)
- `TA_Item_AI_PricelistItemCreator` - Creates M records (M = pricelists)
- `TA_Item_AU_InventoryValueUpdater` - Updates N records
- `TA_Item_AU_PricelistItemUpdater` - Updates M records
- `TA_Item_BD_ChildRemover` - Deletes all child records

**Light Triggers** (minimal impact):
- `TA_Item_BI_ShortNameSetter` - Simple field calculation
- `TA_Item_BI_SetUOMConversion` - Lookup and field set
- `TA_Item_BU_StatusChecker` - Validation query

---

## UOM Conversion Details

### Standard UOMs
- **EA** - Each (base unit)
- **CS** - Case (container of eaches)
- **PK** - Pack (container of eaches)
- **BOX** - Box (container of eaches)

### Transformation Settings
Required Transformation_Setting__c records:
```
From_UOM__c | To_UOM__c | Conversion_Factor__c
------------|-----------|--------------------
EA          | CS        | 12 (12 EA = 1 CS)
EA          | PK        | 6 (6 EA = 1 PK)
CS          | EA        | 0.0833 (1 CS = 12 EA)
```

### Missing UOM Error
**Error**: "No transformation setting found for UOM conversion"

**Fix**: Create Transformation_Setting__c record:
```javascript
{
    "From_UOM__c": "EA",
    "To_UOM__c": "CS",
    "Conversion_Factor__c": 12
}
```

---

## Auto-Creation Impact

When creating 100 items with 5 locations and 3 pricelists:

| Operation | Records Created |
|-----------|----------------|
| Items | 100 |
| Inventory (auto) | 500 (100 × 5) |
| Pricelist Items (auto) | 300 (100 × 3) |
| **Total** | **900** |

**Recommendation**: For bulk imports, bypass auto-creation triggers and load child records separately for better performance and control.

---

## See Also

- `bypass-patterns.md` - How to bypass specific triggers
- `common-errors.md` - Error messages from these triggers
- `../data-model/core-objects.md` - Item__c object structure
- `../field-mappings/item-fields.md` - Complete field list
- `../integration-patterns/bulk-order-creation.md` - Bulk creation patterns
