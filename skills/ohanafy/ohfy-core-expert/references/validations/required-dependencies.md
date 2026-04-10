# Required Dependencies

## Master-Detail Relationships

### Order_Item__c Requires Order__c

**Relationship**: Master-Detail

**Requirement**: Order__c must exist before creating Order_Item__c

**Error**: `"INVALID_CROSS_REFERENCE_KEY: Order__c does not exist"`

**Solution**: Create Order__c first in composite request
```javascript
[
    { "referenceId": "order1", "url": ".../ohfy__Order__c", ... },
    { "body": { "ohfy__Order__c": "@{order1.id}" }, ... }
]
```

---

### Purchase_Order_Item__c Requires Purchase_Order__c

**Relationship**: Master-Detail

**Requirement**: Purchase_Order__c must exist before creating Purchase_Order_Item__c

**Error**: `"INVALID_CROSS_REFERENCE_KEY: Purchase_Order__c does not exist"`

**Solution**: See composite-request-order.md for sequencing

---

## Item Dependencies

### Item__c Creation Triggers

When Item__c is created, two triggers auto-create dependent records:

**TA_Item_AI_InventoryCreator**:
- Creates Inventory__c for each active Location__c
- Dependency: Active Location__c records must exist

**TA_Item_AI_PricelistItemCreator**:
- Creates Pricelist_Item__c for each active Pricelist__c
- Dependency: Active Pricelist__c records must exist

**Bypass**: If no locations or pricelists exist, bypass these triggers:
```apex
MetadataTriggerHandler.bypass('TA_Item_AI_InventoryCreator');
MetadataTriggerHandler.bypass('TA_Item_AI_PricelistItemCreator');
try {
    insert items;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

---

### Item__c Deactivation Requirements

**Trigger**: `TA_Item_BU_StatusChecker`

**Requirement**: Item__c can only be deactivated if all Inventory__c records have Quantity__c = 0

**Error**: `"Cannot deactivate item with existing inventory"`

**Solution**: Zero inventory first
```javascript
// Step 1: Zero inventory
{
    "Id": "invId",
    "ohfy__Quantity__c": 0
}

// Step 2: Deactivate item
{
    "Id": "itemId",
    "ohfy__Active__c": false
}
```

---

## UOM Dependencies

### Item__c UOM Conversion

**Trigger**: `TA_Item_BI_SetUOMConversion`

**Requirement**: Transformation_Setting__c must exist for Unit_of_Measure__c

**Error**: `"No transformation setting found for UOM conversion"`

**Solution**: Create Transformation_Setting__c record
```javascript
{
    "ohfy__From_UOM__c": "EA",
    "ohfy__To_UOM__c": "CS",
    "ohfy__Conversion_Factor__c": 12
}
```

---

## Delivery Route Dependencies

### Order__c Completion

**Trigger**: `TA_Order_BU_DeliveryRouteValidator`

**Requirement**: Order__c must have Delivery__c (route) before Status__c = "Complete"

**Error**: `"Order must have delivery route before completion"`

**Solution**: Associate delivery route first
```javascript
// Step 1: Associate route
{
    "Id": "orderId",
    "ohfy__Delivery__c": "deliveryId"
}

// Step 2: Complete order
{
    "Id": "orderId",
    "ohfy__Status__c": "Complete"
}
```

**Bypass**:
```apex
MetadataTriggerHandler.bypass('TA_Order_BU_DeliveryRouteValidator');
```

---

## Lookup Dependencies (Recommended)

While not strictly required, these lookups should exist before creating records:

### Order__c → Account

**Recommended**: Upsert Account before creating Order__c
```javascript
[
    { "referenceId": "account1", "url": ".../Account/ohfy__External_ID__c/...", ... },
    { "body": { "ohfy__Account__c": "@{account1.id}" }, ... }
]
```

### Item__c → Item_Line__c, Item_Type__c

**Recommended**: Upsert brand and type before creating Item__c
```javascript
[
    { "referenceId": "brand1", "url": ".../ohfy__Item_Line__c/...", ... },
    { "referenceId": "type1", "url": ".../ohfy__Item_Type__c/...", ... },
    { "body": { "ohfy__Item_Line__c": "@{brand1.id}", "ohfy__Item_Type__c": "@{type1.id}" }, ... }
]
```

---

## Data Integrity Dependencies

### Inventory Allocation

**Requirement**: Inventory__c.Available_Quantity__c must be >= Allocation__c.Quantity__c

**Error**: `"You cannot remove more inventory than is available"`

**Solution**: Check availability before allocation
```javascript
const inventory = await sf.query({
    query: `SELECT Available_Quantity__c FROM ohfy__Inventory__c WHERE Id = 'invId'`
});

if (inventory[0].Available_Quantity__c >= requestedQty) {
    // Proceed with allocation
    await sf.create({
        sobject: "ohfy__Allocation__c",
        ohfy__Inventory__c: "invId",
        ohfy__Quantity__c: requestedQty
    });
}
```

---

## See Also

- `../data-model/composite-request-order.md` - Operation sequencing
- `../triggers/item-triggers.md` - Item dependencies
- `../triggers/inventory-triggers.md` - Inventory validation
- `../triggers/common-errors.md` - Dependency error messages
