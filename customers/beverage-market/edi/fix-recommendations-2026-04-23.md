# UFF Generator Fix Recommendations — 2026-04-23

Directed at whoever owns the UFF generator for Beverage Market's MillerCoors 810 invoicing. Based on diagnosis of the 2026-04-23 rejection batch (see `rejection-2026-04-23.md`).

> **STATUS: Critical fix applied 2026-04-24 — production restored.** The rest of this doc remains valid as a reference for the latent bugs that were not addressed in the hotfix. See `rejection-2026-04-23.md` § Resolution for the actual one-line fix that landed.

## Critical fix (applied)

Single-line regression in the Tray script's `getInvoiceNumber` function. Default initializer was `let invoiceNumber = '';`; reverted to `let invoiceNumber = data.ohfy__Order_Number__c;`. This restores the invoice number population for all non-Target EDI orders. PO Number field (line 927) had also been bound to `invoiceNumber`, so it picked up the fix as a side-effect.

## TL;DR

Every UFF file the generator was producing was missing **five mandatory header fields** because of one upstream regression. Every invoice to every retailer was rejecting with `BIG_01_373`. Root cause was a generator mapping bug, not a data problem.

## Required immediate fixes

All invoices are currently rejecting. Priority-1 work.

| # | UFF Position | Length | Type | Field | Required source |
|---|---|---|---|---|---|
| 1 | 77–98 | 22 | A | **Invoice Number** | SF Invoice `Name` or `External_Id__c` — values like `F-1372605505` |
| 2 | 99–120 | 22 | A | Purchase Order Number | Inbound PO reference from the retailer order (SF Order `PO_Number__c` or equivalent) |
| 3 | 421–480 | 60 | A | Distributor Email | Static config — Beverage Market's EDI/AR email address |
| 4 | 516–550 | 35 | A | Distributor Sales Contact Name | Assigned sales rep per account (SF Account `Owner.Name` or similar) |
| 5 | 614–633 | 20 | A | Outlet Account Number | Distributor-assigned customer ID — SF Account `External_Id__c` on the retailer outlet account |

### Format reminders

- All five are `A` (alpha) type: **left-align, pad right with spaces to the exact field length.**
- Do NOT zero-pad (that's for numerics).
- ASCII only — no smart quotes, accented chars, em-dashes.
- Retailer IDs (Invoice Number, Account Number) go in as-is; no transformation.

## Verifications (not confirmed rejections, but worth checking)

### Pricing-scale sanity check (`N.4` fields)

Spot-check in the 2026-04-23 sample shows low Gross Unit Price values that should be verified:

- Line 2 (Modelo Especial 4/6pk BTL case): Gross Unit Price positions 3–11 = `000033000` → $3.3000 with `N.4` encoding. That reads low for a case of premium import beer.
- Line 14 (Steel Reserve 12/24oz case): Gross Unit Price = `000121500` → $12.1500.

If the generator is treating `N.4` fields as `N.2` (a 100× scale error), prices will be off by 100×. File would still structurally parse but AP downstream would dispute. **Confirm the pricing scale across a production batch.**

### Payment Terms code

Position 1107–1108 in the sample = `ZZ` ("Mutually Defined" per X12 reference). The Terms Description at 1148–1207 is `DUE ON RECEIPT`. Consider using a more specific code:

- `22` = Due on Receipt
- `01` = Basic
- `08` = Basic Discount offered

Check 7-Eleven's UFF companion guide for the accepted code set.

### Distributor AP Number

Position 551–560 = `D-00008236`. Field is alpha-typed so the `D-` prefix is spec-legal, but some retailers' application rules reject non-numeric AP numbers. Flag for verification — not a current blocker.

## Regression-test checklist (after fix)

Before resubmitting, validate the generated UFF against these items. Run against a single test invoice first, then a batch.

1. **Header length = 1,207 chars exactly** (before CRLF). `wc -c` on a header-only line should return 1209 (1207 + `\r\n`).
2. **Detail rows = 462 chars each** (before CRLF).
3. **Summary row = 198 chars** (before CRLF).
4. **Line endings are CRLF (`\r\n`)**, not LF-only.
5. **All five previously-blank fields are populated** with real data, left-aligned, space-padded to exact field lengths.
6. **File Trace Number is sequential** and has not been used before (OpenText rejects duplicates).
7. **Summary totals match detail sums**: Net Invoice Total (record 30 positions 3–11) = sum of all Extended Prices (record 20 positions 147–155). Total Number of Detail Lines (record 30 positions 196–198) = actual count of record-20 lines.
8. **ASCII-only** — no UTF-8 smart quotes or accented chars anywhere in alpha fields.

## Cross-retailer readiness

After 7-Eleven rejections clear, the same generator will be sending UFF to **Walmart and other MillerCoors retailers**. Key retailer differences to watch for (full matrix: `knowledge-base/edi/uff-retailer-requirements.md`):

- **UPC/GTIN level:** 7-Eleven expects case-level (positions 247–260, 289–302). Walmart expects pack-level (positions 261–274, 303–316). Generator must emit both and know which one is "the" UPC for each retailer — but since UFF has dedicated positions for all three levels, populate all of them and let the retailer read the level they want.
- **Line-level tax:** Walmart wants State (75–83), County (84–92), and City (93–101) tax populated per line. 7-Eleven only requires the summed Total Tax (102–110).
- **Line-level Product Description:** Walmart requires position 399–458 on every detail line. 7-Eleven doesn't flag it required, but your generator already populates it.

## Latent bugs (still open after hotfix)

Identified by running the test harness in `.context/uff-test/` against the live data payload. Tracked in `customers/beverage-market/known-issues.md` → Open Issues. Brief recap:

| # | Where | Problem | Fix |
|---|---|---|---|
| 1 | `getVendorId` (~line 856) | `null + ''` produces `"null"` → `"NULL"` in UFF position 209–228 when chain has no NA vendor ID | `(vendorId ?? '') + (orderData.EDI_Department_Number__c \|\| '')` |
| 2 | `generate810DetailRecord` (lines 1042–1044) | GTIN Case/Pack/Unit hardcoded to `''` → 14 zeros in detail records | Mirror UPC fields: `cleanUPC(item.ohfy__Item__r?.ohfy__Case_UPC__c)` etc. |
| 3 | Header (line 950) | AP Number reads `customer.Distributor_Vendor_AP_Number__c` — field doesn't exist on SF Account | Decision: add field to SF, or remap to existing field |
| 4 | Header (lines 971–975) | Customer Address block reads from chain banner (often null) instead of outlet | Decision: confirm whether UFF "Customer" block = corporate retailer or outlet |

## Open questions for the distributor / generator owner

1. ~~Where does the generator run?~~ **Resolved:** Tray workflow.
2. Is there a staging / test trading-partner setup at OpenText where a fixed file can be validated before going live? If not, recommend requesting one from the OpenText account rep before the next production attempt.
3. Are rejections from **Walmart** showing the same `BIG_01_373` signature, or a different error? If different (e.g., UPC-level mismatch), a separate Walmart ticket is needed.
4. Latent bug #3 (AP Number) and #4 (Customer Address source) need data-model decisions before fixes can land.
