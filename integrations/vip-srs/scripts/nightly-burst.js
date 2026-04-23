#!/usr/bin/env node
/**
 * Nightly Burst Orchestrator — VIP SRS
 *
 * Simulates N consecutive nightly production loads by looping chronologically
 * over VIP SFTP files. For each day:
 *   1. Download the day's files
 *   2. Snapshot sandbox (before)
 *   3. Run e2e-sandbox-runner full pipeline
 *   4. Execute stale cleanup (per-distributor Script 09 SOQL → delete)
 *   5. Snapshot sandbox (after)
 *   6. Write per-day transaction log (JSON + MD)
 *
 * Usage:
 *   node nightly-burst.js --start 2026-04-15 --end 2026-04-22 --out-dir logs/nightly-burst-2026-04-22/
 *   node nightly-burst.js --dates 2026-04-15,2026-04-16,2026-04-17 --out-dir logs/...
 *
 * Flags:
 *   --start YYYY-MM-DD       inclusive start date
 *   --end YYYY-MM-DD         inclusive end date (weekends auto-skipped)
 *   --dates a,b,c            explicit comma-separated date list (overrides start/end)
 *   --out-dir DIR            output directory for logs
 *   --target-org ALIAS       SF org alias (default: from config)
 *   --distributors CSV       distributor IDs for cleanup (default: FL01,FL02,FL03,FL04,FL05,FL06,FL07,MA01,MA02,MA03,MA04,MA05)
 *   --skip-download          assume data already downloaded
 *   --skip-cleanup           skip the stale cleanup step
 *   --dry-run                pass --dry-run to the runner (no DML)
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
var SCRIPTS_DIR = __dirname;
var VIP_SRS_ROOT = path.resolve(SCRIPTS_DIR, '..');

var args = process.argv.slice(2);
var START_DATE = '';
var END_DATE = '';
var EXPLICIT_DATES = '';
var OUT_DIR = '';
var DISTRIBUTORS = 'FL01,FL02,FL03,FL04,FL05,FL06,FL07,MA01,MA02,MA03,MA04,MA05';
var SKIP_DOWNLOAD = false;
var SKIP_CLEANUP = false;
var DRY_RUN = false;

for (var i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--start': START_DATE = args[++i]; break;
    case '--end': END_DATE = args[++i]; break;
    case '--dates': EXPLICIT_DATES = args[++i]; break;
    case '--out-dir': OUT_DIR = args[++i]; break;
    case '--target-org': TARGET_ORG = args[++i]; break;
    case '--distributors': DISTRIBUTORS = args[++i]; break;
    case '--skip-download': SKIP_DOWNLOAD = true; break;
    case '--skip-cleanup': SKIP_CLEANUP = true; break;
    case '--dry-run': DRY_RUN = true; break;
    case '--config': i++; break;
    case '--help': case '-h':
      console.log('Usage: node nightly-burst.js --start YYYY-MM-DD --end YYYY-MM-DD --out-dir DIR [flags]');
      process.exit(0);
  }
}

if (!OUT_DIR) {
  console.error('ERROR: --out-dir is required');
  process.exit(1);
}

// =============================================================================
// DATE UTILS
// =============================================================================

function isWeekday(ymd) {
  var d = new Date(ymd + 'T12:00:00Z');
  var dow = d.getUTCDay();
  return dow >= 1 && dow <= 5;
}

function enumerateDates(start, end) {
  var dates = [];
  var cur = new Date(start + 'T12:00:00Z');
  var endD = new Date(end + 'T12:00:00Z');
  while (cur.getTime() <= endD.getTime()) {
    var ymd = cur.toISOString().substring(0, 10);
    if (isWeekday(ymd)) dates.push(ymd);
    cur.setUTCDate(cur.getUTCDate() + 1);
  }
  return dates;
}

var BURST_DATES;
if (EXPLICIT_DATES) {
  BURST_DATES = EXPLICIT_DATES.split(',').map(function(s) { return s.trim(); });
} else if (START_DATE && END_DATE) {
  BURST_DATES = enumerateDates(START_DATE, END_DATE);
} else {
  console.error('ERROR: Provide --start/--end or --dates');
  process.exit(1);
}

// =============================================================================
// PATHS
// =============================================================================

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

function run(cmd, opts) {
  opts = opts || {};
  console.log('$ ' + cmd);
  try {
    var out = execSync(cmd, {
      cwd: VIP_SRS_ROOT,
      encoding: 'utf8',
      stdio: opts.silent ? ['inherit', 'pipe', 'pipe'] : 'inherit',
      maxBuffer: 100 * 1024 * 1024,
      timeout: opts.timeout || (20 * 60 * 1000) // 20 min default
    });
    return { ok: true, output: out || '' };
  } catch (e) {
    return { ok: false, output: (e.stdout || '') + (e.stderr || ''), error: e.message };
  }
}

// =============================================================================
// STALE CLEANUP EXECUTOR
// =============================================================================
// Runs Script 09 per-distributor, executes SOQL, deletes returned IDs.
// Uses --use-tooling-api=false; deletes via `sf data delete record` in chunks.

var cleanupStaleScript = require('./09-cleanup-stale.js');

function sfQueryIds(soql) {
  try {
    var out = execSync(
      'sf data query --target-org ' + TARGET_ORG + ' --query "' + soql + '" --result-format json 2>/dev/null',
      { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024, timeout: 60000 }
    );
    var parsed = JSON.parse(out);
    var records = (parsed.result && parsed.result.records) || [];
    return records.map(function(r) { return r.Id; });
  } catch (e) {
    return [];
  }
}

function sfDeleteBulk(sobject, ids) {
  if (!ids.length) return { deleted: 0, failed: 0 };
  // Write CSV for sf data delete bulk - CLI requires CRLF line endings on macOS.
  var csvPath = path.join(OUT_DIR, '.tmp-delete-' + sobject.replace(/[^a-z0-9]/gi, '_') + '.csv');
  var csv = 'Id\r\n' + ids.join('\r\n') + '\r\n';
  fs.writeFileSync(csvPath, csv);
  try {
    execSync(
      'sf data delete bulk --target-org ' + TARGET_ORG + ' --sobject ' + sobject +
      ' --file ' + csvPath + ' --line-ending CRLF --wait 20 2>&1',
      { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024, timeout: 25 * 60 * 1000 }
    );
    fs.unlinkSync(csvPath);
    return { deleted: ids.length, failed: 0 };
  } catch (e) {
    var errOut = (e.stdout || '') + (e.stderr || '');
    if (fs.existsSync(csvPath)) fs.unlinkSync(csvPath);
    return { deleted: 0, failed: ids.length, error: errOut.substring(0, 500) };
  }
}

function runStaleCleanup(fileDate) {
  if (SKIP_CLEANUP) {
    return { skipped: true };
  }
  var distIds = DISTRIBUTORS.split(',').map(function(s) { return s.trim(); });
  var perObjectTotals = {};
  var seenGlobalSoql = {}; // dedupe global (non-per-dist) queries

  function addResult(sobject, ids, deleteResult) {
    if (!perObjectTotals[sobject]) {
      perObjectTotals[sobject] = { deleted: 0, failed: 0, examples: [] };
    }
    perObjectTotals[sobject].deleted += deleteResult.deleted;
    perObjectTotals[sobject].failed += deleteResult.failed;
    if (perObjectTotals[sobject].examples.length < 3) {
      var remaining = 3 - perObjectTotals[sobject].examples.length;
      perObjectTotals[sobject].examples = perObjectTotals[sobject].examples.concat(ids.slice(0, remaining));
    }
  }

  distIds.forEach(function(distId) {
    var out = cleanupStaleScript.step({
      targetDistId: distId,
      fileDate: fileDate,
      fromDate: fileDate,
      toDate: fileDate
    });
    if (!out.queries) return;
    out.queries.forEach(function(q) {
      var isPerDist = q.soql.indexOf(':' + distId + ':') > -1;
      if (!isPerDist) {
        // Global query — run only once across all distIds
        if (seenGlobalSoql[q.soql]) return;
        seenGlobalSoql[q.soql] = true;
      }
      var ids = sfQueryIds(q.soql);
      if (ids.length === 0) return;
      console.log('  ' + q.sobject + ' (' + distId + (isPerDist ? '' : '/global') + '): ' + ids.length + ' stale');
      var result = sfDeleteBulk(q.sobject, ids);
      addResult(q.sobject, ids, result);
    });
  });

  return { perObject: perObjectTotals };
}

// =============================================================================
// MARKDOWN RENDERER
// =============================================================================

function renderDayMarkdown(dayLog) {
  var md = '# Day ' + dayLog.dayIndex + ' — ' + dayLog.fileDate + '\n\n';
  md += '**Run:** ' + dayLog.runStartedAt + '  \n';
  md += '**Duration:** ' + dayLog.runDurationSec + 's  \n';
  md += '**Files loaded:** ' + (dayLog.filesLoaded || []).join(', ') + '  \n';
  md += '**Pipeline status:** ' + dayLog.pipelineStatus + '  \n\n';

  // Per-object table
  md += '## Transaction log\n\n';
  md += '| Label | Added | Updated | Deleted | Failed |\n';
  md += '|-------|------:|--------:|--------:|-------:|\n';
  var labels = Object.keys(dayLog.transactionLog || {}).sort();
  labels.forEach(function(label) {
    var t = dayLog.transactionLog[label];
    md += '| ' + label + ' | ' + t.added + ' | ' + t.updated + ' | ' + (t.deleted || 0) + ' | ' + t.failed + ' |\n';
  });

  // Stale cleanup table
  if (dayLog.staleCleanup && dayLog.staleCleanup.perObject) {
    md += '\n## Stale cleanup (deletes)\n\n';
    md += '| Object | Deleted | Failed | Example IDs |\n';
    md += '|--------|--------:|-------:|-------------|\n';
    Object.keys(dayLog.staleCleanup.perObject).forEach(function(obj) {
      var c = dayLog.staleCleanup.perObject[obj];
      md += '| ' + obj + ' | ' + c.deleted + ' | ' + c.failed + ' | ' + (c.examples || []).join(', ') + ' |\n';
    });
  }

  // Examples section
  md += '\n## Example records per bucket\n\n';
  labels.forEach(function(label) {
    var t = dayLog.transactionLog[label];
    if ((t.added + t.updated + t.failed) === 0) return;
    md += '### ' + label + '\n\n';
    ['added', 'updated', 'failed'].forEach(function(bucket) {
      var examples = (t.examples || {})[bucket] || [];
      if (examples.length === 0) return;
      md += '**' + bucket.charAt(0).toUpperCase() + bucket.slice(1) + ':**\n\n';
      examples.forEach(function(ex) {
        md += '- `' + JSON.stringify(ex).substring(0, 400) + '`\n';
      });
      md += '\n';
    });
  });

  // Counts diff
  if (dayLog.snapshotBefore && dayLog.snapshotAfter) {
    md += '\n## Snapshot diff (before → after)\n\n';
    md += '| Object | Before | After | Δ |\n';
    md += '|--------|-------:|------:|--:|\n';
    var keys = Object.keys(dayLog.snapshotBefore.objects);
    keys.forEach(function(k) {
      var b = dayLog.snapshotBefore.objects[k].count;
      var a = (dayLog.snapshotAfter.objects[k] || {}).count || 0;
      var delta = a - b;
      md += '| ' + dayLog.snapshotBefore.objects[k].displayName + ' | ' + b + ' | ' + a +
            ' | ' + (delta >= 0 ? '+' : '') + delta + ' |\n';
    });
  }

  // Errors
  if (dayLog.pipelineErrors && dayLog.pipelineErrors.length > 0) {
    md += '\n## Errors (' + dayLog.pipelineErrors.length + ')\n\n';
    var errByCategory = {};
    dayLog.pipelineErrors.forEach(function(e) {
      errByCategory[e.category] = (errByCategory[e.category] || 0) + 1;
    });
    Object.keys(errByCategory).forEach(function(cat) {
      md += '- **' + cat + '**: ' + errByCategory[cat] + '\n';
    });
    md += '\nFirst 3 errors:\n\n';
    dayLog.pipelineErrors.slice(0, 3).forEach(function(e) {
      md += '- [' + e.category + '] ' + e.step + ': `' + e.message.substring(0, 200) + '`\n';
    });
  }

  return md;
}

// =============================================================================
// MAIN LOOP
// =============================================================================

console.log('============================================');
console.log('Nightly Burst Simulation');
console.log('============================================');
console.log('Target org:     ' + TARGET_ORG);
console.log('Days:           ' + BURST_DATES.join(', '));
console.log('Distributors:   ' + DISTRIBUTORS);
console.log('Out dir:        ' + OUT_DIR);
console.log('Skip download:  ' + SKIP_DOWNLOAD);
console.log('Skip cleanup:   ' + SKIP_CLEANUP);
console.log('Dry run:        ' + DRY_RUN);
console.log('============================================');
console.log('');

var allDayLogs = [];

for (var di = 0; di < BURST_DATES.length; di++) {
  var fileDate = BURST_DATES[di];
  var dayIndex = di + 1;
  var dayLog = {
    dayIndex: dayIndex,
    fileDate: fileDate,
    runStartedAt: new Date().toISOString()
  };
  var startMs = Date.now();

  console.log('\n========================================');
  console.log('Day ' + dayIndex + '/' + BURST_DATES.length + ': ' + fileDate);
  console.log('========================================');

  // 1. Download
  if (!SKIP_DOWNLOAD) {
    var dateArg = fileDate.replace(/-/g, ''); // YYYYMMDD
    var downloadResult = run('node scripts/download-vip-files.js --date ' + dateArg);
    dayLog.downloadOk = downloadResult.ok;
    if (!downloadResult.ok) {
      console.log('WARN: download reported errors for ' + fileDate);
    }
  }

  var dataDir = path.join(VIP_SRS_ROOT, 'data', fileDate);
  if (!fs.existsSync(dataDir)) {
    console.log('SKIP: no data dir ' + dataDir);
    dayLog.skipped = true;
    dayLog.skipReason = 'data dir missing';
    allDayLogs.push(dayLog);
    continue;
  }

  // 2. Snapshot before
  var beforeSnapPath = path.join(OUT_DIR, 'day-' + dayIndex + '_' + fileDate + '_before.json');
  run('node scripts/snapshot-sandbox.js --out ' + beforeSnapPath +
      ' --label "day-' + dayIndex + '-before" --target-org ' + TARGET_ORG + ' --dist-id ""');
  try { dayLog.snapshotBefore = JSON.parse(fs.readFileSync(beforeSnapPath, 'utf8')); } catch (_) {}

  // 3. Run pipeline
  var runnerJsonPath = path.join(OUT_DIR, 'day-' + dayIndex + '_' + fileDate + '_runner.json');
  var runnerCmd = 'node scripts/e2e-sandbox-runner.js' +
    ' --data-dir data/' + fileDate + '/' +
    ' --file-date ' + fileDate +
    ' --skip-contacts' +
    ' --dist-id ""' +
    ' --target-org ' + TARGET_ORG +
    ' --output-json ' + runnerJsonPath +
    (DRY_RUN ? ' --dry-run' : '');
  var runnerResult = run(runnerCmd);
  dayLog.pipelineStatus = runnerResult.ok ? 'success' : 'partial';

  if (fs.existsSync(runnerJsonPath)) {
    var runnerReport = JSON.parse(fs.readFileSync(runnerJsonPath, 'utf8'));
    dayLog.transactionLog = runnerReport.transactionLog || {};
    dayLog.pipelineErrors = runnerReport.errors || [];
    dayLog.pipelineSteps = runnerReport.summary.steps || [];
    dayLog.filesLoaded = dayLog.pipelineSteps.filter(function(s) { return s.status !== 'skipped'; })
      .map(function(s) { return s.name; });
  }

  // 4. Stale cleanup
  if (!SKIP_CLEANUP && !DRY_RUN) {
    console.log('-- Stale cleanup --');
    dayLog.staleCleanup = runStaleCleanup(fileDate);
    // Merge delete counts into transactionLog
    if (dayLog.staleCleanup.perObject) {
      Object.keys(dayLog.staleCleanup.perObject).forEach(function(obj) {
        var c = dayLog.staleCleanup.perObject[obj];
        var existing = dayLog.transactionLog[obj] || { added: 0, updated: 0, failed: 0, examples: { added: [], updated: [], failed: [] } };
        existing.deleted = (existing.deleted || 0) + c.deleted;
        existing.examples = existing.examples || { added: [], updated: [], failed: [] };
        existing.examples.deleted = c.examples || [];
        dayLog.transactionLog[obj] = existing;
      });
    }
  }

  // 5. Snapshot after
  var afterSnapPath = path.join(OUT_DIR, 'day-' + dayIndex + '_' + fileDate + '_after.json');
  run('node scripts/snapshot-sandbox.js --out ' + afterSnapPath +
      ' --label "day-' + dayIndex + '-after" --target-org ' + TARGET_ORG + ' --dist-id ""');
  try { dayLog.snapshotAfter = JSON.parse(fs.readFileSync(afterSnapPath, 'utf8')); } catch (_) {}

  dayLog.runDurationSec = Math.round((Date.now() - startMs) / 1000);

  // 6. Write day log JSON + MD
  var dayJsonPath = path.join(OUT_DIR, 'day-' + dayIndex + '_' + fileDate + '.json');
  fs.writeFileSync(dayJsonPath, JSON.stringify(dayLog, null, 2));
  var dayMdPath = path.join(OUT_DIR, 'day-' + dayIndex + '_' + fileDate + '.md');
  fs.writeFileSync(dayMdPath, renderDayMarkdown(dayLog));

  console.log('Written: ' + dayJsonPath);
  console.log('Written: ' + dayMdPath);

  // 7. Generate end-user-friendly error report
  try {
    var reportGen = require('./error-report-generator');
    var reportPath = reportGen.generateReport(dayJsonPath);
    console.log('Written: ' + reportPath);
  } catch (e) {
    console.log('WARN: error report generation failed: ' + e.message);
  }

  allDayLogs.push(dayLog);
}

// =============================================================================
// OVERALL INDEX (SUMMARY.md built separately after burst completes)
// =============================================================================

var indexPath = path.join(OUT_DIR, 'burst-index.json');
fs.writeFileSync(indexPath, JSON.stringify({
  days: allDayLogs.map(function(d) {
    return {
      dayIndex: d.dayIndex,
      fileDate: d.fileDate,
      status: d.pipelineStatus || (d.skipped ? 'skipped' : 'unknown'),
      durationSec: d.runDurationSec || 0
    };
  })
}, null, 2));

console.log('\n============================================');
console.log('Burst complete. Index: ' + indexPath);
console.log('============================================');
