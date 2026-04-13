# Composite Request Order

## Overview

Salesforce composite requests must follow a specific order when creating/updating records with Master-Detail relationships. Parent records must exist before children can reference them.

---

## Operation Sequencing Rules

### Rule 1: Parents Before Children

Master-Detail relationships require the parent record to exist before creating the child:

```
CORRECT Order:
1. Order__c (parent)
2. Order_Item__c (child) - references Order__c

WRONG Order:
1. Order_Item__c - ERROR: Order__c does not exist yet
2. Order__c
```

### Rule 2: Lookups Before References

Records must exist before they can be referenced via lookup:

```
CORRECT Order:
1. Account (lookup target)
2. Order__c (references Account via lookup)

WRONG Order:
1. Order__c (tries to reference non-existent Account)
2. Account
```

### Rule 3: Use Upsert for Referenced Records

Use PATCH (upsert) with External_ID for records that might already exist:

```
CORRECT:
1. PATCH Account via External_ID__c (creates or updates)
2. POST Order__c (reference @{account1.id} from step 1)

WRONG:
1. POST Account (fails if already exists)
```

---

## Standard Operation Order

### Complete Order Creation Sequence

```
1. Account (Customer) - PATCH via External_ID__c
2. Item_Line__c (Brand) - PATCH via Mapping_Key__c or VIP_External_ID__c
3. Item_Type__c (Category) - PATCH via Mapping_Key__c or VIP_External_ID__c
4. Item__c (Product) - PATCH via External_ID__c
5. Order__c (Invoice) - PATCH via External_ID__c, reference Account
6. Order_Item__c (Line Item) - PATCH via External_ID__c, reference Order__c and Item__c
```

---

## Example: Create Complete Order

```javascript
{
    "allOrNone": false,
    "compositeRequest": [
        // Step 1: Upsert Customer
        {
            "referenceId": "account1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/Account/ohfy__External_ID__c/shopify_12345",
            "body": {
                "Name": "ABC Distributing",
                "Phone": "555-1234",
                "Type": "Customer"
            }
        },

        // Step 2: Upsert Brand
        {
            "referenceId": "brand1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Item_Line__c/ohfy__Mapping_Key__c/brand_xyz",
            "body": {
                "Name": "XYZ Brewery",
                "ohfy__Active__c": true
            }
        },

        // Step 3: Upsert Category
        {
            "referenceId": "type1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Item_Type__c/ohfy__Mapping_Key__c/type_lager",
            "body": {
                "Name": "Lager",
                "ohfy__Active__c": true
            }
        },

        // Step 4: Upsert Product (reference brand and type)
        {
            "referenceId": "item1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/shopify_98765",
            "body": {
                "Name": "Premium Lager 12pk",
                "ohfy__Item_Number__c": "SKU-001",
                "ohfy__Item_Line__c": "@{brand1.id}",
                "ohfy__Item_Type__c": "@{type1.id}",
                "ohfy__Base_Price__c": 12.99,
                "ohfy__Active__c": true
            }
        },

        // Step 5: Upsert Order (reference customer)
        {
            "referenceId": "order1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Order__c/ohfy__External_ID__c/shopify_order_1001",
            "body": {
                "ohfy__Account__c": "@{account1.id}",
                "ohfy__Order_Date__c": "2025-01-15",
                "ohfy__Status__c": "New",
                "ohfy__Notes__c": "Rush delivery"
            }
        },

        // Step 6: Upsert Order Item (reference order and product)
        {
            "referenceId": "orderitem1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Order_Item__c/ohfy__External_ID__c/shopify_orderitem_1001_1",
            "body": {
                "ohfy__Order__c": "@{order1.id}",
                "ohfy__Item__c": "@{item1.id}",
                "ohfy__Quantity__c": 12,
                "ohfy__Unit_Price__c": 12.99
            }
        }
    ]
}
```

---

## Master-Detail Relationships

### Order__c → Order_Item__c

**Relationship Type**: Master-Detail

**Rule**: Order__c must exist before creating Order_Item__c

```javascript
// CORRECT
[
    {
        "referenceId": "order1",
        "method": "POST",
        "url": ".../ohfy__Order__c",
        "body": { ... }
    },
    {
        "method": "POST",
        "url": ".../ohfy__Order_Item__c",
        "body": {
            "ohfy__Order__c": "@{order1.id}"  // Reference from previous step
        }
    }
]

// WRONG - will fail
[
    {
        "method": "POST",
        "url": ".../ohfy__Order_Item__c",
        "body": {
            "ohfy__Order__c": "unknownId"  // ERROR: parent doesn't exist
        }
    }
]
```

### Purchase_Order__c → Purchase_Order_Item__c

**Relationship Type**: Master-Detail

**Rule**: Purchase_Order__c must exist before creating Purchase_Order_Item__c

```javascript
// CORRECT order
[
    { "referenceId": "po1", "url": ".../ohfy__Purchase_Order__c", ... },
    { "body": { "ohfy__Purchase_Order__c": "@{po1.id}" }, ... }
]
```

---

## Lookup Relationships

### Order__c → Account

**Relationship Type**: Lookup (not Master-Detail)

**Rule**: Account should exist first, but not strictly required

**Best Practice**: Always upsert Account before Order__c

```javascript
// RECOMMENDED
[
    {
        "referenceId": "account1",
        "method": "PATCH",
        "url": ".../Account/ohfy__External_ID__c/shopify_12345",
        "body": { "Name": "Customer" }
    },
    {
        "method": "PATCH",
        "url": ".../ohfy__Order__c/ohfy__External_ID__c/order_1001",
        "body": {
            "ohfy__Account__c": "@{account1.id}"
        }
    }
]
```

### Item__c → Item_Line__c, Item_Type__c

**Relationship Type**: Lookup

**Rule**: Item_Line__c and Item_Type__c should exist before Item__c

```javascript
// RECOMMENDED
[
    { "referenceId": "brand1", "url": ".../ohfy__Item_Line__c/...", ... },
    { "referenceId": "type1", "url": ".../ohfy__Item_Type__c/...", ... },
    {
        "url": ".../ohfy__Item__c/...",
        "body": {
            "ohfy__Item_Line__c": "@{brand1.id}",
            "ohfy__Item_Type__c": "@{type1.id}"
        }
    }
]
```

---

## Reference Syntax

### Cross-Reference Between Requests

Use `@{referenceId.field}` to reference previous request results:

```javascript
[
    {
        "referenceId": "account1",  // Define reference ID
        "method": "POST",
        "url": ".../Account",
        "body": { "Name": "ABC Corp" }
    },
    {
        "method": "POST",
        "url": ".../ohfy__Order__c",
        "body": {
            "ohfy__Account__c": "@{account1.id}"  // Reference previous result
        }
    }
]
```

### Available Reference Fields

After successful operation, you can reference:
- `@{refId.id}` - Salesforce record ID
- `@{refId.success}` - Boolean success flag
- `@{refId.errors}` - Array of errors (if any)

**Most common**: `@{refId.id}` for relationship fields

---

## Error Handling

### allOrNone: false

**Recommended**: Use `"allOrNone": false` to continue processing even if one request fails

```javascript
{
    "allOrNone": false,  // Continue on error
    "compositeRequest": [ ... ]
}
```

**Behavior**:
- Failed requests return error in response
- Successful requests proceed
- Later requests can still reference successful earlier requests

### allOrNone: true

**Use cautiously**: All requests rollback if any fails

```javascript
{
    "allOrNone": true,  // Rollback all on error
    "compositeRequest": [ ... ]
}
```

**Behavior**:
- If ANY request fails, ALL requests rollback
- Atomic transaction guarantee
- Slower performance

---

## Common Patterns

### Pattern 1: Upsert Parent, Insert Child

```javascript
[
    // Upsert order (may exist)
    {
        "referenceId": "order1",
        "method": "PATCH",
        "url": ".../ohfy__Order__c/ohfy__External_ID__c/order_1001",
        "body": { ... }
    },
    // Always insert new order item
    {
        "method": "POST",
        "url": ".../ohfy__Order_Item__c",
        "body": {
            "ohfy__Order__c": "@{order1.id}"
        }
    }
]
```

### Pattern 2: Upsert All via External IDs

```javascript
[
    {
        "referenceId": "order1",
        "method": "PATCH",
        "url": ".../ohfy__Order__c/ohfy__External_ID__c/order_1001",
        "body": { ... }
    },
    {
        "method": "PATCH",
        "url": ".../ohfy__Order_Item__c/ohfy__External_ID__c/orderitem_1001_1",
        "body": {
            "ohfy__Order__c": "@{order1.id}"
        }
    }
]
```

### Pattern 3: Conditional Create

```javascript
// Query first to check existence
const existingOrder = await sf.query({
    query: "SELECT Id FROM ohfy__Order__c WHERE ohfy__External_ID__c = 'order_1001'"
});

if (existingOrder.length > 0) {
    // Update existing
    compositeRequest[0].method = "PATCH";
    compositeRequest[0].url = `.../ohfy__Order__c/${existingOrder[0].Id}`;
} else {
    // Create new
    compositeRequest[0].method = "POST";
    compositeRequest[0].url = ".../ohfy__Order__c";
}
```

---

## Performance Considerations

### Batch Size

Salesforce composite requests support up to **25 subrequests** per call.

**For large datasets**:
```javascript
// Batch into groups of 25
const batches = [];
for (let i = 0; i < requests.length; i += 25) {
    batches.push(requests.slice(i, i + 25));
}

// Execute batches sequentially
for (const batch of batches) {
    await sf.composite({ compositeRequest: batch });
}
```

### Minimize Dependencies

**Faster**: Independent requests (can execute in parallel)
```javascript
[
    { "url": ".../Account/ohfy__External_ID__c/cust1", ... },  // Independent
    { "url": ".../Account/ohfy__External_ID__c/cust2", ... },  // Independent
    { "url": ".../Account/ohfy__External_ID__c/cust3", ... }   // Independent
]
```

**Slower**: Dependent requests (must execute sequentially)
```javascript
[
    { "referenceId": "order1", "url": ".../ohfy__Order__c", ... },
    { "body": { "ohfy__Order__c": "@{order1.id}" }, ... }  // Depends on order1
]
```

---

## Troubleshooting

### "Cannot insert Order_Item__c: Order__c does not exist"

**Cause**: Attempting to create child before parent

**Fix**: Reorder requests - parent first, then child

### "INVALID_CROSS_REFERENCE_KEY"

**Cause**: Referenced record doesn't exist or reference syntax is wrong

**Fix**:
1. Verify `referenceId` matches between requests
2. Ensure parent request succeeded
3. Check reference syntax: `@{refId.id}`

### "Composite Request Failed"

**Cause**: One or more subrequests failed

**Fix**:
1. Check `compositeResponse` array for errors
2. Inspect `httpStatusCode` and `body` for each subrequest
3. Fix failing requests and retry

---

## See Also

- `core-objects.md` - Object relationships
- `external-id-patterns.md` - External ID format and upsert patterns
- `../triggers/common-errors.md` - Relationship validation errors
- `../../.claude/rules/salesforce-api.md` - Salesforce API standards
