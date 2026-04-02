/**
 * Output Structuring Patterns for Tray Integration Scripts
 *
 * Reusable patterns for standardizing exports.step return values,
 * generating summaries, building column/row structures for Tray CSV connectors,
 * and creating consistent error objects.
 *
 * Source examples:
 *   - shopify/transformOrders/script.js (lines 186-203)
 *   - distributor-placements/VIP Placements/formatAccounts/script.js (lines 49-63)
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the output structure to your integration's requirements.
 */

// =============================================================================
// PATTERN 1: Standard Success Output Envelope
// =============================================================================
// Wraps processed data in a consistent success envelope with metadata.

/**
 * @param {*} data - Processed data payload
 * @param {Object} [metadata] - Optional metadata (source, timestamp, etc.)
 * @returns {{ data: *, metadata: Object, errors: Array }}
 */
function createSuccessOutput(data, metadata) {
	return {
		data: data,
		metadata: Object.assign({
			timestamp: new Date().toISOString(),
			status: 'success'
		}, metadata || {}),
		errors: []
	};
}

// =============================================================================
// PATTERN 2: Standard Error Output Envelope
// =============================================================================
// Wraps errors in a consistent error envelope with metadata.

/**
 * @param {Array} errors - Array of error objects or strings
 * @param {Object} [metadata] - Optional metadata
 * @returns {{ data: null, metadata: Object, errors: Array }}
 */
function createErrorOutput(errors, metadata) {
	return {
		data: null,
		metadata: Object.assign({
			timestamp: new Date().toISOString(),
			status: 'error'
		}, metadata || {}),
		errors: Array.isArray(errors) ? errors : [errors]
	};
}

// =============================================================================
// PATTERN 3: Processing Summary
// =============================================================================
// Generates a summary object from processed records and errors.

/**
 * @param {Array} records - Successfully processed records
 * @param {Array} errors - Error records
 * @returns {{ total: number, successful: number, failed: number, timestamp: string }}
 */
function createSummary(records, errors) {
	const successCount = Array.isArray(records) ? records.length : 0;
	const errorCount = Array.isArray(errors) ? errors.length : 0;

	return {
		total: successCount + errorCount,
		successful: successCount,
		failed: errorCount,
		timestamp: new Date().toISOString()
	};
}

// =============================================================================
// PATTERN 4: Tray CSV Connector Columns and Rows
// =============================================================================
// Generates the { columns, colCount, rows, rowCount } structure expected
// by Tray CSV connectors. Field configs define column names, types, and
// how to extract values from data rows.
//
// Field config: { name: string, type?: string, getValue: (record) => * }
// Or simplified: { name: string, field: string } where field is the key in the record.

/**
 * @param {Array<{ name: string, type?: string, field?: string, getValue?: Function }>} fieldConfigs
 * @param {Object[]} data - Array of data records
 * @returns {{ columns: Array<{ name: string, type: string }>, colCount: number, rows: Array<Array>, rowCount: number }}
 */
function createColumnsAndRows(fieldConfigs, data) {
	const columns = fieldConfigs.map(config => ({
		name: config.name,
		type: config.type || 'text'
	}));

	const rows = (data || []).map(record => {
		return fieldConfigs.map(config => {
			if (typeof config.getValue === 'function') {
				return config.getValue(record);
			}
			if (config.field) {
				const value = record[config.field];
				return value !== undefined && value !== null ? value : '';
			}
			return record[config.name] ?? '';
		});
	});

	return {
		columns,
		colCount: columns.length,
		rows,
		rowCount: rows.length
	};
}

// =============================================================================
// PATTERN 5: Ohanafy Standard Error Object
// =============================================================================
// Creates the standard error object structure used across all Ohanafy
// integrations for consistent error reporting.

/**
 * @param {string} type - Error type identifier
 * @param {string} message - Human-readable error message
 * @param {string} [id] - Record identifier associated with the error
 * @param {string} [service] - Service/integration name
 * @returns {{ error: { response: { body: { Type: string, Message: string } }, message: string, statusCode: number }, id: string, service: string }}
 */
function createStandardError(type, message, id, service) {
	return {
		error: {
			response: {
				body: {
					Type: type || 'UnknownError',
					Message: message || 'Unknown error'
				}
			},
			message: message || 'Unknown error',
			statusCode: 500
		},
		id: id || 'Unknown',
		service: service || 'Unknown'
	};
}

// =============================================================================
// PATTERN 6: Auto-Count Wrapper
// =============================================================================
// Adds *Count fields for every array property in a result object.
// e.g., { records: [...], errors: [...] } => adds recordsCount, errorsCount.

/**
 * @param {Object} resultObject - Object containing array properties
 * @returns {Object} Original object with added *Count fields
 */
function wrapWithCounts(resultObject) {
	if (!resultObject || typeof resultObject !== 'object') return resultObject;

	const counted = {};
	Object.keys(resultObject).forEach(key => {
		counted[key] = resultObject[key];
		if (Array.isArray(resultObject[key])) {
			counted[key + 'Count'] = resultObject[key].length;
		}
	});

	return counted;
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// const FIELD_CONFIGS = [
//     { name: 'Account Name', field: 'Name' },
//     { name: 'External ID', field: 'External_ID__c' },
//     { name: 'Amount', field: 'Amount__c', type: 'number' },
//     { name: 'Full Address', getValue: (r) => [r.Street, r.City, r.State].filter(Boolean).join(', ') }
// ];
//
// exports.step = function(input) {
//     const records = input.processedRecords || [];
//     const errors = input.errors || [];
//
//     // Option A: Column/Row format for Tray CSV connector
//     const csvOutput = createColumnsAndRows(FIELD_CONFIGS, records);
//     return wrapWithCounts({
//         ...csvOutput,
//         errors,
//         summary: createSummary(records, errors)
//     });
//
//     // Option B: Standard envelope format
//     // return createSuccessOutput(records, {
//     //     source: 'My Integration',
//     //     summary: createSummary(records, errors)
//     // });
// };
