#!/usr/bin/env node
/**
 * Run Items pipeline only (Item Lines → Item Types → Items).
 * Skips Chains, Distributors, Locations to avoid AccountTriggerMethods on re-upsert.
 */
var fs = require('fs');
var path = require('path');
var execSync = require('child_process').execSync;
var loadConfig = require('./config-loader');

var cfg = loadConfig(process.argv.slice(2));
var ORG = cfg.targetOrg;
var API = cfg.apiVersion;
var DATA_DIR = '';
var args = process.argv.slice(2);
for (var i = 0; i < args.length; i++) {
  if (args[i] === '--data-dir') DATA_DIR = args[++i];
}

// CSV parser
function parseCSV(content) {
  content = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  var lines = content.split('\n').filter(function(l) { return l.trim(); });
  if (lines.length < 2) return [];
  var headers = parseCSVLine(lines[0]);
  var rows = [];
  for (var i = 1; i < lines.length; i++) {
    var values = parseCSVLine(lines[i]);
    var row = {};
    headers.forEach(function(h, idx) { row[h] = values[idx] !== undefined ? values[idx] : ''; });
    rows.push(row);
  }
  return rows;
}
function parseCSVLine(line) {
  var values = [], current = '', inQuotes = false;
  for (var i = 0; i < line.length; i++) {
    var ch = line[i];
    if (ch === '"') { if (inQuotes && line[i+1] === '"') { current += '"'; i++; } else { inQuotes = !inQuotes; } }
    else if (ch === ',' && !inQuotes) { values.push(current); current = ''; }
    else { current += ch; }
  }
  values.push(current);
  return values;
}

// SF helpers
function sfPost(endpoint, body) {
  var tmp = '/tmp/vip-items-' + Date.now() + '.json';
  fs.writeFileSync(tmp, JSON.stringify(body));
  try {
    var r = execSync('sf api request rest "' + endpoint + '" --method POST --body @' + tmp + ' --target-org ' + ORG + ' 2>/dev/null', {encoding:'utf8', timeout:60000});
    try { fs.unlinkSync(tmp); } catch(_) {}
    return JSON.parse(r);
  } catch(e) {
    try { fs.unlinkSync(tmp); } catch(_) {}
    var out = e.stdout ? e.stdout.toString() : '';
    try { return JSON.parse(out); } catch(_) { return {error: e.message}; }
  }
}

function sendBatch(batch, label) {
  var resp = sfPost('/services/data/' + API + '/composite', {compositeRequest: batch.compositeRequest});
  if (resp.compositeResponse) {
    var s = 0, f = 0;
    resp.compositeResponse.forEach(function(r) { if (r.httpStatusCode >= 200 && r.httpStatusCode < 300) s++; else f++; });
    console.log('  ' + label + ': ' + s + ' ok, ' + f + ' fail');
    if (f > 0) {
      resp.compositeResponse.forEach(function(r, i) {
        if (r.httpStatusCode >= 300) console.log('    [' + i + '] ' + JSON.stringify(r.body).substring(0, 200));
      });
    }
    return {success: s, fail: f};
  }
  console.log('  ERROR: ' + JSON.stringify(resp).substring(0, 200));
  return {success: 0, fail: batch.compositeRequest.length};
}

// Main
console.log('=== Items-Only Pipeline ===');
console.log('Org: ' + ORG);

// Get RT ID
var rtResult = execSync("sf data query --target-org " + ORG + " --query \"SELECT Id FROM RecordType WHERE SObjectType='ohfy__Item__c' AND DeveloperName='Finished_Good' LIMIT 1\" --result-format json 2>/dev/null", {encoding:'utf8'});
var rtId = JSON.parse(rtResult).result.records[0].Id;
console.log('Finished Good RT: ' + rtId);

// Load CSV
var csvPath = DATA_DIR
  ? path.join(__dirname, '..', DATA_DIR, 'ITM2DA.csv')
  : path.join(__dirname, '..', 'tests', 'fixtures', 'itm2da-sample.csv');
var csv = fs.readFileSync(csvPath, 'utf8');
var rows = parseCSV(csv);
console.log('Parsed ' + rows.length + ' rows from ' + path.basename(csvPath));

// Transform
delete require.cache[require.resolve('./02-itm2da-items.js')];
var script = require('./02-itm2da-items.js');
var result = script.step({
  rows: rows,
  fileDate: new Date().toISOString().substring(0, 10),
  finishedGoodRecordTypeId: rtId,
  supplierExternalId: cfg.supplier ? cfg.supplier.externalId : null
});
console.log('Transform: ' + JSON.stringify(result.summary));

// Send
var total = {s: 0, f: 0};

console.log('\n--- Item Lines (' + (result.itemLineBatches ? result.itemLineBatches.length : 0) + ' batches) ---');
if (result.itemLineBatches) {
  result.itemLineBatches.forEach(function(b, i) {
    var r = sendBatch(b, 'batch ' + (i+1));
    total.s += r.success; total.f += r.fail;
  });
}

console.log('\n--- Item Types (' + (result.itemTypeBatches ? result.itemTypeBatches.length : 0) + ' batches) ---');
if (result.itemTypeBatches) {
  result.itemTypeBatches.forEach(function(b, i) {
    var r = sendBatch(b, 'batch ' + (i+1));
    total.s += r.success; total.f += r.fail;
  });
}

console.log('\n--- Items (' + result.batches.length + ' batches) ---');
result.batches.forEach(function(b, i) {
  var r = sendBatch(b, 'batch ' + (i+1));
  total.s += r.success; total.f += r.fail;
});

console.log('\n=== Done: ' + total.s + ' succeeded, ' + total.f + ' failed ===');
