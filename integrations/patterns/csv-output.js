/**
 * CSV / Fixed-Width Output Patterns for Tray Integration Scripts
 *
 * Reusable patterns for generating structured output: fixed-width records,
 * dynamic column definitions, and type-specific field formatting.
 *
 * Source examples:
 *   - vip-srs/generate-file-name-and-header/script.js
 *   - vip-srs/convert-srs-to-csv/script.js
 *   - distributor-placements/VIP Placements/formatPlacements/script.js
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the field configurations to your integration's requirements.
 */

// =============================================================================
// PATTERN 1: Type-Specific Field Formatters
// =============================================================================
// Formatters for fixed-width output fields. Each pads/truncates to exact size.
// Types: A (alpha), D (date YYYYMMDD), T (time HHMMSS), N (numeric zero-padded)

const formatters = {
	formatAlpha: (value, size) => {
		if (!value) return ' '.repeat(size);
		return value.toString().trim().padEnd(size, ' ').substring(0, size);
	},

	formatDate: (value, size) => {
		if (!value) return '0'.repeat(size);
		if (typeof value === 'string' && value.length === size && /^\d+$/.test(value)) {
			return value;
		}
		try {
			const date = new Date(value);
			if (isNaN(date.getTime())) return '0'.repeat(size);
			const formatted = date.getFullYear().toString() +
				(date.getMonth() + 1).toString().padStart(2, '0') +
				date.getDate().toString().padStart(2, '0');
			return formatted.padStart(size, '0').slice(-size);
		} catch {
			return '0'.repeat(size);
		}
	},

	formatTime: (value, size) => {
		if (!value) return '0'.repeat(size);
		if (typeof value === 'string' && value.length === size && /^\d+$/.test(value)) {
			return value;
		}
		try {
			const date = new Date(value);
			if (isNaN(date.getTime())) return '0'.repeat(size);
			const formatted = date.getHours().toString().padStart(2, '0') +
				date.getMinutes().toString().padStart(2, '0') +
				date.getSeconds().toString().padStart(2, '0');
			return formatted.slice(-size);
		} catch {
			return '0'.repeat(size);
		}
	},

	formatNumeric: (value, size) => {
		if (value === null || value === undefined || value === '') return '0'.repeat(size);
		return value.toString().padStart(size, '0').slice(-size);
	}
};

function formatField(field, value) {
	switch (field.type) {
		case 'A': return formatters.formatAlpha(value, field.size);
		case 'D': return formatters.formatDate(value, field.size);
		case 'T': return formatters.formatTime(value, field.size);
		case 'N': return formatters.formatNumeric(value, field.size);
		default: return ' '.repeat(field.size);
	}
}

// =============================================================================
// PATTERN 2: Configuration-Driven Header/Record Generation
// =============================================================================
// Generates fixed-width records from a field configuration array.
// Each field config specifies: { name, size, type, value? }
// If value is set, it's used as a static value; otherwise resolved from data.
//
// Example config:
//   const fields = [
//       { name: 'RECID', value: '01', size: 2, type: 'A' },
//       { name: 'SUPPID', size: 3, type: 'A' },
//       { name: 'CRTDATE', size: 8, type: 'D' }
//   ];

function generateRecord(fields, dataResolver) {
	let recordString = '';
	const transformations = [];

	fields.forEach(field => {
		const value = field.value !== undefined ? field.value : dataResolver(field.name);
		const formattedValue = formatField(field, value);
		recordString += formattedValue;

		transformations.push({
			fieldName: field.name,
			inputValue: value,
			outputValue: formattedValue,
			fieldType: field.type,
			fieldSize: field.size
		});
	});

	return { recordString, transformations };
}

function validateRecordLength(recordString, fields) {
	const expectedLength = fields.reduce((sum, field) => sum + field.size, 0);
	return {
		actualLength: recordString.length,
		expectedLength,
		isValid: recordString.length === expectedLength,
		errors: recordString.length !== expectedLength
			? [`Length mismatch: expected ${expectedLength}, got ${recordString.length}`]
			: []
	};
}

// =============================================================================
// PATTERN 3: Fixed-Position Text Parsing
// =============================================================================
// Parses fixed-width text lines into structured data using position specs.
//
// Example spec:
//   const fieldSpecs = [
//       { name: 'RECID', start: 0, end: 2 },
//       { name: 'SUPPID', start: 2, end: 5 },
//       { name: 'DISTID', start: 5, end: 13 }
//   ];

function parseFixedWidth(lines, fieldSpecs, filterFn) {
	const filteredLines = filterFn ? lines.filter(filterFn) : lines;

	const columns = fieldSpecs.map(field => ({
		name: field.name,
		type: field.type || 'string'
	}));

	const data = filteredLines.map(line => {
		const record = {};
		fieldSpecs.forEach(field => {
			record[field.name] = line.substring(field.start, field.end).trim();
		});
		return record;
	});

	return { columns, data };
}

// =============================================================================
// PATTERN 4: Dynamic Column Definitions
// =============================================================================
// Generates column metadata for CSV output with configurable field inclusion.
//
// Returns { columns: [{name, type}], getRow: (record) => [...values] }

function createColumnDefinitions(fieldDefs, options = {}) {
	const { prefix = '', includeOptional = {} } = options;

	const activeFields = Object.entries(fieldDefs)
		.filter(([key, def]) => {
			if (def.optional) return includeOptional[key] === true;
			return true;
		})
		.map(([key, def]) => ({
			key,
			name: prefix ? `${prefix}${def.name}` : def.name,
			type: def.type || 'text'
		}));

	return {
		columns: activeFields.map(f => ({ name: f.name, type: f.type })),
		getRow: (record) => activeFields.map(f => record[f.key] ?? '')
	};
}

// =============================================================================
// PATTERN 5: Delimited CSV String Generation
// =============================================================================
// Generates a comma-delimited (or custom delimiter) CSV string from columns
// and row data. Handles quoting of values containing the delimiter, quotes,
// or newlines.

/**
 * @param {Array<{ name: string }>} columns - Column definitions (header names)
 * @param {Array<Array>} rows - Array of row arrays (values in column order)
 * @param {string} [delimiter=','] - Field delimiter character
 * @returns {string} Complete CSV string with header row and data rows
 */
function generateCsvString(columns, rows, delimiter) {
	const delim = delimiter || ',';

	function escapeField(value) {
		if (value === undefined || value === null) return '';
		const str = String(value);
		// Quote if contains delimiter, double quote, or newline
		if (str.indexOf(delim) !== -1 || str.indexOf('"') !== -1 || str.indexOf('\n') !== -1) {
			return '"' + str.replace(/"/g, '""') + '"';
		}
		return str;
	}

	const headerRow = columns.map(col => escapeField(col.name)).join(delim);

	const dataRows = (rows || []).map(row => {
		return (Array.isArray(row) ? row : []).map(value => escapeField(value)).join(delim);
	});

	return [headerRow].concat(dataRows).join('\n');
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// // Fixed-width record generation
// const headerFields = [
//     { name: 'RECID', value: '01', size: 2, type: 'A' },
//     { name: 'SUPPID', size: 3, type: 'A' },
//     { name: 'CRTDATE', size: 8, type: 'D' }
// ];
//
// exports.step = function(input) {
//     const { recordString, transformations } = generateRecord(
//         headerFields,
//         (fieldName) => input.data[fieldName]
//     );
//     const validation = validateRecordLength(recordString, headerFields);
//     return { header: recordString, validation, transformations };
// };
//
// // Fixed-width text parsing
// exports.step = function(input) {
//     const specs = [
//         { name: 'RECID', start: 0, end: 2 },
//         { name: 'SUPPID', start: 2, end: 5 }
//     ];
//     const lines = input.fileContent.split('\n');
//     return parseFixedWidth(lines, specs, line => line.startsWith('21'));
// };
//
// // Delimited CSV output
// exports.step = function(input) {
//     const columns = [{ name: 'Name' }, { name: 'Amount' }, { name: 'Date' }];
//     const rows = input.records.map(r => [r.Name, r.Amount, r.Date]);
//     return { csvString: generateCsvString(columns, rows) };
// };
