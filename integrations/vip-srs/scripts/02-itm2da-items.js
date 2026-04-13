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

var PREFIX = { ITEM: 'ITM', ITEM_LINE: 'ILN', ITEM_TYPE: 'ITY' };
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
function itemLineKey(name) { return PREFIX.ITEM_LINE + ':' + name; }
function itemTypeKey(name) { return PREFIX.ITEM_TYPE + ':' + name; }

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
  itemLineExternalIdField: 'VIP_External_ID__c',
  itemTypeSobject: NS + 'Item_Type__c',
  itemTypeExternalIdField: 'VIP_External_ID__c'
};

// =============================================================================
// TRANSFORM
// =============================================================================

function transformItem(row, recordTypeId) {
  var supplierItem = clean(row.SupplierItem);
  var record = {};

  // External ID
  record[NS + 'VIP_External_ID__c'] = itemKey(supplierItem);

  // Record Type — Finished Good (required for dependent picklist validation)
  if (recordTypeId) record.RecordTypeId = recordTypeId;

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

  // Package size (human-readable goes to Short Name)
  var packageSize = clean(row.PackageSize);
  if (packageSize) record[NS + 'Packaging_Type_Short_Name__c'] = packageSize;

  // Type__c: all VIP items are finished goods
  record[NS + 'Type__c'] = CONTAINER_TYPE[clean(row.ContainerType)] || CONTAINER_TYPE_DEFAULT;

  // Packaging_Type__c (Stock UOM Sub Type): VIP items are individual bottle/unit SKUs
  record[NS + 'Packaging_Type__c'] = 'Each';

  // Status: A → true, I → false
  var status = clean(row.Status);
  record[NS + 'Is_Active__c'] = status === 'A';

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

  // UOM: "US Count" for all VIP items (individual bottle/unit SKUs)
  // Packaging_Type__c "Each" is a dependent picklist requiring UOM = "US Count"
  // Volume info is captured separately in UOM_In_Fluid_Ounces__c
  record[NS + 'UOM__c'] = 'US Count';

  return record;
}

// =============================================================================
// ORCHESTRATOR
// =============================================================================

exports.step = function(input) {
  var rows = input.rows || input.csvData || input.data || [];

  // Finished Good record type ID (required for dependent picklist validation)
  var finishedGoodRtId = input.finishedGoodRecordTypeId || null;

  // File date for VIP_File_Date__c (date of pipeline run, not from file contents)
  var fileDate = input.fileDate || null;

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

  // Build Item_Line__c upsert records (Composite API PATCH by external ID)
  var itemLineRecords = Object.keys(itemLineNames).map(function(name) {
    var record = { Name: name, VIP_External_ID__c: itemLineKey(name) };
    if (fileDate) record.VIP_File_Date__c = fileDate;
    return record;
  });

  var itemLineChunks = chunkArray(itemLineRecords);
  var itemLineBatches = itemLineChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.VIP_External_ID__c;
        var body = { Name: record.Name };
        if (record.VIP_File_Date__c) body.VIP_File_Date__c = record.VIP_File_Date__c;
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            CONFIG.itemLineSobject + '/' + CONFIG.itemLineExternalIdField + '/' + sanitizeForUrl(extId),
          referenceId: 'itemLine_' + idx,
          body: body
        };
      })
    };
  });

  // Build Item_Type__c upsert records (Composite API PATCH by external ID)
  var itemTypeRecords = Object.keys(itemTypeNames).map(function(name) {
    var record = { Name: name, VIP_External_ID__c: itemTypeKey(name) };
    if (fileDate) record.VIP_File_Date__c = fileDate;
    return record;
  });

  var itemTypeChunks = chunkArray(itemTypeRecords);
  var itemTypeBatches = itemTypeChunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = record.VIP_External_ID__c;
        var body = { Name: record.Name };
        if (record.VIP_File_Date__c) body.VIP_File_Date__c = record.VIP_File_Date__c;
        return {
          method: 'PATCH',
          url: '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
            CONFIG.itemTypeSobject + '/' + CONFIG.itemTypeExternalIdField + '/' + sanitizeForUrl(extId),
          referenceId: 'itemType_' + idx,
          body: body
        };
      })
    };
  });

  // 3. TRANSFORM Item__c records
  var itemRecords = [];
  var transformErrors = [];

  valid.forEach(function(row, idx) {
    try {
      var record = transformItem(row, finishedGoodRtId);

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
    // Item_Line and Item_Type upsert batches (Composite API, processed before items)
    itemLineBatches: itemLineBatches,
    itemLineBatchCount: itemLineBatches.length,
    itemLineRecordCount: itemLineRecords.length,
    itemTypeBatches: itemTypeBatches,
    itemTypeBatchCount: itemTypeBatches.length,
    itemTypeRecordCount: itemTypeRecords.length,
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
      itemLines: itemLineRecords.length,
      itemTypes: itemTypeRecords.length,
      batches: itemBatches.length,
      timestamp: new Date().toISOString()
    }
  };
};
