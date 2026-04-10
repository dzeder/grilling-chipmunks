/**
 * VIP SRS Script 08: CTLDA -> Allocation__c
 *
 * Transforms VIP control/allocation data into Salesforce Allocation records.
 * Each row represents a supplier-to-distributor allocation for a given item,
 * UOM, and period.
 *
 * Source: CTLDA file (8 columns)
 * Target: Allocation__c (VIP_External_ID__c = ALC:{DistId}:{SupplierItem}:{ControlDate}:{UOM})
 * Rows: ~24 per file
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.8
 */

// =============================================================================
// INLINE SHARED
// =============================================================================

var PREFIX = { ITEM: 'ITM', ALLOCATION: 'ALC', LOCATION: 'LOC' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };
var NS = SF_CONFIG.namespacePrefix + '__';

function allocationKey(distId, supplierItem, controlDate, uom) { return PREFIX.ALLOCATION + ':' + distId + ':' + supplierItem + ':' + controlDate + ':' + uom; }
function itemKey(supplierItem) { return PREFIX.ITEM + ':' + supplierItem; }

function clean(v) { if (v === undefined || v === null) return ''; return String(v).trim(); }

function toSfMonthDate(yyyymm) {
  if (!yyyymm || String(yyyymm).length < 6) return '';
  var s = String(yyyymm);
  return s.substring(0, 4) + '-' + s.substring(4, 6) + '-01';
}

function toSfEndOfMonth(yyyymm) {
  if (!yyyymm || String(yyyymm).length < 6) return '';
  var s = String(yyyymm);
  var year = parseInt(s.substring(0, 4), 10);
  var month = parseInt(s.substring(4, 6), 10);
  // Day 0 of next month = last day of current month
  var lastDay = new Date(year, month, 0).getDate();
  var mm = month < 10 ? '0' + month : '' + month;
  var dd = lastDay < 10 ? '0' + lastDay : '' + lastDay;
  return year + '-' + mm + '-' + dd;
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
// UOM MAP
// =============================================================================

var UOM_MAP = { 'B': 'Bottle', 'C': 'Case' };

// =============================================================================
// TRANSFORM
// =============================================================================

function transformAllocation(row, distId, fileDate) {
  var supplierItem = clean(row.SupplierItem);
  var controlDate = clean(row.ControlDate);
  var uom = clean(row.UnitOfMeasure);
  var record = {};

  record.VIP_External_ID__c = allocationKey(distId, supplierItem, controlDate, uom);

  // Item lookup (relationship syntax)
  record[NS + 'Item__r'] = {};
  record[NS + 'Item__r'][NS + 'VIP_External_ID__c'] = itemKey(supplierItem);

  // Location lookup (distributor's warehouse)
  record[NS + 'Location__r'] = { VIP_External_ID__c: PREFIX.LOCATION + ':' + distId };

  // Allocated_Case_Amount__c is the correct writable quantity field
  record[NS + 'Allocated_Case_Amount__c'] = toInt(row.Quantity);
  record[NS + 'Start_Date__c'] = toSfMonthDate(controlDate);
  record[NS + 'End_Date__c'] = toSfEndOfMonth(controlDate);
  record[NS + 'Is_Active__c'] = true;

  // Stale cleanup dates (unmanaged custom fields)
  // Derive From/To from ControlDate month boundaries so cleanup script 09 can match
  record.VIP_From_Date__c = toSfMonthDate(controlDate);
  record.VIP_To_Date__c = toSfEndOfMonth(controlDate);
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

  // 1. VALIDATE & FILTER
  var valid = [];
  var invalid = [];
  var skipped = [];

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

    var controlDate = clean(row.ControlDate);
    if (!controlDate) {
      invalid.push({ rowIndex: idx, reason: 'Missing ControlDate' });
      return;
    }

    valid.push(row);
  });

  // 2. TRANSFORM
  var records = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    var distId = clean(row.DistId) || targetDistId;
    try {
      records.push(transformAllocation(row, distId, fileDate));
    } catch (e) {
      transformErrors.push({ rowIndex: idx, error: e.message });
    }
  });

  // 3. BATCH (unmanaged VIP_External_ID__c)
  var chunks = chunkArray(records);
  var batches = chunks.map(function(chunk) {
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
            NS + 'Allocation__c/VIP_External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'alc_' + idx,
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
    errors: invalid.concat(transformErrors.map(function(e) {
      return { rowIndex: e.rowIndex, reason: 'Transform error: ' + e.error };
    })),
    errorCount: invalid.length + transformErrors.length,
    skippedCount: skipped.length,
    summary: {
      total: rows.length,
      valid: records.length,
      invalid: invalid.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      batches: batches.length,
      timestamp: new Date().toISOString()
    }
  };
};
