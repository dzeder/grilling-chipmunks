# VIP Pricing Deep Dive

> Analysis of VIP's pricing architecture based on Gulf Distributing's live database.
> Pricing is the most complex subsystem in VIP — spanning 160+ tables across price codes,
> price groups, deployment masters, discount worksheets, front-line pricing, post-off allowances,
> cost components, deposits, commissions, and promotions. This document maps it all to Ohanafy.

---

## Executive Summary

VIP's pricing is **not a single table with prices** — it's a multi-dimensional resolution engine. When an order is placed, VIP walks a matrix of territory, warehouse, on/off premise, market type, customer price code, product price group, and date to arrive at the final price. Then it layers on discounts, post-off allowances, deposits, CRV, handling charges, and front-line price tracking.

The system is built around a **worksheet pipeline** (WKSHEETT) that serves as the central hub — every price change flows through a wizard (Import → Worksheet → Output → Errors) before being committed to the live pricing tables.

**Key stats (Gulf Distributing):**

| Area | Primary Table(s) | Rows | Notes |
|------|-------------------|------|-------|
| Deployment Master (Tiered Pricing) | DPMAST1T + DPMASTT | 930,610 + 935,967 | The core pricing engine — 2,763 items x 153 price codes x 323 price groups x 11 warehouses |
| Monthly Costs | MQTCOST | 110,425 | Warehouse-level monthly cost tracking across 10 warehouses |
| Discount/Promotion Lines | DISCOUTT | 37,293 | 12,056 active, 25,237 expired — 1,004 unique items |
| Deposits/Fees | DEPOSITST | 6,339 | Keg (5,389) and standard (950) deposits, avg ~$50 |
| Pending Prices | PENDPRICT | 956 | Staged prices across 155 price codes, 5 unique items |
| Discount Worksheets (Pricelists) | DISCWKSTT | 766 | 735 unique worksheets, mostly type "A" |
| Deployment Worksheets | DEPLWKST | 856 | Front-line + rebate pricing worksheets |
| Price Groups | HDRPRGRPT | 379 | Red Bull tiers, retail chains, territory groups |
| Price Codes | HDRPRCODT | 154 | Division-level customer pricing tiers |
| Commission Profiles | COMMPROFT | 363 | Per-case and percentage-based commissions |
| Front-Line Price Worksheets | FLPWKST | 161 | Retail shelf price tracking |
| Cost Components | CCNAMET | 105 | FIFO, LIFO, Average, Laid-in, + 80 user-defined |
| Pending Costs | PENDCOSTT | 74 | Staged cost changes by warehouse |
| Time-Based Pricing | TIMEPR | 0 | Table exists but unused by Gulf |
| Special Pricing | SPRICET | 0 | Table exists but unused by Gulf |
| Price Books | PRBOOKHT | 0 | Table exists but unused by Gulf |

**Critical finding:** Gulf's primary pricing mechanism is the **Deployment Master** (DPMAST1T/DPMASTT) with 930K+ records — not the traditional price code/special price tables. This is a tiered rebate-based pricing system with up to 20 selling price tiers and 20 rebate amount tiers per item/code/group/warehouse combination.

---

## 1. Price Codes — HDRPRCODT (154 codes)

Price codes are the **customer-facing pricing dimension**. Each customer (or customer group) is assigned a price code that determines what base prices they see. Gulf has 154 price codes organized by division and trade channel.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| PRICECODE | char(5) | Code identifier (e.g., "01", "1W", "H3") |
| DESCRIPTION | char(30) | Human-readable name |
| PCCOSTNAME | char(6) | Cost basis used for this code (links to CCNAMET) |
| ALLOWDISCOUNTS | char(1) | Y/N — whether discounts apply on top of this code's prices |
| CHECKZEROPRICE | char(1) | W = Warn on $0, N = Allow $0 |
| CHECKZERODEPOSIT | char(1) | Check for zero deposit |

### Gulf's Price Code Structure

Price codes are organized by **division** (geographic business unit) and **trade channel**:

| Division | Code Range | Examples |
|----------|-----------|---------|
| **Goldring** (Mobile) | 01–03 | 01 = Civ Off Prem, 02 = Military, 03 = On Premise |
| **GDC** (Gulf Distributing Co) | 11–1Z | 11 = Off Prem, 12 = Military, 13 = On Prem, 14 = Walmart, 15 = Publix, 16 = Winn Dixie, 17 = Circle K, 18 = Dollar General, 19 = CVS, 1A = Walgreens, 1B = Target, 1C = Costco, 1D = Sam's Club, etc. |
| **ABC** (Alabama ABC Board) | 71–7Z | Mirrors GDC structure for ABC territory |
| **GSCA** (Gulf States Central AL) | 81–8Y | Same chain-specific breakout |
| **GDCB** (GDC Birmingham) | 91–9Y | Same chain-specific breakout |
| **Hunt** (Huntsville) | H1–HY | H1 = Off Prem (ALLOWDISCOUNTS=N), H2 = Military, H3 = On Prem |
| **GSCA-Talladega** | T1–T4 | Smaller division |
| **Special** | BN, EM | BN = unknown, EM = Employee Pricing |

**Key insight:** The same product has a different base price depending on the customer's price code. A Walmart store (code 14) pays a different case price than an independent retailer (code 11) or a military exchange (code 12). Each division replicates this pattern.

**Cost basis:** Most codes use default costing. Military codes (02, 12, 72, 82, 92, H2) use `USER15` — a custom cost basis, likely reflecting different landed cost for military channel sales.

---

## 2. Price Groups — HDRPRGRPT (379 groups)

Price groups are the **product-facing pricing dimension**. Products are assigned to price groups that determine pricing tiers. While price codes classify *customers*, price groups classify *products*.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| PRICEGROUP | char(5) | Group identifier |
| DESCRIPTION | char(30) | Human-readable name |
| PGCOSTNAME | char(6) | Cost basis for this group |
| PDAFLAG | char(1) | Mobile/PDA pricing flag |

### Gulf's Price Group Categories

| Category | Prefix | Count | Examples |
|----------|--------|-------|---------|
| **Florida** | FL | ~40 | FL03 (Retail Beer), FL08 (C-Store Beer), FL47 (On Prem Wine), FL87 (FL Promo) |
| **Alabama** | AL/5x | ~30 | 5A (Off Prem Beer), 5B (Military), 5C (On Prem) |
| **Red Bull Tiers** | RB | ~120 | 2025 tiers: Blue Diamond, Double Diamond, Diamond, Gold, Platinum, Triple Diamond — each with +P, +P+AC, Grocery variants. 2026 tiers: BD, D, DD, TD, P, G levels. Jackson On Prem: Classic, Deluxe, Elite, Premium, Select |
| **National Accounts** | RB/various | ~40 | Walmart, Publix, Winn Dixie, Target, Walgreens, Costco, Sam's Club, Circle K, Dollar General, CVS, Buffalo Wild Wings, Top Golf |
| **Military** | MIL | ~5 | AAFES, NEXCOM, DECA, Coast Guard |
| **Employee** | EM | 1 | Employee Pricing |
| **On Premise** | OP | ~5 | FL On Premise categories |

**Key insight:** Red Bull alone accounts for ~120 of the 379 price groups. Their tiered loyalty program (Blue Diamond → Triple Diamond) creates a complex pricing matrix where retailers earn better per-case pricing based on volume/commitment tiers. This is the single largest driver of pricing complexity.

---

## 3. Deployment Master — The Core Pricing Engine

### 3A. DPMASTT — Deployment Header (935,967 rows)

This is the **primary pricing table** in Gulf's VIP instance. Each row maps a product + price code/group + warehouse + date range to a pricing method.

**Scale:** 2,763 unique items x 153 price codes x 323 price groups x 11 warehouses — though not every combination exists.

| Column | Type | Description |
|--------|------|-------------|
| PRODID | char(6) | Product/item code |
| CODEID | char(5) | Price code (customer tier) |
| TYPEID | char(1) | C = Price Code, G = Price Group |
| COMPID | char(5) | Company ID |
| WHSEID | char(5) | Warehouse |
| METHOD | char(1) | 1 = Percentage-based, 2 = Tier-based |
| STARTDATE | numeric(8,0) | Effective start date |
| ENDDATE | numeric(8,0) | Effective end date |
| PROMOID | char(8) | Associated promotion ID |

### 3B. DPMAST1T — Deployment Detail / Tiered Pricing (930,610 rows)

Each header record links to a detail record containing the actual prices. This table has the most complex pricing structure in VIP — **20 selling price tiers and 20 rebate amount tiers** per row.

| Column | Type | Description |
|--------|------|-------------|
| FRONTLINEPRICE | numeric(7,2) | The retail shelf price (what consumer pays) |
| MINIMUMREBATEPRICE | numeric(7,2) | Floor price — rebate cannot reduce below this |
| REBATEPERCENT | numeric(5,2) | Percentage-based rebate (Method 1) |
| SELLINGPRICE01–20 | numeric(7,2) each | 20 tiered selling prices |
| REBATEAMOUNT01–20 | numeric(7,4) each | 20 corresponding rebate amounts (4 decimal precision) |

### How the Two Methods Work

**Method 1 — Percentage Rebate:**
- The distributor's price = FRONTLINEPRICE
- The rebate = FRONTLINEPRICE x REBATEPERCENT
- Net cost to distributor = FRONTLINEPRICE - rebate
- Example: Item 74513, frontline=$37.69, rebate=50% → net cost = $18.85

**Method 2 — Tiered Selling Prices + Rebate Amounts:**
- SELLINGPRICE01 = base tier price (e.g., $34.19)
- REBATEAMOUNT01 = rebate at that tier (e.g., $1.00)
- Higher tiers (02, 03, ...) represent different volume breaks or loyalty tiers
- Example: Item 87877, sell price 01=$34.19, rebate 01=$1.00 → net = $33.19

**The intersection with price groups:** The 20 tiers in DPMAST1T likely correspond to the tiered programs in HDRPRGRPT (particularly the Red Bull Diamond/Gold/Platinum tiers). A retailer in the "Gold" tier would use SELLINGPRICE at one position, while a "Diamond" retailer uses a different position.

### Why This Matters for Migration

The deployment master is the **single most important table** for pricing migration. It contains:
- 930K price points across all combinations
- Both the supplier-facing (rebate) and customer-facing (selling price) components
- Time-bounded pricing (start/end dates)
- Warehouse-specific pricing (different costs in Mobile vs. Birmingham vs. Huntsville)

---

## 4. Discount Worksheets (Pricelists) — DISCWKSTT (766 rows)

Discount worksheets are VIP's mechanism for defining and managing **named pricing programs**. These map to Ohanafy's `Pricelist__c` object.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| DISCOUNTID | char(10) | Unique discount code (e.g., "SM2094", "AB221", "TC50022") |
| DISCDESC | char(30) | Description (e.g., "RECOVERY 5CS QD $3 OFF") |
| DISCOUNTTYPE | char(1) | A = Standard discount, F = Front-line |
| DISCLVL | char(1) | Discount level (mostly "2") |
| BYBOTTLE | char(1) | Y/N — bottle-level pricing |
| STARTDATE / ENDDATE | numeric(8,0) | Effective date range |
| INDIPRICE | char(1) | Individual pricing flag |
| PERFDISC | char(1) | Performance discount flag |

### What the Data Shows

- **735 unique discount worksheets** (some have multiple date-range rows)
- **757 rows are type "A"** (standard), only **9 are type "F"** (front-line)
- Naming convention reveals the business logic:
  - `SM2094` = "RECOVERY 5CS QD $3 OFF" — buy 5 cases, get $3 off (Quantity Deal)
  - `TC50022` = "LITE 15/16 10CS QD 3/9-12/31" — Miller Lite 15/16pk, 10-case quantity deal, Mar-Dec
  - `AB221` = "3CS $10 QD" — 3-case $10 quantity deal
  - `SM2099` = "SAZERAC WELL 5/50 CS QD" — Sazerac well brand, 5 or 50 case tiers

These are **promotional pricing programs** — time-bounded, quantity-triggered discounts that suppliers fund and distributors execute.

---

## 5. Discount Output / Promotions — DISCOUTT (37,293 rows)

DISCOUTT is the **resolved output** of the discount wizard — it contains the actual item-level discount records that apply during order entry.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| PRODID | char(6) | Product/item code |
| CODEID | char(5) | Price code (customer tier) |
| DISCCODE | char(10) | Links back to DISCWKSTT discount program |
| TYPEID | char(1) | G = Group, C = Customer-specific, A = Account-level |
| DISCGRP2–4 | char(10) | Additional discount group hierarchies |
| STARTDATE / ENDDATE | numeric(8,0) | Effective dates |

### Breakdown

| Dimension | Value |
|-----------|-------|
| **Total records** | 37,293 |
| **Active** (end date >= today) | 12,056 (32%) |
| **Expired** | 25,237 (68%) |
| **Unique items** | 1,004 |
| **Type G** (Group/general) | 18,695 (50%) |
| **Type C** (Customer-specific) | 14,439 (39%) |
| **Type A** (Account-level) | 4,159 (11%) |

**Key insight:** Half the discounts are group-level (applying to all customers in a price code), 39% are customer-specific (negotiated deals), and 11% are account-level. This three-tier structure is how VIP handles the spectrum from blanket promotions to individually negotiated pricing.

---

## 6. Pending Prices — PENDPRICT (956 rows)

Pending prices are **staged future prices** — prices that have been entered but not yet activated. They represent upcoming price changes.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| PRODID | char(6) | Product code |
| CODEID | char(5) | Price code |
| CASEPRICE | numeric(7,2) | Case price |
| EACHPRICE | numeric(7,3) | Each/bottle price (3 decimal places) |
| POSTOFF | numeric(7,2) | Post-off allowance amount |
| DISCCODE | char(10) | Associated discount code |
| DISCGRP / DISCGRP3 / DISCGRP4 | char(10) | Discount group hierarchy |
| STARTDATE / ENDDATE | numeric(8,0) | When price takes effect |

### What the Data Shows

- **956 pending prices** across **155 distinct price codes** but only **5 unique items**
- This means a small number of products are getting **price changes across nearly every customer tier simultaneously** — likely a supplier-driven price increase
- Average case price: ~$140–$156 depending on code
- Price code 87 (GSCA-IND GROC PROMO) has the most items (13) with avg $140.07
- Employee pricing (EM) is significantly lower: $97.90
- Hunt division codes (H-prefix) are uniform at $150.00
- All DISCGRP and DISCCODE fields are NULL — these are pure base price changes, not discount-related

---

## 7. Front-Line Pricing — FLPWKST (161 rows) & FLPERRT (470 rows)

Front-line pricing tracks the **retail shelf price** (what the consumer pays at the store). Distributors track this for SSP (Suggested Selling Price) compliance and supplier reporting.

### FLPWKST — Front-Line Price Worksheet

| Column | Type | Description |
|--------|------|-------------|
| CASEPRICE | numeric(7,2) | Suggested retail case price |
| EACHPRICE | numeric(7,3) | Suggested retail each price |
| PERCENT | numeric(4,1) | Markup percentage |
| UPCHARGE | numeric(4,2) | Upcharge amount |
| MINIMUM | numeric(4,2) | Minimum price floor |
| STARTDATE / ENDDATE | numeric(8,0) | Effective dates |
| ID_METHOD | bigint | FK to pricing method |
| ID_CCNAME | bigint | FK to cost component |

**What the data shows:** 161 items with case prices ranging from $11.62 to $88.80. All use Method 2 (tier-based). End dates are set to 20391231 (effectively permanent). No percent, upcharge, or minimum values are set — these are straight suggested prices.

### FLPERRT — Front-Line Price Output/Errors (470 rows)

The resolved front-line prices after wizard processing. Contains CASEPRICE, EACHPRICE, CODEID (price code), and SELLBYBTL (sell-by-bottle flag).

---

## 8. Post-Off Allowances

Post-offs are **supplier-funded price reductions** — the supplier agrees to reduce the distributor's cost by a fixed dollar amount per case for a promotional period. This flows through the worksheet pipeline:

```
POSTWKST (worksheet) → POSTIMPT (import) → POSTOUTT (output) → POSTERRT (errors)
```

Post-off amounts appear in:
- **PENDPRICT.POSTOFF** — pending post-off amounts on future prices
- **ORDERT.ORPOST** — the actual post-off applied to each order line
- **DPMAST1T** — embedded in the rebate structure

Post-offs reduce the distributor's cost without changing the retail shelf price, improving distributor margin. In Ohanafy, these map to `Promotion__c` records with `Is_Front_Line__c = false` and a dollar discount.

---

## 9. Cost Components — CCNAMET (105 codes) & CCSTANT (96 formulas)

VIP has a sophisticated cost component system that builds up the "true cost" of each product from multiple factors.

### Cost Component Names — CCNAMET

| Code | Name | Purpose |
|------|------|---------|
| AVERAG | Average | Average cost (weighted) |
| FIFO | First In/First Out | FIFO inventory cost |
| LIFO | Last In/First Out | LIFO inventory cost |
| INBOND | In Bond | Pre-tax bonded warehouse cost |
| INVEN | Inventory | Current inventory cost |
| LAIDIN | Laid-in | Full landed cost (product + freight + tax + fees) |
| USER01–USER99 | User-defined 1–99 | 80 custom cost slots for distributor-specific cost tracking |

### Cost Component Formulas — CCSTANT (96 formulas)

Each formula defines how to compute a cost basis by **adding or subtracting up to 20 sub-components**:
- CSCC01–CSCC20: References to individual cost component indices
- CSCS01–CSCS20: Sign flags (+/-/blank) for each component
- CSCOST: The resulting cost basis name
- CSWHSE: Warehouse-specific formula
- CSHEAD: Section heading for display

This is how VIP handles the "same product, different landed cost per warehouse" problem — each warehouse has different freight, excise tax, and handling costs that roll up into the final cost basis.

### Cost Basis Configuration — COSTBASET (15 records)

Maps cost basis names to the underlying product table columns they read from. Dimensions include: Sub (brand family), Brand, Supplier, Product Class, Product Type, UOM, Return Category, Container Type, Proof Code, Varietal, and 5 user fields.

### Monthly Costs — MQTCOST (110,425 rows)

Warehouse-level monthly cost tracking:

| Warehouse | Records | Unique Items | Avg Cost | Max Cost |
|-----------|---------|-------------|----------|----------|
| 2 (Milton) | 22,500 | 7,537 | $44.82 | $320.00 |
| 1 (Mobile) | 20,836 | 6,966 | $44.95 | $325.80 |
| 7 (Montgomery) | 20,007 | 6,691 | $44.35 | $325.80 |
| 9 (Birmingham) | 17,293 | 5,784 | $44.82 | $4,601.20* |
| 10 (Huntsville) | 13,854 | 4,637 | $42.30 | $280.30 |
| 5 (Jackson) | 1,350 | 451 | $19.22 | $45.15 |
| 6 (Gulfport) | 1,047 | 350 | $24.63 | $45.15 |
| 11 (ABC Board) | 246 | 82 | $66.98 | $217.98 |
| 99 (AL Liquor) | 194 | 65 | $66.20 | $217.98 |
| 4 (unused) | 13,098 | 4,366 | $0.00 | $0.00 |

*Birmingham has one outlier at $4,601.20 — likely a keg or multi-case pack. Warehouse 4 has 13K records all at $0.00 cost — appears to be a deprecated/inactive warehouse.

### Pending Costs — PENDCOSTT (74 rows)

Staged cost changes:
- Multiple cost IDs per item (e.g., cost ID 1 = base cost, ID 2 = freight, ID 5 = excise)
- Item 95508 in warehouse 7 shows cost history: $82.70 → $89.70 → $93.20 (base cost trending up)
- End dates of 99999999 = permanent (no expiration)

---

## 10. Deposits and Fees — DEPOSITST (6,339 rows)

Deposits track container deposits (kegs, shells) and CRV (California Redemption Value) charges.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| DPDEPTYP | char(1) | K = Keg, S = Standard |
| DPDEPO | numeric(7,2) | Deposit amount |
| DPITEM | char(6) | Item code |
| DPACCT | char(5) | Price code/account |
| DPSDAT / DPEDAT | numeric(8,0) | Date range |
| DPDCOD | char(1) | Deposit code type |
| DPTYPE | char(1) | Type (C = price code, G = price group) |

### Breakdown

| Type | Count | Avg Deposit | Min | Max |
|------|-------|-------------|-----|-----|
| **K** (Keg) | 5,389 | $50.06 | $10.00 | $250.00 |
| **S** (Standard) | 950 | $50.55 | $1.20 | $250.00 |

Keg deposits dominate (85%). The $250 max likely represents specialty/large format kegs. Standard deposits at $1.20 minimum could be bottle deposits in deposit states.

---

## 11. Commission Profiles — COMMPROFT (363 profiles)

Commission profiles define how sales reps and drivers are compensated on sales.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| CPID | char(5) | Commission profile ID |
| CPDESC | char(25) | Description |
| CPRATE | numeric(10,6) | Commission rate (6 decimal precision) |
| CPTYPE | char(2) | Commission type |
| CPBAMT | numeric(6,2) | Base commission amount |
| CPMINPAY | numeric(6,2) | Minimum pay |
| CPQPAY | char(1) | Quantity-based pay flag |
| CPPSET / CPBPSET / CPWPSET | char(3) each | Product set references |

Commission rates are typically per-case amounts (e.g., $0.50/case for Red Bull drivers, $0.03/case for general sales). These interact with pricing because they affect the distributor's true margin on each sale.

---

## 12. How Price Resolution Works on an Order

When a VIP order is placed, the system resolves pricing through this cascade:

```
Customer → Price Code (HDRPRCODT)
    ↓
Product → Price Group (HDRPRGRPT via PCPGXRT cross-reference)
    ↓
Warehouse → Warehouse assignment
    ↓
Date → Current date checked against STARTDATE/ENDDATE
    ↓
DPMASTT lookup: (PRODID + CODEID/PRICEGROUP + WHSEID + DATE)
    ↓
DPMAST1T: Get FRONTLINEPRICE, SELLINGPRICE tiers, REBATEAMOUNT tiers
    ↓
DISCWKSTT/DISCOUTT: Check for applicable discount programs
    ↓
"Best Discount" calculation (WRKDISCT work table):
  - Individual item discounts (DSINDT)
  - Performance/volume discounts (DSINEXT)
  - Quantity break discounts (DSQTYT)
  - Special prices (SPRICET)
  - Time-dependent pricing (TIMEPRT)
    ↓
Apply post-off allowances (ORPOST)
    ↓
Add deposits (ORDEPO), CRV (ORCRV), handling (ORHCHG)
    ↓
Record front-line price (ORFLPR) for supplier reporting
    ↓
Record commission (via COMMPROFT profiles)
    ↓
Final order line on ORDERT with 23+ pricing columns
```

### Order Line Pricing Fields (ORDERT)

| Column | Description |
|--------|-------------|
| ORPRIC | Unit price charged |
| OREPRI | Extended price (qty x price, no deposit) |
| ORSSP | Suggested selling price (retail) |
| ORFLPR | Front-line price (retail tracking) |
| ORPOST | Post-off allowance amount |
| ORDSRT | Discount rate ($/case or %) |
| ORDAMT | Extended discount amount |
| ORAVCS | Average cost |
| ORICOS | Inventory cost |
| ORDEPO | Deposit |
| ORCRV | CRV (California Redemption Value) |
| ORHCHG | Handling charge |
| ORMAMT | Marketing funds amount |
| ORPDAT | Pricing date used for resolution |
| ORONOF | On/off premise code |
| ORMTYP | Market type |
| ORTERR | Territory |
| ORDEPMTH | Depletion method |

---

## 13. Unused Tables in Gulf's Instance

Several pricing tables exist in VIP's schema but are **empty or unused** by Gulf:

| Table | Rows | Purpose | Why Unused |
|-------|------|---------|------------|
| TIMEPR | 0 | Time-dependent pricing | Gulf uses DPMASTT date ranges instead |
| SPRICET | 0 | Special/contract pricing | Gulf uses deployment master for all pricing |
| PRBOOKHT | 0 | Price books (printed catalogs) | Gulf doesn't generate price books |
| ITEMT.SUGGESTED_SELLING_PRICE | 0 items with value | Per-item SSP | Gulf tracks SSP at the deployment level, not item level |
| HDRWHSET.PRICE_CODE | all NULL | Warehouse default price code | Gulf resolves pricing at the customer level, not warehouse level |

This is significant — it means Gulf's pricing is **entirely driven by the deployment master + discount system**, not by the simpler price code → item price lookup that smaller distributors might use.

---

## 14. VIP → Ohanafy Pricing Migration Mapping

### 14A. Direct Mappings

| VIP Source | VIP Table | Ohanafy Target | Notes |
|------------|-----------|----------------|-------|
| **Discount Worksheets** | DISCWKSTT | `Pricelist__c` | Each worksheet becomes a Pricelist. Type A → "Discount", Type F → "Individual Price" |
| **Pending Prices** | PENDPRICT | `Pricelist_Item__c` | Item-level prices within a pricelist. CASEPRICE → Case_Price__c, POSTOFF → Discount_Dollars__c |
| **Discount Output** | DISCOUTT | `Promotion__c` + `Promotion_Item__c` | Each discount line becomes a promotion. Type G → general, C → customer-specific, A → account-level |
| **Deposits** | DEPOSITST | `Fee__c` | Keg and standard deposits. DPDEPO → Default_Amount__c, DPDEPTYP → Type__c |
| **Front-Line Prices** | FLPWKST/FLPERRT | `Promotion__c` (Is_Front_Line__c = true) | Front-line prices map to front-line promotions that adjust the base price |
| **Price Codes** | HDRPRCODT | No direct object — embedded in Pricelist assignment | Price codes determine which Pricelist a customer gets via Pricelist_Account__c |
| **Price Groups** | HDRPRGRPT | `Pricelist_Group__c` + `Tier_Setting__c` | Red Bull tiers map to Pricelist Groups with tier settings |
| **Cost Components** | CCNAMET/CCSTANT | No direct mapping | Ohanafy doesn't have a cost component system; costs live on Item__c |
| **Commissions** | COMMPROFT | No direct mapping | Ohanafy handles commissions differently (if at all) |

### 14B. The Deployment Master Challenge

The deployment master (DPMASTT/DPMAST1T) is the **hardest part** of the pricing migration. Its 930K rows with 20-tier pricing don't have a direct equivalent in Ohanafy. Options:

**Option 1: Flatten to Pricelists (Recommended)**
- Create one `Pricelist__c` per price code (154 pricelists)
- Create `Pricelist_Item__c` records using the SELLINGPRICE01 (or most common tier) from DPMAST1T
- Use `Pricelist_Group__c` and `Tier_Setting__c` for the Red Bull tier program
- Lose the 20-tier granularity but capture the primary pricing

**Option 2: Use Pricelist Groups for Tiers**
- Create `Pricelist_Group__c` for each tier program (Red Bull Diamond/Gold/etc.)
- Create `Pricelist_Setting__c` records for each tier + packaging type combination
- Create `Tier_Setting__c` records to map item types to pricing tiers
- More complex but preserves the tiered structure

**Option 3: Promotions for Rebates**
- Map FRONTLINEPRICE to `Pricelist_Item__c.Case_Price__c`
- Map REBATEAMOUNT to `Promotion__c` with `Discount_Dollars__c`
- Track rebates as promotions that reduce the selling price
- Most faithful to VIP's model but creates many promotion records

### 14C. Pricelist Type Mapping

| VIP Type | VIP Description | Ohanafy Pricelist Type__c |
|----------|----------------|--------------------------|
| A (DISCWKSTT) | Standard discount worksheet | "Discount" |
| F (DISCWKSTT) | Front-line price worksheet | "Individual Price" |
| I (DISCOUNTTYPE) | Individual item price | "Individual Price" |
| P (DISCOUNTTYPE) | Percentage discount | "Discount" with Discount_Type__c = "Percent" |
| — | Red Bull tiered pricing | "Settings" (uses Pricelist_Group__c) |

### 14D. Promotion Type Mapping

| VIP Source | VIP TYPEID | Ohanafy Promotion__c Fields |
|------------|-----------|----------------------------|
| DISCOUTT Type G | Group discount | Is_Chain_Level__c = true |
| DISCOUTT Type C | Customer-specific | Customer__c = specific account |
| DISCOUTT Type A | Account-level | Customer__c = specific account |
| Front-line (FLPWKST) | Front-line price | Is_Front_Line__c = true |
| Post-off | Supplier allowance | Discount_Dollars__c = post-off amount |
| Quantity deal | QD in DISCDESC | Is_Auto_Apply__c = true, Case_Quantity on Promotion_Item__c |

### 14E. Field-Level Mapping Detail

**DISCWKSTT → Pricelist__c:**

| VIP Field | Ohanafy Field | Transform |
|-----------|---------------|-----------|
| DISCOUNTID | Key__c | TRIM() |
| DISCDESC | Name | TRIM() |
| DISCOUNTTYPE | Type__c | A → "Discount", F/I → "Individual Price" |
| DISCOUNTTYPE | Discount_Type__c | P/% → "Percent", else → "Dollars" |
| STARTDATE | Start_Date__c | YYYYMMDD → Date |
| ENDDATE | End_Date__c | YYYYMMDD → Date |
| — | Is_Active__c | TRUE if ENDDATE >= today |

**PENDPRICT → Pricelist_Item__c:**

| VIP Field | Ohanafy Field | Transform |
|-----------|---------------|-----------|
| PRODID | Item__c | Lookup by item code |
| DISCCODE | Pricelist__c | Lookup by Key__c |
| CASEPRICE | Case_Price__c | Direct |
| EACHPRICE | Unit_Price__c | Direct |
| POSTOFF | Discount_Dollars__c | Direct |
| DISCCODE+PRODID | Key__c | Composite key |

**DISCOUTT → Promotion__c + Promotion_Item__c:**

| VIP Field | Ohanafy Field | Transform |
|-----------|---------------|-----------|
| DISCCODE | Name | Lookup description from DISCWKSTT |
| TYPEID | (logic) | G → chain-level, C/A → customer-specific |
| STARTDATE | Start_Date__c | YYYYMMDD → Date |
| ENDDATE | End_Date__c | YYYYMMDD → Date |
| PRODID | Promotion_Item__c.Item__c | Lookup by item code |
| CODEID | (context) | Determines which customer tier |

**DEPOSITST → Fee__c:**

| VIP Field | Ohanafy Field | Transform |
|-----------|---------------|-----------|
| DPDEPTYP | Type__c | K → "Storage", S → "Misc. Charge" |
| DPDEPO | Default_Amount__c | Direct |
| — | Is_Active__c | TRUE |
| — | Is_Invoice__c | TRUE |
| DPDEPTYP+DPDEPO | Key__c | Composite key |

---

## 15. Migration Complexity Assessment

### What Makes This Hard

1. **Scale of deployment master** — 930K rows is too many to create individual Pricelist_Item records. Need to identify the "active" subset and collapse dimensions.

2. **20-tier pricing** — Ohanafy's `Pricelist_Setting__c` supports tiers but not 20 levels. Need to identify which tiers are actually used and map to a manageable number.

3. **Price code explosion** — 154 price codes x items = massive pricelist count. May need to group related codes (e.g., all GDC retail chains that share the same pricing) into fewer pricelists.

4. **Temporal overlap** — VIP has prices with date ranges that overlap, with the system picking the "best" one. Ohanafy pricelists don't have the same conflict resolution logic.

5. **Rebate vs. price** — VIP separates "selling price" from "rebate amount" (two-part pricing). Ohanafy uses a single `Case_Price__c` or `Discount_Dollars__c`. Need to decide: migrate the net price, or model the rebate as a promotion?

6. **No SSP on items** — Gulf doesn't use ITEMT.SUGGESTED_SELLING_PRICE (all zeros). Ohanafy expects `Default_Case_Price__c` on items. Need to derive from deployment master's FRONTLINEPRICE or from the most common selling price.

### Recommended Approach

**Phase 1: Core Pricing (Must-Have)**
1. Set `Item__c.Default_Case_Price__c` from the most common DPMAST1T selling price per item
2. Create `Pricelist__c` records from DISCWKSTT (735 worksheets → 735 pricelists)
3. Create `Pricelist_Item__c` records from PENDPRICT (956 item-level prices)
4. Create `Pricelist_Account__c` to assign pricelists to customers based on their price codes
5. Create `Fee__c` records from DEPOSITST (keg and standard deposits)

**Phase 2: Promotions & Discounts**
6. Create `Promotion__c` records from DISCOUTT active records (12,056 records)
7. Create `Promotion_Item__c` for each item in a promotion
8. Set promotion flags (Is_Front_Line, Is_Chain_Level, Is_Auto_Apply) based on VIP type
9. Link billbacks where applicable

**Phase 3: Tiered/Advanced Pricing**
10. Create `Pricelist_Group__c` for Red Bull tier programs
11. Create `Tier_Setting__c` to map item types to tiers
12. Create `Pricelist_Setting__c` for tier + packaging combinations
13. Derive `Pricelist__c` (Type="Settings") that reference the groups

**Phase 4: Cost & Commission (Reference Only)**
14. Export cost component data for reference (not directly migrated)
15. Export commission profiles for reference (Ohanafy handles differently)
16. Document deployment master detail for ongoing pricing validation

---

## 16. Reference: All Pricing-Related Tables

| Table | Rows | Category | Description |
|-------|------|----------|-------------|
| **DPMAST1T** | **930,610** | Deployment | Tiered selling prices + rebate amounts (20 tiers each) |
| **DPMASTT** | **935,967** | Deployment | Deployment header (item + code + warehouse + dates) |
| MQTCOST | 110,425 | Cost | Monthly cost by item/warehouse |
| **DISCOUTT** | **37,293** | Discount | Resolved discount output (12K active) |
| DEPOSITST | 6,339 | Deposits | Keg and standard deposits |
| PENDPRICT | 956 | Pending | Staged future prices |
| DEPLWKST | 856 | Worksheet | Deployment pricing worksheets |
| **DISCWKSTT** | **766** | Worksheet | Discount worksheets (→ Pricelists) |
| FLPERRT | 470 | Front-Line | Front-line price output |
| **HDRPRGRPT** | **379** | Config | Price group definitions |
| COMMPROFT | 363 | Commission | Commission profiles |
| FLPWKST | 161 | Front-Line | Front-line price worksheets |
| **HDRPRCODT** | **154** | Config | Price code definitions |
| CCNAMET | 105 | Cost | Cost component names |
| CCSTANT | 96 | Cost | Cost component formulas |
| PENDCOSTT | 74 | Pending | Staged cost changes |
| DISCIMPT | 49 | Worksheet | Discount import wizard bridge |
| COSTBASET | 15 | Cost | Cost basis configuration |
| DISCERRT | 12 | Worksheet | Discount wizard errors |
| PENDDEP1T | 1 | Pending | Pending deployment detail |
| TIMEPR | 0 | Pricing | Time-dependent pricing (unused) |
| SPRICET | 0 | Pricing | Special pricing (unused) |
| PRBOOKHT | 0 | Pricing | Price books (unused) |

### Full VIP Pricing Domain (from Reference Docs)

Beyond the tables with data above, VIP's complete pricing schema includes **160+ tables** across these domains:

| Domain | Table Count | Key Tables |
|--------|------------|------------|
| Pricing Core | 53 | DSCNTT, DSINDT, DSINEXT, DSQTYT, SPRICET, TIMEPRT, HDRPRCODT, HDRPRGRPT, PRBOOKHT |
| Worksheets & Cost Mgmt | 46 | WKSHEETT (central hub, 20 FKs), COSTWKSTT, DEPLWKST, DISCWKSTT, FLPWKST, POSTWKST |
| Deployment | ~15 | DPMASTT, DPMAST1T/2T/3T, DPMAST10/11, PENDDEP1T/2T/3T/LT |
| Marketing/Rebates | 18 | MARKETING_FUND, MARKETING_ACCRUAL_*, NATPRODRT |
| Commission | 14 | COMMPROFT, COMMCLCT, COMMISSION_TIER |
| Tax | 16 | FLBEVTAXT, GATAX*, TXTAX*, MOTAXT |
| Test Pricing | 5 | TESTORDHT/DT, TPORDHDT/TPORDERT, FAVACCTST |

---

## 17. Ohanafy Pricing Object Reference

For completeness, here is the Ohanafy pricing data model that VIP data must map into:

### Object Hierarchy

```
Pricelist__c (Named pricing program)
├── Pricelist_Item__c (Per-item prices within a pricelist) [Master-Detail]
│   └── Front_Line_Promotion__c → Promotion_Item__c [Lookup]
├── Pricelist_Account__c (Customer assignments) [Master-Detail]
└── Pricelist_Group__c (Tier-based pricing rules) [Lookup]
    ├── Pricelist_Setting__c (Tier + packaging config) [Lookup]
    └── Tier_Setting__c (Item type → tier mapping) [Lookup]

Promotion__c (Promotional discounts)
├── Promotion_Item__c (Product-level) [Master-Detail to Promotion + Item]
├── Promotion_Item_Type__c (Category-level) [Master-Detail]
├── Promotion_Item_Line__c (Supplier-level) [Master-Detail]
├── Promotion_Invoice_Item__c (Applied tracking) [Master-Detail]
├── Customer__c → Account [Lookup]
├── Territory__c [Lookup]
└── Billback__c [Lookup]

Fee__c (Deposits/surcharges)
Credit__c (Returns/adjustments)
Billback__c (Supplier incentive tracking)
Territory__c (Geographic pricing scope)
```

### Key Ohanafy Fields

**Pricelist__c:**
- Type__c: Discount | Individual Price | Settings
- Discount_Type__c: Percent | Dollars
- Start_Date__c / End_Date__c
- Is_Active__c
- Pricelist_Group__c (for Settings type)

**Pricelist_Item__c:**
- Case_Price__c (currency)
- Discounted_Case_Price__c (currency, 8 decimals)
- Unit_Price__c (currency, 4 decimals)
- Discount_Dollars__c / Discount_Percent__c
- Pricing_Tier__c (text)
- Front_Line_Promotion__c → Promotion_Item__c

**Promotion__c:**
- Is_Front_Line__c (impacts base price)
- Is_Chain_Level__c (entire chain vs. individual)
- Is_Straight_Line__c (uniform discount)
- Is_Auto_Apply__c (auto-apply to eligible orders)
- Discount_Type__c: Percent | Dollar
- Discount_Percent__c / Discount_Dollars__c
- Customer__c / Territory__c / Billback__c

**Promotion_Item__c:**
- Type__c: Reward | Criteria | Reward Exclusion | Criteria Exclusion
- Case_Quantity__c (minimum quantity)
- Discount_Percent__c / Discount_Dollars__c
- Discounted_Case_Price__c
