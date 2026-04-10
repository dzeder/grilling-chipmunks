/**
 * VIP SRS Script 03: DISTDA → Location__c (Distributor Warehouses)
 *
 * Transforms VIP distributor master data into Salesforce Location records.
 * Filters to only the target distributor ID (typically 1 row).
 *
 * Source: DISTDA file (27 columns)
 * Target: Location__c (Location_Code__c = LOC:{DistId})
 * Rows: ~13 total, ~1 after filtering
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.3
 */

// =============================================================================
// INLINE SHARED (for Tray Script connector — no require())
// =============================================================================

var PREFIX = { LOCATION: 'LOC' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };

function locationKey(distId) { return PREFIX.LOCATION + ':' + distId; }
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
  serviceName: 'VIP SRS — DISTDA Locations',
  sobject: NS + 'Location__c',
  externalIdField: 'VIP_External_ID__c'
};

// =============================================================================
// TRANSFORM
// =============================================================================

function transformLocation(row) {
  var distId = clean(row['Distributor ID']);
  var record = {};

  // External ID for upsert
  record.VIP_External_ID__c = locationKey(distId);

  // Also populate Location_Code__c
  record[NS + 'Location_Code__c'] = locationKey(distId);

  // Direct mappings
  record.Name = clean(row['Distributor Name']);
  record[NS + 'Location_Street__c'] = clean(row.Street);
  record[NS + 'Location_City__c'] = clean(row.City);
  record[NS + 'Location_State__c'] = clean(row.State);
  record[NS + 'Location_Postal_Code__c'] = clean(row.Zip);

  // Hardcoded fields
  record[NS + 'Location_Type__c'] = 'Warehouse';
  record[NS + 'Is_Active__c'] = true;
  record[NS + 'Is_Sellable__c'] = true;
  record[NS + 'Is_Finished_Good__c'] = true;

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];
  var targetDistId = input.targetDistId || input.distributorId;

  // 1. VALIDATE & FILTER
  var valid = [];
  var invalid = [];
  var skipped = [];

  rows.forEach(function(row, idx) {
    var recordType = clean(row.RecordId);
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ rowIndex: idx, reason: 'Non-DETAIL' });
      return;
    }

    var distId = clean(row['Distributor ID']);
    if (!distId) {
      invalid.push({ rowIndex: idx, reason: 'Missing Distributor ID' });
      return;
    }

    var distName = clean(row['Distributor Name']);
    if (!distName) {
      invalid.push({ rowIndex: idx, reason: 'Missing Distributor Name' });
      return;
    }

    // Filter to target distributor if specified
    if (targetDistId && distId !== targetDistId) {
      skipped.push({ rowIndex: idx, reason: 'Wrong distributor: ' + distId });
      return;
    }

    valid.push(row);
  });

  // 2. TRANSFORM
  var records = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    try {
      records.push(transformLocation(row));
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
          if (key !== CONFIG.externalIdField) body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            CONFIG.sobject + '/' + CONFIG.externalIdField + '/' + sanitizeForUrl(extId),
          referenceId: 'location_' + idx,
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
