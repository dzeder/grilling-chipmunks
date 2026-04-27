# The Beverage Market — Known Issues

Running log of known issues, workarounds, and resolutions for this customer.

## Open Issues

### Latent UFF generator bugs (uncovered during 2026-04-23 incident)

These were present in the UFF generator before the 2026-04-23 incident and survived the regression fix. Not currently rejecting all invoices, but each will bite specific retailer/data combinations.

#### 1. `getVendorId` emits literal `"NULL"` for non-alcoholic chains without an NA vendor ID

- **Severity:** High (rejects invoices for affected chains)
- **Affected area:** Tray UFF generator → `getVendorId`
- **Code:** Around line 856 of the script — `vendorId = vendorId + (orderData.EDI_Department_Number__c || '');`
- **Trigger:** Order has only non-alcoholic items AND `chainBanner.Distributor_NA_Vendor_ID_Number__c` is null. JavaScript coerces `null + ''` to the string `"null"`, which then formats as `"NULL"` (uppercased) in UFF position 209–228.
- **Fix:** `vendorId = (vendorId ?? '') + (orderData.EDI_Department_Number__c || '');`

#### 2. GTIN fields hardcoded to empty string (positions 289–302, 303–316, 317–330 of detail records)

- **Severity:** High (will reject for any retailer that validates GTIN — including 7-Eleven on case-level and Walmart on pack-level per the UFF retailer matrix)
- **Affected area:** Tray UFF generator → `generate810DetailRecord` lines 1042–1044
- **Code:** All three fields hardcoded `value: ''`, which formats to 14 zeros.
- **Fix:** Mirror the UPC fields — `value: cleanUPC(item.ohfy__Item__r?.ohfy__Case_UPC__c)` etc. UPC-12 zero-padded to 14 chars is a valid GTIN-14.

#### 3. AP Number reads a nonexistent field

- **Severity:** Medium (depends on whether retailer validates AP number)
- **Affected area:** Tray UFF generator → header line 950
- **Code:** `customer.Distributor_Vendor_AP_Number__c` — field does not exist on the customer Account in current SF schema.
- **Fix:** Decision needed — add the field to SF, or remap to an existing field (e.g., `chainBanner.ohfy__Distributor_Vendor_ID_Number__c`).

#### 4. Customer address pulled from chain banner, not customer outlet

- **Severity:** Medium (rejects when chain banner Account has no ShippingAddress)
- **Affected area:** Tray UFF generator → header lines 971–975
- **Code:** Reads `ohfy__Customer__r.ohfy__Chain_Banner_Lookup__r.ShippingAddress.*` for Customer Address/City/State/Zip (positions 881–991). Chain banner is the parent retailer entity, often without its own shipping address.
- **Decision needed:** Spec language is ambiguous — is the UFF "Customer Information" block the corporate retailer (chain banner) or the actual outlet? Pull a known-good UFF from another customer to see which entity populates that block.

## Resolved Issues

### 2026-04-23 — UFF generator regression: blank Invoice Number → all invoices rejecting (`BIG_01_373`)

- **Severity:** Critical (was rejecting every outbound EDI invoice batch)
- **Affected area:** Tray UFF generator script → `getInvoiceNumber` function
- **Reported:** 2026-04-23 (8-invoice batch `MILLER810FFbs.att` to 7-Eleven, references F-1372605505 through F-1372605771)
- **Resolved:** 2026-04-24
- **Root cause:** A single-line regression in `getInvoiceNumber`. Default initializer was changed from `let invoiceNumber = data.ohfy__Order_Number__c;` to `let invoiceNumber = '';`. For any order where `EDI_Order__c === true` and the chain isn't `Target`, neither override branch fired, so the function returned an empty string. Empty Invoice Number space-padded to 22 chars → blank UFF positions 77–98 → blank X12 `BIG02` after OpenText translation → `BIG_01_373` rejection.
- **Fix:** Reverted line 2908 to `let invoiceNumber = data.ohfy__Order_Number__c;`.
- **Misleading error:** OpenText error tag `BIG_01_373` references the date data-element type. The actual cause was the missing Invoice Number (BIG02). When BIG02 is missing, OpenText anchors the error against the first element with a generic data-type reference. Always walk the full UFF header for blank mandatory fields before chasing the literal element named.
- **Diagnostic timeline:**
  1. Parsed the rejected UFF file position-by-position against the spec → identified 5 blank mandatory fields (Invoice #, PO #, Distributor Email, Sales Contact, Outlet Account #).
  2. Asked for the generator code → spotted `getInvoiceNumber` returning `''` for EDI orders.
  3. Asked for last-known-working version → diff revealed exactly one line changed.
- **Artifacts:** `edi/sample-7eleven-rejected-2026-04-23.uff`, `edi/rejection-2026-04-23.md`, `edi/fix-recommendations-2026-04-23.md`.
- **Lesson:** When a working integration suddenly breaks, ask for the last-known-working version of the code first. A 5-second diff often beats a 30-minute byte-by-byte spec walk.

## UFF Rejection Triage Checklist

Run these checks top-down on any rejected UFF file to identify the failure mode quickly:

0. **Diff against last-known-working version of the generator first.** If the integration was working recently, a recent code change is the most likely cause. Items 1–15 below only apply if no recent change exists or the diff is irrelevant.
1. **Record-length** — header = exactly 1,207 chars, detail = 462 chars per line, summary = 198 chars (all before CRLF). Off-by-one = hard reject.
2. **Line endings** — GXS wants CRLF (`\r\n`). LF-only files sometimes fail OpenText validation.
3. **Character encoding** — ASCII only. UTF-8 smart quotes, accented chars, em-dashes in free-form fields reject.
4. **Implied decimals** — `N.4` fields mean 4 implied decimals (`000123456` = $12.3456). Treating as `N.2` produces 100× scale errors.
5. **Date/time format** — `YYYYMMDD` dates only. System Time is `HHMMSSDD` where `DD` = hundredths of a second, not day.
6. **Numeric padding** — numerics right-align zero-pad; alpha left-align space-pad. Zero-padding alpha or space-padding numerics rejects.
7. **Signed numerics** — `S.x` fields use leading sign (`+`/`-`) or COBOL overpunch. Confirm which convention this partner's OpenText map expects.
8. **Filler (61–76)** — must be exactly 16 spaces. Any non-space = format error.
9. **Required-field presence per retailer** — cross-ref `knowledge-base/edi/uff-retailer-requirements.md`. Blank M-flagged fields reject even if the file is structurally valid.
10. **JavaScript `null + ''` coercion** — when a field source is `null` and code concatenates without a guard, the literal string `"null"` ends up in the UFF (uppercases to `"NULL"`). See latent bug #1 above for live example.
11. **UPC/GTIN level** — 7-Eleven wants **case** (positions 247–260, 289–302). Walmart wants **pack** (261–274, 303–316). Populate all levels, but know which one the retailer will read.
12. **Document Type** — position 29–34 must be literal `INV   ` (3 trailing spaces). `INV` unpadded or `INVOICE` rejects.
13. **File Trace Number** — must be sequential, never reused, resets at 999,999,999. Duplicate trace # = OpenText-level reject before retailer sees it.
14. **Record type prefix** — every line starts with `10`, `20`, or `30`. Blank lines between records = reject.
15. **Summary ≠ details consistency** — record-30 Net Invoice Total must equal sum of record-20 Extended Prices. Total Number of Detail Lines must equal actual record-20 line count.
16. **Retailer Identification Number** — 7-Eleven's and Walmart's IDs are distinct. Wrong ID = routes nowhere or rejects.

## Recurring Patterns

### "BIG_01_373" errors from OpenText are usually NOT about the date

OpenText rejections tagged `BIG_01_373` (X12 data element 373 = Date) almost always indicate a **different mandatory BIG element is missing**, most commonly BIG02 = Invoice Number (UFF positions 77–98). The translator can't anchor the segment when a later mandatory element is blank, so it surfaces the error against BIG01 with a generic date-type reference. Always walk the full UFF header for blank mandatory fields before chasing the literal element named in the error.

See `knowledge-base/edi/uff-to-x12-810-mapping.md` for the full X12 ↔ UFF crosswalk.

### Sudden integration regression → diff against last-working version first

If an EDI integration that was working last week suddenly rejects every file, the cause is almost always a recent code change, not a data shift or partner-side change. Before walking through spec compliance for hours, ask the integration owner for the last-known-working version of the generator script and run a literal `diff`. The 2026-04-23 incident root cause was a single-character edit (`= ''` instead of `= data.ohfy__Order_Number__c`); the diff exposed it instantly.
