# VIP to Ohanafy Migration — Project Context

## Project Rules

1. **Goal: Load Gulf's data AND build a reusable migration playbook.** This project has two equally important purposes: (a) transform VIP source data into Ohanafy-compatible output and load it into the Gulf sandbox, and (b) document everything we learn so the next VIP-to-Ohanafy migration is faster and smoother. Every workspace should serve both goals.
2. **Never write to any database.** Do not write, insert, update, or delete data in any database — including Salesforce orgs, PostgreSQL, or any other data store. Read-only queries are fine. Output goes to Google Sheets only.
3. **Always update the specified Google Sheets tab.** When working on a data object, the output must go to the corresponding tab in the Google Sheets workbook. Never output data somewhere else unless explicitly told to.
4. **Update the migration playbook with reusable knowledge.** When you discover a reusable pattern, gotcha, decision tree, or lesson learned, add it to `vip-to-ohanafy-playbook.md` — that's the durable artifact for future migrations. Memory files help Claude remember across conversations; the playbook helps *humans* remember across customers. Document the *why* behind decisions, not just the *what*.
5. **Ask Daniel about Ohanafy objects — don't guess.** If you're unsure what an Ohanafy object does, what a field means, or how something should map, ask. A wrong assumption wastes more time than a question.

## Reference Data Folder

All source reference material lives at: `/Users/danielzeder/Desktop/VIP to Ohanafy/`

Contents:
- `tableDefinitions/` — Text files describing every VIP staging table (e.g., `staging_ITEMT.txt`, `staging_BRANDT.txt`). Read these to understand table structure.
- `csvData/` — CSV exports of analytics-schema tables plus reference data (`schema_columns.csv`, `table_details.csv`, `inferred_relationships.csv`, `pickpath_data.csv`)
- `OHFY-Data_Model/` — Ohanafy Salesforce data model (force-app source, openspec, CLAUDE.md with its own context)
- `gulf-vip-db2-complete-reference.docx` — Complete VIP database reference documentation
- `gulf-vip-db2-schema-reference.docx` — Schema-level reference documentation
- `vipERD.pdf` — VIP entity-relationship diagram
- `sandbox_orgs/tbm-fullcopy` — Salesforce sandbox org data
- `service-account.json` — Google Sheets service account (used by migration scripts)
- `gulf pg` — Database connection credentials file

## Database Connections

**Host:** `gulfstream-db2-data.postgres.database.azure.com`
**Port:** 5432
**Database:** `gulfstream`
**SSL:** required

Two users with different schema access:

| Username | Password | Schema Access |
|---|---|---|
| `ohanafy` | `Xq7!mR#2vK$9pLw@nZ` | `staging` |
| `analytics_user_dev` | `Gf$7kLm9Px#2nQwR` | `analytics` |

Use `ohanafy` for querying raw VIP staging tables (UPPERCASE names like `ITEMT`, `BRANDT`, `ORDERT`).
Use `analytics_user_dev` for querying analytics views/rollups.

## Google Sheets Workbook

**Title:** "Claude VIP -> Ohanafy Data Workbook"
**Sheet ID:** `108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE`
**Service Account:** `/Users/danielzeder/Desktop/VIP to Ohanafy/service-account.json`

Tabs: Loading_Guide, Item_Lines, Item_Types, Suppliers, Customers, Items, Parent_Locations, Child_Locations, Pick_Paths, Territories, Equipment_Vehicles, Routes, Fees, Pricelists, Pricelist_Items, Lots, Inventory, Lot_Inventory, Users, Contacts, Account_Routes, Prospects, Allocations_Customer, Promotions, Overhead, Data_Validation_Sales, Data_Validation_Inventory, Record_Types, Progress_Tracker, User_Warehouse_Permissions

## Target Salesforce Org

**Org:** Gulf Distributing — Partial Copy Sandbox
**Alias:** `gulf-partial-copy-sandbox`
**User:** `integrations@ohanafy.com.gulf.partial`
**Org ID:** `00DWE00000Mbk0q2AB`
**Login URL:** `https://test.salesforce.com`
**Metadata:** `./customer_orgs/gulf-partial-copy/sandbox/force-app/` (3,564 files retrieved 2026-03-13)

This is the target org for loading all migration data. Use this org's metadata to validate field names, picklist values, record types, and object structure before generating CSVs.

## Migration Output

Generated CSV files for Ohanafy import live in `./migration_output/` (27 files: Customers, Items, Pricelists, Contacts, Inventory, Routes, etc.)

## Migration Playbook

**`vip-to-ohanafy-playbook.md`** is the reusable knowledge base for VIP-to-Ohanafy migrations. It should be kept up to date as we work. Before starting a new data object, check if the playbook already has guidance. After finishing one, add what you learned.

This playbook is more important than any single CSV file — the data load is for Gulf, but the playbook is for every future customer.

## Key Docs in This Repo

- `vip-to-ohanafy-playbook.md` — Main migration playbook
- `vip-pricing-deep-dive.md` — Pricing analysis
- `vip-pricing-types-explained.md` — Pricing type explanations
- `vip-accounting-deep-dive.md` — GL, AP, AR accounting system docs

## Critical Rules for Migration CSV Generation

1. **Always verify fields are writable** before including in CSV headers. Query the target org:
   ```
   sf data query --query "SELECT QualifiedApiName, DataType, IsCreatable FROM EntityParticle WHERE EntityDefinitionId = 'ohfy__ObjectName__c' AND IsCreatable = true" --target-org gulf-partial-copy-sandbox --json
   ```
   Never trust the OHFY-Data_Model source alone — it can be stale vs the deployed package.

2. **All Ohanafy custom fields need the `ohfy__` prefix** in subscriber orgs. Standard SF fields (Name, Phone, BillingStreet, RecordTypeId) do NOT get the prefix. The OHFY-Data_Model source omits the prefix.

3. **VIP territories (HDRTERRT) are brand groupings, NOT geographic areas.** Do not import them as Ohanafy territories. Ohanafy parent territories = warehouse regions from HDRWHSET.

4. **CMCHN (chain code) does NOT mean "is a chain."** Nearly every customer has one. Use market_desc (HDRMKTT.DESCRIPTION) prefixes (CHAIN vs IND) for Retail_Type__c.

5. **VIP routes have no day-of-week.** Each route = one driver. Don't assume TBM's route-per-day model.

6. **RecordType IDs are org-specific.** Stored in `migration_output/record_type_ids.csv`. File is named with `_ids` to avoid macOS case collision with `Record_Types.csv` tab output.

7. **Supplier-vendor matching** uses direct code match + fuzzy matching + curated overrides (`migration_output/supplier_vendor_overrides.csv`).

## Before Starting Any Data Work

Do NOT ask the user to verify access each time. This file confirms:
1. CSV files are in `./migration_output/`
2. Both DB users work (tested 2026-03-13)
3. Google Sheets connection works (tested 2026-03-13)
4. Table definitions are at the desktop path above
5. Read the relevant `tableDefinitions/*.txt` file to understand any VIP table before querying it
