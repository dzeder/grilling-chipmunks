/**
 * VIP SRS Script 05: OUTDA → Account (Outlets) + Contact (Buyers)
 *
 * Transforms VIP outlet/account universe into Salesforce Account and Contact records.
 * Links outlets to Chain Banner accounts via CHN:{Chain} lookup.
 *
 * Source: OUTDA file (71 columns)
 * Target: Account (ohfy__External_ID__c = ACT:{DistId}:{Account}),
 *         Contact (External_ID__c = CON:{DistId}:{Account}) -- needs custom field
 * Rows: ~36,587 total, filtered by distributor
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.5
 */

// =============================================================================
// INLINE SHARED
// =============================================================================

var PREFIX = { ACCOUNT: 'ACT', CONTACT: 'CON', CHAIN: 'CHN' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25 };

function accountKey(distId, account) { return PREFIX.ACCOUNT + ':' + distId + ':' + account; }
function contactKey(distId, account) { return PREFIX.CONTACT + ':' + distId + ':' + account; }
function chainKey(chain) { return PREFIX.CHAIN + ':' + chain; }

function clean(v) { if (v === undefined || v === null) return ''; return String(v).trim(); }

function toTitleCase(value) {
  if (!value) return '';
  return String(value).toLowerCase().replace(/(?:^|\s)\S/g, function(c) { return c.toUpperCase(); });
}

function formatPhone(phone) {
  if (!phone) return '';
  var digits = String(phone).replace(/\D/g, '');
  if (digits.length === 11 && digits[0] === '1') digits = digits.substring(1);
  if (digits.length === 10) return digits.substring(0, 3) + '-' + digits.substring(3, 6) + '-' + digits.substring(6);
  return digits || '';
}

function combineAddress(addr1, addr2) {
  var l1 = clean(addr1), l2 = clean(addr2);
  if (l1 && l2) return l1 + '\n' + l2;
  return l1 || l2;
}

function splitBuyerName(buyerName) {
  if (!buyerName || !String(buyerName).trim()) return { firstName: '', lastName: '' };
  var parts = String(buyerName).trim().split(/\s+/);
  if (parts.length === 1) return { firstName: parts[0], lastName: '' };
  return { firstName: parts[0], lastName: parts.slice(1).join(' ') };
}

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

// =============================================================================
// CROSSWALKS
// =============================================================================

// VIP Class of Trade → ohfy__Market__c (restricted picklist) + Premise_Type__c
// Market values must match the org's picklist. null = skip (no match).
var CLASS_OF_TRADE = {
  '01': { market: 'Convenience', premise: 'Off Premise' },
  '02': { market: 'Drug Store', premise: 'Off Premise' },
  '03': { market: 'Liquor', premise: 'Off Premise' },
  '04': { market: 'Military', premise: 'Off Premise' },
  '05': { market: 'Grocery Store', premise: 'Off Premise' },
  '06': { market: 'Employee / Special Account', premise: null },      // Non-Retail (employees, special)
  '07': { market: 'Distributor House Account', premise: null },
  '08': { market: 'Club Mass Merchandiser', premise: 'Off Premise' },
  '09': { market: 'Grocery Store', premise: 'Off Premise' },
  '10': { market: 'Club Mass Merchandiser', premise: 'Off Premise' },
  '11': { market: 'Liquor', premise: 'Off Premise' },                // Fine Wine → Liquor
  '12': { market: 'Liquor', premise: 'Off Premise' },                // State Liquor → Liquor
  '13': { market: 'Supercenter', premise: 'Off Premise' },
  '14': { market: 'Retail Specialty', premise: 'Off Premise' },
  '15': { market: 'E-Commerce', premise: 'Off Premise' },
  '16': { market: 'Convenience', premise: 'Off Premise' },           // Dollar Store → Convenience
  '17': { market: 'CBD / THC', premise: 'Off Premise' },
  '18': { market: 'CBD / THC', premise: 'Off Premise' },
  '19': { market: 'Other Off Premise', premise: 'Off Premise' },
  '21': { market: 'Adult Entertainment', premise: 'On Premise' },
  '22': { market: 'Airlines / Transportation', premise: 'On Premise' },
  '23': { market: 'Bars/Clubs/Taverns', premise: 'On Premise' },
  '24': { market: 'Recreational', premise: 'On Premise' },
  '25': { market: 'Casinos', premise: 'On Premise' },
  '26': { market: 'Concessions / Stadiums', premise: 'On Premise' },
  '27': { market: 'Private Club', premise: 'On Premise' },
  '28': { market: 'Hotel / Motel / Resort', premise: 'On Premise' },
  '29': { market: 'Military', premise: 'On Premise' },
  '30': { market: 'Bars/Clubs/Taverns', premise: 'On Premise' },
  '31': { market: 'Private Club', premise: 'On Premise' },
  '32': { market: 'Restaurants', premise: 'On Premise' },
  '33': { market: 'Special Events', premise: 'On Premise' },
  '34': { market: 'Sports Bar', premise: 'On Premise' },
  '35': { market: 'Restaurants', premise: 'On Premise' },            // Casual Dining → Restaurants
  '36': { market: 'Restaurants', premise: 'On Premise' },            // Fine Dining → Restaurants
  '37': { market: 'School / University', premise: 'On Premise' },
  '38': { market: 'Office / Corporate', premise: 'On Premise' },
  '39': { market: 'Other On Premise', premise: 'On Premise' },
  '40': { market: 'Hospital / Healthcare', premise: 'On Premise' },
  '41': { market: 'Government', premise: 'On Premise' },
  '42': { market: 'Bars/Clubs/Taverns', premise: 'On Premise' },     // Irish Pub → Bars
  '43': { market: 'Tasting Room', premise: 'On Premise' },
  '50': { market: 'Distributor House Account', premise: null },
  '99': { market: 'No Market', premise: null }                        // Unassigned — true fallback
};

var CHAIN_STATUS = { 'C': 'Chain', 'I': 'Independent', '': 'Independent' };
var OUTLET_STATUS = { 'A': true, 'I': false, 'O': false };

// Record Type IDs (from ROS2 org describe)
var RECORD_TYPES = {
  Distributed_Customer: '012WF000003L8VWYA0',
  Wholesaler: '012am0000050BVaAAM'
};

// =============================================================================
// TRANSFORM
// =============================================================================

function transformAccount(row, distId) {
  var account = clean(row.Account);
  var classOfTrade = clean(row.ClassOfTrade);
  var record = {};

  // --- Common fields ---
  record.ohfy__External_ID__c = accountKey(distId, account);
  record.ohfy__Customer_Number__c = account;
  record.Name = clean(row.DBA);
  record.AccountSource = 'VIP SRS';

  // Legal Name — use LicName if present, otherwise match Name
  var licName = clean(row.LicName);
  record.ohfy__Legal_Name__c = licName || record.Name;

  // Address (billing and shipping are the same for VIP data)
  var street = combineAddress(row.Addr1, row.Addr2);
  var city = clean(row.City);
  var state = clean(row.State);
  var postalCode = clean(row.Zip9);
  var country = clean(row.Country) || 'US';

  record.BillingStreet = street;
  record.BillingCity = city;
  record.BillingState = state;
  record.BillingPostalCode = postalCode;
  record.BillingCountry = country;
  record.ShippingStreet = street;
  record.ShippingCity = city;
  record.ShippingState = state;
  record.ShippingPostalCode = postalCode;
  record.ShippingCountry = country;

  // Phone
  var phone = formatPhone(row.Phone);
  if (phone) record.Phone = phone;

  // Status
  var status = clean(row.Status);
  record.ohfy__Is_Active__c = OUTLET_STATUS.hasOwnProperty(status) ? OUTLET_STATUS[status] : true;

  // License
  var license = clean(row.License);
  if (license) record.ohfy__ABC_License_Number__c = license;

  // Distributor rep codes (ROSM1/ROSM2) — NOT Shipyard's own reps
  var salesman1 = clean(row.Salesman1);
  if (salesman1 && salesman1 !== '999' && salesman1 !== 'HOUSE') {
    record.VIP_Salesman1__c = salesman1;
  }
  var salesman2 = clean(row.Salesman2);
  if (salesman2) {
    record.VIP_Salesman2__c = salesman2;
  }

  // COT 06/07/50 = distributor house accounts (sub-distributors, transfers, employee)
  // These use Wholesaler RT and are marked inactive — they're not retail outlets
  var isWholesaler = classOfTrade === '06' || classOfTrade === '07' || classOfTrade === '50';
  if (isWholesaler) {
    record.Type = 'Distributor';
    record.RecordTypeId = RECORD_TYPES.Wholesaler;
    record.ohfy__Is_Active__c = false;
  } else {
    record.Type = 'Distributed Customer';
    record.RecordTypeId = RECORD_TYPES.Distributed_Customer;
  }

  // Class of Trade → Market + Premise_Type
  var cot = CLASS_OF_TRADE[classOfTrade];
  if (cot) {
    if (cot.market) record.ohfy__Market__c = cot.market;
    if (cot.premise) record.ohfy__Premise_Type__c = cot.premise;
  }

  // Retail Type — COT-based override for non-retail accounts, then ChainStatus for retailers
  // COT 06 (Employee/Special), 07 (Distributor House), 50 (Distributor House) = not retailers
  var chainStatus = clean(row.ChainStatus);
  if (classOfTrade === '06' || classOfTrade === '07' || classOfTrade === '50') {
    record.ohfy__Retail_Type__c = 'Distributor';
  } else {
    record.ohfy__Retail_Type__c = CHAIN_STATUS[chainStatus] || 'Independent';
  }

  // Chain Banner lookup — use specific chain if provided, else default by premise
  var chain = clean(row.Chain);
  if (chain) {
    record.ohfy__Chain_Banner__r = { ohfy__External_ID__c: chainKey(chain) };
  } else if (record.ohfy__Retail_Type__c === 'Chain') {
    var premise = cot && cot.premise;
    var defaultChain = premise === 'On Premise' ? 'NO_CHAIN_ON' : 'NO_CHAIN_OFF';
    record.ohfy__Chain_Banner__r = { ohfy__External_ID__c: chainKey(defaultChain) };
  }

  // Store number
  var store = clean(row.Store);
  if (store) record.ohfy__Store_Number__c = store;

  // Link to distributor's warehouse location
  record.ohfy__Fulfillment_Location__r = { VIP_External_ID__c: 'LOC:' + distId };

  return record;
}

function transformContact(row, distId) {
  var account = clean(row.Account);
  var buyer = clean(row.Buyer);

  if (!buyer) return null;

  var name = splitBuyerName(buyer);
  var record = {};

  record.External_ID__c = contactKey(distId, account);
  record.FirstName = name.firstName;
  record.LastName = name.lastName || '(Unknown)';
  // AccountId linked via External_ID__c lookup in a subsequent step
  record._parentAccountKey = accountKey(distId, account);
  record.ohfy__Is_Billing_Contact__c = true;

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];
  var targetDistId = input.targetDistId || input.distributorId;

  // 1. VALIDATE & FILTER
  var valid = [];
  var invalid = [];
  var skipped = [];

  rows.forEach(function(row, idx) {
    var recordType = clean(row.RecordType);
    if (recordType && recordType !== 'DETAIL') {
      skipped.push({ rowIndex: idx, reason: 'Non-DETAIL' });
      return;
    }

    var distId = clean(row.DistId);
    if (targetDistId && distId !== targetDistId) {
      skipped.push({ rowIndex: idx, reason: 'Wrong distributor: ' + distId });
      return;
    }

    // Skip SRS99 placeholder
    var account = clean(row.Account);
    if (account === 'SRS99') {
      skipped.push({ rowIndex: idx, reason: 'SRS99 placeholder' });
      return;
    }

    // Skip blank DBA
    var dba = clean(row.DBA);
    if (!dba) {
      invalid.push({ rowIndex: idx, reason: 'Missing DBA name' });
      return;
    }

    if (!account) {
      invalid.push({ rowIndex: idx, reason: 'Missing Account number' });
      return;
    }

    valid.push(row);
  });

  // 2. TRANSFORM
  var accountRecords = [];
  var contactRecords = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    var distId = clean(row.DistId) || targetDistId;
    try {
      accountRecords.push(transformAccount(row, distId));

      var contact = transformContact(row, distId);
      if (contact) contactRecords.push(contact);
    } catch (e) {
      transformErrors.push({ rowIndex: idx, error: e.message });
    }
  });

  // 3. BATCH — Accounts
  var accountChunks = chunkArray(accountRecords);
  var accountBatches = accountChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.ohfy__External_ID__c;
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== 'ohfy__External_ID__c') body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/Account/ohfy__External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'acct_' + idx,
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
        var body = {
          FirstName: record.FirstName,
          LastName: record.LastName,
          ohfy__Is_Billing_Contact__c: record.ohfy__Is_Billing_Contact__c
        };
        // Link to parent account via external ID relationship
        body.Account = { ohfy__External_ID__c: record._parentAccountKey };
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/Contact/External_ID__c/' + sanitizeForUrl(extId),
          referenceId: 'contact_' + idx,
          body: body
        };
      })
    };
  });

  // 4. OUTPUT
  return {
    accountBatches: accountBatches,
    accountBatchCount: accountBatches.length,
    accountRecords: accountRecords,
    accountCount: accountRecords.length,
    contactBatches: contactBatches,
    contactBatchCount: contactBatches.length,
    contactRecords: contactRecords,
    contactCount: contactRecords.length,
    errors: invalid.concat(transformErrors.map(function(e) {
      return { rowIndex: e.rowIndex, reason: 'Transform error: ' + e.error };
    })),
    errorCount: invalid.length + transformErrors.length,
    skippedCount: skipped.length,
    summary: {
      total: rows.length,
      accounts: accountRecords.length,
      contacts: contactRecords.length,
      invalid: invalid.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      accountBatches: accountBatches.length,
      contactBatches: contactBatches.length,
      timestamp: new Date().toISOString()
    }
  };
};
