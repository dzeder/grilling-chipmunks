/**
 * VIP SRS Integration — External ID Generators
 *
 * Generates deterministic, immutable external ID keys for Salesforce upserts.
 * Keys use only business identifiers — never quantities, prices, or names.
 * Format: {PREFIX}:{component1}:{component2}:...
 */

// Requires: PREFIX from constants.js (inlined in Tray scripts)

// =============================================================================
// KEY GENERATORS
// =============================================================================

/**
 * Account (Chain Banner): CHN:{Chain}
 * @param {string} chain - 10-digit zero-padded chain ID
 */
function chainKey(chain) {
  return PREFIX.CHAIN + ':' + chain;
}

/**
 * Account (Outlet): ACT:{DistId}:{Account}
 * @param {string} distId - Distributor code
 * @param {string} account - Outlet account number
 */
function accountKey(distId, account) {
  return PREFIX.ACCOUNT + ':' + distId + ':' + account;
}

/**
 * Contact (Buyer): CON:{DistId}:{Account}
 * @param {string} distId - Distributor code
 * @param {string} account - Outlet account number
 */
function contactKey(distId, account) {
  return PREFIX.CONTACT + ':' + distId + ':' + account;
}

/**
 * Item__c: ITM:{SupplierItem}
 * @param {string} supplierItem - Supplier item number
 */
function itemKey(supplierItem) {
  return PREFIX.ITEM + ':' + supplierItem;
}

/**
 * Location__c: LOC:{DistId}
 * @param {string} distId - Distributor code
 */
function locationKey(distId) {
  return PREFIX.LOCATION + ':' + distId;
}

/**
 * Invoice__c: INV:{DistId}:{InvoiceNbr}:{InvoiceDate}
 * @param {string} distId - Distributor code
 * @param {string} invoiceNbr - Invoice number
 * @param {string} invoiceDate - Invoice date (YYYYMMDD)
 */
function invoiceKey(distId, invoiceNbr, invoiceDate) {
  return PREFIX.INVOICE + ':' + distId + ':' + invoiceNbr + ':' + invoiceDate;
}

/**
 * Invoice_Item__c: INL:{DistId}:{InvoiceNbr}:{AcctNbr}:{SuppItem}:{UOM}
 * @param {string} distId - Distributor code
 * @param {string} invoiceNbr - Invoice number
 * @param {string} acctNbr - Account number
 * @param {string} suppItem - Supplier item number
 * @param {string} uom - Unit of measure (C or B)
 */
function invoiceLineKey(distId, invoiceNbr, acctNbr, suppItem, uom) {
  return PREFIX.INVOICE_LINE + ':' + distId + ':' + invoiceNbr + ':' + acctNbr + ':' + suppItem + ':' + uom;
}

/**
 * Inventory__c: IVT:{DistId}:{SupplierItem}
 * @param {string} distId - Distributor code
 * @param {string} supplierItem - Supplier item number
 */
function inventoryKey(distId, supplierItem) {
  return PREFIX.INVENTORY + ':' + distId + ':' + supplierItem;
}

/**
 * Inventory_History__c: IVH:{DistId}:{SupplierItem}:{PostingDate}:{UOM}
 * @param {string} distId - Distributor code
 * @param {string} supplierItem - Supplier item number
 * @param {string} postingDate - Posting date (YYYYMMDD)
 * @param {string} uom - Unit of measure (C or B)
 */
function inventoryHistoryKey(distId, supplierItem, postingDate, uom) {
  return PREFIX.INVENTORY_HISTORY + ':' + distId + ':' + supplierItem + ':' + postingDate + ':' + uom;
}

/**
 * Inventory_Adjustment__c: IVA:{DistId}:{SupplierItem}:{TransCode}:{TransDate}:{UOM}
 * @param {string} distId - Distributor code
 * @param {string} supplierItem - Supplier item number
 * @param {string} transCode - Transaction code
 * @param {string} transDate - Transaction date (YYYYMMDD)
 * @param {string} uom - Unit of measure (C or B)
 */
function inventoryAdjustmentKey(distId, supplierItem, transCode, transDate, uom) {
  return PREFIX.INVENTORY_ADJUSTMENT + ':' + distId + ':' + supplierItem + ':' + transCode + ':' + transDate + ':' + uom;
}

/**
 * Allocation__c: ALC:{DistId}:{SupplierItem}:{ControlDate}:{UOM}
 * @param {string} distId - Distributor code
 * @param {string} supplierItem - Supplier item number
 * @param {string} controlDate - Control date (YYYYMM)
 * @param {string} uom - Unit of measure (C or B)
 */
function allocationKey(distId, supplierItem, controlDate, uom) {
  return PREFIX.ALLOCATION + ':' + distId + ':' + supplierItem + ':' + controlDate + ':' + uom;
}

/**
 * Item_Line__c: ILN:{BrandDesc}
 * @param {string} name - Brand description (BrandDesc from ITM2DA)
 */
function itemLineKey(name) {
  return PREFIX.ITEM_LINE + ':' + name;
}

/**
 * Item_Type__c: ITY:{GenericCat3}
 * @param {string} name - Category name (GenericCat3 from ITM2DA)
 */
function itemTypeKey(name) {
  return PREFIX.ITEM_TYPE + ':' + name;
}

/**
 * Placement__c: PLC:{DistId}:{AcctNbr}:{SuppItem}
 * One per Account×Item pair — aggregated from SLSDA invoice lines.
 * @param {string} distId - Distributor code
 * @param {string} acctNbr - Account number
 * @param {string} suppItem - Supplier item number
 */
function placementKey(distId, acctNbr, suppItem) {
  return PREFIX.PLACEMENT + ':' + distId + ':' + acctNbr + ':' + suppItem;
}

// =============================================================================
// EXPORTS (for Node.js testing; inlined in Tray scripts)
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    chainKey: chainKey,
    accountKey: accountKey,
    contactKey: contactKey,
    itemKey: itemKey,
    itemLineKey: itemLineKey,
    itemTypeKey: itemTypeKey,
    locationKey: locationKey,
    invoiceKey: invoiceKey,
    invoiceLineKey: invoiceLineKey,
    inventoryKey: inventoryKey,
    inventoryHistoryKey: inventoryHistoryKey,
    inventoryAdjustmentKey: inventoryAdjustmentKey,
    allocationKey: allocationKey,
    placementKey: placementKey
  };
}
