# ohfy__Order__c

The central transactional object in Ohanafy. Represents sales orders, credit memos, transfers, and other order types across all SKUs.

## Quick facts

- **Namespace:** ohfy__
- **Field count:** ~260 (109 custom + standard)
- **Validation rules:** 14
- **Triggers:** InvoiceTrigger, OrderAutoCheckOut, OrderAutoCheckOutUpdate

## Status lifecycle

`ohfy__Status__c` — the primary order status picklist:

| Status | Meaning | Typical volume |
|--------|---------|----------------|
| Draft | Order created but not submitted | Low (~7 at any time) |
| New | Submitted, awaiting fulfillment | ~311 |
| Picking | Warehouse is picking items | ~6 |
| Loaded | Loaded on truck for delivery | ~200 |
| Out for Delivery | In transit to customer | ~3 |
| Delivered | Arrived at customer, pending completion | ~370 |
| Complete | Fully processed and closed | ~427K (vast majority) |
| Cancelled | Voided order | ~1,496 |

**Lifecycle:** Draft → New → Picking → Loaded → Out for Delivery → Delivered → Complete

**Cancellation:** Can be cancelled from most pre-Complete statuses.

## Payment status

`ohfy__Payment_Status__c` — tracks payment independently from fulfillment:

| Status | Meaning |
|--------|---------|
| Paid | Payment received in full |
| Not Paid | No payment received |
| Partially Paid | Some payment received |
| Processing | Payment in progress |
| Failed | Payment attempt failed |
| (null) | Legacy orders or payment not applicable |

## Subtypes

`ohfy__Subtypes__c` — multi-select picklist indicating product categories on the order. Values are `&`-delimited:

- Alcoholic, Non Alcoholic, Import, Wine, Cider, NA Beer, Red Bull, Cannabis, Overhead, Other

Orders commonly carry multiple subtypes (e.g., `Alcoholic&Import&NA Beer`). This drives tax calculations (wine tax flows) and regulatory reporting.

## Key relationships

| Field | Target | Cardinality | Purpose |
|-------|--------|-------------|---------|
| Account (standard) | Account | Lookup | Customer account |
| ohfy__Delivery__c | ohfy__Delivery__c | Lookup | Delivery assignment |
| ohfy__Fulfillment_Location__c | ohfy__Location__c | Lookup | Warehouse fulfilling the order |
| ohfy__Sales_Rep__c | User | Lookup | Assigned sales rep |
| ohfy__Payment_Account__c | Account | Lookup | Billing account (if different) |

## EDI fields

- `EDI_810_Status__c` — Invoice (810) EDI transmission status
- `EDI_857_Status__c` — Ship notice (857) EDI transmission status

These are custom (non-ohfy__ namespace) fields, likely added per-customer for EDI integration.

## Gotchas

- **109 custom fields** — this is the heaviest object in Ohanafy. Queries should select specific fields, never `SELECT *`.
- **14 validation rules** — bulk operations need bypass patterns. Check `ohfy-core-expert` for bypass mechanisms.
- **Status vs Payment Status** — these are independent lifecycles. An order can be `Complete` but `Not Paid`.
- **Subtypes is multi-select** — cannot use `=` in SOQL. Use `INCLUDES('Wine')` syntax.
- **ohfy__Draft_Credit_Invoice__c** — boolean flag for credit invoice drafts, separate from the main Status field.
- **Wine tax flows** — `Set_Wine_Tax_for_Invoices` and `Update_Wine_Tax_when_Invoice_is_Updated` fire on orders containing wine subtypes.
