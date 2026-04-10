/**
 * VIP SRS Script 02: ITM2DA → Item_Line__c + Item_Type__c + Item__c
 *
 * Transforms VIP supplier item master data into three Ohanafy objects:
 * 1. Item_Line__c (brand groupings from BrandDesc)
 * 2. Item_Type__c (product categories from GenericCat3)
 * 3. Item__c (product catalog)
 *
 * Source: ITM2DA file (66 columns)
 * Target: Item_Line__c, Item_Type__c, Item__c
 * Rows: ~65 per file
 *
 * Spec reference: VIP_AGENT_HANDOFF.md Section 5.2
 */

// =============================================================================
// INLINE SHARED (for Tray Script connector — no require())
// =============================================================================

var PREFIX = { ITEM: 'ITM' };
var SF_CONFIG = { apiVersion: 'v62.0', batchSize: 25, namespacePrefix: 'ohfy' };

var CONTAINER_TYPE = {
  'S': 'Finished Good', 'W': 'Finished Good', 'P': 'Finished Good',
  'D': 'Finished Good', 'F': 'Finished Good', 'H': 'Finished Good',
  'N': 'Finished Good'
};
var CONTAINER_TYPE_DEFAULT = 'Finished Good';

var VOLUME_UOM = { 'ML': 'Metric Volume', 'LTR': 'Metric Volume', 'OZ': 'US Volume' };

var ML_TO_FLOZ = 0.033814;

function itemKey(supplierItem) { return PREFIX.ITEM + ':' + supplierItem; }

function clean(v) { if (v === undefined || v === null) return ''; return String(v).trim(); }
function isBlankOrZeros(v) { if (!v) return true; var t = String(v).trim(); return t === '' || /^0+$/.test(t); }
function toNumber(v) { if (v === undefined || v === null || v === '') return null; var n = Number(v); return isNaN(n) ? null : n; }
function toInt(v) { var n = toNumber(v); return n !== null ? Math.floor(n) : null; }

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
// CONFIG
// =============================================================================

var NS = SF_CONFIG.namespacePrefix + '__';

var CONFIG = {
  serviceName: 'VIP SRS — ITM2DA Items',
  itemSobject: NS + 'Item__c',
  itemExternalIdField: NS + 'VIP_External_ID__c',
  itemLineSobject: NS + 'Item_Line__c',
  itemTypeSobject: NS + 'Item_Type__c'
};

// =============================================================================
// TRANSFORM
// =============================================================================

function transformItem(row) {
  var supplierItem = clean(row.SupplierItem);
  var record = {};

  // External ID
  record[NS + 'VIP_External_ID__c'] = itemKey(supplierItem);

  // Direct mappings
  record[NS + 'Supplier_Number__c'] = supplierItem;
  record.Name = clean(row.Desc);

  // GTINs — skip if all zeros
  if (!isBlankOrZeros(row.CaseGTIN)) record[NS + 'Case_GTIN__c'] = clean(row.CaseGTIN);
  if (!isBlankOrZeros(row.RetailGTIN)) record[NS + 'Unit_GTIN__c'] = clean(row.RetailGTIN);

  // Numeric fields
  var units = toInt(row.Units);
  if (units !== null) record[NS + 'Units_Per_Case__c'] = units;

  var sellingUnits = toInt(row.SellingUnits);
  if (sellingUnits !== null) record[NS + 'Retail_Units_Per_Case__c'] = sellingUnits;

  var weight = toNumber(row.Weight);
  if (weight !== null && weight > 0) record[NS + 'Weight__c'] = weight;

  var casesPerPallet = toInt(row.CasesPPallet1);
  if (casesPerPallet !== null && casesPerPallet > 0) record[NS + 'Cases_Per_Pallet__c'] = casesPerPallet;

  // Package type: BTL → Packaged
  var packageType = clean(row.PackageType);
  if (packageType) {
    record[NS + 'Package_Type__c'] = packageType === 'BTL' ? 'Packaged' : packageType;
  }

  // Package size
  var packageSize = clean(row.PackageSize);
  if (packageSize) record[NS + 'Packaging_Type__c'] = packageSize;

  // Status: A → true, I → false
  var status = clean(row.Status);
  record[NS + 'Is_Active__c'] = status === 'A';

  // Container type → Type__c (all map to Finished Good)
  var containerType = clean(row.ContainerType);
  record[NS + 'Type__c'] = CONTAINER_TYPE[containerType] || CONTAINER_TYPE_DEFAULT;

  // Volume conversion: VolofUnit (in VolUOM) → UOM_In_Fluid_Ounces__c
  var volOfUnit = toNumber(row.VolofUnit);
  var volUOM = clean(row.VolUOM);
  if (volOfUnit !== null && volOfUnit > 0) {
    if (volUOM === 'ML' || volUOM === 'LTR') {
      var mlValue = volUOM === 'LTR' ? volOfUnit * 1000 : volOfUnit;
      record[NS + 'UOM_In_Fluid_Ounces__c'] = Math.round(mlValue * ML_TO_FLOZ * 1000) / 1000;
    } else if (volUOM === 'OZ') {
      record[NS + 'UOM_In_Fluid_Ounces__c'] = volOfUnit;
    }
  }

  // UOM mapping
  if (volUOM && VOLUME_UOM[volUOM]) {
    record[NS + 'UOM__c'] = VOLUME_UOM[volUOM];
  }

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];

  // Collect existing Item_Line and Item_Type lookups if provided
  var existingItemLines = input.existingItemLines || {};   // { name: sfId }
  var existingItemTypes = input.existingItemTypes || {};    // { name: sfId }

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

    var supplierItem = clean(row.SupplierItem);
    if (!supplierItem) {
      invalid.push({ rowIndex: idx, reason: 'Missing SupplierItem' });
      return;
    }

    // Skip zero-volume placeholder
    if (supplierItem === 'XXXXXX') {
      skipped.push({ rowIndex: idx, reason: 'Zero-volume placeholder' });
      return;
    }

    valid.push(row);
  });

  // 2. EXTRACT unique Item_Line and Item_Type values
  var itemLineNames = {};  // { brandDesc: true }
  var itemTypeNames = {};  // { genericCat3: true }

  valid.forEach(function(row) {
    var brandDesc = clean(row.BrandDesc);
    if (brandDesc) itemLineNames[brandDesc] = true;

    var genericCat3 = clean(row.GenericCat3);
    if (genericCat3) itemTypeNames[genericCat3] = true;
  });

  // Build Item_Line__c records (create-if-missing approach)
  var newItemLines = Object.keys(itemLineNames).filter(function(name) {
    return !existingItemLines[name];
  }).map(function(name) {
    return { Name: name };
  });

  // Build Item_Type__c records (create-if-missing approach)
  var newItemTypes = Object.keys(itemTypeNames).filter(function(name) {
    return !existingItemTypes[name];
  }).map(function(name) {
    return { Name: name };
  });

  // 3. TRANSFORM Item__c records
  var itemRecords = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    try {
      var record = transformItem(row);

      // Add Item_Line__c lookup reference (by name)
      var brandDesc = clean(row.BrandDesc);
      if (brandDesc) {
        record._itemLineName = brandDesc;  // Used for post-processing lookup
      }

      // Add Item_Type__c lookup reference (by name)
      var genericCat3 = clean(row.GenericCat3);
      if (genericCat3) {
        record._itemTypeName = genericCat3;  // Used for post-processing lookup
      }

      itemRecords.push(record);
    } catch (e) {
      transformErrors.push({ rowIndex: idx, error: e.message });
    }
  });

  // 4. BATCH — build Composite API requests for Item__c
  var itemChunks = chunkArray(itemRecords);
  var itemBatches = itemChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record[CONFIG.itemExternalIdField];
        var body = {};
        Object.keys(record).forEach(function(key) {
          // Skip internal lookup markers and the external ID field
          if (key.charAt(0) === '_') return;
          if (key === CONFIG.itemExternalIdField) return;
          body[key] = record[key];
        });
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            CONFIG.itemSobject + '/' + CONFIG.itemExternalIdField + '/' + sanitizeForUrl(extId),
          referenceId: 'item_' + idx,
          body: body
        };
      })
    };
  });

  // 5. OUTPUT
  return {
    // Item_Line and Item_Type records to create (processed before items)
    newItemLines: newItemLines,
    newItemLineCount: newItemLines.length,
    newItemTypes: newItemTypes,
    newItemTypeCount: newItemTypes.length,
    // Item batches
    batches: itemBatches,
    batchCount: itemBatches.length,
    records: itemRecords,
    recordCount: itemRecords.length,
    // Lookup references (for wiring Item_Line/Item_Type IDs in a subsequent step)
    itemLineNames: Object.keys(itemLineNames),
    itemTypeNames: Object.keys(itemTypeNames),
    // Errors
    errors: invalid.concat(transformErrors.map(function(e) {
      return { rowIndex: e.rowIndex, reason: 'Transform error: ' + e.error };
    })),
    errorCount: invalid.length + transformErrors.length,
    skippedCount: skipped.length,
    summary: {
      total: rows.length,
      valid: itemRecords.length,
      invalid: invalid.length,
      skipped: skipped.length,
      transformErrors: transformErrors.length,
      newItemLines: newItemLines.length,
      newItemTypes: newItemTypes.length,
      batches: itemBatches.length,
      timestamp: new Date().toISOString()
    }
  };
};
