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

## Custom Fields — VIP Date Stamps (for stale record cleanup)

Applied to 6 objects: Invoice__c, Invoice_Item__c, Placement__c, Inventory_History__c, Inventory_Adjustment__c, Allocation__c

| Field API Name | Type | Purpose |
|---------------|------|---------|
| VIP_File_Date__c | Date | Filename date stamp for stale cleanup |
| VIP_From_Date__c | Date | Reporting period start |
| VIP_To_Date__c | Date | Reporting period end |

## Custom Fields — Other

| Object | Field API Name | Type | Purpose |
|--------|---------------|------|---------|
| Account | Premise_Type__c | Picklist (On Premise, Off Premise) | Needs verification if already exists |

## Custom Picklist Values

| Object | Field | Added Values | Reason |
|--------|-------|-------------|--------|
| Account | Market__c / Account_Sub_Type | 46 Class of Trade values | VIP SRS OUTDA crosswalk (see spec Section 7.1) |

## Validation Rules

| Object | Rule Name | Description |
|--------|-----------|-------------|
| _(none added yet)_ | | |

## Other Customizations

<!-- TBD after sandbox connection -->
