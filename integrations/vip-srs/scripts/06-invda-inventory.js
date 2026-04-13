/**
 * VIP SRS Script 06: INVDA -> Inventory__c + Inventory_History__c + Inventory_Adjustment__c
 *
 * Three output streams routed by TransCode:
 *   - TransCode 10 (latest date per item) -> Inventory__c (merge case/bottle per item)
 *   - TransCode 10,11,12 (all dates)      -> Inventory_History__c (daily snapshots)
 *   - TransCode 20-49,99 (skip 50-59,70,80) -> Inventory_Adjustment__c (movements)
 *
 * Source: INVDA file (19 columns)
 * Target: Inventory__c  (VIP_External_ID__c = IVT:{DistId}:{SupplierItem})
 *         Inventory_History__c (VIP_External_ID__c = IVH:{DistId}:{SupplierItem}:{PostingDate}:{UOM})
 *         Inventory_Adjustment__c (VIP_External_ID__c = IVA:{DistId}:{SupplierItem}:{TransCode}:{TransDate}:{UOM})
 * Rows: ~656 per file
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.7
 */

// =============================================================================
// INLINE SHARED
// =============================================================================

var PREFIX = { ITEM: 'ITM', LOCATION: 'LOC', INVENTORY: 'IVT', HISTORY: 'IVH', ADJUSTMENT: 'IVA' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };
var NS = SF_CONFIG.namespacePrefix + '__';

function inventoryKey(distId, supplierItem) { return PREFIX.INVENTORY + ':' + distId + ':' + supplierItem; }
function historyKey(distId, supplierItem, postingDate, uom) { return PREFIX.HISTORY + ':' + distId + ':' + supplierItem + ':' + postingDate + ':' + uom; }
function adjustmentKey(distId, supplierItem, transCode, transDate, uom) { return PREFIX.ADJUSTMENT + ':' + distId + ':' + supplierItem + ':' + transCode + ':' + transDate + ':' + uom; }
function itemKey(supplierItem) { return PREFIX.ITEM + ':' + supplierItem; }
function locationKey(distId) { return PREFIX.LOCATION + ':' + distId; }

function clean(v) { if (v === undefined || v === null) return ''; return String(v).trim(); }

function toSfDate(yyyymmdd) {
  if (!yyyymmdd || String(yyyymmdd).length < 8) return '';
  var s = String(yyyymmdd);
  return s.substring(0, 4) + '-' + s.substring(4, 6) + '-' + s.substring(6, 8);
}

function toInt(v) {
  var n = parseInt(v, 10);
  return isNaN(n) ? 0 : n;
}

function sanitizeForUrl(value) {
  if (!value) return '';
  return String(value)
    .replace(/%/g, '%25').replace(/ /g, '%20').replace(/#/g, '%23')
    .replace(/\//g, '%2F').replace(/\?/g, '%3F').replace(/&/g, '%26')
    .replace(/\+/g, '%2B').replace(/=/g, '%3D')
    .replace(/\[/g, '%5B').replace(/\]/g, '%5D');
}

function chunkArray(array, size) {
  var s = size || SF_CONFIG.batchSize;
  var chunks = [];
  for (var i = 0; i < array.length; i += s) { chunks.push(array.slice(i, i + s)); }
  return chunks;
}

// =============================================================================
// CROSSWALKS
// =============================================================================

var TRANS_CODE = {
  '10': { type: null, reason: null, target: 'inventory+history' },
  '11': { type: null, reason: null, target: 'history' },
  '12': { type: null, reason: null, target: 'history' },
  '20': { type: 'Addition', reason: 'Purchase', target: 'adjustment' },
  '21': { type: 'Addition', reason: 'Transfer', target: 'adjustment' },
  '22': { type: 'Subtraction', reason: 'Transfer', target: 'adjustment' },
  '30': { type: 'Subtraction', reason: 'Return', target: 'adjustment' },
  '40': { type: 'Subtraction', reason: 'Breakage', target: 'adjustment' },
  '41': { type: 'Subtraction', reason: 'Sample', target: 'adjustment' },
  '50': { type: null, reason: null, target: 'skip' },
  '51': { type: null, reason: null, target: 'skip' },
  '52': { type: null, reason: null, target: 'skip' },
  '53': { type: null, reason: null, target: 'skip' },
  '54': { type: null, reason: null, target: 'skip' },
  '55': { type: null, reason: null, target: 'skip' },
  '59': { type: null, reason: null, target: 'skip' },
  '70': { type: null, reason: null, target: 'skip' },
  '80': { type: null, reason: null, target: 'skip' },
  '99': { type: 'Addition', reason: 'Adjustment', target: 'adjustment' }
};

// =============================================================================
// TRANSFORM
// =============================================================================

function transformInventory(distId, supplierItem, casesOnHand, unitsOnHand) {
  // Collapse 99Z generic volume placeholders to single item
  var itemSuppItem = supplierItem.indexOf('99Z') === 0 ? '99Z-GENERIC' : supplierItem;
  var record = {};
  record.VIP_External_ID__c = inventoryKey(distId, supplierItem);
  // Item lookup (master-detail — set on create, ignored on update)
  record[NS + 'Item__r'] = {};
  record[NS + 'Item__r'][NS + 'VIP_External_ID__c'] = itemKey(itemSuppItem);
  // Location lookup via VIP_External_ID__c
  record[NS + 'Location__r'] = { VIP_External_ID__c: locationKey(distId) };
  // Quantity_On_Hand__c is the writable case quantity field
  record[NS + 'Quantity_On_Hand__c'] = casesOnHand;
  record[NS + 'Is_Active__c'] = true;
  return record;
}

function transformHistory(row, distId, fileDate) {
  var supplierItem = clean(row.SupplierItem);
  // Collapse 99Z generic volume placeholders to single item
  var itemSuppItem = supplierItem.indexOf('99Z') === 0 ? '99Z-GENERIC' : supplierItem;
  var postingDate = clean(row.PostingDate);
  var uom = clean(row.UnitOfMeasure);
  var record = {};

  record.VIP_External_ID__c = historyKey(distId, supplierItem, postingDate, uom);
  record[NS + 'Stamped_Date__c'] = toSfDate(postingDate);
  // Item lookup (relationship syntax)
  record[NS + 'Item__r'] = {};
  record[NS + 'Item__r'][NS + 'VIP_External_ID__c'] = itemKey(itemSuppItem);
  record[NS + 'Quantity_On_Hand__c'] = toInt(row.Quantity);
  // Parent Inventory lookup (relationship syntax)
  record[NS + 'Inventory__r'] = { VIP_External_ID__c: inventoryKey(distId, supplierItem) };

  // Stale cleanup dates (unmanaged custom fields)
  record.VIP_From_Date__c = toSfDate(row.FromDate);
  record.VIP_To_Date__c = toSfDate(row.ToDate);
  if (fileDate) record.VIP_File_Date__c = fileDate;

  return record;
}

function transformAdjustment(row, distId, transCodeInfo, fileDate) {
  var supplierItem = clean(row.SupplierItem);
  var transCode = clean(row.TransCode);
  var transDate = clean(row.TransDate);
  var uom = clean(row.UnitOfMeasure);
  var record = {};

  record.VIP_External_ID__c = adjustmentKey(distId, supplierItem, transCode, transDate, uom);
  record[NS + 'Type__c'] = transCodeInfo.type;
  record[NS + 'Reason__c'] = transCodeInfo.reason;
  record[NS + 'Status__c'] = 'Complete';
  record[NS + 'Date__c'] = toSfDate(transDate);
  record[NS + 'Quantity_Change__c'] = toInt(row.Quantity);
  // Parent Inventory lookup (relationship syntax)
  record[NS + 'Inventory__r'] = { VIP_External_ID__c: inventoryKey(distId, supplierItem) };

  // Stale cleanup dates (unmanaged custom fields)
  record.VIP_From_Date__c = toSfDate(row.FromDate);
  record.VIP_To_Date__c = toSfDate(row.ToDate);
  if (fileDate) record.VIP_File_Date__c = fileDate;

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];
  var targetDistId = input.targetDistId || input.distributorId;
  var fileDate = input.fileDate || '';

  // 1. VALIDATE, FILTER, & ROUTE
  var inventoryRows = [];   // TransCode 10 only
  var historyRows = [];     // TransCode 10, 11, 12
  var adjustmentRows = [];  // TransCode 20-49, 99
  var skipped = [];
  var invalid = [];

  rows.forEach(function(row, idx) {
    var recordType = clean(row.RecordType);
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ rowIndex: idx, reason: 'Non-DETAIL' });
      return;
    }

    var distId = clean(row.DistId);
    if (targetDistId && distId !== targetDistId) {
      skipped.push({ rowIndex: idx, reason: 'Wrong distributor: ' + distId });
      return;
    }

    var supplierItem = clean(row.SupplierItem);
    if (!supplierItem) {
      invalid.push({ rowIndex: idx, reason: 'Missing SupplierItem' });
      return;
    }

    var transCode = clean(row.TransCode);
    var tcInfo = TRANS_CODE[transCode];
    if (!tcInfo) {
      skipped.push({ rowIndex: idx, reason: 'Unknown TransCode: ' + transCode });
      return;
    }

    if (tcInfo.target === 'skip') {
      skipped.push({ rowIndex: idx, reason: 'Skipped TransCode: ' + transCode });
      return;
    }

    // Route to appropriate stream
    if (tcInfo.target === 'inventory+history') {
      inventoryRows.push(row);
      historyRows.push(row);
    } else if (tcInfo.target === 'history') {
      historyRows.push(row);
    } else if (tcInfo.target === 'adjustment') {
      adjustmentRows.push(row);
    }
  });

  // 2a. TRANSFORM — Inventory__c (merge case/bottle, latest date per item)
  var inventoryRecords = [];
  var transformErrors = [];

  try {
    // Group by SupplierItem, find latest PostingDate per item, merge UOMs
    var itemMap = {}; // { supplierItem: { latestDate, cases, units, distId } }

    inventoryRows.forEach(function(row) {
      var supplierItem = clean(row.SupplierItem);
      var postingDate = clean(row.PostingDate);
      var uom = clean(row.UnitOfMeasure);
      var qty = toInt(row.Quantity);
      var distId = clean(row.DistId) || targetDistId;

      if (!itemMap[supplierItem]) {
        itemMap[supplierItem] = { latestDate: postingDate, cases: 0, units: 0, distId: distId };
      }

      var entry = itemMap[supplierItem];

      if (postingDate > entry.latestDate) {
        // New latest date — reset quantities
        entry.latestDate = postingDate;
        entry.cases = 0;
        entry.units = 0;
      }

      if (postingDate === entry.latestDate) {
        if (uom === 'C') entry.cases = qty;
        else if (uom === 'B') entry.units = qty;
      }
    });

    Object.keys(itemMap).forEach(function(supplierItem) {
      var entry = itemMap[supplierItem];
      inventoryRecords.push(transformInventory(entry.distId, supplierItem, entry.cases, entry.units));
    });
  } catch (e) {
    transformErrors.push({ stream: 'inventory', error: e.message });
  }

  // 2b. TRANSFORM — Inventory_History__c
  var historyRecords = [];
  historyRows.forEach(function(row, idx) {
    var distId = clean(row.DistId) || targetDistId;
    try {
      historyRecords.push(transformHistory(row, distId, fileDate));
    } catch (e) {
      transformErrors.push({ stream: 'history', rowIndex: idx, error: e.message });
    }
  });

  // 2c. TRANSFORM — Inventory_Adjustment__c
  var adjustmentRecords = [];
  adjustmentRows.forEach(function(row, idx) {
    var distId = clean(row.DistId) || targetDistId;
    var transCode = clean(row.TransCode);
    var tcInfo = TRANS_CODE[transCode];
    try {
      adjustmentRecords.push(transformAdjustment(row, distId, tcInfo, fileDate));
    } catch (e) {
      transformErrors.push({ stream: 'adjustment', rowIndex: idx, error: e.message });
    }
  });

  // 3. BATCH — Inventory__c
  // If existingInventoryMap is provided, match by Item VIP_External_ID__c + Location
  // to find pre-existing records and PATCH by record ID (stamps VIP_External_ID__c).
  // This avoids the managed "Duplicate Record Blocked" validation rule.
  var existingMap = input.existingInventoryMap || {};

  var inventoryChunks = chunkArray(inventoryRecords);
  var inventoryBatches = inventoryChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.VIP_External_ID__c;
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== 'VIP_External_ID__c') body[key] = record[key];
        });

        // Check if a pre-existing Inventory record matches this Item+Location
        var existingId = existingMap[extId];
        if (existingId) {
          // PATCH by record ID — update existing record and stamp VIP_External_ID__c.
          // Strip master-detail relationship fields (Item__r, Location__r) — they're
          // read-only on update and already correct on the existing record.
          delete body[NS + 'Item__r'];
          delete body[NS + 'Location__r'];
          body.VIP_External_ID__c = extId;
          return {
            method: 'PATCH',
            url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
              NS + 'Inventory__c/' + existingId,
            referenceId: 'inv_' + idx,
            body: body
          };
        }

        // Normal upsert by VIP_External_ID__c (for new records or re-runs)
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            NS + 'Inventory__c/VIP_External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'inv_' + idx,
          body: body
        };
      })
    };
  });

  // 3b. BATCH — Inventory_History__c (unmanaged VIP_External_ID__c)
  var historyChunks = chunkArray(historyRecords);
  var historyBatches = historyChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.VIP_External_ID__c;
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== 'VIP_External_ID__c') body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            NS + 'Inventory_History__c/VIP_External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'ivh_' + idx,
          body: body
        };
      })
    };
  });

  // 3c. BATCH — Inventory_Adjustment__c (unmanaged VIP_External_ID__c)
  var adjustmentChunks = chunkArray(adjustmentRecords);
  var adjustmentBatches = adjustmentChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.VIP_External_ID__c;
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== 'VIP_External_ID__c') body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            NS + 'Inventory_Adjustment__c/VIP_External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'iva_' + idx,
          body: body
        };
      })
    };
  });

  // 4. OUTPUT
  return {
    inventoryBatches: inventoryBatches,
    inventoryBatchCount: inventoryBatches.length,
    inventoryRecords: inventoryRecords,
    inventoryCount: inventoryRecords.length,
    historyBatches: historyBatches,
    historyBatchCount: historyBatches.length,
    historyRecords: historyRecords,
    historyCount: historyRecords.length,
    adjustmentBatches: adjustmentBatches,
    adjustmentBatchCount: adjustmentBatches.length,
    adjustmentRecords: adjustmentRecords,
    adjustmentCount: adjustmentRecords.length,
    // Unified batches/records for test runner compatibility
    batches: inventoryBatches,
    batchCount: inventoryBatches.length,
    records: inventoryRecords,
    recordCount: inventoryRecords.length,
    errors: invalid.concat(transformErrors.map(function(e) {
      return { rowIndex: e.rowIndex, stream: e.stream, reason: 'Transform error: ' + e.error };
    })),
    errorCount: invalid.length + transformErrors.length,
    skippedCount: skipped.length,
    summary: {
      total: rows.length,
      inventory: inventoryRecords.length,
      history: historyRecords.length,
      adjustments: adjustmentRecords.length,
      invalid: invalid.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      inventoryBatches: inventoryBatches.length,
      historyBatches: historyBatches.length,
      adjustmentBatches: adjustmentBatches.length,
      timestamp: new Date().toISOString()
    }
  };
};
