# ohfy__Inventory__c

Current stock levels per Item per Location. The junction object between Item and Location that tracks on-hand quantities.

## Quick facts

- **Namespace:** ohfy__
- **Key relationships:** Master-detail to Item__c, Master-detail to Location__c
- **Child objects:** Inventory_History__c, Inventory_Adjustment__c
- **Validation rules:** "Duplicate Record Blocked" — prevents duplicate Item+Location combos

## Integration constraints

### Duplicate Record Blocked validation rule

The managed package has a validation rule that prevents creating a second Inventory record for the same Item+Location combination. This means:

- **Standard upsert by external ID will fail** if a record already exists for that Item+Location but doesn't have the external ID set. The upsert tries to INSERT (because the external ID doesn't match), and the validation rule blocks it.
- **Pre-query pattern required:** Before loading Inventory, query existing records by Item/Location relationships, build a map of external ID → SF record ID, then PATCH by SF record ID instead of upserting.

### Pre-query pattern (three layers)

Any integration loading Inventory must implement this pattern:

**1. Lazy timing:** The pre-query must run AFTER Items and Locations have external IDs stamped (e.g., after Phase 1 in a multi-phase pipeline). Running at pipeline startup finds 0 matches because the Items don't have external IDs yet.

```sql
SELECT Id, ohfy__Item__r.ohfy__VIP_External_ID__c,
       ohfy__Location__r.VIP_External_ID__c
FROM ohfy__Inventory__c
WHERE ohfy__Item__r.ohfy__VIP_External_ID__c LIKE 'ITM:%'
```

**2. Batch-stamp all existing records:** History and Adjustment child records reference their parent Inventory by external ID. Even if your current file only produces N inventory records, the History rows may reference many more. Stamp external IDs on ALL existing Inventory records that match your Items/Locations — not just the ones in your current file.

**3. Strip master-detail fields on update:** When PATCHing an existing record by SF record ID, remove `ohfy__Item__r` and `ohfy__Location__r` from the body. These are master-detail (create-only) fields. Including them returns `INVALID_FIELD_FOR_INSERT_UPDATE`.

### Master-detail fields

`ohfy__Item__c` and `ohfy__Location__c` are master-detail relationships:
- **Create:** Set via `__r` relationship syntax (e.g., `ohfy__Item__r: { ohfy__VIP_External_ID__c: 'ITM:xxx' }`)
- **Update:** Read-only. Strip from PATCH body. The record stays parented to the original Item and Location.

### Writable vs formula fields

| Field | Writable | Notes |
|-------|----------|-------|
| `ohfy__Quantity_On_Hand__c` | Yes | Case quantity — use this for integration |
| `Cases_On_Hand__c` | No | Formula/rollup |
| `Units_On_Hand__c` | No | Formula/rollup |
| `ohfy__Is_Active__c` | Yes | Active flag |

## Discovered in

- VIP SRS E2E validation (2026-04-13): 264 pre-existing records in ROS2 sandbox blocked all VIP inventory inserts. Fixed with three-layer pre-query pattern.
