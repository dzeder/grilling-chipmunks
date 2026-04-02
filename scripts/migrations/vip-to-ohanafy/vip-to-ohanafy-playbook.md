# VIP to Ohanafy Migration Playbook

> This document captures everything learned while migrating VIP distributor data to Ohanafy.
> Use it as a reference for every new customer migration.

---

## 1. Product Hierarchy

### Ohanafy Structure (4 levels)

```
Account (Supplier)          ← top-level company
  └── Item_Line__c          ← brand family (e.g., "Coors")
        └── Item_Type__c    ← brand (e.g., "Coors Light")
              └── Item__c   ← SKU (e.g., "Coors Light 12oz Can 24pk")
```

### VIP Structure (3 levels)

```
SUPPLIERT                   ← supplier (e.g., "Molson Coors")
  └── BRANDT                ← brand (e.g., "Coors Light", "Vizzy Hard Seltzer")
        └── ITEMT           ← item/SKU (e.g., "Coors Light 12oz Can 24pk")
```

### The Gap: Brand Family

Ohanafy has 4 levels; VIP has 3. The missing level is **brand family** (Item_Line__c).

VIP has two mechanisms for brand families, but customers may or may not use them:

1. **HDRMBFAMT** ("Mobility Brand Family") — a dedicated table for brand families.
   Check if it exists: `SELECT COUNT(*) FROM staging."HDRMBFAMT"`

2. **BRAND_FAMILY_XREF** — a field on both `BRANDT` and `SUPPLIERT` that groups brands.
   Check if populated: `SELECT COUNT(*) FROM staging."BRANDT" WHERE TRIM("BRAND_FAMILY_XREF") <> ''`

#### Decision Tree

```
Does HDRMBFAMT exist and have data?
├── YES → Use it directly as Item_Line__c source
└── NO
    ├── Is BRAND_FAMILY_XREF populated on BRANDT?
    │   ├── YES → Group brands by BRAND_FAMILY_XREF → Item_Line__c
    │   └── NO
    │       └── Fallback: BRANDT = Item_Line AND Item_Type (1:1)
    │           Each VIP brand becomes both a brand family and a brand.
    │           Customer can consolidate families post-load.
    └── ASK the customer if they maintain brand families anywhere
```

#### Gulf Distributing (reference customer)

- HDRMBFAMT: **does not exist** in their database
- BRAND_FAMILY_XREF: **empty** on all 927 brands and all suppliers
- Result: used the 1:1 fallback

#### Key Tables

| VIP Table | Key Columns | Notes |
|-----------|------------|-------|
| SUPPLIERT | SUPPLIER (2-char PK), SUPPLIER_NAME, AP_VENDOR, BRAND_FAMILY_XREF, DELETE_FLAG | Links to APVENT via AP_VENDOR for address/phone |
| APVENT | VRVEND (numeric PK), VRNAME, VRADD1/2, POSTALCODE, VRPHON, VRFAX, VREMAIL, VRSSTAT | Accounts payable vendor master |
| BRANDT | BRAND (3-char PK), BRAND_NAME, SUPPLIER (FK→SUPPLIERT), BRAND_FAMILY_XREF, PRICE_BOOK_DESCRIPTION, DELETE_FLAG | ~927 brands for Gulf |
| ITEMT | ITEM_CODE (6-char), BRAND_CODE (FK→BRANDT), SUPPLIER_CODE (FK→SUPPLIERT), PACKAGE_DESCRIPTION, all UPCs/GTINs, ABV, weights, dimensions | ~8,743 items for Gulf. 88 columns total. |
| HDRMBFAMT | Standard VIP table, may not exist | "Mobility Brand Family" — the proper brand family table |

#### Mapping: VIP SUPPLIERT + APVENT → Ohanafy Account (Supplier)

| Ohanafy Field | VIP Source |
|--------------|-----------|
| Name | SUPPLIERT.SUPPLIER_NAME or APVENT.VRNAME |
| Legal_Name__c | APVENT.VRNAME |
| Customer_Number__c | SUPPLIERT.SUPPLIER |
| AccountNumber | APVENT.VRVEND |
| Type | "Supplier" (hardcoded) |
| BillingStreet | APVENT.VRADD1 + VRADD2 |
| BillingCity | CITYT.CITYNAME (via APVENT.ID_CITY) |
| BillingState | CITYT.STATE (via APVENT.ID_CITY) |
| BillingPostalCode | APVENT.POSTALCODE |
| Phone | APVENT.VRPHON |
| Fax | APVENT.VRFAX |
| Website | APVENT.VREMAIL |
| Is_Active__c | APVENT.VRSSTAT != 'I' |
| External_ID__c / Key__c | SUPPLIERT.SUPPLIER |
| vipid__c | SUPPLIERT.IDENTITY or APVENT.VRIDENTITY |

#### Mapping: VIP SUPPLIERT → Ohanafy Item_Line__c (Brand Family)

> Gulf uses the 1:1 fallback: each VIP SUPPLIER = one Item_Line (no HDRMBFAMT, no BRAND_FAMILY_XREF)

| Ohanafy Field | VIP Source | Notes |
|--------------|-----------|-------|
| Name | SUPPLIERT.SUPPLIER_NAME | |
| Supplier__c | SUPPLIERT.IDENTITY → Account.External_ID__c | **Critical** — uses relationship column `ohfy__Supplier__r.ohfy__External_ID__c` |
| Key__c | SUPPLIERT.SUPPLIER (2-char code) | |
| Type__c | Derive from dominant ITEMT.PRODUCT_CLASS | Beer/Wine/Spirits/Non-Alcoholic |
| External_ID__c | SUPPLIERT.IDENTITY | |

#### Mapping: VIP BRANDT → Ohanafy Item_Type__c (Brand)

| Ohanafy Field | VIP Source | Notes |
|--------------|-----------|-------|
| Name | BRANDT.BRAND_NAME | |
| Key__c | BRANDT.BRAND | |
| Item_Line__c | BRANDT.SUPPLIER → Item_Line Key__c | |
| Short_Name__c | BRANDT.BRAND | |
| Supplier_Number__c | BRANDT.PRICE_BOOK_DESCRIPTION | |
| Type__c | Derive from ITEMT.PRODUCT_CLASS | |
| Subtype__c | Derive from ITEMT.PRODUCT_CLASS | |
| ABV__c | AVG(ITEMT.ALCOHOL_PERCENT) per brand | 51% coverage — null for brands with no ABV data |
| Packaging_Styles__c | Aggregate CONTAINER_TYPE_CODE per brand | Maps: 710→1/6 Barrel(s), 720→1/4 Barrel(s), 730→1/2 Barrel(s), packaged→Case Equivalent(s) |
| External_ID__c | BRANDT.IDENTITY | |

**Important:** Do NOT hardcode Type__c = "Beer" for all records. VIP has PRODUCT_CLASS and PRODUCT_CODE on ITEMT that distinguish Beer, Wine, Spirits, Non-Alc, etc. Derive the type from the most common PRODUCT_CLASS among items in each brand.

#### Mapping: VIP ITEMT → Ohanafy Item__c (Product/SKU)

| Ohanafy Field | VIP Source | Notes |
|--------------|-----------|-------|
| Name | PACKAGE_DESCRIPTION | |
| Item_Number__c | ITEM_CODE | |
| Item_Type__c | BRAND_CODE → lookup | |
| Item_Line__c | SUPPLIER_CODE → lookup | |
| Package_Type__c | Derived from CONTAINER_TYPE_CODE | Map: CAN→Can, BTL→Bottle, KEG→Keg, etc. |
| Packaging_Type__c | PACKAGE_SIZE | |
| UOM__c | Derived from PRODUCT_CLASS | |
| Units_Per_Case__c | UNITS_CASE | |
| Weight__c | CASE_WEIGHT | |
| Cases_Per_Pallet__c | CASES_KEGS_PER_PALLET | |
| Default_Case_Price__c | SUGGESTED_SELLING_PRICE | |
| Case_UPC__c | CASE_UPC | Format to 12 digits |
| Case_GTIN__c | CASE_GTIN | Format to 14 digits |
| Unit_UPC__c | BOTTLE_UPC | Format to 12 digits |
| Unit_GTIN__c | BOTTLE_GTIN | Format to 14 digits |
| Retailer_UPC__c | RETAIL_UPC | Format to 12 digits |
| Short_Name__c | PACKAGE_SHORT | |
| Is_Active__c | ITEM_STATUS != 'I' | |
| Is_Tax_Exempt__c | TAXABLE_FLAG != 'Y' | Inverted: Y=taxable → FALSE exempt |
| Is_Sold_In_Units__c | SELLABLE_BY_UNIT == 'Y' | |
| Is_Lot_Tracked__c | Logical: TRUE for all Finished Good | Overhead/Merchandise = FALSE |
| Credit_Type__c | Logical: "Damaged,Breakage,Spoilage,Returned" | Only for active Finished Good items |
| External_ID__c / Key__c | ITEM_CODE | |
| VIP_External_ID__c | ITEM_CODE | |

**Note:** ITEMT.ALCOHOL_PERCENT (75% populated) maps to **Item_Type__c.ABV__c** (brand-level average), NOT to a field on Item__c. ITEMT.SUGGESTED_SELLING_PRICE is empty for Gulf — prices come from DPMASTT (pricelist system).

---

## 2. Location Hierarchy

### Ohanafy Structure (up to 6 levels, self-referential)

```
Location__c (Type = Warehouse)
  └── Location__c (Type = Zone)
        └── Location__c (Type = Aisle)
              └── Location__c (Type = Rack)
                    └── Location__c (Type = Shelf)
                          └── Location__c (Type = Bin)
```

`Location__c.Parent_Location__c` is a self-referential lookup. Formula fields auto-calculate `Warehouse__c`, `Location_Hierarchy__c`, and `Location_Number__c` by traversing the parent chain.

Key fields: `Type__c` (picklist), `Location_Code__c`, `Is_Active__c`, `Is_Sellable__c`, `Is_Finished_Good__c`, `Is_Truck__c`, `Is_Dirty_Keg_Location__c`, `Key__c`

### VIP Structure

VIP uses two tables:

1. **HDRWHSET** — warehouse headers (typically 5-15 per distributor)
2. **LOCMAST** — all locations within warehouses (can be 20,000+)

LOCMAST has 3 fields that form the hierarchy:
- `LCWHSE` (5-char) — warehouse code
- `LCAREA` (10-char) — area/zone code (often unused — check per customer)
- `LCLOC` (6-char) — individual location code

#### Deriving Zones from Location Codes

VIP customers typically don't use LCAREA. But the location codes embed hierarchy in their naming:

```
A01     = Section A, Position 01
A0101   = Section A, Position 01, Sub-position 01
C169A   = Section C, Position 169, Level A
D220D   = Section D, Position 220, Level D
```

**Zone derivation rule:** The first character of LCLOC is the aisle/section letter. Group locations by this prefix to create Zone-level Location__c records.

#### Location Descriptions Reveal Storage Types

The `LCDESC` field tells you what kind of location it is:

| LCDESC | Meaning | Ohanafy Relevance |
|--------|---------|-------------------|
| Reserve | Bulk/reserve storage | Is_Sellable = FALSE |
| CaseFlow / CASE FLOW | Case pick flow rack | Is_Sellable = TRUE, Is_Finished_Good = TRUE |
| Rack | Selective rack storage | Is_Sellable = TRUE |
| Crane | Automated crane bay | Notes field |
| HandStack | Manual stack area | Notes field |
| Shelf | Shelf-level pick | Is_Sellable = TRUE |
| Keg Flow | Keg flow storage | Notes field |
| PICK AREA | Active pick location | Is_Sellable = TRUE |
| BACKSTOCK | Backstock/overstock | Is_Finished_Good = TRUE |
| Cooler / COOLER | Temperature-controlled | Notes field |

#### LOCMAST Key Columns

| Column | Type | Description |
|--------|------|-------------|
| LCWHSE | char(5) | Warehouse code (FK → HDRWHSET) |
| LCAREA | char(10) | Area code (often "0" or empty) |
| LCLOC | char(6) | Location code |
| LCDESC | char(20) | Description / storage type |
| LCSTAT | char(1) | Status (Y=active, N=inactive) |
| LCPICK | char(1) | Pickable location (Y/N) |
| LCSTAG | char(1) | Staging location (Y/N) |
| LCAVAIL | char(1) | Available (Y/N) |
| LCPALL | char(1) | Pallet location (Y/N) |
| LCBOND | char(1) | Bonded location (Y/N) |
| LCCAPC | numeric | Capacity in cases |
| LCCAPP | numeric | Capacity in pallets |
| LCLOCSEQ | char(6) | Pick sequence number |
| LCPQTY | numeric | Current quantity (location-level, not item-level) |
| LCXCOR/LCYCOR/LCZCOR | numeric | X/Y/Z coordinates for 3D warehouse mapping |
| LCMIN | numeric | Minimum quantity threshold |
| LCREPL | numeric | Replenishment trigger quantity |
| IDENTITY | bigint | VIP identity |

#### Picking Zones (PICKING_ZONES)

VIP also has a **PICKING_ZONES** table (60 rows for Gulf) that defines operational zones for automated picking. These are NOT the same as location zones — they define pick methods, verification rules, and assignment logic. Relevant fields:

- PICKING_ZONE, ZONE_NAME, ZONE_SHORT_NAME, ZONE_TYPE
- WAREHOUSE (which warehouse this zone belongs to)
- PICKING_METHOD, PICK_VERIFICATION, PREPICK
- UNIT_OF_MEASURE (CS=cases, CB=case/bottle, N=none, HK/QK=kegs)

These may or may not need migration depending on whether Ohanafy supports pick zone configuration.

#### Mapping: 3 Tabs for Locations

**Tab: Parent_Locations (Warehouses)**

| Ohanafy Field | VIP Source |
|--------------|-----------|
| Name | HDRWHSET.WAREHOUSE_NAME |
| Location_Code__c | HDRWHSET.WAREHOUSE |
| Type__c | "Warehouse" |
| Is_Active__c | TRUE (unless DELETE_FLAG = 'Y') |
| Is_Finished_Good__c | TRUE |
| Is_Sellable__c | TRUE |
| Key__c | HDRWHSET.WAREHOUSE |
| vipid__c | HDRWHSET.IDENTITY |

**Tab: Child_Locations (Zones — derived from location code prefix)**

```sql
SELECT DISTINCT
    TRIM("LCWHSE") AS warehouse_code,
    LEFT(TRIM("LCLOC"), 1) AS zone_code
FROM staging."LOCMAST"
WHERE import_is_deleted = false
  AND TRIM("LCLOC") != ''
GROUP BY TRIM("LCWHSE"), LEFT(TRIM("LCLOC"), 1)
ORDER BY warehouse_code, zone_code
```

| Ohanafy Field | VIP Source |
|--------------|-----------|
| Name | "Zone " + zone_code (e.g., "Zone A") |
| Location_Code__c | zone_code |
| Parent_Location__c | Lookup via warehouse_code → Parent Location Key__c |
| Type__c | "Zone" |
| Is_Active__c | TRUE |
| Is_Sellable__c | TRUE |
| Key__c | warehouse_code + "-" + zone_code |

**Tab: Pick_Paths (Bins — individual locations)**

| Ohanafy Field | VIP Source |
|--------------|-----------|
| Name | LCDESC or LCLOC |
| Location_Code__c | LCLOC |
| Parent_Location__c | Lookup via warehouse_code + "-" + LEFT(LCLOC, 1) → Zone Key__c |
| Type__c | "Bin" |
| Is_Active__c | LCSTAT = 'Y' |
| Is_Sellable__c | LCAVAIL = 'Y' AND LCPICK = 'Y' |
| Is_Finished_Good__c | LCAVAIL = 'Y' |
| Is_Dirty_Keg_Location__c | Derive from LCDESC containing "BAD KEGS" or "DIRTY" |
| Key__c | warehouse_code + "-" + LCLOC |
| Notes__c | LCDESC (storage type) |
| vipid__c | IDENTITY |

#### Gulf Distributing Stats

- 10 warehouses
- 22,909 total locations across all warehouses
- WH 9 (Birmingham) is the largest with 5,391 locations
- Most warehouses have 15-25 zone/section letters

---

## 3. Inventory

### The Marriage of Product and Location

In Ohanafy, `Inventory__c` is the junction that connects items to locations:
- **Item__c** (MasterDetail — parent)
- **Location__c** (Lookup)
- **Quantity_On_Hand__c**, **Quantity_Available__c**

One `Inventory__c` record = "this item, at this location, has this quantity."

### VIP Source: INVENT Table

The VIP `INVENT` table is the item-level inventory summary. Key columns:
- IYWHSE (warehouse), IYITEM (item code)
- IYONHA (on-hand quantity)
- IYSTAT (status)

**Warning:** INVENT may be empty for some customers. Gulf Distributing had 0 rows.

When INVENT is empty, check these alternatives:
- Ask the customer for a fresh inventory export
- POLOCT (PO receipt transactions — 126K rows for Gulf) has location-level receipt data
- LOCMAST.LCPQTY has location-level quantities but not item-level

### Inventory Tab (when data available)

| Ohanafy Field | VIP Source |
|--------------|-----------|
| Item__c | IYITEM → Item lookup |
| Location__c | IYWHSE + IYLOC → Location lookup |
| Quantity_On_Hand__c | IYONHA or calculated |
| Is_Active__c | TRUE |
| Key__c | IYWHSE + "-" + IYITEM |

---

## 4. Allocations

### Concept

Allocations = "this customer can get this much of this product." It limits how much of a scarce or controlled product a specific customer can order.

### VIP Source Tables

| Table | Rows (Gulf) | Purpose |
|-------|-------------|---------|
| ALLOCHT | 8,258 | Allocation headers — item + warehouse + total qty + date range |
| ALLOCDT | 25,844 | Allocation detail — individual allocation entries |

#### ALLOCHT Columns

| Column | Type | Description |
|--------|------|-------------|
| AHWHSE | char | Warehouse code |
| AHITEM | char | Item code |
| AHTYPE | char | Allocation type |
| AHDESC | char | Description |
| AHQTYA | numeric | Quantity allocated |
| AHQTYT | numeric | Quantity total |
| AHQTYU | numeric | Quantity units |
| AHSDAT | numeric | Start date |
| AHEDAT | numeric | End date |
| AHIDENTITY | bigint | VIP identity |

#### ALLOCDT Columns

| Column | Type | Description |
|--------|------|-------------|
| ADWHSE | char | Warehouse code |
| ADITEM | char | Item code |
| ADQTYA | numeric | Quantity allocated |
| ADQTYU | numeric | Quantity units |
| ADACAS | char | Account/case reference (often empty) |
| ADUSER | char | User who created |
| ADAID# | numeric | Allocation ID (FK → ALLOCHT) |
| ADIDENTITY | bigint | VIP identity |

### Ohanafy Allocation__c

Maps to Ohanafy's `Allocation__c` object. Detailed mapping TBD — allocations are unique per customer's business rules.

---

## 5. User-Warehouse Permissions

### VIP Source

| Table | Rows (Gulf) | Purpose |
|-------|-------------|---------|
| USERST | 1,970 | User master — employee ID, name, email, title, default warehouse |
| USERWHSET | 1,963 | User ↔ warehouse permissions — which users can access which warehouses |

Permission is binary: a user either has `F` (Full) access to a warehouse or no entry (no access).

### Important Notes

- VIP "users" include real humans AND system accounts (delivery routes like "del rt 703", merchandiser devices like "Merchandiser 5MA", dispatch accounts, etc.)
- Gulf has 1,970 total users, of which 1,063 have warehouse assignments
- Users without assignments may be inactive or administrative

### Tab Format: Pivot Table

**Rows** = users, **Columns** = warehouses, **Values** = TRUE/FALSE

```
| EmpID | First | Last | Title | Email | Default WH | WH 1 | WH 2 | WH 5 | ... |
|-------|-------|------|-------|-------|------------|------|------|------|-----|
| JSMITH| John  | Smith| Sales | j@... | 1          | TRUE | TRUE | FALSE| ... |
```

Source SQL:
```sql
SELECT
    TRIM(u."EMPLOYEEID") AS emp_id,
    TRIM(u."FIRSTNAME") AS first_name,
    TRIM(u."LASTNAME") AS last_name,
    TRIM(u."JOBTITLE") AS title,
    TRIM(u."EMAIL") AS email,
    TRIM(u."DEFAULTWAREHOUSE") AS default_wh,
    u."IDENTITY" AS vip_identity
FROM staging."USERST" u
WHERE u.import_is_deleted = false
ORDER BY u."LASTNAME", u."FIRSTNAME"
```

Then join USERWHSET to pivot warehouse columns:
```sql
SELECT u."IDENTITY", TRIM(uw."WAREHOUSE") AS warehouse, TRIM(uw."PERMISSION") AS perm
FROM staging."USERWHSET" uw
JOIN staging."USERST" u ON uw."ID_USERS" = u."IDENTITY"
WHERE uw.import_is_deleted = false
```

---

## 6. Load Order

Objects must be loaded in dependency order:

| Order | Tab | Depends On | VIP Source |
|-------|-----|-----------|-----------|
| 1 | Suppliers (Account) | — | SUPPLIERT + APVENT |
| 2 | Item_Lines (Brand Family) | Suppliers | HDRMBFAMT or BRANDT (see decision tree) |
| 3 | Item_Types (Brand) | Item_Lines | BRANDT |
| 4 | Parent_Locations (Warehouses) | — | HDRWHSET |
| 5 | Child_Locations (Zones) | Parent_Locations | Derived from LOCMAST |
| 6 | Pick_Paths (Bins) | Child_Locations | LOCMAST |
| 7 | Territories | — | HDRTERRT |
| 8 | Routes | Territories | HDRROUTET |
| 9 | Equipment/Vehicles | Parent_Locations | TRUCKT |
| 10 | Customers (Account) | Routes, Territories | BRATTT + CITYT |
| 11 | Items (Products/SKUs) | Item_Types, Item_Lines | ITEMT |
| 12 | Contacts | Customers | CONTMASTT |
| 13 | Account_Routes | Customers, Routes | BRATTT + HDRROUTET |
| 14 | Pricelists | — | DISCWKSTT |
| 15 | Pricelist_Items | Pricelists, Items | PENDPRICT |
| 16 | Inventory | Items, Locations | INVENT (if available) |
| 17 | Allocations | Items, Customers | ALLOCHT + ALLOCDT |
| 18 | Fees/Deposits | Items | DEPOSITST |
| 19 | User_Warehouse_Permissions | — | USERST + USERWHSET |
| 20 | Promotions | Items, Customers | Post-off tables |

---

## 7. Common Pitfalls

### SQL Issues
- **Numeric columns and TRIM():** VIP stores many codes as numeric. `TRIM()` only works on text. Always `CAST(col AS TEXT)` before trimming numeric columns (e.g., BRATTT.CMONOF, BRATTT.CMCDAY).
- **Quoted identifiers required:** All VIP column names must be double-quoted in SQL because they're uppercase: `staging."TABLENAME"."COLUMNNAME"`.
- **Transaction rollback:** If a query fails, the Postgres transaction is poisoned. Always `conn.rollback()` in the except block before running the next query.
- **import_is_deleted:** Most staging tables have this column for soft deletes. Always filter `WHERE import_is_deleted = false`. But some tables (like SUPPLIERT in some instances) may not have it — check first.

### Data Quality
- **DELETE_FLAG vs import_is_deleted:** VIP has its own soft delete (DELETE_FLAG = 'Y') separate from the import system's import_is_deleted. Filter on both.
- **Empty INVENT:** Don't assume inventory data exists. Check row count first.
- **LCAREA unused:** Most customers don't use the area field. Check before building a 3-level location hierarchy that relies on it.
- **Hardcoded "Beer":** VIP distributors sell beer, wine, spirits, and non-alc. Don't hardcode product types — derive from PRODUCT_CLASS.

### Google Sheets
- **Share with service account:** The target Google Sheet must be shared with the service account email (e.g., `data-service@data-service-489817.iam.gserviceaccount.com`).
- **BrokenPipeError:** Large tabs (20K+ rows like Pick_Paths) can cause upload failures. Use batch writes.
- **Two-row headers:** Row 1 = friendly human name, Row 2 = Ohanafy API name. Data starts on Row 3.

---

## 8. Reference: VIP Database Connection

Credentials are typically provided as a `gulf pg` style file:

```
PGHOST=<hostname>.postgres.database.azure.com
PGPORT=5432
PGDATABASE=<database_name>
PGUSER=<user>
PGPASSWORD=<password>
PGSSLMODE=require
```

There may be two credential sets — one for analytics (read-only, analytics schema) and one for the ohanafy user (staging schema). The staging schema has the raw VIP data.

### Schema Layout
- **staging** — raw VIP tables (309 tables for Gulf). This is where the data lives.
- **analytics** — pre-built views/rollups (accessible to analytics_user_dev)
- Table names are ALL CAPS and match VIP's iSeries naming (e.g., SUPPLIERT, BRANDT, ITEMT, BRATTT)

---

## 9. Salesforce Loading: Lessons Learned

> Everything below was discovered the hard way during the Gulf 5-supplier pilot load (2026-03-16).
> These are Ohanafy-managed-package-specific behaviors that **will** repeat on every new org.

### 9.1 Prerequisite: Managed Package RecordType Visibility

**Problem:** Ohanafy managed package RecordTypes (Finished_Good, Package, Draft, Volume, Weight, etc.) are **not automatically visible** on user profiles — even System Administrator. Attempting to set `RecordTypeId` on any record will fail with:

```
INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY, invalid record type
```

**Fix:** Deploy profile metadata BEFORE any data load. Must use **namespaced DeveloperName** format:

```xml
<!-- /force-app/main/default/profiles/Admin.profile-meta.xml -->
<Profile xmlns="http://soap.sforce.com/2006/04/metadata">
    <recordTypeVisibilities>
        <recordType>ohfy__Item__c.ohfy__Finished_Good</recordType>
        <default>true</default>
        <visible>true</visible>
    </recordTypeVisibilities>
    <recordTypeVisibilities>
        <recordType>ohfy__Item_Type__c.ohfy__Finished_Good</recordType>
        <default>true</default>
        <visible>true</visible>
    </recordTypeVisibilities>
    <recordTypeVisibilities>
        <recordType>ohfy__Transformation_Setting__c.ohfy__Volume</recordType>
        <default>true</default>
        <visible>true</visible>
    </recordTypeVisibilities>
</Profile>
```

**Gotchas:**
- Use `ohfy__Object.ohfy__RTDeveloperName` — NOT `.RTDeveloperName` without namespace
- If setting ALL RecordTypes to `visible=false`, you MUST still specify one as `default=true`
- Deploy via: `sf project deploy start --source-dir force-app --target-org <alias>`

### 9.2 Prerequisite: Transformation Settings

The managed package `setUOMConversions` trigger on Item__c queries `ohfy__Transformation_Setting__c` records during insert. If no matching record exists for the item's Packaging_Type, the trigger throws:

```
FIELD_CUSTOM_VALIDATION_EXCEPTION: No Transformation Setting found for UOM: <type> and Fluid Ounce(s)
```

**Must create one record per Packaging_Type value BEFORE loading Items:**

| Packaging_Type | Equal_To (fl oz) | RecordType | Key__c |
|---|---|---|---|
| Each | 1.0 | Volume | Each__Fluid Ounce(s) |
| Case Equivalent(s) | 288.0 | Volume | Case Equivalent(s)__Fluid Ounce(s) |
| Case - 4x6 - 12oz - Can | 288.0 | Volume | Case - 4x6 - 12oz - Can__Fluid Ounce(s) |
| Case - 6x4 - 16oz - Can | 384.0 | Volume | Case - 6x4 - 16oz - Can__Fluid Ounce(s) |
| Case - 2x12 - 12oz - Can | 288.0 | Volume | Case - 2x12 - 12oz - Can__Fluid Ounce(s) |
| Case - 15x - 19.2oz - Can | 288.0 | Volume | Case - 15x - 19.2oz - Can__Fluid Ounce(s) |
| 1/6 Barrel(s) | 661.0 | Volume | 1/6 Barrel(s)__Fluid Ounce(s) |
| 1/4 Barrel(s) | 992.0 | Volume | 1/4 Barrel(s)__Fluid Ounce(s) |
| 1/2 Barrel(s) | 1984.0 | Volume | 1/2 Barrel(s)__Fluid Ounce(s) |
| Barrel(s) | 3968.0 | Volume | Barrel(s)__Fluid Ounce(s) |

All records need: `ohfy__Type__c = 'Volume'`, `ohfy__Equal_To_UOM__c = 'Fluid Ounce(s)'`, `ohfy__Is_Active__c = true`, and the Volume RecordTypeId.

**New packaging types will need new Transformation Settings.** Inventory all unique Packaging_Type values in each customer's data and create settings for any that don't already exist.

### 9.3 Prerequisite: Dependent Picklist Mappings (Packaging_Type__c)

`ohfy__Packaging_Type__c` on Item__c is a **restricted** picklist controlled by `ohfy__UOM__c`. The Ohanafy package ships with only SOME Packaging_Type values mapped to UOM controlling values. Values that exist in the global value set but have no controlling field mapping will be rejected by Salesforce system validation:

```
INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST: Packaging Type: bad value for restricted picklist field: Case Equivalent(s)
```

**This cannot be bypassed with trigger configuration** — system picklist validation runs BEFORE all triggers in Salesforce's Order of Execution.

**Fix:** Deploy updated field metadata that adds `valueSettings` for missing values:

```xml
<!-- ohfy__Packaging_Type__c.field-meta.xml — add to existing valueSettings -->
<valueSettings>
    <controllingFieldValue>US Volume</controllingFieldValue>
    <valueName>Case Equivalent(s)</valueName>
</valueSettings>
<valueSettings>
    <controllingFieldValue>US Volume</controllingFieldValue>
    <valueName>Case - 2x12 - 12oz - Can</valueName>
</valueSettings>
<valueSettings>
    <controllingFieldValue>US Volume</controllingFieldValue>
    <valueName>Case - 15x - 19.2oz - Can</valueName>
</valueSettings>
```

**Before every customer load:** inventory ALL unique Packaging_Type values, check each one has a `valueSettings` entry for the appropriate UOM, and deploy additions.

### 9.4 Packaging_Type Cannot Be Blank for Finished Goods

Even though `Packaging_Type__c` has `required=false` in field metadata, the managed package trigger enforces it for Finished Good items:

```
FIELD_CUSTOM_VALIDATION_EXCEPTION: Please ensure Stock UOM Sub Type field is set for Finished Goods. Error Code: 003
```

**Every Finished Good Item MUST have a non-blank Packaging_Type that is valid for its UOM.**

### 9.5 Trigger Bypass Pattern

When the managed package trigger blocks data loading despite prerequisites being met (opaque managed code), bypass specific trigger methods via `ohfy__Trigger_Configuration__mdt`:

```xml
<!-- ONLY include Is_Bypassed__c — other managed fields cause deploy errors -->
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <label>Set UOM Conversions</label>
    <protected>false</protected>
    <values>
        <field>ohfy__Is_Bypassed__c</field>
        <value xsi:type="xsd:boolean">true</value>
    </values>
</CustomMetadata>
```

**Critical:** Only include `ohfy__Is_Bypassed__c`. Including managed fields (Method_Name__c, Trigger_Context__c, sObject_Trigger__c) causes `Cannot modify managed object` errors.

**After loading, re-enable the trigger** by deploying with `false`, then mass-update records to trigger the `Before_Update` context.

### 9.6 Key__c Is NOT an ExternalId on Item_Line / Item_Type

`ohfy__Key__c` on Item_Line__c and Item_Type__c has `IsIdLookup: false`. This means:
- Cannot use Bulk API relationship columns (`ohfy__Item_Line__r.ohfy__Key__c`)
- Cannot upsert on Key__c
- **Must** insert parents, query back SF IDs, substitute into child CSVs

`ohfy__External_ID__c` on Item__c **IS** an ExternalId — Items CAN use upsert (idempotent).

`Account.ohfy__External_ID__c` **IS** an ExternalId — Item_Line.Supplier__c CAN use relationship column resolution (`ohfy__Supplier__r.ohfy__External_ID__c`).

### 9.7 Recommended Product Load Sequence

```
1. Deploy profile RecordType visibility (Item__c, Item_Type__c, Transformation_Setting__c)
2. Deploy dependent picklist additions (if new Packaging_Type values needed)
3. Create Transformation_Setting__c records for all Packaging_Type values
4. Bypass Set_UOM_Conversions trigger (if needed)
5. Load Item_Lines (insert via sf data import bulk)
6. Query back Item_Line SF IDs (Key__c → Id)
7. Load Item_Types WITHOUT RecordTypeId (insert via sf data import bulk)
8. Query back Item_Type SF IDs (Key__c → Id)
9. Load Items via upsert on External_ID__c, WITHOUT RecordTypeId
10. Post-load Apex: set RecordTypeId = Finished_Good on Item_Types (batch 200)
11. Re-enable Set_UOM_Conversions trigger
12. Post-load Apex: set RecordTypeId = Finished_Good on Items (batch 500)
    → triggers Update_UOM_Conversions → populates ohfy__UOM_In_Fluid_Ounces__c
13. Validate counts and spot-check lookups
```

**Why no RecordTypeId during bulk load?** Avoids profile visibility issues in Bulk API context. Setting it post-load via Apex runs as the authenticated user with full profile access.

### 9.8 UOM Assignment Rules

| Item Type | ohfy__UOM__c | ohfy__Packaging_Type__c |
|---|---|---|
| Singles (SINGLES/SINGLE in description) | US Count | Each |
| Kegged items (Package_Type = "Kegged") | US Volume | 1/6 Barrel(s) default, or specific barrel size |
| All other packaged items | US Volume | Specific case config, or "Case Equivalent(s)" as catch-all |

### 9.9 Anonymous Apex Batch Sizes

When mass-updating Items via Anonymous Apex (RecordType + trigger processing):
- **200**: safe, fast
- **500**: works, ~2 seconds
- **700**: works
- **>1000**: risky due to trigger SOQL overhead per item — stay below this

### 9.10 Account External_ID Collision — Chain Banners vs Customers vs Suppliers

**Problem:** `ohfy__External_ID__c` on Account is shared across ALL Account record types (Retailer, Chain_Banner, Supplier). VIP assigns numeric codes independently per entity type, so collisions are **guaranteed**:
- Customer #515 = "C & T PACKAGE" (Retailer)
- Chain Banner #515 = "CIVIC CENTER" (Chain_Banner)

Upserting chain banners on `ohfy__External_ID__c` will **silently overwrite** customer records with matching IDs. The Bulk API treats this as an update, changing the Name, RecordTypeId, and all fields — destroying the customer record.

**Fix:** Use **offset External_IDs** for non-customer account types:
- Customers: use VIP customer number as-is (e.g., `515`)
- Chain Banners: offset by 100000 (e.g., `100515`)
- Suppliers: use VIP supplier code (typically non-overlapping, but verify)

**Or** use separate upsert fields per record type if available.

**Recovery if collision happens:**
1. Query all Chain_Banner accounts: `SELECT Id, Name, ohfy__External_ID__c FROM Account WHERE RecordTypeId = '<chain_banner_rt>'`
2. Delete the incorrectly-created chain banners
3. Re-query customers to identify clobbered records (compare against source CSV)
4. Restore clobbered customers by upserting from the original Customers.csv

**This is the single most dangerous operation in the migration.** Always verify External_ID uniqueness across record types before upserting.

### 9.11 Equipment Loading

**Source:** VIP `TRUCKT` table.

**Key differences from other objects:**
1. **No External_ID field.** `ohfy__External_ID__c` does NOT exist on `Equipment__c`. Cannot upsert — must use `sf data import bulk` (insert only).
2. **Required field not in VIP:** `ohfy__Fulfillment_Location__c` (lookup to Location__c) is required but TRUCKT has no warehouse reference. Must assign a default location (e.g., the main warehouse) or derive from route assignments.
3. **Restricted picklist mappings:**

   | VIP Value | Ohanafy Picklist | Ohanafy Value |
   |-----------|-----------------|---------------|
   | Active | Status__c | Operational |
   | Inactive | Status__c | Out of Service |
   | Truck | Type__c | Motorized Vehicle |
   | Trailer | Type__c | Other |

   Check the org's deployed picklist values — they're restricted and org-specific.

4. **Duplicate Names:** TRUCKT can have duplicate names (e.g., multiple "CART #01" entries). Since Name is used as the de facto identifier (no External_ID), append the TRUCKT key to disambiguate: `"CART #01 TRK# 1234"`.

5. **Route-Vehicle linking:** VIP `HDRROUTET` does NOT link routes to trucks. If routes need `ohfy__Vehicle__c` populated, do a post-load fix by matching route Key__c to equipment Key__c (both sourced from TRUCKT codes).

6. **Fulfillment_Location__c is a master-detail (NOT updatable).** You cannot reparent equipment after creation. To fix warehouse assignments: (a) save route→vehicle links, (b) clear Vehicle__c on routes, (c) delete equipment, (d) recreate with correct Fulfillment_Location__c, (e) query new IDs, (f) relink routes.

7. **Deriving warehouse from VIP:** TRUCKT has no warehouse field, but you can infer it: join TRUCKT → HDRROUTET (same key) → BRATTT (customer assignments) → CMWHSE (customer warehouse). Take the dominant warehouse (most customers) per truck. Gulf result: 198/235 trucks matched across 6 warehouses; 37 defaulted to Gulf Mobile.

8. **Route classification for unlinked routes:** Not all routes need vehicles. VIP routes include special-purpose routes (transfers, samples, house/warehouse, swapouts, cart-in-market, seasonal overflow, inventory devices, events, regulated, AL liquor). Classify by name pattern before treating missing vehicles as bugs. Gulf: 211/308 routes had matching trucks, 33 were real delivery routes without truck matches, 64 were special-purpose.

9. **Driver assignment:** Route.Driver__c needs real Salesforce Users. For testing, use generic "Mobile Driver" user. Real user provisioning is a go-live prerequisite (requires SF Platform licenses — Gulf had 14 total). The VIP link is HDRROUTET.DESCRIPTION (driver name text) or BRATTT.CMBSM1 → USERST.EMPLOYEECODE.

### 9.12 Fee Loading

**Source:** VIP `DEPOSITST` table.

**Key issue:** `ohfy__External_ID__c` does NOT exist on `Fee__c`. Like Equipment, must use `sf data import bulk` (insert only, not upsert). This means Fee loads are NOT idempotent — running twice creates duplicates.

**Recommendation:** Query existing fees before loading: `SELECT Name, ohfy__Key__c FROM ohfy__Fee__c`. Use Key__c to check for existing records.

### 9.13 Location RecordTypes and Location_Code

**Problem:** Locations loaded without `RecordTypeId` default to Master record type. The Ohanafy UI and hierarchy formulas expect:
- **Parent_Location** RT (`012WE00000LTeCaYAL` in Gulf) for warehouses
- **Location** RT (`012WE00000LTeCZYA1` in Gulf) for zones/child locations

Also, `ohfy__Location_Code__c` is a **writable text field** (not a formula). If left NULL, the location hierarchy display and formulas that reference it will show blanks.

**Fix pattern:**
1. Query existing locations and their parents
2. Generate a 2-column fix CSV: `Id,RecordTypeId` — set Parent_Location RT on warehouses (records with no parent), Location RT on zones
3. Generate a 2-column fix CSV: `Id,ohfy__Location_Code__c` — populate from VIP warehouse/zone codes
4. Apply both via `sf data update bulk`

### 9.14 Default Case Price — VIP Pricing Join

**Problem:** VIP `ITEMT.SUGGESTED_SELLING_PRICE` is 0.00 for most distributors — they don't use that field. Actual prices live in the VIP pricing subsystem.

**Join pattern to get frontline prices:**
```sql
SELECT i."ITEM_CODE", i."DESCRIPTION", p."FRONTLINEPRICE"
FROM staging."ITEMT" i
JOIN staging."DPMASTT" dp ON CAST(i."ITEM_CODE" AS TEXT) = TRIM(dp."DPITEM")
JOIN staging."DPMAST1T" p ON dp."DPIDENTITY" = p."DPIDENTITY"
WHERE p."FRONTLINEPRICE" > 0
  AND i.import_is_deleted = false
```

**Gotchas:**
- DPMASTT has multiple price codes per item (division-specific). Pick the most common or most recent.
- DPMAST1T.DPIDENTITY is the join key to DPMASTT (not ITEM_CODE directly)
- Some items genuinely have no pricing (kegs, inactive items)
- **Keg pricing:** VIP prices kegs via deposits (DEPOSITST), not product pricing (DPMASTT). Kegs will show $0.00 for `Default_Case_Price__c` — this is correct. The `ohfy__Keg_Deposit__c` field holds the deposit value (~$50). Do NOT try to "fix" keg pricing; $0 is the expected state. Gulf had 125 active kegs at $0.
- Use this to populate `ohfy__Default_Case_Price__c` via a post-load fix CSV

### 9.15 Synthetic Inventory When VIP INVENT Is Empty

VIP's `INVENT` table may have 0 rows — Gulf's was completely empty. Rather than loading all inventory at quantity 1,000 (looks fake), generate **varied synthetic quantities**:

**Pattern:** Hash-based distribution using the item's External_ID:
```python
import hashlib
def synthetic_qty(external_id):
    h = int(hashlib.md5(str(external_id).encode()).hexdigest(), 16)
    # Distribute between 3 and 800 cases
    return (h % 798) + 3
```

This gives deterministic, reproducible, varied quantities that look realistic for demo purposes. Kegs get lower ranges (3-50), cases get higher ranges (50-800).

---

## 10. QA Findings — Missing Data Points

Investigation date: 2026-03-18

### Issues Found and Fixed

| Field | Object | Root Cause | Fix | Status |
|-------|--------|-----------|-----|--------|
| Default Case Price | Item__c | VIP `ITEMT.SUGGESTED_SELLING_PRICE` is 0.00 for all items — Gulf doesn't use this field. Actual prices live in `DPMAST1T.FRONTLINEPRICE` via DPMASTT join (see §9.14). | Applied fix CSV: 838 items updated with real frontline prices. Remaining $0 items are kegs (no price source) or inactive. | **FIXED** |
| Location_Code | Location__c | `Location_Code__c` is a writable text field (not formula). Left NULL during initial load, breaking hierarchy display. | Applied fix CSV: 29 locations updated with VIP warehouse/zone codes. | **FIXED** |
| Location RecordType | Location__c | Loaded without RecordTypeId → all defaulted to Master RT. UI can't distinguish warehouses from zones. | Applied fix CSV: 10 warehouses → Parent_Location RT, 20 zones → Location RT. | **FIXED** |
| Route Vehicles | Route__c | VIP HDRROUTET has no truck link. All 308 routes loaded with blank Vehicle__c. | Applied fix CSV: 211 routes linked to equipment records via Key__c matching. 97 unlinked: 33 real delivery (no truck match), 64 special-purpose (transfers, samples, house, etc.). | **FIXED** |
| Equipment Warehouse | Equipment__c | TRUCKT has no warehouse field. All 235 defaulted to Gulf Mobile. Fulfillment_Location__c is master-detail (not updatable). | Delete-recreate cycle: derived warehouse from TRUCKT→HDRROUTET→BRATTT.CMWHSE. 198/235 mapped (6 warehouses), 37 defaulted to Gulf Mobile. | **FIXED** |
| Route Drivers | Route__c | All 308 routes had integration user as Driver. Real users not provisioned (SF license constraint). | 244 delivery routes → Mobile Driver (generic); 64 special routes → integration user. Real user provisioning deferred to go-live. | **FIXED** |
| Keg Pricing | Item__c | 125 active kegs show $0 Default_Case_Price. | Expected: VIP prices kegs via deposits (DEPOSITST), not DPMASTT. Keg_Deposit__c is populated. No fix needed. | **By Design** |
| Inventory Quantities | Inventory__c | VIP INVENT table is empty (0 rows). All 4,513 records initially loaded with Qty=1000 (placeholder). | Applied fix CSV: varied synthetic quantities (3-800 cases) using hash distribution (see §9.15). | **FIXED** |
| Customer RecordType | Account | 252 customer accounts had NULL RecordTypeId (loaded before RT visibility was set up). | Applied fix CSV: all set to Retailer RT (`012WE00000LTeCWYA1`). | **FIXED** |

### Working Correctly (QA Explanation Needed)

| Field | Object | Explanation |
|-------|--------|-------------|
| Chain Banner | Invoice__c | Formula field: `Customer__r.Chain_Banner__c`. Auto-populates from customer record. 10,077 of 10,078 invoices have it. |
| Parent Location | Location__c | Already in Child_Locations.csv as `ohfy__Parent_Location__c`. Correctly omitted from Parent_Locations (they are root-level). |
| Average Case Cost | Item__c | System-calculated field, recalculated from Inventory Receipt data. Expected to be 0 until IRs are loaded and triggers run. |
| Territory | Territory__c | 10 records loaded (Mobile, Huntsville, Birmingham, etc.). Object only has 3 fields: Name, Is_Active__c, Parent_Territory__c. |

### Gulf Custom Fields — Need Population

These are Gulf-specific custom fields (no `ohfy__` prefix) that exist in the deployed org but are not in the Ohanafy base package. They were missed during initial CSV generation because the scripts only referenced the OHFY-Data_Model source.

**Lesson learned:** Always run `EntityParticle` queries against the actual target org to discover subscriber-added custom fields. The package data model source will miss customer-specific fields.

| Field | API Name | Type | VIP Source | Status |
|-------|----------|------|-----------|--------|
| Supplier Name | `Supplier_Name__c` (Invoice_Item__c) | Text(255) | `DASUPP` → `SUPPLIERT.SUPPLIER_NAME` | **FIXED** — 98,800 records via fix CSV (PR #24) |
| Brand Sub Type | `Brand_Sub_Type__c` (Invoice_Item__c) | Text(255) | Item → Item_Type → Subtype chain | **FIXED** — 75,178 records via fix CSV (PR #24) |
| Amount Paid | `Amount_Paid__c` (Invoice__c) | Currency | = Subtotal (rollup from line items) | **FIXED** — 9,864 invoices via fix CSV (PR #24) |
| Account Sub Type | `Market__c` (Account) | Picklist | VIP `CMMTYP` → `HDRMKTT.DESCRIPTION` → `map_market_type()` | **FIXED** — 22 standard values + "Military" deployed; 47 military customers remapped |

---

## 11. Sandbox-to-Sandbox Migration

> Lessons learned from moving all foundational/master data from Gulf partial-copy sandbox to the Gulf CAM sandbox (2026-03-24). This section is the reusable playbook for any future Ohanafy sandbox-to-sandbox transfer.

### 11.1 When to Use This Pattern

Move data between Ohanafy sandboxes when:
- Standing up a new sandbox for a team member / QA / demo
- Cloning a configured sandbox to a fresh org
- Recovering from a broken sandbox

**Exclude historical/transactional data:** Invoices, Invoice Line Items, Purchase Orders, PO Line Items, Inventory Receipts, IR Line Items. These are high-volume and not needed for most sandbox use cases.

### 11.2 Script Architecture (`migrate_sandbox.py`)

```
migrate_sandbox.py
├── Config: SOURCE_ORG, TARGET_ORG, OUTPUT_DIR, CAM_USER_ID
├── SF helpers: run_sf_query(), run_sf_upsert(), run_sf_import()
├── IdResolver class
│   ├── register_source(name, sf_id, key_value)
│   ├── register_target(name, key_value, sf_id)
│   ├── resolve(name, source_sf_id) → target_sf_id
│   └── source_id_to_key / target_key_to_id dictionaries
├── get_common_fields(sobject, source, target)
│   └── Intersects creatable fields from BOTH orgs via EntityParticle
├── extract_records() — SOQL from source
├── transform_lookups() — swap RecordTypeIds + resolve lookup SF IDs
├── migrate_object() — generic ETL with idempotency check
├── Waves 1-8 in dependency order
└── validate() — compare source vs target counts
```

**Key design decisions:**
- **Source is Salesforce, not PostgreSQL** — extract via SOQL, not database queries
- **Field discovery is dynamic** — `get_common_fields()` queries both orgs and intersects creatable fields, so the script works even when orgs have different package versions
- **ID resolution via business keys** — source SF ID → Key__c/External_ID__c → target SF ID. No hardcoded IDs
- **RecordType mapping via `(SobjectType, DeveloperName)`** — works across orgs regardless of namespace or ID differences

### 11.3 Load Order (8 Waves)

```
Wave 1 — No dependencies
  Territory, Fee, Pricelist, Transformation_Setting

Wave 2 — Accounts (non-customer)
  Supplier, Chain_Banner, Wholesaler, Vendor_Service
  ⚠️ Separate job per record type (External_ID collision risk)

Wave 3 — Locations (self-referencing)
  Parent Locations (warehouses), then Child Locations (zones)

Wave 4 — Equipment + Item Lines
  Equipment (→ Location), Item_Line (→ Account/Supplier)

Wave 5 — Routes + Item Types
  Route (→ Equipment), Item_Type (→ Item_Line)

Wave 6 — Customers + Items
  Customer Accounts (→ Territory, Chain_Banner, Location, Pricelist)
  Items (→ Item_Type, Item_Line)

Wave 7 — Child objects
  Contact, Item_Component, Lot, Inventory, Pricelist_Item, Promotion

Wave 8 — Junction/grandchild objects
  Account_Route, Lot_Inventory
```

### 11.4 Pre-Flight Metadata Deployments (CRITICAL)

**You MUST deploy these BEFORE loading data. Every one of these caused a blocker when missed.**

#### A. Permission Set for Record Type Visibility

The integration user cannot set RecordTypeId unless explicitly granted access. Deploy a `Migration_RecordTypes` permission set.

**Gotcha — namespace prefix rules for RT references:**
```xml
<!-- Managed RTs (NamespacePrefix = ohfy): use ohfy__ prefix on DeveloperName -->
<recordType>ohfy__Transformation_Setting__c.ohfy__Volume</recordType>

<!-- Subscriber-created RTs (NamespacePrefix = null): bare DeveloperName -->
<recordType>ohfy__Item__c.Finished_Good</recordType>
```

**How to determine which format:** Query `SELECT DeveloperName, NamespacePrefix FROM RecordType WHERE SobjectType = 'X'` on the **target** org. If `NamespacePrefix = ohfy`, use `ohfy__DeveloperName`. If `null`, use bare `DeveloperName`.

**Gotcha — some orgs have BOTH managed and subscriber RTs with the same name:**
```
Finished_Good (ns=ohfy, INACTIVE)  ← managed package default
Finished_Good (ns=null, ACTIVE)    ← subscriber-created override
```
The active subscriber RT is what the Bulk API uses. Target your permission set at the **active** one.

#### B. Global Value Set Expansion

The managed package ships with ~38 UOM values in `ohfy__Unit_of_Measurement`. Customer orgs with custom Packaging_Types need ALL custom values added to this global value set.

```bash
# 1. Retrieve current value set from target
sf project retrieve start --metadata "GlobalValueSet:ohfy__Unit_of_Measurement" --target-org <target>

# 2. Query all unique UOM/Packaging_Type values from source
sf data query --query "SELECT ohfy__UOM__c, ohfy__Equal_To_UOM__c FROM ohfy__Transformation_Setting__c" --target-org <source>

# 3. Add missing values to the XML, deploy
sf project deploy start --target-org <target>
```

**Gulf had 130 values (92 custom) — the managed package ships with only 38.**

#### C. Dependent Picklist Mappings (`ohfy__Packaging_Type__c`)

`ohfy__Packaging_Type__c` on `Item__c` is a restricted picklist **controlled by** `ohfy__UOM__c`. Adding values to the global value set makes them available system-wide, but each value also needs a `valueSettings` entry mapping it to its controlling UOM value.

**Diagnostic:** Query `sf sobject describe` and decode the `validFor` base64 bitfield. Any Packaging_Type value with empty `validFor` is unmapped and will be rejected:
```
INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST: bad value for restricted picklist field: Case Equivalent(s)
```

**Fix:** Deploy field metadata with additional `valueSettings`:
```xml
<!-- ohfy__Packaging_Type__c.field-meta.xml -->
<valueSettings>
    <controllingFieldValue>US Volume</controllingFieldValue>
    <valueName>Case Equivalent(s)</valueName>
</valueSettings>
```

**Before every migration:** Retrieve the current field metadata, compare against source values, add any missing `valueSettings`, and deploy.

#### D. Record Type Picklist Restrictions

Even after expanding the global value set and adding dependent mappings, **managed record types may not include new values.** The managed RT's picklist restrictions are baked in and don't auto-update when the global value set changes.

**Fix:** Deploy RT metadata with explicit `picklistValues` listing ALL values:
```xml
<RecordType xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>ohfy__Volume</fullName>
    <active>true</active>
    <label>Volume</label>
    <picklistValues>
        <picklist>ohfy__UOM__c</picklist>
        <values><fullName>Each</fullName><default>false</default></values>
        <values><fullName>Case - 2x12 - 12oz - Can</fullName><default>false</default></values>
        <!-- ... all 130 values ... -->
    </picklistValues>
</RecordType>
```

**Objects that need this:** `Transformation_Setting__c` (Volume + Weight RTs), `Item__c` (Finished_Good RT).

#### E. Trigger Bypass (135 CMT Records)

Deploy subscriber-override `ohfy__Trigger_Configuration__mdt` records with `ohfy__Is_Bypassed__c = true`.

**Known limitation:** The bypass may not fully work. Managed code may read the managed CMT record (ns=ohfy, `Is_Bypassed=false`) instead of the subscriber override (ns=null, `Is_Bypassed=true`). In the Gulf migration, triggers still auto-created child records despite bypass being deployed.

**Implication:** Plan for auto-created record cleanup (see §11.6).

### 11.5 Managed Trigger Side Effects — The #1 Operational Headache

**This is the single biggest complication in sandbox-to-sandbox migration.** Managed triggers auto-create child records when parent records are inserted, and the trigger bypass is unreliable.

| Parent Insert | Auto-Created Children | Approx Ratio |
|---|---|---|
| Item__c | Inventory__c (1 per Item × Location) | ~2.3× items |
| Item__c | Pricelist_Item__c (1 per Item × Pricelist) | ~3.5× items |
| Inventory__c | Lot_Inventory__c (1 per Inventory) | 1:1 |

**For Gulf (1820 Items):** Triggers created 4170 Inventory + 4587 Pricelist_Item + 4513 Lot_Inventory = **13,270 auto-created records** that had to be bulk-deleted and replaced with source data.

**Cleanup pattern:**
```python
# 1. Query all IDs
ids = query("SELECT Id FROM ohfy__Inventory__c", target)

# 2. Write delete CSV with CRLF line endings
with open(path, 'w') as f:
    f.write('Id\r\n' + '\r\n'.join(ids) + '\r\n')

# 3. Bulk delete with CRLF flag
sf data delete bulk --sobject ohfy__Inventory__c --file path \
    --target-org target --wait 10 --line-ending CRLF

# 4. Insert source data
sf data import bulk --sobject ohfy__Inventory__c --file source.csv \
    --target-org target --wait 10 --line-ending CRLF
```

**The delete-then-insert must happen quickly** — if you insert the source data and triggers auto-create duplicates simultaneously, you'll get `FIELD_CUSTOM_VALIDATION_EXCEPTION: Duplicate Record Blocked` errors.

**Recommended Wave 7 order:**
1. Load Contacts, Item_Components, Lots first (no auto-creation issues)
2. Delete all auto-created Inventory and Pricelist_Item
3. Load source Inventory and Pricelist_Item immediately after
4. Delete all auto-created Lot_Inventory
5. Load source Lot_Inventory (Wave 8)

### 11.6 Contact Trigger Bug — Two-Pass Insert

**Bug:** The managed `ContactTrigger` crashes on AfterInsert when both `ohfy__Is_Billing_Contact__c` and `ohfy__Is_Delivery_Contact__c` are `true` on the same record. The trigger adds the parent AccountId to a list twice, causing:

```
System.ListException: Duplicate id in list: 001WE00001BCuBOYA1
```

This happens even on single-record inserts via REST API. It's a managed code bug, not a batch size issue.

**Workaround — two-pass insert:**
```
Pass 1: Insert contacts WITHOUT ohfy__Is_Delivery_Contact__c
Pass 2: Update contacts to SET ohfy__Is_Delivery_Contact__c = true
```

The trigger only crashes when both flags are set during INSERT. Setting the second flag via UPDATE works fine.

### 11.7 Object-Specific Gotchas

| Object | Gotcha | Fix |
|---|---|---|
| Transformation_Setting | `Key__c` is unique but NOT ExternalId — can't upsert | Delete existing + re-insert |
| Lot | Has `ohfy__Supplier__c` (Account lookup) not in most documentation | Add to lookup_config |
| Promotion | No `ohfy__Key__c` field | Use Name or other field for bridge key |
| Contact | No `ohfy__Key__c` — use Email as bridge key | Email is unique enough for migration |
| Account | 1 record may have null `External_ID__c` | Accept as known gap (can't upsert nulls) |
| Pricelist_Item | Master-detail to both Pricelist and Item — needs real SF IDs | Items must load first; resolve via Key__c map |
| Lot_Inventory | Master-detail to both Inventory and Lot | Composite key: Item_Key + Location_Key for Inventory resolution |
| CRLF | `sf data delete bulk` ALSO needs `--line-ending CRLF` on macOS | Always pass the flag for ALL bulk operations |

### 11.8 ID Resolution Strategy

| Object | Bridge Key | Used By |
|---|---|---|
| Territory | Name | Account.Territory__c |
| Fee | Key__c | — |
| Pricelist | Key__c | Account.Pricelist__c, Pricelist_Item.Pricelist__c |
| Location | Key__c | Equipment, Account, Inventory |
| Account | External_ID__c | Contact, Item_Line, Account_Route, chain banner refs |
| Equipment | Key__c | Route.Vehicle__c |
| Item_Line | Key__c | Item_Type.Item_Line__c |
| Item_Type | Key__c | Item.Item_Type__c |
| Route | Key__c | Account_Route.Route__c |
| Item | Key__c | Item_Component, Lot, Inventory, Pricelist_Item |
| Lot | Lot_Identifier__c | Lot_Inventory.Lot__c |
| Inventory | composite (Item_Key\|Location_Key) | Lot_Inventory.Inventory__c |

**Upsert-capable (true ExternalId):** `Account.ohfy__External_ID__c`, `Item.ohfy__External_ID__c`

**Insert-only (Key__c is unique but not ExternalId):** Everything else — must use `sf data import bulk` + post-insert ID query.

### 11.9 User Lookup Fields

All User lookup fields must point to a real user in the target org. Map to a named user (e.g., "Cam Koorangi") rather than the integration user — the integration user's records look wrong in the UI.

| Field | Objects |
|---|---|
| OwnerId | All objects |
| ohfy__Driver__c | Route |
| ohfy__Sales_Rep__c | Account |
| ohfy__Created_By_User__c | Various |
| ohfy__Last_Modified_By_User__c | Various |

**Pattern:** Query target org for the user by name: `SELECT Id FROM User WHERE Name LIKE '%Cam%'`. Set as constant in script config.

### 11.10 Idempotency Design

The script's count-based idempotency ("skip if target >= source") has known limitations:
- **Auto-created records inflate counts** — 4170 auto-created Inventory makes it look "done" when source has 4513
- **Partial loads with errors** — 699/1821 Items loaded, but count check sees 699 < 1821 and re-runs (correct behavior)
- **Upsert objects are naturally idempotent** — Account and Item use upsert on External_ID__c, so re-running is safe

**Future improvement:** Check by Key__c existence rather than raw count.

### 11.11 Validation Checklist

After all waves complete, run this validation:

```
1. Record count comparison (--validate-only flag)
   - All 19 objects should match or have documented gaps

2. Field value spot-check (sample 3 records per object)
   - Query by business key in both orgs, compare field values

3. Lookup integrity (17 relationship checks)
   - For each lookup field, verify the parent's business key matches source

4. Orphan detection (12 null-lookup checks)
   - No child records should have null required lookups

5. Record type verification
   - RT distribution should match source (modulo namespace differences)
```

**Gulf results (2026-03-24):** 0 field mismatches, 0 lookup issues, 0 orphans across 23,588 records.

### 11.12 Pre-Flight Deployment Sequence (Copy-Paste Checklist)

```bash
# 1. Authenticate to target org
sf org login web --alias <target-alias> --instance-url https://test.salesforce.com

# 2. Deploy permission set for RT visibility
#    (generate from RecordType query — see §11.4A)
sf project deploy start --target-org <target>

# 3. Assign permission set to integration user
sf org assign permset --name Migration_RecordTypes --target-org <target>

# 4. Deploy expanded global value set
#    (retrieve from source, add missing values)
sf project deploy start --target-org <target>

# 5. Deploy dependent picklist mappings
#    (retrieve field metadata, add valueSettings)
sf project deploy start --target-org <target>

# 6. Deploy RT picklist expansions
#    (Volume, Weight, Finished_Good with all values)
sf project deploy start --target-org <target>

# 7. Deploy trigger bypass (135 CMT records)
sf project deploy start --target-org <target>

# 8. Run migration
python3 migrate_sandbox.py --source <source> --target <target>

# 9. Clean up auto-created records + re-insert source data
#    (handled by script for Inventory/PLI/Lot_Inventory)

# 10. Validate
python3 migrate_sandbox.py --validate-only

# 11. Re-enable triggers (deploy CMT with Is_Bypassed=false)
sf project deploy start --target-org <target>
```

---

## 12. Appendix: Gulf Distributing Stats

| Metric | Value |
|--------|-------|
| Suppliers | ~200 |
| Brands | 927 |
| Items/SKUs | 8,743 |
| Customers | 28,000+ |
| Warehouses | 10 |
| Locations/Bins | 22,909 |
| Users | 1,970 |
| Picking Zones | 60 |
| Allocation Headers | 8,258 |
| Allocation Details | 25,844 |
| Inventory (INVENT) | 0 (empty) |

---

## 12. Sandbox-to-Sandbox Validation

When migrating the same dataset into a second Salesforce sandbox (e.g., Partial Copy → CAM), you need a systematic way to verify the data landed identically. This section captures the full process and every lesson learned from Gulf's CAM sandbox validation.

### 12.1 Why You Need This

The migration playbook produces CSVs, but the *load process* introduces differences: different org users, different field availability, Bulk API quirks, formula field behavior, and human error in load scripts. You can't assume "same CSV = same data." A field-by-field comparison between orgs is the only way to confirm.

### 12.2 Comparison Script Architecture

The script (`compare_sandboxes.py`) follows this pattern:

1. **Describe both orgs** — intersect field lists so you only compare fields that exist in both
2. **Skip system fields** — Id, OwnerId, CreatedById, timestamps, PhotoUrl, CurrencyIsoCode
3. **Skip ALL formula/calculated fields** — they often contain org-specific SF record IDs (e.g., `Supplier__c`, `Location_Hierarchy_Dev__c`) that always differ between orgs
4. **Resolve reference fields** — don't compare SF record IDs directly. Instead, traverse the relationship and compare the business key (e.g., `Account.ohfy__External_ID__c`, `Route.ohfy__Key__c`, `User.Username`)
5. **Match records by business key** — use `ohfy__Key__c`, `ohfy__External_ID__c`, `Name`, or composite keys (Item Key + Location Key for Inventory)
6. **Separate "known diffs" from "real diffs"** — placeholder user fields differ by design between orgs; don't let them pollute the match rate

**Reference field resolution map (`REF_KEY`):**

| Referenced Object | Resolve Via |
|---|---|
| Account | `ohfy__External_ID__c` |
| RecordType | `DeveloperName` |
| User | `Username` |
| Contact | `Name` |
| All ohfy__ objects with Key__c | `ohfy__Key__c` |
| ohfy__Territory__c | `Name` |
| ohfy__Lot__c | `Name` |
| Group, Inventory, Lot_Inventory | Skip (no stable business key) |

**Composite keys for objects without a single key field:**

| Object | Composite Key |
|---|---|
| Contact | `Account.External_ID__c` + `LastName` + `FirstName` |
| Inventory | `Item.Key__c` + `Location.Key__c` |
| Lot_Inventory | `Lot.Name` + `Inventory.Item.Key__c` + `Inventory.Location.Key__c` |

### 12.3 Known Diff Patterns (Expected, Not Bugs)

These will appear in every sandbox-to-sandbox comparison and should be excluded from the mismatch count:

| Field | Object | Why It Differs |
|---|---|---|
| `ohfy__Driver__c` | Route | Different placeholder/generic users per org |
| `ohfy__Sales_Rep__c` | Account | Different placeholder/generic users per org |
| Any User lookup | Various | Unless you map real VIP users → SF users identically in both orgs, these will always differ |

**Key principle:** User lookup fields will differ between orgs unless the *same* usernames exist in both. During migration, routes and accounts are typically assigned to a generic user (e.g., `integrations@ohanafy.com`). Each sandbox has a different username for this user. Track these separately as "known diffs" so they don't mask real issues.

### 12.4 Bugs Found and Fixed (Gulf CAM Validation)

These are the actual data quality issues discovered by comparing Gulf's Partial Copy and CAM sandboxes. Every one of these would have gone unnoticed without the field-level comparison.

#### 12.4.1 Item_Type Short_Name — Wrong Source Field (138 records)

**Symptom:** Partial had Key__c code (e.g., "11") as Short_Name; CAM had human abbreviation (e.g., "BS").

**Root cause:** The migration script used `BRANDT.BRAND` (the brand code) as `ohfy__Short_Name__c`. The correct values are hand-curated abbreviations that don't exist in any VIP table.

**Fix:** Copied the 138 curated Short_Name values from CAM to Partial via Bulk API upsert (by SF Id, since Key__c is not an IdLookup field on Item_Type).

**Playbook lesson:** VIP has no source for Item_Type abbreviations. For future customers, either: (a) ask the customer for their abbreviation list, (b) generate abbreviations programmatically from the brand name, or (c) default to the brand code and let the customer curate later.

#### 12.4.2 Contact Is_Delivery_Contact — Checkbox Dropped During Load (146 records)

**Symptom:** Partial had `ohfy__Is_Delivery_Contact__c = TRUE` for all contacts; CAM had `FALSE`.

**Root cause:** The Bulk API silently dropped the checkbox column during the CAM load — likely a field mapping issue or column name mismatch. Checkbox fields default to `false` when not provided.

**Fix:** Updated all 146 contacts in CAM to `TRUE`.

**Playbook lesson:** After every Bulk API load of objects with checkbox fields, **spot-check that checkboxes actually landed**. The Bulk API does not error when a column is silently ignored — it just defaults to `false`. This is especially dangerous for `Is_Active`, `Is_Default`, and contact role flags.

#### 12.4.3 Item UOM_In_Fluid_Ounces — Inverted Values (207 records)

**Symptom:** CAM had values like `0.003472` where Partial had `288` (the correct fluid ounce count for a 24/12oz case).

**Root cause:** The CAM migration script stored `1/value` instead of `value` — a formula inversion bug.

**Fix:** Copied correct values from Partial to CAM (207 items, by SF Id).

**Playbook lesson:** UOM_In_Fluid_Ounces should be `units_per_case × oz_per_unit` (e.g., 24 × 12 = 288). Verify a sample after load — if the values are tiny decimals like 0.003, they're inverted.

#### 12.4.4 Inventory Lot Value — Missing Values (8 records)

**Symptom:** 8 Inventory records for item 77427 had `ohfy__Inventory_Value_Lot_Tracked__c = 67000` in Partial but `0` in CAM.

**Root cause:** The field was populated in Partial (possibly during demo prep) but not included in the CAM load CSV.

**Fix:** Updated the 8 CAM records to match Partial.

**Playbook lesson:** `Inventory_Value_Lot_Tracked__c` is a writable currency field that doesn't auto-calculate. If you set it in one org, make sure it's in the CSV for subsequent orgs.

#### 12.4.5 Account Billing/Delivery Contact — Lookup Not Populated (146 records)

**Symptom:** `ohfy__Billing_Contact__c` and `ohfy__Delivery_Contact__c` were populated in CAM (pointing to Contact records) but null in Partial.

**Root cause:** These lookup fields were added to the migration *after* the initial Partial load. The CAM load included them; Partial was never backfilled.

**Fix:** Resolved CAM Contact IDs → Contact Name + Account External_ID → Partial Contact IDs, then upserted 146 records for each field.

**Playbook lesson:** Contact lookup fields on Account (`Billing_Contact__c`, `Delivery_Contact__c`) require **SF record IDs**, not names. When copying between orgs, you must resolve through the business key: query the Contact by Name + Account.External_ID in the target org to get the correct target ID.

#### 12.4.6 Account Status__c — Non-Ohanafy Custom Field (275 records)

**Symptom:** CAM had `Status__c = 'Active'` on all accounts; Partial had null.

**Root cause:** `Status__c` is a customer-created picklist field (no `ohfy__` namespace). It wasn't part of the migration CSV because it's not an Ohanafy field.

**Fix:** Set all 275 accounts in Partial to `'Active'`.

**Playbook lesson:** Always check for **non-ohfy custom fields** on standard objects (Account, Contact). Customers often have their own fields that need to be populated. Query `EntityParticle` for fields where `NamespacePrefix = null AND IsCustom-equivalent = true` to find them.

#### 12.4.7 Junk Records — "the beer company" (11 Pricelist Items + 1 Item)

**Symptom:** 11 Pricelist Items in Partial pointed to an Item named "the beer company" with null Key__c, $0 price, across all pricelists.

**Root cause:** Test/accidental records created during development. Their Key__c values contained baked-in SF record IDs, making them unmatchable.

**Fix:** Deleted all 11 Pricelist Items and the orphan Item from Partial.

**Playbook lesson:** Before running the comparison, clean up test records. Any record with null Key__c is suspect. Any Key__c containing a Salesforce record ID (starts with `a0`) is also suspect — keys should be VIP business codes, not SF IDs.

### 12.5 Comparison Checklist

Run this checklist after loading data into any new sandbox:

- [ ] Run `compare_sandboxes.py` against the reference org
- [ ] Verify 100% match rate (excluding known User lookup diffs)
- [ ] Spot-check checkbox fields landed correctly (not defaulted to false)
- [ ] Spot-check numeric fields aren't inverted or truncated
- [ ] Check for null Key__c records (junk data)
- [ ] Check non-ohfy custom fields on Account/Contact are populated
- [ ] Verify Contact lookup fields (Billing_Contact, Delivery_Contact) resolve correctly
- [ ] Confirm record counts match ± any intentionally excluded records

### 12.6 Cross-Org Lookup Resolution Pattern

When a field in Org A contains a Salesforce record ID that needs to be set in Org B, use this pattern:

```python
# 1. Query Org A: get the record ID + business key of the referenced record
cam_recs = query(ORG_A, """
    SELECT ohfy__External_ID__c,
           ohfy__Billing_Contact__r.Name,
           ohfy__Billing_Contact__r.Account.ohfy__External_ID__c
    FROM Account WHERE ohfy__Billing_Contact__c != null
""")

# 2. Query Org B: build a lookup from business key → SF record ID
partial_contacts = query(ORG_B, """
    SELECT Id, Name, Account.ohfy__External_ID__c
    FROM Contact WHERE Account.ohfy__External_ID__c != null
""")
contact_lookup = {
    (c['Name'], c['Account']['ohfy__External_ID__c']): c['Id']
    for c in partial_contacts
}

# 3. Match and generate update CSV with Org B's record IDs
for acct in cam_recs:
    contact_name = acct['ohfy__Billing_Contact__r']['Name']
    contact_acct = acct['ohfy__Billing_Contact__r']['Account']['ohfy__External_ID__c']
    target_contact_id = contact_lookup.get((contact_name, contact_acct))
    # Write {Account.Id, ohfy__Billing_Contact__c: target_contact_id} to CSV
```

This pattern works for any lookup field where the target object has a stable business key. Always resolve through the business key — never copy SF record IDs between orgs.

### 12.7 Gulf Results: Before and After

| Metric | Before Fixes | After Fixes |
|---|---|---|
| Match rate | 94.5% | 100% |
| Real diffs | 1,082 | 0 |
| Objects with diffs | 7 | 0 |
| Missing records | 11 | 0 |
| Objects audited | 19 | 19 |
| Total records | ~20,000 | ~20,000 |

Fixes applied: 6 field-level fixes across both orgs + 12 junk records deleted.
