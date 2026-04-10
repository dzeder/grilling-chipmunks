# External ID Patterns

## Overview

OHFY-Core uses a standardized External_ID__c pattern to enable upsert operations and cross-system ID mapping. This document defines the External_ID format and provides examples for common integrations.

---

## Standard Format

```
{service}_{identifier}
```

**Components**:
- `service` - Lowercase system name (shopify, gpa, ware2go, etc.)
- `_` - Underscore separator
- `identifier` - System-specific ID (alphanumeric, may include special chars)

---

## Common Service Prefixes

| Service | Prefix | Example |
|---------|--------|---------|
| Shopify | `shopify_` | `shopify_12345678` |
| WooCommerce | `woo_` | `woo_4201` |
| Ware2Go | `ware2go_` | `ware2go_SKU001` |
| GP Analytics | `gpa_` | `gpa_1019#HRB` |
| VIP SRS | colon-delimited prefix | `CHN:0000010305`, `ITM:102312102`, `ACT:FL01:00015` |
| EDI | `edi_` | `edi_PO-12345` |
| Square | `square_` | `square_ABCD1234` |
| QuickBooks | `qbo_` | `qbo_987654` |
| Magento | `magento_` | `magento_5678` |
| BigCommerce | `bigc_` | `bigc_9012` |

---

## Object-Specific Patterns

### Account (Customer)

**Field**: `ohfy__External_ID__c` (**managed package field — requires `ohfy__` namespace**)

**Examples**:
```
shopify_12345678        # Shopify customer ID
woo_cust_4201          # WooCommerce customer ID
qbo_987654             # QuickBooks customer ID
edi_ISA-QUAL-ID        # EDI trading partner ID
CHN:0000010305         # VIP SRS chain banner (colon-delimited prefix)
ACT:FL01:00015         # VIP SRS outlet account (dist:acctNum)
```

**Upsert**:
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/Account/ohfy__External_ID__c/shopify_12345678",
    "body": {
        "Name": "ABC Distributing"
    }
}
```

---

### Item__c (Product)

**Field**: `ohfy__External_ID__c`

**Examples**:
```
shopify_98765432        # Shopify variant ID
gpa_1019#HRB           # GP Analytics PDCN (includes # separator)
woo_4201               # WooCommerce product ID
ware2go_SKU001         # Ware2Go SKU
ITM:102312102          # VIP SRS item code (colon-delimited prefix)
edi_UPC-012345678901   # EDI UPC code
```

**Upsert**:
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/shopify_98765432",
    "body": {
        "Name": "Premium Lager 12pk",
        "ohfy__Item_Number__c": "SKU-001"
    }
}
```

---

### Item_Line__c (Brand)

**Field**: `ohfy__Mapping_Key__c`

**Examples**:
```
gpa_brand_abc          # GP Analytics brand
ILN:Shipyard IPA       # VIP SRS product line (colon-delimited prefix)
shopify_vendor_123     # Shopify vendor
```

**Upsert**:
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Item_Line__c/ohfy__Mapping_Key__c/gpa_brand_abc",
    "body": {
        "Name": "ABC Brewery"
    }
}
```

---

### Item_Type__c (Category)

**Field**: `ohfy__Mapping_Key__c`

**Examples**:
```
gpa_type_lager         # GP Analytics type
shopify_cat_beer       # Shopify category
woo_cat_123            # WooCommerce category ID
```

**Upsert**:
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Item_Type__c/ohfy__Mapping_Key__c/gpa_type_lager",
    "body": {
        "Name": "Lager"
    }
}
```

---

### Order__c (Invoice)

**Field**: `ohfy__External_ID__c`

**Examples**:
```
shopify_order_1001     # Shopify order number
woo_order_4201         # WooCommerce order ID
ware2go_SO-12345       # Ware2Go sales order
edi_850-PO12345        # EDI 850 purchase order
```

**Upsert**:
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Order__c/ohfy__External_ID__c/shopify_order_1001",
    "referenceId": "order1",
    "body": {
        "ohfy__Account__c": "@{account1.id}",
        "ohfy__Order_Date__c": "2025-01-15"
    }
}
```

---

### Order_Item__c (Invoice Item)

**Field**: `ohfy__External_ID__c`

**Examples**:
```
shopify_orderitem_1001_1   # Order + line number
woo_lineitem_4201_2        # WooCommerce line item ID
ware2go_SOL-12345-001      # Ware2Go SO line
edi_850-PO12345-LN001      # EDI line item
```

**Upsert**:
```javascript
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Order_Item__c/ohfy__External_ID__c/shopify_orderitem_1001_1",
    "body": {
        "ohfy__Order__c": "@{order1.id}",
        "ohfy__Item__c": "@{item1.id}",
        "ohfy__Quantity__c": 12
    }
}
```

---

## Special Characters in External IDs

### GP Analytics PDCN Format

GP Analytics uses `#` separator in PDCNs:
```
gpa_1019#HRB           # Valid
gpa_2045#ABC           # Valid
gpa_1234#XYZ-SPECIAL   # Valid with hyphen
```

**URL Encoding Required**:
```javascript
// CORRECT - URL encode the #
const externalId = "gpa_1019#HRB";
const encoded = encodeURIComponent(externalId); // "gpa_1019%23HRB"

const url = `/services/data/v62.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/${encoded}`;
```

### EDI Identifiers

EDI may include hyphens and other characters:
```
edi_PO-12345           # Purchase order with hyphen
edi_ISA-QUAL-ID        # ISA qualifier
edi_850-PO12345-LN001  # Document + PO + line
```

### Safe Characters

**Always safe** (no encoding needed):
- Letters: `a-z`, `A-Z`
- Numbers: `0-9`
- Underscore: `_`
- Hyphen: `-`

**Require URL encoding**:
- Hash: `#` → `%23`
- Space: ` ` → `%20`
- Slash: `/` → `%2F`
- Ampersand: `&` → `%26`

---

## Composite Request Patterns

### Create Order with Items

```javascript
{
    "allOrNone": false,
    "compositeRequest": [
        // 1. Upsert account
        {
            "referenceId": "account1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/Account/ohfy__External_ID__c/shopify_12345",
            "body": {
                "Name": "ABC Distributing"
            }
        },
        // 2. Upsert items
        {
            "referenceId": "item1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/shopify_98765",
            "body": {
                "Name": "Product A"
            }
        },
        // 3. Upsert order (reference account)
        {
            "referenceId": "order1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Order__c/ohfy__External_ID__c/shopify_order_1001",
            "body": {
                "ohfy__Account__c": "@{account1.id}",
                "ohfy__Order_Date__c": "2025-01-15"
            }
        },
        // 4. Upsert order items (reference order and item)
        {
            "referenceId": "orderitem1",
            "method": "PATCH",
            "url": "/services/data/v62.0/sobjects/ohfy__Order_Item__c/ohfy__External_ID__c/shopify_orderitem_1001_1",
            "body": {
                "ohfy__Order__c": "@{order1.id}",
                "ohfy__Item__c": "@{item1.id}",
                "ohfy__Quantity__c": 12
            }
        }
    ]
}
```

---

## External ID Field Mapping

### Objects with External_ID__c

| Object | API Name | External ID Field |
|--------|----------|------------------|
| Account | Account | ohfy__External_ID__c |
| Item__c | ohfy__Item__c | ohfy__External_ID__c |
| Order__c | ohfy__Order__c | ohfy__External_ID__c |
| Order_Item__c | ohfy__Order_Item__c | ohfy__External_ID__c |
| Inventory__c | ohfy__Inventory__c | - (use composite Item+Location) |

### Objects with Mapping_Key__c

| Object | API Name | External ID Field |
|--------|----------|------------------|
| Item_Line__c | ohfy__Item_Line__c | ohfy__Mapping_Key__c |
| Item_Type__c | ohfy__Item_Type__c | ohfy__Mapping_Key__c |

### Objects with Multiple External IDs

**Item__c** has multiple external ID options:
- `ohfy__External_ID__c` - Primary (recommended)
- `ohfy__Mapping_Key__c` - Legacy
- `ohfy__GPA_External_ID__c` - GP Analytics specific
- `ohfy__VIP_External_ID__c` - VIP SRS specific

**Account** has multiple external ID options:
- `ohfy__External_ID__c` - Primary (recommended) — **managed package field, requires `ohfy__` namespace**
- `Mapping_Key__c` - Legacy
- `EFT_Customer_ID__c` - EFT payment system

---

## Best Practices

### 1. Use Consistent Prefixes
```javascript
// CORRECT - consistent prefix
shopify_12345
shopify_order_1001
shopify_orderitem_1001_1

// WRONG - inconsistent
shopify_12345
Shopify_order_1001
SHOPIFY_item_1
```

### 2. URL Encode Special Characters
```javascript
// CORRECT
const externalId = "gpa_1019#HRB";
const encoded = encodeURIComponent(externalId);
const url = `.../ohfy__External_ID__c/${encoded}`;

// WRONG - will fail
const url = `.../ohfy__External_ID__c/gpa_1019#HRB`;
```

### 3. Handle Missing External IDs
```javascript
// Query to check if exists
const existing = await sf.query({
    query: `SELECT Id FROM ohfy__Item__c
            WHERE ohfy__External_ID__c = 'shopify_12345'`
});

if (existing.length > 0) {
    // Update existing via Id
    await sf.update({ Id: existing[0].Id, Name: "Updated" });
} else {
    // Create new with External_ID
    await sf.create({ ohfy__External_ID__c: "shopify_12345", Name: "New" });
}
```

### 4. Avoid Duplicate External IDs
External_ID__c is marked as unique - attempting to create duplicate will fail:
```
DUPLICATE_EXTERNAL_ID: External_ID__c already exists
```

Use PATCH (upsert) instead of POST (insert) to avoid this error.

---

## See Also

- `core-objects.md` - Object definitions
- `composite-request-order.md` - Operation sequencing
- `../../claude/rules/salesforce-api.md` - URL encoding rules
- `../triggers/common-errors.md` - Duplicate external ID errors
