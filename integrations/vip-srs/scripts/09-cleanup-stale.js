/**
 * VIP SRS Script 09: Stale Record Cleanup
 *
 * Generates SOQL queries and delete batches for stale records from previous
 * VIP files within the same reporting period. After upserts complete for a
 * given file, records with an older VIP_File_Date__c in the same
 * From/To window are stale and must be deleted.
 *
 * This script does NOT execute queries — it produces the SOQL strings and
 * delete batch structure for the Tray workflow to execute via SF connector.
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 10
 */

// =============================================================================
// INLINE SHARED
// =============================================================================

var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 200, namespacePrefix: 'ohfy' };
var NS = SF_CONFIG.namespacePrefix + '__';

// =============================================================================
// CLEANUP CONFIG — which objects get stale cleanup
// =============================================================================

var CLEANUP_TARGETS = [
  {
    sobject: NS + 'Depletion__c',
    externalIdField: 'VIP_External_ID__c',
    prefix: 'DEP',
    fileDateField: 'VIP_File_Date__c',
    fromDateField: 'VIP_From_Date__c',
    toDateField: 'VIP_To_Date__c'
  },
  {
    sobject: NS + 'Placement__c',
    externalIdField: 'VIP_External_ID__c',
    prefix: 'PLC',
    fileDateField: 'VIP_File_Date__c',
    // Placement has no From/To date fields — one record per Account×Item,
    // rebuilt each run. Stale = older file date for this distributor.
    fromDateField: null,
    toDateField: null
  },
  {
    sobject: NS + 'Inventory_History__c',
    externalIdField: 'VIP_External_ID__c',
    prefix: 'IVH',
    fileDateField: 'VIP_File_Date__c',
    fromDateField: 'VIP_From_Date__c',
    toDateField: 'VIP_To_Date__c'
  },
  {
    sobject: NS + 'Inventory_Adjustment__c',
    externalIdField: 'VIP_External_ID__c',
    prefix: 'IVA',
    fileDateField: 'VIP_File_Date__c',
    fromDateField: 'VIP_From_Date__c',
    toDateField: 'VIP_To_Date__c'
  },
  {
    sobject: NS + 'Allocation__c',
    externalIdField: 'VIP_External_ID__c',
    prefix: 'ALC',
    fileDateField: 'VIP_File_Date__c',
    fromDateField: 'VIP_From_Date__c',
    toDateField: 'VIP_To_Date__c'
  }
];

// =============================================================================
// SOQL BUILDERS
// =============================================================================

function buildStaleQuery(target, distId, currentFileDate, fromDate, toDate) {
  var sql = 'SELECT Id FROM ' + target.sobject +
    ' WHERE ' + target.fileDateField + ' < ' + currentFileDate;
  if (target.fromDateField && target.toDateField) {
    sql += ' AND ' + target.fromDateField + ' >= ' + fromDate +
      ' AND ' + target.toDateField + ' <= ' + toDate;
  }
  sql += " AND " + target.externalIdField + " LIKE '" + target.prefix + ':' + distId + ":%'";
  return sql;
}

function buildCountQuery(target, distId, currentFileDate, fromDate, toDate) {
  var sql = 'SELECT COUNT() FROM ' + target.sobject +
    ' WHERE ' + target.fileDateField + ' < ' + currentFileDate;
  if (target.fromDateField && target.toDateField) {
    sql += ' AND ' + target.fromDateField + ' >= ' + fromDate +
      ' AND ' + target.toDateField + ' <= ' + toDate;
  }
  sql += " AND " + target.externalIdField + " LIKE '" + target.prefix + ':' + distId + ":%'";
  return sql;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var distId = input.targetDistId || input.distributorId;
  var currentFileDate = input.fileDate || input.currentFileDate;
  var fromDate = input.fromDate;
  var toDate = input.toDate;

  var errors = [];

  if (!distId) errors.push({ reason: 'Missing targetDistId' });
  if (!currentFileDate) errors.push({ reason: 'Missing fileDate/currentFileDate' });
  if (!fromDate) errors.push({ reason: 'Missing fromDate' });
  if (!toDate) errors.push({ reason: 'Missing toDate' });

  if (errors.length > 0) {
    return {
      queries: [],
      queryCount: 0,
      errors: errors,
      errorCount: errors.length,
      summary: {
        status: 'failed',
        reason: 'Missing required inputs',
        timestamp: new Date().toISOString()
      }
    };
  }

  // Generate stale cleanup queries for each target object
  // Each target includes a countQuery for safety validation:
  // compare stale count vs upsert count from the same run.
  // If stale count > upsert count, the file may be truncated — skip cleanup and alert.
  var queries = CLEANUP_TARGETS.map(function(target) {
    return {
      sobject: target.sobject,
      prefix: target.prefix,
      purpose: 'Delete stale ' + target.sobject + ' records',
      soql: buildStaleQuery(target, distId, currentFileDate, fromDate, toDate),
      countQuery: buildCountQuery(target, distId, currentFileDate, fromDate, toDate),
      safetyNote: 'Compare stale count against upsert count for ' + target.sobject + '. If stale > upserted, skip delete (possible truncated file).'
    };
  });

  return {
    queries: queries,
    queryCount: queries.length,
    distId: distId,
    currentFileDate: currentFileDate,
    fromDate: fromDate,
    toDate: toDate,
    errors: [],
    errorCount: 0,
    summary: {
      queryCount: queries.length,
      objects: queries.map(function(q) { return q.sobject; }),
      distId: distId,
      currentFileDate: currentFileDate,
      fromDate: fromDate,
      toDate: toDate,
      timestamp: new Date().toISOString()
    }
  };
};
