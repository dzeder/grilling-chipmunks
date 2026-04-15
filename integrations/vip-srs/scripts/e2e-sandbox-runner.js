#!/usr/bin/env node
/**
 * VIP SRS E2E Sandbox Runner
 *
 * Runs all transform scripts with fixture data and POSTs the resulting
 * Composite API batches to a real Salesforce sandbox.
 *
 * Usage:
 *   node e2e-sandbox-runner.js                          # run all phases
 *   node e2e-sandbox-runner.js --phase 1                # run phase 1 only
 *   node e2e-sandbox-runner.js --target-org my-sandbox  # custom org
 *   node e2e-sandbox-runner.js --dist-id FL01           # filter by distributor
 *   node e2e-sandbox-runner.js --dry-run                # show batches without sending
 *   node e2e-sandbox-runner.js --output-json out.json   # write structured JSON report
 *   node e2e-sandbox-runner.js --config config/gulf.json # use a different customer config
 */

var fs = require('fs');
var path = require('path');
var execSync = require('child_process').execSync;
var loadConfig = require('./config-loader');

// =============================================================================
// CONFIG
// =============================================================================

// Load customer config (--config flag or default shipyard.json), then apply CLI overrides
var _cfg = loadConfig(process.argv.slice(2));
var TARGET_ORG = _cfg.targetOrg;
var DIST_ID = _cfg.distId;
var API_VERSION = _cfg.apiVersion;
var DRY_RUN = false;
var PHASE_FILTER = null; // null = all phases
var FILE_DATE = ''; // YYYY-MM-DD — set via --file-date, defaults to today (date of run)
var OUTPUT_JSON = ''; // path to write structured JSON report
var DATA_DIR = ''; // path to real VIP data files (overrides FIXTURES_DIR)
var SKIP_CONTACTS = false; // skip all Contact DML (workaround for AccountTriggerMethods)
var MAX_RETRIES = 3; // retry attempts for transient API failures

// CLI args override config values
var args = process.argv.slice(2);
for (var i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--target-org': TARGET_ORG = args[++i]; break;
    case '--dist-id': DIST_ID = args[++i]; break;
    case '--dry-run': DRY_RUN = true; break;
    case '--phase': PHASE_FILTER = parseInt(args[++i], 10); break;
    case '--file-date': FILE_DATE = args[++i]; break;
    case '--output-json': OUTPUT_JSON = args[++i]; break;
    case '--data-dir': DATA_DIR = args[++i]; break;
    case '--skip-contacts': SKIP_CONTACTS = true; break;
    case '--config': i++; break; // already consumed by config-loader
    case '--help': case '-h':
      console.log('Usage: node e2e-sandbox-runner.js [--config FILE] [--target-org ORG] [--dist-id ID] [--phase N] [--file-date YYYY-MM-DD] [--output-json FILE] [--data-dir DIR] [--dry-run]');
      process.exit(0);
  }
}

// =============================================================================
// PATHS
// =============================================================================

var SCRIPTS_DIR = path.join(__dirname);
var FIXTURES_DIR = path.join(__dirname, '..', 'tests', 'fixtures');

// When --data-dir is set, resolve real VIP filenames instead of test fixtures.
// VIP files on SFTP follow {TYPE}.N{MMDDYYYY}.gz naming; after download they're {TYPE}.csv
// or may retain the original name sans .gz. We check multiple patterns.
function resolveDataFile(fixtureFile) {
  if (!DATA_DIR) return path.join(FIXTURES_DIR, fixtureFile);

  var dataDir = path.isAbsolute(DATA_DIR)
    ? DATA_DIR
    : path.join(__dirname, '..', DATA_DIR);

  // Map fixture filenames to VIP file type prefixes
  var FIXTURE_TO_TYPE = {
    'srschain-sample.csv': 'SRSCHAIN',
    'itm2da-sample.csv': 'ITM2DA',
    'distda-sample.csv': 'DISTDA',
    'itmda-sample.csv': 'ITMDA',
    'outda-sample.csv': 'OUTDA',
    'invda-sample.csv': 'INVDA',
    'slsda-25.csv': 'SLSDA',
    'slsda-sample.csv': 'SLSDA',
    'ctlda-sample.csv': 'CTLDA'
  };

  var vipType = FIXTURE_TO_TYPE[fixtureFile];
  if (!vipType) return path.join(dataDir, fixtureFile); // unknown fixture, try as-is

  // Try multiple filename patterns in order of likelihood
  var candidates = [
    vipType + '.csv',                           // TYPE.csv (standard after download)
    vipType + 'DA.csv',                         // TYPEDA.csv (some have DA suffix already)
    fixtureFile                                 // original fixture name as fallback
  ];

  // Also check for files matching TYPE*.csv (covers TYPE.N04082026.csv etc.)
  try {
    var dirFiles = fs.readdirSync(dataDir);
    dirFiles.forEach(function(f) {
      if (f.toUpperCase().indexOf(vipType) === 0 && f.toLowerCase().endsWith('.csv')) {
        if (candidates.indexOf(f) === -1) candidates.unshift(f); // prioritize actual matches
      }
    });
  } catch (_) { /* directory may not exist yet */ }

  for (var ci = 0; ci < candidates.length; ci++) {
    var candidatePath = path.join(dataDir, candidates[ci]);
    if (fs.existsSync(candidatePath)) return candidatePath;
  }

  // Nothing found — return the standard name so the "not found" error is clear
  return path.join(dataDir, vipType + '.csv');
}

// =============================================================================
// CSV PARSER (same as test-runner.js)
// =============================================================================

function parseCSV(content) {
  content = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  var lines = content.split('\n').filter(function(l) { return l.trim(); });
  if (lines.length < 2) return [];
  var headers = parseCSVLine(lines[0]);
  var rows = [];
  for (var i = 1; i < lines.length; i++) {
    var values = parseCSVLine(lines[i]);
    var row = {};
    headers.forEach(function(h, idx) {
      row[h] = values[idx] !== undefined ? values[idx] : '';
    });
    rows.push(row);
  }
  return rows;
}

function parseCSVLine(line) {
  var values = [];
  var current = '';
  var inQuotes = false;
  for (var i = 0; i < line.length; i++) {
    var ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
      else { inQuotes = !inQuotes; }
    } else if (ch === ',' && !inQuotes) {
      values.push(current); current = '';
    } else { current += ch; }
  }
  values.push(current);
  return values;
}

// =============================================================================
// SF API HELPERS
// =============================================================================

// Retry-eligible: timeouts, 503 (throttling), ECONNRESET, socket hang up
function isRetryable(error) {
  if (!error) return false;
  var msg = typeof error === 'string' ? error : (error.message || JSON.stringify(error));
  return /timeout|ETIMEDOUT|ECONNRESET|socket hang up|503|SERVICE_UNAVAILABLE/i.test(msg);
}

function sleepMs(ms) {
  execSync('sleep ' + (ms / 1000), { timeout: ms + 1000 });
}

function sfApiPost(endpoint, body) {
  for (var attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    var tmpFile = '/tmp/vip-e2e-body-' + Date.now() + '.json';
    fs.writeFileSync(tmpFile, JSON.stringify(body));
    try {
      var result = execSync(
        'sf api request rest "' + endpoint + '" --method POST --body @' + tmpFile +
        ' --target-org ' + TARGET_ORG + ' 2>/dev/null',
        { encoding: 'utf8', timeout: 60000 }
      );
      try { fs.unlinkSync(tmpFile); } catch (_) {}
      return JSON.parse(result);
    } catch (e) {
      try { fs.unlinkSync(tmpFile); } catch (_) {}
      var output = e.stdout ? e.stdout.toString() : '';
      // If we got a parseable response, return it (not a transient failure)
      try { var parsed = JSON.parse(output); return parsed; } catch (_) {}
      // Retry on transient errors
      if (isRetryable(e) && attempt < MAX_RETRIES) {
        var delay = Math.pow(2, attempt - 1) * 1000; // 1s, 2s, 4s
        console.log('    RETRY ' + attempt + '/' + MAX_RETRIES + ' after ' + delay + 'ms (' + (e.message || '').substring(0, 80) + ')');
        sleepMs(delay);
        continue;
      }
      return { error: e.message, stdout: output };
    }
  }
}

function sfApiPatch(endpoint, body) {
  for (var attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    var tmpFile = '/tmp/vip-e2e-body-' + Date.now() + '.json';
    fs.writeFileSync(tmpFile, JSON.stringify(body));
    try {
      var result = execSync(
        'sf api request rest "' + endpoint + '" --method PATCH --body @' + tmpFile +
        ' --target-org ' + TARGET_ORG + ' 2>/dev/null',
        { encoding: 'utf8', timeout: 60000 }
      );
      try { fs.unlinkSync(tmpFile); } catch (_) {}
      // PATCH upsert returns 204 (no body) on success, 201 with body on create
      if (!result || !result.trim()) return { success: true, httpStatusCode: 204 };
      return JSON.parse(result);
    } catch (e) {
      try { fs.unlinkSync(tmpFile); } catch (_) {}
      var output = e.stdout ? e.stdout.toString() : '';
      if (!output || !output.trim()) return { success: true, httpStatusCode: 204 };
      try { var parsed = JSON.parse(output); return parsed; } catch (_) {}
      if (isRetryable(e) && attempt < MAX_RETRIES) {
        var delay = Math.pow(2, attempt - 1) * 1000;
        console.log('    RETRY ' + attempt + '/' + MAX_RETRIES + ' after ' + delay + 'ms (' + (e.message || '').substring(0, 80) + ')');
        sleepMs(delay);
        continue;
      }
      return { error: e.message };
    }
  }
}

// Known error patterns for categorization
var KNOWN_ERRORS = {
  ACCOUNT_TRIGGER_METHODS: /AccountTriggerMethods/,
  FIELD_FILTER_VALIDATION: /FIELD_FILTER_VALIDATION_EXCEPTION/,
  DUPLICATE_BLOCKED: /Duplicate Record Blocked/i,
  CUSTOM_VALIDATION: /FIELD_CUSTOM_VALIDATION_EXCEPTION/
};

// Global error tracker for JSON output
var errorDetails = [];

function categorizeError(bodyStr) {
  for (var key in KNOWN_ERRORS) {
    if (KNOWN_ERRORS[key].test(bodyStr)) return key;
  }
  return 'OTHER';
}

function sendCompositeBatch(batch, label) {
  var body = { compositeRequest: batch.compositeRequest };
  var endpoint = '/services/data/' + API_VERSION + '/composite';
  console.log('    Sending batch: ' + batch.compositeRequest.length + ' subrequests...');

  if (DRY_RUN) {
    console.log('    [DRY RUN] Would send ' + batch.compositeRequest.length + ' subrequests');
    batch.compositeRequest.slice(0, 2).forEach(function(req) {
      console.log('      ' + req.method + ' ' + req.url);
    });
    if (batch.compositeRequest.length > 2) {
      console.log('      ... and ' + (batch.compositeRequest.length - 2) + ' more');
    }
    return { compositeResponse: batch.compositeRequest.map(function() { return { httpStatusCode: 200 }; }) };
  }

  var response = sfApiPost(endpoint, body);

  if (response.compositeResponse) {
    var successes = 0;
    var failures = 0;
    response.compositeResponse.forEach(function(r) {
      if (r.httpStatusCode >= 200 && r.httpStatusCode < 300) successes++;
      else failures++;
    });
    console.log('    Result: ' + successes + ' succeeded, ' + failures + ' failed');
    if (failures > 0) {
      response.compositeResponse.forEach(function(r, idx) {
        if (r.httpStatusCode >= 300) {
          var bodyStr = JSON.stringify(r.body);
          var category = categorizeError(bodyStr);
          var prefix = category === 'OTHER' ? 'ERROR' : category;
          console.log('    ' + prefix + ' [' + idx + '] ' + r.httpStatusCode + ': ' + bodyStr.substring(0, 200));
          errorDetails.push({
            step: label,
            index: idx,
            httpStatus: r.httpStatusCode,
            category: category,
            referenceId: batch.compositeRequest[idx] ? batch.compositeRequest[idx].referenceId : null,
            message: bodyStr.substring(0, 500)
          });
        }
      });
    }
    return response;
  } else {
    console.log('    ERROR: Unexpected response: ' + JSON.stringify(response).substring(0, 200));
    return response;
  }
}

function sendBatches(batches, label) {
  var totalSuccess = 0;
  var totalFail = 0;

  for (var i = 0; i < batches.length; i++) {
    console.log('  ' + label + ' batch ' + (i + 1) + '/' + batches.length);
    var response = sendCompositeBatch(batches[i], label);
    if (response.compositeResponse) {
      response.compositeResponse.forEach(function(r) {
        if (r.httpStatusCode >= 200 && r.httpStatusCode < 300) totalSuccess++;
        else totalFail++;
      });
    }
  }

  return { success: totalSuccess, fail: totalFail };
}

/**
 * SObject Collections upsert — 200 records per batch (8x faster than Composite).
 * PATCH /composite/sobjects/{SObject}/{ExternalIdField}
 * Body: { allOrNone: false, records: [{ attributes: {type}, ...fields }] }
 * Response: [{id, success, errors, created}, ...]
 */
function sendCollectionsUpsert(records, sobjectName, externalIdField, label) {
  if (!records || records.length === 0) {
    console.log('  ' + label + ': 0 records, skipping');
    return { success: 0, fail: 0 };
  }

  var BATCH_SIZE = 200;
  var totalSuccess = 0;
  var totalFail = 0;

  var chunks = [];
  for (var i = 0; i < records.length; i += BATCH_SIZE) {
    chunks.push(records.slice(i, i + BATCH_SIZE));
  }

  for (var ci = 0; ci < chunks.length; ci++) {
    var chunk = chunks[ci];
    console.log('  ' + label + ' batch ' + (ci + 1) + '/' + chunks.length + ' (' + chunk.length + ' records)');

    if (DRY_RUN) {
      console.log('    [DRY RUN] Would upsert ' + chunk.length + ' ' + sobjectName + ' records');
      totalSuccess += chunk.length;
      continue;
    }

    var payload = {
      allOrNone: false,
      records: chunk.map(function(rec) {
        var r = { attributes: { type: sobjectName } };
        Object.keys(rec).forEach(function(key) {
          if (key[0] !== '_') r[key] = rec[key];
        });
        return r;
      })
    };

    var endpoint = '/services/data/' + API_VERSION + '/composite/sobjects/' +
      sobjectName + '/' + externalIdField;
    var response = sfApiPatch(endpoint, payload);

    if (Array.isArray(response)) {
      var batchOk = 0, batchFail = 0;
      response.forEach(function(r, idx) {
        if (r.success) {
          batchOk++;
        } else {
          batchFail++;
          var errMsg = r.errors ? JSON.stringify(r.errors) : 'Unknown error';
          var category = categorizeError(errMsg);
          console.log('    ' + category + ' [' + idx + ']: ' + errMsg.substring(0, 200));
          errorDetails.push({
            step: label,
            index: (ci * BATCH_SIZE) + idx,
            httpStatus: 400,
            category: category,
            referenceId: null,
            message: errMsg.substring(0, 500)
          });
        }
      });
      totalSuccess += batchOk;
      totalFail += batchFail;
      console.log('    Result: ' + batchOk + ' ok, ' + batchFail + ' fail');
    } else if (response && (response.success || (response.httpStatusCode && response.httpStatusCode < 300))) {
      totalSuccess += chunk.length;
      console.log('    Result: ' + chunk.length + ' ok');
    } else {
      totalFail += chunk.length;
      console.log('    ERROR: ' + JSON.stringify(response).substring(0, 200));
    }
  }

  return { success: totalSuccess, fail: totalFail };
}

function sfQuery(soql) {
  try {
    var result = execSync(
      'sf data query --target-org ' + TARGET_ORG + ' --query "' + soql + '" --result-format json 2>/dev/null',
      { encoding: 'utf8', timeout: 30000 }
    );
    var parsed = JSON.parse(result);
    return parsed.result ? parsed.result.records : [];
  } catch (e) {
    return [];
  }
}

function getRecordTypeId(sobject, developerName) {
  var records = sfQuery("SELECT Id FROM RecordType WHERE SObjectType='" + sobject + "' AND DeveloperName='" + developerName + "' LIMIT 1");
  return records.length > 0 ? records[0].Id : null;
}

function createRecordByName(sobject, name) {
  if (DRY_RUN) {
    console.log('    [DRY RUN] Would create ' + sobject + ': ' + name);
    return true;
  }

  var endpoint = '/services/data/' + API_VERSION + '/sobjects/' + sobject;
  var response = sfApiPost(endpoint, { Name: name });

  if (response.success || response.id) {
    console.log('    Created ' + sobject + ': ' + name + ' → ' + (response.id || 'ok'));
    return true;
  } else {
    // Might already exist — that's fine
    var errMsg = JSON.stringify(response);
    if (errMsg.indexOf('DUPLICATE') > -1 || errMsg.indexOf('already exists') > -1) {
      console.log('    Already exists: ' + sobject + ': ' + name);
      return true;
    }
    console.log('    ERROR creating ' + sobject + ' ' + name + ': ' + errMsg.substring(0, 200));
    return false;
  }
}

// =============================================================================
// PIPELINE DEFINITION
// =============================================================================

var PIPELINE = [
  // Phase 1: Reference Data
  {
    phase: 1,
    name: '01-srschain → Account (Chain Banners)',
    script: '01-srschain-chains.js',
    fixture: 'srschain-sample.csv',
    run: function(result) {
      return sendCollectionsUpsert(result.records, 'Account', 'ohfy__External_ID__c', 'Chain Banners');
    }
  },
  {
    phase: 1,
    name: '02-itm2da → Item_Line + Item_Type + Item',
    script: '02-itm2da-items.js',
    fixture: 'itm2da-sample.csv',
    run: function(result) {
      // Upsert Item_Lines — Composite (small set, batch builder adds Supplier__r)
      if (result.itemLineBatches && result.itemLineBatches.length > 0) {
        sendBatches(result.itemLineBatches, 'Item Lines');
      }
      // Upsert Item_Types — Composite (small set, restricted picklist field selection)
      if (result.itemTypeBatches && result.itemTypeBatches.length > 0) {
        sendBatches(result.itemTypeBatches, 'Item Types');
      }
      // Upsert Items — Collections (200/batch)
      return sendCollectionsUpsert(result.records, 'ohfy__Item__c', 'ohfy__VIP_External_ID__c', 'Items');
    }
  },
  {
    phase: 1,
    name: '03-distda → Account (Distributor) + Contact + Location',
    script: '03-distda-locations.js',
    fixture: 'distda-sample.csv',
    run: function(result) {
      // Accounts first (parent) — Collections (200/batch)
      var acctResult = sendCollectionsUpsert(result.accountRecords || [], 'Account', 'ohfy__External_ID__c', 'Distributors (Accounts)');
      // Contacts second (child) — Composite (parent-linking in batch builder)
      var contResult = { success: 0, fail: 0 };
      if (!SKIP_CONTACTS && result.contactBatches && result.contactBatches.length > 0) {
        contResult = sendBatches(result.contactBatches, 'Distributor Contacts');
      } else if (SKIP_CONTACTS && result.contactRecords && result.contactRecords.length > 0) {
        console.log('    SKIP: ' + result.contactRecords.length + ' contacts (--skip-contacts)');
      }
      // Locations — Collections (200/batch)
      var locResult = sendCollectionsUpsert(result.locationRecords || [], 'ohfy__Location__c', 'VIP_External_ID__c', 'Locations');
      return {
        success: acctResult.success + contResult.success + locResult.success,
        fail: acctResult.fail + contResult.fail + locResult.fail
      };
    }
  },
  // Phase 2: Enrichment
  {
    phase: 2,
    name: '04-itmda → Item (enrichment)',
    script: '04-itmda-enrichment.js',
    fixture: 'itmda-sample.csv',
    run: function(result) {
      return sendCollectionsUpsert(result.records, 'ohfy__Item__c', 'ohfy__VIP_External_ID__c', 'Item Enrichment');
    }
  },
  {
    phase: 2,
    name: '05-outda → Account (Outlets) + Contact (Buyers)',
    script: '05-outda-accounts.js',
    fixture: 'outda-sample.csv',
    run: function(result) {
      // Accounts — Collections (200/batch)
      var acctResult = sendCollectionsUpsert(result.accountRecords, 'Account', 'ohfy__External_ID__c', 'Accounts (Outlets)');
      // Contacts — Composite (parent-linking in batch builder, skipped due to AccountTriggerMethods)
      var contResult = { success: 0, fail: 0 };
      if (!SKIP_CONTACTS) {
        contResult = sendBatches(result.contactBatches, 'Contacts (Buyers)');
      } else {
        console.log('    SKIP: ' + (result.contactRecords ? result.contactRecords.length : 0) + ' contacts (--skip-contacts)');
      }
      return {
        success: acctResult.success + contResult.success,
        fail: acctResult.fail + contResult.fail
      };
    }
  },
  // Phase 3: Inventory
  {
    phase: 3,
    name: '06-invda → Inventory + History + Adjustments',
    script: '06-invda-inventory.js',
    fixture: 'invda-sample.csv',
    run: function(result) {
      // Inventory — Collections (200/batch)
      var invResult = sendCollectionsUpsert(result.inventoryRecords || [], 'ohfy__Inventory__c', 'VIP_External_ID__c', 'Inventory');
      // History + Adjustments — Collections (200/batch)
      var histResult = sendCollectionsUpsert(result.historyRecords || [], 'ohfy__Inventory_History__c', 'VIP_External_ID__c', 'Inventory History');
      var adjResult = sendCollectionsUpsert(result.adjustmentRecords || [], 'ohfy__Inventory_Adjustment__c', 'VIP_External_ID__c', 'Inventory Adjustments');
      return {
        success: invResult.success + histResult.success + adjResult.success,
        fail: invResult.fail + histResult.fail + adjResult.fail
      };
    }
  },
  // Phase 4: Transactions
  {
    phase: 4,
    name: '07-slsda → Depletion',
    script: '07-slsda-depletions.js',
    fixture: 'slsda-25.csv',
    run: function(result) {
      return sendCollectionsUpsert(result.records, 'ohfy__Depletion__c', 'VIP_External_ID__c', 'Depletions');
    }
  },
  {
    phase: 4,
    name: '07b-slsda → Placement',
    script: '07b-slsda-placements.js',
    fixture: 'slsda-25.csv',
    run: function(result) {
      return sendCollectionsUpsert(result.records, 'ohfy__Placement__c', 'VIP_External_ID__c', 'Placements');
    }
  },
  {
    phase: 4,
    name: '08-ctlda → Allocation',
    script: '08-ctlda-allocations.js',
    fixture: 'ctlda-sample.csv',
    run: function(result) {
      return sendCollectionsUpsert(result.records, 'ohfy__Allocation__c', 'VIP_External_ID__c', 'Allocations');
    }
  }
];

// =============================================================================
// MAIN
// =============================================================================

console.log('============================================');
console.log('VIP SRS E2E Sandbox Runner');
console.log('============================================');
if (_cfg.customer) console.log('Customer:    ' + _cfg.customer + (_cfg.supplierCode ? ' (' + _cfg.supplierCode + ')' : ''));
if (_cfg._configFile) console.log('Config:      ' + path.basename(_cfg._configFile));
console.log('Target org:  ' + TARGET_ORG);
console.log('Dist ID:     ' + (DIST_ID || '(all distributors)'));
console.log('Data dir:    ' + (DATA_DIR || '(test fixtures)'));
console.log('File date:   ' + (FILE_DATE || '(today: ' + new Date().toISOString().substring(0, 10) + ')'));
console.log('Mode:        ' + (DRY_RUN ? 'DRY RUN' : 'LIVE'));
console.log('Phase:       ' + (PHASE_FILTER ? PHASE_FILTER : 'ALL'));
console.log('============================================');
console.log('');

// Pre-fetch record type IDs needed by scripts
var FINISHED_GOOD_RT_ID = getRecordTypeId('ohfy__Item__c', 'Finished_Good');
if (FINISHED_GOOD_RT_ID) {
  console.log('Finished Good RT: ' + FINISHED_GOOD_RT_ID);
} else {
  console.log('WARNING: Finished_Good RecordType not found on ohfy__Item__c');
}

var CUSTOMER_RT_ID = getRecordTypeId('Account', 'Customer');
if (CUSTOMER_RT_ID) {
  console.log('Customer RT: ' + CUSTOMER_RT_ID);
} else {
  console.log('WARNING: Customer RecordType not found on Account');
}
console.log('');

// =============================================================================
// PHASE 0: SUPPLIER ACCOUNT (from config)
// =============================================================================

var SUPPLIER_ID = null; // populated if config.supplier exists
if (_cfg.supplier && _cfg.supplier.name && (!PHASE_FILTER || PHASE_FILTER <= 1)) {
  console.log('=== Phase 0: Supplier Account ===');
  var supplierExtId = _cfg.supplier.externalId || ('SUP:' + (_cfg.supplierCode || 'UNKNOWN'));
  var supplierRT = _cfg.supplier.recordType || 'Supplier';
  var supplierType = _cfg.supplier.type || 'Supplier';

  // Resolve Supplier record type ID
  var supplierRtId = getRecordTypeId('Account', supplierRT);
  if (!supplierRtId) {
    console.log('  WARNING: RecordType "' + supplierRT + '" not found on Account. Skipping RT.');
  }

  // Upsert by external ID
  var supplierBody = {
    Name: _cfg.supplier.name,
    Type: supplierType,
    AccountSource: 'VIP SRS'
  };
  if (supplierRtId) supplierBody.RecordTypeId = supplierRtId;

  var supplierEndpoint = '/services/data/' + API_VERSION + '/sobjects/Account/ohfy__External_ID__c/' + supplierExtId;

  if (DRY_RUN) {
    console.log('  [DRY RUN] Would upsert Supplier: ' + _cfg.supplier.name + ' (' + supplierExtId + ')');
  } else {
    var supplierResp = sfApiPatch(supplierEndpoint, supplierBody);
    if (supplierResp.success || supplierResp.id || (supplierResp.httpStatusCode && supplierResp.httpStatusCode < 300)) {
      console.log('  Supplier upserted: ' + _cfg.supplier.name + ' (' + supplierExtId + ')');
      SUPPLIER_ID = supplierResp.id || null;
    } else {
      console.log('  ERROR upserting Supplier: ' + JSON.stringify(supplierResp).substring(0, 200));
    }
  }
  console.log('');
}

// Pre-query existing Inventory records to handle "Duplicate Record Blocked" validation rule.
// Maps VIP inventory key (IVT:{DistId}:{SuppItem}) → existing Salesforce record ID.
// NOTE: Runs lazily before Phase 3 (not at startup) because Phase 1 must stamp
// VIP_External_ID__c on Items first for the SOQL relationship filter to match.
var existingInventoryMap = {};
var _NS = 'ohfy__';
var _inventoryPreQueryDone = false;

function runInventoryPreQuery() {
  if (_inventoryPreQueryDone) return;
  _inventoryPreQueryDone = true;
  console.log('Pre-query: Checking for existing Inventory records...');
  var invRecords = sfQuery(
    "SELECT Id, " + _NS + "Item__r." + _NS + "VIP_External_ID__c, " +
    _NS + "Location__r.VIP_External_ID__c " +
    "FROM " + _NS + "Inventory__c " +
    "WHERE " + _NS + "Item__r." + _NS + "VIP_External_ID__c LIKE 'ITM:%'"
  );
  invRecords.forEach(function(r) {
    var itemRef = r[_NS + 'Item__r'];
    var locRef = r[_NS + 'Location__r'];
    var itemExtId = itemRef ? itemRef[_NS + 'VIP_External_ID__c'] : null;
    var locExtId = locRef ? locRef['VIP_External_ID__c'] : null;
    if (itemExtId && locExtId) {
      var distId = locExtId.replace('LOC:', '');
      var suppItem = itemExtId.replace('ITM:', '');
      var vipKey = 'IVT:' + distId + ':' + suppItem;
      existingInventoryMap[vipKey] = r.Id;
    }
  });
  var mapKeys = Object.keys(existingInventoryMap);
  console.log('  Found ' + mapKeys.length + ' existing Inventory records with VIP items');

  // Batch-stamp VIP_External_ID__c on all existing records that don't have it yet.
  // This ensures History/Adjustment rows can reference ANY existing Inventory by VIP key.
  if (mapKeys.length > 0) {
    console.log('  Stamping VIP_External_ID__c on existing Inventory records...');
    var stampBatches = [];
    for (var si = 0; si < mapKeys.length; si += 25) {
      var chunk = mapKeys.slice(si, si + 25);
      stampBatches.push({
        compositeRequest: chunk.map(function(vipKey, idx) {
          return {
            method: 'PATCH',
            url: '/services/data/' + API_VERSION + '/sobjects/' +
              _NS + 'Inventory__c/' + existingInventoryMap[vipKey],
            referenceId: 'stamp_' + idx,
            body: { VIP_External_ID__c: vipKey }
          };
        })
      });
    }
    var stampResult = sendBatches(stampBatches, 'Inventory stamp');
    console.log('  Stamped: ' + stampResult.success + ' succeeded, ' + stampResult.fail + ' failed');
  }
  console.log('');
}

var totalSuccess = 0;
var totalFail = 0;
var stepResults = [];

PIPELINE.forEach(function(step) {
  if (PHASE_FILTER !== null && step.phase !== PHASE_FILTER) return;

  console.log('=== Phase ' + step.phase + ': ' + step.name + ' ===');

  // Load data file (real VIP data via --data-dir, or test fixtures)
  var fixturePath = resolveDataFile(step.fixture);
  if (!fs.existsSync(fixturePath)) {
    console.log('  SKIP: Data file not found: ' + fixturePath);
    console.log('');
    stepResults.push({ name: step.name, status: 'skipped', reason: 'No data file' });
    return;
  }

  var csvContent = fs.readFileSync(fixturePath, 'utf8');
  var rows = parseCSV(csvContent);
  console.log('  Parsed ' + rows.length + ' rows from ' + path.basename(fixturePath));

  // Load and run script
  var scriptPath = path.join(SCRIPTS_DIR, step.script);
  // Clear require cache to avoid stale state
  delete require.cache[require.resolve(scriptPath)];
  var script = require(scriptPath);

  var input = { rows: rows };
  if (DIST_ID) input.targetDistId = DIST_ID;

  // fileDate = date of run (for stale cleanup). CLI arg overrides, otherwise today.
  var fileDate = FILE_DATE || new Date().toISOString().substring(0, 10);
  input.fileDate = fileDate;

  // Inject record type IDs
  if (FINISHED_GOOD_RT_ID) input.finishedGoodRecordTypeId = FINISHED_GOOD_RT_ID;
  if (CUSTOMER_RT_ID) input.customerRecordTypeId = CUSTOMER_RT_ID;

  // Inject supplier external ID for Script 02 (links Item_Lines to Supplier Account)
  if (_cfg.supplier && _cfg.supplier.externalId) {
    input.supplierExternalId = _cfg.supplier.externalId;
  }

  // Inject existing Inventory map for Script 06 (avoids duplicate validation rule)
  if (step.script === '06-invda-inventory.js') {
    runInventoryPreQuery();
    if (Object.keys(existingInventoryMap).length > 0) {
      input.existingInventoryMap = existingInventoryMap;
    }
  }

  var result;
  try {
    result = script.step(input);
  } catch (e) {
    console.log('  ERROR: Script failed: ' + e.message);
    console.log('');
    stepResults.push({ name: step.name, status: 'error', reason: e.message });
    return;
  }

  console.log('  Transform: ' + JSON.stringify(result.summary || {}).substring(0, 150));

  // Send to SF
  try {
    var sendResult = step.run(result);
    var s = sendResult.success || 0;
    var f = sendResult.fail || 0;
    totalSuccess += s;
    totalFail += f;
    stepResults.push({ name: step.name, status: f > 0 ? 'partial' : 'success', success: s, fail: f });
  } catch (e) {
    console.log('  ERROR: Send failed: ' + e.message);
    stepResults.push({ name: step.name, status: 'error', reason: e.message });
  }

  console.log('');
});

// =============================================================================
// SUMMARY
// =============================================================================

console.log('============================================');
console.log('E2E Summary');
console.log('============================================');
stepResults.forEach(function(r) {
  var status = r.status === 'success' ? 'OK' :
               r.status === 'partial' ? 'PARTIAL' :
               r.status === 'skipped' ? 'SKIP' : 'ERR';
  var detail = r.success !== undefined ? ' (' + r.success + ' ok, ' + r.fail + ' fail)' :
               r.reason ? ' (' + r.reason + ')' : '';
  console.log('  [' + status + '] ' + r.name + detail);
});
console.log('');
console.log('Total: ' + totalSuccess + ' succeeded, ' + totalFail + ' failed');
if (DRY_RUN) console.log('(DRY RUN — no records were actually sent)');

// Categorized error summary
if (errorDetails.length > 0) {
  var errorsByCategory = {};
  errorDetails.forEach(function(e) {
    errorsByCategory[e.category] = (errorsByCategory[e.category] || 0) + 1;
  });
  console.log('');
  console.log('Error breakdown:');
  Object.keys(errorsByCategory).forEach(function(cat) {
    console.log('  ' + cat + ': ' + errorsByCategory[cat]);
  });
}

console.log('============================================');

// JSON output
if (OUTPUT_JSON) {
  var report = {
    timestamp: new Date().toISOString(),
    config: {
      customer: _cfg.customer || null,
      supplierCode: _cfg.supplierCode || null,
      configFile: _cfg._configFile ? path.basename(_cfg._configFile) : null,
      targetOrg: TARGET_ORG,
      distId: DIST_ID || null,
      fileDate: FILE_DATE || new Date().toISOString().substring(0, 10),
      dryRun: DRY_RUN,
      phaseFilter: PHASE_FILTER
    },
    summary: {
      totalSuccess: totalSuccess,
      totalFail: totalFail,
      steps: stepResults
    },
    errors: errorDetails,
    errorsByCategory: {}
  };
  errorDetails.forEach(function(e) {
    report.errorsByCategory[e.category] = (report.errorsByCategory[e.category] || 0) + 1;
  });
  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(report, null, 2));
  console.log('');
  console.log('JSON report written to: ' + OUTPUT_JSON);
}

process.exit(totalFail > 0 ? 1 : 0);
