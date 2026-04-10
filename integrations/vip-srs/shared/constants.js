/**
 * VIP SRS Integration — Shared Constants
 *
 * External ID prefixes, crosswalk maps, transaction codes, and
 * configuration constants used across all VIP SRS scripts.
 */

// =============================================================================
// EXTERNAL ID PREFIXES
// =============================================================================

var PREFIX = {
  CHAIN: 'CHN',
  ACCOUNT: 'ACT',
  CONTACT: 'CON',
  ITEM: 'ITM',
  LOCATION: 'LOC',
  INVOICE: 'INV',
  INVOICE_LINE: 'INL',
  INVENTORY: 'IVT',
  INVENTORY_HISTORY: 'IVH',
  INVENTORY_ADJUSTMENT: 'IVA',
  ALLOCATION: 'ALC',
  PLACEMENT: 'DPL'
};

// =============================================================================
// SALESFORCE CONFIG
// =============================================================================

var SF_CONFIG = {
  apiVersion: 'v62.0',
  batchSize: 25,
  namespacePrefix: 'ohfy'
};

// =============================================================================
// 7.1 CLASS OF TRADE CROSSWALK
// OUTDA.ClassOfTrade → Account.Market__c + Account.Premise_Type__c
// =============================================================================

var CLASS_OF_TRADE = {
  '01': { market: 'Convenience Store', premise: 'Off Premise' },
  '02': { market: 'Drug Store', premise: 'Off Premise' },
  '03': { market: 'Liquor Store', premise: 'Off Premise' },
  '04': { market: 'Military', premise: 'Off Premise' },
  '05': { market: 'Grocery Store', premise: 'Off Premise' },
  '06': { market: 'Non-Retail', premise: null },
  '07': { market: 'Distributor', premise: null },
  '08': { market: 'Mass Merchant', premise: 'Off Premise' },
  '09': { market: 'Grocery Store', premise: 'Off Premise' },
  '10': { market: 'Wholesale Club', premise: 'Off Premise' },
  '11': { market: 'Fine Wine Store', premise: 'Off Premise' },
  '12': { market: 'State Liquor Store', premise: 'Off Premise' },
  '13': { market: 'General Merchandise', premise: 'Off Premise' },
  '14': { market: 'Retail Specialty', premise: 'Off Premise' },
  '15': { market: 'E-Commerce', premise: 'Off Premise' },
  '16': { market: 'Dollar Store', premise: 'Off Premise' },
  '17': { market: 'CBD/THC', premise: 'Off Premise' },
  '18': { market: 'CBD/THC', premise: 'Off Premise' },
  '19': { market: 'Other Off Premise', premise: 'Off Premise' },
  '21': { market: 'Adult Entertainment', premise: 'On Premise' },
  '22': { market: 'Transportation', premise: 'On Premise' },
  '23': { market: 'Bar', premise: 'On Premise' },
  '24': { market: 'Entertainment', premise: 'On Premise' },
  '25': { market: 'Casino', premise: 'On Premise' },
  '26': { market: 'Concessionaire', premise: 'On Premise' },
  '27': { market: 'Country Club', premise: 'On Premise' },
  '28': { market: 'Hotel', premise: 'On Premise' },
  '29': { market: 'Military', premise: 'On Premise' },
  '30': { market: 'Night Club', premise: 'On Premise' },
  '31': { market: 'Private Club', premise: 'On Premise' },
  '32': { market: 'Restaurant', premise: 'On Premise' },
  '33': { market: 'Special Event', premise: 'On Premise' },
  '34': { market: 'Sports Bar', premise: 'On Premise' },
  '35': { market: 'Casual Dining', premise: 'On Premise' },
  '36': { market: 'Fine Dining', premise: 'On Premise' },
  '37': { market: 'School', premise: 'On Premise' },
  '38': { market: 'Office', premise: 'On Premise' },
  '39': { market: 'Other On Premise', premise: 'On Premise' },
  '40': { market: 'Hospital', premise: 'On Premise' },
  '41': { market: 'Government', premise: 'On Premise' },
  '42': { market: 'Irish Pub', premise: 'On Premise' },
  '43': { market: 'Tasting Room', premise: 'On Premise' },
  '50': { market: 'Direct Distributor', premise: null },
  '99': { market: 'Unassigned', premise: null }
};

// =============================================================================
// 7.2 INVENTORY TRANSACTION CODE CROSSWALK
// INVDA.TransCode → Inventory_Adjustment__c.Type__c + Reason__c
// =============================================================================

var TRANS_CODE = {
  '10': { target: 'inventory', type: null, reason: null, description: 'Ending Inventory' },
  '11': { target: 'history_only', type: null, reason: null, description: 'Committed Inventory' },
  '12': { target: 'history_only', type: null, reason: null, description: 'Saleable Inventory' },
  '20': { target: 'adjustment', type: 'Addition', reason: 'Purchase', description: 'Receipts' },
  '21': { target: 'adjustment', type: 'Addition', reason: 'Transfer', description: 'Transfer In' },
  '22': { target: 'adjustment', type: 'Subtraction', reason: 'Transfer', description: 'Transfer Out' },
  '30': { target: 'adjustment', type: 'Subtraction', reason: 'Return', description: 'Supplier Returns' },
  '40': { target: 'adjustment', type: 'Subtraction', reason: 'Breakage', description: 'Breakage' },
  '41': { target: 'adjustment', type: 'Subtraction', reason: 'Sample', description: 'Samples' },
  '99': { target: 'adjustment', type: 'Addition', reason: 'Adjustment', description: 'Misc Adjustments' }
  // TransCodes 50-59 (MTD aggregates) are skipped — they overlap daily codes 20-41
  // TransCode 70 (On Order) and 80 (In Bond) are skipped — future state
};

// =============================================================================
// 7.3 CHAIN STATUS CROSSWALK
// =============================================================================

var CHAIN_STATUS = {
  'C': 'Chain',
  'I': 'Independent',
  '': 'Independent'
};

// =============================================================================
// 7.4 ITEM STATUS CROSSWALK
// =============================================================================

var ITEM_STATUS = {
  'A': true,
  'I': false
};

// =============================================================================
// 7.5 OUTLET STATUS CROSSWALK
// =============================================================================

var OUTLET_STATUS = {
  'A': true,
  'I': false,
  'O': false
};

// =============================================================================
// 7.6 CONTAINER TYPE CROSSWALK
// ITM2DA.ContainerType → Item__c.Type__c
// All values map to 'Finished Good'
// =============================================================================

var CONTAINER_TYPE = {
  'S': 'Finished Good',    // Spirits
  'W': 'Finished Good',    // Wine
  'P': 'Finished Good',    // Beer Package
  'D': 'Finished Good',    // Beer Draft
  'F': 'Finished Good',    // FMB
  'H': 'Finished Good',    // Seltzer
  'N': 'Finished Good'     // Non-Alcoholic
};

var CONTAINER_TYPE_DEFAULT = 'Finished Good';

// =============================================================================
// 7.7 VOLUME UOM CROSSWALK
// ITM2DA.VolUOM → Item__c.UOM__c
// =============================================================================

var VOLUME_UOM = {
  'ML': 'Metric Volume',
  'LTR': 'Metric Volume',
  'OZ': 'US Volume'
};

// =============================================================================
// CONTROL RECORD FILTERS
// =============================================================================

var CONTROL_RECORDS = {
  accountPlaceholder: 'SRS99',
  itemPlaceholder: 'XXXXXX'
};

// =============================================================================
// ML TO FL OZ CONVERSION
// =============================================================================

var ML_TO_FLOZ = 0.033814;

// =============================================================================
// EXPORTS (for Node.js testing; inlined in Tray scripts)
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PREFIX: PREFIX,
    SF_CONFIG: SF_CONFIG,
    CLASS_OF_TRADE: CLASS_OF_TRADE,
    TRANS_CODE: TRANS_CODE,
    CHAIN_STATUS: CHAIN_STATUS,
    ITEM_STATUS: ITEM_STATUS,
    OUTLET_STATUS: OUTLET_STATUS,
    CONTAINER_TYPE: CONTAINER_TYPE,
    CONTAINER_TYPE_DEFAULT: CONTAINER_TYPE_DEFAULT,
    VOLUME_UOM: VOLUME_UOM,
    CONTROL_RECORDS: CONTROL_RECORDS,
    ML_TO_FLOZ: ML_TO_FLOZ
  };
}
