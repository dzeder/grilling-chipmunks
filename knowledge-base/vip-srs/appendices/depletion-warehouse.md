# Depletion Warehouse Reporting (ISV Spec Appendix H)

## Overview

Starting with Version 3.0, VIP requires reporting which warehouse a product is sourced from at the sales transaction level.

## The Problem

A distributor's retail sales are all sourced from the same warehouse when the distributor has one warehouse. But when a distributor has multiple warehouses (common after industry consolidation), a single retailer may be served by multiple warehouses, especially near warehouse borders.

## The Solution

The Sales file (SLS) includes a WarehouseID field (WhseId, position 25) that identifies the depletion warehouse for each transaction. This allows attribution of sales to the correct warehouse.

## Building Summary Inventory from Multiple Warehouses

1. Start with daily inventory transactions per warehouse
2. Combine with sales data attributed to each warehouse
3. Calculate daily on-hand by warehouse
4. Verify: Beginning On Hand + Receipts + Transfers In - Transfers Out - Returns - Breakage - Samples - Adjustments - Sales = Ending On Hand

If the above balances, all transactions, sales, and inventory have been correctly reported.

## Sales File Fields

- **ROWHSE** (in OUTDA) — The default warehouse for the outlet
- **WhseId** (in SLSDA) — The actual depletion warehouse per transaction

## Impact on Ohanafy

The Location__c object in Ohanafy maps to warehouse/distributor. When a distributor has multiple warehouses, each gets its own Location__c record. The WhseId in SLSDA determines which Location__c the depletion is attributed to.
