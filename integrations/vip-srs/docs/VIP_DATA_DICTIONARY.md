# VIP SRS Data Dictionary

Reference for building Salesforce reports and dashboards on VIP-integrated data.

**Source of truth:** The transform scripts in `scripts/` are authoritative for field mappings. The VIP_AGENT_HANDOFF.md spec is stale in several places (see ROADMAP Gotcha #22).

**Last updated:** 2026-04-14

---

## How to Read This Document

- **API Name** — the Salesforce field API name. Prefix `ohfy__` = managed package field; no prefix or `VIP_` prefix = custom unmanaged field.
- **Type** — Salesforce field data type. Currency fields are marked with `$`.
- **Source** — VIP file type and column name, or `(calculated)` / `(hardcoded)` if derived.
- **Notes** — Picklist crosswalks, formatting rules, constraints.
- Fields marked **create-only** are master-detail relationships that can only be set on initial record creation.

---

## Quick Reference: Currency Fields

These are the fields you aggregate for revenue and pricing reports.

| Object | Field | What It Represents |
|--------|-------|--------------------|
| Depletion__c | `VIP_Net_Price__c` | Per-unit net price (can be negative for returns) |
| Depletion__c | `VIP_Net_Amount__c` | **Extended net amount** = Qty x NetPrice. This is the revenue line total. |
| Placement__c | `ohfy__Last_Invoice_Price__c` | Net price from the most recent transaction for this Account x Item |

**For revenue reporting, use `VIP_Net_Amount__c` on Depletion__c.** Do not sum `VIP_Net_Price__c` — that's per-unit price, not line totals.

---

## Quick Reference: Date Fields

| Category | Fields | Meaning |
|----------|--------|---------|
| **Transaction dates** | `ohfy__Date__c` (Depletion), `ohfy__Stamped_Date__c` (History), `ohfy__Date__c` (Adjustment) | When the transaction occurred |
| **Reporting period** | `VIP_From_Date__c`, `VIP_To_Date__c` | The VIP file's reporting window (e.g., daily for SLSDA, monthly for CTLDA) |
| **File date** | `VIP_File_Date__c` | Date the pipeline ran. Used for stale record cleanup, NOT the transaction date. |
| **Placement dates** | `ohfy__First_Sold_Date__c`, `ohfy__Last_Sold_Date__c` | Earliest and latest transaction dates across all depletions for an Account x Item |
| **Allocation period** | `ohfy__Start_Date__c`, `ohfy__End_Date__c` | First and last day of the allocation month |

---

## Object Relationship Map

```
Account (Supplier)
  └── Item_Line__c (ohfy__Supplier__r)
        └── Item_Type__c (ohfy__Item_Line__r)
              └── Item__c (ohfy__Item_Type__r, ohfy__Item_Line__r)

Account (Chain Banner)
  └── Account (Distributed Customer) via ohfy__Chain_Banner__r

Account (Distributor / Customer)
  ├── Contact (Distributor Primary)
  └── Location__c

Account (Distributed Customer)
  ├── Contact (Buyer)
  ├── Depletion__c (ohfy__Customer__r)
  └── Placement__c (ohfy__Account__r) ← create-only

Item__c
  ├── Depletion__c (ohfy__Item__r)
  ├── Placement__c (ohfy__Item__r) ← create-only
  ├── Inventory__c (ohfy__Item__r) ← create-only
  └── Allocation__c (ohfy__Item__r)

Location__c
  ├── Account (Distributed Customer) via ohfy__Fulfillment_Location__r
  ├── Inventory__c (ohfy__Location__r)
  └── Allocation__c (ohfy__Location__r)

Inventory__c
  ├── Inventory_History__c (ohfy__Inventory__r)
  └── Inventory_Adjustment__c (ohfy__Inventory__r)
```

### Report Join Paths

| Report Goal | Join Path |
|-------------|-----------|
| Depletions by Brand | Depletion → Item → Item_Line (brand) |
| Depletions by Account | Depletion → Account (Customer) |
| Depletions by Chain | Depletion → Account → Chain_Banner (Account) |
| Depletions by Category | Depletion → Item → Item_Type → Category__c |
| Placements by Account | Placement → Account |
| Placements by Item | Placement → Item → Item_Line |
| Inventory by Item | Inventory → Item |
| Inventory trend | Inventory_History → Inventory → Item |
| Allocations by Item | Allocation → Item |
| Allocations by Location | Allocation → Location |

---

## Account (4 record types)

Stores all parties in the supply chain. VIP data creates 4 distinct record types.

### Supplier (Record Type: n/a — uses default)

One record per supplier, created from customer config (not from VIP files).

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `ohfy__External_ID__c` | Text | Config: `supplier.code` | Format: `SUP:{code}` (e.g., `SUP:ARG`) |
| `Name` | Text | Config: `supplier.name` | |
| `ohfy__Legal_Name__c` | Text | Config: `supplier.legalName` | |
| `Type` | Text | (hardcoded) | `Supplier` |
| `BillingStreet/City/State/PostalCode` | Text | Config: `supplier.address.*` | |
| `Phone` | Phone | Config: `supplier.phone` | |
| `Website` | URL | Config: `supplier.website` | |
| `ohfy__Is_Active__c` | Checkbox | (hardcoded) | `true` |
| `AccountSource` | Text | (hardcoded) | `VIP SRS` |

**External ID:** `SUP:{SupplierCode}` on `ohfy__External_ID__c`

---

### Chain Banner (Record Type: Chain_Banner)

Parent accounts for retail chains. SRSCHAIN file. ~6,633 rows per file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `ohfy__External_ID__c` | Text | SRSCHAIN: Chain | Format: `CHN:{Chain}` |
| `Name` | Text | SRSCHAIN: Desc | Title case |
| `ohfy__Legal_Name__c` | Text | SRSCHAIN: Desc | Same as Name |
| `Is_Chain_Banner__c` | Checkbox | (hardcoded) | `true` |
| `ohfy__Retail_Type__c` | Text | (hardcoded) | `Chain` |
| `ohfy__Is_Active__c` | Checkbox | (hardcoded) | `true` |
| `Type` | Text | (hardcoded) | `Chain Banner` |
| `AccountSource` | Text | (hardcoded) | `VIP SRS` |

**External ID:** `CHN:{Chain}` on `ohfy__External_ID__c`

---

### Distributor / Customer (Record Type: Customer)

The supplier's direct customers — distributors and wholesalers. DISTDA file. 1 row per distributor.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `ohfy__External_ID__c` | Text | DISTDA: DistId | Format: `DST:{DistId}` |
| `Name` | Text | DISTDA: Distributor Name | |
| `ohfy__Legal_Name__c` | Text | DISTDA: Distributor Name | |
| `ohfy__Customer_Number__c` | Text | DISTDA: DistId | Raw distributor ID |
| `Type` | Text | (hardcoded) | `Customer` |
| `ohfy__Retail_Type__c` | Text | (hardcoded) | `Distributor` |
| `BillingStreet/City/State/PostalCode/Country` | Text | DISTDA: Street/City/State/Zip | Country defaults to `US` |
| `ShippingStreet/City/State/PostalCode/Country` | Text | DISTDA | Same as Billing |
| `Phone` | Phone | DISTDA: Phone | Formatted: `(XXX) XXX-XXXX` |
| `ohfy__Is_Active__c` | Checkbox | (hardcoded) | `true` |
| `AccountSource` | Text | (hardcoded) | `VIP SRS` |

**External ID:** `DST:{DistId}` on `ohfy__External_ID__c`

---

### Distributed Customer (Record Type: Distributed_Customer)

Retailers and outlets — the distributor's customers. Also includes a subset tagged as Distributors (ClassOfTrade 06/07/50). OUTDA file. ~36,587 rows per file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `ohfy__External_ID__c` | Text | OUTDA: DistId + Account | Format: `ACT:{DistId}:{Account}` |
| `ohfy__Customer_Number__c` | Text | OUTDA: Account | Raw account number |
| `Name` | Text | OUTDA: DBA | Doing-business-as name |
| `ohfy__Legal_Name__c` | Text | OUTDA: LicName or DBA | License name if present, else DBA |
| `BillingStreet` | Text | OUTDA: Addr1 + Addr2 | Combined if both present |
| `BillingCity/State/PostalCode/Country` | Text | OUTDA | Country defaults to `US` |
| `ShippingStreet/City/State/PostalCode/Country` | Text | OUTDA | Same as Billing |
| `Phone` | Phone | OUTDA: Phone | Formatted: `XXX-XXX-XXXX` |
| `ohfy__Chain_Banner__r` | Lookup | OUTDA: Chain | Links to `CHN:{Chain}` — blank if no chain |
| `ohfy__Market__c` | Picklist | OUTDA: ClassOfTrade | Crosswalk (see Crosswalks section). Restricted picklist — 14 CoT codes map to null. |
| `ohfy__Premise_Type__c` | Picklist | OUTDA: ClassOfTrade | `Off Premise` (codes 01-19) or `On Premise` (codes 21-43) |
| `ohfy__Retail_Type__c` | Picklist | OUTDA: ChainStatus | `C` → `Chain`, `I` or blank → `Independent` |
| `VIP_Salesman1__c` | Text(8) | OUTDA: Salesman1 | Distributor rep code (ROSM1). Skips `999` and `HOUSE`. |
| `VIP_Salesman2__c` | Text(8) | OUTDA: Salesman2 | Distributor rep code (ROSM2). May be blank. |
| `ohfy__Store_Number__c` | Text | OUTDA: Store | |
| `ohfy__Is_Active__c` | Checkbox | OUTDA: Status | `A` → true, `I`/`O` → false |
| `ohfy__ABC_License_Number__c` | Text | OUTDA: License | |
| `Type` | Text | (conditional) | `Customer` if CoT 06/07/50; `Distributed Customer` otherwise |
| `RecordTypeId` | ID | (conditional) | Customer RT if CoT 06/07/50; Distributed_Customer RT otherwise |
| `ohfy__Fulfillment_Location__r` | Lookup | OUTDA: DistId | Links to `LOC:{DistId}` (retailers only) |
| `AccountSource` | Text | (hardcoded) | `VIP SRS` |

**External ID:** `ACT:{DistId}:{Account}` on `ohfy__External_ID__c`

---

## Contact (2 types)

### Distributor Primary Contact

One contact per distributor. DISTDA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `External_ID__c` | Text | DISTDA: DistId | Format: `CON:{DistId}:DIST` |
| `FirstName` | Text | DISTDA: Contact 1 Name | Parsed: first word |
| `LastName` | Text | DISTDA: Contact 1 Name | Parsed: remaining words |
| `Email` | Email | DISTDA: Contact 1 Email | Skips `x@vtinfo.com` (placeholder) |
| `Account` (lookup) | Lookup | DISTDA: DistId | Links to `DST:{DistId}` |

**Skipped if:** Contact 1 Name is blank or `Default User`

---

### Buyer Contact

One contact per outlet account. OUTDA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `External_ID__c` | Text | OUTDA: DistId + Account | Format: `CON:{DistId}:{Account}` |
| `FirstName` | Text | OUTDA: Buyer | Parsed: first word |
| `LastName` | Text | OUTDA: Buyer | Parsed: remaining words; fallback `(Unknown)` |
| `Account` (lookup) | Lookup | OUTDA: DistId + Account | Links to `ACT:{DistId}:{Account}` |
| `ohfy__Is_Billing_Contact__c` | Checkbox | (hardcoded) | `true` |

**Note:** Contact inserts are currently blocked by the AccountTriggerMethods cascade issue. See known-issues.md.

---

## Item__c

Product master data. Created from ITM2DA (~65 rows per file), enriched by ITMDA (~102 rows per distributor).

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `ohfy__VIP_External_ID__c` | Text | ITM2DA: SupplierItem | Format: `ITM:{SupplierItem}` |
| `ohfy__Supplier_Number__c` | Text | ITM2DA: SupplierItem | Raw supplier item code |
| `Name` | Text | ITM2DA: Desc | Full item description |
| `ohfy__Case_GTIN__c` | Text | ITM2DA: CaseGTIN | Skipped if all zeros |
| `ohfy__Unit_GTIN__c` | Text | ITM2DA: RetailGTIN | Skipped if all zeros |
| `ohfy__Units_Per_Case__c` | Number | ITM2DA: Units | Integer |
| `ohfy__Retail_Units_Per_Case__c` | Number | ITM2DA: SellingUnits | Integer |
| `ohfy__Weight__c` | Number | ITM2DA: Weight | Decimal |
| `ohfy__Cases_Per_Pallet__c` | Number | ITM2DA: CasesPPallet1 | Only if > 0 |
| `ohfy__Package_Type__c` | Text | ITM2DA: PackageType | `BTL` → `Packaged` |
| `ohfy__Packaging_Type_Short_Name__c` | Text | ITM2DA: PackageSize | Human-readable package size |
| `ohfy__Type__c` | Text | ITM2DA: ContainerType | Crosswalk; default `Finished Good` |
| `ohfy__Packaging_Type__c` | Picklist | (hardcoded) | `Each` — required for depletion lookup filter |
| `ohfy__Is_Active__c` | Checkbox | ITM2DA: Status | `A` → true, `I` → false |
| `ohfy__UOM_In_Fluid_Ounces__c` | Number | ITM2DA: VolofUnit + VolUOM | ML × 0.033814 or direct OZ |
| `ohfy__UOM__c` | Picklist | (hardcoded) | `US Count` — required for depletion lookup filter |
| `ohfy__Item_Line__r` | Lookup | ITM2DA: BrandDesc | Links to `ILN:{BrandDesc}` |
| `ohfy__Item_Type__r` | Lookup | ITM2DA: BrandDesc + GenericCat3 | Links to `ITY:{BrandDesc}:{GenericCat3}` |

**Enrichment fields (from ITMDA, Script 04):**

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `ohfy__Item_Number__c` | Text | ITMDA: DistItem | Distributor's own SKU |
| `ohfy__SKU_Number__c` | Text | ITMDA: DistItem | Same as Item_Number |
| `ohfy__Short_Name__c` | Text | ITMDA: Description | Does NOT overwrite Name |
| `ohfy__UPC__c` | Text | ITMDA: GTIN | Skipped if all zeros |
| `ohfy__Unit_UPC__c` | Text | ITMDA: DistItemGTIN | Skipped if all zeros |

**External ID:** `ITM:{SupplierItem}` on `ohfy__VIP_External_ID__c`

---

## Item_Line__c

Brand grouping for items. ITM2DA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | ITM2DA: BrandDesc | Format: `ILN:{BrandDesc}` |
| `Name` | Text | ITM2DA: BrandDesc | Brand name |
| `ohfy__Type__c` | Text | (hardcoded) | `Finished Good` |
| `ohfy__Supplier__r` | Lookup | Config: supplierExternalId | Links to `SUP:{code}` |
| `VIP_File_Date__c` | Date | (input) | Pipeline run date |

**External ID:** `ILN:{BrandDesc}` on `VIP_External_ID__c`

---

## Item_Type__c

Category grouping for items within a brand. ITM2DA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | ITM2DA: BrandDesc + GenericCat3 | Format: `ITY:{BrandDesc}:{GenericCat3}` |
| `Name` | Text | ITM2DA: GenericCat3 | Category name |
| `ohfy__Item_Line__r` | Lookup | ITM2DA: BrandDesc | Links to `ILN:{BrandDesc}` |
| `ohfy__Type__c` | Text | (hardcoded) | `Finished Good` |
| `ohfy__Category__c` | Picklist | ITM2DA: GenericCat3 | Crosswalk: `GENERIC VOL` → `Vodka`; others pass through |
| `VIP_File_Date__c` | Date | (input) | Pipeline run date |

**External ID:** `ITY:{BrandDesc}:{GenericCat3}` on `VIP_External_ID__c`

---

## Location__c

Distributor warehouse locations. DISTDA file. 1 per distributor.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | DISTDA: DistId | Format: `LOC:{DistId}` |
| `ohfy__Location_Code__c` | Text | DISTDA: DistId | Raw dist ID (max 5 chars) |
| `Name` | Text | DISTDA: Distributor Name | |
| `ohfy__Location_Street__c` | Text | DISTDA: Street | |
| `ohfy__Location_City__c` | Text | DISTDA: City | |
| `ohfy__Location_State__c` | Text | DISTDA: State | |
| `ohfy__Location_Postal_Code__c` | Text | DISTDA: Zip | |
| `ohfy__Type__c` | Picklist | (hardcoded) | `Warehouse` |
| `ohfy__Is_Active__c` | Checkbox | (hardcoded) | `true` |
| `ohfy__Is_Sellable__c` | Checkbox | (hardcoded) | `true` |
| `ohfy__Is_Finished_Good__c` | Checkbox | (hardcoded) | `true` |

**External ID:** `LOC:{DistId}` on `VIP_External_ID__c`

---

## Depletion__c

Distributor-to-retailer sales transactions. Each row = one invoice line item. SLSDA file. ~110 rows per file per distributor.

**This is NOT supplier-to-distributor invoicing.** VIP SLSDA = depletions (sell-through). Invoice__c is a separate data source.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | SLSDA: composite | Format: `DEP:{DistId}:{InvoiceNbr}:{AcctNbr}:{SuppItem}:{UOM}` (`:NEG` suffix if qty < 0) |
| `ohfy__Customer__r` | Lookup (master-detail) | SLSDA: DistId + AcctNbr | Links to `ACT:{DistId}:{AcctNbr}`. **Create-only.** |
| `ohfy__Item__r` | Lookup | SLSDA: SuppItem | Links to `ITM:{SuppItem}` |
| `ohfy__Case_Quantity__c` | Number | SLSDA: Qty | Set when UOM = C (cases) |
| `VIP_Unit_Quantity__c` | Number | SLSDA: Qty | Set when UOM = B (bottles) |
| `ohfy__Date__c` | Date | SLSDA: InvoiceDate | Transaction date |
| `VIP_Net_Price__c` | $ Currency | SLSDA: NetPrice | Per-unit net price. Can be negative (returns). |
| `VIP_Net_Amount__c` | $ Currency | (calculated) | **Qty x NetPrice.** Extended line total for revenue reporting. |
| `VIP_Invoice_Number__c` | Text | SLSDA: InvoiceNbr | |
| `VIP_From_Date__c` | Date | SLSDA: FromDate | Reporting period start |
| `VIP_To_Date__c` | Date | SLSDA: ToDate | Reporting period end |
| `VIP_File_Date__c` | Date | (input) | Pipeline run date |

**External ID:** `DEP:{DistId}:{InvoiceNbr}:{AcctNbr}:{SuppItem}:{UOM}` on `VIP_External_ID__c`

**Skipped rows:** SRS99 accounts, XXXXXX items, zero qty + zero price

---

## Placement__c

Aggregated Account x Item relationships from depletion data. One record per unique distributor + account + item combination. SLSDA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | SLSDA: composite | Format: `PLC:{DistId}:{AcctNbr}:{SuppItem}` |
| `ohfy__Account__r` | Lookup (master-detail) | SLSDA: DistId + AcctNbr | Links to `ACT:{DistId}:{AcctNbr}`. **Create-only.** |
| `ohfy__Item__r` | Lookup (master-detail) | SLSDA: SuppItem | Links to `ITM:{SuppItem}`. **Create-only.** |
| `ohfy__First_Sold_Date__c` | Date | SLSDA: InvoiceDate | MIN(InvoiceDate) across all rows for this Account x Item |
| `ohfy__Last_Sold_Date__c` | Date | SLSDA: InvoiceDate | MAX(InvoiceDate) across all rows for this Account x Item |
| `ohfy__Last_Purchase_Date__c` | Date | SLSDA: InvoiceDate | Date of the latest transaction row |
| `ohfy__Last_Purchase_Quantity__c` | Number | SLSDA: Qty | Quantity from the latest transaction row |
| `ohfy__Last_Invoice_Price__c` | $ Currency | SLSDA: NetPrice | Net price from the latest transaction row |
| `ohfy__Is_Active__c` | Checkbox | (hardcoded) | `true` |
| `ohfy__Is_New_Placement__c` | Checkbox | (hardcoded) | `true` |
| `ohfy__Lost_Placement_After_Days__c` | Number | (hardcoded) | `60` — CSO reorder alert threshold |
| `VIP_File_Date__c` | Date | (input) | Pipeline run date |

**Formula fields (auto-calculated by managed package):**
- `Days_Since_Last_Order__c` — days between today and Last_Sold_Date
- `Lost_Placement_Date__c` — Last_Sold_Date + Lost_Placement_After_Days

**External ID:** `PLC:{DistId}:{AcctNbr}:{SuppItem}` on `VIP_External_ID__c`

---

## Inventory__c

Current stock levels. Only TransCode 10 (on-hand), latest posting date per item. INVDA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | INVDA: DistId + SupplierItem | Format: `IVT:{DistId}:{SupplierItem}` |
| `ohfy__Item__r` | Lookup (master-detail) | INVDA: SupplierItem | Links to `ITM:{SupplierItem}`. **Create-only.** |
| `ohfy__Location__r` | Lookup | INVDA: DistId | Links to `LOC:{DistId}` |
| `ohfy__Quantity_On_Hand__c` | Number | INVDA: Quantity (UOM=C) | Case quantity from latest posting date |
| `ohfy__Is_Active__c` | Checkbox | (hardcoded) | `true` |

**External ID:** `IVT:{DistId}:{SupplierItem}` on `VIP_External_ID__c`

---

## Inventory_History__c

Daily inventory snapshots. TransCode 10 (on-hand), 11 (committed), 12 (backordered). INVDA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | INVDA: composite | Format: `IVH:{DistId}:{SupplierItem}:{PostingDate}:{UOM}` |
| `ohfy__Stamped_Date__c` | Date | INVDA: PostingDate | Snapshot date |
| `ohfy__Item__r` | Lookup | INVDA: SupplierItem | Links to `ITM:{SupplierItem}` |
| `ohfy__Quantity_On_Hand__c` | Number | INVDA: Quantity | Direct |
| `ohfy__Inventory__r` | Lookup | INVDA: DistId + SupplierItem | Links to parent `IVT:{DistId}:{SupplierItem}` |
| `VIP_From_Date__c` | Date | INVDA: FromDate | Reporting period start |
| `VIP_To_Date__c` | Date | INVDA: ToDate | Reporting period end |
| `VIP_File_Date__c` | Date | (input) | Pipeline run date |

**External ID:** `IVH:{DistId}:{SupplierItem}:{PostingDate}:{UOM}` on `VIP_External_ID__c`

---

## Inventory_Adjustment__c

Inventory movements — purchases, transfers, returns, breakage, samples. TransCode 20-49, 99. INVDA file.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | INVDA: composite | Format: `IVA:{DistId}:{SupplierItem}:{TransCode}:{TransDate}:{UOM}` |
| `ohfy__Type__c` | Picklist | INVDA: TransCode | `Addition` or `Subtraction` (see TransCode crosswalk) |
| `ohfy__Reason__c` | Picklist | INVDA: TransCode | Purchase, Transfer, Return, Breakage, Sample, Adjustment |
| `ohfy__Status__c` | Picklist | (hardcoded) | `Complete` |
| `ohfy__Date__c` | Date | INVDA: TransDate | Movement date |
| `ohfy__Quantity_Change__c` | Number | INVDA: Quantity | Can be negative |
| `ohfy__Inventory__r` | Lookup | INVDA: DistId + SupplierItem | Links to parent `IVT:{DistId}:{SupplierItem}` |
| `VIP_From_Date__c` | Date | INVDA: FromDate | Reporting period start |
| `VIP_To_Date__c` | Date | INVDA: ToDate | Reporting period end |
| `VIP_File_Date__c` | Date | (input) | Pipeline run date |

**Skipped TransCodes:** 50-55, 59, 70, 80 (MTD aggregates, future states)

**External ID:** `IVA:{DistId}:{SupplierItem}:{TransCode}:{TransDate}:{UOM}` on `VIP_External_ID__c`

---

## Allocation__c

Monthly quantity allocations by distributor and item. CTLDA file. ~24 rows per file per distributor.

| API Name | Type | Source | Notes |
|----------|------|--------|-------|
| `VIP_External_ID__c` | Text | CTLDA: composite | Format: `ALC:{DistId}:{SupplierItem}:{ControlDate}:{UOM}` |
| `ohfy__Item__r` | Lookup | CTLDA: SupplierItem | Links to `ITM:{SupplierItem}` |
| `ohfy__Location__r` | Lookup | CTLDA: DistId | Links to `LOC:{DistId}` |
| `ohfy__Allocated_Case_Amount__c` | Number | CTLDA: Quantity | Integer — **no dollar value, quantity only** |
| `ohfy__Start_Date__c` | Date | CTLDA: ControlDate | First day of month |
| `ohfy__End_Date__c` | Date | CTLDA: ControlDate | Last day of month |
| `ohfy__Is_Active__c` | Checkbox | (hardcoded) | `true` |
| `VIP_From_Date__c` | Date | CTLDA: ControlDate | First day of month |
| `VIP_To_Date__c` | Date | CTLDA: ControlDate | Last day of month |
| `VIP_File_Date__c` | Date | (input) | Pipeline run date |

**External ID:** `ALC:{DistId}:{SupplierItem}:{ControlDate}:{UOM}` on `VIP_External_ID__c`

---

## Crosswalk Reference

### Class of Trade → Market + Premise Type

Used by Script 05 (OUTDA Accounts). 46 VIP codes → 22 Market picklist values.

| CoT Code | Market | Premise Type |
|----------|--------|-------------|
| 01 | Grocery/Supermarket | Off Premise |
| 02 | Liquor Store | Off Premise |
| 03 | Convenience Store | Off Premise |
| 04 | *(null)* | Off Premise |
| 05 | Drug Store | Off Premise |
| 06 | *(null — Distributor)* | *(null)* |
| 07 | *(null — Distributor)* | *(null)* |
| 08 | Mass Merchandise | Off Premise |
| 09 | Club Store | Off Premise |
| 10 | Wholesale Club | Off Premise |
| 11 | Tobacco Store | Off Premise |
| 12 | Gas Station | Off Premise |
| 13 | Dollar Store | Off Premise |
| 14 | *(null)* | Off Premise |
| 15 | *(null)* | Off Premise |
| 16 | Superette/Small Grocery | Off Premise |
| 17 | *(null)* | Off Premise |
| 18 | *(null)* | Off Premise |
| 19 | Other On Premise | Off Premise |
| 21 | Bars/Clubs/Taverns | On Premise |
| 22 | Restaurant/Casual Dining | On Premise |
| 23 | Restaurant/Fine Dining | On Premise |
| 24 | Hotel/Motel | On Premise |
| 25 | Bowling/Recreation | On Premise |
| 26 | Golf/Country Club | On Premise |
| 27 | Airport | On Premise |
| 28 | Catering/Banquet | On Premise |
| 29 | *(null)* | On Premise |
| 30 | Arena/Stadium | On Premise |
| 31 | Casino | On Premise |
| 32 | Cruise Line | On Premise |
| 33 | Movie Theater | On Premise |
| 34 | Night Club | On Premise |
| 35 | Fast Food/Quick Service | On Premise |
| 36 | Sports Bar | On Premise |
| 37 | *(null)* | On Premise |
| 38 | *(null)* | On Premise |
| 39 | Other On Premise | On Premise |
| 40 | *(null)* | On Premise |
| 41 | *(null)* | On Premise |
| 42 | Amusement/Theme Park | On Premise |
| 43 | *(null)* | On Premise |
| 50 | *(null — Distributor)* | *(null)* |
| 99 | *(null)* | *(null)* |

*(null)* entries have no matching Salesforce picklist value. The account is created but `ohfy__Market__c` is left blank.

### Inventory TransCode → Type + Reason

Used by Script 06 (INVDA Adjustments).

| TransCode | Type | Reason |
|-----------|------|--------|
| 20 | Addition | Purchase |
| 21 | Subtraction | Return to Vendor |
| 30 | Addition | Transfer In |
| 31 | Subtraction | Transfer Out |
| 40 | Subtraction | Breakage |
| 41 | Subtraction | Sample |
| 42 | Subtraction | Adjustment |
| 49 | Addition | Adjustment |
| 99 | Addition | Adjustment |

**Skipped:** 10-12 (on-hand/committed/backordered — goes to Inventory/History), 50-55/59/70/80 (MTD aggregates)

### Category Crosswalk (Item_Type__c)

Most GenericCat3 values pass through directly to `ohfy__Category__c`. Exceptions:

| VIP GenericCat3 | Salesforce Category__c |
|-----------------|----------------------|
| `GENERIC VOL` | `Vodka` |

---

## Data Freshness and Sync Cadence

- **Daily sync:** SLSDA (depletions), OUTDA (outlets), INVDA (inventory) are delivered daily via SFTP.
- **Monthly sync:** CTLDA (allocations) is delivered monthly.
- **Reference data:** SRSCHAIN (chains), ITM2DA (items), DISTDA (distributors), ITMDA (enrichment) are delivered daily but change infrequently.
- **`VIP_File_Date__c`** stamps when the pipeline last processed each record. Records not present in the latest file keep their old file date. The stale cleanup script (Script 09) deletes records with file dates older than the current run, scoped by reporting period.
- **Idempotent upserts:** Re-running the same file produces the same records (upsert by external ID). No duplicates.

---

## SLSDA Dollar Fields Not Currently Mapped

The following fields exist in VIP SLSDA source data but are **not mapped** to Salesforce. They can be added as custom fields if the team needs them for reporting.

| VIP Column | Description | Notes |
|------------|-------------|-------|
| `Front` | List/front price per unit | Reference price — may differ from NetPrice |
| `NetPrice4` | Net price with 4-decimal precision | Higher precision variant of NetPrice |
| `Deposit` | Container deposit amount | |
| `Crv` | CA container redemption value | California-specific |
| `LocalTax` | Local tax amount | |
| `AdtlChrg` | Additional charges/fees | |
