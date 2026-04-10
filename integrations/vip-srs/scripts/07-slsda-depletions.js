/**
 * VIP SRS Script 07: SLSDA -> Depletion__c
 *
 * Transforms VIP sales/invoice line items into Ohanafy Depletion records.
 * Each SLSDA row represents a distributor-to-retailer sale (depletion).
 *
 * Pre-filter: Drop SRS99 accounts, XXXXXX items, zero qty+price rows.
 *
 * Source: SLSDA file (25 columns)
 * Target: Depletion__c (VIP_External_ID__c = DEP:{DistId}:{InvoiceNbr}:{AcctNbr}:{SuppItem}:{UOM})
 * Rows: ~110 per file (filtered by distributor)
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.6
 */

// =============================================================================
// INLINE SHARED
// =============================================================================

var PREFIX = { ITEM: 'ITM', ACCOUNT: 'ACT', DEPLETION: 'DEP' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };
var NS = SF_CONFIG.namespacePrefix + '__';

function depletionKey(distId, invoiceNbr, acctNbr, suppItem, uom) {
  return PREFIX.DEPLETION + ':' + distId + ':' + invoiceNbr + ':' + acctNbr + ':' + suppItem + ':' + uom;
}
function accountKey(distId, acctNbr) { return PREFIX.ACCOUNT + ':' + distId + ':' + acctNbr; }
function itemKey(suppItem) { return PREFIX.ITEM + ':' + suppItem; }

function clean(v) { if (v === undefined || v === null) return ''; return String(v).trim(); }

function toSfDate(yyyymmdd) {
  if (!yyyymmdd || String(yyyymmdd).length < 8) return '';
  var s = String(yyyymmdd);
  return s.substring(0, 4) + '-' + s.substring(4, 6) + '-' + s.substring(6, 8);
}

function toNumber(v) {
  var n = parseFloat(v);
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
// TRANSFORM
// =============================================================================

function transformDepletion(row, distId, fileDate) {
  var invoiceNbr = clean(row.InvoiceNbr);
  var acctNbr = clean(row.AcctNbr);
  var suppItem = clean(row.SuppItem);
  var uom = clean(row.UOM);
  var qty = toNumber(row.Qty);
  var invoiceDate = clean(row.InvoiceDate);
  var record = {};

  // External ID — negative qty gets :NEG suffix
  var extId = depletionKey(distId, invoiceNbr, acctNbr, suppItem, uom);
  if (qty < 0) extId += ':NEG';
  record.VIP_External_ID__c = extId;

  // Customer lookup (master-detail — set on create via relationship)
  record[NS + 'Customer__r'] = { ohfy__External_ID__c: accountKey(distId, acctNbr) };

  // Item lookup (relationship syntax)
  record[NS + 'Item__r'] = {};
  record[NS + 'Item__r'][NS + 'VIP_External_ID__c'] = itemKey(suppItem);

  // Case vs Bottle quantity
  if (uom === 'C') {
    record[NS + 'Case_Quantity__c'] = qty;
  } else if (uom === 'B') {
    record.VIP_Unit_Quantity__c = qty;
  }

  // Date
  record[NS + 'Date__c'] = toSfDate(invoiceDate);

  // VIP-specific custom fields
  record.VIP_Net_Price__c = toNumber(row.NetPrice);
  record.VIP_Invoice_Number__c = invoiceNbr;

  // Stale cleanup dates (unmanaged)
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

  // 1. VALIDATE & FILTER
  var valid = [];
  var invalid = [];
  var skipped = [];

  rows.forEach(function(row, idx) {
    var recordType = clean(row.RcdType);
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ rowIndex: idx, reason: 'Non-DETAIL' });
      return;
    }

    var distId = clean(row.DistId);
    if (targetDistId && distId !== targetDistId) {
      skipped.push({ rowIndex: idx, reason: 'Wrong distributor: ' + distId });
      return;
    }

    // Drop SRS99 placeholder accounts
    var acctNbr = clean(row.AcctNbr);
    if (acctNbr === 'SRS99') {
      skipped.push({ rowIndex: idx, reason: 'SRS99 placeholder' });
      return;
    }

    // Drop XXXXXX placeholder items
    var suppItem = clean(row.SuppItem);
    if (suppItem === 'XXXXXX') {
      skipped.push({ rowIndex: idx, reason: 'XXXXXX placeholder' });
      return;
    }

    // Drop zero qty + zero price rows
    var qty = toNumber(row.Qty);
    var netPrice = toNumber(row.NetPrice);
    if (qty === 0 && netPrice === 0) {
      skipped.push({ rowIndex: idx, reason: 'Zero qty and price' });
      return;
    }

    if (!clean(row.InvoiceNbr)) {
      invalid.push({ rowIndex: idx, reason: 'Missing InvoiceNbr' });
      return;
    }

    valid.push(row);
  });

  // 2. TRANSFORM — Depletion__c (one per row)
  var records = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    var distId = clean(row.DistId) || targetDistId;
    try {
      records.push(transformDepletion(row, distId, fileDate));
    } catch (e) {
      transformErrors.push({ rowIndex: idx, error: e.message });
    }
  });

  // 3. BATCH — Depletion__c (unmanaged VIP_External_ID__c)
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
            NS + 'Depletion__c/VIP_External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'dep_' + idx,
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
      depletions: records.length,
      invalid: invalid.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      batches: batches.length,
      timestamp: new Date().toISOString()
    }
  };
};
