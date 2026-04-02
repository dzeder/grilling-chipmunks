# Gulf Distributing — VIP to Ohanafy Migration Support Guide

This document accompanies **Distro - Data Workbook TEMPLATE 3_3.xlsx** and provides context for each tab: where the data comes from in VIP, mapping decisions made, and open questions.

---

## Tab 1: User

### VIP Source Tables
| Table | Description | CSV Available? |
|---|---|---|
| **USERST** | Primary user master — first name, last name, email, job title, employee ID, department, default warehouse/company | **No** — not exported to CSV |
| **USERCOMPT** | User-to-company permission mapping | No |
| **USERWHSET** | User-to-warehouse permission mapping | No |
| **USERROLET** | User-to-role assignments | No |
| **HDRDRT** | Driver master — driver code, name, supervisor, account | Yes |
| **HDRMERCHT** | Merchandiser master — merch code, name, warehouse, company, supervisor, phone | Yes |
| **COMMEMPT** | Commission employees — employee number, type (SLS), commission rates | Yes |

### Column Mapping
| Workbook Column | Ohanafy API Field | VIP Source | Notes |
|---|---|---|---|
| A: First Name | FirstName | USERST.FIRSTNAME | |
| B: Last Name | LastName | USERST.LASTNAME | |
| C: Email | Email | USERST.EMAIL | |
| D: Role | — | Manual assignment | Not a Salesforce API field; for internal tracking |
| **E: Phone** | Phone | HDRMERCHT.PAGER or manual | New column. Drivers/merchandisers may have phone numbers |
| **F: Employee ID** | ohanafy__Employee_ID__c | USERST.EMPLOYEEID | New column. Critical for cross-referencing back to VIP |
| **G: Employee Type** | ohanafy__Employee_Type__c | USERST.EMPLOYEETYPE + personnel tables | New column. Values: SLS (sales), Driver, Merchandiser, Warehouse, Admin |
| **H: Job Title** | Title | USERST.JOBTITLE | New column |
| **I: Department** | Department | USERST.DEPARTMENTID | New column |
| **J: Default Warehouse** | ohanafy__Default_Warehouse__c | USERST.DEFAULTWAREHOUSE | New column. Gulf has 10 warehouses in HDRWHSET |
| **K: Default Company** | ohanafy__Default_Company__c | USERST.DEFAULTCOMPANY | New column. Gulf has multiple company entities in HDRCOMPT |
| **L: Supervisor** | ManagerId | HDRDRT.SUPERVISOR / HDRMERCHT.SUPERVISOR | New column. Will need to reference another User record in Ohanafy |
| **M: Active** | IsActive | DELETE_FLAG fields | New column. Filter out terminated/inactive users |
| **N: VIP User Code** | ohanafy__VIP_User_Code__c | USERST.EMPLOYEECODE / HDRDRT.DRIVER / HDRMERCHT.MERCHANDISER | New column. Legacy ID for traceability |
| O: Alias | Alias | Formula: first initial + last name | Auto-generated |
| P: Username | Username | Formula: copies email | Auto-generated |
| Q: Time Zone | TimeZoneSidKey | Manual | Likely "America/Chicago" for Gulf |
| R: Profile Name | Profile Name | Manual | "System Admin" or "Ohanafy Standard User" |

### Data Population Status
**Not populated.** The core USERST table was not included in the CSV data exports. To populate this tab, Gulf needs to either:
1. Export the USERST table from VIP
2. Provide a manual user list

Partial data available from HDRDRT (drivers with names) and HDRMERCHT (merchandisers with names), but these lack email addresses.

### Open Questions
- [ ] Can we get a USERST CSV export?
- [ ] What Ohanafy roles/profiles will Gulf use? (System Admin vs Standard User)
- [ ] Default time zone — is all of Gulf in Central Time, or do Florida locations use Eastern?
- [ ] How should supervisor hierarchy be structured in Ohanafy?

---

## Tab 2: Pricelist

### VIP Source Tables
| Table | Description | Rows | CSV Available? |
|---|---|---|---|
| **HDRPRCODT** | Price Code master — broad pricing structures | 154 active | Yes |
| **HDRPRGRPT** | Price Group master — granular customer/chain-level pricing tiers | 370 active | Yes |
| **DPMASTT** | Deal Pricing master — item-level deal records with dates | 807,881 | Yes |
| **DPMAST1T** | Deal Price detail — frontline prices, selling prices, rebate amounts | Large | Yes |
| **DISCWKSTT** | Discount worksheets | Yes | Yes |
| **BRATTT.CMPGRP** | Customer's assigned price group | — | Yes (on BRATTT) |

### Understanding VIP's Pricing Model

VIP uses a **two-level pricing hierarchy**:

**Level 1 — Price Codes (HDRPRCODT)** define the **pricing structure/rules** for broad account categories:
- Controls which cost column drives the price (`PCCOSTNAME`)
- Controls whether discounts are allowed (`ALLOWDISCOUNTS`)
- Controls zero price/deposit check behavior
- Named by company division + account type (e.g., "GDC-WALMART", "ABC-MILITARY", "HUNT-ON PREMISE")
- 154 active codes — relatively few, broad categories
- Example: All Walmart accounts in the GDC division share price code "1A"

**Level 2 — Price Groups (HDRPRGRPT)** define **customer-level pricing tiers** that are more granular:
- Specific pricing for individual chains/retailers (e.g., "RB CIRCLE K", "RB COSTCO")
- Tiered reward/rebate programs (e.g., "RB 2025 PLAT + P", "RB 2025 GOLD + P", "RB 2025 BLUE DMND + P")
- Each customer is assigned a price group via `BRATTT.CMPGRP`
- 370 active groups — chain-specific or program-specific

**How they work together:** A customer gets a Price Code (broad rules) AND a Price Group (specific tier). The Price Code determines base pricing logic; the Price Group fine-tunes for that retailer/tier.

**Deal Pricing (DPMASTT/DPMAST1T)** overlays time-bound promotions on top:
- 807K+ deal records
- Each deal links to an item, warehouse, price group, and date range
- `DPMETHOD` defines the deal calculation method
- `DPBORW` = Beer or Wine indicator
- Connected to the Pricelist Item and Promotions tabs (later in workbook)

### Column Mapping
| Workbook Column | Ohanafy API Field | VIP Source | Notes |
|---|---|---|---|
| A: Name | Name | HDRPRCODT.DESCRIPTION or HDRPRGRPT.DESCRIPTION | Used as the pricelist display name |
| B: Discount | ohanafy__Discount__c | Set to 0 | Default; specific discounts handled at Pricelist Item level |
| C: Type | ohanafy__Type__c | "Individual Price" | Standard Ohanafy pricelist type |
| D: Item Type | ohanafy__Item_Types__c | "Finished Good" | Standard for beverage distribution |
| E: Status | ohanafy__Active__c | TRUE | All active price codes/groups imported as active |
| **F: Description** | ohanafy__Description__c | Same as Name | New column. Full description of the pricelist |
| **G: VIP Price Code** | ohanafy__VIP_Price_Code__c | HDRPRCODT.PRICECODE | New column. Legacy code (e.g., "01", "7A", "H3") |
| **H: VIP Price Group** | ohanafy__VIP_Price_Group__c | HDRPRGRPT.PRICEGROUP | New column. Legacy group (e.g., "AC", "TV", "XM") |
| **I: Allow Discounts** | ohanafy__Allow_Discounts__c | HDRPRCODT.ALLOWDISCOUNTS | New column. Y/N — only populated for Price Code rows |
| **J: Effective Date** | ohanafy__Effective_Date__c | DPMASTT.DPBDAT | New column. Left blank — varies by deal, needs Gulf input |
| **K: End Date** | ohanafy__End_Date__c | DPMASTT.DPEDAT | New column. Left blank — varies by deal, needs Gulf input |
| **L: Company** | ohanafy__Company__c | DPMASTT.DPCOMP | New column. Left blank — needs Gulf input on which company per pricelist |
| **M: Warehouse** | ohanafy__Warehouse__c | DPMASTT.DPWHSE | New column. Left blank — Gulf has 10 warehouses |
| **N: Beer/Wine** | ohanafy__Beer_Wine__c | DPMASTT.DPBORW | New column. Left blank — VIP separates B vs W at deal level |
| **O: Cost Column Name** | ohanafy__Cost_Column_Name__c | HDRPRCODT.PCCOSTNAME / HDRPRGRPT.PGCOSTNAME | New column. "USER15" for military pricing, blank for standard |
| P: Mapping Key | ohanafy__Mapping_Key__c | Formula: "P-" + Record Number | Auto-generated |
| Q: Record Number | Record Number | Auto-increment | Sequential identifier |

### Data Population Status
**Populated with 524 rows:**
- Rows 3–156: **154 price codes** from HDRPRCODT (sorted by code)
- Rows 157–526: **370 price groups** from HDRPRGRPT (sorted by group code)

**Fields populated:** Name, Discount (0), Type, Item Type, Status, Description, VIP Price Code OR VIP Price Group, Allow Discounts (price codes only), Cost Column Name (where applicable)

**Fields left blank (need Gulf input):** Effective Date, End Date, Company, Warehouse, Beer/Wine

### Key Patterns in the Data
- **Company divisions visible in Price Code names:** GDC (Gulf Dist Co), ABC (ABC Board), GDCB (GDC Birmingham), GSCA (Gulf States Craft Ales?), HUNT (Huntsville), EBM
- **Military pricing** uses cost column "USER15" — applies to 6 price codes (02, 12, 72, 82, 92, H2) and 7 price groups (AD, GA, GQ, 48, 15, 19, plus coast guard)
- **RedBull (RB) pricing** dominates price groups with tiered programs: Blue Diamond, Diamond, Double Diamond, Triple Diamond, Platinum, Gold, Bronze — each with +P (plus promo) and +AC (plus ad credit) variants
- Only one price code has Allow Discounts = "N": H1 (HUNT-CIV NO DISCOUNT)

### Open Questions
- [ ] Should Price Codes and Price Groups be separate pricelists in Ohanafy, or consolidated?
- [ ] Which company/warehouse should be assigned to each pricelist? (Currently blank)
- [ ] Should Beer/Wine be split into separate pricelists, or combined?
- [ ] What effective/end dates should be used? Current fiscal year? Or leave open-ended?
- [ ] Are all 524 pricelists still actively used, or can some be pruned?
- [ ] How do the RedBull tier programs (Blue Diamond, Platinum, etc.) map to Ohanafy's pricing model?

---

---

## Tab 3: Supplier

### VIP Source Tables
| Table | Description | Rows | CSV Available? |
|---|---|---|---|
| **SUPPLIERT** | Product supplier master — supplier code, name, AP vendor link, fiscal year, EDI info | ~302 unique codes | **No** — not exported to CSV |
| **APVENT** | AP vendor master — name, address, phone, email, payment terms, tax info | 5,557 total (275 in category 2 = product suppliers) | Yes |
| **APVENDOREMAILTABLE** | Vendor email contacts | Small | Yes |
| **BRANDT** | Brand master — links brands to suppliers via SUPPLIER column | ~302 unique supplier codes | Yes |

### Understanding VIP's Supplier vs Vendor Model

VIP has **two separate but linked tables** for suppliers:

**SUPPLIERT** (Product Supplier Master) — tracks suppliers as product sources:
- Keyed by SUPPLIER code (e.g., "5R", "8Q", "A1")
- Links to AP vendor via `AP_VENDOR` field
- Contains purchasing config: cost columns, PO settings, EDI trading partner
- ~302 unique supplier codes referenced from BRANDT table
- **No CSV export available**

**APVENT** (AP Vendor Master) — tracks vendors for accounts payable:
- Keyed by VRVEND (vendor number, e.g., "399", "400", "450")
- Contains contact info: name, address, phone, fax, email
- Contains payment info: due days, discount percent, 1099 status
- 5,557 total records across 4 categories:
  - **Category 1** (5,007): General vendors — cities, services, utilities, etc.
  - **Category 2** (275): **Product suppliers** — breweries, beverage companies
  - **Category 4** (1): Hotel
  - **Category 5** (274): Office/corporate vendors

**How they link:** SUPPLIERT.AP_VENDOR → APVENT.VRVEND connects the product supplier record to its AP vendor record for payment processing.

### Data Source Decision
All 5,557 APVENT records included, tagged by category via the new **Vendor Category** column. Sorted with Product Suppliers first, then General, Office/Corporate, and Hotel. This lets Gulf filter/review by category in the spreadsheet.

### Column Mapping
| Workbook Column | Ohanafy API Field | VIP Source | Notes |
|---|---|---|---|
| A: Record Type | Record Type | "Supplier" (hardcoded) | Ohanafy record type |
| B: Name | Name | APVENT.VRNAME | Vendor/supplier display name |
| C: Record Type Id | RecordTypeId | Formula: VLOOKUP to Record Types tab | Auto-generated |
| D: Mapping Key | ohanafy__Mapping_Key__c | Formula: "S-" + Record Number | Auto-generated |
| E: Mailing Street | BillingStreet | APVENT.VRADD1 | Address line 1 from AP vendor |
| F: Mailing City | BillingCity | CITYT.CITYNAME via APVENT.ID_CITY | Resolved via city lookup table (81% fill rate) |
| G: Mailing State | BillingState | CITYT.STATE via APVENT.ID_CITY | Resolved via city lookup table |
| H: Mailing Zip Code | BillingPostalCode | APVENT.POSTALCODE | |
| I: Mailing Country | BillingCountry | "US" (defaulted) | |
| J: Physical Street | ShippingStreet | Mirrored from Mailing Street | |
| K: Physical City | ShippingCity | Mirrored from Mailing City | |
| L: Physical State | ShippingState | Mirrored from Mailing State | |
| M: Physical Zip Code | ShippingPostalCode | Mirrored from Mailing Zip | |
| N: Physical Country | ShippingCountry | "US" (defaulted) | |
| O: Region | ohanafy__Region__c | Derived from state | Core states expanded (Alabama, Florida, etc.); others show abbreviation |
| P: Phone | Phone | APVENT.VRPHON | Formatted with dashes where 10-digit |
| Q: Website | Website | Not in APVENT | |
| **R: Email** | ohanafy__Email__c | APVENT.VREMAIL or APVENDOREMAILTABLE.EMAIL | New column. Merged from both sources |
| **S: Fax** | Fax | APVENT.VRFAX | New column. Formatted with dashes |
| **T: VIP Vendor Code** | ohanafy__VIP_Vendor_Code__c | APVENT.VRVEND | New column. Legacy vendor number for traceability |
| **U: Supplier Category** | ohanafy__Supplier_Category__c | APVENT.ID_APVENCAT | New column. "Product Supplier", "General", "Office/Corporate", or "Hotel" |
| **V: 1099 Required** | ohanafy__1099_Required__c | APVENT.VR1099 | New column. Y/N — tax reporting requirement |
| **W: Sales Tax Exempt** | ohanafy__Sales_Tax_Exempt__c | APVENT.VRSALESTX | New column. Y/N |
| **X: Payment Due Days** | ohanafy__Payment_Due_Days__c | APVENT.VRDUED | New column. Number of days until payment due |
| **Y: Discount Percent** | ohanafy__Discount_Percent__c | APVENT.VRSDPCT | New column. Early payment discount percentage |
| Z: Rating | ohanafy__Rating__c | Defaulted to 5 | |
| AA: Status | ohanafy__Status__c | Derived from APVENT.VRSNOPAY | "Active" if VRSNOPAY != "Y", else "Inactive" |
| AB: Payment Terms | ohanafy__Payment_Terms__c | Derived from APVENT.VRDUED | Formatted as "30 Days", "10 Days", etc. |
| AC: Type | Type | "Supplier" (hardcoded) | |
| AD: Stage | ohanafy__Stage__c | "Supplier" (hardcoded) | |
| AE: Record Number | Record Number | Auto-increment | Sequential identifier |

### Data Population Status
**Populated with 5,557 rows** — all APVENT vendors, tagged by category. Sorted: Product Suppliers (275) first, then General (5,007), Office/Corporate (274), Hotel (1).

**Fields populated:** Name, Address, Zip, Country, Phone, Email, Fax, VIP Vendor Code, 1099 flag, Sales Tax flag, Payment Due Days, Discount Percent, Rating, Status, Payment Terms, Type, Stage

**Fields not populated (need Gulf input or missing source data):**
- Website — not stored in APVENT
- City/State for ~19% of records (1,039 vendors had no ID_CITY match in CITYT)

### Known Limitations
- **No SUPPLIERT CSV** — we used APVENT as the source. The SUPPLIERT-to-APVENT linkage (AP_VENDOR) is unknown without that export.
- **City/State 81% filled** — resolved via CITYT lookup table. 1,039 vendors had no matching ID_CITY and will need manual review.
- **Physical address = mailing address** — mirrored since APVENT only stores one address. May need correction for vendors with separate physical locations.
- **Region mapping** — Gulf's 6 core states (AL, FL, MS, GA, TN, LA) expanded to full names. Out-of-territory states show as abbreviations. Region logic may need refinement.

### Open Questions
- [ ] Can we get a SUPPLIERT CSV export? This would give us supplier codes and the AP_VENDOR linkage
- [ ] Should all 5,557 vendors migrate, or only certain categories?
- [ ] Should General vendors (5,007 records) use a different Ohanafy record type than Product Suppliers?
- [ ] Should out-of-territory states have full region names or be grouped (e.g., "Out of Territory")?

---

## Tab 4: Suppliers(Item Line)

### VIP Source Tables
| Table | Description | Rows | CSV Available? |
|---|---|---|---|
| **BRANDT** | Brand master — brand code, name, supplier code, quota type, sell-by-bottle flag | 927 active | Yes |
| **SUPPLIERT** | Supplier master — links supplier code to AP vendor | ~302 unique codes | **No** — not exported |

### Understanding the Hierarchy

```
Supplier (e.g., Molson Coors)           → Supplier tab (from APVENT)
  └── Supplier Item Line (e.g., Coors)  → This tab (from BRANDT)
        └── Brand (e.g., Coors Light)   → Brands tab
              └── Product (e.g., Coors Light 12pk cans) → Product tab (from ITEMT)
```

In VIP, the **BRANDT** table represents the item line level. Each brand record has:
- A **BRAND** code (2-char, e.g., "BX" = Becks)
- A **BRAND_NAME** (e.g., "BECKS")
- A **SUPPLIER** code (2-char, e.g., "1I" = AB InBev imports)
- No brand family hierarchy (BRAND_FAMILY_XREF is empty for all records)

### Top Suppliers by Item Line Count
| VIP Code | Likely Supplier | Item Lines | Sample Brands |
|---|---|---|---|
| 1C | Molson Coors | 98 | Miller Euro, Redd's, Sauza Diablo, Blue Moon |
| 3N | Red Bull | 49 | Red Bull (many seasonal/variety variants) |
| 2T | Keurig Dr Pepper | 33 | 7UP, A&W, Hawaiian Punch, Snapple |
| 1V | Pabst | 24 | Jack Daniels, Schlitz, Colt 45, Champale |
| 2F | Constellation | 23 | Corona, Modelo, Svedka |
| 2U | Boston Beer | 22 | Sam Adams, Twisted Tea, Angry Orchard, Dogfish |
| 1I | AB InBev Imports | 20 | Becks, Stella Artois, Hoegaarden, Spaten |
| 2Q | Heineken | 20 | Amstel, Bohemia, Dos Equis, Tecate |

### Column Mapping
| Workbook Column | Ohanafy API Field | VIP Source | Notes |
|---|---|---|---|
| A: Name | Name | BRANDT.BRAND_NAME | Item line display name |
| **B: VIP Brand Code** | ohanafy__VIP_Brand_Code__c | BRANDT.BRAND | New column. 2-char legacy code (e.g., "BX", "AP") |
| **C: VIP Supplier Code** | ohanafy__VIP_Supplier_Code__c | BRANDT.SUPPLIER | New column. 2-char code (e.g., "1C", "3N") |
| **D: Supplier Name** | ohanafy__Supplier_Name__c | Needs manual mapping | New column. Must match a Name in Supplier tab for VLOOKUP |
| **E: Quota Type** | ohanafy__Quota_Type__c | BRANDT.QUOTA_TYPE | New column |
| **F: Sell By Bottle** | ohanafy__Sell_By_Bottle__c | BRANDT.SELL_BY_BOTTLE | New column. Y/N |
| G: Supplier | ohanafy__Supplier__c | Formula: VLOOKUP on D against Supplier tab | Returns Supplier Mapping Key |
| H: Mapping Key | ohanafy__Mapping_Key__c | Formula: "IL-" + Record Number | Auto-generated |
| I: Record Number | Record Number | Auto-increment | Sequential identifier |

### Data Population Status
**Populated with 927 rows** from BRANDT (all active brands), sorted by supplier code then name.

**Fields populated:** Name, VIP Brand Code, VIP Supplier Code, Quota Type, Sell By Bottle, Mapping Key, Record Number

**Partially populated:**
- **Supplier Name (col D)** — 718/927 rows (77%) auto-matched by fuzzy-matching brand names against APVENT category-2 vendor names. 209 rows (125 unique supplier codes) still need manual mapping — these are mostly smaller/niche brands where the brand name doesn't appear in the vendor name.

### Known Limitations
- **Supplier linkage partial** — Without SUPPLIERT CSV, we used fuzzy name matching (brand name keywords vs APVENT vendor name) to fill 77% of supplier names. The remaining 23% will show #N/A in the VLOOKUP until manually filled. A SUPPLIERT export would resolve all of them.
- **Flat structure** — BRAND_FAMILY_XREF is empty for all records, so there's no parent-child brand family hierarchy. Every brand is a standalone item line.

### Open Questions
- [ ] Can we get a SUPPLIERT CSV export? This would auto-fill the supplier name mapping
- [ ] Are all 927 brands still active item lines, or have some been discontinued?
- [ ] Should the 302 supplier codes be consolidated? (Some suppliers may have multiple APVENT records)

---

## Tab 5: Brands

### VIP Source Tables
| Table | Description | Rows | CSV Available? |
|---|---|---|---|
| **BRANDT** | Brand master — same source as Supplier Item Lines | 927 active | Yes |
| **ITEMT** | Product master — aggregated per brand for stats | 8,743 items across 686 brands | Yes |
| **HDRPSTATT** | Product status codes (Active, Seasonal, Deleted, etc.) | Small | Yes |

### VIP Data Model Note
VIP has **only one level** between Supplier and Product (BRANDT). Ohanafy has **two levels** (Item Line + Brand). Since VIP doesn't distinguish between them, we mapped:
- **Supplier Item Lines tab** = BRANDT records
- **Brands tab** = BRANDT records (1:1 with Item Lines)

The VLOOKUP in column L links each Brand back to its matching Item Line by name. This 1:1 relationship can be restructured later if Gulf wants to create a more granular hierarchy.

### Column Mapping
| Workbook Column | Ohanafy API Field | VIP Source | Notes |
|---|---|---|---|
| A: Record Type Name | Record Type | Formula: copies Type (col K) | "Finished Good" |
| B: RecordTypeId | RecordTypeId | Formula: VLOOKUP to Record Types tab | Auto-generated |
| C: Name | Name | BRANDT.BRAND_NAME | Brand display name |
| D: Mapping Key | ohanafy__Mapping_Key__c | Formula: "B-" + Record Number | Auto-generated |
| E: Supplier | — | BRANDT.BRAND_NAME | Item Line name for VLOOKUP (same as brand name in 1:1 model) |
| **F: VIP Brand Code** | ohanafy__VIP_Brand_Code__c | BRANDT.BRAND | New column. 2-char legacy code |
| **G: VIP Supplier Code** | ohanafy__VIP_Supplier_Code__c | BRANDT.SUPPLIER | New column. 2-char code linking to supplier |
| **H: Product Class** | ohanafy__Product_Class__c | ITEMT.PRODUCT_CLASS (most common per brand) | New column. Derived: Beer, Non-Alcoholic, Spirits/RTD, Import Beer, etc. |
| **I: Item Count** | ohanafy__Item_Count__c | Count of ITEMT records per brand | New column. Total SKUs under this brand |
| **J: Active Items** | ohanafy__Active_Items__c | Count of active/seasonal ITEMT records | New column. Active SKU count |
| K: Type | ohanafy__Type__c | "Finished Good" | Standard Ohanafy type |
| L: Item Line | ohanafy__Item_Line__c | Formula: VLOOKUP on E against Item Line tab | Returns Item Line Mapping Key |
| M: Record Number | Record Number | Auto-increment | Sequential identifier |

### Data Population Status
**Populated with 927 rows** from BRANDT, sorted alphabetically by name.

**Key stats:**
- 686 brands have items in ITEMT (total 8,743 SKUs)
- 241 brands have NO items in ITEMT (may be inactive/discontinued)
- Product class breakdown: Beer (380), Non-Alcoholic (122), Spirits/RTD (53), Import Beer (37), FMB/Flavored (31), Wine (30), and others

### Product Class Labels
Since the HDRCLASST table (class descriptions) was not exported, product class codes were labeled based on the items they contain:
| Code | Label | Brand Count |
|---|---|---|
| 01 | Beer | 380 |
| 04 | Non-Alcoholic | 122 |
| 06 | Spirits/RTD | 53 |
| 03 | Import Beer | 37 |
| 14 | FMB/Flavored | 31 |
| 05 | Wine | 30 |
| 02 | Craft Beer | 14 |
| 07 | Cider/Seltzer | 11 |

### Open Questions
- [ ] Are the product class labels accurate? (We inferred them — HDRCLASST was not exported)
- [ ] Should the 241 brands with no items be excluded?
- [ ] Should Brand and Item Line remain 1:1, or should Gulf create brand families (e.g., group all Red Bull variants under one Item Line)?

---

## Tab 8: Customer

### VIP Source Tables
| Table | Description | Rows | CSV Available? |
|---|---|---|---|
| **BRATTT** | Customer master — account number, DBA name, legal name, phone, license, salesman code, price code/group, terms, on/off premise, route, chain, class, county, lat/lon | 28,694 total (15,337 active) | Yes |
| **POSACCT** | POS/delivery account addresses — street, city, state, zip for delivery locations | 3,810 | Yes |
| **CUSTADT** | Customer address table — mailing addresses (type "M") | 271 | Yes |
| **CITYT** | City/state lookup — resolves ID_CITY to city name and state | 1,453 | Yes |
| **POSSM** | POS salesman master — salesman code, "LAST, FIRST" format names | 239 | Yes |
| **USERST** | User master — employee code, first/last name | Not exported | No |
| **HDRDRT** | Driver master — driver code, name | Yes | Yes |
| **HDRTERMT** | Payment terms — terms code, description | 5 entries | Yes |
| **HDRONOFFT** | On/off premise types — 1=On, 2=Off, 3=Employee/Supplier | Small | Yes |
| **HDRCHAINT** | Chain master — chain code to description | Yes | Yes |
| **HDRCNTYCODET** | County code master — county code to name | Yes | Yes |

### Understanding VIP's Customer Model

VIP's customer master (**BRATTT**) uses a "CM" column prefix convention for Customer Master fields. Key fields:
- **CMACCT** — Customer account number (unique identifier)
- **CMDBA** — "Doing Business As" name (primary display name)
- **CMLGNM** — Legal name
- **CMPHON** — Phone number
- **CMLIC#** — License/ABC number
- **CMBSM1** — Primary salesman code
- **CMPRCD** — Price code (links to HDRPRCODT)
- **CMPGRP** — Price group (links to HDRPRGRPT)
- **CMTERM** — Payment terms code
- **CMONOF** — On/off premise type (1/2/3)
- **CMROUT** — Route code
- **CMCHN** — Chain code
- **CMCLAS** — Class code
- **CMCNTY** — County code
- **CMSTTP** — Sub-type
- **CMLATD/CMLOND** — Latitude/longitude
- **CMSTAT** — Status (A=Active)
- **CMETHO** — Payment method code

**Address architecture:** VIP's AS/400 system does **not** store street addresses in the customer master table. Historically, drivers knew delivery locations by route — the system tracked customers by city (ID_CITY) and zip code (POSTALCODE) but not street address. Street addresses exist only in:
- **POSACCT** — POS/delivery addresses (~3,810 records, covering ~20% of active customers)
- **CUSTADT** — Mailing addresses (271 records, all type "M")

### Column Mapping
| Workbook Column | Ohanafy API Field | VIP Source | Notes |
|---|---|---|---|
| A: Record Type Name | Record Type | "Customer" (hardcoded) | |
| B: Record Type Id | RecordTypeId | Formula: VLOOKUP to Record Types tab | |
| C: Legacy Name | ohanafy__Legacy_Name__c | BRATTT.CMDBA | DBA name |
| D: Customer Name | Name | BRATTT.CMDBA | Display name |
| E: Mapping Key | ohanafy__Mapping_Key__c | Formula: "CUST-" + Record Number | |
| F: Legal Name | ohanafy__Legal_Name__c | BRATTT.CMLGNM | |
| G: Sales Rep Name | ohanafy__Sales_Rep__c | POSSM/USERST/HDRDRT via CMBSM1 | 3-source priority lookup; placeholder names filtered |
| H: Pricelist Name | ohanafy__Pricelist__c | HDRPRCODT.DESCRIPTION via CMPRCD | 100% coverage |
| I–M: Mailing Address | BillingStreet/City/State/Zip/Country | Formulas: mirror Physical address | |
| N: Physical Street | ShippingStreet | POSACCT.ADDRESS or CUSTADT.ADDRESS | **Only ~20% coverage** |
| O: Physical City | ShippingCity | CITYT.CITYNAME via ID_CITY | 100% coverage |
| P: Physical State | ShippingState | CITYT.STATE via ID_CITY | 100% coverage |
| Q: Physical Zip | ShippingPostalCode | BRATTT.POSTALCODE | |
| R: Physical Country | ShippingCountry | "US" (defaulted) | |
| S: Region | ohanafy__Region__c | HDRCNTYCODET.DESCRIPTION via CMCNTY | County name |
| T: Type | Type | "Customer" (hardcoded) | |
| U: Stage | ohanafy__Stage__c | "Customer" (hardcoded) | |
| V: Payment Terms | ohanafy__Payment_Terms__c | Mapped from CMTERM | Net 0, Net 15, Net 30, Net 60, COD |
| W: Payment Method | ohanafy__Payment_Method__c | CMETHO + term-based override | Check, Wire, Cash, Money Order, ACH, EDI, FinTech, Other |
| X: Delivery Method | ohanafy__Delivery_Method__c | Left blank | |
| Y: Consignment Items | ohanafy__Consignment_Items__c | Left blank | |
| Z: Phone | Phone | BRATTT.CMPHON | Formatted with dashes; 99.9% coverage |
| AA: Website | Website | Not in VIP | |
| AB: Status | ohanafy__Status__c | "Active" | Only active (CMSTAT='A') records imported |
| AC: Customer Number | ohanafy__Customer_Number__c | BRATTT.CMACCT | VIP account number |
| AD: Premise Type | ohanafy__Premise_Type__c | HDRONOFFT via CMONOF | On Premise / Off Premise |
| AE: Sub Type | ohanafy__Sub_Type__c | BRATTT.CMSTTP | |
| AF: ABC Number | ohanafy__ABC_Number__c | BRATTT.CMLIC# | License number; 85% coverage |
| AG: EFT Provider | ohanafy__EFT_Provider__c | Left blank | |
| AH: EFT Customer ID | ohanafy__EFT_Customer_ID__c | Left blank | |
| AI: Tax Exempt | ohanafy__Tax_Exempt__c | BRATTT.CMTXEX | |
| AJ: Sales Rep Key | ohanafy__Sales_Rep_Key__c | Formula: VLOOKUP to User tab | |
| AK: Pricelist Key | ohanafy__Pricelist_Key__c | Formula: VLOOKUP to Pricelist tab | |
| **AL: VIP On/Off Code** | ohanafy__VIP_OnOff_Code__c | BRATTT.CMONOF | New column. Legacy code (1/2/3) |
| **AM: VIP Route Code** | ohanafy__VIP_Route_Code__c | BRATTT.CMROUT | New column. Delivery route assignment |
| **AN: VIP Chain Code** | ohanafy__VIP_Chain_Code__c | BRATTT.CMCHN | New column. Chain/retail group |
| **AO: VIP Class Code** | ohanafy__VIP_Class_Code__c | BRATTT.CMCLAS | New column. Customer classification |
| **AP: VIP Salesman Code** | ohanafy__VIP_Salesman_Code__c | BRATTT.CMBSM1 | New column. Legacy salesman ID |
| **AQ: VIP County Code** | ohanafy__VIP_County_Code__c | BRATTT.CMCNTY | New column. County/territory code |
| AR: Record Number | Record Number | Auto-increment | Sequential identifier |

### Data Population Status
**Populated with 15,337 rows** — all active customers (CMSTAT = 'A').

**Key coverage stats:**
| Field | Coverage | Notes |
|---|---|---|
| Phone | 99.9% (15,330/15,337) | Nearly universal |
| City/State | 100% | Via CITYT lookup |
| Lat/Lon | 96% (14,665/15,337) | Available but not in workbook |
| License/ABC # | 85% (13,025/15,337) | |
| Pricelist | 100% | All matched via CMPRCD |
| **Street Address** | **~20%** | **See Follow-Up Questions below** |
| Sales Rep Name | 24% | 58% have no salesman code; some codes have placeholder names |
| Payment Terms | High | Mapped from CMTERM via lookup table |

**Premise type breakdown:** 10,674 Off Premise (70%), 4,661 On Premise (30%)

### Payment Terms Mapping
VIP's CMTERM field stores internal term codes. Mapped to standard format:
| CMTERM | Mapped To | Notes |
|---|---|---|
| 0, 3, 5, 8, 9 | COD | Cash on delivery variants |
| N | Net 15 | |
| 1, 6, E, F | Net 30 | Standard 30-day terms |
| 2 | Net 15 | |
| H | Net 60 | Extended terms |

### Payment Method Mapping
Primary source is CMETHO field, with EDI/FinTech override from term codes:
| CMETHO | Method | Override |
|---|---|---|
| 4 | Check | |
| W | Wire | |
| 2 | Cash | |
| M | Money Order | |
| A | ACH | |
| O | Other | |
| — | EDI | If CMTERM = 'E' |
| — | FinTech | If CMTERM = 'F' |

### Sales Rep Name Resolution
Salesman codes (CMBSM1) are resolved using a 3-source priority lookup:
1. **USERST** — employee code match where type = 'SLS' (highest priority)
2. **POSSM** — POS salesman table ("LAST, FIRST" format, flipped to "First Last")
3. **HDRDRT** — driver table (fallback)

Placeholder names are filtered out: "Open XXX", "Driver Sell XXX", "House Route", "WebOrders", "Mobile House", "Milton House", "Bham House", "Montg House". These are system/routing placeholders, not real sales reps.

Result: 137 of 187 unique salesman codes resolved to real names, covering ~24% of all customers.

### Known Limitations
- **Street address coverage is ~20%** — VIP's AS/400 architecture did not store street addresses in the customer master. Addresses only exist in POSACCT (delivery) and CUSTADT (mailing) tables. See follow-up questions below.
- **Sales rep assignment gaps** — 58% of customers have no salesman code (CMBSM1 is blank). Of the 42% with codes, some map to placeholder names. Only ~24% of customers have a resolved real sales rep name.
- **Mailing = Physical** — Mailing address columns are formula-mirrored from physical address. Customers with different billing/shipping addresses will need manual correction.
- **No SUPPLIERT/USERST CSV** — Sales rep resolution relies on POSSM and HDRDRT as fallback sources since USERST was not exported.

### Follow-Up Questions

**Street Address Coverage (Critical)**
- [ ] **Only ~20% of customers have street addresses.** VIP's POSACCT table has 3,810 delivery addresses and CUSTADT has 271 mailing addresses, but the customer master (BRATTT) has no address fields at all. This appears to be a VIP/AS400 system design limitation — drivers historically knew locations by route, not by street address.
- [ ] **Does Gulf have customer addresses in another system?** (e.g., a separate CRM, a routing/GPS system, delivery management software, or even spreadsheets maintained by sales reps)
- [ ] **Can we reverse-geocode from lat/lon?** 96% of customers (14,665/15,337) have latitude/longitude coordinates (CMLATD/CMLOND). These could potentially be reverse-geocoded to generate street addresses, though accuracy varies.
- [ ] **Are the POSACCT addresses current?** The 3,810 addresses we do have come from POS/delivery records — are these regularly maintained, or could they be outdated?
- [ ] **Is 20% acceptable for go-live, or is this a blocker?** Ohanafy may require addresses for delivery routing, invoicing, and compliance. Gulf should confirm whether they can operate with partial address data initially and backfill later.

**Sales Rep Assignment**
- [ ] 58% of customers have no salesman code. Is this expected (e.g., house accounts, web orders), or should all customers have a sales rep assigned before migration?
- [ ] Placeholder names like "Open 1T1" and "House Route" were filtered out. Should these be mapped to specific people or left blank?

**Payment Terms & Method**
- [ ] The payment terms mapping was built from the 5 HDRTERMT entries plus observed CMTERM values. Does Gulf want to validate the COD vs Net 30 assignments?
- [ ] EDI and FinTech payment methods were inferred from term codes 'E' and 'F'. Is this correct?

**General**
- [ ] Should inactive customers (CMSTAT != 'A') also be migrated? Currently only 15,337 active records are included out of 28,694 total.
- [ ] Are the 6 new VIP reference columns (On/Off Code, Route, Chain, Class, Salesman, County) needed long-term in Ohanafy, or just for migration reference?
- [ ] How should the chain code (CMCHN) be used in Ohanafy? VIP has chain groupings — does Ohanafy have an equivalent?

---

## Tab 9: Contact

### VIP Source Tables
| Table | Description | Rows | CSV Available? |
|---|---|---|---|
| **BRATTT** | Customer master — CMBUYR field stores buyer/contact name per account | 10,026 active with buyer name (65%) | Yes |
| **APVENT** | Vendor master — VREMAIL field for vendor-level email contacts | 37 with email | Yes |
| **APVENDOREMAILTABLE** | Vendor email contacts — 842 rows but 804 are placeholder `@email.com` | 38 usable | Yes |

### Understanding VIP's Contact Data

VIP does **not** have a dedicated contact table. Contact information is embedded in other tables:

- **BRATTT.CMBUYR** — A free-text "buyer name" field on the customer master. Contains the primary contact/buyer for each account. 65% of active customers have this field populated (10,026/15,337).
- **BRATTT.CMPHON** — Phone number on the customer record (not contact-specific).
- **No customer email** — BRATTT has no email column. Customer email addresses are not stored in VIP.
- **APVENT.VREMAIL** — Vendor-level emails (only 37 vendors have real email addresses).
- **APVENDOREMAILTABLE** — Mostly placeholder data (804/842 rows have fake `@email.com` addresses).

**CMBUYR name patterns:**
- Full names with space: 6,376 (e.g., "MATT KING", "SCOTT PRICE")
- First name only: ~2,636 (e.g., "JEN", "CHRIS", "ALEX")
- Numeric junk: 634 (e.g., "13722") — filtered out
- Multi-person with separators: ~200 (e.g., "TONY & JEN LINDBERG", "JOHN OR MARLA") — parsed to first person only

### Column Mapping
| Workbook Column | Ohanafy API Field | VIP Source | Notes |
|---|---|---|---|
| A: Customer Name | — | BRATTT.CMDBA | Links contact to customer account |
| B: Supplier Name | — | APVENT.VRNAME | Links contact to supplier (vendor contacts only) |
| C: First Name | FirstName | Parsed from CMBUYR | First word of buyer name |
| D: Last Name | LastName | Parsed from CMBUYR | Remaining words of buyer name |
| E: Mobile Phone | MobilePhone | BRATTT.CMPHON | Formatted with dashes; same as customer phone |
| F: Email | Email | APVENT.VREMAIL | Only for vendor contacts (37 rows) |
| G: Title | Title | Not available | |
| H: Department | Department | Not available | |
| I: Description | Description | Not available | |
| J: Preferred Contact | Preferred_Contact__c | "TRUE" | Default for all contacts |
| K–M: Opt-out flags | HasOptedOutOfEmail/Fax, DoNotCall | Not available | |
| N: Contact Name | — | Formula: First + " " + Last | |
| O: Contact Key | ohanafy__Mapping_Key__c | Formula: "CON-" + Record Number | |
| P: Customer Key | — | Formula: VLOOKUP to Customer tab | Matches Customer Name → Mapping Key |
| Q: Supplier Key | — | Formula: VLOOKUP to Supplier tab | Matches Supplier Name → Mapping Key |
| R–S: Vendor/CP Key | — | Not populated | |
| T: Account Id | AccountId | Formula: first non-blank of P/Q/R/S | |
| U: Record Number | — | Auto-increment | |

### Data Population Status
**Populated with 9,429 rows:**
- **9,392 customer contacts** from BRATTT.CMBUYR (active customers with non-empty, non-numeric buyer names)
- **37 vendor contacts** from APVENT (vendors with real email addresses)

**Name quality:**
| Type | Count | Notes |
|---|---|---|
| Full name (first + last) | 6,285 | Parsed from "FIRST LAST" format |
| First name only | 3,144 | Single word or abbreviation — no last name available |

### Known Limitations
- **No customer email** — VIP does not store email addresses for customers. The Email column is only populated for the 37 vendor contacts.
- **Phone = customer phone** — The phone number is copied from the customer record (CMPHON), not a contact-specific phone. If a buyer has a different phone number, it's not captured.
- **First name only for 33%** — Many CMBUYR entries are just first names ("JEN", "CHRIS") with no last name. These contacts will need enrichment.
- **Multi-person entries parsed to first person** — Buyer names like "TONY & JEN LINDBERG" or "JOHN OR MARLA MCCARTHY" are split and only the first person is kept. The second contact is lost.
- **Vendor contacts are company-level** — The 37 vendor contacts use the vendor company name as the contact name (not an individual person), since APVENT.VRNAME is the company name.
- **No title/department** — VIP doesn't store job title or department for buyer contacts.

### Follow-Up Questions
- [ ] Does Gulf have customer email addresses in another system? (CRM, email marketing platform, etc.)
- [ ] Should the 634 numeric-only CMBUYR entries (e.g., "13722") be investigated? These may be store numbers or reference codes rather than junk.
- [ ] For multi-person buyer names (e.g., "Tony & Jen"), should both people be created as separate contacts?
- [ ] Should all 15,337 active customers have a contact record, or only the 10,026 with buyer names?

---

## Tab: Pickpath (New Sheet)

### VIP Source Tables
| Table | Description | Rows | CSV Available? |
|---|---|---|---|
| **LOCMAST** | Location master — warehouse pick/storage locations with sequence, coordinates, capacity, and pick configuration | 21,272 | Yes |
| **HDRWHSET** | Warehouse master — warehouse code to name mapping | 10 warehouses | Yes |

### Understanding VIP's Location Model

VIP's **LOCMAST** table (LC prefix = Location Code) defines every physical storage and pick location within each warehouse. Each location has:

- **LCWHSE** — Warehouse code (links to HDRWHSET)
- **LCLOC** — Location code (e.g., "CTG101", "B0511", "KEG")
- **LCDESC** — Description (e.g., "FULL PALLET", "RESERVE", "DRAFT PRODUCT")
- **LCLOCSEQ** — Location sequence number (pick path ordering) — populated for 29% of rows
- **LCCNTSEQ** — Count sequence number — populated for 44% of rows
- **LCPICK** — Pick flag (Y/N) — determines if the location is a pick face
- **LCAREA** — Area designation
- **LCSTAT** — Status code
- **LCAVAIL** — Available flag (Y/N)
- **LCPTYP** — Pick type (A=case, K=keg, etc.)
- **LCPQTY** — Pick quantity
- **LCREPL** — Replenish level
- **LCSTAG** — Staging flag (Y/N)
- **LCXCOR/LCYCOR/LCZCOR** — 3D zone coordinates
- **LCTHRS/LCMIN/LCMMAX/LCMMIN/LCMMOV** — Threshold, min, and move parameters
- **LCPALL** — Pallet flag (Y/N)
- **LCBOND** — Bond flag (Y/N)

### Column Mapping
| Workbook Column | Ohanafy Field | VIP Source | Notes |
|---|---|---|---|
| A: Warehouse Code | warehouse_code | LOCMAST.LCWHSE | |
| B: Warehouse Name | warehouse_name | HDRWHSET.WAREHOUSE_NAME | Resolved via lookup |
| C: Path Sequence | path_sequence | Generated | Per-warehouse sequential number (1, 2, 3...) ordered by LCLOCSEQ → LCCNTSEQ → LCLOC |
| D: Location Code | location_code | LOCMAST.LCLOC | |
| E: Location Desc | location_desc | LOCMAST.LCDESC | |
| F: Location Sequence | location_sequence | LOCMAST.LCLOCSEQ | VIP's native sequence; blank for 71% of rows |
| G: Count Sequence | count_sequence | LOCMAST.LCCNTSEQ | |
| H: Pick Flag | pick_flag | LOCMAST.LCPICK | Y or N |
| I: Area | area | LOCMAST.LCAREA | |
| J: Status | status | LOCMAST.LCSTAT | |
| K: Available | available | LOCMAST.LCAVAIL | |
| L–N: Zone Coordinates | zone_coord_x/y/z | LOCMAST.LCXCOR/LCYCOR/LCZCOR | 3D warehouse coordinates |
| O: Pick Type | LCPTYP | LOCMAST.LCPTYP | A=case, K=keg |
| P: Pick Qty | LCPQTY | LOCMAST.LCPQTY | |
| Q: Replenish | LCREPL | LOCMAST.LCREPL | |
| R: Staging | LCSTAG | LOCMAST.LCSTAG | |
| S: Threshold | LCTHRS | LOCMAST.LCTHRS | |
| T: Min | LCMIN | LOCMAST.LCMIN | |
| U–W: Move params | LCMMAX/LCMMIN/LCMMOV | LOCMAST | Move max, min, MOV |
| X: Pallet | LCPALL | LOCMAST.LCPALL | Y/N |
| Y: Bond | LCBOND | LOCMAST.LCBOND | Y/N — bonded warehouse flag |
| Z: Record Number | IDENTITY | Auto-increment | |

### Data Population Status
**Populated with 21,272 rows** — all non-deleted LOCMAST records.

**Breakdown by type:**
| Pick Flag | Count | % |
|---|---|---|
| Pick (Y) | 9,849 | 46% |
| Non-pick (N) | 11,417 | 54% |
| Blank | 6 | <1% |

**Rows per warehouse:**
| WH | Name | Locations |
|---|---|---|
| 1 | Gulf Mobile | 2,408 |
| 2 | Goldring Gulf Milton | 4,796 |
| 4 | *(no name in HDRWHSET)* | 3,673 |
| 7 | Montgomery | 2,094 |
| 9 | Birmingham | 5,386 |
| 10 | Huntsville | 1,742 |
| c | *(no name in HDRWHSET)* | 1,167 |
| 5, 6, 11 | Jackson, Gulfport, ABC Board | 2 each |

### Path Sequence Generation
VIP's native `LCLOCSEQ` is only populated for 29% of rows (mostly pick locations). To ensure every row has an ordering value, we generate a **Path Sequence** as a per-warehouse row number (1, 2, 3...) using this sort order:
1. `LCLOCSEQ` (VIP's location sequence, when available)
2. `LCCNTSEQ` (count sequence, as secondary sort)
3. `LCLOC` (location code, as tiebreaker)

### Known Limitations
- **Warehouse 4 and "c" have no names** — These warehouse codes are in LOCMAST but not in HDRWHSET. Gulf should confirm what these warehouses are.
- **LCLOCSEQ coverage is low** — Only 6,214/21,272 (29%) have VIP's native location sequence. The generated path sequence provides ordering for all rows, but may not match Gulf's actual pick path.
- **Warehouses 5, 6, 11 have minimal data** — Only 2 locations each. May be inactive or test warehouses.

### Follow-Up Questions
- [ ] What are warehouse codes "4" and "c"? They have significant location counts (3,673 and 1,167) but no name in HDRWHSET.
- [ ] Is the generated path sequence (sorted by LCLOCSEQ → LCCNTSEQ → LCLOC) a reasonable approximation of the actual pick path? Should Gulf provide the correct pick path ordering?
- [ ] Should inactive or non-pick locations (54%) be included in the migration, or only pick locations?
- [ ] Warehouses 5 (Jackson), 6 (Gulfport), and 11 (ABC Board) have only 2 locations each — are these still in use?

---

## Tab: Pricelist Item

### Overview
Links individual items to pricelists with their deal/case pricing. Each row represents one item's price within a specific pricelist.

- **Rows written**: 21,109
- **Pricelists with items**: 186 (of 524 total pricelists)
- **Source tables**: DPMASTT (deal pricing header) + DPMAST1T (deal pricing detail)

### Data Sources

**DPMASTT** — Deal Pricing Master (807,880 rows total)
- Links items (`DPITEM`) to price codes (`DPPRCD`) or price groups (`DPPGRP`) per warehouse (`DPWHSE`)
- Has begin/end dates (`DPBDAT`/`DPEDAT`) for deal validity
- Each row has either a price code OR a price group, never both
- `DPIDENTITY` joins to `DPMAST1T.ID_DPMAST` for actual price values

**DPMAST1T** — Deal Pricing Detail (802,493 rows total)
- Contains `FRONTLINEPRICE` (the case price used for migration)
- Also has 20 `SELLINGPRICE01-20` columns and 20 `REBATEAMOUNT01-20` columns (not used — mostly zeros)
- `REBATEPERCENT` and `MINIMUMREBATEPRICE` available but not currently mapped

### Mapping Logic

| Column | Field | Source | Type |
|--------|-------|--------|------|
| A | Item | ITEMT.PACKAGE_DESCRIPTION (via DPMASTT.DPITEM) | Data |
| B | Pricelist | Pricelist tab name (matched via VIP Price Code or Price Group) | Data |
| C | Price (Discounted) | DPMAST1T.FRONTLINEPRICE (max across warehouses) | Data |
| D | Price (Default) | VLOOKUP to Product tab Default Price (col J) | Formula |
| E | Discount % | `=((D-C)/D)*100` | Formula |
| F | Pricelist Key | VLOOKUP to Pricelist tab Mapping Key (col P) | Formula |
| G | Item Key | VLOOKUP to Product tab Mapping Key (col D) | Formula |

### Filtering & Deduplication
- **Date filter**: Only deals with `DPEDAT >= 20250101` (current/recent)
- **Active items only**: Joined to ITEMT where `ITEM_STATUS IN ('A', 'S')`
- **Non-zero prices only**: Excluded rows where `FRONTLINEPRICE = 0`
- **Known pricelists only**: Excluded items whose price code/group doesn't match a pricelist in the Pricelist tab
- **Warehouse dedup**: When the same item+pricelist has different prices across warehouses, the MAX price is used

### Volume Breakdown
- Price code-based items: 154 price codes → matched to pricelists
- Price group-based items: 370 price groups → matched to pricelists
- Top pricelists by item count:
  - GOLDRING-CIV OFF PREM: 567 items
  - GDC-PUBLIX: 237 items
  - GOLDRING-ON PREMISE: 226 items
  - GDC-WALMART: 221 items
  - HUNT-PUBLIX: 206 items

### Data Quality Notes
- **338 pricelists have no item pricing** — These pricelists exist in the Pricelist tab but have no matching deal pricing rows in DPMASTT for active items. They may be inactive, header-only, or use a different pricing mechanism.
- **Warehouse price variance**: 6,268 item+price code combos have different prices across warehouses. MAX was chosen to avoid $0.00 prices (common in some warehouse records). Gulf should confirm this approach.
- **SELLINGPRICE columns unused**: DPMAST1T has 20 selling price tiers — only FRONTLINEPRICE is currently mapped. If Gulf uses tiered pricing, these may need separate handling.

### Follow-Up Questions
- [ ] Is FRONTLINEPRICE the correct price to use for the case/deal price, or should one of the SELLINGPRICE01-20 columns be used instead?
- [ ] For items with different prices across warehouses, is MAX the right dedup strategy? Or should pricing be warehouse-specific?
- [ ] Should expired deal pricing (pre-2025) be included for historical reference, or is current pricing sufficient?
- [ ] Are the 338 pricelists with no items expected to be empty, or is there a different pricing source for those?
- [ ] Should REBATEAMOUNT and REBATEPERCENT from DPMAST1T be captured anywhere in the migration?

---

## Tab: Route

### Overview
Delivery/sales routes, typically named by the assigned driver.

- **Rows written**: 308
- **Driver routes**: 255 (named after drivers)
- **Special routes**: 53 (samples, open routes, overflow, etc.)
- **Source table**: HDRROUTET (Route Master)

### Data Sources

**HDRROUTET** — Route Master (308 rows, 0 deleted)
- `ROUTE` (char 5) — Route code (e.g., "104", "497", "H26")
- `DESCRIPTION` (char 14) — Route description, typically driver name in "LAST, FIRST" format
- Route codes often match driver codes in HDRDRT

**HDRDRT** — Driver Master (518 drivers)
- `DRIVER` (char 5) — Driver code (matches route code for 241/308 routes)
- `DRIVER_NAME` (char 14) — Driver name

### Mapping Logic

| Column | Field | Source | Type |
|--------|-------|--------|------|
| A | Route Name | `"{ROUTE} - {DESCRIPTION}"` (e.g., "104 - BALDWIN, PAUL") | Data |
| B | Mapping Key | `=CONCAT("R-",J{row})` | Formula |
| C | Vehicle Name | Not available in VIP | Empty |
| D | Driver Name | HDRDRT.DRIVER_NAME flipped to "First Last" format | Data |
| E | Active | TRUE for all routes | Data |
| F | Day of Week | Not in VIP data | Empty |
| G | Deliveries Per Day | Not in VIP data | Empty |
| H | Vehicle | VLOOKUP to VehicleEquipment tab (pending) | Formula |
| I | Driver | VLOOKUP driver name to User tab Mapping Key | Formula |
| J | Record Number | Sequential 1, 2, 3... | Data |

### Data Quality Notes
- **Route names = driver names** — VIP routes are named after drivers (e.g., "BALDWIN, PAUL"). This is common in beverage distribution but may need renaming for Ohanafy if routes should be geographic or day-based.
- **No day-of-week or frequency data** — VIP doesn't store route scheduling at the route master level.
- **No vehicle assignments** — VehicleEquipment tab not yet populated; vehicle lookup formulas are placeholder.
- **Special routes**: 53 routes are samples, open routes, or overflow (e.g., "GGDC SAMPLES", "OPEN RT 951") — these may not be real delivery routes.

### Follow-Up Questions
- [ ] Should routes be renamed from driver names to something more descriptive (geographic, day-based)?
- [ ] Are sample routes (GGDC SAMPLES, GDC SAMPLES, etc.) needed in the migration?
- [ ] Is there day-of-week or frequency data elsewhere in VIP that should be mapped?
- [ ] Should inactive/former driver routes be excluded?

---

## Tab: AccountRoute

### Overview
Links customers to their assigned delivery routes.

- **Rows written**: 15,358
- **Distinct routes used**: 228 (of 308 total routes)
- **Source**: BRATTT.CMBRT (customer route assignment field)

### Data Sources

**BRATTT** — Customer Master
- `CMBRT` (route code) — Links each customer to a route from HDRROUTET
- 15,358 active customers have a route assignment (of 15,337 total active)
- All 228 distinct CMBRT values match routes in HDRROUTET

### Mapping Logic

| Column | Field | Source | Type |
|--------|-------|--------|------|
| A | Route Name | Route tab name (matched via CMBRT → HDRROUTET.ROUTE) | Data |
| B | Customer Name | BRATTT.CMDBA (customer DBA name) | Data |
| C | Route Key | VLOOKUP to Route tab Mapping Key (col B) | Formula |
| D | Customer Key | VLOOKUP to Customer tab Mapping Key (col E) | Formula |

### Volume Breakdown
Top routes by customer count:
- 497 - GGDC SAMPLES: 238 customers
- 197 - GDC SAMPLES: 203 customers
- 951 - OPEN RT 951: 190 customers
- 797 - ABC SAMPLES: 186 customers
- 716 - OPEN RT 716: 178 customers

### Data Quality Notes
- **Near-complete coverage**: 15,358/15,337 active customers have route assignments (>99.9%).
- **Sample routes dominate top spots** — The 5 largest routes are all sample/open routes, not real delivery routes. Gulf should confirm if these should be migrated.
- **No stop order** — VIP doesn't store customer stop sequence in BRATTT. The Ohanafy `Stop_Order__c` field is not populated. PKSTOPT has 2,621 stop records but uses a different key structure.

### Follow-Up Questions
- [ ] Should customers assigned to sample routes (GGDC SAMPLES, GDC SAMPLES, etc.) be included in AccountRoute?
- [ ] Is there stop order/sequence data in PKSTOPT or elsewhere that should be mapped to `Stop_Order__c`?
- [ ] Should Start_Time and End_Time be populated for any routes?

---

## Tab: Promotions

### Overview
Quantity discount promotions linking items to promotional pricing with date ranges. This is one of the most complex data areas in the VIP system.

- **Rows written**: 24,448
- **Distinct promotions**: 734
- **Source tables**: DISCWKSTT (promotion headers) + DISCOUTT (promotion-item detail) + DPMASTT/DPMAST1T (deal economics) + ITEMT (item names)
- **Economics enrichment**: 55.5% of rows have real pricing data from deployment tables

### VIP Promotion Data Architecture

VIP has a multi-table promotion system:

1. **DISCWKSTT** (766 rows) — Discount Worksheets = **Promotion headers**
   - `DISCOUNTID` (e.g., "SM1467", "AB193") — Unique promotion identifier
   - `DISCDESC` — Description with embedded deal terms (e.g., "LITE/COORS 24PK 14CS QD", "RECOVERY 5CS QD $3 OFF")
   - `STARTDATE`/`ENDDATE` — Promotion date range
   - `DISCOUNTTYPE` — Type code (A = All/broad)
   - No explicit discount amount field — deal terms are embedded in the description

2. **DISCOUTT** (37,293 rows) — Discount Output = **Promotion-item detail**
   - `DISCGRP2` → Links to DISCWKSTT.DISCOUNTID
   - `PRODID` — Item code (matches ITEMT.ITEM_CODE, 1,000 unique items)
   - `TYPEID` — A (4,159), C (14,439), G (18,695) — likely All/Customer/Group level
   - `STARTDATE`/`ENDDATE` — Matches parent promotion dates

3. **DEPLWKST** (856 rows) — Deployment worksheets with FRONTLINE price and REBATEPCT, but no clean join to DISCWKSTT
4. **PENDPRICT** (956 rows) — Pending prices with case/each pricing
5. **ALLOCHT** (8,255 rows) — Allocation headers for stock/budget tracking
6. **PENDDSINT** (409 rows) — Pending discount pricing with 15 price break points

### Mapping Logic (17 columns)

| Column | Field | Source | Type |
|--------|-------|--------|------|
| A | Promotion Name | `"{DISCOUNTID} - {DISCDESC}"` | Data |
| B | Deal Description | Raw DISCDESC from DISCWKSTT | Data |
| C | Deal Type | Parsed from description (see below) | Data |
| D | Item | ITEMT.PACKAGE_DESCRIPTION (via DISCOUTT.PRODID) | Data |
| E | Brand | BRANDT.BRAND_NAME (via ITEMT.BRAND_CODE) | Data |
| F | Method | "Billback $" or "Billback %" from DPMASTT.DPMETHOD (1=dollar, 2=pct) | Data |
| G | Selling Price | DPMAST1T.SELLINGPRICE01 — the promo case price | Data |
| H | Rebate $/Case | DPMAST1T.REBATEAMOUNT01 — per-case rebate for dollar-off deals | Data |
| I | Rebate % | DPMAST1T.REBATEPERCENT — rebate percentage for pct deals | Data |
| J | Frontline Price | DPMAST1T.FRONTLINEPRICE — base/list price (used for pct deals) | Data |
| K | Qty Min | Case quantity parsed from description (e.g., "10CS" → 10) | Data |
| L | Qty Max | Second quantity if tiered (e.g., "5/50 CS" → 50) | Data |
| M | Start Date | DISCWKSTT.STARTDATE formatted as YYYY-MM-DD | Data |
| N | End Date | DISCWKSTT.ENDDATE formatted as YYYY-MM-DD | Data |
| O | Applies To | Scope type from DISCOUTT.TYPEID (All Customers / Price Code / Price Group) | Data |
| P | Scope Detail | Price group or code name (e.g., "RB 2026 BD+P" for Red Bull tier) | Data |
| Q | Promo ID | DISCWKSTT.DISCOUNTID for reference/dedup | Data |

### Deal Type Classification

Deal types are parsed from the promotion description keywords:

| Deal Type | Count | Pattern |
|-----------|-------|---------|
| Quantity Discount | 8,954 | Contains "QD" (no $ amount) |
| Promotion | 5,073 | No recognizable pattern |
| Quantity Discount + $ Off | 4,101 | Contains "QD" + "$X" |
| Buy X Get Y | 2,692 | Contains "BUY" + "GET" |
| Fixed Price | 2,117 | Contains "$X" (no "QD" or "OFF") |
| Constellation Program | 878 | Contains "CONST" |
| Tiered Program | 351 | Contains "DIAMOND"/"PLATINUM"/"GOLD"/"BRONZE" |
| Mix & Match | 244 | Contains "PICK" |
| $ Off | 38 | Contains "$X OFF" (no "QD") |

### Scope / Applies To

DISCOUTT.TYPEID determines who the promotion applies to:

| Type | Meaning | Count | CODEID Maps To |
|------|---------|-------|----------------|
| A | All Customers | 4,159 rows (153 promos) | Appears to be item/account-level codes |
| C | Price Code | 14,439 rows (465 promos) | HDRPRCODT price codes (e.g., "01" = GOLDRING-CIV OFF PREM) |
| G | Price Group | 18,695 rows (172 promos) | HDRPRGRPT price groups (e.g., "RD" = RB 2026 BD+P+AC) |

### Description Parsing

VIP promotion descriptions embed deal terms in free text. Common patterns parsed:
- **Quantity**: `{N}CS QD` or `{N} CS` or `{N}/{M} CS QD` (tiered) → Qty Min/Max
- **Dollar discount**: `${X}` or `${X.XX} OFF` → Discount column
- **Examples**:
  - "LITE/COORS 24PK 14CS QD" → qty=14, no $
  - "RECOVERY 5CS QD $3 OFF" → qty=5, $=3.00
  - "COSTCO 10CS $0.82" → qty=10, $=0.82
  - "TKM CADDIE 8PK 3/10 CS QD" → qty_min=3, qty_max=10
  - "RB 2025 DIAMOND + P+ AC PP2" → no quantity or $ (complex Red Bull program)

### Deal Economics (DPMASTT/DPMAST1T Join)

The actual pricing data lives in the deployment master tables, NOT in the promotion description text:

- **Join path**: DISCOUTT → DPMASTT (on item + price group/code + date overlap) → DPMAST1T (on DPIDENTITY = ID_DPMAST)
- **Warehouse filter**: `DPWHSE='1'` to avoid row fan-out (all warehouses have identical economics)
- **Date overlap**: DPMASTT.DPBDAT <= DISCOUTT.ENDDATE AND DPMASTT.DPEDAT >= DISCOUTT.STARTDATE
- **TYPEID routing**: G → match on DPPGRP, C → match on DPPRCD, A → no match (economics unavailable)

**Method breakdown** (for 13,580 matched rows):
| Method | DPMETHOD | Count | Key Fields |
|--------|----------|-------|------------|
| Billback $ | 1 | 7,514 | SELLINGPRICE01 = promo price, REBATEAMOUNT01 = $/case rebate |
| Billback % | 2 | 6,066 | FRONTLINEPRICE = base price, REBATEPERCENT = rebate % |

- **All deals are billbacks** (DPBORW = 'B' across entire DPMASTT table). No off-invoice pricing found.
- **10,868 rows (44.5%) have no economics match** — primarily Type A (All Customers) promos and items without a deployed price for the promo period.

### Coverage Statistics
- **Economics enrichment**: 13,580/24,448 (55.5%) — rows with real pricing from DPMASTT/DPMAST1T
- **48 promo IDs skipped** — Present in DISCOUTT but no matching header in DISCWKSTT

### Ohanafy Promotion Model (for reference)

The Ohanafy `Promotion__c` object supports:
- `Discount_Dollars__c` / `Discount_Percent__c` with `Discount_Type__c` (Percent, Dollar)
- `Customer__c` (account-specific promotions)
- `Territory__c` (territory-level promotions)
- `Is_Front_Line__c`, `Is_Auto_Apply__c`, `Is_Chain_Level__c`, `Is_Straight_Line__c`
- `Promotion_Item__c` child records with Item, Case_Quantity, Discounted_Case_Price, Type (Reward/Criteria)

### Data Quality Notes
- **Real pricing now included** — 55.5% of rows have actual selling prices and rebate amounts from DPMASTT/DPMAST1T deployment tables. This replaces the unreliable text-parsed dollar amounts.
- **44.5% missing economics** — Primarily Type A (All Customers) promos where DISCOUTT.CODEID doesn't match a DPMASTT price group/code, and items without a deployed price for the promo window. These rows have blank Method/Selling Price/Rebate columns.
- **All deals are billbacks** — Every row in DPMASTT has DPBORW='B'. VIP has no off-invoice pricing in this dataset.
- **Deal Type still from description** — The Deal Type column (Quantity Discount, Buy X Get Y, etc.) is still parsed from the free-text description. It provides useful categorization even though the actual economics now come from structured data.
- **Volume tiers exist but not shown** — DPMAST1T has 20 SELLINGPRICE/REBATEAMOUNT tiers. We only show tier 01 (primary). ~19% of rows have a populated tier 02 with different pricing for higher volumes.

### Follow-Up Questions
- [ ] **44.5% missing economics**: Type A (All Customers) promos and some items don't match DPMASTT. Should Gulf review these for manual pricing entry, or are they informational-only promos?
- [ ] **Volume tiers**: Should we include tier 02 pricing (buy more, pay less) for the ~19% of items that have it? Could add Selling Price 02 and Rebate 02 columns.
- [ ] How should the DISCOUTT TYPEID (A/C/G) map to Ohanafy's promotion scope (Customer, Territory, Chain Level)?
- [ ] For tiered quantity promotions (e.g., "5/50 CS QD"), does Qty Min mean "buy 5 OR 50" or "buy 5 TO 50"?
- [ ] Should promotions that have already expired (end date in 2025) be excluded, or kept for historical reference?
- [ ] Are ALLOCHT allocation records (8,255 rows with stock/budget tracking) needed for the Promotions migration or a separate Allocations tab?
- [ ] The Red Bull promotions (251BD, 251BZ, etc.) are complex tiered billback programs — now with real pricing shown, do they look correct?

---

*This document will be updated as each additional tab is completed.*
