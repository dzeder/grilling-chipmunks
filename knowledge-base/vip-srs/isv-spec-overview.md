# VIP SRS — ISV Interface File Specifications v6.0

Overview of the VIP Supplier Reporting System file format conventions and delivery mechanisms.

**Version:** 6.0
**Last Updated:** January 1, 2023
**Publisher:** Vermont Information Processing, Inc.
**Classification:** Confidential

---

## About the Supplier Reporting System

VIP SRS collects and standardizes beverage distribution data from distributors and delivers it to suppliers. Data types:
- Retail outlets
- Sales
- Inventory
- Products
- Sales people
- Retroactive discounts
- Future sales

**Timing:** Most data is collected daily. Building and transferring files should be efficient. Retroactive discount transactions may be reported more infrequently.

**Automation:** VIP's FTP program can be scheduled to pick up and send files automatically. Direct FTP is also available.

---

## Version History

### Version 3.0 Changes
- **Depletion Warehouse** — Identify which warehouse sales were depleted from (multi-warehouse support)
- **Deposit/CRV/Local Taxes, Additional Charges** — More accurate Price Promotion Reimbursement
- **Total Sales** — Expanded decimal precision for pricing. Net price recalculated when item is repacked (see Appendix E)
- **Distributor Sales Rep Information** — Sales reps at transaction level, org hierarchy
- **Items** — Multiple vintages, retail UPC/GTIN, misclassification identification
- **Stores** — GLN collection, store contact info

### Version 5.1 Changes
- **Distributor Discount ID** — Links discounts to distributor's system
- **Price Support** — Distributor's calculated price support (on-invoice + depletion allowance + supplier offset)
- **Other Charges** — Charges excluded from reported price (local taxes, split case charges)
- **Other Pricing References** — Transaction classification (sale, sample, breakage, combo, free good, EDLP, quantity discount)
- **Retroactive Discounts** — New file for cumulative discounts (CQD — Chain Quantity Discounts)

### Version 6.0 Changes
- About file versions and changes to previous version requirements
- Process for implementation updates

---

## File Format

All VIP SRS files follow these conventions:

- **Encoding:** ASCII
- **Format:** Delimited (comma-separated), variable-length fields
- **Text fields:** Surrounded by double quotes
- **Record types:** HEADER, DETAIL, FOOTER (every file has all three)
- **Max field width:** Defined per field in the spec

### Data Types

| Code | Type | Description |
|------|------|-------------|
| A | Alphanumeric | Any valid ASCII character. Surrounded by quotes. |
| N | Numeric | Numbers only. Can contain decimals. Notation: `5.2` means 5-digit field with 2 decimal places (e.g., `123.45`). |
| S | Signed | Numbers only. Can contain decimals and a minus sign. |
| Z | Date/Timestamp | Format: `YYYY-MM-DD-HH.MM.SS.XXXXXX` (e.g., `2018-02-05-01.47.21.125456`). |

### Required Fields

When a field is marked Required=Y, the system checks for valid values. If the field exists in the system, the existing value should be mapped directly or via SRS cross-reference. If the field does not exist and the specification provides no default:
- **Numeric fields:** Populate with 0, right-justify, pad with zeros
- **Alphanumeric fields:** Leave blank

---

## Record Structure

Every VIP file has three record types:

### Header Record
| Field | Description |
|-------|-------------|
| RECORDTYPE | `HEADER` |
| FILENAME | File name identifier |
| FILEDATE | Date of creation (YYYYMMDD) |

### Detail Records
Variable number of data records. Fields vary by file type.

### Footer Record
| Field | Description |
|-------|-------------|
| RECORDTYPE | `FOOTER` |
| FILENAME | File name identifier |
| FILEDATE | Date of creation (YYYYMMDD) |
| TOTREC | Total number of detail records (excludes header and footer) |

The footer's TOTREC should be validated against the actual detail record count.

---

## File Naming Convention

### Standard SRS Files
```
{TYPE}{SUFFIX}.N{MMDDYYYY}
```

| Component | Description | Examples |
|-----------|-------------|----------|
| TYPE | File type prefix | SRSDIST, SRSCHAIN, SRSVALUE |
| SUFFIX | Delivery frequency | DA (daily), WK (weekly), MN (monthly), FX (fixed), NW (new) |
| N | Literal separator | Always `N` |
| MMDDYYYY | File build date | 04082026 |

**Examples:**
- `SRSDIST.N04082026` — Distributor master, built April 8, 2026
- `SLSDA.N04082026` — Daily sales file
- `INVDA.N04082026` — Daily inventory file
- `OUTDA.N04082026` — Daily outlet file
- `SRSCHAIN.N04082026` — Chain reference file

### SFTP File Naming (for direct SFTP put)
```
O{xxxxx}{yyy}.OUT    — Retail outlet
S{xxxxx}{yyy}.SLS    — Sales
I{xxxxx}{yyy}.INV    — Inventory
C{xxxxx}{yyy}.ITM    — Item cross-reference
M{xxxxx}{yyy}.SLM    — Salesperson
```

Where `xxxxx` = 5-character SRS ID code, `yyy` = sequential 3-digit number (001-999, restarts at 001).

---

## SFTP Delivery

### Put Data (supplier → VIP)
- **Server:** sftp.vtinfo.com
- **User ID:** srsftpuser
- **Password:** snddtanow
- **Command:** PUT \<filename\>

### Get Data (VIP → supplier)
- **Server:** sftp.vtinfo.com
- **User ID:** srsftpuser
- **Password:** snddtanow
- **Files:** GET SRSITEM, GET SRSVALUE, GET SRSCHAIN

### Compression
Files are delivered as `.gz` (gzipped). Decompress before processing.

---

## Processing Sequence

Files must be loaded in this order. Parent/reference data before transaction data.

| Seq | Type | Prefix | Name | Load Method |
|-----|------|--------|------|-------------|
| 1 | Master Data | VAL | SRS Valid Values | Add/Update |
| 2 | Master Data | DIST | Supplier Distributor Master | Add/Update |
| 3 | Master Data | ITM2 | Supplier Item Master | Add/Update |
| 4 | Master Data | CHN | SRS Chain | Add/Update |
| 5 | Dist-reported master | OUT | Retail Outlets | Add/Update |
| 6 | Dist-reported txn | SLS | Sales | Drop/Load |
| 7 | Dist-reported txn | ORD | Future Sales (Orders) | Drop/Load |
| 8 | Dist-reported txn | INV | Inventory | Append or Drop/Load |
| 9 | Summarized txn | DEPL | Summary Depletions | Drop/Load |
| 10 | Dist-reported ref | DIC | Distributor Item Cross-Reference | Add/Update |
| 11 | Dist-reported ref | SLM | Distributor Salesperson | Add/Update |
| 12 | Control ref | CAL | Distributor Sales Calendar | Add/Update |
| 13 | Control ref | NON | Non Reporters | Drop/Load |
| 14 | Control | CTL | Sales Control | Drop/Load |
| 15 | Control | CTLS | Depletions Control | Drop/Load |

### Load Methods

- **Add/Update:** Incoming records are matched by key fields. New records are added; existing records are updated. Records NOT in the file are retained.
- **Drop/Load:** All existing records for the distributor are deleted and replaced with the incoming file. The file represents the complete current state.
- **Append:** New records are added to existing data (used for timestamp-based inventory extracts).

---

## ISV Vendor Codes (Appendix A)

Each Independent Software Vendor has a unique 4-character code assigned by VIP.

| ISV ID | ISV Name |
|--------|----------|
| 0147 | APPRISE SOFTWARE |
| 0075 | BDC |
| 0036 | CAM |
| 0019 | DPS |
| 0085 | EOSTAR |
| 0023 | IU - AWARD |
| 0007 | IU - BSI |
| 0024 | IU - INSIGHT |
| 0058 | KIRKS CONSULTING |
| 0027 | LINK |
| 0136 | MAS500 |
| 0138 | MAS90 |
| 0003 | PICK |
| 0084 | QUICKBOOKS |
| 0086 | SAP |
| 0154 | SOFTEON |
| 0170 | TECH SYSTEMS |
| 0066 | TURILLE |
| 0038 | TURNKEY |
| 0001 | VIP |
| 0015 | VIP-MV-WIN |

Additional UNIQUE- prefixed codes exist for distributor-specific ISV configurations (ARROW BEER, COKE/CBS, RNDC, JOHNSON BRO, etc.).

---

## Data Verification

VIP provides three verification mechanisms:

1. **Daily Edit Report** — Available on the VIP SRS website after files are created. Shows total outlet records, sales built, and inventory quantity by supplier.

2. **History Balancing/Self Audit** — Compare to VIP SRS website monthly to verify accurate reporting.

3. **Data Validation Files:**
   - **Item** — Contains all valid item codes for the Sales, Inventory, and Cross-Reference files. Also used for Repack items.
   - **Chains** — All valid chain codes for the Outlet file.
   - **Outlet Attributes** — Valid values for class-of-trade, ethnicity codes, and other outlet attributes.

---

## Submitting History

VIP collects up to two years of daily invoice-level history.

**Monthly Buckets:** If a distributor does not maintain daily invoice-level sales but has unit and dollar sales at the account/item monthly level, VIP converts to a single day's transaction per account/item combination for the period.

**Efficiency:** Files should be built in the minimal amount of time without help of programmers.
