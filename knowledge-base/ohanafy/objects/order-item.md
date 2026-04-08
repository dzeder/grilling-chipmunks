# ohfy__Order_Item__c

Line items on an ohfy__Order__c. Each record represents one product (ohfy__Item__c) on an order with quantities, pricing, and fulfillment tracking.

## Quick facts

- **Namespace:** ohfy__
- **Field count:** ~144
- **Validation rules:** 0 (on this object; parent Order__c has 14)
- **Triggers:** None directly (parent InvoiceTrigger fires on Order__c)

## Draft tracking

**`ohfy__Is_Draft__c`** (boolean) — indicates the line item is in draft state.

> **Gotcha:** There is NO `ohfy__Status__c` field on Order_Item__c. Draft state is tracked via the boolean `ohfy__Is_Draft__c`, not a picklist. The parent `ohfy__Order__r.ohfy__Status__c` controls the order-level status.

- `true` → 55 records (across 5.2M+ total)
- `false` → 5,267,554 records

**Draft items on non-draft orders:** 40 records found where `Is_Draft__c = true` but parent order is not Draft. This may indicate items added to an existing order that haven't been finalized.

## Quantity fields

Order_Item tracks quantities through the fulfillment lifecycle:

| Field | Purpose |
|-------|---------|
| ohfy__Ordered_Quantity__c | Original quantity ordered |
| ohfy__Original_Order_Quantity__c | Snapshot of initial order (doesn't change) |
| ohfy__Picked_Quantity__c | Quantity picked in warehouse |
| ohfy__Loaded_Quantity__c | Quantity loaded on truck |
| ohfy__quantity_shipped__c | Quantity shipped (note: lowercase) |
| ohfy__Invoiced_Quantity__c | Quantity invoiced to customer |
| ohfy__Backorder_Quantity__c | Quantity backordered |
| ohfy__Outstanding_Quantity__c | Remaining quantity to fulfill |
| ohfy__Difference_Quantity__c | Delta between ordered and invoiced |
| ohfy__Retail_Quantity__c | Retail-facing quantity |

**Unit breakdowns:**
- ohfy__Case_Ordered_Quantity__c — cases ordered
- ohfy__Pallet_Ordered_Quantity__c — pallets ordered
- ohfy__Layer_Ordered_Quantity__c — layers ordered
- ohfy__Ind_Unit_Ordered_Quantity__c / ohfy__Ind_Unit_Invoiced_Quantity__c — individual units

> **Gotcha:** `ohfy__quantity_shipped__c` uses lowercase `quantity` — inconsistent with the rest of the field naming convention. Easy to miss in SOQL.

## Pricing fields

| Field | Purpose |
|-------|---------|
| ohfy__Unit_Price__c | Price per case/unit |
| ohfy__Individual_Unit_Price__c | Price per individual unit |
| ohfy__Discounted_Unit_Price__c | Price after discounts |
| ohfy__Landed_Unit_Price__c | Price including freight/duties |
| ohfy__Landed_Individual_Unit_Price__c | Landed price per individual unit |
| EDI_Frontline_Price_to_Retail__c | EDI retail price (non-namespaced) |

## Key relationships

| Field | Target | Purpose |
|-------|--------|---------|
| ohfy__Order__c | ohfy__Order__c | Parent order (master-detail) |
| ohfy__Item__c | ohfy__Item__c | Product being ordered |
| ohfy__Item_Type__c | ohfy__Item_Type__c | Product category |
| ohfy__Delivery__c | ohfy__Delivery__c | Delivery assignment |
| ohfy__Lot__c | ohfy__Lot__c | Inventory lot (for lot-tracked items) |
| ohfy__Allocation__c | ohfy__Allocation__c | Inventory allocation |
| ohfy__Order_Item__c | ohfy__Order_Item__c | Self-reference (linked items) |

## Item denormalization

Several Item__c fields are denormalized onto Order_Item__c for performance:

- ohfy__Item_Name__c, ohfy__Item_Short_Name__c
- ohfy__Item_Number__c, ohfy__Item_SKU__c
- ohfy__Item_Case_UPC__c
- ohfy__Item_Units_Per_Case__c, ohfy__Item_Weight__c
- ohfy__Item_Keg_Deposit__c
- ohfy__Item_Quantity_Available__c, ohfy__Item_Quantity_On_Hand__c

These are likely formula or roll-up fields pulling from the parent Item__c. Useful for reporting without joins.

## External IDs

- ohfy__External_Order_ID__c — links back to external order system
- ohfy__External_Item_ID__c — links back to external item system
- ohfy__Ohanafy_Purchase_Order_Item_ID__c — cross-reference to PO items
- ohfy__QuickBooks_Item_ID__c / ohfy__QuickBooks_Item_ID_Company_2__c — QuickBooks integration

## Gotchas

- **No status picklist** — use `ohfy__Is_Draft__c` for draft state, `ohfy__Order__r.ohfy__Status__c` for lifecycle state.
- **5.2M+ records** — high-volume object. Always use selective WHERE clauses. COUNT queries are fine but full table scans will timeout.
- **Lowercase field name** — `ohfy__quantity_shipped__c` breaks the CamelCase convention.
- **No triggers on this object** — business logic fires through the parent Order__c triggers or via Flows.
- **Multiple quantity fields** — know which one you need. `Ordered_Quantity__c` is what the customer asked for, `Invoiced_Quantity__c` is what they got, `Outstanding_Quantity__c` is the gap.
