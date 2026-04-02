/**
 * String Manipulation Patterns for Tray Integration Scripts
 *
 * Reusable patterns for business name normalization, address cleaning,
 * proper casing, padding, diacritics removal, and SOQL/Composite URL sanitization.
 *
 * Source examples:
 *   - distributor-placements/VIP Placements/formatAccounts/script.js (lines 67-74)
 *   - distributor-placements/VIP Placements/formatDistributors/script.js
 *   - ware2go/transformOrders/script.js (line 114)
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * to your integration's requirements.
 */

// =============================================================================
// CONSTANTS
// =============================================================================

const BUSINESS_SUFFIXES = {
	'llc': 'LLC',
	'l.l.c.': 'LLC',
	'inc': 'Inc.',
	'inc.': 'Inc.',
	'corp': 'Corp.',
	'corp.': 'Corp.',
	'ltd': 'Ltd.',
	'ltd.': 'Ltd.',
	'co': 'Co.',
	'co.': 'Co.',
	'lp': 'LP',
	'l.p.': 'LP',
	'llp': 'LLP',
	'l.l.p.': 'LLP',
	'dba': 'DBA',
	'd.b.a.': 'DBA'
};

const PHONE_FORMATS = {
	'US': (digits) => `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`,
	'E164': (digits) => `+1${digits.slice(0, 10)}`,
	'plain': (digits) => digits
};

// =============================================================================
// PATTERN 1: Proper Case / Title Case
// =============================================================================
// Converts a string to title case (first letter of each word capitalized).
// Handles null/undefined safely.

/**
 * @param {string} str - Input string
 * @returns {string} Title-cased string
 */
function toProperCase(str) {
	if (!str) return '';
	return str
		.toLowerCase()
		.split(' ')
		.map(word => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ');
}

// =============================================================================
// PATTERN 2: Business Name Normalization
// =============================================================================
// Trims, proper-cases, normalizes whitespace, and standardizes common
// business suffixes (LLC, Inc., Corp., etc.).

/**
 * @param {string} name - Business name to normalize
 * @returns {string} Normalized business name
 */
function normalizeBusinessName(name) {
	if (!name) return '';

	// Trim and collapse whitespace
	let normalized = name.trim().replace(/\s+/g, ' ');

	// Proper case each word
	normalized = toProperCase(normalized);

	// Standardize business suffixes
	const words = normalized.split(' ');
	const lastWord = words[words.length - 1].toLowerCase().replace(/[.,]$/g, '');

	if (BUSINESS_SUFFIXES[lastWord]) {
		words[words.length - 1] = BUSINESS_SUFFIXES[lastWord];
	}

	return words.join(' ');
}

// =============================================================================
// PATTERN 3: Address Formatting
// =============================================================================
// Concatenates address components, filtering out blank/falsy parts.

/**
 * @param {Object} parts - Address components { line1, line2, city, state, zip, country }
 * @returns {string} Formatted address string
 */
function formatAddress(parts) {
	if (!parts) return '';

	const street = [parts.line1, parts.line2].filter(Boolean).join(' ');

	// Build city/state together to avoid double-space when both are present
	let cityState = '';
	if (parts.city && parts.state) {
		cityState = parts.city + ', ' + parts.state;
	} else {
		cityState = parts.city || parts.state || '';
	}
	const cityStateZip = [cityState, parts.zip].filter(Boolean).join(' ');

	return [street, cityStateZip, parts.country].filter(Boolean).join(', ');
}

// =============================================================================
// PATTERN 4: Configurable String Cleaner
// =============================================================================
// Applies a configurable set of cleaning operations to a string value.

/**
 * @param {*} value - Value to clean
 * @param {Object} [options] - Cleaning options
 * @param {boolean} [options.trim=true] - Trim whitespace
 * @param {boolean} [options.collapseWhitespace=false] - Collapse multiple spaces to one
 * @param {boolean} [options.removeDiacritics=false] - Strip diacritical marks
 * @param {boolean} [options.stripNonPrintable=false] - Remove non-printable characters
 * @param {number} [options.maxLength] - Truncate to max length
 * @returns {string}
 */
function cleanString(value, options) {
	if (value === undefined || value === null) return '';

	let str = String(value);
	const opts = options || {};

	if (opts.trim !== false) str = str.trim();
	if (opts.collapseWhitespace) str = str.replace(/\s+/g, ' ');
	if (opts.removeDiacritics) str = removeDiacritics(str);
	if (opts.stripNonPrintable) str = str.replace(/[^\x20-\x7E]/g, '');
	if (opts.maxLength && str.length > opts.maxLength) str = str.substring(0, opts.maxLength);

	return str;
}

// =============================================================================
// PATTERN 5: Field Padding
// =============================================================================
// Left or right pads a value to a fixed length, with optional truncation.

/**
 * @param {*} value - Value to pad
 * @param {number} length - Target length
 * @param {string} [char=' '] - Pad character
 * @param {string} [direction='right'] - 'left' or 'right'
 * @returns {string}
 */
function padField(value, length, char, direction) {
	const str = value !== undefined && value !== null ? String(value) : '';
	const padChar = char || ' ';
	const dir = direction || 'right';

	const padded = dir === 'left'
		? str.padStart(length, padChar)
		: str.padEnd(length, padChar);

	return padded.substring(0, length);
}

// =============================================================================
// PATTERN 6: Strip Leading Zeros
// =============================================================================
// Removes leading zeros from a string value while preserving at least one digit.

/**
 * @param {*} value - Value to strip
 * @returns {string}
 */
function stripLeadingZeros(value) {
	if (!value) return '0';
	const str = String(value).replace(/^0+/, '');
	return str || '0';
}

// =============================================================================
// PATTERN 7: Phone Number Formatting
// =============================================================================
// Extracts digits from a phone string and applies a named format.

/**
 * @param {string} phone - Raw phone number string
 * @param {string} [format='US'] - Format name: 'US', 'E164', 'plain'
 * @returns {string}
 */
function formatPhoneNumber(phone, format) {
	if (!phone) return '';

	const digits = String(phone).replace(/\D/g, '');
	// Strip leading 1 for US numbers
	const normalized = digits.length === 11 && digits.startsWith('1')
		? digits.substring(1)
		: digits;

	if (normalized.length < 7) return phone; // return original if too short

	const formatter = PHONE_FORMATS[format || 'US'];
	return formatter ? formatter(normalized) : normalized;
}

// =============================================================================
// PATTERN 8: SOQL Value Sanitization
// =============================================================================
// Escapes single quotes for safe use in SOQL queries.

/**
 * @param {*} value - Value to sanitize
 * @returns {string}
 */
function sanitizeForSoql(value) {
	if (value === undefined || value === null) return '';
	return String(value).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

// =============================================================================
// PATTERN 9: Salesforce Composite URL Sanitization
// =============================================================================
// Encodes special characters for Salesforce Composite API URL segments.

/**
 * @param {*} value - Value to sanitize for URL segment
 * @returns {string}
 */
function sanitizeForCompositeUrl(value) {
	if (value === undefined || value === null) return '';
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

// =============================================================================
// PATTERN 10: Diacritics Removal
// =============================================================================
// Removes diacritical marks using NFD Unicode normalization.

/**
 * @param {string} str - Input string with potential diacritics
 * @returns {string} String with diacritics removed
 */
function removeDiacritics(str) {
	if (!str) return '';
	return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// exports.step = function(input) {
//     const accounts = input.accounts || [];
//
//     const formatted = accounts.map(acct => ({
//         Name: normalizeBusinessName(acct.name),
//         BillingAddress: formatAddress({
//             line1: acct.address1,
//             line2: acct.address2,
//             city: acct.city,
//             state: acct.state,
//             zip: acct.zip
//         }),
//         Phone: formatPhoneNumber(acct.phone, 'US'),
//         External_ID__c: sanitizeForCompositeUrl(acct.externalId)
//     }));
//
//     return { accounts: formatted, count: formatted.length };
// };
