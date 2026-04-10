# VIP to Ohanafy Integration -- Agent Handoff

**Version:** 1.0
**Date:** 2026-04-09
**Status:** Draft / Pending Signoff

---

## 1. Objective

Build a daily automated integration that ingests 9 VIP beverage distribution data files, transforms them to the Ohanafy data model, and loads them into a Salesforce org via Tray.io.

- **Source:** 9 VIP `.gz` CSV files delivered daily via SFTP
- **Target:** Ohanafy Salesforce org (14 target objects across `ohfy` namespace)
- **Platform:** Tray.io
- **Cadence:** Daily, automated
- **Scope:** Each Ohanafy org belongs to one distributor. The pipeline filters VIP data by distributor ID to load only the relevant records.

---

## 2. Source Data: 9 VIP File Types

VIP delivers 9 gzipped CSV files per business day. Filename format: `{TYPE}.N{YYYYMMDD}.gz`

| # | File | Description | Columns | Rows (typical) | Grain |
|---|------|-------------|---------|----------------|-------|
| 1 | SRSCHAIN | Chain/account group reference | 3 | 6,633 | One row per chain |
| 2 | SRSVALUE | Code/enum lookup values | 5 | 177 | One row per code value |
| 3 | ITM2DA | Supplier item master (extended) | 66 | 65 | One row per supplier SKU |
| 4 | DISTDA | Distributor master | 27 | 13 | One row per distributor |
| 5 | ITMDA | Distributor-to-item mapping | 17 | 102 | One row per distributor + item |
| 6 | OUTDA | Outlet/retail account universe | 71 | 36,587 | One row per outlet per distributor |
| 7 | SLSDA | Sales/invoice line items | 25 | 110 | One row per invoice line |
| 8 | INVDA | Inventory transactions | 19 | 656 | One row per item + date + trans type + UOM |
| 9 | CTLDA | Supplier allocations | 8 | 24 | One row per distributor + item + month |

---

## 3. Source File Column Definitions

### 3.1 SRSCHAIN (Chain Reference)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordType | String | `DETAIL` | Always DETAIL for data rows |
| 2 | Chain | String | `0000010305` | 10-digit zero-padded chain ID |
| 3 | Desc | String | `BENS FINE WINE & SPIRITS` | Chain name |

### 3.2 SRSVALUE (Code/Enum Lookup)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordType | String | `DETAIL` | Always DETAIL for data rows |
| 2 | FieldName | String | `ITCTYP` | Code group identifier |
| 3 | FieldDesc | String | `Container Type` | Human-readable code group name |
| 4 | Value | String | `S` | The coded value |
| 5 | ValueDesc | String | `Spirits` | Description for the value |

**Code Groups:** ITCTYP (Container Type), OUTCLS (Class of Trade), INVTRN (Inventory Transaction), OUTETHN (Patron Ethnicity), OUTIND (Industry Volume), OUTLIF (Patron Lifestyle), OUTOCC (Occupation), OUTAGE (Patron Age), OUTPKG (Package Type)

### 3.3 ITM2DA (Supplier Item Master -- 66 columns)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordId | String | `DETAIL` | Row type indicator |
| 2 | SupplierId | String | `ARG` | Supplier code (same for all rows) |
| 3 | Reserved | String | `` | Always empty |
| 4 | SupplierItem | String | `102312102` | Supplier's unique item number (primary key) |
| 5 | Desc | String | `Original Vodka - 6/1L` | Full item description |
| 6 | CaseGTIN | String | `00000000000000` | Case-level barcode (often zeros) |
| 7 | RetailGTIN | String | `00000000000000` | Retail unit barcode (often zeros) |
| 8 | ActivationDate | String | `19331210` | Date item was activated (YYYYMMDD) |
| 9 | DeactivationDate | String | `00000000` | Date item was deactivated (zeros if active) |
| 10 | Units | Integer | `6` | Units per case |
| 11 | SellingUnits | Integer | `6` | Retail selling units per case |
| 12 | Weight | Decimal | `.00` | Case weight |
| 13 | OuncesPCase | Integer | `0` | Ounces per case (use ExtMLpCase instead) |
| 14 | UnitVolumeDesc | String | `1LTR` | Descriptive volume per unit |
| 15 | CasesPPallet1 | Integer | `0` | Cases per pallet (primary config) |
| 16 | CasesPPallet2 | Integer | `6` | Cases per pallet (secondary config) |
| 17 | AlcoholPct | Decimal | `40.0` | Alcohol percentage |
| 18 | PackageCode | String | `102312102` | Package identifier |
| 19 | BrandCode | String | `11083076` | Brand numeric code |
| 20 | BrandDesc | String | `Original Vodka` | Brand name (maps to Item_Line__c) |
| 21 | GeoCode | String | `` | Geographic code (usually empty) |
| 22 | PackageType | String | `BTL` | Package type code |
| 23 | PackageSize | String | `SNGL 1L` | Human-readable package size |
| 24 | Cube | Decimal | `.00` | Cube measurement |
| 25 | LastChgDate | String | `00000000` | Last change date |
| 26 | Status | String | `A` | A=Active, I=Inactive |
| 27 | ContainerType | String | `S` | Container type code (see SRSVALUE ITCTYP) |
| 28 | TerritoryPtr | String | `01` | Territory pointer |
| 29 | GenericCat1 | String | `` | Category level 1 (usually empty) |
| 30 | GenericCat2 | String | `` | Category level 2 (usually empty) |
| 31 | GenericCat3 | String | `Vodka` | Category level 3 (maps to Item_Type__c) |
| 32 | GenericCat4 | String | `` | Category level 4 |
| 33 | GenericCat5 | String | `` | Category level 5 |
| 34 | GenericCat6 | String | `` | Category level 6 |
| 35 | ExtOZpCase | Decimal | `202.884` | Extended ounces per case |
| 36 | ExtMLpCase | Decimal | `6000.000` | Extended milliliters per case |
| 37 | VolofUnit | Decimal | `1.000` | Volume of one unit (in VolUOM) |
| 38 | UnitsPerRtlPkg | Integer | `1` | Units per retail package |
| 39 | VolUOM | String | `LTR` | Volume unit of measure (ML, LTR, OZ) |
| 40 | PackageTypeCode | String | `BTL` | Redundant with PackageType |
| 41 | CodeDateFormat | String | `` | Code date format |
| 42 | SupplementItemDesc | String | `Original Vodka - 6/1L` | Supplemental description |
| 43 | BottleGTIN | String | `00000000000000` | Bottle-level barcode |
| 44 | CodeDateDays | String | `000` | Code date days |
| 45 | CaseWidth | Decimal | `.00` | Case width |
| 46 | CaseHeight | Decimal | `.00` | Case height |
| 47 | CaseLength | Decimal | `.00` | Case length |
| 48 | PackWidth | Decimal | `.00` | Pack width |
| 49 | PackHeight | Decimal | `.00` | Pack height |
| 50 | PackLength | Decimal | `.00` | Pack length |
| 51 | CasesPerTier | Integer | `000` | Cases per pallet tier |
| 52 | Vintage | String | `0000` | Vintage year (N/A for spirits) |
| 53 | SeasonalFlag | String | `N` | Seasonal item flag |
| 54 | MilitaryFlag | String | `C` | Military availability flag |
| 55 | CatgID7 | String | `2` | Category ID level 7 |
| 56 | CatgDesc7 | String | `1 l Bottle` | Category description level 7 |
| 57 | CatgID8 | String | `1` | Category ID level 8 |
| 58 | CatgDesc8 | String | `Original Vodka` | Category description level 8 |
| 59-66 | CatgID9-12 / CatgDesc9-12 | String | `` | Category levels 9-12 (usually empty) |

### 3.4 DISTDA (Distributor Master -- 27 columns)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordId | String | `DETAIL` | Row type indicator |
| 2 | Supplier ID | String | `ARG` | Supplier code |
| 3 | Distributor ID | String | `FL01` | Distributor code (primary key) |
| 4 | Distributor Name | String | `Gold Coast Eagle Distributing Inc.` | Legal name |
| 5 | Street | String | `2150 47th St` | Street address |
| 6 | City | String | `Sarasota` | City |
| 7 | State | String | `FL` | State code |
| 8 | Zip | String | `34234` | ZIP code |
| 9 | Phone | String | `09413557685` | Phone number |
| 10 | Contact 1 Name | String | `Trad Gulbranson` | Primary contact |
| 11 | Contact 1 Email | String | `trad.gulbranson@gceagle.com` | Primary contact email |
| 12 | ParentId | String | `` | Parent distributor ID |
| 13 | Distributor Rep | String | `Aaron.Wells@vtinfo.com` | VIP system rep email |
| 14 | ISV Name | String | `VIP` | Distributor's platform |
| 15 | Distributor Rank | String | `00006` | Rank |
| 16 | Certification Status | String | `Certified` | Certification status |
| 17 | Phase | String | `9` | Implementation phase |
| 18 | Last Audit Month EOM | String | `` | Last audit date |
| 19 | Last Audit User | String | `` | Last auditor |
| 20 | Division Code | String | `0001` | Division code |
| 21 | Division Description | String | `Default` | Division name |
| 22 | Area Code | String | `0001` | Area code |
| 23 | Area Description | String | `Default` | Area name |
| 24 | Market Code | String | `0001` | Market code |
| 25 | Market Description | String | `Default` | Market name |
| 26 | Rep Code | String | `` | Rep code |
| 27 | Rep Description | String | `` | Rep name |

### 3.5 ITMDA (Distributor Item Mapping -- 17 columns)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordType | String | `DETAIL` | Row type indicator |
| 2 | Supplier | String | `ARG` | Supplier code |
| 3 | Distributor | String | `FL01` | Distributor code (filter key) |
| 4 | GLN | String | `` | Global Location Number (usually blank) |
| 5 | SupplierItem | String | `102312102` | Supplier item number (FK to ITM2DA) |
| 6 | DistItem | String | `803698` | Distributor's internal SKU |
| 7 | Description | String | `Ice Pik Vodka 6/1000mL LN` | Distributor's item description |
| 8 | GTIN | String | `00780369881525` | GTIN barcode |
| 9 | Status | String | `A` | A=Active, I=Inactive |
| 10 | Sell | Integer | `0` | Sell indicator |
| 11 | Unit | Integer | `6` | Units per case |
| 12 | CreationDate | String | `20250911` | Date created (YYYYMMDD) |
| 13 | DistItemSize | String | `1000ML` | Distributor's size description |
| 14 | Proof | Decimal | `1.60` | Proof value |
| 15 | Vintage | String | `` | Vintage year |
| 16 | DistItemGTIN | String | `00780369881525` | Distributor item GTIN |
| 17 | Repack | String | `A` | Repack indicator |

### 3.6 OUTDA (Outlet/Account Universe -- 71 columns)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordType | String | `DETAIL` | Row type indicator |
| 2 | DistId | String | `FL01` | Distributor code (filter key) |
| 3 | Reserved | String | ` ` | Reserved field |
| 4 | Account | String | `00015` | Outlet account number |
| 5 | DBA | String | `Suncoast Beverage` | Doing-business-as name |
| 6 | LicName | String | `` | License name (often blank) |
| 7 | Addr1 | String | `4480 Dr MLK Jr Blvd` | Street address line 1 |
| 8 | Addr2 | String | `` | Street address line 2 |
| 9 | City | String | `Ft Myers` | City |
| 10 | State | String | `FL` | State code |
| 11 | Zip9 | String | `33905` | ZIP+4 code |
| 12 | Country | String | `USA` | Country code |
| 13 | Phone | String | `2392239134` | Phone number |
| 14 | Chain | String | `` | Chain ID (FK to SRSCHAIN) |
| 15 | Chain2 | String | `` | Secondary chain ID |
| 16 | ClassOfTrade | String | `06` | Class of trade code (see crosswalk 7.1) |
| 17 | FineWine | String | `` | Fine wine indicator |
| 18 | ChainStatus | String | `I` | C=Chain, I=Independent |
| 19 | Displays | String | `N` | Display indicator |
| 20 | PatronEthnicity | String | `50` | Patron ethnicity code |
| 21 | IndustryVolume | String | `C` | Industry volume indicator |
| 22 | PatronLifeStyle | String | `` | Patron lifestyle code |
| 23 | Occupation | String | `` | Occupation code |
| 24 | PatronAge | String | `02` | Patron age code |
| 25 | PackageType | String | `2` | Package type preference |
| 26 | Wine | String | `` | Wine indicator |
| 27 | Spirit | String | `` | Spirit indicator |
| 28 | Malt | String | `` | Malt indicator |
| 29 | Sell | String | `2` | Sell indicator |
| 30 | Salesman1 | String | `900` | Primary salesman code |
| 31 | Salesman2 | String | `` | Secondary salesman code |
| 32 | Store | String | `` | Store number |
| 33 | Status | String | `A` | A=Active, I=Inactive, O=Out of Business |
| 34-63 | T01-T30 | String | `Y`/`N` | Delivery day flags (30 positions) |
| 64 | TD1 | String | `` | Territory descriptor 1 |
| 65 | TD2 | String | `` | Territory descriptor 2 |
| 66 | VipId | String | `` | VIP identifier |
| 67 | vpMalt | String | `` | VIP malt indicator |
| 68 | Buyer | String | `Catherine Napfel` | Buyer contact name |
| 69 | LicenseType | String | `` | License type |
| 70 | WhseDist | String | `FL01` | Warehouse distributor ID |
| 71 | License | String | `WSL2100120` | ABC license number |

### 3.7 SLSDA (Sales/Invoice Lines -- 25 columns)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RcdType | String | `DETAIL` | Row type indicator |
| 2 | DistId | String | `FL01` | Distributor code (filter key) |
| 3 | Reserved | String | `00205` | Reserved field |
| 4 | InvoiceDate | String | `20260403` | Invoice date (YYYYMMDD) |
| 5 | InvoiceNbr | String | `0699528` | Invoice number |
| 6 | AcctNbr | String | `21159` | Account number (FK to OUTDA) |
| 7 | SuppItem | String | `102312102` | Supplier item (FK to ITM2DA) |
| 8 | Qty | Integer | `15` | Quantity |
| 9 | UOM | String | `C` | Unit of measure: C=Case, B=Bottle |
| 10 | Front | Decimal | `86.00` | List/front price (reference only) |
| 11 | FlUOM | String | `A` | Front line UOM |
| 12 | NetPrice | Decimal | `58.46` | Net price per unit |
| 13 | NetUOM | String | `A` | Net price UOM |
| 14 | FromDate | String | `20260403` | Reporting period start (YYYYMMDD) |
| 15 | ToDate | String | `20260408` | Reporting period end (YYYYMMDD) |
| 16 | VipId | String | `` | VIP identifier |
| 17 | DistItem | String | `803698` | Distributor item number |
| 18 | NetPrice4 | Decimal | `58.4600` | Net price (4 decimal precision) |
| 19 | Deposit | Decimal | `.0000` | Deposit amount |
| 20 | Crv | Decimal | `.0000` | CA redemption value |
| 21 | LocalTax | Decimal | `.0000` | Local tax amount |
| 22 | AdtlChrg | Decimal | `.0000` | Additional charges |
| 23 | SlsRepId | String | `056` | Sales rep code |
| 24 | Repack | String | `A` | Repack indicator |
| 25 | WhseId | String | `FL01` | Warehouse distributor ID |

### 3.8 INVDA (Inventory Transactions -- 19 columns)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordType | String | `DETAIL` | Row type indicator |
| 2 | DistId | String | `FL01` | Distributor code (filter key) |
| 3 | Reserved | String | `` | Reserved field |
| 4 | GLN | String | `0000000000000` | Global Location Number |
| 5 | PostingDate | String | `20260403` | Posting date (YYYYMMDD) |
| 6 | SupplierItem | String | `102312102` | Supplier item (FK to ITM2DA) |
| 7 | TransCode | String | `10` | Transaction code (see crosswalk 7.2) |
| 8 | TransDate | String | `20260403` | Transaction date (YYYYMMDD) |
| 9 | Quantity | Integer | `34` | Quantity |
| 10 | UnitOfMeasure | String | `C` | C=Case, B=Bottle |
| 11 | PurchaseOrder | String | `` | Purchase order number |
| 12 | TransDistName | String | `` | Transfer distributor name |
| 13 | TransState | String | `` | Transfer state |
| 14 | TimeStamp | String | `2026-04-03-20.00.50...` | System timestamp |
| 15 | FromDate | String | `20260403` | Reporting period start |
| 16 | ToDate | String | `20260408` | Reporting period end |
| 17 | DistItem | String | `803698` | Distributor item number |
| 18 | DistItemSts | String | `A` | Distributor item status |
| 19 | Repack | String | `A` | Repack indicator |

### 3.9 CTLDA (Supplier Allocations -- 8 columns)

| # | Column | Type | Example | Description |
|---|--------|------|---------|-------------|
| 1 | RecordType | String | `DETAIL` | Row type indicator |
| 2 | DistId | String | `FL01` | Distributor code (filter key) |
| 3 | Reserved | String | `` | Reserved field |
| 4 | DistName | String | `Gold Coast Eagle Distributing Inc.` | Distributor name (denormalized) |
| 5 | SupplierItem | String | `102312102` | Supplier item (FK to ITM2DA) |
| 6 | Quantity | Integer | `15` | Allocated quantity |
| 7 | UnitOfMeasure | String | `C` | C=Case, B=Bottle |
| 8 | ControlDate | String | `202604` | Effective period (YYYYMM) |

---

## 4. Target Data: 14 Ohanafy Objects

| # | Ohanafy Object | Record Type | Fed By | Purpose |
|---|---------------|-------------|--------|---------|
| 1 | Account | Chain Banner | SRSCHAIN | Parent chain accounts (Publix, Walmart, etc.) |
| 2 | Account | Outlet | OUTDA | Retail locations (bars, stores, restaurants) |
| 3 | Contact | Buyer | OUTDA | Buyer contacts at outlets |
| 4 | Item__c | -- | ITM2DA + ITMDA | Product catalog |
| 5 | Item_Line__c | -- | ITM2DA | Brand groupings |
| 6 | Item_Type__c | -- | ITM2DA | Product categories |
| 7 | Location__c | Warehouse | DISTDA | Distributor warehouse(s) |
| 8 | Invoice__c | -- | SLSDA | Invoice headers |
| 9 | Invoice_Item__c | -- | SLSDA | Invoice line items |
| 10 | Distributor_Placement__c | -- | SLSDA | Depletion/sell-through records |
| 11 | Inventory__c | -- | INVDA | Current stock levels |
| 12 | Inventory_History__c | -- | INVDA | Daily inventory snapshots |
| 13 | Inventory_Adjustment__c | -- | INVDA | Inventory movements |
| 14 | Allocation__c | -- | CTLDA | Monthly supplier allocations |

---

## 5. Complete Field Mappings: VIP to Ohanafy

### 5.1 SRSCHAIN -> Account (Chain Banner)

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| RecordType | `DETAIL` | -- | Skip | Always DETAIL |
| Chain | `0000010305` | Account.`External_ID__c` | Prefix: `CHN:{Chain}` | Upsert key |
| Desc | `BENS FINE WINE & SPIRITS` | Account.`Name` | Title case | |
| -- | -- | Account.`Is_Chain_Banner__c` | Hardcode `true` | |
| -- | -- | Account.`Retail_Type__c` | Hardcode `Chain` | |
| -- | -- | Account.`Is_Active__c` | Hardcode `true` | |
| -- | -- | Account.`Type` | Hardcode `Retail Chain` | |

**Filter:** Skip rows where Chain or Desc is blank.

---

### 5.2 ITM2DA -> Item__c (Supplier Catalog)

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| RecordId | `DETAIL` | -- | Skip | |
| SupplierId | `ARG` | -- | Skip | Same for all rows |
| Reserved | `` | -- | Skip | Always empty |
| SupplierItem | `102312102` | Item__c.`VIP_External_ID__c` | Prefix: `ITM:{SupplierItem}` | Upsert key |
| SupplierItem | `102312102` | Item__c.`Supplier_Number__c` | Direct | |
| Desc | `Original Vodka - 6/1L` | Item__c.`Name` | Direct | |
| CaseGTIN | `00000000000000` | Item__c.`Case_GTIN__c` | Direct | Skip if all zeros |
| RetailGTIN | `00000000000000` | Item__c.`Unit_GTIN__c` | Direct | Skip if all zeros |
| ActivationDate | `19331210` | -- | Not mapped | |
| DeactivationDate | `00000000` | -- | Not mapped | |
| Units | `6` | Item__c.`Units_Per_Case__c` | Integer | |
| SellingUnits | `6` | Item__c.`Retail_Units_Per_Case__c` | Integer | |
| Weight | `.00` | Item__c.`Weight__c` | Decimal | |
| OuncesPCase | `0` | -- | Not mapped | Use ExtMLpCase instead |
| UnitVolumeDesc | `1LTR` | -- | Not mapped | Descriptive only |
| CasesPPallet1 | `0` | Item__c.`Cases_Per_Pallet__c` | Integer | |
| CasesPPallet2 | `6` | -- | Not mapped | Secondary config |
| AlcoholPct | `40.0` | -- | Not mapped | No standard field; custom if needed |
| PackageCode | `102312102` | -- | Not mapped | |
| BrandCode | `11083076` | -- | Not mapped | Use BrandDesc instead |
| BrandDesc | `Original Vodka` | Item_Line__c (lookup) | Lookup/create by name | Create Item_Line if missing |
| GeoCode | `` | -- | Not mapped | Always empty |
| PackageType | `BTL` | Item__c.`Package_Type__c` | `BTL` -> `Packaged` | |
| PackageSize | `SNGL 1L` | Item__c.`Packaging_Type__c` | Direct | |
| Cube | `.00` | -- | Not mapped | |
| LastChgDate | `00000000` | -- | Not mapped | |
| Status | `A` | Item__c.`Is_Active__c` | `A` -> true, `I` -> false | |
| ContainerType | `S` | Item__c.`Type__c` | `S` -> `Finished Good` | See SRSVALUE ITCTYP |
| TerritoryPtr | `01` | -- | Not mapped | |
| GenericCat1-2 | `` | -- | Not mapped | |
| GenericCat3 | `Vodka` | Item_Type__c (lookup) | Lookup/create by name | Create Item_Type if missing |
| GenericCat4-6 | `` | -- | Not mapped | |
| ExtOZpCase | `202.884` | -- | Not mapped | |
| ExtMLpCase | `6000.000` | -- | Not mapped | Reference only |
| VolofUnit | `1.000` | Item__c.`UOM_In_Fluid_Ounces__c` | ML: `value * 0.033814` | Convert to fl oz |
| UnitsPerRtlPkg | `1` | -- | Not mapped | |
| VolUOM | `LTR` | Item__c.`UOM__c` | `ML`/`LTR` -> `Metric Volume`, `OZ` -> `US Volume` | |
| PackageTypeCode | `BTL` | -- | Not mapped | Redundant with PackageType |
| CodeDateFormat | `` | -- | Not mapped | |
| SupplementItemDesc | `Original Vodka - 6/1L` | -- | Not mapped | Same as Desc |
| BottleGTIN | `00000000000000` | -- | Not mapped | Often all zeros |
| CodeDateDays-CasesPerTier | *(various)* | -- | Not mapped | Dimensional/logistical data |
| Vintage | `0000` | -- | Not mapped | N/A for spirits |
| SeasonalFlag | `N` | -- | Not mapped | |
| MilitaryFlag | `C` | -- | Not mapped | |
| CatgID7-12 / CatgDesc7-12 | *(various)* | -- | Not mapped | Category hierarchy |

**Filter:** Skip row where SupplierItem = `XXXXXX` (zero-volume placeholder).

---

### 5.3 DISTDA -> Location__c (Distributor Warehouse)

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| RecordId | `DETAIL` | -- | Skip | |
| Supplier ID | `ARG` | -- | Skip | |
| Distributor ID | `FL01` | Location__c.`Location_Code__c` | Prefix: `LOC:{DistributorID}` | Upsert key |
| Distributor Name | `Gold Coast Eagle Distributing Inc.` | Location__c.`Name` | Direct | |
| Street | `2150 47th St` | Location__c.`Location_Street__c` | Direct | |
| City | `Sarasota` | Location__c.`Location_City__c` | Direct | |
| State | `FL` | Location__c.`Location_State__c` | Direct | |
| Zip | `34234` | Location__c.`Location_Postal_Code__c` | Direct | |
| Phone-Rep Description | *(various)* | -- | Not mapped | Admin/system info |
| -- | -- | Location__c.`Location_Type__c` | Hardcode `Warehouse` | |
| -- | -- | Location__c.`Is_Active__c` | Hardcode `true` | |
| -- | -- | Location__c.`Is_Sellable__c` | Hardcode `true` | |
| -- | -- | Location__c.`Is_Finished_Good__c` | Hardcode `true` | |

**Filter:** Only load the row matching the target distributor ID.

---

### 5.4 ITMDA -> Item__c (Distributor Enrichment)

Enriches Item records already created from ITM2DA. Upserts on the same `VIP_External_ID__c`.

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| RecordType | `DETAIL` | -- | Skip | |
| Supplier | `ARG` | -- | Skip | |
| Distributor | `FL01` | -- | Filter only | Must match target dist |
| GLN | `` | -- | Not mapped | Usually blank |
| SupplierItem | `102312102` | Item__c.`VIP_External_ID__c` | Prefix: `ITM:{SupplierItem}` | Match key (same as ITM2DA) |
| DistItem | `803698` | Item__c.`Item_Number__c` | Direct | Distributor's own SKU |
| DistItem | `803698` | Item__c.`SKU_Number__c` | Direct | Same value |
| Description | `Ice Pik Vodka 6/1000mL LN` | Item__c.`Short_Name__c` | Direct | Does NOT overwrite Name |
| GTIN | `00780369881525` | Item__c.`UPC__c` | Direct | |
| Status | `A` | -- | Not mapped | Already set from ITM2DA |
| Sell-Unit | *(various)* | -- | Not mapped | Already set from ITM2DA |
| CreationDate | `20250911` | -- | Not mapped | |
| DistItemSize | `1000ML` | -- | Not mapped | Already set from ITM2DA |
| Proof-Vintage | *(various)* | -- | Not mapped | |
| DistItemGTIN | `00780369881525` | Item__c.`Unit_UPC__c` | Direct | |
| Repack | `A` | -- | Not mapped | Informational |

**Filter:** Only load rows for the target distributor. Log orphans where SupplierItem has no matching ITM2DA record.

---

### 5.5 OUTDA -> Account (Outlets) + Contact (Buyers)

#### 5.5a Account Mapping

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| DistId | `FL01` | -- | Filter only | Must match target dist |
| Account | `00015` | Account.`External_ID__c` | Prefix: `ACT:{DistId}:{Account}` | Upsert key |
| Account | `00015` | Account.`Customer_Number__c` | Direct | |
| DBA | `Suncoast Beverage` | Account.`Name` | Direct | |
| LicName | `` | Account.`Legal_Name__c` | Direct | Often blank |
| Addr1 | `4480 Dr MLK Jr Blvd` | Account.`BillingStreet` | Direct | |
| Addr2 | `` | -- | Append to BillingStreet | If not blank |
| City | `Ft Myers` | Account.`BillingCity` | Direct | |
| State | `FL` | Account.`BillingState` | Direct | |
| Zip9 | `33905` | Account.`BillingPostalCode` | Direct | |
| Country | `USA` | Account.`BillingCountry` | Default `US` if blank | |
| Phone | `2392239134` | Account.`Phone` | Format `XXX-XXX-XXXX` | |
| Chain | `` | Account.`Chain_Banner__c` | Lookup: `CHN:{Chain}` | Blank if no chain |
| ClassOfTrade | `06` | Account.`Market__c` | Crosswalk (Section 7.1) | |
| ClassOfTrade | `06` | Account.`Premise_Type__c` | Derived: 01-19=Off, 21-43=On | |
| ChainStatus | `I` | Account.`Retail_Type__c` | `C`->`Chain`, `I`->`Independent` | |
| Salesman1 | `900` | Account.`Sales_Rep__c` | Lookup User by rep code | Requires mapping table |
| Store | `` | Account.`Store_Number__c` | Direct | |
| Status | `A` | Account.`Is_Active__c` | `A`->true, `I`/`O`->false | |
| License | `WSL2100120` | Account.`ABC_License_Number__c` | Direct | |

#### 5.5b Contact Mapping (from Buyer field)

Only created when Buyer field is non-blank.

| Derived From | Ohanafy Object.Field | Transform | Notes |
|-------------|---------------------|-----------|-------|
| DistId + Account | Contact.`External_ID__c` | `CON:{DistId}:{Account}` | Upsert key |
| Buyer (first word) | Contact.`FirstName` | Split on space | |
| Buyer (remaining) | Contact.`LastName` | Split on space | |
| DistId + Account | Contact.`AccountId` | Lookup `ACT:{DistId}:{Account}` | Parent account |
| -- | Contact.`Is_Billing_Contact__c` | Hardcode `true` | |

**Filter:** Skip `SRS99` (non-retail placeholder). Skip blank DBA rows.

---

### 5.6 SLSDA -> Invoice__c + Invoice_Item__c + Distributor_Placement__c

#### Pre-filter

Drop control records before any mapping:
- `AcctNbr = SRS99`
- `SuppItem = XXXXXX`
- `Qty = 0 AND NetPrice = 0`

#### 5.6a Invoice__c (Header)

Group rows by `{DistId}:{InvoiceNbr}:{InvoiceDate}` to produce one Invoice per group.

| Derived From | Ohanafy Object.Field | Transform | Notes |
|-------------|---------------------|-----------|-------|
| DistId + InvoiceNbr + InvoiceDate | Invoice__c.`Invoice_Number__c` | `INV:{DistId}:{InvoiceNbr}:{InvoiceDate}` | Upsert key |
| InvoiceDate | Invoice__c.`Invoice_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | |
| AcctNbr (first row) | Invoice__c.`Customer__c` | Lookup `ACT:{DistId}:{AcctNbr}` | |
| SlsRepId (first row) | Invoice__c.`Sales_Rep__c` | Lookup User by rep code | Requires mapping table |
| -- | Invoice__c.`Status__c` | Hardcode `Completed` | Historical data |
| Sum(Qty * NetPrice) | Invoice__c.`Grand_Total__c` | Calculate from lines | |
| FromDate | Invoice__c.`VIP_From_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| ToDate | Invoice__c.`VIP_To_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| *(filename)* | Invoice__c.`VIP_File_Date__c` | `N20260408` -> `2026-04-08` | For stale cleanup |

#### 5.6b Invoice_Item__c (Line Items)

One record per SLSDA row after filtering.

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| SuppItem | `102312102` | Invoice_Item__c.`Item__c` | Lookup `ITM:{SuppItem}` | |
| Qty | `15` | Invoice_Item__c.`Case_Quantity__c` | Direct (when UOM=C) | |
| Qty | `6` | Invoice_Item__c.`Unit_Quantity__c` | Direct (when UOM=B) | |
| UOM | `C` | -- | Determines which qty/price field | |
| NetPrice | `58.46` | Invoice_Item__c.`Case_Price__c` | Direct (when UOM=C) | |
| NetPrice | `14.75` | Invoice_Item__c.`Unit_Price__c` | Direct (when UOM=B) | |
| FromDate | `20260403` | Invoice_Item__c.`VIP_From_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| ToDate | `20260408` | Invoice_Item__c.`VIP_To_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| Deposit | `.0000` | Invoice_Fee__c | Only if > 0 | |
| LocalTax | `.0000` | Invoice_Item__c.`Tax__c` | Direct | |
| *(filename)* | -- | Invoice_Item__c.`VIP_File_Date__c` | `N20260408` -> `2026-04-08` | For stale cleanup |
| *(composite)* | -- | Invoice_Item__c.`VIP_External_ID__c` | `INL:{DistId}:{InvoiceNbr}:{AcctNbr}:{SuppItem}:{UOM}` | Upsert key |
| *(composite)* | -- | Invoice_Item__c.`Invoice__c` | Lookup `INV:{DistId}:{InvoiceNbr}:{InvoiceDate}` | Parent invoice |

#### 5.6c Distributor_Placement__c

Same source rows, mapped to the depletion tracking object.

| Derived From | Ohanafy Object.Field | Transform | Notes |
|-------------|---------------------|-----------|-------|
| *(composite)* | `Integration_ID__c` | `DPL:{DistId}:{InvoiceNbr}:{AcctNbr}:{SuppItem}:{UOM}` | Upsert key |
| AcctNbr | `ohanafy__Customer__c` | Lookup `ACT:{DistId}:{AcctNbr}` | |
| SuppItem | `ohanafy__Item__c` | Lookup `ITM:{SuppItem}` | |
| Qty | `ohanafy__Quantity__c` | Direct | Negative = return |
| InvoiceDate | `ohanafy__Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | |
| NetPrice | `Price__c` | Direct | |
| FromDate | `VIP_From_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| ToDate | `VIP_To_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| *(filename)* | `VIP_File_Date__c` | `N20260408` -> `2026-04-08` | For stale cleanup |

**Negative quantities:** Rows with negative Qty are credits/returns. Load with negative quantity. Suffix the Integration_ID with `:NEG` for Distributor_Placement__c.

---

### 5.7 INVDA -> Inventory__c + Inventory_History__c + Inventory_Adjustment__c

#### Pre-processing

VIP sends separate rows for Bottle (B) and Case (C) per item/date/transaction. For Inventory__c, merge into one record with both `Cases_On_Hand` and `Units_On_Hand`.

#### 5.7a Inventory__c (Current Stock) -- TransCode 10 only, latest date

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| DistId | `FL01` | -- | Filter only | |
| SupplierItem | `102312102` | Inventory__c.`VIP_External_ID__c` | `IVT:{DistId}:{SupplierItem}` | Upsert key |
| SupplierItem | `102312102` | Inventory__c.`Item__c` | Lookup `ITM:{SupplierItem}` | MasterDetail |
| DistId | `FL01` | Inventory__c.`Location__c` | Lookup `LOC:{DistId}` | |
| Qty (UOM=C) | `34` | Inventory__c.`Cases_On_Hand__c` | Latest date only | |
| Qty (UOM=B) | `4` | Inventory__c.`Units_On_Hand__c` | Latest date only | |
| -- | -- | Inventory__c.`Is_Active__c` | Hardcode `true` | |

#### 5.7b Inventory_History__c (Daily Snapshots) -- TransCode 10, all dates

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| PostingDate | `20260403` | Inventory_History__c.`Inventory_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | |
| SupplierItem | `102312102` | Inventory_History__c.`Item__c` | Lookup `ITM:{SupplierItem}` | |
| TransCode | `10` | -- | Filter: only load 10 | |
| Quantity | `34` | Inventory_History__c.`Quantity_On_Hand__c` | Direct | |
| FromDate | `20260403` | Inventory_History__c.`VIP_From_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| ToDate | `20260408` | Inventory_History__c.`VIP_To_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| *(filename)* | -- | Inventory_History__c.`VIP_File_Date__c` | `N20260408` -> `2026-04-08` | For stale cleanup |
| *(composite)* | -- | Inventory_History__c.`VIP_External_ID__c` | `IVH:{DistId}:{SupplierItem}:{PostingDate}:{UOM}` | Upsert key |
| *(lookup)* | -- | Inventory_History__c.`Inventory__c` | Lookup `IVT:{DistId}:{SupplierItem}` | Parent inventory |

#### 5.7c Inventory_Adjustment__c (Movements) -- TransCode 20-99

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| DistId | `FL01` | -- | Filter only | |
| SupplierItem | `102312102` | -- | Part of External ID + Item lookup | |
| TransCode | `20` | Inventory_Adjustment__c.`Type__c` | Crosswalk (Section 7.2) | |
| TransCode | `20` | Inventory_Adjustment__c.`Reason__c` | Crosswalk (Section 7.2) | |
| TransDate | `20260403` | Inventory_Adjustment__c.`Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | |
| Quantity | `6` | Inventory_Adjustment__c.`Quantity_Change__c` | Direct | |
| FromDate | `20260403` | Inventory_Adjustment__c.`VIP_From_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| ToDate | `20260408` | Inventory_Adjustment__c.`VIP_To_Date__c` | `YYYYMMDD` -> `YYYY-MM-DD` | For stale cleanup |
| *(filename)* | -- | Inventory_Adjustment__c.`VIP_File_Date__c` | `N20260408` -> `2026-04-08` | For stale cleanup |
| *(composite)* | -- | Inventory_Adjustment__c.`VIP_External_ID__c` | `IVA:{DistId}:{SupplierItem}:{TransCode}:{TransDate}:{UOM}` | Upsert key |
| *(lookup)* | -- | Inventory_Adjustment__c.`Inventory__c` | Lookup `IVT:{DistId}:{SupplierItem}` | Parent inventory |

---

### 5.8 CTLDA -> Allocation__c

| VIP Column | VIP Example | Ohanafy Object.Field | Transform | Notes |
|------------|-------------|---------------------|-----------|-------|
| RecordType | `DETAIL` | -- | Skip | |
| DistId | `FL01` | -- | Filter only | Must match target dist |
| Reserved | `` | -- | Skip | |
| DistName | `Gold Coast Eagle...` | -- | Not mapped | Denormalized |
| SupplierItem | `102312102` | Allocation__c item reference | Lookup `ITM:{SupplierItem}` | |
| Quantity | `15` | Allocation__c quantity | Direct | |
| UnitOfMeasure | `C` | Allocation__c UOM | `B` -> Bottle, `C` -> Case | |
| ControlDate | `202604` | Allocation__c effective period | `YYYYMM` -> `YYYY-MM-01` | First of month |
| *(filename)* | -- | Allocation__c.`VIP_File_Date__c` | `N20260408` -> `2026-04-08` | For stale cleanup |
| *(composite)* | -- | Allocation__c.`VIP_External_ID__c` | `ALC:{DistId}:{SupplierItem}:{ControlDate}:{UOM}` | Upsert key |

---

### 5.9 SRSVALUE -- Not Loaded to Salesforce

SRSVALUE is consumed as a transformation reference, not loaded as records. Its values are embedded in the crosswalk maps defined in Section 7.

---

## 6. External ID Strategy

### Key Format: `{PREFIX}:{components joined by :}`

Keys use only **immutable business identifiers**. No quantities, prices, or names. Same input file always produces the same keys.

| Target Object | Prefix | Key Components | Example |
|--------------|--------|---------------|---------|
| Account (Chain) | `CHN` | Chain | `CHN:0000010305` |
| Account (Outlet) | `ACT` | DistId, Account | `ACT:FL01:00015` |
| Contact | `CON` | DistId, Account | `CON:FL01:00015` |
| Item__c | `ITM` | SupplierItem | `ITM:102312102` |
| Location__c | `LOC` | DistId | `LOC:FL01` |
| Invoice__c | `INV` | DistId, InvoiceNbr, InvoiceDate | `INV:FL01:0699528:20260403` |
| Invoice_Item__c | `INL` | DistId, InvoiceNbr, AcctNbr, SuppItem, UOM | `INL:FL01:0699528:21159:102312102:C` |
| Inventory__c | `IVT` | DistId, SupplierItem | `IVT:FL01:102312102` |
| Inventory_History__c | `IVH` | DistId, SupplierItem, PostingDate, UOM | `IVH:FL01:102312102:20260403:C` |
| Inventory_Adjustment__c | `IVA` | DistId, SupplierItem, TransCode, TransDate, UOM | `IVA:FL01:102312102:20:20260403:C` |
| Allocation__c | `ALC` | DistId, SupplierItem, ControlDate, UOM | `ALC:FL01:102312102:202604:C` |
| Distributor_Placement__c | `DPL` | DistId, InvoiceNbr, AcctNbr, SuppItem, UOM | `DPL:FL01:0699528:21159:102312102:C` |

### Design Principles

- **No mutable data in keys.** Quantities, prices, salesperson names are never included.
- **Prefixed.** Makes keys self-describing and prevents collisions across objects.
- **Colon-delimited.** Underscores appear in VIP data; colons do not.
- **Deterministic.** Same input file always produces the same keys. No timestamps, row numbers, or UUIDs.

### Salesforce External ID Field Assignments

| Object | Field Used | Already Exists? |
|--------|-----------|----------------|
| Account | `External_ID__c` | Yes |
| Contact | `External_ID__c` | Needs verification |
| Item__c | `VIP_External_ID__c` | Yes |
| Location__c | `Location_Code__c` | Yes |
| Invoice__c | `Invoice_Number__c` | Yes |
| Invoice_Item__c | `VIP_External_ID__c` | **New** |
| Inventory__c | `VIP_External_ID__c` | **New** |
| Inventory_History__c | `VIP_External_ID__c` | **New** |
| Inventory_Adjustment__c | `VIP_External_ID__c` | **New** |
| Allocation__c | `VIP_External_ID__c` | **New** |
| Distributor_Placement__c | `Integration_ID__c` | Yes |

---

## 7. Value Crosswalks

### 7.1 Class of Trade (OUTDA.ClassOfTrade -> Account.Market__c + Account.Premise_Type__c)

| VIP Code | VIP Description | Ohanafy Market | Premise Type |
|----------|----------------|----------------|-------------|
| 01 | Convenience/Gas | Convenience Store | Off Premise |
| 02 | Drug Store | Drug Store | Off Premise |
| 03 | Liquor/Package Store | Liquor Store | Off Premise |
| 04 | Military Off-Premise | Military | Off Premise |
| 05 | Small Grocery Store | Grocery Store | Off Premise |
| 06 | Non-Retail | Non-Retail | *(none)* |
| 07 | Sub-Distributor | Distributor | *(none)* |
| 08 | Mass Merch/Supercenter | Mass Merchant | Off Premise |
| 09 | Supermarket | Grocery Store | Off Premise |
| 10 | Wholesale Club | Wholesale Club | Off Premise |
| 11 | Fine Wine Store | Fine Wine Store | Off Premise |
| 12 | State Liquor Store | State Liquor Store | Off Premise |
| 13 | General Merchandise | General Merchandise | Off Premise |
| 14 | Retail-Specialty Services | Retail Specialty | Off Premise |
| 15 | E-Commerce | E-Commerce | Off Premise |
| 16 | Dollar Store | Dollar Store | Off Premise |
| 17 | CBD/THC Recreational | CBD/THC | Off Premise |
| 18 | CBD/THC Medicinal | CBD/THC | Off Premise |
| 19 | Other Off Premise | Other Off Premise | Off Premise |
| 21 | Adult Entertainment | Adult Entertainment | On Premise |
| 22 | Transportation | Transportation | On Premise |
| 23 | Bar/Tavern | Bar | On Premise |
| 24 | Recreation/Entertainment | Entertainment | On Premise |
| 25 | Casino/Gaming | Casino | On Premise |
| 26 | Concessionaire | Concessionaire | On Premise |
| 27 | Golf/Country Club | Country Club | On Premise |
| 28 | Hotel/Motel | Hotel | On Premise |
| 29 | Military On-Premise | Military | On Premise |
| 30 | Music/Dance Club | Night Club | On Premise |
| 31 | Private Club | Private Club | On Premise |
| 32 | Restaurant | Restaurant | On Premise |
| 33 | Special Event/Temp License | Special Event | On Premise |
| 34 | Sports Bar | Sports Bar | On Premise |
| 35 | Casual Theme Restaurant | Casual Dining | On Premise |
| 36 | Fine Dining/White Tablecloth | Fine Dining | On Premise |
| 37 | School | School | On Premise |
| 38 | Factory/Office | Office | On Premise |
| 39 | Other On Premise | Other On Premise | On Premise |
| 40 | Health/Hospital | Hospital | On Premise |
| 41 | Government/Non-Military | Government | On Premise |
| 42 | Irish Pub | Irish Pub | On Premise |
| 43 | Tasting Room | Tasting Room | On Premise |
| 50 | Direct Distributors | Direct Distributor | *(none)* |
| 99 | Unassigned | Unassigned | *(none)* |

> **Note:** Ohanafy Market values must be validated against the target org's `Account_Sub_Type` global value set. New picklist values may need to be added.

### 7.2 Inventory TransCode (INVDA.TransCode -> Inventory_Adjustment Type + Reason)

| VIP Code | VIP Description | Ohanafy Type__c | Ohanafy Reason__c | Target Object |
|----------|----------------|----------------|-------------------|--------------|
| 10 | Ending Inventory | -- | -- | Inventory__c + Inventory_History__c |
| 11 | Committed Inventory | -- | -- | Inventory_History__c only |
| 12 | Saleable Inventory | -- | -- | Inventory_History__c only |
| 20 | Receipts | Addition | Purchase | Inventory_Adjustment__c |
| 21 | Transfer In | Addition | Transfer | Inventory_Adjustment__c |
| 22 | Transfer Out | Subtraction | Transfer | Inventory_Adjustment__c |
| 30 | Supplier Returns | Subtraction | Return | Inventory_Adjustment__c |
| 40 | Breakage | Subtraction | Breakage | Inventory_Adjustment__c |
| 41 | Samples | Subtraction | Sample | Inventory_Adjustment__c |
| 50 | MTD Receipts | Addition | Purchase | *Skip (overlaps 20)* |
| 51 | MTD Transfers In | Addition | Transfer | *Skip (overlaps 21)* |
| 52 | MTD Transfers Out | Subtraction | Transfer | *Skip (overlaps 22)* |
| 53 | MTD Supplier Returns | Subtraction | Return | *Skip (overlaps 30)* |
| 54 | MTD Breakage | Subtraction | Breakage | *Skip (overlaps 40)* |
| 55 | MTD Samples | Subtraction | Sample | *Skip (overlaps 41)* |
| 59 | MTD Adjustments | Addition | Adjustment | *Skip (MTD aggregate)* |
| 70 | On Order | -- | -- | *Skip (future state)* |
| 80 | In Bond | -- | -- | *Skip (future state)* |
| 99 | Misc Adjustments | Addition | Adjustment | Inventory_Adjustment__c |

### 7.3 Chain Status (OUTDA.ChainStatus -> Account.Retail_Type__c)

| VIP Value | Ohanafy Value |
|-----------|--------------|
| `C` | `Chain` |
| `I` | `Independent` |
| *(blank)* | `Independent` |

### 7.4 Item Status (ITM2DA.Status -> Item__c.Is_Active__c)

| VIP Value | Ohanafy Value |
|-----------|--------------|
| `A` | `true` |
| `I` | `false` |

### 7.5 Outlet Status (OUTDA.Status -> Account.Is_Active__c)

| VIP Value | VIP Description | Ohanafy Value |
|-----------|----------------|--------------|
| `A` | Active | `true` |
| `I` | Inactive | `false` |
| `O` | Out of Business | `false` |

### 7.6 Container Type (ITM2DA.ContainerType -> Item__c.Type__c)

| VIP Value | VIP Description | Ohanafy Value |
|-----------|----------------|--------------|
| `S` | Spirits | `Finished Good` |
| `W` | Wine | `Finished Good` |
| `P` | Beer Package | `Finished Good` |
| `D` | Beer Draft | `Finished Good` |
| `F` | FMB | `Finished Good` |
| `H` | Seltzer | `Finished Good` |
| `N` | Non-Alcoholic | `Finished Good` |
| *(all others)* | *(various)* | `Finished Good` |

### 7.7 Volume UOM (ITM2DA.VolUOM -> Item__c.UOM__c)

| VIP Value | Ohanafy Value |
|-----------|--------------|
| `ML` | `Metric Volume` |
| `LTR` | `Metric Volume` |
| `OZ` | `US Volume` |

---

## 8. Load Order

Dependencies dictate sequence. Parent/lookup targets must exist before children reference them.

```
Phase 1: Reference Data (no dependencies, run in parallel)
  1a. SRSCHAIN  -> Account (Chain Banners)
  1b. ITM2DA    -> Item_Line__c + Item_Type__c + Item__c
  1c. DISTDA    -> Location__c

Phase 2: Enrichment (depends on Phase 1, run in parallel)
  2a. ITMDA     -> Item__c (enrich with distributor SKUs)
  2b. OUTDA     -> Account (Outlets, links to Chain Banners)
  2c. OUTDA     -> Contact (Buyers, links to Outlet Accounts)

Phase 3: Inventory (depends on Phases 1 + 2)
  3a. INVDA [TransCode 10, latest] -> Inventory__c (current stock)
  3b. INVDA [TransCode 10, all]    -> Inventory_History__c (daily snapshots)
  3c. INVDA [TransCode 20-99]      -> Inventory_Adjustment__c (movements)
  3d. CLEANUP stale inventory records

Phase 4: Transactions (depends on Phases 1 + 2)
  4a. SLSDA     -> Invoice__c (headers)
  4b. SLSDA     -> Invoice_Item__c (line items)
  4c. SLSDA     -> Distributor_Placement__c (depletions)
  4d. CTLDA     -> Allocation__c
  4e. CLEANUP stale sales/allocation records
```

---

## 9. Pipeline Architecture (Tray.io)

### Per File Type: 5-Step Pattern

```
INGEST -> PARSE/VALIDATE -> TRANSFORM -> LOAD -> CLEANUP
```

**Ingest:** SFTP pickup of `.gz` files. Decompress. Split by file type based on filename prefix.

**Parse/Validate:** CSV to row arrays. Filter by target DistId. Drop control records. Validate required fields. Build lookup maps from Salesforce queries.

**Transform:** Apply field mappings. Generate External IDs. Translate coded values via crosswalks. Merge Bottle/Case rows. Classify quantities.

**Load:** Salesforce Composite API bulk upsert, 25 records per batch. Capture success/failure per record.

**Cleanup:** Delete stale records from previous files within the same reporting period. See Section 10.

### Tray.io Connector Stack

| Connector | Usage |
|-----------|-------|
| SFTP | File pickup from VIP delivery |
| Script (JS) | All transformation logic |
| Salesforce | Composite API bulk upsert, SOQL queries for lookup maps |
| HTTP | Health checks, alerting |
| Loop | Batch processing (25-record chunks) |
| Conditional | Route by file type, handle errors |

---

## 10. Stale Record Cleanup

VIP files are overlapping snapshots. Each new file is the **source of truth** for its reporting period. Records that appeared in a previous file but not the current one have been voided or corrected upstream.

### Mechanism

Every record from a VIP file gets stamped with three fields:
- `VIP_File_Date__c` -- date from the filename (e.g., `N20260408` -> `2026-04-08`)
- `VIP_From_Date__c` -- reporting period start
- `VIP_To_Date__c` -- reporting period end

After a successful upsert, delete stale records:

```sql
SELECT Id FROM {Object}
WHERE VIP_File_Date__c < :currentFileDate
  AND VIP_From_Date__c >= :fileFromDate
  AND VIP_To_Date__c <= :fileToDate
  AND {ExternalIdField} LIKE '{PREFIX}:{DistId}:%'
```

Then clean up orphaned Invoice headers:

```sql
SELECT Id FROM Invoice__c
WHERE Invoice_Number__c LIKE 'INV:{DistId}:%'
  AND Id NOT IN (SELECT Invoice__c FROM Invoice_Item__c)
```

### Which Objects Get Cleanup

| Object | Cleanup? | Reason |
|--------|----------|--------|
| Invoice_Item__c | Yes | Voided invoices disappear from next file |
| Invoice__c | Yes | Orphaned headers after line item cleanup |
| Distributor_Placement__c | Yes | Same as Invoice_Item |
| Inventory_History__c | Yes | Snapshot replaced by newer file |
| Inventory_Adjustment__c | Yes | Corrections replace previous |
| Allocation__c | Yes | Allocation changes replace previous |
| Inventory__c | No | Always overwritten via upsert |
| Account | No | Deactivated, not deleted |
| Item__c | No | Deactivated, not deleted |
| Contact | No | Updated, not deleted |
| Location__c | No | Updated, not deleted |

**Safety:** Cleanup is scoped by External ID prefix + DistId + reporting period + file date. Cannot touch records from other distributors, other periods, or manually created records.

---

## 11. New Salesforce Fields Required

### External ID Fields (for upsert)

| Object | Field | Type | Unique | Purpose |
|--------|-------|------|--------|---------|
| Invoice_Item__c | `VIP_External_ID__c` | Text(255) | Yes | Upsert key |
| Inventory__c | `VIP_External_ID__c` | Text(255) | Yes | Upsert key |
| Inventory_History__c | `VIP_External_ID__c` | Text(255) | Yes | Upsert key |
| Inventory_Adjustment__c | `VIP_External_ID__c` | Text(255) | Yes | Upsert key |
| Allocation__c | `VIP_External_ID__c` | Text(255) | Yes | Upsert key |

### Stale Record Cleanup Fields

| Field | Type | Added To |
|-------|------|----------|
| `VIP_File_Date__c` | Date | Invoice__c, Invoice_Item__c, Distributor_Placement__c, Inventory_History__c, Inventory_Adjustment__c, Allocation__c |
| `VIP_From_Date__c` | Date | Same as above |
| `VIP_To_Date__c` | Date | Same as above |

### Other Fields

| Object | Field | Type | Purpose |
|--------|-------|------|---------|
| Account | `Premise_Type__c` | Picklist (On Premise, Off Premise) | May already exist; verify |

---

## 12. Error Handling

### Record Classification

Every row is classified before loading:

| Bucket | Description | Action |
|--------|-------------|--------|
| validRecords | Passed all validation | Upsert to Salesforce |
| invalidRecords | Failed validation (missing required field, bad format) | Log with error reason |
| orphanedRecords | Lookup target not found (missing Account or Item) | Log with missing key |
| skippedRecords | Control records, wrong DistId, placeholders | Count only |

### Validation Rules

| Rule | Applies To | Action |
|------|-----------|--------|
| Required field missing | All | -> invalidRecords |
| Account lookup not found | SLSDA, INVDA | -> orphanedRecords |
| Item lookup not found | SLSDA, INVDA, CTLDA | -> orphanedRecords |
| DistId does not match target | All | -> skippedRecords |
| Control record (SRS99/XXXXXX) | SLSDA, OUTDA | -> skippedRecords |
| Duplicate External ID in batch | All | Aggregate (sum qty) or take latest |
| Salesforce upsert failure | All | Log error type + message, retry once |

### Daily Run Summary

After each run, generate:
- Records loaded per object (created vs. updated)
- Records skipped (with reason counts)
- Records failed (with Salesforce error details)
- Stale records cleaned up per object
- New orphans (items or accounts in VIP but not in Ohanafy)

---

## 13. Open Questions

1. **Distributor_Placement__c vs Invoice_Item__c** -- Load SLSDA to both, or just one? Existing integrations use Distributor_Placement for depletion reporting. The Invoice model gives richer financial data. Recommend both.

2. **MTD inventory codes** -- TransCodes 50-59 are month-to-date aggregates that overlap daily codes 20-41. Loading both would double-count. Recommend skipping MTD.

3. **Historical backfill** -- Sample data covers 11 business days. For a new customer, do we backfill all historical data or start from a cutover date?

4. **Sales Rep mapping** -- VIP provides rep codes (`056`, `SB4`, `SS6`). Ohanafy needs Salesforce User IDs. Requires a manual mapping table per distributor.

5. **Market picklist values** -- The Class of Trade crosswalk (Section 7.1) maps to Market values that may not exist in the target org's `Account_Sub_Type` value set. Need to validate and add missing values.

6. **OUTDA deactivation** -- When Status changes to `O` (out of business), should we deactivate the Account or just update the flag?

---

## 14. ERD Reference

See `docs/erd.png` (or `docs/erd.pdf`) for the full entity relationship diagram showing how VIP source files map to Ohanafy target objects.

Key relationships:
- **DISTDA** (distributor) and **ITM2DA** (item) are the two master hubs
- **ITMDA** bridges supplier items to distributor-specific SKUs
- **OUTDA** outlets link to **SRSCHAIN** chains via Chain_Banner
- **SLSDA** sales link distributors, outlets, and items
- **INVDA** inventory links distributors and items
- **SRSVALUE** decodes every coded field across all files

---

## 15. Companion Files

| File | Purpose |
|------|---------|
| `docs/VIP_INTEGRATION_SPEC.html` | Branded, shareable HTML version with all tabs |
| `docs/VIP_INTEGRATION_SPEC.md` | Original markdown spec |
| `docs/ERD.md` | Mermaid ERD source |
| `docs/erd.mmd` | Mermaid ERD raw file |
| `docs/erd.png` | Rendered ERD image |
| `docs/erd.pdf` | Rendered ERD PDF |
| `docs/SRSCHAIN.md` | SRSCHAIN column reference |
| `docs/SRSVALUE.md` | SRSVALUE column reference |
| `docs/ITM2DA.md` | ITM2DA column reference (66 cols) |
| `docs/DISTDA.md` | DISTDA column reference (27 cols) |
| `docs/ITMDA.md` | ITMDA column reference (17 cols) |
| `docs/OUTDA.md` | OUTDA column reference (71 cols) |
| `docs/SLSDA.md` | SLSDA column reference (25 cols) |
| `docs/INVDA.md` | INVDA column reference (19 cols) |
| `docs/CTLDA.md` | CTLDA column reference (8 cols) |
| `data/` | Sample VIP data files |
| `.ohfy-data-model/` | Ohanafy Salesforce metadata |
| `.integrations/` | Tray.io integration patterns |
