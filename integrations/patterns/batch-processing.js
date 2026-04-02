/**
 * Batch Processing Patterns for Tray Integration Scripts
 *
 * Reusable patterns for array chunking, grouping, deduplication,
 * and Salesforce Composite API batch request building.
 *
 * Source examples:
 *   - gpa/itemForecasts/processAccounts/script.js (lines 30-31)
 *   - fintech/remittanceProcessing/createBatchUpdates/script.js (lines 118-133)
 *   - BJs_Workday_AR_4_Account_Credit/3-group/script.js
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the batch sizes and request builders to your integration.
 */

// =============================================================================
// CONSTANTS
// =============================================================================

const SF_COMPOSITE_BATCH_SIZE = 25; // Salesforce Composite API subrequest limit

// =============================================================================
// PATTERN 1: Array Chunking
// =============================================================================
// Splits an array into fixed-size chunks. Immutable — does not modify input.

/**
 * @param {Array} array - Array to split
 * @param {number} size - Maximum chunk size
 * @returns {Array<Array>} Array of chunks
 */
function chunkArray(array, size) {
	if (!Array.isArray(array) || array.length === 0) return [];
	if (size <= 0) return [array];

	const chunks = [];
	for (let i = 0; i < array.length; i += size) {
		chunks.push(array.slice(i, i + size));
	}
	return chunks;
}

// =============================================================================
// PATTERN 2: Reduce-Based Grouping
// =============================================================================
// Groups array items by a key function. Returns { key: [items] }.

/**
 * @param {Array} array - Array of items to group
 * @param {Function} keyFn - Function that returns the group key for an item
 * @returns {Object} Object with group keys mapping to arrays of items
 */
function groupBy(array, keyFn) {
	if (!Array.isArray(array)) return {};

	return array.reduce(function(groups, item) {
		const key = keyFn(item);
		if (key === undefined || key === null) return groups;
		if (!groups[key]) groups[key] = [];
		groups[key].push(item);
		return groups;
	}, {});
}

// =============================================================================
// PATTERN 3: Deduplication by Key
// =============================================================================
// Removes duplicates keeping the first occurrence of each key.

/**
 * @param {Array} array - Array to deduplicate
 * @param {Function} keyFn - Function that returns the dedup key for an item
 * @returns {Array} Deduplicated array
 */
function deduplicateBy(array, keyFn) {
	if (!Array.isArray(array)) return [];

	const seen = new Set();
	return array.filter(function(item) {
		const key = keyFn(item);
		if (seen.has(key)) return false;
		seen.add(key);
		return true;
	});
}

// =============================================================================
// PATTERN 4: Unique Field Value Extraction
// =============================================================================
// Extracts unique non-empty values from a specific field across an array.

/**
 * @param {Array} array - Array of objects
 * @param {string} field - Field name to extract values from
 * @returns {Array} Array of unique non-empty values
 */
function getUniqueValues(array, field) {
	if (!Array.isArray(array)) return [];

	const values = new Set();
	array.forEach(function(item) {
		const value = item[field];
		if (value !== undefined && value !== null && value !== '') {
			values.add(value);
		}
	});
	return Array.from(values);
}

// =============================================================================
// PATTERN 5: Composite API Batch Request Builder
// =============================================================================
// Chunks records and applies a request builder function to create
// Salesforce Composite API batch payloads.

/**
 * @param {Array} records - Records to process
 * @param {number} batchSize - Records per batch (default: 25 for SF Composite)
 * @param {Function} requestBuilder - Function(record, index) => composite subrequest object
 * @returns {Array<{ compositeRequest: Array }>} Array of batch payloads
 */
function createBatchRequests(records, batchSize, requestBuilder) {
	if (!Array.isArray(records) || records.length === 0) return [];

	const size = batchSize || SF_COMPOSITE_BATCH_SIZE;
	const chunks = chunkArray(records, size);

	return chunks.map(function(chunk) {
		return {
			compositeRequest: chunk.map(function(record, index) {
				return requestBuilder(record, index);
			})
		};
	});
}

// =============================================================================
// PATTERN 6: Batch Result Accumulation
// =============================================================================
// Aggregates results from multiple batch responses into a single summary.

/**
 * @param {Array} batches - Array of batch response objects
 * @param {Function} resultExtractor - Function(batchResponse) => { successes: [], errors: [] }
 * @returns {{ successes: Array, errors: Array, summary: { totalBatches: number, totalSuccesses: number, totalErrors: number } }}
 */
function accumulateResults(batches, resultExtractor) {
	const successes = [];
	const errors = [];

	(batches || []).forEach(function(batch) {
		var extracted = resultExtractor(batch);
		if (extracted.successes) successes.push.apply(successes, extracted.successes);
		if (extracted.errors) errors.push.apply(errors, extracted.errors);
	});

	return {
		successes: successes,
		errors: errors,
		summary: {
			totalBatches: (batches || []).length,
			totalSuccesses: successes.length,
			totalErrors: errors.length
		}
	};
}

// =============================================================================
// PATTERN 7: Predicate-Based Partitioning
// =============================================================================
// Splits an array into two groups based on a predicate function.

/**
 * @param {Array} array - Array to partition
 * @param {Function} predicateFn - Function(item) => boolean
 * @returns {[Array, Array]} [matched, unmatched]
 */
function partitionBy(array, predicateFn) {
	if (!Array.isArray(array)) return [[], []];

	var matched = [];
	var unmatched = [];

	array.forEach(function(item) {
		if (predicateFn(item)) {
			matched.push(item);
		} else {
			unmatched.push(item);
		}
	});

	return [matched, unmatched];
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// exports.step = function(input) {
//     const records = input.records || [];
//
//     // Deduplicate by external ID
//     const unique = deduplicateBy(records, (r) => r.External_ID__c);
//
//     // Partition valid from invalid
//     const [valid, invalid] = partitionBy(unique, (r) => r.Name && r.External_ID__c);
//
//     // Build Composite API batch requests
//     const batches = createBatchRequests(valid, 25, (record, idx) => ({
//         method: 'PATCH',
//         url: `/services/data/v61.0/sobjects/Account/External_ID__c/${record.External_ID__c}`,
//         referenceId: `Account${idx}`,
//         body: { Name: record.Name, BillingCity: record.City }
//     }));
//
//     return {
//         batches,
//         batchCount: batches.length,
//         invalidRecords: invalid,
//         invalidCount: invalid.length,
//         summary: { total: records.length, unique: unique.length, valid: valid.length }
//     };
// };
