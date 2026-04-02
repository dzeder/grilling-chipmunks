# Purchasing Objects

## Overview

Purchasing objects manage vendor relationships, purchase orders, and purchase order items for inventory replenishment.

---

## Vendor__c (Supplier)

**Purpose**: Vendor/supplier accounts

**API Name**: `ohfy__Vendor__c`

**Critical Fields**:
- `Name` - Vendor name
- `Vendor_Number__c` - Vendor code
- `Active__c` - Boolean
- `Payment_Terms__c` - NET30, NET60, etc.
- `Email__c` - Contact email
- `Phone__c` - Contact phone

**Relationships**:
```
Vendor__c
  ├── Purchase_Order__c (1:M) - Purchase orders
  └── Item_Line__c (1:M) - Product brands
```

**Integration Pattern**:
```javascript
{
    "method": "POST",
    "url": "/services/data/v58.0/sobjects/ohfy__Vendor__c",
    "body": {
        "Name": "ABC Distributors",
        "ohfy__Vendor_Number__c": "V-001",
        "ohfy__Active__c": true
    }
}
```

---

## Purchase_Order__c (PO)

**Purpose**: Purchase orders to vendors

**API Name**: `ohfy__Purchase_Order__c`

**Critical Fields**:
- `Name` - PO number (auto-generated)
- `Vendor__c` - Vendor (lookup, **REQUIRED**)
- `Status__c` - Draft, Submitted, Approved, Received, Complete, Cancelled
- `Order_Date__c` - Date ordered
- `Expected_Date__c` - Expected delivery
- `Total_Amount__c` - PO total (calculated)
- `Location__c` - Receiving location (lookup)

**Relationships**:
```
Purchase_Order__c
  ├── Vendor__c (M:1) - Vendor [REQUIRED]
  ├── Location__c (M:1) - Receiving location
  └── Purchase_Order_Item__c (1:M) - PO line items [Master-Detail]
```

**Status Progression**:
```
Draft → Submitted → Approved → Received → Complete
                              ↓
                         Cancelled
```

**Triggers**:
- `TA_PurchaseOrder_BU_Completer` - Completion logic
- `TA_PurchaseOrder_AU_Canceller` - Cancellation logic
- `TA_PurchaseOrder_BD_AdjRemover` - Delete adjustments on delete

**Integration Pattern**:
```javascript
{
    "method": "POST",
    "url": "/services/data/v58.0/sobjects/ohfy__Purchase_Order__c",
    "referenceId": "po1",
    "body": {
        "ohfy__Vendor__c": "vendorId",
        "ohfy__Order_Date__c": "2025-01-15",
        "ohfy__Status__c": "Draft",
        "ohfy__Location__c": "locationId"
    }
}
```

---

## Purchase_Order_Item__c (PO Line Item)

**Purpose**: Purchase order line items

**API Name**: `ohfy__Purchase_Order_Item__c`

**Critical Fields**:
- `Purchase_Order__c` - Parent PO (Master-Detail, **REQUIRED**)
- `Item__c` - Product (lookup, **REQUIRED**)
- `Quantity_Ordered__c` - Quantity ordered
- `Quantity_Received__c` - Quantity received
- `Unit_Cost__c` - Cost per unit
- `Total_Cost__c` - Line total (calculated)

**Relationships**:
```
Purchase_Order_Item__c
  ├── Purchase_Order__c (M:1) - Parent PO [Master-Detail, REQUIRED]
  └── Item__c (M:1) - Product [REQUIRED]
```

**Triggers**:
- `TA_POItem_BD_AdjRemover` - Delete adjustments on delete
- `TA_POItem_AU_AdjUpdater` - Update adjustment amounts

**Integration Pattern**:
```javascript
{
    "method": "POST",
    "url": "/services/data/v58.0/sobjects/ohfy__Purchase_Order_Item__c",
    "body": {
        "ohfy__Purchase_Order__c": "@{po1.id}",
        "ohfy__Item__c": "itemId",
        "ohfy__Quantity_Ordered__c": 100,
        "ohfy__Unit_Cost__c": 8.50
    }
}
```

---

## Receiving Workflow

### Step 1: Create Purchase Order
```javascript
// Create PO
{
    "compositeRequest": [
        {
            "referenceId": "po1",
            "method": "POST",
            "url": "/services/data/v58.0/sobjects/ohfy__Purchase_Order__c",
            "body": {
                "ohfy__Vendor__c": "vendorId",
                "ohfy__Status__c": "Draft",
                "ohfy__Location__c": "warehouse1"
            }
        }
    ]
}
```

### Step 2: Add Line Items
```javascript
// Add items to PO
{
    "compositeRequest": [
        {
            "method": "POST",
            "url": "/services/data/v58.0/sobjects/ohfy__Purchase_Order_Item__c",
            "body": {
                "ohfy__Purchase_Order__c": "poId",
                "ohfy__Item__c": "item1",
                "ohfy__Quantity_Ordered__c": 100,
                "ohfy__Unit_Cost__c": 8.50
            }
        }
    ]
}
```

### Step 3: Submit/Approve PO
```javascript
// Update status
{
    "Id": "poId",
    "ohfy__Status__c": "Submitted"
}
```

### Step 4: Receive Items
```javascript
// Update received quantities
{
    "Id": "poItemId",
    "ohfy__Quantity_Received__c": 95  // Received 95 of 100
}

// When all items received, update PO status
{
    "Id": "poId",
    "ohfy__Status__c": "Complete"
}
```

### Step 5: Update Inventory
```javascript
// Increase inventory at receiving location
{
    "Id": "inventoryId",
    "ohfy__Quantity__c": 195  // was 100, add 95 received
}
```

---

## See Also

- `core-objects.md` - Item__c and Account objects
- `inventory-objects.md` - Inventory management
- `../triggers/order-triggers.md` - Similar patterns for sales orders
