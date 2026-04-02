/**
 * Date/Time Patterns for Tray Integration Scripts
 *
 * Reusable patterns for date parsing, Salesforce date formatting,
 * timezone conversion, and date math — all without external libraries.
 *
 * Source examples:
 *   - shopify/Shopify_Orders/formatDate/script.js
 *   - shopify/transformOrders/script.js (lines 276-291)
 *   - BJs_Workday_Reverse_JE/1-convert_time/script.js
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * to your integration's date handling requirements.
 */

// =============================================================================
// PATTERN 1: Date Validation
// =============================================================================
// Checks if a value can be parsed into a valid Date object.

/**
 * @param {*} dateString - Value to check
 * @returns {boolean} True if value represents a valid date
 */
function isValidDate(dateString) {
	if (!dateString) return false;
	var d = new Date(dateString);
	return !isNaN(d.getTime());
}

// =============================================================================
// PATTERN 2: Flexible Date Parsing
// =============================================================================
// Parses date strings in multiple common formats:
// MM/DD/YYYY, DD/MM/YYYY (when day > 12), YYYY-MM-DD, ISO strings, Date objects.
// Returns a Date object or null on failure.

/**
 * @param {*} value - Date value to parse
 * @returns {Date|null} Parsed Date object or null
 */
function parseDateFlexible(value) {
	if (!value) return null;
	if (value instanceof Date) return isNaN(value.getTime()) ? null : value;

	var str = String(value).trim();

	// YYYY-MM-DD or ISO string
	if (/^\d{4}-\d{2}-\d{2}/.test(str)) {
		var d = new Date(str);
		return isNaN(d.getTime()) ? null : d;
	}

	// MM/DD/YYYY or DD/MM/YYYY
	var slashMatch = str.match(/^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$/);
	if (slashMatch) {
		var a = parseInt(slashMatch[1], 10);
		var b = parseInt(slashMatch[2], 10);
		var year = parseInt(slashMatch[3], 10);

		var month, day;
		if (a > 12) {
			// DD/MM/YYYY (day first)
			day = a;
			month = b;
		} else {
			// MM/DD/YYYY (month first — US default)
			month = a;
			day = b;
		}

		var result = new Date(year, month - 1, day);
		if (result.getFullYear() === year && result.getMonth() === month - 1 && result.getDate() === day) {
			return result;
		}
		return null;
	}

	// Fallback: try native parsing
	var fallback = new Date(str);
	return isNaN(fallback.getTime()) ? null : fallback;
}

// =============================================================================
// PATTERN 3: Salesforce Date Format (YYYY-MM-DD)
// =============================================================================
// Formats a date value to Salesforce Date field format.

/**
 * @param {*} value - Date value to format
 * @returns {string} Date in YYYY-MM-DD format, or empty string on failure
 */
function formatSalesforceDate(value) {
	var date = parseDateFlexible(value);
	if (!date) return '';

	var parts = formatDateParts(date);
	return parts.year + '-' + parts.month + '-' + parts.day;
}

// =============================================================================
// PATTERN 4: Salesforce DateTime Format (YYYY-MM-DDTHH:mm:ss.000Z)
// =============================================================================
// Formats a date value to Salesforce DateTime field format (ISO 8601).

/**
 * @param {*} value - Date value to format
 * @returns {string} DateTime in YYYY-MM-DDTHH:mm:ss.000Z format, or empty string
 */
function formatSalesforceDateTime(value) {
	var date = parseDateFlexible(value);
	if (!date) return '';

	return date.toISOString();
}

// =============================================================================
// PATTERN 5: Offset-Based Timezone Conversion
// =============================================================================
// Converts a date string between timezone offsets without external libraries.

/**
 * @param {*} dateString - Date value to convert
 * @param {number} fromOffsetHours - Source timezone offset in hours (e.g., -5 for EST)
 * @param {number} toOffsetHours - Target timezone offset in hours (e.g., -8 for PST)
 * @returns {string} ISO string in the target timezone, or empty string
 */
function convertTimezone(dateString, fromOffsetHours, toOffsetHours) {
	var date = parseDateFlexible(dateString);
	if (!date) return '';

	var diffMs = (toOffsetHours - fromOffsetHours) * 60 * 60 * 1000;
	var converted = new Date(date.getTime() + diffMs);

	return converted.toISOString();
}

// =============================================================================
// PATTERN 6: Date Arithmetic
// =============================================================================
// Adds or subtracts a specified amount from a date value.
// Supports units: days, months, hours, minutes.

/**
 * @param {*} dateString - Base date value
 * @param {number} amount - Amount to add (negative to subtract)
 * @param {string} unit - Unit: 'days', 'months', 'hours', 'minutes'
 * @returns {string} ISO string of the resulting date, or empty string
 */
function dateAdd(dateString, amount, unit) {
	var date = parseDateFlexible(dateString);
	if (!date) return '';

	var result = new Date(date.getTime());

	switch (unit) {
		case 'days':
			result.setDate(result.getDate() + amount);
			break;
		case 'months':
			result.setMonth(result.getMonth() + amount);
			break;
		case 'hours':
			result.setHours(result.getHours() + amount);
			break;
		case 'minutes':
			result.setMinutes(result.getMinutes() + amount);
			break;
		default:
			return '';
	}

	return result.toISOString();
}

// =============================================================================
// PATTERN 7: Zero-Padded Date Parts
// =============================================================================
// Extracts year, month, day, hours, minutes, seconds as zero-padded strings.

/**
 * @param {Date} date - Date object
 * @returns {{ year: string, month: string, day: string, hours: string, minutes: string, seconds: string }}
 */
function formatDateParts(date) {
	return {
		year: date.getFullYear().toString(),
		month: (date.getMonth() + 1).toString().padStart(2, '0'),
		day: date.getDate().toString().padStart(2, '0'),
		hours: date.getHours().toString().padStart(2, '0'),
		minutes: date.getMinutes().toString().padStart(2, '0'),
		seconds: date.getSeconds().toString().padStart(2, '0')
	};
}

// =============================================================================
// PATTERN 8: Compact Date Format (YYYYMMDD)
// =============================================================================
// Formats a date as an 8-character compact string for fixed-width file output.

/**
 * @param {*} value - Date value to format
 * @returns {string} 8-char date string (YYYYMMDD), or '00000000' on failure
 */
function formatYYYYMMDD(value) {
	var date = parseDateFlexible(value);
	if (!date) return '00000000';

	var parts = formatDateParts(date);
	return parts.year + parts.month + parts.day;
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// exports.step = function(input) {
//     const orders = input.orders || [];
//
//     const formatted = orders.map(order => ({
//         ...order,
//         OrderDate: formatSalesforceDate(order.created_at),
//         ProcessedAt: formatSalesforceDateTime(order.processed_at),
//         ShipByDate: dateAdd(order.created_at, 3, 'days'),
//         FileDate: formatYYYYMMDD(order.created_at)
//     }));
//
//     return {
//         orders: formatted,
//         orderCount: formatted.length,
//         processedDate: formatSalesforceDate(new Date())
//     };
// };
