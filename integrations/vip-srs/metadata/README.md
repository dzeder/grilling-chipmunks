# VIP Supplier Reports & Dashboards

Salesforce report types, reports, and dashboards for visualizing VIP integration data. Shared across all customers using the VIP SRS integration.

## Folders

Both reports and dashboards deploy into a single **VIP Data** folder in Salesforce.

## Report Catalog

### Supplier Metrics

| Report | Type | Description |
|--------|------|-------------|
| Depletions by Brand MTD | Matrix | Cases/revenue by brand by week |
| Depletions by Account MTD | Summary | Total cases/revenue per retailer |
| Active Placements Summary | Tabular | Active placements grouped by brand |
| Lost Placements Alert | Tabular | Accounts exceeding lost placement threshold |
| Inventory Levels by Item | Summary | Current Quantity_On_Hand by SKU |
| Stale Record Monitor | Tabular | VIP_File_Date__c freshness check |

### Dirty Data (Data Quality)

| Report | What it catches |
|--------|----------------|
| Orphaned Depletions (Missing Item) | Depletions where Item lookup is null |
| Orphaned Depletions (Missing Account) | Depletions where Customer lookup is null |
| Accounts Missing Chain Banner | Outlets without parent chain reference |
| Accounts with Unmapped Market | VIP Class of Trade codes with no SF picklist match |
| Items Missing Filter Prerequisites | Items missing RT/Type/UOM/Packaging_Type (blocks Depletion inserts) |
| Duplicate Item Lines | Item_Line__c records with duplicate BrandDesc |
| Stale Records by Object | Records where VIP_File_Date__c < today |
| Inventory Missing External ID | Pre-existing records without VIP_External_ID__c stamp |

### Dashboards

| Dashboard | Purpose |
|-----------|---------|
| Supplier Overview | Depletions, placements, inventory, and integration health at a glance |
| Data Quality Overview | All dirty data metrics on one screen — orphans, gaps, stale records, duplicates |

## Prerequisites

VIP custom fields must exist in the target org before deploying reports. These come from the customer's deploy package (e.g., `customers/shipyard-ros2/deploy-v2/`).

## Development Workflow

1. **Build report types first** in sandbox UI (Setup > Report Types)
2. **Build reports/dashboards** in Report Builder / Dashboard Editor
3. **Retrieve to local:**
   ```bash
   sf project retrieve start \
     --metadata "ReportType,Report:VIP_Data,Dashboard:VIP_Data" \
     --target-org <sandbox-alias> \
     --output-dir integrations/vip-srs/metadata/force-app
   ```
4. **Review XML** — check for org-specific references (see Gotchas below)
5. **Commit** to this repo

## Deploying to a Customer Org

```bash
sf project deploy start \
  --source-dir integrations/vip-srs/metadata/force-app \
  --target-org <customer-alias>
```

Deploy report types first if they don't already exist in the target org.

## Gotchas

- **`<runningUser>`** in dashboard XML references a specific username — must be updated per org before deploying
- **Report types must exist** before reports that reference them
- **Filter values** (date ranges, record type IDs) may need adjustment per customer
- **Managed package namespace** — reports reference `ohfy__` prefixed fields; the managed package must be installed

## Naming Conventions

- Report types: `VIP_{PrimaryObject}_{with_RelatedObject}`
- Reports: `{MetricOrDimension}_{GroupBy}_{TimeWindow}`
- Dashboards: `{DomainArea}_{Perspective}`
- All deployed into `VIP_Data` folders
