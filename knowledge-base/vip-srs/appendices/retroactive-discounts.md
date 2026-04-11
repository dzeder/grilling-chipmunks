# Retroactive Discounts (ISV Spec Appendix J)

## Overview

Retroactive discounts are cumulative discounts applied after the initial sale, common in the beverage industry. Two options for reporting:

## Option 1 — Reverse & Rebill in Sales File

The original transaction is reversed (negative quantity/amount) and a new transaction is created with the discounted price. Both appear in the SLS file. This is the standard method.

## Option 2 — Retroactive Discount File Reporting

A separate file contains only the discount adjustments. This file is created infrequently (not daily). It includes the distributor discount ID linking back to the distributor's system, and the price support details.

## Discount Types

- Chain Quantity Discounts (CQD)
- Volume discounts
- Promotional discounts
- Depletion allowances

## Version 5.1 Additions

- **Distributor Discount ID field** — Links discounts to distributor's discount management system
- **Price Support field** — Distributor's calculated price support including on-invoice discount + depletion allowance + supplier offset

## Impact on Ohanafy

In the current pipeline, retroactive discounts appearing as reverse/rebill in SLSDA are processed normally (negative qty = return/credit). The separate Retroactive Discount file is NOT currently integrated.
