# VIP Accounting Deep Dive

> Analysis of VIP's accounting capabilities based on Gulf Distributing's live database.
> Ohanafy does not currently have an accounting module — this document captures what VIP has
> so we can plan what to build or integrate with.

---

## Executive Summary

VIP has a **full-featured accounting system** built into its distribution platform. It's not a standalone module — it's deeply woven into the operational flow. Every delivery, credit, payment, and deposit flows through to a General Ledger via transaction records.

**Key stats (Gulf Distributing):**

| Area | Table(s) | Rows | Notes |
|------|----------|------|-------|
| Chart of Accounts | GLACCOUNTMASTER | 3,492 | 9 companies, account #s 100010–999998 |
| Daily Transactions | DAILYT | 30,071,343 | The heart of VIP — every sale, credit, payment |
| AP Checks | APCHKLT | 11,687 | $63.6M total, 2018–2022 |
| AP Payment Batches | APPAYMENTBATCH | 3,854 | Active through 2026-03-12 |
| AR Comments | ARCMNTST | 3,857 | Collection notes, fintech status |
| AR Batch Tasks | AR_BATCH_TASK | 125,375 | Batch posting to GL |
| Open AP Invoices | APRC_AT | 140 | Current open payables |
| Customer AR Balances | BRATTT.CMAR$ | 5,568 with balance | $10.7M owed, $428K credits |

---

## 1. General Ledger (GL)

### Chart of Accounts — GLACCOUNTMASTER (3,492 rows)

This is the full chart of accounts. Every GL account used by the business lives here.

**Key columns:**

| Column | Type | Description |
|--------|------|-------------|
| GLACCOUNTNUMBER | numeric | Account number (e.g., 110301) |
| FORMATTEDACCOUNTNUMBER | char(16) | Formatted display number |
| GLACCOUNTDESCRIPTION | char(30) | Human-readable name |
| GLCOMPANYNUMBER | char(1) | Company code (1–9) |
| ACCOUNTTYPE | char(1) | Always blank for Gulf — unused field |
| IDENTITY | bigint | VIP identity |

**Account structure follows standard accounting ranges:**

| Range | Category | Examples |
|-------|----------|---------|
| 110xxx | Cash & Bank | Petty Cash, JP Morgan Operating, Regions Deposit, Truist Operating, Merrill Lynch |
| 111xxx | Receivables | Accounts Receivable, AR-Freight, AR-Supplier |
| 112xxx–119xxx | Other Current Assets | Prepaid expenses, inventory accounts |
| 2xxxxx | Expenses/Overhead | Professional Services, 401K Match, Cell Phone, Recruitment, Safety |
| 3xxxxx | Revenue/Sales | Salaries, Sales Incentives |
| 5xxxxx | Payroll & Operations | Payroll Taxes, Unemployment, Telephone |
| 999997 | Default Inventory | System default |
| 999998 | Default COGS | System default |

**Multi-company structure (9 companies):**

| Company | Accounts | Likely Entity |
|---------|----------|---------------|
| 1 | 918 | GDCM (Gulf Distributing Co Mobile — primary) |
| 2 | 56 | Unknown |
| 3 | 582 | ABC (Allstate Beverage) |
| 4 | 153 | EBMJ (East Bay/Mobile Joint venture?) |
| 5 | 659 | GGDC |
| 6 | 305 | EBMG |
| 7 | 416 | GDCA |
| 8 | 204 | Unknown |
| 9 | 199 | Unknown |

Company names are derived from APPAYMENTBATCH descriptions (e.g., "GDCM AP 03/11/2026", "ABC AP 03/11/2026").

### GL Report Definitions — GLHEADT (5,359 rows)

These define the financial reports that VIP can generate. Sample reports:

- BALANCE SHEET - MOBILE (rep 151)
- BALANCE SHEET - GDCM (rep 150)
- CONSOLIDATED P&L (rep 100)
- INCOME STATEMENT - MOBILE (rep 140)
- ALABAMA - COMBINED DETAIL (rep 149)
- ACT V BUD MANAGER VIEW CO# 3 (rep AB3)
- Various personal expense reports (MF'S EXPENSES, LM'S EXPENSES, etc.)

### GL Column Definitions — GLCOLT (78 rows)

Defines columns for GL reports (period amounts, comparisons, formatting). This is the report layout engine — 36 periods with amounts (G4CN01–G4CN36), column properties (G4CO01–G4CO36), and year references (G4YR01–G4YR36).

### GL Fiscal Years — GLYEART (2 rows)

Currently tracking years **2025** and **2026**.

### GL User Permissions

- **USERGLCOT** (106 rows) — Maps users to GL company permissions (which companies each user can see)
- **USERGLHT** (907 rows) — Maps users to GL report access (which reports each user can view)

---

## 2. Accounts Payable (AP)

### Vendor Master — APVENT (5,665 rows)

Already used in migration for supplier data. Key **accounting-specific** fields:

| Column | Type | Description |
|--------|------|-------------|
| VRVEND | numeric | Vendor number (PK) |
| VRNAME | char | Vendor name |
| VRDUED | numeric | Due days (payment terms) |
| VRDUEC | char | Due code (payment terms type) |
| VR1099 | char | 1099 reporting flag |
| VR99BX | numeric | 1099 box number |
| VR99NAME/ADD1/ADD2/PC | char | 1099 name and address |
| VRSDPCT | numeric | Discount percentage |
| VRSEPCHK | char | Separate check flag |
| VRSNOPAY | char | No-pay flag |
| VRSABA | numeric | ABA routing number |
| VRSBACT | char | Bank account number |
| VRSBANK | char | Bank name |
| VRSATYP | char | Payment type |
| VRSALESTX | char | Sales tax flag |
| VRCHKMSG | char | Check message |
| VRDCOD | char | Discount code |

### AP Checks — APCHKLT (11,687 rows)

Every check ever written to vendors. **Date range: 2018-01-05 to 2022-11-09.** Total: $63,651,818.35.

| Column | Type | Description |
|--------|------|-------------|
| CHECKNUMBER | numeric | Check number |
| CHECKDATE | numeric | Check date (YYYYMMDD) |
| CHECKAMOUNT | numeric | Dollar amount |
| VENDORNUMBER | numeric | FK to APVENT |
| STATUSCODE | char(1) | R = Regular/cleared, V = Void |
| BATCHNUMBER | char(2) | Batch identifier |
| CLEAREDDATE | numeric | Bank cleared date |
| PAYMENTMETHOD | numeric | Payment method code |
| GLCOMPANYNUMBER | char(1) | Which company |
| ACCOUNTNUMBER | char(5) | GL account for payment |

**Status distribution:** 11,546 regular (R), 141 voided (V)

> **Note:** Check data stops at Nov 2022 — Gulf may have switched to electronic payments after this, or the check register data isn't being synced. AP payment batches continue through March 2026.

### AP Payment Batches — APPAYMENTBATCH (3,854 rows)

Batch payment processing records. Still active (most recent: 2026-03-12). These represent groups of payments being processed together.

| Column | Description |
|--------|-------------|
| DESCRIPTION | Batch description (e.g., "GDCM AP 03/11/2026") |
| POSTINGDATE | GL posting date |
| STATUSCODE | PST = Posted |
| GLCOMPANYNUMBER | Company |
| HANDWRITTENCHECKS | Count of manual checks |
| VOIDINVOICES | Count of voided invoices |

### Open AP — APRC_AT (140 rows)

Current open payables (invoices not yet fully paid).

| Column | Type | Description |
|--------|------|-------------|
| AWVENA | numeric | Vendor number |
| AWINVA | char(15) | Invoice number |
| AWIDAT | numeric | Invoice date |
| AWDDAT | numeric | Due date |
| AWITOT | numeric | Invoice total |
| AWDAMT | numeric | Discount amount |
| AWDCDA | char(1) | D/C code (A = accrual) |

Sample data shows recurring invoices (RECUR 2603, LEASE 2603) and one-time POs. Amounts range from $50 to $277,500.

### AP GL Account Types — APGLACCOUNTTYPE (3 rows)

| Code | Name |
|------|------|
| POAC | PO Accrual |
| APAC | AP Liability |
| DTAC | Discounts Taken |

### AP GL Distributions — APGLDISTRIBUTIONS (2 rows)

Maps AP invoice line items to GL accounts. Links invoices to their GL distribution (which GL accounts get debited/credited).

### AP PO Accrual Accounts — AP_PO_ACCRUAL_ACCOUNTS (38 rows)

Maps warehouses to their PO accrual GL accounts. Currently all empty/zero — may not be in use.

---

## 3. Accounts Receivable (AR)

### Customer AR Balances — BRATTT

The customer master table carries real-time AR data:

| Column | Type | Description |
|--------|------|-------------|
| CMAR$ | numeric | Current AR balance |
| CMCLIM | numeric | Credit limit |
| CMTERM | char | Payment terms code |
| CMTXCD | char(1) | Tax code (N = not taxable, Y = taxable) |
| CMGLPT | numeric | GL posting flag (0 or 1) |
| CMCOMP | char | Company code |
| CMMTD$ | numeric | Month-to-date sales |
| CMPPAY | char | Pre-pay flag |

**AR summary (28,741 customers):**
- 5,568 customers with AR balance
- **$10,719,195.86** total owed to distributor
- **$427,907.36** in credits/overpayments
- **Net AR: $10,291,288.50**

**Payment terms distribution:**

| Code | Customers | Likely Meaning |
|------|-----------|---------------|
| 1 | 10,998 | COD |
| F | 6,201 | Fintech/Electronic |
| 3 | 4,454 | Net 30 |
| 0 | 2,895 | Prepaid/None |
| E | 1,139 | EDI |
| 2 | 759 | Net 15 |
| 5 | 707 | Net 5? |
| 9 | 670 | Net 90? |
| 8 | 551 | Net 60? |

**Tax code split:** 25,201 non-taxable (N), 3,540 taxable (Y)

**Top AR balances:** Sam's Clubs and Walmart stores ($50K–$91K each), military exchanges ($55K–$90K)

### AR Comments — ARCMNTST (3,857 rows)

Collection and account notes. These are timestamped, user-attributed notes on customer accounts. Recent examples:
- "Active on Fintech 3/12/26"
- "1ST - 3/5/26" (first contact date)
- "TERMS - BEER COD/NA CHARGE"
- "FINTECH ACCT"
- "REP HAS MO" (rep has money order)

This is an active collections workflow — users are logging contacts and status changes daily.

### AR Batch Tasks — AR_BATCH_TASK (125,375 rows)

Batch AR operations posted to GL. Three main batch code categories:

| Prefix | Count | Purpose |
|--------|-------|---------|
| W## | ~68,000 | Weekly settlement batches (warehouses) |
| E## | ~24,000 | EDI payment batches |
| R## | ~15,000 | Regular payment batches |
| F## | ~14,000 | Fintech payment batches |
| I## | ~5,600 | Invoice batches |
| ADJ | 7 | Manual adjustments |

Each batch has: description, GL batch code, transaction date, transaction number, total payments, company, trading partner.

### AR File — ARFILET (0 rows)

Empty in Gulf's instance. Likely an older AR open-item file that's been superseded by BRATTT.CMAR$.

---

## 4. Daily Transactions — DAILYT (30,071,343 rows)

This is the **backbone of VIP's accounting**. Every operational transaction creates DAILYT records that ultimately post to the GL. Date range: **2024-01-01 to 2026-03-14** (2+ years of data).

### Transaction Types

| Type | Recent 30-day Count | Description |
|------|-------------------|-------------|
| 1 | 1,103,276 | **Sales/Invoice** — the primary transaction. Item-level line items from customer invoices |
| 2 | 61,126 | **Credit/Return** — credit memos and product returns |
| 4 | 30,670 | **Delivery/Adjustment** — delivery confirmations, often $0 |
| P | 18,392 | **Payment** — customer payments received |
| 5 | 16,925 | **Deposit/Fee** — container deposits, delivery fees |
| E | 8,210 | **EDI** — electronic data interchange transactions |
| 3 | 63 | **Adjustment** — manual GL adjustments (rare) |

### Key Columns (selected from 130+ columns)

**Transaction identity:**
- DATYPE — transaction type (1/2/3/4/5/E/P)
- DAIDAT — invoice date (YYYYMMDD)
- DAINV# — invoice number
- DAACCT — customer account code
- DALIN# — line number within invoice

**Product/quantity:**
- DAITEM — item code
- DAQTY — quantity (cases)
- DAUNIT — units
- DABRAN — brand code
- DASUPP — supplier code
- DASIZE — size code
- DAPCLS — product class

**Pricing/dollars:**
- DAPRIC — unit price
- DADAMT — dollar amount (extended price)
- DAFLPR — front-line price
- DASSP — suggested selling price
- DAICOS — item cost (COGS)
- DAPCOS — promotional cost
- DAPOST — posting amount
- DADEPO — deposit amount

**GL integration:**
- DAGLK# — GL key/account number
- DAGLC# — GL company number

**Warehouse/logistics:**
- DAWHSE — warehouse code
- DAWLOC — warehouse location
- DATRK# — truck number
- DALOAD — load number
- DADR# — driver/route number

**Other:**
- DACHN — chain code
- DASDAT — ship date
- DAXDAT — expiration date
- DATXCD — tax code
- DACRID — credit ID (for type 2)
- DAORD# — order number

### How DAILYT Feeds the GL

The flow is: **Operational transaction** → **DAILYT record** → **AR_BATCH_TASK** → **GL posting**

- Each DAILYT record has DAGLK# (GL key) and DAGLC# (GL company) that determine where it posts
- AR_BATCH_TASK groups DAILYT records into batches for GL posting
- The GL batch codes (W, E, R, F, I) reflect the source of the transactions

---

## 5. Tax — FLBEVTAXT (1 row)

Florida beverage tax configuration. Contains beer, wine, and liquor tax rates plus numerous tax set codes (FLISET, FLPSET prefixes). This is state-specific tax configuration for beverage excise taxes.

---

## 6. Bank — BANK_ACCOUNTS (0 rows)

Table exists but is empty for Gulf. Bank info may be stored elsewhere or managed outside VIP.

---

## 7. What Ohanafy Needs to Consider

### What VIP Has That Ohanafy Doesn't (Yet)

1. **Chart of Accounts / GL** — VIP has a full GL with 3,492 accounts across 9 companies. Ohanafy will likely integrate with an external accounting system (QuickBooks, Sage, NetSuite) rather than building its own GL.

2. **Multi-company accounting** — Gulf operates 9 separate legal entities, each with its own set of GL accounts. Ohanafy needs to understand this for any financial reporting or integration.

3. **AP workflow** — Invoice receipt → approval → payment batch → check/EFT → GL posting. VIP handles vendor payments including 1099 tracking, discount terms, and bank routing.

4. **AR lifecycle** — Invoice → aging → collection notes → payment → GL posting. VIP tracks AR balances on the customer master (BRATTT.CMAR$) and has an active collections notes system (ARCMNTST).

5. **Transaction-level GL posting** — Every line item on every invoice has a GL key. VIP's DAILYT table is the bridge between operations and accounting.

6. **Beverage tax engine** — State-specific excise tax calculations for beer, wine, and spirits.

### Migration Implications

| Area | Migration Strategy |
|------|-------------------|
| Chart of Accounts | Export for reference; will be set up in external accounting system |
| Customer AR balances | Already migrated via BRATTT.CMAR$ on Customer records |
| Customer payment terms | Already migrated via BRATTT.CMTERM |
| Vendor payment terms | Already migrated via APVENT.VRDUED/VRDUEC |
| DAILYT history | Too large to migrate (30M rows); export summaries if needed |
| AP open invoices | 140 records — could be exported for transitional reference |
| AR collection notes | 3,857 records — worth migrating as customer notes |
| GL report definitions | Not directly transferable; recreate in new accounting system |
| Tax codes | Simple N/Y flag on customers; already captured |

### Integration Architecture Options

**Option A: Ohanafy + External Accounting (e.g., QuickBooks, Sage)**
- Ohanafy handles operations (orders, inventory, delivery)
- External system handles GL, AP, AR aging, financial reporting
- Integration syncs invoices and payments between systems
- This is the most common pattern for Salesforce-based distribution platforms

**Option B: Ohanafy Builds Lightweight AR/AP**
- AR tracking (balances, aging, payments) within Ohanafy
- AP vendor management within Ohanafy
- GL journal entries exported to external system
- More operational control but more to build

**Option C: Ohanafy Builds Full Accounting**
- Chart of accounts, GL, AR, AP, financial reporting
- Highest complexity, longest timeline
- Only makes sense if accounting is a core differentiator

---

## 8. Reference: All Accounting Tables

| Table | Rows | Category | Description |
|-------|------|----------|-------------|
| GLACCOUNTMASTER | 3,492 | GL | Chart of accounts |
| GLHEADT | 5,359 | GL | Report header definitions |
| GLCOLT | 78 | GL | Report column definitions |
| GLDRPTMT | 4,440 | GL | Report drill-down metadata |
| GLMWRKT | 260 | GL | GL work file (batch processing) |
| GLYEART | 2 | GL | Fiscal years (2025, 2026) |
| GLACCOUNTCATEGORY | 0 | GL | Account categories (unused) |
| GLACCOUNTSUMMARYLASTYEAR | 3,492 | GL | Prior year summary balances |
| GLTRANSACTIONHISTORYTABLE | 0 | GL | Transaction history (unused/purged) |
| GLDRPTHT | 0 | GL | Report drill-down header (unused) |
| APVENT | 5,665 | AP | Vendor master |
| APCHKLT | 11,687 | AP | Check register |
| APPAYMENTBATCH | 3,854 | AP | Payment batches |
| APCURRENTBATCHES | 317 | AP | Current open batches |
| APRC_AT | 140 | AP | Open AP invoices |
| APGLACCOUNTTYPE | 3 | AP | GL account types (PO Accrual, AP Liability, Discounts Taken) |
| APGLDISTRIBUTIONS | 2 | AP | Invoice GL distributions |
| AP_PO_ACCRUAL_ACCOUNTS | 38 | AP | Warehouse PO accrual accounts |
| APBATCHSTATUS | 4 | AP | Batch status codes |
| APRMT | 20 | AP | AP remittance messages |
| APMWT | 15 | AP | AP message work table |
| APWK_BT | 5 | AP | AP work batch |
| APCHECKSTABLE | 0 | AP | Check setup (unused) |
| APINVOICEHISTORYTABLE | 0 | AP | Invoice history (unused/purged) |
| APPAYMENTMETHODTABLE | 0 | AP | Payment methods (unused) |
| APVENDOREMAILTABLE | 987 | AP | Vendor email addresses for AP |
| ARCMNTST | 3,857 | AR | AR collection comments/notes |
| AR_BATCH_TASK | 125,375 | AR | AR batch posting to GL |
| AR_BATCH_AUTO_APPLY_RULE | 1 | AR | Auto-apply rules |
| ARFILET | 0 | AR | AR file (legacy, empty) |
| HDRARRSPT | 9 | AR | AR responsibility codes |
| NOTE_ARBENTRY_JOIN | 1,321,336 | AR | AR batch entry notes junction |
| NOTE_ARTRAN_JOIN | 5 | AR | AR transaction notes junction |
| DAILYT | 30,071,343 | Transactions | All operational transactions |
| DAILYIT_NOTE | 616 | Transactions | Invoice/transaction notes |
| FLBEVTAXT | 1 | Tax | Beverage tax configuration |
| BANK_ACCOUNTS | 0 | Banking | Bank accounts (unused) |
| USERGLCOT | 106 | Security | User GL company permissions |
| USERGLHT | 907 | Security | User GL report permissions |
| ROECARTHT | 7,799 | Other | Route cart headers (returns/empties) |
| ROECARTDT | 1,924 | Other | Route cart details |
| PDAPMTST | 0 | Other | PDA payment status (unused) |
| VARRPTHT | 1 | Other | Variance report header |
| SAMPLE_ORDER_ACCOUNTS | 58 | Other | Sample/donation accounts |
