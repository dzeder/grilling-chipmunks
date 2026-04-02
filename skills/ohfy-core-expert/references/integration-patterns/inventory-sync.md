# Inventory Sync

## Overview

Patterns for safely synchronizing inventory levels from external systems to OHFY-Core.

---

## Pattern 1: Full Inventory Sync

Sync all inventory from external system, creating or updating as needed.

```javascript
async function syncInventory(externalInventory) {
    // Map: itemExternalId_locationId → quantity
    const inventoryMap = new Map();

    externalInventory.forEach(inv => {
        const key = `${inv.itemExternalId}_${inv.locationId}`;
        inventoryMap.set(key, inv.quantity);
    });

    // Query existing inventory
    const existingInventory = await sf.query({
        query: `SELECT Id, ohfy__Item__r.ohfy__External_ID__c, ohfy__Location__c, ohfy__Quantity__c
                FROM ohfy__Inventory__c
                WHERE ohfy__Item__r.ohfy__External_ID__c IN ('${Array.from(inventoryMap.keys()).join("','")}') `
    });

    const toUpdate = [];
    const toCreate = [];

    // Update existing
    existingInventory.forEach(inv => {
        const key = `${inv.ohfy__Item__r.ohfy__External_ID__c}_${inv.ohfy__Location__c}`;
        const newQty = inventoryMap.get(key);

        if (newQty !== undefined && newQty !== inv.ohfy__Quantity__c) {
            toUpdate.push({
                Id: inv.Id,
                ohfy__Quantity__c: newQty
            });
        }

        // Remove from map (processed)
        inventoryMap.delete(key);
    });

    // Create new for remaining
    for (const [key, quantity] of inventoryMap) {
        const [itemExternalId, locationId] = key.split('_');

        toCreate.push({
            ohfy__Item__c: itemExternalId,  // Will need to lookup Item Id
            ohfy__Location__c: locationId,
            ohfy__Quantity__c: quantity
        });
    }

    // Execute updates and creates
    if (toUpdate.length > 0) {
        await sf.update(toUpdate);
    }

    if (toCreate.length > 0) {
        await sf.create(toCreate);
    }
}
```

---

## Pattern 2: Delta Inventory Sync

Only sync inventory that changed since last sync.

```javascript
async function deltaInventorySync(lastSyncDate) {
    // Get changed inventory from external system
    const changedInventory = await externalSystem.getInventoryChanges(lastSyncDate);

    const compositeRequests = [];

    changedInventory.forEach(inv => {
        compositeRequests.push({
            method: "PATCH",
            url: `/services/data/v58.0/sobjects/ohfy__Inventory__c/ohfy__Item__c,ohfy__Location__c/${inv.itemId},${inv.locationId}`,
            body: {
                ohfy__Quantity__c: inv.quantity,
                ohfy__Available_Quantity__c: inv.available
            }
        });
    });

    // Batch and execute
    const batches = [];
    for (let i = 0; i < compositeRequests.length; i += 25) {
        batches.push(compositeRequests.slice(i, i + 25));
    }

    for (const batch of batches) {
        await sf.composite({ allOrNone: false, compositeRequest: batch });
    }

    // Update last sync timestamp
    await saveLastSyncDate(new Date());
}
```

---

## Pattern 3: Safe Inventory Adjustment

Adjust inventory using Inventory_Adjustment__c for audit trail.

```javascript
async function adjustInventory(adjustments) {
    const compositeRequests = [];

    adjustments.forEach(adj => {
        // Create adjustment record
        compositeRequests.push({
            referenceId: `adj_${adj.inventoryId}`,
            method: "POST",
            url: "/services/data/v58.0/sobjects/ohfy__Inventory_Adjustment__c",
            body: {
                ohfy__Inventory__c: adj.inventoryId,
                ohfy__Adjustment_Type__c: adj.type,  // "Physical Count", "Damage", etc.
                ohfy__Quantity__c: adj.delta,  // +/- amount
                ohfy__Reason__c: adj.reason
            }
        });

        // Update inventory quantity
        compositeRequests.push({
            method: "PATCH",
            url: `/services/data/v58.0/sobjects/ohfy__Inventory__c/${adj.inventoryId}`,
            body: {
                ohfy__Quantity__c: adj.newQuantity
            }
        });
    });

    await sf.composite({ allOrNone: false, compositeRequest: compositeRequests });
}
```

---

## Pattern 4: Inventory Validation

Validate inventory before sync to prevent negative quantities.

```javascript
async function validateAndSyncInventory(updates) {
    // Query current inventory
    const inventoryIds = updates.map(u => u.inventoryId);
    const currentInventory = await sf.query({
        query: `SELECT Id, ohfy__Quantity__c, ohfy__Allocated_Quantity__c
                FROM ohfy__Inventory__c
                WHERE Id IN ('${inventoryIds.join("','")}')`
    });

    const inventoryMap = new Map();
    currentInventory.forEach(inv => {
        inventoryMap.set(inv.Id, inv);
    });

    const validated = [];
    const errors = [];

    updates.forEach(update => {
        const current = inventoryMap.get(update.inventoryId);

        if (!current) {
            errors.push({ inventoryId: update.inventoryId, error: "Inventory not found" });
            return;
        }

        // Check if update would cause negative quantity
        if (update.newQuantity < 0) {
            errors.push({
                inventoryId: update.inventoryId,
                error: "Cannot set negative quantity",
                current: current.ohfy__Quantity__c,
                requested: update.newQuantity
            });
            return;
        }

        // Check if update would cause available < allocated
        if (update.newQuantity < current.ohfy__Allocated_Quantity__c) {
            errors.push({
                inventoryId: update.inventoryId,
                error: "New quantity less than allocated quantity",
                allocated: current.ohfy__Allocated_Quantity__c,
                requested: update.newQuantity
            });
            return;
        }

        validated.push(update);
    });

    // Sync validated updates
    if (validated.length > 0) {
        await syncInventoryUpdates(validated);
    }

    return { success: validated.length, errors };
}
```

---

## Pattern 5: Inventory Reconciliation

Compare OHFY inventory with external system and flag discrepancies.

```javascript
async function reconcileInventory() {
    // Get inventory from external system
    const externalInventory = await externalSystem.getAllInventory();

    // Get inventory from OHFY
    const ohfyInventory = await sf.query({
        query: `SELECT Id, ohfy__Item__r.ohfy__External_ID__c, ohfy__Location__c, ohfy__Quantity__c
                FROM ohfy__Inventory__c`
    });

    const discrepancies = [];

    // Build map of OHFY inventory
    const ohfyMap = new Map();
    ohfyInventory.forEach(inv => {
        const key = `${inv.ohfy__Item__r.ohfy__External_ID__c}_${inv.ohfy__Location__c}`;
        ohfyMap.set(key, inv.ohfy__Quantity__c);
    });

    // Compare with external
    externalInventory.forEach(ext => {
        const key = `${ext.itemExternalId}_${ext.locationId}`;
        const ohfyQty = ohfyMap.get(key);

        if (ohfyQty !== ext.quantity) {
            discrepancies.push({
                itemExternalId: ext.itemExternalId,
                locationId: ext.locationId,
                ohfyQuantity: ohfyQty || 0,
                externalQuantity: ext.quantity,
                difference: (ext.quantity - (ohfyQty || 0))
            });
        }
    });

    return discrepancies;
}
```

---

## Pattern 6: Allocation-Aware Sync

Sync inventory while preserving allocations.

```javascript
async function syncInventoryWithAllocations(updates) {
    // Query current inventory with allocations
    const inventoryIds = updates.map(u => u.inventoryId);
    const inventoryData = await sf.query({
        query: `SELECT Id, ohfy__Quantity__c, ohfy__Allocated_Quantity__c, ohfy__Available_Quantity__c
                FROM ohfy__Inventory__c
                WHERE Id IN ('${inventoryIds.join("','")}')`
    });

    const inventoryMap = new Map();
    inventoryData.forEach(inv => {
        inventoryMap.set(inv.Id, inv);
    });

    const toUpdate = [];

    updates.forEach(update => {
        const current = inventoryMap.get(update.inventoryId);

        // Calculate new available based on new total and existing allocations
        const newAvailable = update.newQuantity - current.ohfy__Allocated_Quantity__c;

        if (newAvailable < 0) {
            console.warn(`Warning: Inventory ${update.inventoryId} new available would be negative (${newAvailable})`);
            // Option: Cancel allocations or skip update
            return;
        }

        toUpdate.push({
            Id: update.inventoryId,
            ohfy__Quantity__c: update.newQuantity
            // Available_Quantity__c recalculated by trigger
        });
    });

    if (toUpdate.length > 0) {
        await sf.update(toUpdate);
    }
}
```

---

## Best Practices

### 1. Always Validate Before Update

Check for negative quantities and allocation conflicts before syncing.

### 2. Use Audit Trail

Create Inventory_Adjustment__c records for manual adjustments to maintain history.

### 3. Handle Errors Gracefully

```javascript
try {
    await syncInventory(data);
} catch (error) {
    console.error("Inventory sync failed:", error);
    // Log to monitoring system
    // Retry with exponential backoff
}
```

### 4. Implement Idempotency

Ensure sync can be safely retried without creating duplicates.

### 5. Monitor Discrepancies

Regularly reconcile OHFY inventory with external systems and alert on differences.

---

## See Also

- `../data-model/inventory-objects.md` - Inventory object structure
- `../triggers/inventory-triggers.md` - Inventory trigger validation
- `../validations/required-dependencies.md` - Inventory dependencies
