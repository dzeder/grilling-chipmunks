# Duplicate Checks

## Order_Item__c Duplicate Prevention

### Validation Rule

**Trigger**: `TA_OrderItem_BI_DuplicateChecker`

**Rule**: Cannot have multiple Order_Item__c records with the same Item__c for the same Order__c.

### Error Message

**"This item already exists in the order"**

### Example Failure

```javascript
// Order already has this item
[
    { "ohfy__Order__c": "orderId", "ohfy__Item__c": "item123" },  // OK
    { "ohfy__Order__c": "orderId", "ohfy__Item__c": "item123" }   // ERROR - duplicate
]
```

### Solutions

**Option 1: Deduplicate Before Insert**
```javascript
const itemMap = new Map();
orderItems.forEach(item => {
    const key = item.Item__c;
    if (itemMap.has(key)) {
        // Combine quantities instead of creating duplicate
        itemMap.get(key).Quantity__c += item.Quantity__c;
    } else {
        itemMap.set(key, item);
    }
});
const deduplicatedItems = Array.from(itemMap.values());
```

**Option 2: Use External_ID Upsert**
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Order_Item__c/ohfy__External_ID__c/order1_item123",
    "body": {
        "ohfy__Order__c": "orderId",
        "ohfy__Item__c": "itemId",
        "ohfy__Quantity__c": 5
    }
}
```

**Option 3: Bypass (Use with Caution)**
```apex
MetadataTriggerHandler.bypass('TA_OrderItem_BI_DuplicateChecker');
try {
    insert orderItems;
} finally {
    MetadataTriggerHandler.clearBypass('TA_OrderItem_BI_DuplicateChecker');
}
```

---

## Inventory__c Duplicate Prevention

### Validation Rule

**Trigger**: `TA_Inventory_BI_DuplicateChecker`

**Rule**: Cannot have multiple Inventory__c records with the same Item__c + Location__c combination.

### Error Message

**"Duplicate inventory record for this item and location"**

### Solutions

**Option 1: Query First**
```javascript
const existing = await sf.query({
    query: `SELECT Id FROM ohfy__Inventory__c
            WHERE ohfy__Item__c = 'itemId'
            AND ohfy__Location__c = 'locationId'`
});

if (existing.length > 0) {
    // Update existing
    await sf.update({ Id: existing[0].Id, ohfy__Quantity__c: 100 });
} else {
    // Create new
    await sf.create({ ohfy__Item__c: "itemId", ohfy__Location__c: "locationId", ohfy__Quantity__c: 100 });
}
```

**Option 2: Composite Upsert**
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Inventory__c/ohfy__Item__c,ohfy__Location__c/itemId,locationId",
    "body": {
        "ohfy__Quantity__c": 100
    }
}
```

---

## External_ID__c Duplicate Prevention

### Validation Rule

**Salesforce Standard**: External_ID__c fields are marked as unique.

### Error Message

**"DUPLICATE_EXTERNAL_ID: External_ID__c already exists"**

### Solutions

**Option 1: Use PATCH (Upsert)**
```javascript
// Recommended - creates or updates
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/shopify_12345",
    "body": { "Name": "Product Name" }
}
```

**Option 2: Query First**
```javascript
const existing = await sf.query({
    query: `SELECT Id FROM ohfy__Item__c WHERE ohfy__External_ID__c = 'shopify_12345'`
});

if (existing.length > 0) {
    await sf.update({ Id: existing[0].Id, Name: "Updated" });
} else {
    await sf.create({ ohfy__External_ID__c: "shopify_12345", Name: "New" });
}
```

---

## See Also

- `../triggers/order-triggers.md` - TA_OrderItem_BI_DuplicateChecker
- `../triggers/inventory-triggers.md` - TA_Inventory_BI_DuplicateChecker
- `../triggers/common-errors.md` - Duplicate error messages
- `../data-model/external-id-patterns.md` - External ID patterns
