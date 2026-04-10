# Shipyard Brewing Company — Customizations

Custom fields, picklist values, validation rules, and other org-specific differences from standard OHFY configuration.

## Custom Fields — VIP External ID Fields (for upsert)

| Object | Field API Name | Type | Length | Unique | External ID | Purpose |
|--------|---------------|------|--------|--------|-------------|---------|
| ohfy__Invoice_Item__c | VIP_External_ID__c | Text | 255 | Yes | Yes | Upsert key for INL: prefix |
| ohfy__Inventory__c | VIP_External_ID__c | Text | 255 | Yes | Yes | Upsert key for IVT: prefix |
| ohfy__Inventory_History__c | VIP_External_ID__c | Text | 255 | Yes | Yes | Upsert key for IVH: prefix |
| ohfy__Inventory_Adjustment__c | VIP_External_ID__c | Text | 255 | Yes | Yes | Upsert key for IVA: prefix |
| ohfy__Allocation__c | VIP_External_ID__c | Text | 255 | Yes | Yes | Upsert key for ALC: prefix |
| ohfy__Placement__c | VIP_External_ID__c | Text | 255 | Yes | Yes | Upsert key for PLC: prefix (Account×Item) |

## Custom Fields — VIP Date Stamps (for stale record cleanup)

Applied to transaction objects: Depletion__c, Placement__c, Inventory_History__c, Inventory_Adjustment__c, Allocation__c (and Invoice__c, Invoice_Item__c when built).

| Field API Name | Type | Purpose |
|---------------|------|---------|
| VIP_File_Date__c | Date | Date of pipeline run — for stale cleanup ("last refreshed on") |
| VIP_From_Date__c | Date | Reporting period start (from file contents) |
| VIP_To_Date__c | Date | Reporting period end (from file contents) |

**Note:** VIP_File_Date__c is the date the pipeline ran, NOT a date from the file. FromDate/ToDate capture the file's reporting window.

## Custom Fields — Other

| Object | Field API Name | Type | Purpose |
|--------|---------------|------|---------|
| Account | ohfy__Premise_Type__c | Picklist (On Premise, Off Premise) | **Exists in managed package** — not a custom addition |

## Restricted Picklist Fields (verified 2026-04-10)

These managed package fields are restricted picklists. VIP crosswalk values must match exactly.

| Object | Field | Valid Values (sample) | Notes |
|--------|-------|----------------------|-------|
| Account | ohfy__Market__c | Grocery Store, Liquor, Convenience, Bars/Clubs/Taverns, Restaurants, ... (22 total) | 14 of 46 VIP Class of Trade codes have no match |
| Account | ohfy__Premise_Type__c | On Premise, Off Premise | Direct match |
| Account | ohfy__Retail_Type__c | Chain, Independent, Distributor | Direct match |
| ohfy__Item__c | ohfy__Packaging_Type__c | Each, Liter(s), 1/2 Barrel(s), Case Equivalent(s), ... (38 total) | Gated by record type — need Finished Good RT |
| ohfy__Item__c | ohfy__Package_Type__c | Packaged, Kegged, Bulk, ... (8 total) | Not restricted |
| ohfy__Location__c | ohfy__Type__c | Warehouse, Zone, Aisle, Rack, Shelf, Bin | Restricted |

## Record Types (verified 2026-04-10)

### Account
| Record Type | Developer Name | ID | Integration User | VIP Usage |
|------------|----------------|-----|------------------|-----------|
| Chain Banner | Chain_Banner | 012am0000050BVYAA2 | Assigned ✓ | SRSCHAIN chain parent records |
| Customer | Customer | 012am0000050BVXAA2 | Assigned ✓ | OUTDA distributors (ClassOfTrade 06/07/50) |
| Distributed Customer | Distributed_Customer | 012WF000003L8VWYA0 | Assigned ✓ | OUTDA retailers (all other ClassOfTrade) |
| Wholesaler | Wholesaler | 012am0000050BVaAAM | Not assigned | Not used by VIP |
| Supplier | Supplier | 012am0000050BVcAAM | Not assigned | Not used by VIP |

### Item__c
| Record Type | Developer Name | Notes |
|------------|----------------|-------|
| Finished Good | Finished_Good | Required for VIP items. Integration user needs assignment. |
| Keg Shell | Keg_Shell | |
| Merchandise | Merchandise | |
| Packaging | Packaging | |
| Raw Material | Raw_Material | |

## Lookup Filters

| Object.Field | Filter | Notes |
|-------------|--------|-------|
| ohfy__Depletion__c.ohfy__Item__c | Item must have: Finished Good RT + Type__c + UOM__c + Packaging_Type__c + Transformation_Setting__c | `optionalFilter: false` — blocks save if any prerequisite missing |

## Validation Rules

| Object | Rule Name | Description |
|--------|-----------|-------------|
| ohfy__Item__c | (Error Code 003) | "Please ensure Stock UOM Sub Type field is set for Finished Goods" — requires `Packaging_Type__c` when Type = Finished Good |

## Other Customizations

| Field | Max Length | Notes |
|-------|-----------|-------|
| ohfy__Location_Code__c | 5 | Raw dist ID only (e.g., `FL01`), not prefixed key |
