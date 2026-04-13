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
 */

var fs = require('fs');
var path = require('path');
var execSync = require('child_process').execSync;

// =============================================================================
// CONFIG
// =============================================================================

var TARGET_ORG = 'shipyard-ros2-sandbox';
var DIST_ID = ''; // empty = all distributors; use --dist-id FL01 to filter
var DRY_RUN = false;
var PHASE_FILTER = null; // null = all phases
var API_VERSION = 'v62.0';
var FILE_DATE = ''; // YYYY-MM-DD — set via --file-date, defaults to today (date of run)

// Parse CLI args
var args = process.argv.slice(2);
for (var i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--target-org': TARGET_ORG = args[++i]; break;
    case '--dist-id': DIST_ID = args[++i]; break;
    case '--dry-run': DRY_RUN = true; break;
    case '--phase': PHASE_FILTER = parseInt(args[++i], 10); break;
    case '--file-date': FILE_DATE = args[++i]; break;
    case '--help': case '-h':
      console.log('Usage: node e2e-sandbox-runner.js [--target-org ORG] [--dist-id ID] [--phase N] [--file-date YYYY-MM-DD] [--dry-run]');
      process.exit(0);
  }
}

// =============================================================================
// PATHS
// =============================================================================

var SCRIPTS_DIR = path.join(__dirname);
var FIXTURES_DIR = path.join(__dirname, '..', 'tests', 'fixtures');

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

function sfApiPost(endpoint, body) {
  var tmpFile = '/tmp/vip-e2e-body-' + Date.now() + '.json';
  fs.writeFileSync(tmpFile, JSON.stringify(body));
  try {
    var result = execSync(
      'sf api request rest "' + endpoint + '" --method POST --body @' + tmpFile +
      ' --target-org ' + TARGET_ORG + ' 2>/dev/null',
      { encoding: 'utf8', timeout: 60000 }
    );
    return JSON.parse(result);
  } catch (e) {
    var output = e.stdout ? e.stdout.toString() : '';
    try { return JSON.parse(output); } catch (_) {}
    return { error: e.message, stdout: output };
  } finally {
    try { fs.unlinkSync(tmpFile); } catch (_) {}
  }
}

function sfApiPatch(endpoint, body) {
  var tmpFile = '/tmp/vip-e2e-body-' + Date.now() + '.json';
  fs.writeFileSync(tmpFile, JSON.stringify(body));
  try {
    var result = execSync(
      'sf api request rest "' + endpoint + '" --method PATCH --body @' + tmpFile +
      ' --target-org ' + TARGET_ORG + ' 2>/dev/null',
      { encoding: 'utf8', timeout: 60000 }
    );
    // PATCH upsert returns 204 (no body) on success, 201 with body on create
    if (!result || !result.trim()) return { success: true, httpStatusCode: 204 };
    return JSON.parse(result);
  } catch (e) {
    var output = e.stdout ? e.stdout.toString() : '';
    if (!output || !output.trim()) return { success: true, httpStatusCode: 204 };
    try { return JSON.parse(output); } catch (_) {}
    return { error: e.message };
  } finally {
    try { fs.unlinkSync(tmpFile); } catch (_) {}
  }
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
          console.log('    ERROR [' + idx + '] ' + r.httpStatusCode + ': ' + JSON.stringify(r.body));
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
      return sendBatches(result.batches, 'Chain Banners');
    }
  },
  {
    phase: 1,
    name: '02-itm2da → Item_Line + Item_Type + Item',
    script: '02-itm2da-items.js',
    fixture: 'itm2da-sample.csv',
    run: function(result) {
      // Create Item_Lines first
      if (result.newItemLines && result.newItemLines.length > 0) {
        console.log('  Creating ' + result.newItemLines.length + ' Item Lines...');
        result.newItemLines.forEach(function(il) {
          createRecordByName('ohfy__Item_Line__c', il.Name);
        });
      }
      // Create Item_Types
      if (result.newItemTypes && result.newItemTypes.length > 0) {
        console.log('  Creating ' + result.newItemTypes.length + ' Item Types...');
        result.newItemTypes.forEach(function(it) {
          createRecordByName('ohfy__Item_Type__c', it.Name);
        });
      }
      // Upsert Items
      return sendBatches(result.batches, 'Items');
    }
  },
  {
    phase: 1,
    name: '03-distda → Location',
    script: '03-distda-locations.js',
    fixture: 'distda-sample.csv',
    run: function(result) {
      return sendBatches(result.batches, 'Locations');
    }
  },
  // Phase 2: Enrichment
  {
    phase: 2,
    name: '04-itmda → Item (enrichment)',
    script: '04-itmda-enrichment.js',
    fixture: 'itmda-sample.csv',
    run: function(result) {
      return sendBatches(result.batches, 'Item Enrichment');
    }
  },
  {
    phase: 2,
    name: '05-outda → Account (Outlets) + Contact (Buyers)',
    script: '05-outda-accounts.js',
    fixture: 'outda-sample.csv',
    run: function(result) {
      // Accounts first (parent)
      var acctResult = sendBatches(result.accountBatches, 'Accounts (Outlets)');
      // Contacts second (child — needs Account to exist)
      var contResult = sendBatches(result.contactBatches, 'Contacts (Buyers)');
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
      // Inventory first (parent)
      var invResult = sendBatches(result.inventoryBatches, 'Inventory');
      // History + Adjustments (children)
      var histResult = sendBatches(result.historyBatches, 'Inventory History');
      var adjResult = sendBatches(result.adjustmentBatches, 'Inventory Adjustments');
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
      return sendBatches(result.batches, 'Depletions');
    }
  },
  {
    phase: 4,
    name: '07b-slsda → Placement',
    script: '07b-slsda-placements.js',
    fixture: 'slsda-25.csv',
    run: function(result) {
      return sendBatches(result.batches, 'Placements');
    }
  },
  {
    phase: 4,
    name: '08-ctlda → Allocation',
    script: '08-ctlda-allocations.js',
    fixture: 'ctlda-sample.csv',
    run: function(result) {
      return sendBatches(result.batches, 'Allocations');
    }
  }
];

// =============================================================================
// MAIN
// =============================================================================

console.log('============================================');
console.log('VIP SRS E2E Sandbox Runner');
console.log('============================================');
console.log('Target org:  ' + TARGET_ORG);
console.log('Dist ID:     ' + (DIST_ID || '(all distributors)'));
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
console.log('');

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

  // Load fixture
  var fixturePath = path.join(FIXTURES_DIR, step.fixture);
  if (!fs.existsSync(fixturePath)) {
    console.log('  SKIP: Fixture not found: ' + step.fixture);
    console.log('');
    stepResults.push({ name: step.name, status: 'skipped', reason: 'No fixture' });
    return;
  }

  var csvContent = fs.readFileSync(fixturePath, 'utf8');
  var rows = parseCSV(csvContent);
  console.log('  Parsed ' + rows.length + ' rows from ' + step.fixture);

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

  // Inject record type IDs for item scripts
  if (FINISHED_GOOD_RT_ID) input.finishedGoodRecordTypeId = FINISHED_GOOD_RT_ID;

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
console.log('============================================');

process.exit(totalFail > 0 ? 1 : 0);
