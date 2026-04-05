# Key Salesforce Automations

<!-- Seeded from OHFY-Core source index. Covers both Flows and Apex scheduled/batch operations. -->

## Scheduled Batch Operations (Apex)

These run on a schedule (typically nightly) and handle bulk data processing:

| Scheduler | Batch Class | What It Does |
|-----------|-------------|-------------|
| S_Update_AccountItems | BA_AccountItem_Updater | Update computed fields on Account Item records |
| S_Delivery_LockDeliveries | B_Delivery_LockDeliveries | Lock deliveries for tomorrow's date (prevent changes) |
| — | B_Delivery_StatusUpdater | Update delivery status based on daily rules |
| — | B_Route_DeliveryCreator | Auto-create delivery records for active routes |
| S_Update_DisplayItems | B_DisplayItem_Updater | Update computed fields on Display Items |
| — | B_Inventory_HistoryTracker | Create daily Inventory History snapshot records |
| — | B_Inventory_ValueCalculator | Calculate inventory values (also: BA_Inventory_ValueCalculator) |
| S_Invoice_LockInvoices | B_Invoice_LockInvoices | Lock picked invoices for tomorrow's date |
| S_Order_MetricUpdater | B_Order_MetricUpdater | Update order metrics from recently completed invoices |
| S_Pricelist_PricelistSetter | B_Pricelist_PricelistSetter | Set pricelists on start date for all related records |
| — | B_Pricelist_FrontLinePromotionSetter | Apply front-line promotional pricing |
| S_AccountItem_HistoryTracker | B_AccountItem_HistoryTracker | Track Account Item field changes over time |

## Key Object Automations

### Delivery Lifecycle
1. **Route → Delivery creation** (B_Route_DeliveryCreator): Auto-creates delivery records for active routes
2. **Delivery locking** (B_Delivery_LockDeliveries): Locks tomorrow's deliveries to prevent last-minute changes
3. **Status updates** (B_Delivery_StatusUpdater): Daily status transitions based on business rules

### Pricing Lifecycle
1. **Pricelist activation** (B_Pricelist_PricelistSetter): Activates pricelists on their start date
2. **Promotional pricing** (B_Pricelist_FrontLinePromotionSetter): Applies front-line promotions

### Inventory Tracking
1. **Daily snapshot** (B_Inventory_HistoryTracker): Records daily inventory levels for trending
2. **Value calculation** (B_Inventory_ValueCalculator): Computes inventory dollar values

### Order Metrics
1. **Invoice completion** (B_Order_MetricUpdater): Updates order metrics from completed invoices

## Trigger Handler Map

From OHFY-Core source index — triggers delegate to handler classes:

- Triggers follow the **single trigger per object** pattern
- All triggers use the **bypass mechanism** for data loads
- Handler classes contain the business logic (not the trigger itself)
- See `skills/ohanafy/ohfy-core-expert/references/source-index.md` for the full trigger → handler map

## Flows to Document

<!-- As Salesforce Flows are identified during customer implementations, document:
  - Name and API name
  - Trigger (record-triggered, screen, scheduled, etc.)
  - What it does in plain English
  - Objects and fields it touches
  - Known issues or limitations
-->
