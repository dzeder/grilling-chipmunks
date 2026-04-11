# Repack Logic (ISV Spec Appendix E)

## Overview

When a distributor repacks a supplier's product (e.g., breaks a case into individual bottles, creates variety packs), the repack flag indicates this in Sales, Inventory, and Cross-Reference files.

## Repack Flag Values

| Flag | Meaning |
|------|---------|
| Y | Repacked |
| N | Not repacked |
| A | Active/standard |
| C | Case Multiple |
| D | Repacked by distributor |
| M | Case Multiply |

## Logic for ALL Repack Items

When the REPACK flag indicates a repacked item, the system must recalculate net price. The net price is recalculated from the total sales based on the original case configuration.

## Impact on Sales

For repacked items in the SLS file, the quantity and UOM reflect the repacked configuration, not the original. Net price is adjusted accordingly.

## Impact on Inventory

Repacked items may have different units-per-case than the original item. The DIC file's SELUNIT and UNIT fields reflect the repacked configuration.

## Impact on Cross-Reference

The DIC file includes a DVRPACK field indicating the repack type for each distributor-item combination.

## Example

A 4/6-pack repack of a 24-unit case:

- **Original:** 1 case = 24 units
- **Repack:** 4 selling units (6-packs), each containing 6 units
- **SELUNIT=4, UNIT=24**
