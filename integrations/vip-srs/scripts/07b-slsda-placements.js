/**
 * VIP SRS Script 07b: SLSDA -> Placement__c
 *
 * Aggregates SLSDA invoice lines into Account×Item placement records.
 * Each unique DistId+AcctNbr+SuppItem combo produces one Placement upsert
 * with the latest invoice data and earliest/latest sold dates.
 *
 * Pre-filter: Same as 07 (drop SRS99, XXXXXX, zero qty+price).
 *
 * Source: SLSDA file (25 columns)
 * Target: Placement__c (VIP_External_ID__c = PLC:{DistId}:{AcctNbr}:{SuppItem})
 *
 * Note: Account__c and Item__c are master-detail (create-only). On first upsert
 * they are set via relationship syntax; on subsequent upserts they are omitted
 * by the Composite API (PATCH ignores non-updateable fields).
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.6
 */

// =============================================================================
// INLINE SHARED
// =============================================================================

var PREFIX = { ITEM: 'ITM', ACCOUNT: 'ACT', PLACEMENT: 'PLC' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };
var NS = SF_CONFIG.namespacePrefix + '__';

function placementKey(distId, acctNbr, suppItem) {
  return PREFIX.PLACEMENT + ':' + distId + ':' + acctNbr + ':' + suppItem;
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
// AGGREGATE
// =============================================================================

/**
 * Groups valid rows by Account×Item and computes aggregate fields:
 *  - earliestDate: min InvoiceDate → First_Sold_Date__c
 *  - latestDate: max InvoiceDate → Last_Sold_Date__c, Last_Purchase_Date__c
 *  - latestPrice: NetPrice from the row with the latest InvoiceDate
 *  - latestQty: Qty from the row with the latest InvoiceDate
 */
function aggregatePlacements(rows, distId, fileDate) {
  var map = {}; // key → { earliestDate, latestDate, latestPrice, latestQty, distId, acctNbr, suppItem, fileDate }

  rows.forEach(function(row) {
    var rowDistId = clean(row.DistId) || distId;
    var acctNbr = clean(row.AcctNbr);
    var suppItem = clean(row.SuppItem);
    var key = placementKey(rowDistId, acctNbr, suppItem);
    var invoiceDate = clean(row.InvoiceDate);
    var qty = toNumber(row.Qty);
    var netPrice = toNumber(row.NetPrice);

    if (!map[key]) {
      map[key] = {
        distId: rowDistId,
        acctNbr: acctNbr,
        suppItem: suppItem,
        earliestDate: invoiceDate,
        latestDate: invoiceDate,
        latestPrice: netPrice,
        latestQty: qty,
        fileDate: fileDate
      };
    } else {
      var entry = map[key];
      if (invoiceDate < entry.earliestDate) {
        entry.earliestDate = invoiceDate;
      }
      if (invoiceDate > entry.latestDate) {
        entry.latestDate = invoiceDate;
        entry.latestPrice = netPrice;
        entry.latestQty = qty;
      }
    }
  });

  return map;
}

// =============================================================================
// TRANSFORM
// =============================================================================

function transformPlacement(entry) {
  var record = {};

  record.VIP_External_ID__c = placementKey(entry.distId, entry.acctNbr, entry.suppItem);

  // Master-detail lookups (create-only — Composite API ignores on update)
  record[NS + 'Account__r'] = { ohfy__External_ID__c: accountKey(entry.distId, entry.acctNbr) };

  var itemRef = {};
  itemRef[NS + 'VIP_External_ID__c'] = itemKey(entry.suppItem);
  record[NS + 'Item__r'] = itemRef;

  // Dates
  record[NS + 'First_Sold_Date__c'] = toSfDate(entry.earliestDate);
  record[NS + 'Last_Sold_Date__c'] = toSfDate(entry.latestDate);
  record[NS + 'Last_Purchase_Date__c'] = toSfDate(entry.latestDate);

  // Latest transaction values
  record[NS + 'Last_Invoice_Price__c'] = entry.latestPrice;
  record[NS + 'Last_Purchase_Quantity__c'] = entry.latestQty;

  // Active — has sales activity
  record[NS + 'Is_Active__c'] = true;

  // Stale cleanup date
  if (entry.fileDate) record.VIP_File_Date__c = entry.fileDate;

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];
  var targetDistId = input.targetDistId || input.distributorId;
  var fileDate = input.fileDate || '';

  // 1. VALIDATE & FILTER (same rules as 07-depletions)
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

    var acctNbr = clean(row.AcctNbr);
    if (acctNbr === 'SRS99') {
      skipped.push({ rowIndex: idx, reason: 'SRS99 placeholder' });
      return;
    }

    var suppItem = clean(row.SuppItem);
    if (suppItem === 'XXXXXX') {
      skipped.push({ rowIndex: idx, reason: 'XXXXXX placeholder' });
      return;
    }

    var qty = toNumber(row.Qty);
    var netPrice = toNumber(row.NetPrice);
    if (qty === 0 && netPrice === 0) {
      skipped.push({ rowIndex: idx, reason: 'Zero qty and price' });
      return;
    }

    valid.push(row);
  });

  // 2. AGGREGATE — group by Account×Item
  var placementMap = aggregatePlacements(valid, targetDistId, fileDate);
  var keys = Object.keys(placementMap);

  // 3. TRANSFORM — one Placement per Account×Item
  var records = [];
  var transformErrors = [];

  keys.forEach(function(key) {
    try {
      records.push(transformPlacement(placementMap[key]));
    } catch (e) {
      transformErrors.push({ key: key, error: e.message });
    }
  });

  // 4. BATCH — Placement__c (unmanaged VIP_External_ID__c)
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
            NS + 'Placement__c/VIP_External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'plc_' + idx,
          body: body
        };
      })
    };
  });

  // 5. OUTPUT
  return {
    batches: batches,
    batchCount: batches.length,
    records: records,
    recordCount: records.length,
    errors: invalid.concat(transformErrors.map(function(e) {
      return { key: e.key, reason: 'Transform error: ' + e.error };
    })),
    errorCount: invalid.length + transformErrors.length,
    skippedCount: skipped.length,
    summary: {
      total: rows.length,
      validRows: valid.length,
      uniquePlacements: records.length,
      invalid: invalid.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      batches: batches.length,
      timestamp: new Date().toISOString()
    }
  };
};
