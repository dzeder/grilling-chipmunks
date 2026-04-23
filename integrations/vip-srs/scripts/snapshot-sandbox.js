#!/usr/bin/env node
/**
 * VIP SRS Sandbox Snapshot
 *
 * Captures a point-in-time snapshot of all VIP-loaded objects: record count
 * plus 5 most-recently-modified sample records per object. Used by the
 * nightly-burst orchestrator to compute day-level before/after diffs.
 *
 * Usage:
 *   node snapshot-sandbox.js --out logs/snapshot.json
 *   node snapshot-sandbox.js --out logs/snapshot.json --target-org shipyard-ros2-sandbox
 *   node snapshot-sandbox.js --out logs/snapshot.json --label "pre-burst"
 */

var execSync = require('child_process').execSync;
var fs = require('fs');
var path = require('path');
var loadConfig = require('./config-loader');
var verifyLoad = require('./verify-load');

var OBJECTS = verifyLoad.OBJECTS;

// =============================================================================
// CONFIG
// =============================================================================

var _cfg = loadConfig(process.argv.slice(2));
var TARGET_ORG = _cfg.targetOrg;
var DIST_ID = _cfg.distId;
var OUTPUT = '';
var LABEL = '';

var args = process.argv.slice(2);
for (var i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--target-org': TARGET_ORG = args[++i]; break;
    case '--dist-id': DIST_ID = args[++i]; break;
    case '--out': OUTPUT = args[++i]; break;
    case '--label': LABEL = args[++i]; break;
    case '--config': i++; break;
    case '--help': case '-h':
      console.log('Usage: node snapshot-sandbox.js --out FILE [--label LABEL] [--target-org ORG] [--dist-id ID]');
      process.exit(0);
  }
}

if (!OUTPUT) {
  console.error('ERROR: --out is required');
  process.exit(1);
}

// =============================================================================
// SOQL HELPERS
// =============================================================================

function sfQuery(soql) {
  try {
    var result = execSync(
      'sf data query --target-org ' + TARGET_ORG + ' --query "' + soql + '" --result-format json 2>/dev/null',
      { encoding: 'utf8', timeout: 60000, maxBuffer: 50 * 1024 * 1024 }
    );
    var parsed = JSON.parse(result);
    return parsed.result || parsed;
  } catch (e) {
    var output = e.stdout ? e.stdout.toString() : '';
    try {
      var parsed = JSON.parse(output);
      return parsed.result || parsed;
    } catch (_) {}
    return { totalSize: -1, records: [], error: e.message };
  }
}

function countRecords(soql) {
  var result = sfQuery(soql);
  if (result.totalSize !== undefined) return result.totalSize;
  return -1;
}

// =============================================================================
// SNAPSHOT
// =============================================================================

console.log('Snapshot: ' + (LABEL || '(unlabeled)') + ' | org=' + TARGET_ORG + ' | distId=' + (DIST_ID || 'all'));
console.log('============================================');

var snapshot = {
  label: LABEL,
  takenAt: new Date().toISOString(),
  targetOrg: TARGET_ORG,
  distId: DIST_ID || null,
  objects: {}
};

var totalRecords = 0;

OBJECTS.forEach(function(obj) {
  var countQuery = typeof obj.countQuery === 'function' ? obj.countQuery(DIST_ID) : obj.countQuery;
  var count = countRecords(countQuery);
  if (count > 0) totalRecords += count;

  console.log('  ' + obj.name + ': ' + count);

  // Pull 5 recent samples (by LastModifiedDate when available)
  var samples = [];
  if (count > 0) {
    // Build a sample query using the prefix pattern. Prefer LastModifiedDate ordering.
    var extIdPattern = "'" + obj.prefix + ":%'";
    var extIdField = obj.extIdField;
    // Account uses different extId fields by prefix — infer from the count query
    var soql = 'SELECT Id, ' + extIdField + ', LastModifiedDate FROM ' + obj.sobject +
               ' WHERE ' + extIdField + " LIKE " + extIdPattern +
               ' ORDER BY LastModifiedDate DESC NULLS LAST LIMIT 5';
    var result = sfQuery(soql);
    if (result.records && result.records.length > 0) {
      samples = result.records.map(function(r) {
        var clean = {};
        Object.keys(r).forEach(function(k) {
          if (k !== 'attributes') clean[k] = r[k];
        });
        return clean;
      });
    }
  }

  snapshot.objects[obj.sobject + ':' + obj.prefix] = {
    displayName: obj.name,
    sobject: obj.sobject,
    prefix: obj.prefix,
    phase: obj.phase,
    count: count,
    recentSamples: samples
  };
});

snapshot.totalRecords = totalRecords;

console.log('============================================');
console.log('Total: ' + totalRecords + ' records across ' + OBJECTS.length + ' object/prefix buckets');

// Ensure output dir exists
var outDir = path.dirname(OUTPUT);
if (outDir && !fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}
fs.writeFileSync(OUTPUT, JSON.stringify(snapshot, null, 2));
console.log('Written: ' + OUTPUT);
