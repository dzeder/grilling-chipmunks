/**
 * VIP SRS Script 03: DISTDA → Account (Customer) + Contact + Location__c
 *
 * Transforms VIP distributor master data into:
 * 1. Account (Customer RT) — the distributor company (supplier's customer)
 * 2. Contact — the distributor's primary contact
 * 3. Location__c — the distributor's warehouse
 *
 * Source: DISTDA file (27 columns)
 * Target: Account, Contact, Location__c
 * Rows: ~13 total, ~1 after filtering (or all if no targetDistId)
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.3
 */

// =============================================================================
// INLINE SHARED (for Tray Script connector — no require())
// =============================================================================

var PREFIX = { LOCATION: 'LOC', DISTRIBUTOR: 'DST', CONTACT: 'CON' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };

function locationKey(distId) { return PREFIX.LOCATION + ':' + distId; }
function distributorKey(distId) { return PREFIX.DISTRIBUTOR + ':' + distId; }
function distributorContactKey(distId) { return PREFIX.CONTACT + ':' + distId + ':DIST'; }
function clean(v) { if (v === undefined || v === null) return ''; return String(v).trim(); }

function sanitizeForUrl(value) {
  if (!value) return '';
  return String(value)
    .replace(/%/g, '%25').replace(/ /g, '%20').replace(/#/g, '%23')
    .replace(/\//g, '%2F').replace(/\?/g, '%3F').replace(/&/g, '%26')
    .replace(/\+/g, '%2B').replace(/=/g, '%3D')
    .replace(/\[/g, '%5B').replace(/\]/g, '%5D');
}

function chunkArray(array, size) {
  var s = size || SF_CONFIG.batchSize;
  var chunks = [];
  for (var i = 0; i < array.length; i += s) { chunks.push(array.slice(i, i + s)); }
  return chunks;
}

function toPhoneNumber(value) {
  if (!value) return '';
  var digits = String(value).replace(/\D/g, '');
  // Strip leading 0 (VIP format: 09413557685 → 9413557685)
  if (digits.length === 11 && digits[0] === '0') digits = digits.substring(1);
  if (digits.length === 10) {
    return '(' + digits.substring(0, 3) + ') ' + digits.substring(3, 6) + '-' + digits.substring(6);
  }
  return digits;
}

function parseName(fullName) {
  if (!fullName) return { firstName: '', lastName: '' };
  var name = fullName.replace(/#\d+$/, '').trim(); // Strip trailing #1 etc.
  var parts = name.split(/\s+/);
  if (parts.length === 1) return { firstName: '', lastName: parts[0] };
  return { firstName: parts[0], lastName: parts.slice(1).join(' ') };
}

// =============================================================================
// CONFIG
// =============================================================================

var NS = SF_CONFIG.namespacePrefix + '__';

// =============================================================================
// TRANSFORM
// =============================================================================

function transformAccount(row) {
  var distId = clean(row['Distributor ID']);
  var record = {};

  // External ID for upsert
  record[NS + 'External_ID__c'] = distributorKey(distId);

  // Name and legal name
  record.Name = clean(row['Distributor Name']);
  record[NS + 'Legal_Name__c'] = record.Name;

  // Customer number = DistId
  record[NS + 'Customer_Number__c'] = distId;

  // Record type and type
  record.Type = 'Customer';
  record[NS + 'Retail_Type__c'] = 'Distributor';
  record.AccountSource = 'VIP SRS';

  // Address (billing = shipping)
  var street = clean(row.Street);
  var city = clean(row.City);
  var state = clean(row.State);
  var zip = clean(row.Zip);

  if (street) record.BillingStreet = street;
  if (city) record.BillingCity = city;
  if (state) record.BillingState = state;
  if (zip) record.BillingPostalCode = zip;
  record.BillingCountry = 'US';

  if (street) record.ShippingStreet = street;
  if (city) record.ShippingCity = city;
  if (state) record.ShippingState = state;
  if (zip) record.ShippingPostalCode = zip;
  record.ShippingCountry = 'US';

  // Phone
  var phone = toPhoneNumber(row.Phone);
  if (phone) record.Phone = phone;

  // Active
  record[NS + 'Is_Active__c'] = true;

  return record;
}

function transformContact(row, distId) {
  var contactName = clean(row['Contact 1 Name']);
  var contactEmail = clean(row['Contact 1 Email']);

  // Skip if no meaningful contact data
  if (!contactName || contactName === 'Default User') return null;
  if (contactEmail === 'x@vtinfo.com') contactEmail = ''; // Placeholder

  var parsed = parseName(contactName);
  var record = {};

  record.External_ID__c = distributorContactKey(distId);
  record.FirstName = parsed.firstName;
  record.LastName = parsed.lastName || contactName;
  if (contactEmail) record.Email = contactEmail;

  // Link to distributor account via external ID relationship
  var acctRef = {};
  acctRef[NS + 'External_ID__c'] = distributorKey(distId);
  record.Account = acctRef;

  return record;
}

function transformLocation(row) {
  var distId = clean(row['Distributor ID']);
  var record = {};

  // External ID for upsert
  record.VIP_External_ID__c = locationKey(distId);

  // Location_Code__c stores the raw distributor ID (max 5 chars)
  record[NS + 'Location_Code__c'] = distId;

  // Direct mappings
  record.Name = clean(row['Distributor Name']);
  record[NS + 'Location_Street__c'] = clean(row.Street);
  record[NS + 'Location_City__c'] = clean(row.City);
  record[NS + 'Location_State__c'] = clean(row.State);
  record[NS + 'Location_Postal_Code__c'] = clean(row.Zip);

  // Hardcoded fields
  record[NS + 'Type__c'] = 'Warehouse';
  record[NS + 'Is_Active__c'] = true;
  record[NS + 'Is_Sellable__c'] = true;
  record[NS + 'Is_Finished_Good__c'] = true;

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];
  var targetDistId = input.targetDistId || input.distributorId;
  var fileDate = input.fileDate || null;

  // Record type ID for Customer (passed from runner, or hardcoded)
  var customerRtId = input.customerRecordTypeId || null;

  // 1. VALIDATE & FILTER
  var valid = [];
  var invalid = [];
  var skipped = [];

  rows.forEach(function(row, idx) {
    var recordType = clean(row.RecordId);
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ rowIndex: idx, reason: 'Non-DETAIL' });
      return;
    }

    var distId = clean(row['Distributor ID']);
    if (!distId) {
      invalid.push({ rowIndex: idx, reason: 'Missing Distributor ID' });
      return;
    }

    var distName = clean(row['Distributor Name']);
    if (!distName) {
      invalid.push({ rowIndex: idx, reason: 'Missing Distributor Name' });
      return;
    }

    // Filter to target distributor if specified
    if (targetDistId && distId !== targetDistId) {
      skipped.push({ rowIndex: idx, reason: 'Wrong distributor: ' + distId });
      return;
    }

    valid.push(row);
  });

  // 2. TRANSFORM
  var accountRecords = [];
  var contactRecords = [];
  var locationRecords = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    try {
      var distId = clean(row['Distributor ID']);

      // Account (Customer RT)
      var acct = transformAccount(row);
      if (customerRtId) acct.RecordTypeId = customerRtId;
      accountRecords.push(acct);

      // Contact (primary distributor contact)
      var contact = transformContact(row, distId);
      if (contact) contactRecords.push(contact);

      // Location (warehouse)
      locationRecords.push(transformLocation(row));
    } catch (e) {
      transformErrors.push({ rowIndex: idx, error: e.message });
    }
  });

  // 3. BATCH — Accounts
  var accountChunks = chunkArray(accountRecords);
  var accountBatches = accountChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record[NS + 'External_ID__c'];
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== NS + 'External_ID__c') body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/Account/' +
            NS + 'External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'distAcct_' + idx,
          body: body
        };
      })
    };
  });

  // 3b. BATCH — Contacts
  var contactChunks = chunkArray(contactRecords);
  var contactBatches = contactChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.External_ID__c;
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== 'External_ID__c') body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/Contact/' +
            'External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'distContact_' + idx,
          body: body
        };
      })
    };
  });

  // 3c. BATCH — Locations
  var locationChunks = chunkArray(locationRecords);
  var locationBatches = locationChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.VIP_External_ID__c;
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== 'VIP_External_ID__c') body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            NS + 'Location__c/VIP_External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'location_' + idx,
          body: body
        };
      })
    };
  });

  // 4. OUTPUT
  return {
    // Legacy: location batches for backward compatibility
    batches: locationBatches,
    batchCount: locationBatches.length,
    // New: separate batch arrays for runner
    accountBatches: accountBatches,
    contactBatches: contactBatches,
    locationBatches: locationBatches,
    // Records (raw — used by Collections API in runner)
    records: locationRecords,
    recordCount: locationRecords.length,
    accountRecords: accountRecords,
    accountRecordCount: accountRecords.length,
    contactRecords: contactRecords,
    contactRecordCount: contactRecords.length,
    locationRecords: locationRecords,
    errors: invalid.concat(transformErrors.map(function(e) {
      return { rowIndex: e.rowIndex, reason: 'Transform error: ' + e.error };
    })),
    errorCount: invalid.length + transformErrors.length,
    skippedCount: skipped.length,
    summary: {
      total: rows.length,
      valid: valid.length,
      accounts: accountRecords.length,
      contacts: contactRecords.length,
      locations: locationRecords.length,
      invalid: invalid.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      batches: accountBatches.length + contactBatches.length + locationBatches.length,
      timestamp: new Date().toISOString()
    }
  };
};
