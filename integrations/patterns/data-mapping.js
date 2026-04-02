/**
 * Configurable Data Mapping Patterns for Tray Integration Scripts
 *
 * Reusable patterns for field mapping, transformation rules, and
 * relationship lookups in data processing integrations.
 *
 * Source examples:
 *   - csv-upload/create-orders/script.js (lines 358-1164)
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the field mappings and rule configurations to your integration.
 */

// =============================================================================
// PATTERN 1: Condition-Based Field Rules Engine
// =============================================================================
// Applies transformation rules to field values based on configurable conditions.
// Supports AND/OR condition logic and 10+ transform types.
//
// Rule config structure:
//   {
//       field: 'targetFieldName',
//       rules: [{
//           conditions: [{ field: 'sourceField', operator: 'equals', value: 'X' }],
//           conditionLogic: 'AND' | 'OR',
//           transform: 'toNumber' | 'absolute' | 'concat' | 'replace' | ...,
//           sourceField: 'fieldToRead',
//           value: 'literalOrTemplate'
//       }]
//   }

const CONDITION_OPERATORS = {
	equals: (fieldValue, condValue) => fieldValue === condValue,
	startsWith: (fieldValue, condValue) => typeof fieldValue === 'string' && fieldValue.startsWith(condValue),
	contains: (fieldValue, condValue) => typeof fieldValue === 'string' && fieldValue.includes(condValue),
	isInvalid: (fieldValue) => fieldValue === null || fieldValue === undefined || fieldValue === ''
};

function evaluateConditions(row, conditions, logic) {
	if (!conditions || conditions.length === 0) return true;

	const checker = (condition) => {
		const fieldValue = row[condition.field];
		const operator = CONDITION_OPERATORS[condition.operator];
		return operator ? operator(fieldValue, condition.value) : false;
	};

	return logic === 'AND'
		? conditions.every(checker)
		: conditions.some(checker);
}

/**
 * Safe arithmetic evaluator — replaces eval() for formula strings.
 * Only allows numbers, basic operators (+, -, *, /), parentheses, and whitespace.
 * Throws on any non-arithmetic content.
 *
 * Uses Function() constructor instead of eval() — the whitelist regex above ensures
 * only arithmetic tokens reach execution. Do NOT "simplify" this back to eval().
 * Note: 1e999 passes the regex and evaluates to Infinity; callers should guard
 * against non-finite results if that matters for their use case.
 */
function safeEvaluateArithmetic(expr) {
	const sanitized = String(expr).trim();
	// Reject anything that isn't numbers, operators, parens, dots, or whitespace
	if (/[^0-9+\-*/().eE\s]/.test(sanitized)) {
		throw new Error('Invalid arithmetic expression: ' + sanitized);
	}
	if (sanitized === '') return 0;
	return Function('"use strict"; return (' + sanitized + ')')();
}

const TRANSFORMS = {
	absolute: (input) => {
		const num = parseFloat(input);
		return isNaN(num) ? '0' : Math.abs(num).toString();
	},

	toNumber: (input) => {
		let raw = input;
		if (typeof raw === 'string') {
			raw = raw.trim();
			// Handle accounting negative format: (123.45) -> -123.45
			if (/^\(\d+(\.\d+)?\)$/.test(raw)) {
				raw = '-' + raw.replace(/[()]/g, '');
			}
		}
		const num = parseFloat(raw);
		return isNaN(num) ? '0' : num.toString();
	},

	concat: (input, rule, row) => {
		const template = rule.value || '';
		if (!template) return (input || '').toString();
		return template.replace(/\{([^}]+)\}/g, (match, field) => {
			return (row[field] !== undefined && row[field] !== null) ? row[field] : '';
		});
	},

	replace: (input, rule) => {
		let config = rule.value;
		if (typeof config === 'string') {
			try { config = JSON.parse(config); } catch { config = { search: '', replace: '' }; }
		}
		const str = (input || '').toString();
		return config?.search ? str.split(config.search).join(config.replace || '') : str;
	},

	substring: (input, rule) => {
		let config = rule.value;
		if (typeof config === 'string') {
			try { config = JSON.parse(config); } catch { config = { start: 0 }; }
		}
		const str = (input || '').toString();
		return config.end !== undefined ? str.substring(config.start || 0, config.end) : str.substring(config.start || 0);
	},

	toString: (input) => (input !== undefined && input !== null) ? input.toString() : '',

	calculate: (input, rule, row) => {
		const calc = rule.calculation;
		if (!calc) return '0';

		// Formula-based: replace {FieldName} with values, then evaluate safely
		if (calc.formula) {
			let formula = calc.formula;
			const matches = formula.match(/\{([^}]+)\}/g);
			if (matches) {
				matches.forEach(match => {
					const fieldName = match.slice(1, -1);
					formula = formula.replace(match, parseFloat(row[fieldName]) || 0);
				});
			}
			try { return safeEvaluateArithmetic(formula).toString(); } catch { return '0'; }
		}

		// Multi-operand: { operation, operands: ['field1', 'field2'] }
		if (calc.operands && Array.isArray(calc.operands)) {
			const values = calc.operands.map(f => parseFloat(row[f]) || 0);
			let result = values[0];
			for (let i = 1; i < values.length; i++) {
				switch (calc.operation) {
					case 'add': result += values[i]; break;
					case 'subtract': result -= values[i]; break;
					case 'multiply': result *= values[i]; break;
					case 'divide': result = values[i] === 0 ? 0 : result / values[i]; break;
					case 'min': result = Math.min(result, values[i]); break;
					case 'max': result = Math.max(result, values[i]); break;
					default: return '0';
				}
			}
			return result.toString();
		}

		return '0';
	}
};

function applyFieldRules(row, rules, fieldName) {
	if (!rules) return { value: null, sourceField: null };

	const fieldRuleSet = rules.find(r => r.field === fieldName);
	if (!fieldRuleSet) return { value: null, sourceField: null };

	for (const rule of fieldRuleSet.rules) {
		if (rule.action === 'ignore') continue;

		const logic = rule.conditionLogic || 'OR';
		if (!evaluateConditions(row, rule.conditions, logic)) continue;

		// Get initial input value
		let inputValue = rule.sourceField ? row[rule.sourceField] : null;
		let sourceField = rule.sourceField || null;

		// Apply transform
		const transform = TRANSFORMS[rule.transform];
		if (transform) {
			return { value: transform(inputValue, rule, row), sourceField };
		}

		// No transform: use sourceField or literal value
		if (rule.sourceField) {
			return { value: row[rule.sourceField], sourceField: rule.sourceField };
		}
		if (rule.value !== null && rule.value !== undefined) {
			return { value: rule.value, sourceField: null };
		}
	}

	return { value: null, sourceField: null };
}

// =============================================================================
// PATTERN 2: Relationship Lookup Maps
// =============================================================================
// Creates Map objects for efficient lookups between related objects.
// Supports multiple object types with configurable lookup/return fields.
//
// Relationship config:
//   {
//       lookupObject: 'Account',
//       lookupField: 'External_ID__c',
//       returnField: 'Id',
//       sourceField: 'AccountExternalId'
//   }

function createLookupMaps(relationships, lookupDataSets) {
	const lookupMaps = {};

	relationships.forEach(rel => {
		if (lookupMaps[rel.lookupObject]) return; // already built

		const dataset = lookupDataSets[rel.lookupObject];
		if (!dataset) return;

		const map = new Map();
		dataset.forEach(obj => {
			const key = obj[rel.lookupField];
			if (key) {
				map.set(key, {
					returnValue: obj[rel.returnField],
					fullObject: obj
				});
			}
		});

		lookupMaps[rel.lookupObject] = map;
	});

	return lookupMaps;
}

function lookupValue(lookupMaps, objectType, key) {
	const map = lookupMaps[objectType];
	if (!map) return null;
	const match = map.get(key);
	return match ? match.returnValue : null;
}

function lookupObject(lookupMaps, objectType, key) {
	const map = lookupMaps[objectType];
	if (!map) return null;
	const match = map.get(key);
	return match ? match.fullObject : null;
}

// =============================================================================
// PATTERN 3: Multi-Priority Field Resolution
// =============================================================================
// Resolves field values through a 4-level priority chain:
//   1. Field rules (condition-based transforms)
//   2. Direct source field mapping
//   3. Relationship lookup navigation
//   4. Static value fallback
//
// Mapping config:
//   {
//       targetField: 'ohfy__Amount__c',
//       sourceField: 'Amount',          // priority 2
//       lookupField: 'Account__r.Name', // priority 3
//       staticValue: '0',               // priority 4
//       type: 'number'
//   }

function processField(row, mapping, config, lookupMaps) {
	const { targetField, sourceField, lookupField, type } = mapping;
	let value = '';

	// 1. FIRST PRIORITY: Field rules
	// Empty string ('') is treated as "no result" — rules must return a non-empty
	// value to override lower-priority sources (sourceField, lookup, static).
	const ruleResult = applyFieldRules(row, config.fieldRules, targetField);
	if (ruleResult.value !== null && ruleResult.value !== undefined && ruleResult.value !== '') {
		value = ruleResult.value;
	}
	// 2. SECOND PRIORITY: Direct source field (case-insensitive)
	else if (sourceField) {
		const matchKey = Object.keys(row).find(k => k.toLowerCase() === sourceField.toLowerCase());
		if (matchKey) value = row[matchKey];
	}
	// 3. THIRD PRIORITY: Lookup field navigation (e.g. Account__r.Payment_Terms__c)
	else if (lookupField && lookupMaps) {
		const parts = lookupField.split('.');
		const relType = parts[0].split('__r')[0];

		const relationship = config.relationships?.find(rel =>
			rel.lookupObject === relType
		);

		if (relationship) {
			const sourceValue = row[relationship.sourceField];
			if (sourceValue !== null && sourceValue !== undefined && sourceValue !== '') {
				const obj = lookupObject(lookupMaps, relationship.lookupObject, sourceValue);
				if (obj) {
					// Navigate through relationship path
					let current = obj;
					for (let i = 1; i < parts.length && current; i++) {
						current = current[parts[i]] ?? null;
					}
					value = current ?? '';
				}
			}
		}
	}

	// 4. FOURTH PRIORITY: Static value
	if ((value === '' || value === null || value === undefined) && mapping.staticValue !== undefined) {
		value = mapping.staticValue;
	}

	return { value, type: type || 'string' };
}

// =============================================================================
// PATTERN 4: Batch Field Processing
// =============================================================================
// Processes all fields in a mapping config for a single data row.

function processRow(row, fieldMappings, config, lookupMaps) {
	const result = {};
	const errors = [];

	fieldMappings.forEach(mapping => {
		const { value, type } = processField(row, mapping, config, lookupMaps);

		if (mapping.required && (value === '' || value === null || value === undefined)) {
			errors.push({
				field: mapping.targetField,
				message: `Required field missing: ${mapping.targetField}`
			});
		}

		result[mapping.targetField] = value;
	});

	return { result, errors, isValid: errors.length === 0 };
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// const fieldMappings = [
//     { targetField: 'ohfy__Account__c', sourceField: 'CustomerID', required: true },
//     { targetField: 'ohfy__Amount__c', sourceField: 'Total', type: 'number' },
//     { targetField: 'ohfy__Status__c', staticValue: 'Draft' }
// ];
//
// const fieldRules = [
//     {
//         field: 'ohfy__Amount__c',
//         rules: [{
//             conditions: [{ field: 'Type', operator: 'equals', value: 'Credit' }],
//             transform: 'absolute',
//             sourceField: 'Total'
//         }]
//     }
// ];
//
// exports.step = function(input) {
//     const rows = input.csvData || [];
//     const config = { fieldRules, relationships: [], fieldMapping: fieldMappings };
//     const lookupMaps = createLookupMaps(config.relationships, input.lookupData || {});
//
//     const processed = rows.map(row => processRow(row, fieldMappings, config, lookupMaps));
//     return {
//         records: processed.filter(r => r.isValid).map(r => r.result),
//         errors: processed.filter(r => !r.isValid).flatMap(r => r.errors)
//     };
// };
