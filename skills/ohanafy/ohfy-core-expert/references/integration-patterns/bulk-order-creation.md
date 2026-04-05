# Bulk Order Creation

## Overview

Patterns for efficiently creating orders with items in bulk while avoiding trigger issues and maintaining data integrity.

---

## Pattern 1: Upsert Everything (Recommended)

Use PATCH with External_ID for all records - safest for integrations.

```javascript
{
    "allOrNone": false,
    "compositeRequest": [
        // Upsert customer
        {
            "referenceId": "account1",
            "method": "PATCH",
            "url": "/services/data/v58.0/sobjects/Account/External_ID__c/shopify_12345",
            "body": {
                "Name": "ABC Distributing",
                "Type": "Customer"
            }
        },
        // Upsert items
        {
            "referenceId": "item1",
            "method": "PATCH",
            "url": "/services/data/v58.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/shopify_98765",
            "body": {
                "Name": "Premium Lager 12pk",
                "ohfy__Base_Price__c": 12.99
            }
        },
        // Upsert order
        {
            "referenceId": "order1",
            "method": "PATCH",
            "url": "/services/data/v58.0/sobjects/ohfy__Order__c/ohfy__External_ID__c/shopify_order_1001",
            "body": {
                "ohfy__Account__c": "@{account1.id}",
                "ohfy__Order_Date__c": "2025-01-15",
                "ohfy__Status__c": "New"
            }
        },
        // Upsert order item
        {
            "referenceId": "orderitem1",
            "method": "PATCH",
            "url": "/services/data/v58.0/sobjects/ohfy__Order_Item__c/ohfy__External_ID__c/shopify_orderitem_1001_1",
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

**Benefits**:
- Handles both new and existing records
- No duplicate errors
- Idempotent (can retry safely)

---

## Pattern 2: Bypass Triggers for Performance

For large bulk loads, bypass non-critical triggers.

```apex
// Bypass auto-creation and notification triggers
MetadataTriggerHandler.bypass('TA_Order_AI_DeliveryAssociator');
MetadataTriggerHandler.bypass('TA_Order_AU_GoalUpdater');
MetadataTriggerHandler.bypass('TA_Invoice_AU_SendEmail');
U_OrderStatusValidationBypass.isBypassEnabled = true;

try {
    // Bulk insert orders
    insert orderList;

    // Bulk insert order items
    insert orderItemList;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
    MetadataTriggerHandler.clearAllBypasses();
}
```

**Benefits**:
- Faster execution
- Avoid unnecessary trigger logic
- Suitable for historical data loads

**Risks**:
- Missing business logic
- No email notifications
- No goal tracking
- No delivery association

---

## Pattern 3: Batch Processing

Split large datasets into batches of 25 (Salesforce composite limit).

```javascript
// Split into batches
const batchSize = 25;
const batches = [];

for (let i = 0; i < compositeRequests.length; i += batchSize) {
    batches.push(compositeRequests.slice(i, i + batchSize));
}

// Process batches sequentially
for (const batch of batches) {
    const response = await sf.composite({
        allOrNone: false,
        compositeRequest: batch
    });

    // Log errors
    response.compositeResponse.forEach((result, index) => {
        if (result.httpStatusCode !== 200 && result.httpStatusCode !== 201) {
            console.error(`Request ${index} failed:`, result.body);
        }
    });
}
```

---

## Pattern 4: Deduplicate Order Items

Prevent duplicate item errors by combining quantities.

```javascript
// Deduplicate order items by Item__c
const itemMap = new Map();

orderItems.forEach(item => {
    const key = item.ohfy__Item__c;

    if (itemMap.has(key)) {
        // Combine quantities
        itemMap.get(key).ohfy__Quantity__c += item.ohfy__Quantity__c;
    } else {
        itemMap.set(key, item);
    }
});

const deduplicatedItems = Array.from(itemMap.values());
```

---

## Pattern 5: Error Handling

Handle errors gracefully and retry failed requests.

```javascript
const failedRequests = [];

response.compositeResponse.forEach((result, index) => {
    if (result.httpStatusCode >= 400) {
        failedRequests.push({
            index,
            request: compositeRequests[index],
            error: result.body
        });
    }
});

// Retry failed requests
if (failedRequests.length > 0) {
    console.log(`Retrying ${failedRequests.length} failed requests...`);

    const retryRequests = failedRequests.map(f => f.request);
    const retryResponse = await sf.composite({
        allOrNone: false,
        compositeRequest: retryRequests
    });
}
```

---

## Complete Example: Shopify Order Sync

```javascript
async function syncShopifyOrders(shopifyOrders) {
    const compositeRequests = [];

    shopifyOrders.forEach(shopifyOrder => {
        // Customer
        compositeRequests.push({
            referenceId: `account_${shopifyOrder.customer.id}`,
            method: "PATCH",
            url: `/services/data/v58.0/sobjects/Account/External_ID__c/shopify_${shopifyOrder.customer.id}`,
            body: {
                Name: shopifyOrder.customer.name,
                Phone: shopifyOrder.customer.phone,
                BillingStreet: shopifyOrder.billing_address.address1,
                Type: "Customer"
            }
        });

        // Items
        shopifyOrder.line_items.forEach(lineItem => {
            compositeRequests.push({
                referenceId: `item_${lineItem.variant_id}`,
                method: "PATCH",
                url: `/services/data/v58.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/shopify_${lineItem.variant_id}`,
                body: {
                    Name: lineItem.name,
                    ohfy__Item_Number__c: lineItem.sku,
                    ohfy__Base_Price__c: parseFloat(lineItem.price)
                }
            });
        });

        // Order
        compositeRequests.push({
            referenceId: `order_${shopifyOrder.id}`,
            method: "PATCH",
            url: `/services/data/v58.0/sobjects/ohfy__Order__c/ohfy__External_ID__c/shopify_order_${shopifyOrder.id}`,
            body: {
                ohfy__Account__c: `@{account_${shopifyOrder.customer.id}.id}`,
                ohfy__Order_Date__c: shopifyOrder.created_at,
                ohfy__Status__c: "New",
                ohfy__Notes__c: shopifyOrder.note
            }
        });

        // Order Items
        shopifyOrder.line_items.forEach((lineItem, index) => {
            compositeRequests.push({
                referenceId: `orderitem_${shopifyOrder.id}_${index}`,
                method: "PATCH",
                url: `/services/data/v58.0/sobjects/ohfy__Order_Item__c/ohfy__External_ID__c/shopify_orderitem_${shopifyOrder.id}_${index}`,
                body: {
                    ohfy__Order__c: `@{order_${shopifyOrder.id}.id}`,
                    ohfy__Item__c: `@{item_${lineItem.variant_id}.id}`,
                    ohfy__Quantity__c: lineItem.quantity,
                    ohfy__Unit_Price__c: parseFloat(lineItem.price)
                }
            });
        });
    });

    // Batch into groups of 25
    const batches = [];
    for (let i = 0; i < compositeRequests.length; i += 25) {
        batches.push(compositeRequests.slice(i, i + 25));
    }

    // Execute batches
    for (const batch of batches) {
        await sf.composite({ allOrNone: false, compositeRequest: batch });
    }
}
```

---

## See Also

- `../data-model/composite-request-order.md` - Operation sequencing
- `../triggers/bypass-patterns.md` - Trigger bypass details
- `safe-bypass-patterns.md` - Recommended bypass usage
