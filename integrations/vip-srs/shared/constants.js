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
  DEPLETION: 'DEP',
  INVENTORY: 'IVT',
  INVENTORY_HISTORY: 'IVH',
  INVENTORY_ADJUSTMENT: 'IVA',
  ALLOCATION: 'ALC',
  PLACEMENT: 'PLC',
  ITEM_LINE: 'ILN',
  ITEM_TYPE: 'ITY'
};

// =============================================================================
// SALESFORCE CONFIG
// =============================================================================

var SF_CONFIG = {
  apiVersion: 'v62.0',
  batchSize: 25,
  namespacePrefix: 'ohfy'
};

// Placement threshold: days without a reorder before flagging as lost placement
// CSO requirement: 60-day reorder alert window
var LOST_PLACEMENT_DAYS = 60;

// =============================================================================
// 7.1 CLASS OF TRADE CROSSWALK
// OUTDA.ClassOfTrade → Account.Market__c + Account.Premise_Type__c
// =============================================================================

// VIP Class of Trade → ohfy__Market__c (restricted picklist) + ohfy__Premise_Type__c
// Market values MUST match the org's restricted picklist. null = skip (no match).
// Validated against ROS2 sandbox 2026-04-10.
var CLASS_OF_TRADE = {
  '01': { market: 'Convenience', premise: 'Off Premise' },
  '02': { market: 'Drug Store', premise: 'Off Premise' },
  '03': { market: 'Liquor', premise: 'Off Premise' },
  '04': { market: null, premise: 'Off Premise' },                    // Military — no SF match
  '05': { market: 'Grocery Store', premise: 'Off Premise' },
  '06': { market: null, premise: null },                              // Non-Retail — no SF match
  '07': { market: 'Distributor House Account', premise: null },
  '08': { market: 'Club Mass Merchandiser', premise: 'Off Premise' },
  '09': { market: 'Grocery Store', premise: 'Off Premise' },
  '10': { market: 'Club Mass Merchandiser', premise: 'Off Premise' },
  '11': { market: 'Liquor', premise: 'Off Premise' },                // Fine Wine → Liquor
  '12': { market: 'Liquor', premise: 'Off Premise' },                // State Liquor → Liquor
  '13': { market: 'Supercenter', premise: 'Off Premise' },
  '14': { market: null, premise: 'Off Premise' },                    // Retail Specialty — no SF match
  '15': { market: null, premise: 'Off Premise' },                    // E-Commerce — no SF match
  '16': { market: 'Convenience', premise: 'Off Premise' },           // Dollar Store → Convenience
  '17': { market: null, premise: 'Off Premise' },                    // CBD/THC — no SF match
  '18': { market: null, premise: 'Off Premise' },                    // CBD/THC — no SF match
  '19': { market: null, premise: 'Off Premise' },                    // Other Off Premise — no SF match
  '21': { market: 'Adult Entertainment', premise: 'On Premise' },
  '22': { market: 'Airlines / Transportation', premise: 'On Premise' },
  '23': { market: 'Bars/Clubs/Taverns', premise: 'On Premise' },
  '24': { market: 'Recreational', premise: 'On Premise' },
  '25': { market: 'Casinos', premise: 'On Premise' },
  '26': { market: 'Concessions / Stadiums', premise: 'On Premise' },
  '27': { market: 'Private Club', premise: 'On Premise' },
  '28': { market: 'Hotel / Motel / Resort', premise: 'On Premise' },
  '29': { market: null, premise: 'On Premise' },                     // Military — no SF match
  '30': { market: 'Bars/Clubs/Taverns', premise: 'On Premise' },
  '31': { market: 'Private Club', premise: 'On Premise' },
  '32': { market: 'Restaurants', premise: 'On Premise' },
  '33': { market: 'Special Events', premise: 'On Premise' },
  '34': { market: 'Sports Bar', premise: 'On Premise' },
  '35': { market: 'Restaurants', premise: 'On Premise' },            // Casual Dining → Restaurants
  '36': { market: 'Restaurants', premise: 'On Premise' },            // Fine Dining → Restaurants
  '37': { market: null, premise: 'On Premise' },                     // School — no SF match
  '38': { market: null, premise: 'On Premise' },                     // Office — no SF match
  '39': { market: null, premise: 'On Premise' },                     // Other On Premise — no SF match
  '40': { market: null, premise: 'On Premise' },                     // Hospital — no SF match
  '41': { market: null, premise: 'On Premise' },                     // Government — no SF match
  '42': { market: 'Bars/Clubs/Taverns', premise: 'On Premise' },     // Irish Pub → Bars
  '43': { market: null, premise: 'On Premise' },                     // Tasting Room — no SF match
  '50': { market: 'Distributor House Account', premise: null },
  '99': { market: null, premise: null }                               // Unassigned — skip
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
// 7.5b DISTRIBUTOR CLASS OF TRADE CODES
// ClassOfTrade values that indicate a Distributor/Wholesaler (not a retailer)
// =============================================================================

var DISTRIBUTOR_COT = { '06': true, '07': true, '50': true };

// =============================================================================
// 7.5c ACCOUNT RECORD TYPE IDS (ROS2 sandbox)
// NOTE: Customer RT not yet available to integration user — org config needed
// =============================================================================

var RECORD_TYPES = {
  Account: {
    Customer: '012am0000050BVXAA2',
    Distributed_Customer: '012WF000003L8VWYA0',
    Chain_Banner: '012am0000050BVYAA2'
  }
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
    DISTRIBUTOR_COT: DISTRIBUTOR_COT,
    RECORD_TYPES: RECORD_TYPES,
    CONTAINER_TYPE: CONTAINER_TYPE,
    CONTAINER_TYPE_DEFAULT: CONTAINER_TYPE_DEFAULT,
    VOLUME_UOM: VOLUME_UOM,
    CONTROL_RECORDS: CONTROL_RECORDS,
    ML_TO_FLOZ: ML_TO_FLOZ
  };
}
