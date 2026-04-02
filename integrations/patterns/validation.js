/**
 * Input Validation Patterns for Tray Integration Scripts
 *
 * Reusable patterns for field validation, type checking, format verification,
 * and batch validation pipelines used across integration scripts.
 *
 * Source examples:
 *   - csv-upload/lookup-queries/script.js (lines 200-223)
 *   - shopify/transformOrders/script.js (lines 32-70)
 *   - csv-upload/create-accounts/script.js (lines 136-145)
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the field rules and format definitions to your integration.
 */

// =============================================================================
// CONSTANTS
// =============================================================================

const FORMAT_PATTERNS = {
	'email': /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
	'phone': /^\+?[\d\s\-().]{7,20}$/,
	'date-YYYY-MM-DD': /^\d{4}-\d{2}-\d{2}$/,
	'salesforce-id': /^[a-zA-Z0-9]{15}([a-zA-Z0-9]{3})?$/,
	'zip-code': /^\d{5}(-\d{4})?$/
};

const TYPE_VALIDATORS = {
	'string': (value) => typeof value === 'string',
	'number': (value) => {
		if (typeof value === 'number') return !isNaN(value);
		if (typeof value === 'string') return value.trim() !== '' && !isNaN(Number(value));
		return false;
	},
	'boolean': (value) => typeof value === 'boolean' || value === 'true' || value === 'false',
	'date': (value) => {
		if (!value) return false;
		const d = new Date(value);
		return !isNaN(d.getTime());
	},
	'email': (value) => typeof value === 'string' && FORMAT_PATTERNS['email'].test(value),
	'phone': (value) => typeof value === 'string' && FORMAT_PATTERNS['phone'].test(value)
};

// =============================================================================
// PATTERN 1: Required Field Validation
// =============================================================================
// Checks that all specified fields exist and are non-empty in a data row.
// Returns validation result with per-field error messages.

/**
 * @param {Object} row - Data row to validate
 * @param {string[]} fieldNames - Array of required field names
 * @returns {{ isValid: boolean, errors: string[] }}
 */
function validateRequiredFields(row, fieldNames) {
	const errors = [];

	fieldNames.forEach(field => {
		const value = row[field];
		if (value === undefined || value === null || value === '') {
			errors.push(`Required field missing: ${field}`);
		}
	});

	return { isValid: errors.length === 0, errors };
}

// =============================================================================
// PATTERN 2: Field Type Validation
// =============================================================================
// Validates that a value matches the expected type.
// Supported types: string, number, boolean, date, email, phone.

/**
 * @param {*} value - Value to validate
 * @param {string} expectedType - One of: string, number, boolean, date, email, phone
 * @returns {boolean}
 */
function validateFieldType(value, expectedType) {
	if (value === undefined || value === null || value === '') return true; // empty values pass type check
	const validator = TYPE_VALIDATORS[expectedType];
	return validator ? validator(value) : true;
}

// =============================================================================
// PATTERN 3: Field Length Validation
// =============================================================================
// Validates string length within min/max bounds.

/**
 * @param {*} value - Value to check length
 * @param {number} [min=0] - Minimum length (inclusive)
 * @param {number} [max=Infinity] - Maximum length (inclusive)
 * @returns {{ isValid: boolean, error: string|null }}
 */
function validateFieldLength(value, min, max) {
	if (value === undefined || value === null || value === '') {
		return min > 0
			? { isValid: false, error: `Value is empty but minimum length is ${min}` }
			: { isValid: true, error: null };
	}

	const len = String(value).length;
	const minLen = min || 0;
	const maxLen = max || Infinity;

	if (len < minLen) {
		return { isValid: false, error: `Length ${len} is below minimum ${minLen}` };
	}
	if (len > maxLen) {
		return { isValid: false, error: `Length ${len} exceeds maximum ${maxLen}` };
	}

	return { isValid: true, error: null };
}

// =============================================================================
// PATTERN 4: Field Format Validation
// =============================================================================
// Validates a value against a named format pattern.
// Supported formats: email, phone, date-YYYY-MM-DD, salesforce-id, zip-code.

/**
 * @param {*} value - Value to validate
 * @param {string} formatName - One of: email, phone, date-YYYY-MM-DD, salesforce-id, zip-code
 * @returns {boolean}
 */
function validateFieldFormat(value, formatName) {
	if (value === undefined || value === null || value === '') return true; // empty values pass format check
	const pattern = FORMAT_PATTERNS[formatName];
	return pattern ? pattern.test(String(value)) : true;
}

// =============================================================================
// PATTERN 5: Validator Factory
// =============================================================================
// Creates a reusable validator from a field rules configuration array.
// Each rule: { field, required, type, minLength, maxLength, format }

/**
 * @param {Array<{ field: string, required?: boolean, type?: string, minLength?: number, maxLength?: number, format?: string }>} fieldRules
 * @returns {Function} Validator function for use with validateRow/validateBatch
 */
function createValidator(fieldRules) {
	return function validator(row) {
		const errors = [];

		fieldRules.forEach(rule => {
			const value = row[rule.field];
			const fieldLabel = rule.field;

			// Required check
			if (rule.required && (value === undefined || value === null || value === '')) {
				errors.push(`${fieldLabel}: required field is missing`);
				return; // skip further checks for missing required fields
			}

			// Skip remaining checks if value is empty and not required
			if (value === undefined || value === null || value === '') return;

			// Type check
			if (rule.type && !validateFieldType(value, rule.type)) {
				errors.push(`${fieldLabel}: expected type '${rule.type}', got '${typeof value}'`);
			}

			// Length check
			if (rule.minLength !== undefined || rule.maxLength !== undefined) {
				const lengthResult = validateFieldLength(value, rule.minLength, rule.maxLength);
				if (!lengthResult.isValid) {
					errors.push(`${fieldLabel}: ${lengthResult.error}`);
				}
			}

			// Format check
			if (rule.format && !validateFieldFormat(value, rule.format)) {
				errors.push(`${fieldLabel}: does not match format '${rule.format}'`);
			}
		});

		return errors;
	};
}

// =============================================================================
// PATTERN 6: Single Row Validation
// =============================================================================
// Validates a single row using a validator created by createValidator.

/**
 * @param {Object} row - Data row to validate
 * @param {Function} validator - Validator function from createValidator
 * @returns {{ isValid: boolean, errors: string[], validatedRow: Object }}
 */
function validateRow(row, validator) {
	const errors = validator(row);
	return {
		isValid: errors.length === 0,
		errors,
		validatedRow: row
	};
}

// =============================================================================
// PATTERN 7: Batch Validation Pipeline
// =============================================================================
// Validates an array of rows, partitioning into valid and invalid sets.

/**
 * @param {Object[]} rows - Array of data rows
 * @param {Function} validator - Validator function from createValidator
 * @returns {{ valid: Object[], invalid: Array<{ row: Object, rowIndex: number, errors: string[] }>, summary: { total: number, validCount: number, invalidCount: number } }}
 */
function validateBatch(rows, validator) {
	const valid = [];
	const invalid = [];

	rows.forEach((row, index) => {
		const result = validateRow(row, validator);
		if (result.isValid) {
			valid.push(result.validatedRow);
		} else {
			invalid.push({ row, rowIndex: index, errors: result.errors });
		}
	});

	return {
		valid,
		invalid,
		summary: {
			total: rows.length,
			validCount: valid.length,
			invalidCount: invalid.length
		}
	};
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// const fieldRules = [
//     { field: 'AccountName', required: true, type: 'string', maxLength: 255 },
//     { field: 'Email', required: false, type: 'email', format: 'email' },
//     { field: 'Amount', required: true, type: 'number' },
//     { field: 'ExternalId', required: true, format: 'salesforce-id' },
//     { field: 'ZipCode', format: 'zip-code' }
// ];
//
// exports.step = function(input) {
//     const rows = input.csvData || [];
//     const validator = createValidator(fieldRules);
//     const results = validateBatch(rows, validator);
//
//     return {
//         validRecords: results.valid,
//         invalidRecords: results.invalid,
//         summary: results.summary
//     };
// };
