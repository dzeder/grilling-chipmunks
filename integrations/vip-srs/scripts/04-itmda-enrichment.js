/**
 * VIP SRS Script 04: ITMDA → Item__c (Distributor Enrichment)
 *
 * Enriches Item__c records (created by 02-itm2da-items.js) with
 * distributor-specific data: local SKU numbers, UPCs, short names.
 * Does NOT overwrite the Item Name set by ITM2DA.
 *
 * Source: ITMDA file (17 columns)
 * Target: Item__c (VIP_External_ID__c = ITM:{SupplierItem})
 * Rows: ~102 per file (filtered by distributor)
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.4
 */

// =============================================================================
// INLINE SHARED
// =============================================================================

var PREFIX = { ITEM: 'ITM' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };

function itemKey(supplierItem) { return PREFIX.ITEM + ':' + supplierItem; }
function clean(v) { if (v === undefined || v === null) return ''; return String(v).trim(); }

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
// CONFIG
// =============================================================================

var NS = SF_CONFIG.namespacePrefix + '__';

var CONFIG = {
  serviceName: 'VIP SRS — ITMDA Item Enrichment',
  sobject: NS + 'Item__c',
  externalIdField: NS + 'VIP_External_ID__c'
};

// =============================================================================
// TRANSFORM
// =============================================================================

function transformEnrichment(row) {
  var supplierItem = clean(row.SupplierItem);
  var record = {};

  record[NS + 'VIP_External_ID__c'] = itemKey(supplierItem);

  // Distributor SKU numbers
  var distItem = clean(row.DistItem);
  if (distItem) {
    record[NS + 'Item_Number__c'] = distItem;
    record[NS + 'SKU_Number__c'] = distItem;
  }

  // Short name (does NOT overwrite Name)
  var description = clean(row.Description);
  if (description) {
    record[NS + 'Short_Name__c'] = description;
  }

  // UPCs
  var gtin = clean(row.GTIN);
  if (gtin && !/^0+$/.test(gtin)) {
    record[NS + 'UPC__c'] = gtin;
  }

  var distItemGTIN = clean(row.DistItemGTIN);
  if (distItemGTIN && !/^0+$/.test(distItemGTIN)) {
    record[NS + 'Unit_UPC__c'] = distItemGTIN;
  }

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];
  var targetDistId = input.targetDistId || input.distributorId;
  // Set of known supplier items from ITM2DA (for orphan detection)
  var knownItems = input.knownItems || null; // Set or array

  var knownItemSet = null;
  if (knownItems) {
    if (Array.isArray(knownItems)) {
      knownItemSet = {};
      knownItems.forEach(function(k) { knownItemSet[k] = true; });
    } else {
      knownItemSet = knownItems;
    }
  }

  // 1. VALIDATE & FILTER
  var valid = [];
  var invalid = [];
  var skipped = [];
  var orphaned = [];

  rows.forEach(function(row, idx) {
    var recordType = clean(row.RecordType);
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ rowIndex: idx, reason: 'Non-DETAIL' });
      return;
    }

    // Filter by distributor
    var distributor = clean(row.Distributor);
    if (targetDistId && distributor !== targetDistId) {
      skipped.push({ rowIndex: idx, reason: 'Wrong distributor: ' + distributor });
      return;
    }

    var supplierItem = clean(row.SupplierItem);
    if (!supplierItem) {
      invalid.push({ rowIndex: idx, reason: 'Missing SupplierItem' });
      return;
    }

    // Orphan detection: item not in ITM2DA
    if (knownItemSet && !knownItemSet[supplierItem]) {
      orphaned.push({ rowIndex: idx, reason: 'SupplierItem ' + supplierItem + ' not found in ITM2DA', supplierItem: supplierItem });
      return;
    }

    valid.push(row);
  });

  // 2. TRANSFORM
  var records = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    try {
      records.push(transformEnrichment(row));
    } catch (e) {
      transformErrors.push({ rowIndex: idx, error: e.message });
    }
  });

  // 3. BATCH
  var chunks = chunkArray(records);
  var batches = chunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record[CONFIG.externalIdField];
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key === CONFIG.externalIdField) return;
          body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            CONFIG.sobject + '/' + CONFIG.externalIdField + '/' + sanitizeForUrl(extId),
          referenceId: 'item_enrich_' + idx,
          body: body
        };
      })
    };
  });

  // 4. OUTPUT
  return {
    batches: batches,
    batchCount: batches.length,
    records: records,
    recordCount: records.length,
    orphaned: orphaned,
    orphanedCount: orphaned.length,
    errors: invalid.concat(transformErrors.map(function(e) {
      return { rowIndex: e.rowIndex, reason: 'Transform error: ' + e.error };
    })),
    errorCount: invalid.length + transformErrors.length,
    skippedCount: skipped.length,
    summary: {
      total: rows.length,
      valid: records.length,
      invalid: invalid.length,
      orphaned: orphaned.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      batches: batches.length,
      timestamp: new Date().toISOString()
    }
  };
};
