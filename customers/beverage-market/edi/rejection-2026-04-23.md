# UFF Rejection Incident — 2026-04-23

## Source

- **Distributor:** Beverage Market dba Capitol Beverage Company WV (Miller Distributor # `854628`, Vendor ID `77731`, DUNS `094472288-0000`)
- **Batch filename:** `MILLER810FFbs.att`
- **Retailer:** 7-Eleven (Retailer ID `007347602SLND`, outlet example `#46132`)
- **Batch size:** 8 invoices (all rejected with same signature)
- **File Trace #s (examples):** `001525317` (the sample file archived here is one of this batch)

## Rejected invoice references

From the Business Network Support Notification screenshot:

| Session | Reference # |
|---|---|
| 041339724 | F-1372605505 |
| 041339728 | F-1372605526 |
| 041339758 | F-1372605538 |
| 041339770 | F-1372605564 |
| 041339739 | F-1372605594 |
| 041339767 | F-1372605640 |
| 041339742 | F-1372605671 |
| 041339771 | F-1372605771 |

## OpenText notification

> **Business Network Support Notification — Translation Data Error**
> **Action Required By:** CAPITOL BEVERAGE COMPANY WV
> **Error Type:** 506 — User-Defined Generic Error
> **Source:** AI
> **Error Message:** Attachment Error# 504, On `MILLER810FFbs.att` — Target Error Within Attachment — `ECSCApiRec.att` (Message Processing). **Tag in Error: BIG — ~BIG_01_373**
> **Support:** 877-425-8213 / `mdep-help@opentext.com`

## Diagnosis

**Root cause:** UFF generator is not populating mandatory fields in the header record. See `sample-7eleven-rejected-2026-04-23.uff` for reference.

Walking the 1,207-char header against the UFF spec (`knowledge-base/edi/uff-format.md`):

| Position | Field | Required | Actual |
|---|---|---|---|
| 77–98 | **Invoice Number** | M | 22 spaces (blank) ❌ |
| 99–120 | Purchase Order Number | M | 22 spaces (blank) ❌ |
| 421–480 | Distributor Email | M | 60 spaces (blank) ❌ |
| 516–550 | Distributor Sales Contact | M | 35 spaces (blank) ❌ |
| 614–633 | Outlet Account Number | M | 20 spaces (blank) ❌ |

All other mandatory header fields (Invoice Date, Distributor Name/Address/Phone, Outlet Number/Name/Address, Terms) are correctly populated.

### Why the error says `BIG_01_373` instead of Invoice Number

X12 810 `BIG` segment maps (per `knowledge-base/edi/uff-to-x12-810-mapping.md`):

- `BIG01` = Invoice Date ← UFF 121–128 (present, `20260422`)
- `BIG02` = **Invoice Number** ← UFF 77–98 (**BLANK** — this is the failure)
- `BIG03` = PO Date ← UFF 129–136
- `BIG04` = PO Number ← UFF 99–120 (blank — secondary)

When OpenText translates UFF → X12 and discovers `BIG02` is blank (a mandatory X12 element), the BIG segment becomes structurally invalid. OpenText's error reporter anchors on the first element (`BIG_01`) and uses the X12 data-element reference for Date (`373`) as a generic tag. **The date itself is fine; the error label is misleading.**

### Why this is systemic

All 8 invoices in the batch fail with the exact same error and the same missing-field signature. This is not a data issue on individual invoices — the generator is consistently not writing the invoice number into positions 77–98 (nor the other 4 mandatory fields). Every outbound invoice to every MillerCoors retailer will fail the same way until this is fixed.

The reference numbers visible in the OpenText UI (`F-1372605505`, etc.) are the values that should be populating positions 77–98 of the UFF but aren't.

## Resolution (2026-04-24)

**Root cause: one-line regression in the Tray UFF generator script.**

After the user provided both the current (broken) script and the last-known-working version (from one week prior), a `diff` showed a single line changed in `getInvoiceNumber`:

```diff
 function getInvoiceNumber(data) {
     if (!data) return null;

-    let invoiceNumber = '';
+    let invoiceNumber = data.ohfy__Order_Number__c;

     if (data.EDI_Order__c === false || data.ohfy__EDI_Order__c === false) {
         invoiceNumber = data?.ohfy__External_ID__c ?? data?.ohfy__Order_Number__c;
     }
     if (data.ohfy__Customer__r.ohfy__Chain_Banner_Lookup__r.Name === 'Target') {
         invoiceNumber = data.ohfy__Order_Number__c.slice(-7);
     }
     return invoiceNumber;
 }
```

For any order where `EDI_Order__c === true` and the chain isn't Target (i.e., normal 7-Eleven, Walmart, etc. orders), neither override branch fires. The default initializer is the *only* path that sets the invoice number. Changing the default from `data.ohfy__Order_Number__c` to `''` silently broke every EDI invoice.

**The other 4 blank fields** (PO Number, Distributor Email, Distributor Sales Contact, Outlet Account Number) were either side-effects of the same code path (`PO Number` field on line 927 reused the `invoiceNumber` variable) or pre-existing data gaps that didn't matter because the bigger BIG02 error was rejecting the file at the OpenText layer first.

**Fix applied:** reverted the one line. Confirmed working in production.

### Why the error message was misleading

OpenText surfaced the error as `BIG_01_373` — element 01 (Invoice Date) with X12 data element reference 373 (Date type). The actual missing element was `BIG02` (Invoice Number → UFF positions 77–98). When BIG02 is missing, the translator cannot structurally validate the segment and anchors the error against the first element with a generic data-type reference. **The date itself was perfectly valid.** Always walk the full UFF header for blank mandatory fields before chasing the literal element named in the error.

### Latent bugs uncovered during diagnosis (not fixed yet)

Walking the file revealed four pre-existing UFF generator bugs that survived the regression fix. Tracked in `customers/beverage-market/known-issues.md` → Open Issues:

1. `getVendorId` emits literal `"NULL"` for non-alcoholic chains without an NA vendor ID (JavaScript `null + ''` coercion)
2. GTIN fields hardcoded to empty string in `generate810DetailRecord` (positions 289–302, 303–316, 317–330)
3. `AP Number` reads `customer.Distributor_Vendor_AP_Number__c` — a field that doesn't exist on the SF Account
4. `Customer Address` block reads from chain banner instead of customer outlet — fails when chain banner has no ShippingAddress

### Diagnostic timeline

| Step | Action | Output |
|---|---|---|
| 1 | Parse rejected UFF file position-by-position against spec | Identified 5 blank mandatory header fields |
| 2 | Cross-ref `BIG_01_373` against UFF→X12 mapping | Confirmed `BIG02` (Invoice Number) is the actual missing element |
| 3 | Request generator code | Spotted `getInvoiceNumber` returning `''` for EDI orders |
| 4 | Build test harness, run with sample variables | Reproduced blank Invoice Number; identified additional bugs (NULL vendor, blank GTINs) |
| 5 | Request last-known-working version | One-line diff exposed the exact regression |
| 6 | Revert + verify | Production restored |

### Lesson

**When an integration that was working last week suddenly rejects every file, ask for the last-known-working version of the code first.** A 5-second `diff` exposes recent regressions instantly. The byte-by-byte spec walk was useful for confirming the diagnosis and uncovering latent bugs, but the working-vs-broken diff would have pointed straight at the answer.

## Related

- Full triage checklist: `customers/beverage-market/known-issues.md`
- UFF spec: `knowledge-base/edi/uff-format.md`
- X12 mapping: `knowledge-base/edi/uff-to-x12-810-mapping.md`
- Per-retailer requirements: `knowledge-base/edi/uff-retailer-requirements.md`
