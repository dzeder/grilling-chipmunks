#!/usr/bin/env node
/**
 * VIP SRS Tray Project Generator
 *
 * Generates a complete, importable Tray.io project JSON for the VIP SRS
 * supplier integration. Reads inlined scripts from build/output/*.tray.js
 * and wires them into a two-workflow project (Main + Error Handler).
 *
 * Usage: node generate-tray-project.js
 * Output: writes to daniels-ohanafy-artifacts/vip-srs-supplier/v1.0/project-export.json
 */

var crypto = require('crypto');
var fs = require('fs');
var path = require('path');

// ============================================================================
// Config
// ============================================================================

var DIST_ID = 'FL01';
var SUPPLIER_CODE = 'ARG';
var SF_API_VERSION = 'v62.0';
var SFTP_BASE_PATH = '/vip/ARG/';
var SLACK_CHANNEL = 'U05UL218VA5'; // Daniel DM
var WORKSPACE_ID = 'c52d79bd-5882-4b67-9e35-67fac73b367f';

var BUILD_OUTPUT = path.join(__dirname, 'output');
var ARTIFACTS_DIR = '/Users/danielzeder/conductor/repos/daniels-ohanafy-artifacts/vip-srs-supplier/v1.0';

// VIP file types to download from SFTP
var FILE_TYPES = [
  'SRSCHAIN', 'ITM2DA', 'DISTDA', 'ITMDA',
  'OUTDA', 'INVDA', 'SLSDA', 'CTLDA'
];

// ============================================================================
// Helpers
// ============================================================================

function uuid() { return crypto.randomUUID(); }

function str(v) { return { type: 'string', value: v }; }
function bool(v) { return { type: 'boolean', value: v }; }
function num(v) { return { type: 'number', value: v }; }
function int(v) { return { type: 'integer', value: v }; }
function jp(v) { return { type: 'jsonpath', value: v }; }
function arr(v) { return { type: 'array', value: v }; }
function obj(v) { return { type: 'object', value: v }; }
function nil() { return { type: 'null', value: null }; }

function scriptVar(name, jsonpath) {
  return { type: 'object', value: { name: str(name), value: jp(jsonpath) } };
}

// Step counters
var counters = {};
function nextStep(connectorName) {
  counters[connectorName] = (counters[connectorName] || 0) + 1;
  return connectorName + '-' + counters[connectorName];
}

// Read a .tray.js script file
function readScript(filename) {
  var p = path.join(BUILD_OUTPUT, filename);
  if (!fs.existsSync(p)) {
    console.error('Missing script: ' + p);
    process.exit(1);
  }
  return fs.readFileSync(p, 'utf8');
}

// ============================================================================
// Step builders
// ============================================================================

function triggerScheduledDaily(hour, minute, tz) {
  return {
    title: 'Daily Schedule',
    connector: { name: 'scheduled', version: '3.5' },
    operation: 'daily',
    output_schema: {},
    error_handling: {},
    properties: {
      synchronous: bool(false),
      public_url: jp('$.env.public_url'),
      hour: str(String(hour)),
      minute: str(String(minute)),
      day_of_week: obj({
        monday: bool(true), tuesday: bool(true), wednesday: bool(true),
        thursday: bool(true), friday: bool(true), saturday: bool(true),
        sunday: bool(true)
      }),
      tz: str(tz)
    }
  };
}

function triggerAlerting() {
  return {
    title: 'Alert',
    connector: { name: 'alerting-trigger', version: '1.1' },
    operation: 'trigger',
    output_schema: {},
    error_handling: {},
    properties: {
      include_raw_response: bool(true)
    }
  };
}

function sftpDownload(title) {
  return {
    title: title,
    connector: { name: 'ftp-client', version: '6.1' },
    operation: 'sftp_download',
    output_schema: {},
    error_handling: {},
    properties: {
      debug: bool(false)
    }
  };
}

function scriptStep(title, variables, scriptContent) {
  return {
    title: title,
    connector: { name: 'script', version: '3.4' },
    operation: 'execute',
    output_schema: {},
    error_handling: {},
    properties: {
      variables: arr(variables),
      script: str(scriptContent),
      file_output: bool(false)
    }
  };
}

function loopStep(title, arrayJsonpath) {
  return {
    title: title,
    connector: { name: 'loop', version: '1.3' },
    operation: 'loop_array',
    output_schema: {},
    error_handling: {},
    properties: {
      array: jp(arrayJsonpath)
    }
  };
}

function sfCompositePost(title, bodyJsonpath) {
  return {
    title: title,
    connector: { name: 'salesforce', version: '8.8' },
    operation: 'raw_http_request',
    output_schema: {},
    error_handling: {},
    properties: {
      method: str('POST'),
      include_raw_body: bool(false),
      parse_response: str('true'),
      url: obj({ endpoint: str('services/data/' + SF_API_VERSION + '/composite') }),
      query_parameters: arr([]),
      body: obj({ raw: jp(bodyJsonpath) })
    }
  };
}

function sfQuery(title, soql) {
  return {
    title: title,
    connector: { name: 'salesforce', version: '8.8' },
    operation: 'raw_http_request',
    output_schema: {},
    error_handling: {},
    properties: {
      method: str('GET'),
      include_raw_body: bool(false),
      parse_response: str('true'),
      url: obj({ endpoint: str('services/data/' + SF_API_VERSION + '/query') }),
      query_parameters: arr([
        { type: 'object', value: { key: str('q'), value: str(soql) } }
      ]),
      body: obj({ none: nil() })
    }
  };
}

function slackMessage(title, channel, textJsonpath) {
  return {
    title: title,
    connector: { name: 'slack', version: '11.0' },
    operation: 'send_message',
    output_schema: {},
    error_handling: {},
    properties: {
      use_user_token: bool(false),
      username: str('VIP SRS Pipeline'),
      parse: str('none'),
      link_names: bool(false),
      reply_broadcast: bool(false),
      channel: str(channel),
      text: jp(textJsonpath)
    }
  };
}

// ============================================================================
// CSV Parser script (inline, shared across all file types)
// ============================================================================

var CSV_PARSER_SCRIPT = [
  'exports.step = function(input, fileInput) {',
  '  var content = input.fileContent || "";',
  '  content = content.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n");',
  '  var lines = content.split("\\n").filter(function(l) { return l.trim(); });',
  '  if (lines.length < 2) return { rows: [], rowCount: 0 };',
  '  var headers = parseLine(lines[0]);',
  '  var rows = [];',
  '  for (var i = 1; i < lines.length; i++) {',
  '    var vals = parseLine(lines[i]);',
  '    var row = {};',
  '    for (var j = 0; j < headers.length; j++) {',
  '      row[headers[j]] = vals[j] !== undefined ? vals[j] : "";',
  '    }',
  '    rows.push(row);',
  '  }',
  '  return { rows: rows, rowCount: rows.length };',
  '  function parseLine(line) {',
  '    var values = [], current = "", inQ = false;',
  '    for (var k = 0; k < line.length; k++) {',
  '      var ch = line[k];',
  '      if (ch === \'"\') { inQ = !inQ; }',
  '      else if (ch === "," && !inQ) { values.push(current.trim()); current = ""; }',
  '      else { current += ch; }',
  '    }',
  '    values.push(current.trim());',
  '    return values;',
  '  }',
  '};'
].join('\n');

// ============================================================================
// Init script — computes fileDate, config object
// ============================================================================

var INIT_SCRIPT = [
  'exports.step = function(input, fileInput) {',
  '  var now = new Date();',
  '  var yyyy = now.getFullYear();',
  '  var mm = String(now.getMonth() + 1).padStart(2, "0");',
  '  var dd = String(now.getDate()).padStart(2, "0");',
  '  var fileDate = yyyy + "-" + mm + "-" + dd;',
  '  var fileSuffix = "N" + yyyy + mm + dd;',
  '  return {',
  '    fileDate: fileDate,',
  '    fileSuffix: fileSuffix,',
  '    distributorId: "' + DIST_ID + '",',
  '    supplierCode: "' + SUPPLIER_CODE + '",',
  '    sftpBasePath: "' + SFTP_BASE_PATH + '",',
  '    sfApiVersion: "' + SF_API_VERSION + '"',
  '  };',
  '};'
].join('\n');

// ============================================================================
// Notification script — formats Slack message from summary
// ============================================================================

var NOTIFICATION_SCRIPT = [
  'exports.step = function(input, fileInput) {',
  '  var s = input.summary || {};',
  '  var status = s.status || "unknown";',
  '  var icon = status === "success" ? "white_check_mark" : status === "partial" ? "warning" : "x";',
  '  var lines = [',
  '    ":" + icon + ": *VIP SRS Pipeline — " + status.toUpperCase() + "*",',
  '    "Distributor: " + (s.distId || "?") + " | File Date: " + (s.fileDate || "?"),',
  '    "Records: " + (s.totalRecords || 0) + " | Errors: " + (s.totalErrors || 0) + " | Skipped: " + (s.totalSkipped || 0),',
  '    ""',
  '  ];',
  '  var scripts = s.scripts || [];',
  '  for (var i = 0; i < scripts.length; i++) {',
  '    var sc = scripts[i];',
  '    var sIcon = sc.status === "success" ? "white_check_mark" : sc.status === "partial" ? "warning" : sc.status === "not_run" ? "black_small_square" : "x";',
  '    lines.push(":" + sIcon + ": " + sc.label + ": " + (sc.records || 0) + " records, " + (sc.errors || 0) + " errors");',
  '  }',
  '  return { message: lines.join("\\n") };',
  '};'
].join('\n');

// ============================================================================
// Error handler notification script
// ============================================================================

var ERROR_HANDLER_SCRIPT = [
  'exports.step = function(input, fileInput) {',
  '  var err = input.error || {};',
  '  var lines = [',
  '    ":x: *VIP SRS Pipeline — ERROR*",',
  '    "Workflow: " + (err.workflow_title || "unknown"),',
  '    "Step: " + (err.failed_step_name || "unknown"),',
  '    "Error: " + (err.message || JSON.stringify(err)),',
  '    "",',
  '    "Check logs: " + (err.step_log_url || "N/A")',
  '  ];',
  '  return { message: lines.join("\\n") };',
  '};'
].join('\n');

// ============================================================================
// Build the main workflow
// ============================================================================

var steps = {};
var structure = [];

// --- Trigger ---
steps['trigger'] = triggerScheduledDaily(6, 0, 'EST5EDT');
structure.push({ name: 'trigger', type: 'normal', content: {} });

// --- Init ---
var initName = nextStep('script');
steps[initName] = scriptStep('Init — Compute Dates & Config', [], INIT_SCRIPT);
structure.push({ name: initName, type: 'normal', content: {} });

// --- SFTP Downloads (8 files) ---
var ftpStepNames = {};
FILE_TYPES.forEach(function(ft) {
  var name = nextStep('ftp-client');
  steps[name] = sftpDownload('SFTP — ' + ft);
  structure.push({ name: name, type: 'normal', content: {} });
  ftpStepNames[ft] = name;
});

// --- CSV Parsing (8 scripts, one per file) ---
var csvStepNames = {};
FILE_TYPES.forEach(function(ft) {
  var name = nextStep('script');
  steps[name] = scriptStep(
    'Parse CSV — ' + ft,
    [scriptVar('fileContent', '$.steps.' + ftpStepNames[ft] + '.result.file')],
    CSV_PARSER_SCRIPT
  );
  structure.push({ name: name, type: 'normal', content: {} });
  csvStepNames[ft] = name;
});

// Helper: add a transform script + its loop(s) + SF composite step(s)
function addTransformPhase(opts) {
  // Read script from build output
  var scriptContent = readScript(opts.scriptFile);

  // Build variables array
  var variables = opts.variables.map(function(v) { return scriptVar(v.name, v.path); });

  // Script step
  var scriptName = nextStep('script');
  steps[scriptName] = scriptStep(opts.title, variables, scriptContent);
  structure.push({ name: scriptName, type: 'normal', content: {} });

  // For each batch type, add loop + SF composite
  var batchStepNames = {};
  opts.batches.forEach(function(b) {
    var loopName = nextStep('loop');
    var sfName = nextStep('salesforce');
    steps[loopName] = loopStep('Loop — ' + b.label, '$.steps.' + scriptName + '.result.' + b.field);
    steps[sfName] = sfCompositePost('SF Composite — ' + b.label, '$.steps.' + loopName + '.value');
    structure.push({
      name: loopName,
      type: 'loop',
      content: {
        _loop: [{ name: sfName, type: 'normal', content: {} }]
      }
    });
    batchStepNames[b.field] = { loop: loopName, sf: sfName, script: scriptName };
  });

  return { scriptName: scriptName, batchStepNames: batchStepNames };
}

// --- Phase 1: Reference Data ---

// Script 01 — SRSCHAIN → Account (Chain Banners)
addTransformPhase({
  title: '01 — Chain Banners',
  scriptFile: '01-srschain-chains.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['SRSCHAIN'] + '.result.rows' }
  ],
  batches: [{ field: 'batches', label: 'Chain Banners' }]
});

// Script 02 — ITM2DA → Item_Line + Item_Type + Item
addTransformPhase({
  title: '02 — Items (Lines, Types, Items)',
  scriptFile: '02-itm2da-items.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['ITM2DA'] + '.result.rows' },
    { name: 'fileDate', path: '$.steps.' + initName + '.result.fileDate' }
  ],
  batches: [
    { field: 'itemLineBatches', label: 'Item Lines' },
    { field: 'itemTypeBatches', label: 'Item Types' },
    { field: 'batches', label: 'Items' }
  ]
});

// Script 03 — DISTDA → Location
addTransformPhase({
  title: '03 — Locations',
  scriptFile: '03-distda-locations.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['DISTDA'] + '.result.rows' },
    { name: 'targetDistId', path: '$.steps.' + initName + '.result.distributorId' }
  ],
  batches: [{ field: 'batches', label: 'Locations' }]
});

// --- Phase 2: Enrichment ---

// Script 04 — ITMDA → Item enrichment
addTransformPhase({
  title: '04 — Item Enrichment',
  scriptFile: '04-itmda-enrichment.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['ITMDA'] + '.result.rows' },
    { name: 'targetDistId', path: '$.steps.' + initName + '.result.distributorId' }
  ],
  batches: [{ field: 'batches', label: 'Item Enrichment' }]
});

// Script 05 — OUTDA → Account + Contact
addTransformPhase({
  title: '05 — Accounts & Contacts',
  scriptFile: '05-outda-accounts.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['OUTDA'] + '.result.rows' },
    { name: 'targetDistId', path: '$.steps.' + initName + '.result.distributorId' }
  ],
  batches: [
    { field: 'accountBatches', label: 'Accounts' },
    { field: 'contactBatches', label: 'Contacts' }
  ]
});

// --- Phase 3: Inventory ---

// Pre-query existing Inventory records (for dedup workaround)
var invQueryName = nextStep('salesforce');
steps[invQueryName] = sfQuery(
  'Query Existing Inventory',
  "SELECT Id, ohfy__Item__r.VIP_External_ID__c FROM ohfy__Inventory__c WHERE ohfy__Item__r.VIP_External_ID__c LIKE 'ITM:%'"
);
structure.push({ name: invQueryName, type: 'normal', content: {} });

// Build existingInventoryMap from query results
var invMapScriptName = nextStep('script');
var INV_MAP_SCRIPT = [
  'exports.step = function(input, fileInput) {',
  '  var records = input.records || [];',
  '  var map = {};',
  '  for (var i = 0; i < records.length; i++) {',
  '    var rec = records[i];',
  '    var itemRef = rec.ohfy__Item__r;',
  '    if (itemRef && itemRef.VIP_External_ID__c) {',
  '      map[itemRef.VIP_External_ID__c] = rec.Id;',
  '    }',
  '  }',
  '  return { existingInventoryMap: map, count: Object.keys(map).length };',
  '};'
].join('\n');
steps[invMapScriptName] = scriptStep(
  'Build Inventory Map',
  [scriptVar('records', '$.steps.' + invQueryName + '.response.body.records')],
  INV_MAP_SCRIPT
);
structure.push({ name: invMapScriptName, type: 'normal', content: {} });

// Script 06 — INVDA → Inventory + History + Adjustments
addTransformPhase({
  title: '06 — Inventory',
  scriptFile: '06-invda-inventory.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['INVDA'] + '.result.rows' },
    { name: 'targetDistId', path: '$.steps.' + initName + '.result.distributorId' },
    { name: 'fileDate', path: '$.steps.' + initName + '.result.fileDate' },
    { name: 'existingInventoryMap', path: '$.steps.' + invMapScriptName + '.result.existingInventoryMap' }
  ],
  batches: [
    { field: 'inventoryBatches', label: 'Inventory' },
    { field: 'historyBatches', label: 'Inventory History' },
    { field: 'adjustmentBatches', label: 'Inventory Adjustments' }
  ]
});

// --- Phase 4: Transactions ---

// Script 07 — SLSDA → Depletions
var dep = addTransformPhase({
  title: '07 — Depletions',
  scriptFile: '07-slsda-depletions.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['SLSDA'] + '.result.rows' },
    { name: 'targetDistId', path: '$.steps.' + initName + '.result.distributorId' },
    { name: 'fileDate', path: '$.steps.' + initName + '.result.fileDate' }
  ],
  batches: [{ field: 'batches', label: 'Depletions' }]
});

// Script 07b — SLSDA → Placements
addTransformPhase({
  title: '07b — Placements',
  scriptFile: '07b-slsda-placements.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['SLSDA'] + '.result.rows' },
    { name: 'targetDistId', path: '$.steps.' + initName + '.result.distributorId' },
    { name: 'fileDate', path: '$.steps.' + initName + '.result.fileDate' }
  ],
  batches: [{ field: 'batches', label: 'Placements' }]
});

// Script 08 — CTLDA → Allocations
addTransformPhase({
  title: '08 — Allocations',
  scriptFile: '08-ctlda-allocations.tray.js',
  variables: [
    { name: 'rows', path: '$.steps.' + csvStepNames['CTLDA'] + '.result.rows' },
    { name: 'targetDistId', path: '$.steps.' + initName + '.result.distributorId' },
    { name: 'fileDate', path: '$.steps.' + initName + '.result.fileDate' }
  ],
  batches: [{ field: 'batches', label: 'Allocations' }]
});

// --- Cleanup (Script 09) — generates SOQL queries, no execution ---
var cleanupName = nextStep('script');
steps[cleanupName] = scriptStep(
  '09 — Cleanup Queries',
  [
    scriptVar('targetDistId', '$.steps.' + initName + '.result.distributorId'),
    scriptVar('fileDate', '$.steps.' + initName + '.result.fileDate')
  ],
  readScript('09-cleanup-stale.tray.js')
);
structure.push({ name: cleanupName, type: 'normal', content: {} });

// --- Summary (Script 10) ---
var summaryName = nextStep('script');
// The summary script needs results from all prior scripts
// We'll pass a placeholder — user needs to wire the actual result references after import
// since we can't predict all step names ahead of time in a clean way.
// Actually, we CAN reference them because we know the step names.

// Collect the script step names for each transform
// We need to find which script-N corresponds to each transform
// Let me just compute this from our known naming

var SUMMARY_WIRING_SCRIPT = [
  'exports.step = function(input, fileInput) {',
  '  // This step aggregates results from all transform scripts.',
  '  // Each input.X is the .result from the corresponding script step.',
  '  var results = {',
  '    chains: { recordCount: (input.chains || {}).recordCount || 0, errorCount: (input.chains || {}).errorCount || 0, skippedCount: (input.chains || {}).skippedCount || 0 },',
  '    items: { recordCount: (input.items || {}).recordCount || 0, errorCount: (input.items || {}).errorCount || 0, skippedCount: (input.items || {}).skippedCount || 0 },',
  '    locations: { recordCount: (input.locations || {}).recordCount || 0, errorCount: (input.locations || {}).errorCount || 0, skippedCount: (input.locations || {}).skippedCount || 0 },',
  '    enrichment: { recordCount: (input.enrichment || {}).recordCount || 0, errorCount: (input.enrichment || {}).errorCount || 0, skippedCount: (input.enrichment || {}).skippedCount || 0 },',
  '    accounts: { recordCount: (input.accounts || {}).accountCount || 0, errorCount: (input.accounts || {}).errorCount || 0, skippedCount: (input.accounts || {}).skippedCount || 0 },',
  '    contacts: { recordCount: (input.accounts || {}).contactCount || 0, errorCount: 0, skippedCount: 0 },',
  '    inventory: { recordCount: (input.inventory || {}).inventoryCount || 0, errorCount: (input.inventory || {}).errorCount || 0, skippedCount: (input.inventory || {}).skippedCount || 0 },',
  '    history: { recordCount: (input.inventory || {}).historyCount || 0, errorCount: 0, skippedCount: 0 },',
  '    adjustments: { recordCount: (input.inventory || {}).adjustmentCount || 0, errorCount: 0, skippedCount: 0 },',
  '    depletions: { recordCount: (input.depletions || {}).recordCount || 0, errorCount: (input.depletions || {}).errorCount || 0, skippedCount: (input.depletions || {}).skippedCount || 0 },',
  '    placements: { recordCount: (input.placements || {}).recordCount || 0, errorCount: (input.placements || {}).errorCount || 0, skippedCount: (input.placements || {}).skippedCount || 0 },',
  '    allocations: { recordCount: (input.allocations || {}).recordCount || 0, errorCount: (input.allocations || {}).errorCount || 0, skippedCount: (input.allocations || {}).skippedCount || 0 }',
  '  };',
  '  return require("./10-run-summary-inline.js").step({ results: results, targetDistId: input.distId, fileDate: input.fileDate });',
  '};'
].join('\n');

// Actually, we can't use require() in Tray. Let me just use the inlined 10-run-summary script directly
// but we need to pass the results object. The 10-run-summary script expects input.results.
// Let me build a wrapper that collects results and calls the summary logic.

// Read the summary script
var summaryScriptContent = readScript('10-run-summary.tray.js');

// We need to know which script steps correspond to which transforms.
// From the counters, script-1 = init, script-2..9 = CSV parse,
// script-10 = chains, script-11 = items, script-12 = locations,
// script-13 = enrichment, script-14 = accounts, script-15 = inv map,
// script-16 = inventory, script-17 = depletions, script-18 = placements,
// script-19 = allocations, script-20 = cleanup

// Summary step: pass all results as variables
steps[summaryName] = scriptStep(
  '10 — Run Summary',
  [
    scriptVar('chains', '$.steps.script-10.result'),
    scriptVar('items', '$.steps.script-11.result'),
    scriptVar('locations', '$.steps.script-12.result'),
    scriptVar('enrichment', '$.steps.script-13.result'),
    scriptVar('accounts', '$.steps.script-14.result'),
    scriptVar('inventory', '$.steps.script-16.result'),
    scriptVar('depletions', '$.steps.script-17.result'),
    scriptVar('placements', '$.steps.script-18.result'),
    scriptVar('allocations', '$.steps.script-19.result'),
    scriptVar('distId', '$.steps.' + initName + '.result.distributorId'),
    scriptVar('fileDate', '$.steps.' + initName + '.result.fileDate')
  ],
  summaryScriptContent
);
structure.push({ name: summaryName, type: 'normal', content: {} });

// --- Slack Notification ---
var notifyScriptName = nextStep('script');
steps[notifyScriptName] = scriptStep(
  'Format Slack Message',
  [scriptVar('summary', '$.steps.' + summaryName + '.result')],
  NOTIFICATION_SCRIPT
);
structure.push({ name: notifyScriptName, type: 'normal', content: {} });

var slackName = nextStep('slack');
steps[slackName] = slackMessage(
  'Slack — Pipeline Summary',
  SLACK_CHANNEL,
  '$.steps.' + notifyScriptName + '.result.message'
);
structure.push({ name: slackName, type: 'normal', content: {} });

// ============================================================================
// Build the error handler workflow
// ============================================================================

var errorSteps = {};
var errorStructure = [];

errorSteps['trigger'] = triggerAlerting();
errorStructure.push({ name: 'trigger', type: 'normal', content: {} });

var errScriptName = 'script-1';
errorSteps[errScriptName] = scriptStep(
  'Format Error Message',
  [scriptVar('error', '$.steps.trigger.results')],
  ERROR_HANDLER_SCRIPT
);
errorStructure.push({ name: errScriptName, type: 'normal', content: {} });

var errSlackName = 'slack-1';
errorSteps[errSlackName] = slackMessage(
  'Slack — Error Alert',
  SLACK_CHANNEL,
  '$.steps.' + errScriptName + '.result.message'
);
errorStructure.push({ name: errSlackName, type: 'normal', content: {} });

// ============================================================================
// Assemble project JSON
// ============================================================================

var projectId = uuid();
var mainWfId = uuid();
var errorWfId = uuid();
var now = new Date().toISOString().replace(/\.\d{3}Z$/, '.000000Z');

var project = {
  tray_export_version: 4,
  export_type: 'project',
  workflows: [
    {
      id: mainWfId,
      created: now,
      workspace_id: WORKSPACE_ID,
      project_id: projectId,
      group: uuid(),
      creator: WORKSPACE_ID,
      version: { id: uuid(), created: now },
      title: 'VIP SRS — Daily Pipeline',
      description: 'Daily SFTP-to-Salesforce sync for VIP beverage distribution data. Downloads 8 CSV files, transforms through 11 scripts, loads to 14 SF objects via Composite API.',
      enabled: true,
      tags: [],
      settings: {
        config: {
          distributorId: DIST_ID,
          supplierCode: SUPPLIER_CODE,
          sfApiVersion: SF_API_VERSION,
          sftpBasePath: SFTP_BASE_PATH
        },
        alerting_workflow_id: errorWfId,
        input_schema: {},
        output_schema: {}
      },
      steps_structure: structure,
      steps: steps,
      legacy_error_handling: false,
      dependencies: []
    },
    {
      id: errorWfId,
      created: now,
      workspace_id: WORKSPACE_ID,
      project_id: projectId,
      group: uuid(),
      creator: WORKSPACE_ID,
      version: { id: uuid(), created: now },
      title: 'VIP SRS — Error Handler',
      description: 'Sends Slack DM to Daniel when the pipeline errors.',
      enabled: true,
      tags: [],
      settings: {
        config: {},
        input_schema: {},
        output_schema: {}
      },
      steps_structure: errorStructure,
      steps: errorSteps,
      legacy_error_handling: false,
      dependencies: []
    }
  ],
  projects: [
    {
      id: projectId,
      version: null,
      name: 'VIP SRS Supplier — Shipyard ROS2',
      config: {
        distributorId: DIST_ID,
        supplierCode: SUPPLIER_CODE
      },
      workflows: [mainWfId, errorWfId],
      dependencies: [],
      installation_source_id: null,
      installation_version_id: null
    }
  ],
  data_tables: [],
  vector_tables: [],
  agents: [],
  apim_operations: []
};

// ============================================================================
// Validate
// ============================================================================

var issues = [];

project.workflows.forEach(function(w) {
  var structNames = [];
  function collectNames(arr) {
    arr.forEach(function(s) {
      structNames.push(s.name);
      if (s.content) {
        if (s.content._loop) collectNames(s.content._loop);
        if (s.content['true']) collectNames(s.content['true']);
        if (s.content['false']) collectNames(s.content['false']);
        if (s.content['error']) collectNames(s.content['error']);
        if (s.content['success']) collectNames(s.content['success']);
      }
    });
  }
  collectNames(w.steps_structure);
  var stepKeys = Object.keys(w.steps);

  structNames.forEach(function(n) {
    if (stepKeys.indexOf(n) === -1) issues.push(w.title + ': "' + n + '" in structure but not in steps');
  });
  stepKeys.forEach(function(n) {
    if (structNames.indexOf(n) === -1) issues.push(w.title + ': "' + n + '" in steps but not in structure');
  });

  // Check connector names
  stepKeys.forEach(function(sn) {
    var c = w.steps[sn].connector;
    if (c && ['sftp', 'http-client', 'tray-io-workflow-trigger', 'manual'].indexOf(c.name) !== -1) {
      issues.push(w.title + '/' + sn + ': invalid connector ' + c.name);
    }
  });

  // Check all values in properties are typed
  stepKeys.forEach(function(sn) {
    var props = w.steps[sn].properties;
    Object.keys(props).forEach(function(pk) {
      var v = props[pk];
      if (v && typeof v === 'object' && !v.type) {
        issues.push(w.title + '/' + sn + '.' + pk + ': missing type wrapper');
      }
    });
  });
});

// Connector summary
var connSummary = {};
project.workflows.forEach(function(w) {
  Object.keys(w.steps).forEach(function(sn) {
    var c = w.steps[sn].connector;
    if (c) {
      var k = c.name + '@' + c.version;
      connSummary[k] = (connSummary[k] || 0) + 1;
    }
  });
});

// ============================================================================
// Output
// ============================================================================

var json = JSON.stringify(project, null, 2);
var sizeKB = Math.round(Buffer.byteLength(json) / 1024);

console.log('=== VIP SRS Tray Project Generator ===\n');
console.log('Workflows: ' + project.workflows.length);
project.workflows.forEach(function(w) {
  console.log('  ' + w.title + ' (' + Object.keys(w.steps).length + ' steps)');
});
console.log('\nConnectors:');
Object.keys(connSummary).sort().forEach(function(k) {
  console.log('  ' + k + ' (' + connSummary[k] + ')');
});
console.log('\nSize: ' + sizeKB + ' KB');

if (issues.length) {
  console.log('\nERRORS (' + issues.length + '):');
  issues.forEach(function(i) { console.log('  ' + i); });
  process.exit(1);
} else {
  console.log('\nAll validation checks passed.');
}

// Write to artifacts repo
if (!fs.existsSync(ARTIFACTS_DIR)) {
  fs.mkdirSync(ARTIFACTS_DIR, { recursive: true });
}
var outPath = path.join(ARTIFACTS_DIR, 'project-export.json');
fs.writeFileSync(outPath, json);
console.log('\nWritten to: ' + outPath);
