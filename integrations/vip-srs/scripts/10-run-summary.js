/**
 * VIP SRS Script 10: Daily Run Summary
 *
 * Aggregates results from all prior scripts in a run into a single summary
 * object. Intended to be the final step in the Tray workflow, feeding into
 * alerting/notification connectors.
 *
 * Input: An object with result summaries from each prior script step.
 * Output: Unified summary with per-object counts and overall status.
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 9 (Pipeline Architecture)
 */

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var results = input.results || {};
  var distId = input.targetDistId || input.distributorId || '';
  var fileDate = input.fileDate || '';

  // Collect per-script summaries
  var scripts = [
    { name: '01-srschain', label: 'Chain Banners', key: 'chains' },
    { name: '02-itm2da', label: 'Items', key: 'items' },
    { name: '03-distda', label: 'Locations', key: 'locations' },
    { name: '04-itmda', label: 'Item Enrichment', key: 'enrichment' },
    { name: '05-outda-accounts', label: 'Accounts (Outlets)', key: 'accounts' },
    { name: '05-outda-contacts', label: 'Contacts (Buyers)', key: 'contacts' },
    { name: '06-invda-inventory', label: 'Inventory (Current)', key: 'inventory' },
    { name: '06-invda-history', label: 'Inventory History', key: 'history' },
    { name: '06-invda-adjustments', label: 'Inventory Adjustments', key: 'adjustments' },
    { name: '07-slsda-depletions', label: 'Depletions', key: 'depletions' },
    { name: '07b-slsda-placements', label: 'Placements', key: 'placements' },
    { name: '08-ctlda', label: 'Allocations', key: 'allocations' },
    { name: '09-cleanup', label: 'Stale Cleanup', key: 'cleanup' }
  ];

  var totalRecords = 0;
  var totalErrors = 0;
  var totalSkipped = 0;
  var hasFailures = false;
  var scriptSummaries = [];

  scripts.forEach(function(script) {
    var data = results[script.key];
    if (!data) {
      scriptSummaries.push({
        name: script.name,
        label: script.label,
        status: 'not_run',
        records: 0,
        errors: 0,
        skipped: 0
      });
      return;
    }

    var records = data.recordCount || data.records || data.count || 0;
    var errors = data.errorCount || data.errors || 0;
    var skippedCount = data.skippedCount || data.skipped || 0;

    totalRecords += records;
    totalErrors += errors;
    totalSkipped += skippedCount;
    if (errors > 0) hasFailures = true;

    scriptSummaries.push({
      name: script.name,
      label: script.label,
      status: errors > 0 ? 'partial' : 'success',
      records: records,
      errors: errors,
      skipped: skippedCount
    });
  });

  var overallStatus = 'success';
  if (hasFailures) overallStatus = 'partial';
  if (totalRecords === 0 && totalErrors > 0) overallStatus = 'failed';

  return {
    status: overallStatus,
    distId: distId,
    fileDate: fileDate,
    totalRecords: totalRecords,
    totalErrors: totalErrors,
    totalSkipped: totalSkipped,
    scripts: scriptSummaries,
    summary: {
      status: overallStatus,
      distId: distId,
      fileDate: fileDate,
      totalRecords: totalRecords,
      totalErrors: totalErrors,
      totalSkipped: totalSkipped,
      scriptCount: scriptSummaries.length,
      successCount: scriptSummaries.filter(function(s) { return s.status === 'success'; }).length,
      partialCount: scriptSummaries.filter(function(s) { return s.status === 'partial'; }).length,
      notRunCount: scriptSummaries.filter(function(s) { return s.status === 'not_run'; }).length,
      timestamp: new Date().toISOString()
    }
  };
};
