# Core Objects

## Overview

The core objects represent the primary business entities in OHFY-Core: customers (Account), products (Item__c), orders (Order__c), and order details (Order_Item__c).

---

## Account (Customer)

**Purpose**: Customer/vendor accounts

**API Name**: `Account` (standard object with custom fields)

**Fields**: 183 total (standard + custom)

**Key External IDs**:
- `ohfy__External_ID__c` - Cross-system identifier (format: `{service}_{identifier}`) — **managed package field, requires `ohfy__` namespace**
- `Mapping_Key__c` - Legacy mapping identifier
- `EFT_Customer_ID__c` - EFT payment system ID

**Critical Fields**:
- `Name` - Account name
- `Account_Number__c` - Business account number
- `Type` - Customer, Vendor, Distributor, etc.
- `Status__c` - Active, Inactive, Suspended
- `ohfy__Market__c` - Market/channel classification (**restricted picklist** — values vary by org, e.g., Grocery Store, Liquor, Convenience, Bars/Clubs/Taverns, Restaurants)
- `ohfy__Premise_Type__c` - On Premise, Off Premise (**restricted picklist**)
- `ohfy__Retail_Type__c` - Chain, Independent, Distributor (**restricted picklist**)
- `Payment_Terms__c` - NET30, COD, etc.
- `Credit_Limit__c` - Maximum credit allowed
- `Tax_Exempt__c` - Tax exemption status
- `Delivery_Instructions__c` - Special delivery notes

**Relationships**:
```
Account
  ├── Order__c (1:M) - Customer orders
  ├── Payment__c (1:M) - Customer payments
  ├── Account_Item__c (1:M) - Account-specific items
  ├── Route__c (1:M) - Delivery routes
  └── Account_Goal__c (1:M) - Sales goals
```

**Integration Pattern**:
```javascript
// Upsert via ohfy__External_ID__c (managed package field — requires ohfy__ namespace)
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/Account/ohfy__External_ID__c/shopify_12345",
    "body": {
        "Name": "ABC Distributing",
        "Phone": "555-1234",
        "BillingStreet": "123 Main St",
        "Type": "Customer"
    }
}
```

---

## Item__c (Product)

**Purpose**: Products/inventory items

**API Name**: `ohfy__Item__c`

**Fields**: 135 total

**Key External IDs**:
- `External_ID__c` - Cross-system identifier (format: `{service}_{identifier}`)
- `Mapping_Key__c` - Legacy mapping identifier
- `GPA_External_ID__c` - GP Analytics PDCN
- `VIP_External_ID__c` - VIP SRS item code

**Critical Fields**:
- `Name` - Item name/description
- `Item_Number__c` - SKU/product code
- `Active__c` - Boolean (cannot deactivate with inventory > 0)
- `Item_Line__c` - Brand/product line (lookup)
- `Item_Type__c` - Category/type (lookup)
- `Unit_of_Measure__c` - EA, CS, PK, etc.
- `Base_Price__c` - Default price
- `Cost__c` - Item cost
- `Taxable__c` - Boolean
- `Track_Inventory__c` - Boolean
- `Track_Lots__c` - Boolean (lot/serial tracking)

**Relationships**:
```
Item__c
  ├── Item_Line__c (M:1) - Brand/product line
  ├── Item_Type__c (M:1) - Category
  ├── Inventory__c (1:M) - Inventory per location
  ├── Pricelist_Item__c (1:M) - Prices per pricelist
  ├── Order_Item__c (1:M) - Order line items
  └── Lot__c (1:M) - Lot numbers
```

**Record Types**:
- `Finished_Good` - Finished Good (required for VIP items — gates `Type__c` and `Packaging_Type__c` picklist values)
- `Keg_Shell` - Keg Shell
- `Merchandise` - Merchandise
- `Packaging` - Packaging
- `Raw_Material` - Raw Material

> **Note:** `ohfy__Packaging_Type__c` is a restricted picklist gated by record type. The integration user must have the target record type assigned, and the Composite body must include `RecordTypeId`. Without it, the default Master record type rejects valid picklist values.

**Triggers**:
- `TA_Item_AI_InventoryCreator` - Auto-creates Inventory__c for each Location__c
- `TA_Item_AI_PricelistItemCreator` - Auto-creates Pricelist_Item__c for each Pricelist__c
- `TA_Item_BU_StatusChecker` - Prevents deactivation with inventory

**Integration Pattern**:
```javascript
// Upsert via External_ID__c
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Item__c/ohfy__External_ID__c/shopify_98765",
    "body": {
        "Name": "Premium Lager 12pk",
        "ohfy__Item_Number__c": "SKU-001",
        "ohfy__Base_Price__c": 12.99,
        "ohfy__Unit_of_Measure__c": "CS",
        "ohfy__Active__c": true
    }
}
```

**Bypass Auto-Creation**:
```apex
// Bypass auto-creation during bulk import
MetadataTriggerHandler.bypass('TA_Item_AI_InventoryCreator');
MetadataTriggerHandler.bypass('TA_Item_AI_PricelistItemCreator');
try {
    insert items;
} finally {
    MetadataTriggerHandler.clearAllBypasses();
}
```

---

## Item_Line__c (Brand/Product Line)

**Purpose**: Product brands or lines

**API Name**: `ohfy__Item_Line__c`

**Key External IDs**:
- `Mapping_Key__c` - Legacy mapping identifier

**Critical Fields**:
- `Name` - Brand/line name
- `Active__c` - Boolean
- `Vendor__c` - Vendor (lookup)

**Integration Pattern**:
```javascript
// Upsert via Mapping_Key__c
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Item_Line__c/ohfy__Mapping_Key__c/brand_abc",
    "body": {
        "Name": "ABC Brewery",
        "ohfy__Active__c": true
    }
}
```

---

## Item_Type__c (Category)

**Purpose**: Product categories/types

**API Name**: `ohfy__Item_Type__c`

**Key External IDs**:
- `Mapping_Key__c` - Legacy mapping identifier

**Critical Fields**:
- `Name` - Type/category name
- `Active__c` - Boolean

**Integration Pattern**:
```javascript
// Upsert via Mapping_Key__c
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Item_Type__c/ohfy__Mapping_Key__c/type_lager",
    "body": {
        "Name": "Lager",
        "ohfy__Active__c": true
    }
}
```

---

## Order__c (Invoice)

**Purpose**: Customer orders/invoices

**API Name**: `ohfy__Order__c`

**Fields**: 116 total

**Key External IDs**:
- `External_ID__c` - Cross-system identifier (format: `{service}_{identifier}`)

**Critical Fields**:
- `Name` - Order number (auto-generated by trigger)
- `Account__c` - Customer (lookup to Account, **REQUIRED**)
- `Status__c` - New, Picking, Loaded, Out For Delivery, Delivered, Complete, Cancelled
- `Order_Date__c` - Order date
- `Delivery_Date__c` - Scheduled delivery
- `Delivery__c` - Delivery route (lookup)
- `Total_Amount__c` - Order total (calculated)
- `Payment_Method__c` - Cash, Check, Credit Card, etc.
- `Notes__c` - Order notes

**Relationships**:
```
Order__c
  ├── Account (M:1) - Customer [REQUIRED]
  ├── Delivery__c (M:1) - Delivery route
  ├── Order_Item__c (1:M) - Order line items [Master-Detail]
  ├── Payment__c (1:M) - Payments
  └── Allocation__c (1:M) - Inventory allocations
```

**Status Progression** (validated by `TA_Invoice_BU_StatusUpdater`):
```
New → Scheduled → In Progress → Picking → Loaded →
Out For Delivery → Delivered → Complete
                              ↓
                         Cancelled
```

**Triggers**:
- `TA_Invoice_BU_StatusUpdater` - Validates status can only move forward
- `TA_Invoice_AU_Completer` - Completion logic
- `TA_Invoice_AU_Canceller` - Cancellation logic
- `TA_Order_AI_DeliveryAssociator` - Auto-associates delivery route

**Integration Pattern**:
```javascript
// Create order with upsert
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Order__c/ohfy__External_ID__c/shopify_order_1001",
    "referenceId": "order1",
    "body": {
        "ohfy__Account__c": "@{account1.id}",
        "ohfy__Order_Date__c": "2025-01-15",
        "ohfy__Status__c": "New",
        "ohfy__Notes__c": "Rush delivery"
    }
}
```

**Bypass Status Validation**:
```apex
// Allow non-sequential status changes
U_OrderStatusValidationBypass.isBypassEnabled = true;
try {
    order.Status__c = 'Complete';
    update order;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
}
```

---

## Order_Item__c (Invoice Item)

**Purpose**: Order line items

**API Name**: `ohfy__Order_Item__c`

**Fields**: 91 total

**Key External IDs**:
- `External_ID__c` - Cross-system identifier (format: `{service}_{identifier}`)

**Critical Fields**:
- `Order__c` - Parent order (Master-Detail, **REQUIRED**)
- `Item__c` - Product (lookup, **REQUIRED**)
- `Quantity__c` - Quantity ordered
- `Unit_Price__c` - Price per unit
- `Discount__c` - Discount amount
- `Total_Price__c` - Line total (calculated)
- `Status__c` - New, Allocated, Picked, Loaded, Delivered

**Relationships**:
```
Order_Item__c
  ├── Order__c (M:1) - Parent order [Master-Detail, REQUIRED]
  ├── Item__c (M:1) - Product [REQUIRED]
  └── Lot_Invoice_Item__c (1:M) - Lot assignments
```

**Triggers**:
- `TA_OrderItem_BI_DuplicateChecker` - Prevents duplicate Item__c per Order__c
- `TA_InvoiceItem_BD_AdjDeleter` - Deletes adjustments on delete

**Integration Pattern**:
```javascript
// Create order item (must reference existing Order__c)
{
    "method": "PATCH",
    "url": "/services/data/v62.0/sobjects/ohfy__Order_Item__c/ohfy__External_ID__c/shopify_item_001",
    "body": {
        "ohfy__Order__c": "@{order1.id}",  // Reference from composite request
        "ohfy__Item__c": "@{item1.id}",
        "ohfy__Quantity__c": 12,
        "ohfy__Unit_Price__c": 12.99
    }
}
```

**Avoid Duplicate Item Error**:
```javascript
// Deduplicate before insert
const itemMap = new Map();
orderItems.forEach(item => {
    const key = item.Item__c;
    if (itemMap.has(key)) {
        // Combine quantities
        itemMap.get(key).Quantity__c += item.Quantity__c;
    } else {
        itemMap.set(key, item);
    }
});
const deduplicatedItems = Array.from(itemMap.values());
```

---

## Integration_Sync__c (Sync Tracking)

**Purpose**: Track integration synchronization status

**API Name**: `ohfy__Integration_Sync__c`

**Key Fields**:
- `Name` - Auto-number (SYNC-0001)
- `Object_Type__c` - Object being synced (Order, Item, etc.)
- `External_System__c` - Source system (Shopify, WooCommerce, etc.)
- `External_ID__c` - External system ID
- `Sync_Status__c` - Pending, Success, Failed
- `Error_Message__c` - Error details
- `Last_Sync_Date__c` - Last sync timestamp

**Integration Pattern**:
```javascript
// Create sync record
{
    "method": "POST",
    "url": "/services/data/v62.0/sobjects/ohfy__Integration_Sync__c",
    "body": {
        "ohfy__Object_Type__c": "Order",
        "ohfy__External_System__c": "Shopify",
        "ohfy__External_ID__c": "shopify_order_1001",
        "ohfy__Sync_Status__c": "Success",
        "ohfy__Last_Sync_Date__c": "2025-01-15T10:30:00Z"
    }
}
```

---

## External_ID__c (ID Mapping)

**Purpose**: Cross-reference external system IDs

**API Name**: `ohfy__External_ID__c`

**Key Fields**:
- `Name` - Auto-number
- `External_System__c` - Source system
- `External_Value__c` - External ID value
- `OHFY_Object__c` - OHFY object type
- `OHFY_Record_ID__c` - Salesforce record ID

**Integration Pattern**:
```javascript
// Create mapping record
{
    "method": "POST",
    "url": "/services/data/v62.0/sobjects/ohfy__External_ID__c",
    "body": {
        "ohfy__External_System__c": "Shopify",
        "ohfy__External_Value__c": "shopify_12345",
        "ohfy__OHFY_Object__c": "Item__c",
        "ohfy__OHFY_Record_ID__c": "a0Y3i000000AbC1"
    }
}
```

---

## Object Naming Conventions

All OHFY custom objects use the `ohfy__` namespace prefix:
- `ohfy__Item__c`
- `ohfy__Order__c`
- `ohfy__Order_Item__c`
- `ohfy__Inventory__c`
- etc.

Standard Salesforce objects (Account, Contact) do NOT have the namespace prefix.

---

## See Also

- `inventory-objects.md` - Inventory and location objects
- `purchasing-objects.md` - Purchase orders and vendor objects
- `external-id-patterns.md` - External ID format patterns
- `composite-request-order.md` - Operation sequencing for composite requests
- `../field-mappings/` - Complete field lists for each object
