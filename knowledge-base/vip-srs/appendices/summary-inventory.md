# Summary Inventory File (ISV Spec Appendix G)

## Overview

The Summary Inventory file is a monthly aggregated view derived from the daily Inventory (INV) transaction file. It provides beginning/ending on-hand plus all movement categories for the month.

## File Structure

Same header/detail/footer pattern as all VIP files.

## File Creation

Built from daily INV data. Includes monthly summaries of all transaction codes.

## Ability to Create for Past Periods

Yes, historical summary inventory can be generated.

## Timing and Inventory Backup

Summary is typically available after month-end close. For mid-month snapshots, use the daily INV file's TransCode 10 (Ending Inventory).

## File Naming

Uses INV prefix with summary-specific suffix.

## Quantity and Signs

All quantities are expressed as positive numbers. The transaction code determines the direction (addition vs subtraction).

## Relationship to Daily INV

The summary aggregates daily detail (codes 20-41, 99) into monthly totals (codes 50-59). If you process daily detail, do NOT also process monthly summary — this would double-count.
