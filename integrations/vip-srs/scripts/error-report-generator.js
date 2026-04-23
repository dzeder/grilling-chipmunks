/**
 * Error Report Generator — VIP SRS nightly load
 *
 * Reads a per-day runner JSON (produced by nightly-burst.js) and writes a
 * plain-English markdown report suitable for a non-engineering audience.
 *
 * Input:  .../logs/nightly-burst-<date>/day-N_<YYYY-MM-DD>.json
 * Output: .../logs/nightly-burst-<date>/day-N_<YYYY-MM-DD>_report.md
 *
 * Usage (standalone):
 *   node error-report-generator.js <path/to/day-N.json>
 *
 * Usage (library):
 *   const { generateReport } = require('./error-report-generator');
 *   generateReport(dayJsonPath);
 */

var fs = require('fs');
var path = require('path');

// Classify a raw Salesforce error message into a human-friendly bucket.
// Returns: { key, label, impact, action, severity }
function classifyError(step, rawMessage) {
  var msg = rawMessage || '';
  var statusCode = 'UNKNOWN';
  var detailMessage = msg;
  try {
    var parsed = JSON.parse(msg);
    if (Array.isArray(parsed) && parsed[0]) {
      statusCode = parsed[0].statusCode || 'UNKNOWN';
      detailMessage = parsed[0].message || msg;
    }
  } catch (_) {
    // keep raw
  }

  if (statusCode === 'DUPLICATE_VALUE') {
    return {
      key: 'duplicate_in_batch',
      label: 'Same record appeared twice in one batch',
      impact: 'None — the system kept the latest version and the record loaded successfully on retry.',
      action: 'No action needed. The distributor file occasionally restates the same row.',
      severity: 'info',
      statusCode: statusCode,
      detail: detailMessage
    };
  }

  if (statusCode === 'FIELD_CUSTOM_VALIDATION_EXCEPTION') {
    if (/Stock UOM Sub Type|Packaging_Type/i.test(detailMessage)) {
      return {
        key: 'item_missing_packaging',
        label: 'Finished Good item missing packaging type',
        impact: 'This item did NOT load. Depletions/inventory for it will fail until the item is created.',
        action: 'Usually self-healing: the item will load correctly once it appears in the supplier catalog (ITM2DA file). If it persists > 1 day, ask Shipyard/VIP whether the item should exist.',
        severity: 'warning',
        statusCode: statusCode,
        detail: detailMessage
      };
    }
    if (/Duplicate Record Blocked/i.test(detailMessage)) {
      return {
        key: 'inventory_blocked_by_duplicate',
        label: 'Inventory already exists for this Item + Location',
        impact: 'This Inventory row did NOT load. Salesforce has a separate Inventory record for the same Item + Location combination.',
        action: 'Engineering review — the pre-sync scan missed this existing record. Safe to ignore if counts look right.',
        severity: 'warning',
        statusCode: statusCode,
        detail: detailMessage
      };
    }
    return {
      key: 'salesforce_validation',
      label: 'Salesforce validation rule rejected the record',
      impact: 'The record did NOT load. Downstream data referencing it may be incomplete.',
      action: 'See the detailed error below. If unclear, share with the integration team.',
      severity: 'error',
      statusCode: statusCode,
      detail: detailMessage
    };
  }

  if (statusCode === 'INVALID_FIELD' && /Foreign key external ID/i.test(detailMessage)) {
    var fkMatch = detailMessage.match(/Foreign key external ID: ([^\s]+) not found/);
    var fk = fkMatch ? fkMatch[1] : '(unknown)';
    return {
      key: 'missing_parent_record',
      label: 'Referenced parent record does not exist yet',
      impact: 'This row did NOT load because it references "' + fk + '" which has not been created.',
      action: 'Usually self-healing on the next load once the parent record exists. If persistent, check why the parent item/inventory is missing.',
      severity: 'warning',
      statusCode: statusCode,
      detail: detailMessage
    };
  }

  if (statusCode === 'ENTITY_IS_DELETED') {
    return {
      key: 'record_deleted_mid_run',
      label: 'Record was deleted during the load',
      impact: 'None — the record was already cleaned up.',
      action: 'No action needed.',
      severity: 'info',
      statusCode: statusCode,
      detail: detailMessage
    };
  }

  if (statusCode === 'INSUFFICIENT_ACCESS_OR_READONLY') {
    return {
      key: 'permission_error',
      label: 'Permission issue',
      impact: 'Record did NOT load because the integration user lacks permission.',
      action: 'Ask a Salesforce admin to grant the integration user access.',
      severity: 'error',
      statusCode: statusCode,
      detail: detailMessage
    };
  }

  if (/AccountTriggerMethods/i.test(detailMessage) || /ServiceLocator/i.test(detailMessage)) {
    return {
      key: 'account_trigger_methods',
      label: 'Salesforce managed-package trigger error (AccountTriggerMethods)',
      impact: 'Account update failed. The underlying integration is blocked until the managed package is fixed.',
      action: 'Known blocker — tracked by Ohanafy engineering. Workaround (CMDT trigger bypass) is already in place during bulk loads.',
      severity: 'error',
      statusCode: statusCode,
      detail: detailMessage
    };
  }

  return {
    key: 'other_' + statusCode.toLowerCase(),
    label: 'Other Salesforce error (' + statusCode + ')',
    impact: 'Record did NOT load.',
    action: 'Share the detail below with the integration team.',
    severity: 'error',
    statusCode: statusCode,
    detail: detailMessage
  };
}

function pct(n, d) {
  if (!d) return '0%';
  return Math.round((n / d) * 1000) / 10 + '%';
}

function formatNumber(n) {
  return (n || 0).toLocaleString('en-US');
}

function generateReport(dayJsonPath, outputPath) {
  var day = JSON.parse(fs.readFileSync(dayJsonPath, 'utf8'));
  var out = outputPath || dayJsonPath.replace(/\.json$/, '_report.md');

  var errors = day.pipelineErrors || [];
  var txn = day.transactionLog || {};
  var cleanup = day.staleCleanup || {};
  var pre = (day.snapshotBefore && day.snapshotBefore.objects) || {};
  var post = (day.snapshotAfter && day.snapshotAfter.objects) || {};

  // Classify every error
  var buckets = {};
  errors.forEach(function(e) {
    var c = classifyError(e.step, e.message);
    var key = c.key;
    if (!buckets[key]) {
      buckets[key] = {
        label: c.label,
        impact: c.impact,
        action: c.action,
        severity: c.severity,
        statusCode: c.statusCode,
        count: 0,
        bySteps: {},
        examples: []
      };
    }
    buckets[key].count++;
    buckets[key].bySteps[e.step] = (buckets[key].bySteps[e.step] || 0) + 1;
    if (buckets[key].examples.length < 3) {
      buckets[key].examples.push({
        step: e.step,
        message: c.detail
      });
    }
  });

  // Totals
  var totalAdded = 0, totalUpdated = 0, totalFailed = errors.length;
  var perObject = [];
  Object.keys(txn).forEach(function(step) {
    var t = txn[step];
    var added = t.added || 0;
    var updated = t.updated || 0;
    var failed = t.failed || 0;
    totalAdded += added;
    totalUpdated += updated;
    if (added || updated || failed) {
      perObject.push({ step: step, added: added, updated: updated, failed: failed });
    }
  });

  var totalCleanupDeleted = 0;
  var cleanupPerObject = [];
  Object.keys(cleanup.perObject || {}).forEach(function(obj) {
    var c = cleanup.perObject[obj];
    totalCleanupDeleted += (c.deleted || 0);
    cleanupPerObject.push({ object: obj, deleted: c.deleted || 0, failed: c.failed || 0 });
  });

  // Overall status
  var errorBuckets = Object.keys(buckets);
  var status;
  if (errors.length === 0) status = 'OK — everything loaded cleanly';
  else if (errorBuckets.every(function(k) { return buckets[k].severity === 'info'; })) status = 'OK — all issues were handled automatically';
  else if (errorBuckets.some(function(k) { return buckets[k].severity === 'error'; })) status = 'Attention needed — some records did not load';
  else status = 'Partial — minor issues, most records loaded';

  // Build markdown
  var md = [];
  md.push('# Daily Data Load Report — ' + (day.fileDate || 'unknown date'));
  md.push('');
  md.push('_Generated ' + new Date().toISOString() + ' from ' + path.basename(dayJsonPath) + '_');
  md.push('');
  md.push('## Summary');
  md.push('');
  md.push('**Status:** ' + status);
  md.push('');
  md.push('- **Records added:** ' + formatNumber(totalAdded));
  md.push('- **Records updated:** ' + formatNumber(totalUpdated));
  md.push('- **Records deleted (cleanup):** ' + formatNumber(totalCleanupDeleted));
  md.push('- **Records with issues:** ' + formatNumber(totalFailed));
  md.push('- **Run duration:** ' + (day.runDurationSec || '?') + 's');
  md.push('');

  // Record counts before/after — iterate the union of keys present in either snapshot
  var haveSnapshots = Object.keys(pre).length > 0 && Object.keys(post).length > 0;
  if (haveSnapshots) {
    md.push('## Record counts (before → after)');
    md.push('');
    md.push('| Object | Before | After | Change |');
    md.push('|--------|-------:|------:|-------:|');
    var seenKeys = {};
    Object.keys(pre).concat(Object.keys(post)).forEach(function(k) { seenKeys[k] = true; });
    Object.keys(seenKeys).sort().forEach(function(key) {
      var bObj = pre[key] || {};
      var aObj = post[key] || {};
      var displayName = aObj.displayName || bObj.displayName || key;
      var b = (bObj.count != null) ? bObj.count : null;
      var a = (aObj.count != null) ? aObj.count : null;
      if (b === null && a === null) return;
      var delta = (a || 0) - (b || 0);
      if (delta === 0) return; // only show rows that changed
      var arrow = delta > 0 ? '+' : '';
      md.push('| ' + displayName + ' | ' + formatNumber(b) + ' | ' + formatNumber(a) + ' | ' + arrow + formatNumber(delta) + ' |');
    });
    md.push('');
  }

  // What loaded
  if (perObject.length) {
    md.push('## What loaded');
    md.push('');
    md.push('| Data type | Added | Updated | Had issues |');
    md.push('|-----------|------:|--------:|-----------:|');
    perObject.forEach(function(p) {
      md.push('| ' + p.step + ' | ' + formatNumber(p.added) + ' | ' + formatNumber(p.updated) + ' | ' + formatNumber(p.failed) + ' |');
    });
    md.push('');
  }

  // Cleanup
  if (cleanupPerObject.length) {
    md.push('## What got cleaned up');
    md.push('');
    md.push('Records deleted because they were no longer in the distributor\'s current reporting window:');
    md.push('');
    md.push('| Data type | Deleted | Failed to delete |');
    md.push('|-----------|--------:|-----------------:|');
    cleanupPerObject.forEach(function(c) {
      md.push('| ' + c.object + ' | ' + formatNumber(c.deleted) + ' | ' + formatNumber(c.failed) + ' |');
    });
    md.push('');
  }

  // Issues
  if (errorBuckets.length === 0) {
    md.push('## Issues');
    md.push('');
    md.push('None. All records loaded successfully.');
    md.push('');
  } else {
    md.push('## Issues you should know about');
    md.push('');
    md.push('_' + errors.length + ' records had issues. They are grouped below by type, with plain-English explanations._');
    md.push('');
    // Sort: error > warning > info, then by count desc
    var sevOrder = { error: 0, warning: 1, info: 2 };
    var keys = errorBuckets.sort(function(a, b) {
      var sa = sevOrder[buckets[a].severity] || 3;
      var sb = sevOrder[buckets[b].severity] || 3;
      if (sa !== sb) return sa - sb;
      return buckets[b].count - buckets[a].count;
    });
    keys.forEach(function(k, idx) {
      var b = buckets[k];
      var sevLabel = { error: 'NEEDS ATTENTION', warning: 'REVIEW', info: 'FYI' }[b.severity] || 'FYI';
      md.push('### ' + (idx + 1) + '. ' + b.label + '  \u2014  `' + sevLabel + '` (' + b.count + ' records)');
      md.push('');
      md.push('- **What happened:** Salesforce returned `' + b.statusCode + '`. ' + pct(b.count, errors.length) + ' of all issues today.');
      var stepKeys = Object.keys(b.bySteps);
      if (stepKeys.length) {
        md.push('- **Where:** ' + stepKeys.map(function(s) { return s + ' (' + b.bySteps[s] + ')'; }).join(', '));
      }
      md.push('- **Impact:** ' + b.impact);
      md.push('- **Recommended action:** ' + b.action);
      if (b.examples.length) {
        md.push('- **Examples:**');
        b.examples.forEach(function(ex) {
          md.push('    - `' + ex.step + '` — ' + (ex.message || '').substring(0, 220));
        });
      }
      md.push('');
    });
  }

  // Glossary
  md.push('## Glossary');
  md.push('');
  md.push('- **Added** — Salesforce record did not exist; we created it.');
  md.push('- **Updated** — Salesforce record already existed; we refreshed its fields.');
  md.push('- **Deleted (cleanup)** — Record is no longer in the distributor\'s current reporting window, so we removed it to keep the data in sync.');
  md.push('- **Had issues** — One or more records could not be saved. See "Issues" above.');
  md.push('');

  fs.writeFileSync(out, md.join('\n'));
  return out;
}

module.exports = { generateReport: generateReport, classifyError: classifyError };

// CLI
if (require.main === module) {
  var arg = process.argv[2];
  if (!arg) {
    console.error('Usage: node error-report-generator.js <path/to/day-N.json>');
    process.exit(1);
  }
  var written = generateReport(arg);
  console.log('Wrote report: ' + written);
}
