#!/usr/bin/env node
/**
 * VIP SRS Post-Load Verification
 *
 * Runs SOQL count queries for all 14 VIP object types, spot-checks key
 * records, and outputs a structured report (human + optional JSON).
 *
 * Usage:
 *   node verify-load.js                              # default org, all objects
 *   node verify-load.js --dist-id FL01               # filter by distributor
 *   node verify-load.js --target-org my-sandbox      # custom org
 *   node verify-load.js --output-json results.json   # write JSON report
 *   node verify-load.js --spot-checks                # include record spot-checks
 *   node verify-load.js --config config/gulf.json    # use a different customer config
 */

var execSync = require('child_process').execSync;
var fs = require('fs');
var path = require('path');
var loadConfig = require('./config-loader');

// =============================================================================
// CONFIG
// =============================================================================

var _cfg = loadConfig(process.argv.slice(2));
var TARGET_ORG = _cfg.targetOrg;
var DIST_ID = _cfg.distId;
var OUTPUT_JSON = '';
var SPOT_CHECKS = false;

var args = process.argv.slice(2);
for (var i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--target-org': TARGET_ORG = args[++i]; break;
    case '--dist-id': DIST_ID = args[++i]; break;
    case '--output-json': OUTPUT_JSON = args[++i]; break;
    case '--spot-checks': SPOT_CHECKS = true; break;
    case '--config': i++; break; // already consumed by config-loader
    case '--help': case '-h':
      console.log('Usage: node verify-load.js [--config FILE] [--target-org ORG] [--dist-id ID] [--output-json FILE] [--spot-checks]');
      process.exit(0);
  }
}

// =============================================================================
// SOQL HELPER
// =============================================================================

function sfQuery(soql) {
  try {
    var result = execSync(
      'sf data query --target-org ' + TARGET_ORG + ' --query "' + soql + '" --result-format json 2>/dev/null',
      { encoding: 'utf8', timeout: 30000 }
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
// OBJECT DEFINITIONS
// =============================================================================

var OBJECTS = [
  // Phase 1: Reference
  {
    phase: 1,
    name: 'Account (Chain Banners)',
    sobject: 'Account',
    extIdField: 'ohfy__External_ID__c',
    prefix: 'CHN',
    distScoped: false,
    countQuery: "SELECT COUNT() FROM Account WHERE ohfy__External_ID__c LIKE 'CHN:%'",
    spotQuery: "SELECT Name, Type, ohfy__Is_Chain_Banner__c, AccountSource FROM Account WHERE ohfy__External_ID__c LIKE 'CHN:%' LIMIT 3"
  },
  {
    phase: 1,
    name: 'Item_Line__c',
    sobject: 'ohfy__Item_Line__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'ILN',
    distScoped: false,
    countQuery: "SELECT COUNT() FROM ohfy__Item_Line__c WHERE VIP_External_ID__c LIKE 'ILN:%'",
    spotQuery: "SELECT Name, VIP_External_ID__c FROM ohfy__Item_Line__c WHERE VIP_External_ID__c LIKE 'ILN:%' LIMIT 3"
  },
  {
    phase: 1,
    name: 'Item_Type__c',
    sobject: 'ohfy__Item_Type__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'ITY',
    distScoped: false,
    countQuery: "SELECT COUNT() FROM ohfy__Item_Type__c WHERE VIP_External_ID__c LIKE 'ITY:%'",
    spotQuery: "SELECT Name, VIP_External_ID__c FROM ohfy__Item_Type__c WHERE VIP_External_ID__c LIKE 'ITY:%' LIMIT 3"
  },
  {
    phase: 1,
    name: 'Item__c',
    sobject: 'ohfy__Item__c',
    extIdField: 'ohfy__VIP_External_ID__c',
    prefix: 'ITM',
    distScoped: false,
    countQuery: "SELECT COUNT() FROM ohfy__Item__c WHERE ohfy__VIP_External_ID__c LIKE 'ITM:%'",
    spotQuery: "SELECT Name, RecordType.Name, ohfy__Type__c, ohfy__UOM__c, ohfy__Packaging_Type__c FROM ohfy__Item__c WHERE ohfy__VIP_External_ID__c LIKE 'ITM:%' LIMIT 3"
  },
  {
    phase: 1,
    name: 'Location__c',
    sobject: 'ohfy__Location__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'LOC',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM ohfy__Location__c WHERE VIP_External_ID__c = 'LOC:" + distId + "'"
        : "SELECT COUNT() FROM ohfy__Location__c WHERE VIP_External_ID__c LIKE 'LOC:%'";
    },
    spotQuery: "SELECT Name, VIP_External_ID__c, ohfy__Location_Code__c FROM ohfy__Location__c WHERE VIP_External_ID__c LIKE 'LOC:%' LIMIT 3"
  },
  // Phase 2: Enrichment
  {
    phase: 2,
    name: 'Account (Outlets)',
    sobject: 'Account',
    extIdField: 'ohfy__External_ID__c',
    prefix: 'ACT',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM Account WHERE ohfy__External_ID__c LIKE 'ACT:" + distId + ":%'"
        : "SELECT COUNT() FROM Account WHERE ohfy__External_ID__c LIKE 'ACT:%'";
    },
    spotQuery: function(distId) {
      var filter = distId ? "'ACT:" + distId + ":%'" : "'ACT:%'";
      return "SELECT Name, Type, ohfy__Market__c, ohfy__Premise_Type__c, AccountSource FROM Account WHERE ohfy__External_ID__c LIKE " + filter + " LIMIT 3";
    }
  },
  {
    phase: 2,
    name: 'Contact (Buyers)',
    sobject: 'Contact',
    extIdField: 'External_ID__c',
    prefix: 'CON',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM Contact WHERE External_ID__c LIKE 'CON:" + distId + ":%'"
        : "SELECT COUNT() FROM Contact WHERE External_ID__c LIKE 'CON:%'";
    },
    spotQuery: "SELECT Name, External_ID__c FROM Contact WHERE External_ID__c LIKE 'CON:%' LIMIT 3"
  },
  // Phase 3: Inventory
  {
    phase: 3,
    name: 'Inventory__c',
    sobject: 'ohfy__Inventory__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'IVT',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM ohfy__Inventory__c WHERE VIP_External_ID__c LIKE 'IVT:" + distId + ":%'"
        : "SELECT COUNT() FROM ohfy__Inventory__c WHERE VIP_External_ID__c LIKE 'IVT:%'";
    },
    spotQuery: "SELECT ohfy__Item__r.Name, ohfy__Quantity_On_Hand__c, VIP_External_ID__c FROM ohfy__Inventory__c WHERE VIP_External_ID__c LIKE 'IVT:%' LIMIT 3"
  },
  {
    phase: 3,
    name: 'Inventory_History__c',
    sobject: 'ohfy__Inventory_History__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'IVH',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM ohfy__Inventory_History__c WHERE VIP_External_ID__c LIKE 'IVH:" + distId + ":%'"
        : "SELECT COUNT() FROM ohfy__Inventory_History__c WHERE VIP_External_ID__c LIKE 'IVH:%'";
    },
    spotQuery: "SELECT VIP_External_ID__c, VIP_File_Date__c FROM ohfy__Inventory_History__c WHERE VIP_External_ID__c LIKE 'IVH:%' LIMIT 3"
  },
  {
    phase: 3,
    name: 'Inventory_Adjustment__c',
    sobject: 'ohfy__Inventory_Adjustment__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'IVA',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM ohfy__Inventory_Adjustment__c WHERE VIP_External_ID__c LIKE 'IVA:" + distId + ":%'"
        : "SELECT COUNT() FROM ohfy__Inventory_Adjustment__c WHERE VIP_External_ID__c LIKE 'IVA:%'";
    },
    spotQuery: "SELECT VIP_External_ID__c, ohfy__Type__c, ohfy__Status__c FROM ohfy__Inventory_Adjustment__c WHERE VIP_External_ID__c LIKE 'IVA:%' LIMIT 3"
  },
  // Phase 4: Transactions
  {
    phase: 4,
    name: 'Depletion__c',
    sobject: 'ohfy__Depletion__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'DEP',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM ohfy__Depletion__c WHERE VIP_External_ID__c LIKE 'DEP:" + distId + ":%'"
        : "SELECT COUNT() FROM ohfy__Depletion__c WHERE VIP_External_ID__c LIKE 'DEP:%'";
    },
    spotQuery: "SELECT ohfy__Customer__r.Name, ohfy__Item__r.Name, ohfy__Case_Quantity__c, ohfy__Date__c FROM ohfy__Depletion__c WHERE VIP_External_ID__c LIKE 'DEP:%' LIMIT 3"
  },
  {
    phase: 4,
    name: 'Placement__c',
    sobject: 'ohfy__Placement__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'PLC',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM ohfy__Placement__c WHERE VIP_External_ID__c LIKE 'PLC:" + distId + ":%'"
        : "SELECT COUNT() FROM ohfy__Placement__c WHERE VIP_External_ID__c LIKE 'PLC:%'";
    },
    spotQuery: "SELECT ohfy__Account__r.Name, ohfy__Item__r.Name, ohfy__First_Sold_Date__c, ohfy__Last_Sold_Date__c, ohfy__Is_New_Placement__c FROM ohfy__Placement__c WHERE VIP_External_ID__c LIKE 'PLC:%' LIMIT 3"
  },
  {
    phase: 4,
    name: 'Allocation__c',
    sobject: 'ohfy__Allocation__c',
    extIdField: 'VIP_External_ID__c',
    prefix: 'ALC',
    distScoped: true,
    countQuery: function(distId) {
      return distId
        ? "SELECT COUNT() FROM ohfy__Allocation__c WHERE VIP_External_ID__c LIKE 'ALC:" + distId + ":%'"
        : "SELECT COUNT() FROM ohfy__Allocation__c WHERE VIP_External_ID__c LIKE 'ALC:%'";
    },
    spotQuery: "SELECT VIP_External_ID__c, ohfy__End_Date__c FROM ohfy__Allocation__c WHERE VIP_External_ID__c LIKE 'ALC:%' LIMIT 3"
  }
];

// =============================================================================
// MAIN
// =============================================================================

console.log('============================================');
console.log('VIP SRS Post-Load Verification');
console.log('============================================');
if (_cfg.customer) console.log('Customer:    ' + _cfg.customer);
if (_cfg._configFile) console.log('Config:      ' + path.basename(_cfg._configFile));
console.log('Target org:  ' + TARGET_ORG);
console.log('Dist ID:     ' + (DIST_ID || '(all)'));
console.log('Spot checks: ' + (SPOT_CHECKS ? 'YES' : 'NO'));
console.log('============================================');
console.log('');

var results = [];
var totalRecords = 0;
var currentPhase = 0;

OBJECTS.forEach(function(obj) {
  if (obj.phase !== currentPhase) {
    currentPhase = obj.phase;
    console.log('--- Phase ' + currentPhase + ' ---');
  }

  var query = typeof obj.countQuery === 'function' ? obj.countQuery(DIST_ID) : obj.countQuery;
  var count = countRecords(query);
  totalRecords += (count > 0 ? count : 0);

  var status = count > 0 ? 'OK' : count === 0 ? 'EMPTY' : 'ERROR';
  var icon = count > 0 ? '  [OK]   ' : count === 0 ? '  [EMPTY]' : '  [ERR]  ';
  console.log(icon + ' ' + obj.name + ': ' + count);

  var entry = {
    phase: obj.phase,
    name: obj.name,
    sobject: obj.sobject,
    prefix: obj.prefix,
    count: count,
    status: status
  };

  // Spot checks
  if (SPOT_CHECKS && count > 0) {
    var spotSoql = typeof obj.spotQuery === 'function' ? obj.spotQuery(DIST_ID) : obj.spotQuery;
    var spotResult = sfQuery(spotSoql);
    if (spotResult.records && spotResult.records.length > 0) {
      entry.samples = spotResult.records.map(function(r) {
        // Strip attributes key for cleaner output
        var clean = {};
        Object.keys(r).forEach(function(k) {
          if (k !== 'attributes') clean[k] = r[k];
        });
        return clean;
      });
      console.log('           Sample: ' + JSON.stringify(entry.samples[0]).substring(0, 120));
    }
  }

  results.push(entry);
});

console.log('');
console.log('============================================');
console.log('Total VIP records: ' + totalRecords);
console.log('============================================');

var emptyObjects = results.filter(function(r) { return r.status === 'EMPTY'; });
var errorObjects = results.filter(function(r) { return r.status === 'ERROR'; });

if (emptyObjects.length > 0) {
  console.log('');
  console.log('Empty objects (' + emptyObjects.length + '):');
  emptyObjects.forEach(function(r) {
    console.log('  - ' + r.name + ' (' + r.prefix + ':*)');
  });
}

if (errorObjects.length > 0) {
  console.log('');
  console.log('Query errors (' + errorObjects.length + '):');
  errorObjects.forEach(function(r) {
    console.log('  - ' + r.name);
  });
}

// JSON output
if (OUTPUT_JSON) {
  var report = {
    timestamp: new Date().toISOString(),
    targetOrg: TARGET_ORG,
    distId: DIST_ID || null,
    totalRecords: totalRecords,
    objects: results,
    summary: {
      ok: results.filter(function(r) { return r.status === 'OK'; }).length,
      empty: emptyObjects.length,
      error: errorObjects.length
    }
  };
  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(report, null, 2));
  console.log('');
  console.log('JSON report written to: ' + OUTPUT_JSON);
}

// Exit code: 0 if all OK or EMPTY, 1 if any errors
process.exit(errorObjects.length > 0 ? 1 : 0);
