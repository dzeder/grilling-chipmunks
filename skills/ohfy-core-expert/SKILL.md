---
name: ohfy-core-expert
description: |
  Expert knowledge of the OHFY-Core Salesforce 2GP managed package. Apply when:
  - Generating Tray scripts that interact with Salesforce
  - Building composite requests for CRUD operations
  - Debugging API errors related to triggers/validations
  - Understanding object relationships and field mappings
  - Implementing bypass patterns for bulk operations
  - Mapping external system data to Salesforce fields
  Covers: 143 objects, 37 triggers, bypass patterns, status validations,
  external ID patterns, and common integration error resolutions.
---

# OHFY-Core Expert Skill

## Package Overview

- **Namespace**: `ohfy__`
- **Objects**: 143 custom objects
- **Triggers**: 37 (Metadata-Driven Framework)
- **API Version**: 58.0
- **Version**: v1.132.0.NEXT

This skill provides progressive disclosure of expert knowledge about the OHFY-Core Salesforce managed package to help prevent integration errors and optimize API interactions.

## Quick References

### Objects
See `references/data-model/` for complete object documentation:
- `core-objects.md` - Account, Order, Item, Order_Item
- `inventory-objects.md` - Location, Inventory, Lot, Allocation
- `purchasing-objects.md` - Purchase_Order, Vendor
- `external-id-patterns.md` - Cross-system ID mapping patterns
- `composite-request-order.md` - Master-detail operation sequencing

### Field Mappings
See `references/field-mappings/` for detailed field documentation:
- `item-fields.md` - All 135 Item__c fields
- `order-fields.md` - All 116 Order__c fields
- `account-fields.md` - All 183 Account fields
- `order-item-fields.md` - All 91 Order_Item__c fields

### Triggers & Bypass
See `references/triggers/` for trigger actions and bypass patterns:
- `trigger-framework.md` - Metadata-Driven Trigger Framework
- `bypass-patterns.md` - TriggerBase, MetadataTriggerHandler, validation bypass
- `order-triggers.md` - All Order__c trigger actions (19 actions)
- `item-triggers.md` - All Item__c trigger actions (9 actions)
- `inventory-triggers.md` - Inventory protection triggers (5 actions)
- `common-errors.md` - Error messages and solutions

### Validations
See `references/validations/` for validation rules:
- `status-transitions.md` - Valid status progressions
- `duplicate-checks.md` - Duplicate prevention rules
- `required-dependencies.md` - Data dependencies

### Integration Patterns
See `references/integration-patterns/` for safe bulk operation patterns:
- `bulk-order-creation.md` - Order/Item creation patterns
- `inventory-sync.md` - Inventory update patterns
- `safe-bypass-patterns.md` - Recommended bypass usage

## Critical Knowledge

### Status Validation (Order__c)
Invoice status must progress forward:
```
New (1) → Scheduled (1) → In Progress (1) → Picking (2) → Loaded (3) → Out For Delivery (4) → Delivered (5) → Complete (6)
                                                                                                              → Cancelled (7)
```

**Bypass**:
```apex
U_OrderStatusValidationBypass.isBypassEnabled = true;
invoiceRecord.Status__c = 'Loaded';
update invoiceRecord;
U_OrderStatusValidationBypass.isBypassEnabled = false;
```

### Negative Inventory Prevention
Inventory__c validates quantities cannot go negative.

**Error**: "You cannot remove more inventory than is available"

**Trigger**: `TA_Inventory_BU_PreventNegativeInventory` (BEFORE_UPDATE)

### Duplicate Order Items
Order_Item__c prevents duplicate items per order.

**Error**: "This item already exists in the order"

**Trigger**: `TA_OrderItem_BI_DuplicateChecker` (BEFORE_INSERT)

### External ID Pattern
Format: `{service}_{identifier}`

Examples:
- `shopify_12345678` - Shopify variant ID
- `gpa_1019#HRB` - GP Analytics PDCN
- `woo_4201` - WooCommerce product ID
- `ware2go_SKU001` - Ware2Go SKU
- `edi_PO-12345` - EDI purchase order number

### Master-Detail Operation Order
Parent records must exist before children in composite requests:

```
1. Account (upsert via External_ID__c)
2. Item_Line__c (upsert via Mapping_Key__c)
3. Item_Type__c (upsert via Mapping_Key__c)
4. Item__c (upsert via External_ID__c)
5. Order__c (upsert via External_ID__c, reference Account)
6. Order_Item__c (upsert via External_ID__c, reference Order__c and Item__c)
```

## When to Use This Skill

Claude should reference this skill when:

1. **Writing Tray scripts** that perform Salesforce CRUD operations
2. **Debugging integration errors** mentioning triggers or validations
3. **Building composite requests** with multiple related objects
4. **Needing to understand** which bypass pattern to use
5. **Mapping fields** from external systems to OHFY objects
6. **Handling status transitions** for Order__c records
7. **Creating External_ID values** for new integrations
8. **Preventing common errors** like negative inventory or duplicate items

## Common Integration Failures

| Failure Type | Cause | Solution Reference |
|--------------|-------|-------------------|
| Status progression violation | Skipping invoice statuses | `validations/status-transitions.md` |
| Duplicate order items | Adding same item twice | `triggers/order-triggers.md` |
| Negative inventory | Removing more than available | `triggers/inventory-triggers.md` |
| Missing delivery routes | Creating orders without routes | `triggers/bypass-patterns.md` |
| Deactivating items with inventory | Item has stock | `triggers/item-triggers.md` |
| UOM conversion missing | No Transformation_Setting__c | `triggers/item-triggers.md` |

## Reference Architecture

### Trigger Framework
- **Base**: Metadata-Driven Trigger Framework (Google pattern)
- **Custom Metadata**: `sObject_Trigger_Setting__mdt`, `Trigger_Action__mdt`
- **Bypass Mechanisms**: TriggerBase, MetadataTriggerHandler, validation utilities

### Object Relationships
```
Account (Customer)
  └── Order__c (Invoice) [M-D]
       └── Order_Item__c (Invoice Item) [M-D]
            └── Item__c (Product) [Lookup]
                 ├── Item_Line__c (Brand) [Lookup]
                 ├── Item_Type__c (Type) [Lookup]
                 └── Location__c (Warehouse) [Lookup]
                      └── Inventory__c (Stock) [Lookup]
```

### Integration Objects
- **External_ID__c** - Cross-system ID mapping (upsert via External_ID__c)
- **Integration_Sync__c** - Sync status tracking (auto-number)
- **Distributor_Placement__c** - GPA placements

## Progressive Disclosure Usage

1. **Start here** for overview and critical knowledge
2. **Navigate to references/** for detailed documentation as needed
3. **Use search** to find specific fields, triggers, or error messages
4. **Reference integration-patterns/** for safe bulk operation code

## Maintenance Notes

This skill is generated from OHFY-Core repository source code:
- Location: `/Users/derekhsquires/Documents/Ohanafy/github-repos/OHFY-Core`
- Source: `force-app/main/default/` (objects, classes, triggers)
- Update skill when OHFY-Core package version changes
