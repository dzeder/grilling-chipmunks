/**
 * VIP SRS Integration — Transform Utilities
 *
 * Date conversion, phone formatting, string normalization,
 * and other data transformation functions.
 */

// =============================================================================
// DATE TRANSFORMS
// =============================================================================

/**
 * Convert VIP date format YYYYMMDD to Salesforce format YYYY-MM-DD.
 * Returns null for invalid/zero dates.
 * @param {string} vipDate - Date string in YYYYMMDD format
 * @returns {string|null} Date in YYYY-MM-DD format, or null
 */
function toSfDate(vipDate) {
  if (!vipDate || vipDate === '00000000' || vipDate.length !== 8) return null;
  var year = vipDate.substring(0, 4);
  var month = vipDate.substring(4, 6);
  var day = vipDate.substring(6, 8);
  if (year === '0000' || month === '00' || day === '00') return null;
  return year + '-' + month + '-' + day;
}

/**
 * Convert VIP control date YYYYMM to first-of-month YYYY-MM-01.
 * @param {string} controlDate - Date string in YYYYMM format
 * @returns {string|null} Date in YYYY-MM-01 format, or null
 */
function toSfMonthDate(controlDate) {
  if (!controlDate || controlDate.length !== 6) return null;
  var year = controlDate.substring(0, 4);
  var month = controlDate.substring(4, 6);
  if (year === '0000' || month === '00') return null;
  return year + '-' + month + '-01';
}

/**
 * Extract date from VIP filename format: N{YYYYMMDD}
 * e.g., "N20260408" → "2026-04-08"
 * @param {string} filename - VIP filename or date portion
 * @returns {string|null} Date in YYYY-MM-DD format, or null
 */
function extractFileDate(filename) {
  if (!filename) return null;
  // Match N followed by 8 digits
  var match = String(filename).match(/N(\d{8})/);
  if (!match) return null;
  return toSfDate(match[1]);
}

// =============================================================================
// STRING TRANSFORMS
// =============================================================================

/**
 * Convert string to title case (first letter of each word capitalized).
 * @param {string} value - Input string
 * @returns {string} Title-cased string
 */
function toTitleCase(value) {
  if (!value) return '';
  return String(value).toLowerCase().replace(/(?:^|\s)\S/g, function(char) {
    return char.toUpperCase();
  });
}

/**
 * Clean and trim a string value. Returns empty string for null/undefined.
 * @param {string} value - Input value
 * @returns {string} Trimmed string
 */
function clean(value) {
  if (value === undefined || value === null) return '';
  return String(value).trim();
}

/**
 * Check if a string is blank, null, or all zeros (common in VIP data).
 * @param {string} value - Input value
 * @returns {boolean} true if blank or all zeros
 */
function isBlankOrZeros(value) {
  if (!value) return true;
  var trimmed = String(value).trim();
  return trimmed === '' || /^0+$/.test(trimmed);
}

// =============================================================================
// PHONE FORMATTING
// =============================================================================

/**
 * Format a phone number as XXX-XXX-XXXX.
 * Strips non-digits, handles 10 or 11 digit numbers.
 * @param {string} phone - Raw phone string
 * @returns {string} Formatted phone or original value
 */
function formatPhone(phone) {
  if (!phone) return '';
  var digits = String(phone).replace(/\D/g, '');

  // Strip leading 1 for 11-digit US numbers
  if (digits.length === 11 && digits[0] === '1') {
    digits = digits.substring(1);
  }

  if (digits.length === 10) {
    return digits.substring(0, 3) + '-' + digits.substring(3, 6) + '-' + digits.substring(6);
  }

  // Return cleaned digits if not standard length
  return digits || '';
}

// =============================================================================
// NUMERIC TRANSFORMS
// =============================================================================

/**
 * Parse a numeric value, returning null for non-numeric inputs.
 * @param {string|number} value - Input value
 * @returns {number|null}
 */
function toNumber(value) {
  if (value === undefined || value === null || value === '') return null;
  var num = Number(value);
  return isNaN(num) ? null : num;
}

/**
 * Parse an integer value, returning null for non-numeric inputs.
 * @param {string|number} value - Input value
 * @returns {number|null}
 */
function toInt(value) {
  var num = toNumber(value);
  return num !== null ? Math.floor(num) : null;
}

/**
 * Convert milliliters to fluid ounces.
 * @param {number} ml - Value in milliliters
 * @returns {number|null}
 */
function mlToFlOz(ml) {
  var num = toNumber(ml);
  if (num === null) return null;
  return Math.round(num * 0.033814 * 1000) / 1000;
}

// =============================================================================
// BUYER NAME SPLITTING
// =============================================================================

/**
 * Split a buyer name into first and last name.
 * @param {string} buyerName - Full name string (e.g., "Catherine Napfel")
 * @returns {{ firstName: string, lastName: string }}
 */
function splitBuyerName(buyerName) {
  if (!buyerName || !String(buyerName).trim()) {
    return { firstName: '', lastName: '' };
  }

  var parts = String(buyerName).trim().split(/\s+/);
  if (parts.length === 1) {
    return { firstName: parts[0], lastName: '' };
  }

  return {
    firstName: parts[0],
    lastName: parts.slice(1).join(' ')
  };
}

// =============================================================================
// ADDRESS FORMATTING
// =============================================================================

/**
 * Combine address lines, skipping blanks.
 * @param {string} addr1 - Address line 1
 * @param {string} addr2 - Address line 2
 * @returns {string} Combined address
 */
function combineAddress(addr1, addr2) {
  var line1 = clean(addr1);
  var line2 = clean(addr2);
  if (line1 && line2) return line1 + '\n' + line2;
  return line1 || line2;
}

// =============================================================================
// COMPOSITE API HELPERS
// =============================================================================

/**
 * Sanitize a value for use in SF Composite API URL path.
 * @param {string} value - Value to encode
 * @returns {string} URL-safe value
 */
function sanitizeForUrl(value) {
  if (!value) return '';
  return String(value)
    .replace(/%/g, '%25')
    .replace(/ /g, '%20')
    .replace(/#/g, '%23')
    .replace(/\//g, '%2F')
    .replace(/\?/g, '%3F')
    .replace(/&/g, '%26')
    .replace(/\+/g, '%2B')
    .replace(/=/g, '%3D')
    .replace(/\[/g, '%5B')
    .replace(/\]/g, '%5D');
}

/**
 * Build a Composite API PATCH URL for upsert.
 * @param {string} sobject - SObject API name (with namespace if needed)
 * @param {string} externalIdField - External ID field API name
 * @param {string} externalIdValue - External ID value
 * @returns {string} Composite API URL path
 */
function buildUpsertUrl(sobject, externalIdField, externalIdValue) {
  return '/services/data/' + SF_CONFIG.apiVersion + '/sobjects/' +
    sobject + '/' + externalIdField + '/' + sanitizeForUrl(externalIdValue);
}

/**
 * Chunk an array into batches of specified size.
 * @param {Array} array - Input array
 * @param {number} size - Chunk size (default: 25)
 * @returns {Array<Array>} Array of chunks
 */
function chunkArray(array, size) {
  var chunkSize = size || SF_CONFIG.batchSize;
  var chunks = [];
  for (var i = 0; i < array.length; i += chunkSize) {
    chunks.push(array.slice(i, i + chunkSize));
  }
  return chunks;
}

/**
 * Build Composite API batch requests from transformed records.
 * @param {Array} records - Transformed SF records with external ID values
 * @param {string} sobject - Target SObject
 * @param {string} externalIdField - External ID field name
 * @param {Function} getExternalId - Function to extract external ID from record
 * @returns {Array} Array of composite request payloads
 */
function buildCompositeBatches(records, sobject, externalIdField, getExternalId) {
  var chunks = chunkArray(records);

  return chunks.map(function(chunk) {
    return {
      compositeRequest: chunk.map(function(record, idx) {
        var extId = getExternalId(record);
        // Remove the external ID from the body if it's a custom field
        // (SF handles it via the URL for upsert)
        var body = {};
        Object.keys(record).forEach(function(key) {
          if (key !== externalIdField) {
            body[key] = record[key];
          }
        });

        return {
          method: 'PATCH',
          url: buildUpsertUrl(sobject, externalIdField, extId),
          referenceId: sobject.replace(/[^a-zA-Z0-9]/g, '') + '_' + idx,
          body: body
        };
      })
    };
  });
}

// =============================================================================
// EXPORTS (for Node.js testing; inlined in Tray scripts)
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    toSfDate: toSfDate,
    toSfMonthDate: toSfMonthDate,
    extractFileDate: extractFileDate,
    toTitleCase: toTitleCase,
    clean: clean,
    isBlankOrZeros: isBlankOrZeros,
    formatPhone: formatPhone,
    toNumber: toNumber,
    toInt: toInt,
    mlToFlOz: mlToFlOz,
    splitBuyerName: splitBuyerName,
    combineAddress: combineAddress,
    sanitizeForUrl: sanitizeForUrl,
    buildUpsertUrl: buildUpsertUrl,
    chunkArray: chunkArray,
    buildCompositeBatches: buildCompositeBatches
  };
}
