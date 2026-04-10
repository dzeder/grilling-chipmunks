/**
 * VIP SRS Script 01: SRSCHAIN → Account (Chain Banners)
 *
 * Transforms VIP chain reference data into Salesforce Account records
 * with record type "Chain Banner".
 *
 * Source: SRSCHAIN file (3 columns: RecordType, Chain, Desc)
 * Target: Account (ohfy__External_ID__c = CHN:{Chain})
 * Rows: ~6,633 per file
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.1
 */

// =============================================================================
// INLINE SHARED (for Tray Script connector — no require())
// =============================================================================

/* --- constants (partial) --- */
var PREFIX = { CHAIN: 'CHN' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25 };

/* --- external-ids --- */
function chainKey(chain) {
  return PREFIX.CHAIN + ':' + chain;
}

/* --- transforms --- */
function toTitleCase(value) {
  if (!value) return '';
  return String(value).toLowerCase().replace(/(?:^|\s)\S/g, function(c) { return c.toUpperCase(); });
}

function clean(value) {
  if (value === undefined || value === null) return '';
  return String(value).trim();
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
// CONFIG
// =============================================================================

var CONFIG = {
  serviceName: 'VIP SRS — SRSCHAIN Chains',
  sobject: 'Account',
  externalIdField: 'ohfy__External_ID__c'
};

// =============================================================================
// VALIDATION RULES
// =============================================================================

var REQUIRED_FIELDS = ['Chain', 'Desc'];

// =============================================================================
// TRANSFORM
// =============================================================================

function transformChain(row) {
  var chain = clean(row.Chain);
  var desc = clean(row.Desc);

  return {
    ohfy__External_ID__c: chainKey(chain),
    Name: toTitleCase(desc),
    ohfy__Legal_Name__c: toTitleCase(desc),
    ohfy__Is_Chain_Banner__c: true,
    ohfy__Retail_Type__c: 'Chain',
    ohfy__Is_Active__c: true,
    Type: 'Chain Banner',
    RecordTypeId: '012am0000050BVYAA2', // Chain_Banner — NOT yet available to integration user
    AccountSource: 'VIP SRS'
  };
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];

  // 1. VALIDATE — filter and classify
  var valid = [];
  var invalid = [];
  var skipped = [];

  rows.forEach(function(row, idx) {
    // Skip non-DETAIL rows
    var recordType = clean(row.RecordType);
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ rowIndex: idx, reason: 'Non-DETAIL: ' + recordType });
      return;
    }

    // Check required fields
    var chain = clean(row.Chain);
    var desc = clean(row.Desc);
    if (!chain || !desc) {
      invalid.push({ rowIndex: idx, reason: 'Missing Chain or Desc', row: row });
      return;
    }

    valid.push(row);
  });

  // 2. TRANSFORM
  var records = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    try {
      records.push(transformChain(row));
    } catch (e) {
      transformErrors.push({ rowIndex: idx, error: e.message });
    }
  });

  // 3. BATCH — build Composite API requests
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
          referenceId: 'chain_' + idx,
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
