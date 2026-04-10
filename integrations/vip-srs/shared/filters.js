/**
 * VIP SRS Integration — Row Filtering
 *
 * Functions to filter VIP CSV rows: distributor ID matching,
 * control record detection, blank required field checks.
 */

// Requires: CONTROL_RECORDS from constants.js (inlined in Tray scripts)

// =============================================================================
// DISTRIBUTOR ID FILTER
// =============================================================================

/**
 * Filter rows to only those matching the target distributor ID.
 * @param {Array} rows - CSV rows
 * @param {string} targetDistId - Target distributor ID to keep
 * @param {string} distIdField - Field name containing dist ID (default: 'DistId')
 * @returns {{ matched: Array, skipped: number }}
 */
function filterByDistributor(rows, targetDistId, distIdField) {
  var field = distIdField || 'DistId';
  var matched = [];
  var skipped = 0;

  rows.forEach(function(row) {
    if (String(row[field] || '').trim() === targetDistId) {
      matched.push(row);
    } else {
      skipped++;
    }
  });

  return { matched: matched, skipped: skipped };
}

// =============================================================================
// CONTROL RECORD FILTERS
// =============================================================================

/**
 * Check if a row is a control/placeholder record that should be skipped.
 * @param {Object} row - CSV row
 * @returns {boolean} true if the row should be skipped
 */
function isControlRecord(row) {
  var acctNbr = String(row.AcctNbr || row.Account || '').trim();
  var suppItem = String(row.SuppItem || row.SupplierItem || '').trim();

  if (acctNbr === CONTROL_RECORDS.accountPlaceholder) return true;
  if (suppItem === CONTROL_RECORDS.itemPlaceholder) return true;

  return false;
}

/**
 * Check if a sales row is a zero-value record that should be skipped.
 * @param {Object} row - SLSDA row
 * @returns {boolean} true if qty=0 AND netPrice=0
 */
function isZeroValueRecord(row) {
  var qty = Number(row.Qty || 0);
  var netPrice = Number(row.NetPrice || 0);
  return qty === 0 && netPrice === 0;
}

/**
 * Filter DETAIL rows only (skip header/trailer rows).
 * @param {Array} rows - CSV rows
 * @param {string} recordTypeField - Field name for record type (default: 'RecordType')
 * @returns {Array} rows where RecordType === 'DETAIL'
 */
function filterDetailRows(rows, recordTypeField) {
  var field = recordTypeField || 'RecordType';
  return rows.filter(function(row) {
    return String(row[field] || '').trim() === 'DETAIL';
  });
}

// =============================================================================
// REQUIRED FIELD CHECKS
// =============================================================================

/**
 * Check if a row has all required fields populated.
 * @param {Object} row - CSV row
 * @param {Array<string>} requiredFields - Field names that must be non-empty
 * @returns {{ valid: boolean, missingFields: Array<string> }}
 */
function checkRequiredFields(row, requiredFields) {
  var missing = [];

  requiredFields.forEach(function(field) {
    var value = row[field];
    if (value === undefined || value === null || String(value).trim() === '') {
      missing.push(field);
    }
  });

  return { valid: missing.length === 0, missingFields: missing };
}

/**
 * Classify rows into valid, invalid, orphaned, and skipped buckets.
 * @param {Array} rows - CSV rows
 * @param {Object} options
 * @param {string} options.targetDistId - Distributor ID to filter by (optional)
 * @param {string} options.distIdField - Field name for dist ID
 * @param {Array<string>} options.requiredFields - Required field names
 * @param {boolean} options.checkControls - Whether to check for control records
 * @param {Object} options.lookupSets - Maps of field→Set for orphan detection
 * @returns {{ valid: Array, invalid: Array, orphaned: Array, skipped: Array }}
 */
function classifyRows(rows, options) {
  var valid = [];
  var invalid = [];
  var orphaned = [];
  var skipped = [];

  rows.forEach(function(row) {
    // Skip non-DETAIL rows
    var recordType = String(row.RecordType || row.RecordId || row.RcdType || '').trim();
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ row: row, reason: 'Non-DETAIL record type: ' + recordType });
      return;
    }

    // Skip wrong distributor
    if (options.targetDistId && options.distIdField) {
      var distId = String(row[options.distIdField] || '').trim();
      if (distId !== options.targetDistId) {
        skipped.push({ row: row, reason: 'Wrong distributor: ' + distId });
        return;
      }
    }

    // Skip control records
    if (options.checkControls && isControlRecord(row)) {
      skipped.push({ row: row, reason: 'Control record' });
      return;
    }

    // Skip zero-value records
    if (options.checkControls && isZeroValueRecord(row)) {
      skipped.push({ row: row, reason: 'Zero value record' });
      return;
    }

    // Check required fields
    if (options.requiredFields) {
      var check = checkRequiredFields(row, options.requiredFields);
      if (!check.valid) {
        invalid.push({ row: row, reason: 'Missing fields: ' + check.missingFields.join(', ') });
        return;
      }
    }

    // Check lookups for orphans
    if (options.lookupSets) {
      var isOrphan = false;
      var orphanReason = [];

      Object.keys(options.lookupSets).forEach(function(field) {
        var value = String(row[field] || '').trim();
        if (value && !options.lookupSets[field].has(value)) {
          isOrphan = true;
          orphanReason.push(field + '=' + value + ' not found');
        }
      });

      if (isOrphan) {
        orphaned.push({ row: row, reason: orphanReason.join('; ') });
        return;
      }
    }

    valid.push(row);
  });

  return { valid: valid, invalid: invalid, orphaned: orphaned, skipped: skipped };
}

// =============================================================================
// EXPORTS (for Node.js testing; inlined in Tray scripts)
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    filterByDistributor: filterByDistributor,
    isControlRecord: isControlRecord,
    isZeroValueRecord: isZeroValueRecord,
    filterDetailRows: filterDetailRows,
    checkRequiredFields: checkRequiredFields,
    classifyRows: classifyRows
  };
}
