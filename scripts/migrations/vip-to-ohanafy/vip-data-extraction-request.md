# VIP DB2 Data Extraction Request — Gulf Distributing

**Date:** 2026-03-16
**Requested by:** Ohanafy Integrations Team
**Deadline:** Thursday 2026-03-19 (migration go-live)
**Target:** `gulfstream-db2-data.postgres.database.azure.com` → `staging` schema

---

## Priority 1 — CRITICAL: Tables That Do Not Exist in PostgreSQL

These tables have **never been created or synced** to the staging database. They are not present in any schema (`staging`, `analytics`, `as400_mirror`, `azure_cdc`, `azure_storage`, `import_control`, `public`). No table definition files exist for them either.

| VIP DB2 Table | Description | Why We Need It | Expected Row Count |
|---|---|---|---|
| **HDRT** | Customer/Account master header | Core customer record: account #, name, address, type, status, credit info. This is the primary customer table in VIP. Without it we cannot build the Ohanafy Account records. | ~4,000-5,000 |
| **CONTMASTT** | Contact master | Contact names, emails, phone numbers linked to customer accounts. Required for Ohanafy Contact records. | Unknown |
| **HDRMBFAMT** | Customer MBF/family pricing amounts | Multi-brand family discount amounts per customer. Required for pricing tier migration. | Unknown |
| **PRICET** | Price list master | Base price lists (case price, each price, deposit by item/price code). Required for Ohanafy Pricelist/Pricelist_Item records. | Unknown |
| **CLASST** | Class/category master | Item classification codes (beer, wine, spirits, NA, etc.). Used for item categorization in Ohanafy. | ~20-50 |
| **DEPTT** | Department master | Department codes referenced by items and GL accounts. | ~10-30 |
| **SIZET** | Size master | Container size definitions (12oz, 16oz, 750ml, etc.). Referenced by ITEMT. | ~30-60 |
| **PKGT** | Package type master | Package type definitions (case, keg, 6-pack, etc.). Referenced by ITEMT. | ~20-40 |

## Priority 2 — CRITICAL: Tables That Exist But Have 0 Rows

These tables exist in the `staging` schema with correct column structures, but contain **no data**. They need to be populated from the VIP DB2 source.

| Staging Table | Description | Why We Need It | Expected Row Count |
|---|---|---|---|
| **ORDERT** | Order detail lines | Open/pending order lines. Needed for any in-flight order migration. (Note: historical completed sales exist in DAILYT with 30.2M rows) | Unknown |
| **ORDHDT** | Order headers | Open/pending order headers. Paired with ORDERT. | Unknown |
| **INVENT** | Current inventory | Current inventory levels by item/warehouse/location. Required for Ohanafy Inventory records. | ~10,000-50,000 |
| **SPRICET** | Special pricing | Customer-specific price overrides (by account + item or account + brand). Required for customer deal pricing in Ohanafy. | Unknown |
| **HDRCLASST** | Customer class codes | Customer-to-class assignment (on/off premise, chain type, etc.). Used for customer segmentation and record types. | ~4,000-5,000 |

## Priority 3 — NICE TO HAVE: Additional Reference Tables

These are not blocking but would improve data quality:

| VIP DB2 Table | Description | Notes |
|---|---|---|
| **ROUTET** | Route master (if different from HDRROUTET) | We have HDRROUTET (308 rows) — confirm this is the complete route list |
| **TERRT** | Territory master (if different from HDRTERRT) | We have HDRTERRT (98 rows) — confirm this is complete |
| **VENDORT** | Vendor master (if different from APVENT/SUPPLIERT) | We have APVENT (5,665) and SUPPLIERT (427) |
| **WHSET** | Warehouse master (if different from HDRWHSET) | We have HDRWHSET (10 rows) — confirm this is complete |

---

## What We Already Have (No Action Needed)

These tables are populated and working:

| Table | Rows | Status |
|---|---|---|
| ITEMT (items) | 8,743 | OK |
| BRANDT (brands) | 927 | OK |
| DAILYT (sales history) | 30,192,806 | OK |
| POSACCT (partial customer data) | 3,809 | OK — has NAME_DBA, address, phone |
| SUPPLIERT (suppliers) | 427 | OK |
| APVENT (AP vendors) | 5,665 | OK |
| HDRROUTET (routes) | 308 | OK |
| HDRTERRT (territories) | 98 | OK |
| HDRWHSET (warehouses) | 10 | OK |
| HDRDRT (drivers) | 518 | OK |
| USERST (users) | 1,970 | OK |
| + 258 other populated tables | Various | OK |

---

## Technical Details

- **Target database:** `gulfstream` on `gulfstream-db2-data.postgres.database.azure.com:5432`
- **Target schema:** `staging`
- **Sync user:** `ohanafy`
- **Current sync mechanism:** Azure CDC (tracked_tables shows 11 tables being tracked)
- **Total staging objects:** 309 tables + 1 view
- **Populated:** 271 tables
- **Empty:** 38 tables (including the 5 critical ones above)

## Questions for the VIP/Data Team

1. **HDRT** — What is the canonical customer master table name in VIP DB2? Is it `HDRT`, `HEADER`, or something else? The staging DB has `POSACCT` (3,809 rows) with partial customer info but it lacks account type, credit terms, license info, etc.
2. **ORDERT/ORDHDT** — Are these empty because there are genuinely no open orders, or because they were never synced? If open orders aren't needed (all historical sales are in DAILYT), we can deprioritize.
3. **INVENT** — Same question — is inventory data synced elsewhere, or does this need a fresh extract?
4. **PRICET** — What is the pricing table called in VIP DB2? We have `PENDPRICT` (956 pending prices) and `WKPRCRCPT` (26K work price records) but not the base price list.
5. **Table definitions** — Can you provide the DB2 DDL or column definitions for the 8 missing tables in Priority 1? We have definitions for 242 other tables but not these.
