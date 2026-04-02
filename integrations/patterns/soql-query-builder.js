/**
 * SOQL Query Building Patterns for Tray Integration Scripts
 *
 * Reusable patterns for dynamic SOQL construction, IN clause formatting,
 * WHERE composition, special character escaping, and Composite API URL building.
 *
 * Source examples:
 *   - csv-upload/lookup-queries/script.js (lines 6-14)
 *   - gpa/itemForecasts/createBuyersQuery/script.js
 *   - VIP SRS/10_Get_Query/1-get_query/script.js
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the query structure to your integration's requirements.
 */

// =============================================================================
// CONSTANTS
// =============================================================================

const DEFAULT_API_VERSION = 'v61.0';
const SOQL_IN_CLAUSE_LIMIT = 2000; // Salesforce limit for IN clause values
const COMPOSITE_BATCH_LIMIT = 25; // Salesforce Composite API subrequest limit

// =============================================================================
// PATTERN 1: SOQL Value Escaping
// =============================================================================
// Escapes backslashes and single quotes for safe SOQL string values.

/**
 * @param {*} value - Value to escape
 * @returns {string} Escaped string safe for SOQL
 */
function escapeSOQLValue(value) {
	if (value === undefined || value === null) return '';
	return String(value).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

// =============================================================================
// PATTERN 2: IN Clause Formatting
// =============================================================================
// Formats an array of values as a SOQL IN clause: ('val1','val2','val3').
// Escapes each value and handles empty arrays.

/**
 * @param {Array} values - Array of values for the IN clause
 * @returns {string} Formatted IN clause string
 */
function formatInClause(values) {
	if (!Array.isArray(values) || values.length === 0) {
		// Return a syntactically valid IN clause that matches nothing.
		// Using ('') ensures the query won't error out with an empty IN clause,
		// and won't match any real records (empty string IDs don't exist in SF).
		return "('')";
	}

	const formatted = values
		.map(value => `'${escapeSOQLValue(value)}'`)
		.join(',');

	return `(${formatted})`;
}

// =============================================================================
// PATTERN 3: WHERE Clause Composition
// =============================================================================
// Builds a WHERE clause from an array of condition objects.
// Supports AND/OR logic and multiple operators.
//
// Condition: { field, operator, value }
// Operators: =, !=, >, <, >=, <=, LIKE, IN, NOT IN, includes, excludes

/**
 * @param {Array<{ field: string, operator: string, value: * }>} conditions
 * @param {string} [logic='AND'] - 'AND' or 'OR'
 * @returns {string} WHERE clause (without the 'WHERE' keyword)
 */
function buildWhereClause(conditions, logic) {
	if (!Array.isArray(conditions) || conditions.length === 0) return '';

	const parts = conditions.map(cond => {
		const field = cond.field;
		const op = (cond.operator || '=').toUpperCase();

		if (op === 'IN' || op === 'NOT IN') {
			const values = Array.isArray(cond.value) ? cond.value : [cond.value];
			return `${field} ${op} ${formatInClause(values)}`;
		}

		if (op === 'LIKE') {
			return `${field} LIKE '${escapeSOQLValue(cond.value)}'`;
		}

		if (op === 'INCLUDES' || op === 'EXCLUDES') {
			const values = Array.isArray(cond.value) ? cond.value : [cond.value];
			const formatted = values.map(v => `'${escapeSOQLValue(v)}'`).join(',');
			return `${field} ${op} (${formatted})`;
		}

		if (cond.value === null) {
			return op === '!=' ? `${field} != null` : `${field} = null`;
		}

		if (typeof cond.value === 'number' || typeof cond.value === 'boolean') {
			return `${field} ${op} ${cond.value}`;
		}

		return `${field} ${op} '${escapeSOQLValue(cond.value)}'`;
	});

	return parts.join(` ${(logic || 'AND').toUpperCase()} `);
}

// =============================================================================
// PATTERN 4: Full SELECT Query Builder
// =============================================================================
// Builds a complete SOQL SELECT query from a configuration object.

/**
 * @param {Object} config
 * @param {string} config.object - SObject name
 * @param {string[]} config.fields - Fields to select
 * @param {string} [config.where] - Pre-built WHERE clause string
 * @param {Array} [config.conditions] - Condition objects (alternative to where)
 * @param {string} [config.conditionLogic='AND'] - Logic for conditions
 * @param {string} [config.orderBy] - ORDER BY clause
 * @param {number} [config.limit] - LIMIT value
 * @param {number} [config.offset] - OFFSET value
 * @returns {string} Complete SOQL query string
 */
function buildSelectQuery(config) {
	const fields = config.fields.join(', ');
	let query = `SELECT ${fields} FROM ${config.object}`;

	// Build WHERE from conditions array or use pre-built string
	const whereClause = config.where
		|| (config.conditions ? buildWhereClause(config.conditions, config.conditionLogic) : '');

	if (whereClause) {
		query += ` WHERE ${whereClause}`;
	}

	if (config.orderBy) query += ` ORDER BY ${config.orderBy}`;
	if (config.limit) query += ` LIMIT ${parseInt(config.limit, 10)}`;
	if (config.offset) query += ` OFFSET ${parseInt(config.offset, 10)}`;

	return query;
}

// =============================================================================
// PATTERN 5: Salesforce Composite API URL Builder
// =============================================================================
// Builds the URL for Salesforce Composite API upsert requests using external IDs.

/**
 * @param {string} sobject - SObject API name
 * @param {string} externalIdField - External ID field API name
 * @param {string} externalIdValue - External ID value
 * @param {string} [apiVersion] - API version (default: v61.0)
 * @returns {string} Composite API URL path
 */
function buildCompositeUrl(sobject, externalIdField, externalIdValue, apiVersion) {
	const version = apiVersion || DEFAULT_API_VERSION;
	const encodedValue = String(externalIdValue)
		.replace(/%/g, '%25')   // Must be first to avoid double-encoding
		.replace(/ /g, '%20')
		.replace(/#/g, '%23')
		.replace(/\//g, '%2F')
		.replace(/\?/g, '%3F')
		.replace(/&/g, '%26')
		.replace(/\+/g, '%2B')
		.replace(/=/g, '%3D')
		.replace(/\[/g, '%5B')
		.replace(/\]/g, '%5D');

	return `/services/data/${version}/sobjects/${sobject}/${externalIdField}/${encodedValue}`;
}

// =============================================================================
// PATTERN 6: IN Clause Chunking
// =============================================================================
// Splits large value arrays into chunks that respect the SOQL IN clause limit.
// Returns multiple formatted IN clauses for use in separate queries.

/**
 * @param {Array} values - Array of values to chunk
 * @param {number} [chunkSize=2000] - Max values per IN clause
 * @returns {string[]} Array of formatted IN clause strings
 */
function chunkInClause(values, chunkSize) {
	if (!Array.isArray(values) || values.length === 0) return ["('')"];

	const size = chunkSize || SOQL_IN_CLAUSE_LIMIT;
	const chunks = [];

	for (let i = 0; i < values.length; i += size) {
		chunks.push(formatInClause(values.slice(i, i + size)));
	}

	return chunks;
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// exports.step = function(input) {
//     const accountIds = input.accountIds || [];
//
//     // Simple query with IN clause
//     const query = buildSelectQuery({
//         object: 'Account',
//         fields: ['Id', 'Name', 'External_ID__c', 'BillingCity'],
//         conditions: [
//             { field: 'External_ID__c', operator: 'IN', value: accountIds },
//             { field: 'IsDeleted', operator: '=', value: false }
//         ],
//         orderBy: 'Name ASC',
//         limit: 2000
//     });
//
//     // Composite API URL for upsert
//     const url = buildCompositeUrl(
//         'Account',
//         'External_ID__c',
//         'ACCT-001',
//         'v61.0'
//     );
//
//     return { query, compositeUrl: url };
// };
