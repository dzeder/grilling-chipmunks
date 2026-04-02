/**
 * Lookup Map Patterns for Tray Integration Scripts
 *
 * Reusable patterns for status mapping, transaction code lookups,
 * configurable Map/switch factories, and set-based existence checks.
 *
 * Source examples:
 *   - VIP SRS/02a_SLS_INV_Reporting_Generator/1-generate_details/script.js
 *   - shopify/transformOrders/script.js (lines 211-230)
 *   - distributor-placements/VIP Placements/formatAccounts/script.js (lines 108-161)
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the lookup configurations to your integration's requirements.
 */

// =============================================================================
// PATTERN 1: Lookup Map from Array
// =============================================================================
// Builds a Map from an array of objects using specified key and value fields.

/**
 * @param {Object[]} entries - Array of objects
 * @param {string} keyField - Field to use as Map key
 * @param {string} valueField - Field to use as Map value
 * @returns {Map} Map of keyField => valueField
 */
function createLookupMap(entries, keyField, valueField) {
	var map = new Map();
	if (!Array.isArray(entries)) return map;

	entries.forEach(function(entry) {
		var key = entry[keyField];
		if (key !== undefined && key !== null && key !== '') {
			map.set(key, entry[valueField]);
		}
	});

	return map;
}

// =============================================================================
// PATTERN 2: Reverse Lookup Map
// =============================================================================
// Builds a reverse Map (value => key) from an array of objects.

/**
 * @param {Object[]} entries - Array of objects
 * @param {string} keyField - Field that becomes the Map value
 * @param {string} valueField - Field that becomes the Map key
 * @returns {Map} Reverse Map of valueField => keyField
 */
function createReverseLookupMap(entries, keyField, valueField) {
	var map = new Map();
	if (!Array.isArray(entries)) return map;

	entries.forEach(function(entry) {
		var value = entry[valueField];
		if (value !== undefined && value !== null && value !== '') {
			map.set(value, entry[keyField]);
		}
	});

	return map;
}

// =============================================================================
// PATTERN 3: Safe Lookup with Default
// =============================================================================
// Retrieves a value from a Map with a fallback default.

/**
 * @param {Map} map - Lookup Map
 * @param {*} key - Key to look up
 * @param {*} defaultValue - Fallback if key not found
 * @returns {*} Looked-up value or default
 */
function lookupWithDefault(map, key, defaultValue) {
	if (!map || !map.has(key)) return defaultValue;
	return map.get(key);
}

// =============================================================================
// PATTERN 4: Status Mapper Factory
// =============================================================================
// Creates a reusable mapping function from a status map object.
// Returns a function that maps input values to output values.

/**
 * @param {Object} statusMap - Object mapping input values to output values
 * @param {string} [defaultStatus='Unknown'] - Fallback for unmapped values
 * @returns {Function} Mapping function (value) => mappedValue
 */
function createStatusMapper(statusMap, defaultStatus) {
	var fallback = defaultStatus !== undefined ? defaultStatus : 'Unknown';

	return function(value) {
		if (value === undefined || value === null) return fallback;
		var key = String(value);
		return statusMap.hasOwnProperty(key) ? statusMap[key] : fallback;
	};
}

// =============================================================================
// PATTERN 5: Code-to-Description Lookup Factory
// =============================================================================
// Creates a function that maps codes to descriptions. Useful for replacing
// inline switch statements (e.g., VIP sub-channel descriptions).

/**
 * @param {Object} codeMap - Object mapping codes to descriptions
 * @returns {Function} Lookup function (code) => description or code itself
 */
function createCodeLookup(codeMap) {
	return function(code) {
		if (code === undefined || code === null) return '';
		var key = String(code);
		return codeMap.hasOwnProperty(key) ? codeMap[key] : key;
	};
}

// =============================================================================
// PATTERN 6: Set from Field Values
// =============================================================================
// Builds a Set from field values for fast O(1) existence checks.

/**
 * @param {Object[]} array - Array of objects
 * @param {string} field - Field name to extract into the Set
 * @returns {Set} Set of unique field values
 */
function buildSetFromField(array, field) {
	var set = new Set();
	if (!Array.isArray(array)) return set;

	array.forEach(function(item) {
		var value = item[field];
		if (value !== undefined && value !== null && value !== '') {
			set.add(value);
		}
	});

	return set;
}

// =============================================================================
// PATTERN 7: Set-Based Match/Unmatch Partitioning
// =============================================================================
// Partitions an array into matched and unmatched based on field presence in a Set.

/**
 * @param {Object[]} sourceArray - Array to partition
 * @param {Set} lookupSet - Set of values to match against
 * @param {string} field - Field in sourceArray to check against the Set
 * @returns {{ matched: Object[], unmatched: Object[] }}
 */
function matchByField(sourceArray, lookupSet, field) {
	var matched = [];
	var unmatched = [];

	if (!Array.isArray(sourceArray)) return { matched: matched, unmatched: unmatched };

	sourceArray.forEach(function(item) {
		if (lookupSet.has(item[field])) {
			matched.push(item);
		} else {
			unmatched.push(item);
		}
	});

	return { matched: matched, unmatched: unmatched };
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// // Status mapping for order processing
// const ORDER_STATUS_MAP = {
//     'pending': 'Draft',
//     'confirmed': 'Submitted',
//     'shipped': 'Fulfilled',
//     'cancelled': 'Cancelled',
//     'returned': 'Returned'
// };
//
// // Sub-channel code descriptions
// const SUB_CHANNEL_CODES = {
//     '01': 'On Premise',
//     '02': 'Off Premise',
//     '03': 'Chain',
//     '04': 'Independent',
//     '05': 'National Account'
// };
//
// exports.step = function(input) {
//     const orders = input.orders || [];
//     const existingAccounts = input.existingAccounts || [];
//
//     // Create lookup tools
//     const mapStatus = createStatusMapper(ORDER_STATUS_MAP, 'Draft');
//     const getSubChannel = createCodeLookup(SUB_CHANNEL_CODES);
//     const existingSet = buildSetFromField(existingAccounts, 'External_ID__c');
//
//     // Partition new vs existing
//     const { matched, unmatched } = matchByField(orders, existingSet, 'accountId');
//
//     // Transform with status mapping
//     const transformed = orders.map(order => ({
//         ...order,
//         Status__c: mapStatus(order.status),
//         Sub_Channel_Description__c: getSubChannel(order.subChannelCode)
//     }));
//
//     return {
//         orders: transformed,
//         newAccounts: unmatched,
//         existingAccounts: matched
//     };
// };
