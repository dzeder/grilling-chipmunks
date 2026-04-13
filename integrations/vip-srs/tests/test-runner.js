/**
 * VIP SRS Integration — Simple Test Runner
 *
 * Loads a script, feeds it sample CSV data, and validates the output.
 * Usage: node test-runner.js ../scripts/01-srschain-chains.js fixtures/srschain-sample.csv
 */

var fs = require('fs');
var path = require('path');

// Simple CSV parser (handles quoted fields with commas)
function parseCSV(content) {
  // Normalize line endings (CRLF → LF)
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
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === ',' && !inQuotes) {
      values.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  values.push(current);

  return values;
}

// Main
var args = process.argv.slice(2);
if (args.length < 2) {
  console.log('Usage: node test-runner.js <script-path> <csv-fixture-path> [targetDistId]');
  process.exit(1);
}

var scriptPath = path.resolve(args[0]);
var fixturePath = path.resolve(args[1]);
var targetDistId = args[2] || null;

console.log('=== VIP SRS Test Runner ===');
console.log('Script:', path.basename(scriptPath));
console.log('Fixture:', path.basename(fixturePath));
if (targetDistId) console.log('Target Dist ID:', targetDistId);
console.log('');

// Load script
var script = require(scriptPath);

// Load and parse CSV
var csvContent = fs.readFileSync(fixturePath, 'utf8');
var rows = parseCSV(csvContent);
console.log('Parsed', rows.length, 'rows from CSV');
console.log('');

// Run script
var input = { rows: rows };
if (targetDistId) input.targetDistId = targetDistId;

var result = script.step(input);

// Normalize output — handle dual-output scripts (e.g., 05-outda has accountBatches/contactBatches)
var records = result.records || result.accountRecords || [];
var recordCount = result.recordCount || result.accountCount || 0;
var batches = result.batches || result.accountBatches || [];
var batchCount = result.batchCount || result.accountBatchCount || 0;

// Print results
console.log('=== Results ===');
console.log('Summary:', JSON.stringify(result.summary, null, 2));
console.log('');

if (recordCount > 0) {
  console.log('First record:', JSON.stringify(records[0], null, 2));
  console.log('');
}

if (batchCount > 0) {
  console.log('First batch (first 2 requests):');
  var firstBatch = batches[0];
  firstBatch.compositeRequest.slice(0, 2).forEach(function(req) {
    console.log('  ' + req.method + ' ' + req.url);
    console.log('  Body:', JSON.stringify(req.body, null, 2));
  });
  console.log('');
}

// Contact output (dual-output scripts)
if (result.contactRecords && result.contactRecords.length > 0) {
  console.log('First contact:', JSON.stringify(result.contactRecords[0], null, 2));
  console.log('Contact count:', result.contactCount);
  console.log('');
}

// Inventory-specific outputs
if (result.inventoryRecords) {
  console.log('Inventory records:', result.inventoryCount);
  if (result.inventoryRecords.length > 0) console.log('First inventory:', JSON.stringify(result.inventoryRecords[0], null, 2));
}
if (result.historyRecords) {
  console.log('History records:', result.historyCount);
  if (result.historyRecords.length > 0) console.log('First history:', JSON.stringify(result.historyRecords[0], null, 2));
}
if (result.adjustmentRecords) {
  console.log('Adjustment records:', result.adjustmentCount);
  if (result.adjustmentRecords.length > 0) console.log('First adjustment:', JSON.stringify(result.adjustmentRecords[0], null, 2));
}

// Invoice-specific outputs
if (result.invoiceRecords) {
  console.log('Invoice headers:', result.invoiceCount);
  if (result.invoiceRecords.length > 0) console.log('First invoice:', JSON.stringify(result.invoiceRecords[0], null, 2));
}
if (result.invoiceItemRecords) {
  console.log('Invoice items:', result.invoiceItemCount);
  if (result.invoiceItemRecords.length > 0) console.log('First invoice item:', JSON.stringify(result.invoiceItemRecords[0], null, 2));
}
if (result.placementRecords) {
  console.log('Placement records:', result.placementCount);
  if (result.placementRecords.length > 0) console.log('First placement:', JSON.stringify(result.placementRecords[0], null, 2));
}

if (result.errors && result.errors.length > 0) {
  console.log('Errors (' + result.errors.length + '):');
  result.errors.slice(0, 5).forEach(function(e) {
    console.log('  -', JSON.stringify(e));
  });
  console.log('');
}

// Extra outputs (for ITM2DA — Item_Line/Item_Type upsert batches)
if (result.itemLineBatches && result.itemLineBatches.length > 0) {
  console.log('Item Line batches:', result.itemLineBatchCount, '(' + result.itemLineRecordCount + ' records)');
  var firstIL = result.itemLineBatches[0].compositeRequest[0];
  console.log('  First:', firstIL.method, firstIL.url);
  console.log('  Body:', JSON.stringify(firstIL.body));
}
if (result.itemTypeBatches && result.itemTypeBatches.length > 0) {
  console.log('Item Type batches:', result.itemTypeBatchCount, '(' + result.itemTypeRecordCount + ' records)');
  var firstIT = result.itemTypeBatches[0].compositeRequest[0];
  console.log('  First:', firstIT.method, firstIT.url);
  console.log('  Body:', JSON.stringify(firstIT.body));
}

// Assertions
var passed = 0;
var failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log('  PASS:', message);
  } else {
    failed++;
    console.log('  FAIL:', message);
  }
}

console.log('');
console.log('=== Assertions ===');
assert(recordCount > 0, 'Should produce at least one record');
assert(batchCount > 0, 'Should produce at least one batch');
assert(result.summary !== undefined, 'Should include summary');

if (batches.length > 0) {
  var firstReq = batches[0].compositeRequest[0];
  assert(firstReq.method === 'PATCH', 'Composite method should be PATCH');
  assert(firstReq.url.indexOf('/sobjects/') > -1, 'URL should contain /sobjects/');
  assert(batches[0].compositeRequest.length <= 25, 'Batch size should be <= 25');
}

console.log('');
console.log('Results:', passed, 'passed,', failed, 'failed');
process.exit(failed > 0 ? 1 : 0);
