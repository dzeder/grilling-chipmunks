# Zero Sales Records (ISV Spec Appendix F)

## Overview

VIP creates zero sales records in specific circumstances to ensure data completeness.

## When Zero Sales Records Are Created

- When a distributor reports no sales for a day but HAS reported outlets and inventory
- When a distributor's sales file has only control/placeholder records (SRS99/XXXXXX)
- To indicate "this distributor reported, but had zero sales today"

## Creating a Zero Sales Record

The record has Qty=0, NetPrice=0, with the standard header fields populated. AcctNbr is set to a placeholder. SupplierItem is set to a placeholder.

## Why This Matters

Without zero sales records, it's impossible to distinguish between "no sales reported" and "distributor didn't report at all." The Non-Reporters file (NON) covers the latter case.

## Integration Note

In the Ohanafy pipeline, zero sales records are filtered out during pre-processing (Qty=0 AND NetPrice=0 filter in SLSDA transform).
