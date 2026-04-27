---
title: "UFF — Universal Flat File (MillerCoors 810 Invoice Format)"
last_updated: "2026-04-23"
relevant_skills: [ohfy-edi-expert, tray-expert, edi-processing-specialist]
---

# UFF — Universal Flat File

Fixed-width positional text format mandated by MillerCoors for distributor → retailer invoices. Routed via **OpenText/GXS** (OpenText acquired GXS; "GXS" still appears in field descriptions and filenames). OpenText translates UFF ↔ X12 810 for trading partners who prefer X12 — **UFF *is* the 810** from the distributor's perspective. No X12 generation happens on the Ohanafy side.

## Record types

One UFF document = one header + many details + one summary.

| Record | Prefix | Length | Purpose |
|---|---|---|---|
| Header | `10` | **1,207 chars** | Identification, invoice/shipping, distributor, outlet, customer, terms |
| Detail | `20` | **462 chars** (per line) | Line-item pricing, taxes, quantities, UPC/GTIN, product info |
| Summary | `30` | **198 chars** | Document totals — qty, weight, volume, taxes, charges, detail-line count |

Each record type is a separate line terminated with CRLF (`\r\n`). First two chars of every line must be the record-type code.

## Field-type encoding

| Type | Meaning | Example value | Example encoding |
|---|---|---|---|
| `A` | Alpha (left-align, space-pad) | `CHARLESTON` in 30 chars | `CHARLESTON                    ` |
| `N.0` | Numeric, 0 implied decimals (right-align, zero-pad) | `12345` in 9 chars | `000012345` |
| `N.2` | Numeric, 2 implied decimals | `$249.90` in 9 chars | `000024990` |
| `N.4` | Numeric, 4 implied decimals | `$12.3456` in 9 chars | `000123456` |
| `S.2` | Signed numeric, 2 implied decimals | `-$25.00` in 9 chars | `-00002500` |
| `S.4` | Signed numeric, 4 implied decimals | `-$1.0000` in 9 chars | `-00010000` |
| `D` | Date `YYYYMMDD` | April 22, 2026 | `20260422` |
| `T` | Time `HHMMSSDD` (DD = hundredths of second) | 05:00:09.23 | `05000923` |

**Required-field flags:**
- `M` = Mandatory — must be populated
- `A` = Applicable — mandatory when the data exists (e.g., Address Line 2)
- `C` = Conditional — mandatory based on documented conditions
- `O` = Optional

## Header record (10) — 1,207 chars

### Identification (positions 1–76)

| Start | End | Size | Type | Req | Field | Notes |
|---|---|---|---|---|---|---|
| 1 | 2 | 2 | N.0 | M | Record Type | Literal `10` |
| 3 | 8 | 6 | A | M | Miller Assigned Distributor Number | 6-char distributor ID assigned by MillerCoors |
| 9 | 28 | 20 | A | M | Retailer Identification Number | Retailer's trading-partner ID (may be DUNS+4) |
| 29 | 34 | 6 | A | M | Document Type | Literal `INV   ` (3 trailing spaces) or `PRE-D ` |
| 35 | 43 | 9 | N.0 | M | File Trace Number | Sequential, increments by 1, resets at 999999999 |
| 44 | 51 | 8 | D | M | System Date | Operating system date when generated |
| 52 | 59 | 8 | T | M | System Time | Operating system time |
| 60 | 60 | 1 | A | M | Product Category Invoice Code | `1`=soda, `2`=beer, `3`=wine, `4`=adjustment, space=mixed |
| 61 | 76 | 16 | A | M | Filler | Must be 16 spaces |

### Invoice and shipping (77–208)

| Start | End | Size | Type | Req | Field | Notes |
|---|---|---|---|---|---|---|
| 77 | 98 | 22 | A | M | Invoice Number | Must match any hard-copy invoice back-up |
| 99 | 120 | 22 | A | M | Purchase Order Number | Customer-assigned PO reference |
| 121 | 128 | 8 | D | M | Invoice Date | Date invoice was issued |
| 129 | 136 | 8 | D | M | Purchase Order Date | Date PO was created |
| 137 | 144 | 8 | D | M | Delivery Date / Return Date | Actual delivery or return date |
| 145 | 146 | 2 | A | M | Debit/Credit Flag | `DR` = debit (shipment), `CR` = credit (pickup/return) |
| 147 | 206 | 60 | A | O | Shipping Instructions | Free-form |
| 207 | 208 | 2 | A | O | Shipment Order Status | `CL`, `CM`, `CS`, `PD`, `SH`, `SI`, `SQ` |

### Distributor info (209–580)

| Start | End | Size | Type | Req | Field |
|---|---|---|---|---|---|
| 209 | 228 | 20 | A | M | Distributor Vendor ID Number |
| 229 | 241 | 13 | N.0 | O | Distributor Global Location Number (GLN) |
| 242 | 254 | 13 | N.0 | M | Distributor DUNS+4 |
| 255 | 289 | 35 | A | M | Distributor Name |
| 290 | 324 | 35 | A | M | Distributor Address 1 |
| 325 | 359 | 35 | A | A | Distributor Address 2 |
| 360 | 389 | 30 | A | M | Distributor City |
| 390 | 391 | 2 | A | M | Distributor State |
| 392 | 400 | 9 | A | M | Distributor Postal Code |
| 401 | 410 | 10 | N.0 | M | Distributor Phone Number |
| 411 | 420 | 10 | N.0 | M | Distributor Fax Number |
| 421 | 480 | 60 | A | M | Distributor Email Address |
| 481 | 515 | 35 | A | M | Distributor Administrative Contact Name |
| 516 | 550 | 35 | A | M | Distributor Sales Contact Name |
| 551 | 560 | 10 | A | M | Distributor AP Number |
| 561 | 570 | 10 | A | M | Delivery Route Number |
| 571 | 580 | 10 | A | M | Delivery Truck Number |

### Outlet info (581–799)

| Start | End | Size | Type | Req | Field |
|---|---|---|---|---|---|
| 581 | 600 | 20 | A | M | Outlet Number (a.k.a. store number) |
| 601 | 613 | 13 | N.0 | O | Outlet Global Location Number |
| 614 | 633 | 20 | A | M | Outlet Account Number (distributor-assigned) |
| 634 | 668 | 35 | A | M | Outlet Name |
| 669 | 703 | 35 | A | M | Outlet Address 1 |
| 704 | 738 | 35 | A | A | Outlet Address 2 |
| 739 | 768 | 30 | A | M | Outlet City |
| 769 | 770 | 2 | A | M | Outlet State |
| 771 | 779 | 9 | A | M | Outlet Postal Code |
| 780 | 799 | 20 | A | M | Outlet License Number |

### Customer info (800–1106)

Follows same pattern as distributor info (account number, GLN, DUNS+4, name, two address lines, city/state/zip, phone, fax, contact name, email).

### Terms info (1107–1207)

| Start | End | Size | Type | Req | Field |
|---|---|---|---|---|---|
| 1107 | 1108 | 2 | A | M | Payment Terms |
| 1109 | 1110 | 2 | A | M | Terms Basis Date |
| 1111 | 1116 | 6 | S.3 | M | Terms Discount Percent |
| 1117 | 1124 | 8 | D | M | Terms Discount Due Date |
| 1125 | 1127 | 3 | N.0 | M | Terms Discount Days Due |
| 1128 | 1135 | 8 | D | M | Terms Due Date |
| 1136 | 1138 | 3 | N.0 | M | Terms Net Days |
| 1139 | 1147 | 9 | S.2 | M | Terms Discount Amount |
| 1148 | 1207 | 60 | A | M | Terms Description |

## Detail record (20) — 462 chars (per line)

Positions 1–462. Key sections:

| Start | End | Size | Type | Req | Field |
|---|---|---|---|---|---|
| 1 | 2 | 2 | N.0 | M | Record Type (`20`) |
| 3 | 11 | 9 | N.4 | M | Gross Unit Price |
| 12 | 20 | 9 | N.4 | A | Deposit Amount |
| 21 | 29 | 9 | N.4 | A | Charge CRV (California Redemption Value) |
| 30 | 38 | 9 | N.4 | A | Split Case Fee |
| 39 | 47 | 9 | N.4 | A | Miscellaneous Charge 2 |
| 48 | 56 | 9 | N.4 | A | Sumptuary Tax (sin/luxury tax) |
| 57 | 65 | 9 | S.4 | A | Charge Rounding |
| 66 | 74 | 9 | S.4 | M | Total Charges |
| 75 | 83 | 9 | N.4 | M | State Tax (per unit) |
| 84 | 92 | 9 | N.4 | M | County Tax (per unit) |
| 93 | 101 | 9 | N.4 | M | City Tax (per unit) |
| 102 | 110 | 9 | N.4 | M | Total Tax (per unit, excludes sumptuary) |
| 111 | 119 | 9 | N.4 | A | Delivery Charge (per unit) |
| 120 | 128 | 9 | N.4 | A | Freight Charge (per unit) |
| 129 | 137 | 9 | S.4 | A | Promotional Discount (negative value, per unit) |
| 138 | 146 | 9 | N.4 | M | Net Unit Price |
| 147 | 155 | 9 | S.2 | M | Extended Price (qty × net unit price) |
| 156 | 164 | 9 | N.2 | O | Price to Consumer (shelf price) |
| 165 | 173 | 9 | S.0 | M | Quantity Ordered |
| 174 | 175 | 2 | A | M | Ordered Unit of Measure (`BO`, `CA`, `EA`, `KE`, `DS`) |
| 176 | 184 | 9 | S.0 | M | Quantity Shipped |
| 185 | 186 | 2 | A | M | Shipped Unit of Measure |
| 187 | 246 | 60 | A | O | Free Form Message |
| 247 | 260 | 14 | N.0 | M | UPC — Case (1-5-5-1 format) |
| 261 | 274 | 14 | N.0 | M | UPC — Pack |
| 275 | 288 | 14 | N.0 | M | UPC — Unit |
| 289 | 302 | 14 | N.0 | M | GTIN — Case |
| 303 | 316 | 14 | N.0 | M | GTIN — Pack |
| 317 | 330 | 14 | N.0 | M | GTIN — Unit |
| 331 | 350 | 20 | A | M | Distributor Item Number |
| 351 | 370 | 20 | A | O | Customer Item Number |
| 371 | 376 | 6 | N.0 | M | Packs per Case |
| 377 | 382 | 6 | N.0 | M | Units per Pack |
| 383 | 390 | 8 | N.4 | M | Case Weight (pounds) |
| 391 | 398 | 8 | N.4 | M | Case Volume (oz if product type 01/02, mL if 03/04) |
| 399 | 458 | 60 | A | M | Product Description |
| 459 | 460 | 2 | A | M | Product Type |
| 461 | 462 | 2 | A | M | Pack Basis Code |

## Summary record (30) — 198 chars

| Start | End | Size | Type | Req | Field |
|---|---|---|---|---|---|
| 1 | 2 | 2 | N.0 | M | Record Type (`30`) |
| 3 | 11 | 9 | S.2 | M | Net Invoice Total (extended prices − AR Adj − Ticket Adj) |
| 12 | 20 | 9 | S.2 | A | AR Adjustment |
| 21 | 29 | 9 | S.2 | A | Ticket Adjustment Discount |
| 30 | 39 | 10 | S.4 | M | Total Quantity Ordered |
| 40 | 49 | 10 | S.4 | M | Total Quantity Shipped |
| 50 | 59 | 10 | N.4 | M | Total Weight (pounds) |
| 60 | 69 | 10 | N.4 | M | Total Volume (ounces) |
| 70 | 78 | 9 | S.4 | A | Total Deposit |
| 79 | 87 | 9 | S.4 | A | Total Charge CRV |
| 88 | 96 | 9 | S.4 | A | Total Split Case Fee |
| 97 | 105 | 9 | S.4 | A | Total Miscellaneous Charge 2 |
| 106 | 114 | 9 | S.4 | A | Total Sumptuary Tax |
| 115 | 123 | 9 | S.4 | A | Total Charge Rounding |
| 124 | 132 | 9 | S.4 | M | Grand Total Charges |
| 133 | 141 | 9 | S.4 | M | Total State Tax |
| 142 | 150 | 9 | S.4 | M | Total County Tax |
| 151 | 159 | 9 | S.4 | M | Total City Tax |
| 160 | 168 | 9 | S.4 | M | Grand Total Tax |
| 169 | 177 | 9 | S.4 | A | Total Delivery Charge |
| 178 | 186 | 9 | S.4 | A | Total Freight Charge |
| 187 | 195 | 9 | S.4 | A | Total Promotional Discount |
| 196 | 198 | 3 | N.0 | M | Total Number of Detail Lines |

## Common pitfalls

1. **Record length off-by-one.** Padding calculation mistakes produce 1206/1208-char headers. OpenText's translator hard-rejects before retailer sees the file.
2. **Blank mandatory fields.** Positional fields can be "present but empty" (all spaces). OpenText rejects but the error often surfaces against an adjacent field because positional fields have no explicit presence flag.
3. **Implied-decimal scale errors.** `N.4` fields expect four implied decimals. Treating them as `N.2` produces 100× scale errors that either reject at validation or (worse) pass validation and cause AP disputes.
4. **Padding direction flipped.** Numerics must right-align zero-pad; alpha must left-align space-pad. Zero-padding alpha or space-padding a DUNS number rejects.
5. **Line endings.** GXS wants CRLF (`\r\n`). LF-only files sometimes pass a naive parser but fail OpenText's validator.
6. **Non-ASCII characters.** Smart quotes, accented characters, and em-dashes in free-form fields (shipping instructions, product description, contact names) reject.
7. **Document Type missing trailing spaces.** Position 29–34 must be `INV   ` (exactly `INV` + 3 spaces). `INV` or `INVOICE` rejects.
8. **File Trace Number collisions.** Must be sequential per sender, never reused, resets at 999,999,999. Duplicate trace # = reject at OpenText layer before retailer sees the file.
9. **Summary ≠ details.** Summary totals (record 30) must equal the sum of detail extended amounts (record 20). Off-by-penny rounding errors get caught.
10. **UPC/GTIN level mismatch.** Partners differ on which UPC level they want: case vs. pack vs. unit. Even if all three are present in the detail row, sending a case UPC where a pack UPC is required rejects.

## Translated error mapping (UFF → X12 810)

When OpenText rejects a UFF file, its error references often use **X12 segment names** (BIG, N1, IT1, TDS). See `knowledge-base/edi/uff-to-x12-810-mapping.md` for the crosswalk — essential when diagnosing a rejection whose error tag doesn't directly reference a UFF field name.

## Diagnosing rejections — recommended workflow

When a UFF file rejects, work through these steps in order. Skip ahead only after eliminating the prior step.

### Step 0 — Diff against last-known-working version of the generator

If the integration was working recently (days, not months) and is now rejecting, the cause is almost always a **recent code change**, not a data shift, partner-side change, or new spec interpretation. Before any other diagnostic work:

1. Ask the generator owner for the last-known-working version of the script.
2. Run a literal `diff` against the current version.
3. Pay particular attention to default initializers, fallback values, and conditional branches. JavaScript regressions often look like trivial edits (e.g., `let x = ''` vs `let x = source.field`).

This step takes seconds and frequently exposes the entire problem. A working ↔ broken diff is faster and more reliable than a byte-by-byte spec walk for any regression-style failure.

**Real example (2026-04-23, Beverage Market):** All 8 invoices in a 7-Eleven batch rejected with `BIG_01_373`. A 1-line diff exposed:

```diff
-    let invoiceNumber = '';
+    let invoiceNumber = data.ohfy__Order_Number__c;
```

That single change caused every Invoice Number field to come out blank. Documented at `customers/beverage-market/edi/rejection-2026-04-23.md`.

### Step 1 — Decode the X12 error tag

OpenText surfaces rejections as `<SEGMENT>_<ELEMENT>_<DATA_ELEMENT>` (e.g., `BIG_01_373`, `N1_04_67`, `IT1_07_234`). Use `knowledge-base/edi/uff-to-x12-810-mapping.md` to translate the X12 segment back to UFF positions.

**Critical: error tags are often misleading.** When a *later* mandatory element in a segment is missing, OpenText anchors the error against the *first* element with a generic data-element type reference. `BIG_01_373` typically means BIG02 (Invoice Number) is missing, not BIG01 (Invoice Date). Walk every mandatory position in the named segment, not just the literal element.

### Step 2 — Walk every mandatory position in the rejected file

Given the X12 segment from Step 1, walk every UFF position that feeds it:

1. Cross-reference the position table in this doc.
2. For each mandatory (`M`) field, check: is it populated? Right type? Right padding direction? Right scale (for `N.x` fields)?
3. Note all blank or malformed M-fields.

Common pre-existing landmines surfaced this way:
- JavaScript `null + ''` coercion produces literal `"null"` / `"NULL"` strings in alpha fields.
- Hardcoded empty defaults that should map to source data (e.g., GTIN fields hardcoded to `''`).
- Code reads from wrong object property (e.g., a field that exists on the order but is read from the customer).

### Step 3 — Cross-reference retailer requirements

Some rejections are retailer-specific even when the file is structurally valid against the base spec. Check `knowledge-base/edi/uff-retailer-requirements.md` for:
- Required fields that the base spec marks optional.
- UPC/GTIN level expectations (case vs. pack vs. unit).
- Line-level vs. summary-level tax requirements.

### Step 4 — Reproduce with a test harness

For systemic bugs (not "bad data on this one invoice"), build a quick Node harness that:

1. Loads sample variables (real production data preferred).
2. Runs the generator's helper functions against them.
3. Concatenates the output and validates record lengths + mandatory-field presence.

Pattern available at `.context/uff-test/run.js` (Beverage Market). Re-run after any proposed fix to confirm before deploying.

### Step 5 — Record findings

Update the customer's `known-issues.md` with the resolution and any latent bugs uncovered. Move the active blocker to "Resolved Issues" with the diagnostic timeline. Future rejections of the same signature should be diagnosed in minutes by reading the recurring-patterns section.
