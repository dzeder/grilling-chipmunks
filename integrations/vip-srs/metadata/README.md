# VIP Supplier Reports & Dashboards

Salesforce report types, reports, and dashboards for visualizing VIP integration data. Shared across all customers using the VIP SRS integration.

## Folders

Both reports and dashboards deploy into a single **VIP Data** folder in Salesforce.

## Report Catalog

### Data Quality — Missing Fields (9 reports)

One report per VIP-loaded object. Each uses OR logic across all VIP-populated fields so any blank field surfaces the record.

| Report | Report Type | Grouped By | Key Fields Checked |
|--------|-------------|------------|-------------------|
| Items Missing Required Fields | `CustomEntity$ohfy__Item__c` | Item Name | Item Line, Item Type, UOM, Type, Package Type, Supplier Number |
| Item Lines Missing Fields | `CustomEntity$ohfy__Item_Line__c` | Item Line Name | VIP External ID, Type |
| Item Types Missing Fields | `CustomEntity$ohfy__Item_Type__c` | Item Type Name | VIP External ID, Item Line, Category, Type |
| Customers Missing Fields | `AccountList` (Type=Customer) | Account Name | External ID, Customer Number, Street, City, State, Phone |
| Chain Banners Missing Fields | `AccountList` (Type=Chain Banner) | Account Name | External ID, Retail Type |
| Retailers Missing Fields | `AccountList` (Type=Distributed Customer) | Account Name | External ID, Customer Number, Address, Market, Premise Type, Chain Banner*, Retail Type |
| Depletions Missing Fields | `AccountCustomEntity$ohfy__Depletion__c` | Account Name | Item, VIP External ID, Case Quantity, Date, Net Price |
| Placements Missing Fields | `VIP_Placements__c` | Account | Item, VIP External ID, First Sold Date, Last Sold Date, Last Purchase Quantity |
| Inventory Missing Fields | `CustomEntityCustomEntity$ohfy__Item__c$ohfy__Inventory__c` | Location Name | VIP External ID, Location, Cases On Hand, Units On Hand |

*Chain Banner check only flags when Retail_Type = "Chain" — independents are excluded.

### Data Quality — Duplicate Names (7 reports)

| Report | Report Type | Scoped By |
|--------|-------------|-----------|
| Duplicate Item Names | `CustomEntity$ohfy__Item__c` | All Items |
| Duplicate Item Line Names | `CustomEntity$ohfy__Item_Line__c` | All Item Lines |
| Duplicate Item Type Names | `CustomEntity$ohfy__Item_Type__c` | All Item Types |
| Duplicate Customer Names | `AccountList` | Type = Customer |
| Duplicate Account Names | `AccountList` | Type = Distributed Customer |
| Duplicate Chain Banner Names | `AccountList` | Type = Chain Banner |

### Supplier Metrics (12 reports)

| Report | Report Type | Description |
|--------|-------------|-------------|
| Depletions by Brand MTD | `VIP_Depletions_with_Items__c` | Cases/revenue by brand by week |
| Depletions by Account MTD | `VIP_Accounts_with_Depletions__c` | Total cases/revenue per retailer |
| Active Placements Summary | `VIP_Placements_with_Items__c` | Active placements grouped by brand |
| Lost Placements Alert | `VIP_Placements_with_Items__c` | Accounts exceeding lost placement threshold |
| Inventory Levels by Item | `VIP_Inventory_with_Items__c` | Current quantity on hand by SKU |
| Depletions by Market | `VIP_Accounts_with_Depletions__c` | Cases/revenue by market and state |
| Top Accounts by Volume | `VIP_Accounts_with_Depletions__c` | Accounts ranked by depletion case volume |
| New Placements This Month | `VIP_Placements_with_Items__c` | New points of distribution by brand |
| Depletions by Salesman | `VIP_Accounts_with_Depletions__c` | Cases/revenue by distributor rep code |
| Depletions Trend by Month | `VIP_Depletions_with_Items__c` | MoM depletion trend (Matrix format, configure chart in UI) |
| Distribution Coverage by Brand | `VIP_Accounts_with_Placements__c` | Active accounts per item/brand |
| Declining Accounts | `VIP_Accounts_with_Placements__c` | Lowest L30D volume accounts for retention |

### Integration Health (1 report)

| Report | Report Type | Description |
|--------|-------------|-------------|
| Stale Record Monitor | `VIP_Depletions_with_Items__c` | VIP_File_Date__c freshness check (on Data Quality dashboard) |

### Dashboards

| Dashboard | Layout |
|-----------|--------|
| **Data Quality Overview** | Left: Items, Item Lines, Item Types / Middle: Customers, Chain Banners, Retailers / Right: Depletions, Placements, Inventory |
| **Supplier Overview** | Left: Depletions by Brand, Active Placements, New Placements, Depletions Trend / Middle: Depletions by Account, Top Accounts, Lost Placements, Coverage by Brand / Right: Inventory Levels, Depletions by Market, Depletions by Salesman, Declining Accounts |

### Superseded Reports (still in repo for reference)

These were replaced during development. They remain in the metadata but are NOT on any dashboard.

| Report | Replaced By | Reason |
|--------|-------------|--------|
| Orphaned_Depletions_Missing_Item | Depletions_Missing_Fields | Outer join false positives |
| Orphaned_Depletions_Missing_Account | Depletions_Missing_Fields | Outer join false positives |
| Accounts_Missing_Chain_Banner | Retailers_Missing_Fields | Combined into single report |
| Accounts_Unmapped_Market | Retailers_Missing_Fields | Combined into single report |
| Inventory_Missing_External_ID | Inventory_Missing_Fields | Outer join false positives |
| Items_Missing_Filter_Prerequisites | Items_Missing_Required_Fields | Outer join false positives |
| Duplicate_Item_Lines | Duplicate_Item_Line_Names | Naming consistency |

## Report Types

### Custom (deployed as metadata)

| Report Type | Base Object | Join | Purpose |
|-------------|-------------|------|---------|
| VIP_Depletions_with_Items | `ohfy__Item__c` | → `ohfy__Depletions__r` (Inner) | Supplier depletion metrics |
| VIP_Placements_with_Items | `ohfy__Item__c` | → `ohfy__Placements__r` (Inner) | Supplier placement metrics |
| VIP_Inventory_with_Items | `ohfy__Item__c` | → `ohfy__Inventory_Items__r` (Inner) | Supplier inventory metrics |
| VIP_Items_with_Lines | `ohfy__Item_Line__c` | → `ohfy__Items__r` (Outer) | Item catalog analysis |
| VIP_Accounts_with_Depletions | `Account` | → `ohfy__Depletions__r` (Inner) | Account-level depletion metrics |
| VIP_Accounts_with_Placements | `Account` | → `ohfy__Placements__r` (Inner) | Account-level placement metrics, coverage, declining accounts |
| VIP_Placements | `ohfy__Placement__c` | None (standalone) | Placement data quality |

### Built-in Managed Package (no metadata needed)

These are auto-generated by the Ohanafy managed package and use **inner joins** — critical for data quality reports.

| Report Type API Name | Objects | Join Type |
|---------------------|---------|-----------|
| `CustomEntity$ohfy__Item__c` | Item only | N/A |
| `CustomEntity$ohfy__Item_Line__c` | Item Line only | N/A |
| `CustomEntity$ohfy__Item_Type__c` | Item Type only | N/A |
| `AccountList` | Account only | N/A |
| `AccountCustomEntity$ohfy__Depletion__c` | Account → Depletion | Inner |
| `CustomEntityCustomEntity$ohfy__Item__c$ohfy__Inventory__c` | Item → Inventory | Inner |

## Critical Lessons Learned

### 1. Outer Join False Positives

**Problem:** Custom report types with outer joins (e.g., `VIP_Accounts_with_Depletions__c`) return parent rows that have ZERO child records. Filtering on `child_field = null` matches these phantom rows, producing massive false positives.

**Fix:** Use built-in managed package report types for data quality reports. They use inner joins, so only rows with actual child data appear.

**Rule:** Outer-join report types are fine for supplier metrics (where you WANT to see items with no depletions). Never use them for "missing field" or "orphaned record" reports.

### 2. Report Type Field Reference Formats

Field references vary by report type base:

| Report Type Base | Standard Fields | Custom Fields |
|-----------------|-----------------|---------------|
| `CustomEntity$ohfy__Object__c` | `CUST_NAME`, `CUST_ID`, `CUST_CREATED_DATE` | `ohfy__Object__c.ohfy__Field__c` |
| `AccountList` | `ACCOUNT.NAME`, `TYPE`, `ADDRESS1_STATE`, `PHONE1` | `Account.ohfy__Field__c` |
| `AccountCustomEntity$ohfy__Depletion__c` | Parent: `ACCOUNT.NAME` / Child: `CUST_NAME`, `CUST_CREATED_DATE` | `ohfy__Depletion__c.ohfy__Field__c` |
| `CustomEntityCustomEntity$Parent$Child` | Parent: `CUST_NAME` / Child: `CHILD_CREATED_DATE` | `ohfy__Child__c.ohfy__Field__c` |
| Custom standalone (e.g., `VIP_Placements__c`) | `ohfy__Object__c$Name`, `ohfy__Object__c$CreatedDate` | `ohfy__Object__c$ohfy__Field__c` |

Use the Analytics API to discover exact field references:
```
GET /services/data/v62.0/analytics/reportTypes
GET /services/data/v62.0/analytics/report-types/{typeName}
```

### 3. Account Reports Must Scope by Type

VIP loads four types of accounts. Every account report MUST filter by `TYPE`:

| Account Type | What It Is |
|-------------|------------|
| `Customer` | Distributors (Shipyard's direct customers) |
| `Distributed Customer` | Retail outlets (bars, restaurants, stores) |
| `Chain Banner` | Chain groupings (e.g., "Total Wine") |
| `Supplier` | The supplier themselves |

### 4. Grouping = Far Left in Summary Reports

The grouping field appears as the section header — it's the most prominent element. Best practices:
- **Product objects** (Items, Item Lines, Item Types): Group by record Name
- **Account reports**: Group by Account Name
- **Transaction reports** (Depletions, Placements): Group by Account Name, Item as first column
- **Inventory**: Group by Location Name, Item as first column

Never group by Supplier or Is_Active — these bury the record identity.

### 5. SF Report XML Gotchas

- **Grouping field cannot also be in columns** — deploy error: "can't include groupings in selected columns list"
- **`booleanFilter` for OR logic** — use `1 OR 2 OR 3` or `1 AND (2 OR 3 OR 4)` for complex filters
- **Nested boolean logic** — `(9 AND 11)` inside an OR clause to conditionally check fields (e.g., Chain Banner only when Retail_Type = Chain)
- **Folder circular reference** on deploy — deploy reports/dashboards WITHOUT the `-meta.xml` folder file if the folder already exists in the org
- **Deploy order** — report types first, then reports, then dashboards

### 6. Discovering Available Report Types

```bash
# List all report types in the org
sf data query --query "SELECT DeveloperName, Label FROM ReportType WHERE IsActive = true" --target-org <alias>

# Or via REST API for field-level detail
curl -H "Authorization: Bearer $TOKEN" \
  "$INSTANCE_URL/services/data/v62.0/analytics/reportTypes"
```

Built-in types from managed packages follow the pattern `CustomEntity$namespace__Object__c`.

## Prerequisites

VIP custom fields must exist in the target org before deploying reports. These come from the customer's deploy package (e.g., `customers/shipyard-ros2/deploy-v2/`).

## Development Workflow

1. **Build report types first** in sandbox UI (Setup > Report Types) — or deploy from this metadata
2. **Build reports/dashboards** in Report Builder / Dashboard Editor
3. **Retrieve to local:**
   ```bash
   sf project retrieve start \
     --metadata "ReportType,Report:VIP_Data,Dashboard:VIP_Data" \
     --target-org <sandbox-alias> \
     --output-dir integrations/vip-srs/metadata/force-app
   ```
4. **Review XML** — check for org-specific references (see Gotchas)
5. **Commit** to this repo

## Deploying to a Customer Org

```bash
# From the metadata directory:
cd integrations/vip-srs/metadata

# Deploy report types first
sf project deploy start --source-dir force-app/main/default/reportTypes --target-org <alias>

# Then reports (without folder metadata if folder exists)
sf project deploy start --source-dir force-app/main/default/reports --target-org <alias>

# Then dashboards
sf project deploy start --source-dir force-app/main/default/dashboards --target-org <alias>
```

If you get a "circular reference" error on the folder, copy just the report/dashboard files (not the `-meta.xml` folder file) to a temp directory and deploy from there.

## Gotchas

- **`<runningUser>`** in dashboard XML references a specific username — must be updated per org
- **Report types must exist** before reports that reference them
- **Managed package namespace** — reports reference `ohfy__` prefixed fields; the managed package must be installed
- **Folder circular reference** — deploy without folder metadata if the folder already exists in the target org
- **Custom report types with outer joins** — fine for metrics, dangerous for data quality reports (see Lesson #1)

## Naming Conventions

- Report types: `VIP_{PrimaryObject}_{with_RelatedObject}` or `VIP_{Object}` for standalone
- Reports: descriptive name matching dashboard purpose (e.g., `Items_Missing_Required_Fields`)
- Dashboards: `{DomainArea}_{Perspective}` (e.g., `Data_Quality_Overview`)
- All deployed into `VIP_Data` folders
