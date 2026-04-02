/**
 * Composite Script Scaffold for Tray Integration Scripts
 *
 * Ready-to-customize starter template combining the most common patterns:
 * validate -> transform -> batch -> output. Pre-wired with CONFIG section,
 * FIELD_MAPPINGS, STATUS_MAP, and a standard exports.step orchestrator.
 *
 * How to use:
 *   1. Copy this entire file as your new script.js
 *   2. Update CONFIG with your integration-specific values
 *   3. Define FIELD_MAPPINGS for your target SObject
 *   4. Adjust STATUS_MAP and VALIDATION_RULES
 *   5. Customize the transform() function for business logic
 *
 * Source patterns:
 *   - validation.js, string-manipulation.js, batch-processing.js,
 *     soql-query-builder.js, output-structuring.js, lookup-maps.js
 */

// =============================================================================
// CONFIG — Customize for your integration
// =============================================================================

var CONFIG = {
	serviceName: 'My Integration',           // Used in error reporting
	sobject: 'Account',                      // Target Salesforce object
	externalIdField: 'External_ID__c',       // External ID field for upserts
	apiVersion: 'v61.0',                     // Salesforce API version
	batchSize: 25,                           // Composite API subrequest limit
	namespacePrefix: 'ohfy'                  // Salesforce namespace prefix
};

// =============================================================================
// FIELD MAPPINGS — Define source-to-target field relationships
// =============================================================================

var FIELD_MAPPINGS = [
	{ targetField: 'Name', sourceField: 'AccountName', required: true },
	{ targetField: CONFIG.namespacePrefix + '__External_ID__c', sourceField: 'ExternalId', required: true },
	{ targetField: 'BillingStreet', sourceField: 'Address' },
	{ targetField: 'BillingCity', sourceField: 'City' },
	{ targetField: 'BillingState', sourceField: 'State' },
	{ targetField: 'BillingPostalCode', sourceField: 'ZipCode' },
	{ targetField: 'Phone', sourceField: 'Phone' }
];

// =============================================================================
// STATUS MAP — Map source values to Salesforce picklist values
// =============================================================================

var STATUS_MAP = {
	'active': 'Active',
	'inactive': 'Inactive',
	'pending': 'Pending',
	'closed': 'Closed'
};

// =============================================================================
// VALIDATION RULES — Define field validation requirements
// =============================================================================

var VALIDATION_RULES = [
	{ field: 'AccountName', required: true, type: 'string', maxLength: 255 },
	{ field: 'ExternalId', required: true, type: 'string' },
	{ field: 'Email', type: 'email', format: 'email' },
	{ field: 'Phone', type: 'phone' },
	{ field: 'ZipCode', format: 'zip-code' }
];

// =============================================================================
// VALIDATION — Input validation pipeline
// =============================================================================

function validateRow(row, rules) {
	var errors = [];

	rules.forEach(function(rule) {
		var value = row[rule.field];

		// Required check
		if (rule.required && (value === undefined || value === null || value === '')) {
			errors.push(rule.field + ': required field is missing');
			return;
		}

		if (value === undefined || value === null || value === '') return;

		// Type check
		if (rule.type === 'number' && isNaN(Number(value))) {
			errors.push(rule.field + ': expected number');
		}

		// Length check
		if (rule.maxLength && String(value).length > rule.maxLength) {
			errors.push(rule.field + ': exceeds max length ' + rule.maxLength);
		}
	});

	return { isValid: errors.length === 0, errors: errors };
}

function validateBatch(rows, rules) {
	var valid = [];
	var invalid = [];

	rows.forEach(function(row, index) {
		var result = validateRow(row, rules);
		if (result.isValid) {
			valid.push(row);
		} else {
			invalid.push({ row: row, rowIndex: index, errors: result.errors });
		}
	});

	return { valid: valid, invalid: invalid };
}

// =============================================================================
// TRANSFORM — Map source fields to target SObject fields
// =============================================================================

function mapStatus(value) {
	if (!value) return '';
	var key = String(value).toLowerCase();
	return STATUS_MAP.hasOwnProperty(key) ? STATUS_MAP[key] : value;
}

function cleanString(value) {
	if (value === undefined || value === null) return '';
	return String(value).trim().replace(/\s+/g, ' ');
}

function transform(row) {
	var record = {};

	FIELD_MAPPINGS.forEach(function(mapping) {
		var value = row[mapping.sourceField];
		record[mapping.targetField] = cleanString(value);
	});

	return record;
}

// =============================================================================
// BATCH — Build Composite API request payloads
// =============================================================================

function chunkArray(array, size) {
	var chunks = [];
	for (var i = 0; i < array.length; i += size) {
		chunks.push(array.slice(i, i + size));
	}
	return chunks;
}

function sanitizeForCompositeUrl(value) {
	if (!value) return '';
	return String(value)
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
}

function buildCompositeRequests(records) {
	var chunks = chunkArray(records, CONFIG.batchSize);

	return chunks.map(function(chunk) {
		return {
			compositeRequest: chunk.map(function(record, idx) {
				var externalIdValue = record[CONFIG.namespacePrefix + '__External_ID__c'] || record[CONFIG.externalIdField];
				return {
					method: 'PATCH',
					url: '/services/data/' + CONFIG.apiVersion + '/sobjects/' +
						CONFIG.sobject + '/' + CONFIG.externalIdField + '/' +
						sanitizeForCompositeUrl(externalIdValue),
					referenceId: CONFIG.sobject + idx,
					body: record
				};
			})
		};
	});
}

// =============================================================================
// OUTPUT — Standardize the return structure
// =============================================================================

function createSummary(records, validationErrors, transformErrors) {
	return {
		total: records.length + (validationErrors || []).length,
		successful: records.length,
		validationErrors: (validationErrors || []).length,
		transformErrors: (transformErrors || []).length,
		timestamp: new Date().toISOString()
	};
}

function createStandardError(type, message, id) {
	return {
		error: {
			response: {
				body: { Type: type, Message: message }
			},
			message: message,
			statusCode: 500
		},
		id: id || 'Unknown',
		service: CONFIG.serviceName
	};
}

// =============================================================================
// ORCHESTRATOR — Main exports.step function
// =============================================================================

exports.step = function(input) {
	var rows = input.csvData || input.records || input.data || [];

	// 1. VALIDATE
	var validation = validateBatch(rows, VALIDATION_RULES);

	// 2. TRANSFORM
	var transformErrors = [];
	var transformed = [];

	validation.valid.forEach(function(row, index) {
		try {
			transformed.push(transform(row));
		} catch (e) {
			transformErrors.push(createStandardError(
				'TransformError',
				e.message,
				'Row ' + index
			));
		}
	});

	// 3. BATCH
	var batches = buildCompositeRequests(transformed);

	// 4. OUTPUT
	var validationErrors = validation.invalid.map(function(item) {
		return createStandardError(
			'ValidationError',
			item.errors.join('; '),
			'Row ' + item.rowIndex
		);
	});

	var allErrors = validationErrors.concat(transformErrors);

	return {
		batches: batches,
		batchCount: batches.length,
		records: transformed,
		recordCount: transformed.length,
		errors: allErrors,
		errorCount: allErrors.length,
		summary: createSummary(transformed, validationErrors, transformErrors)
	};
};
