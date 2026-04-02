/**
 * Error Handling Patterns for Tray Integration Scripts
 *
 * Reusable patterns for extracting, normalizing, and standardizing errors
 * from Salesforce composite API responses and batch operations.
 *
 * Source examples:
 *   - fintech/remittanceProcessing/processBatchUpdateResults/script.js
 *   - ware2go/2GP/orders/processBatchCreateErrors/script.js
 *
 * Usage: Copy the pattern(s) you need into your script.js and adapt
 * the service name and error type mappings to your integration.
 */

// =============================================================================
// PATTERN 1: Salesforce Composite Batch Error Extraction
// =============================================================================
// Extracts and flattens errors from Salesforce composite API batch responses.
// Each result in the array may contain multiple errors.

function hasErrors(result) {
	return !result.success && result.errors && result.errors.length > 0;
}

function extractErrorsFromResult(result, resultIndex) {
	return result.errors.map((error, errorIndex) => ({
		...error,
		resultIndex,
		errorIndex
	}));
}

function extractAllErrors(results) {
	return results
		.map((result, index) => ({ result, index }))
		.filter(({ result }) => hasErrors(result))
		.flatMap(({ result, index }) => extractErrorsFromResult(result, index));
}

// =============================================================================
// PATTERN 2: Salesforce Status Code to Error Type Mapping
// =============================================================================
// Maps Salesforce statusCode values to standardized error type names.
// Extend this mapping as new error codes are encountered.

const SF_ERROR_TYPE_MAP = {
	// Cross Reference & ID Errors
	'INVALID_CROSS_REFERENCE_KEY': 'InvalidCrossReferenceKey',
	'INVALID_ID_FIELD': 'InvalidIdField',
	'MALFORMED_ID': 'MalformedId',
	'INVALID_ID': 'InvalidId',

	// Field Validation Errors
	'REQUIRED_FIELD_MISSING': 'RequiredFieldMissing',
	'FIELD_CUSTOM_VALIDATION_EXCEPTION': 'FieldCustomValidationException',
	'INVALID_FIELD_FOR_INSERT_UPDATE': 'InvalidFieldForInsertUpdate',
	'INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST': 'InvalidOrNullForRestrictedPicklist',
	'INVALID_EMAIL_ADDRESS': 'InvalidEmailAddress',

	// Data Type & Format Errors
	'STRING_TOO_LONG': 'StringTooLong',
	'NUMBER_OUTSIDE_VALID_RANGE': 'NumberOutsideValidRange',
	'INVALID_TYPE': 'InvalidType',
	'INVALID_DATE_FORMAT': 'InvalidDateFormat',

	// Duplicate & Uniqueness Errors
	'DUPLICATE_VALUE': 'DuplicateValue',
	'DUPLICATE_EXTERNAL_ID': 'DuplicateExternalId',

	// Permission & Access Errors
	'INSUFFICIENT_ACCESS_OR_READONLY': 'InsufficientAccessOrReadonly',
	'FIELD_NOT_UPDATEABLE': 'FieldNotUpdateable',
	'ENTITY_IS_DELETED': 'EntityIsDeleted',

	// Business Rule & Workflow Errors
	'VALIDATION_RULE_FAILED': 'ValidationRuleFailed',
	'TRIGGER_EXCEPTION': 'TriggerException',
	'APEX_TRIGGER_EXCEPTION': 'ApexTriggerException',

	// Limit & Quota Errors
	'REQUEST_LIMIT_EXCEEDED': 'RequestLimitExceeded',
	'TOO_MANY_RECORDS': 'TooManyRecords',

	// Generic Fallbacks
	'UNKNOWN_EXCEPTION': 'UnknownException'
};

function mapStatusCodeToType(statusCode) {
	return SF_ERROR_TYPE_MAP[statusCode] || 'UnknownError';
}

// =============================================================================
// PATTERN 3: Standardized Error Object Format
// =============================================================================
// Creates the Ohanafy standard error object structure used across all
// integrations for consistent error reporting and logging.
//
// Structure:
//   { error: { response: { body: { Type, Message } }, message, statusCode }, id, service }

function createStandardizedError(error, serviceName) {
	return {
		error: {
			response: {
				body: {
					Type: mapStatusCodeToType(error.statusCode),
					Message: error.message || 'Unknown error'
				}
			},
			message: `Batch error (Result #${error.resultIndex + 1}, Error #${error.errorIndex + 1}): ${error.message}`,
			statusCode: 500
		},
		id: `Batch Result #${error.resultIndex + 1}`,
		service: serviceName
	};
}

function transformToStandardizedFormat(errors, serviceName) {
	return errors.map(error => createStandardizedError(error, serviceName));
}

// =============================================================================
// PATTERN 4: Simple Batch Error Normalization (Flat)
// =============================================================================
// Lightweight pattern for normalizing batch errors when you don't need
// the full status code mapping. Filters out successes and flattens errors.

function normalizeBatchErrors(records, serviceName) {
	return records.flatMap((record) => {
		if (record?.success === true) return [];
		const errs = Array.isArray(record?.errors) ? record.errors : [];
		return errs.map((e) => ({
			error: {
				response: {
					body: {
						Type: e?.statusCode || 'UNKNOWN',
						Message: e?.message || 'Unknown error'
					}
				},
				message: e?.statusCode || 'UNKNOWN',
				statusCode: 500
			},
			id: e?.message || 'Unknown',
			service: serviceName
		}));
	});
}

// =============================================================================
// PATTERN 5: Full Pipeline (extract -> map -> standardize)
// =============================================================================
// Combines patterns 1-3 into a single function for Salesforce composite results.

function processBatchErrors(results, serviceName) {
	const allErrors = extractAllErrors(results);
	return transformToStandardizedFormat(allErrors, serviceName);
}

// =============================================================================
// PATTERN 6: SOAP/XML Error Extraction
// =============================================================================
// Extracts error details from SOAP fault responses. Handles the nested
// fault structure commonly returned by Salesforce SOAP API and partner WSDL.

function extractSoapErrors(soapResponse, serviceName) {
	if (!soapResponse) return [];

	const faultString = soapResponse.faultstring || soapResponse.faultString || '';
	const faultCode = soapResponse.faultcode || soapResponse.faultCode || 'SOAP_FAULT';
	const detail = soapResponse.detail || soapResponse.Detail || {};

	// Extract nested exception details if available
	const exceptionCode = detail.exceptionCode || detail.ExceptionCode || faultCode;
	const exceptionMessage = detail.exceptionMessage || detail.ExceptionMessage || faultString;

	if (!faultString && !exceptionMessage) return [];

	return [{
		error: {
			response: {
				body: {
					Type: mapStatusCodeToType(exceptionCode) !== 'UnknownError'
						? mapStatusCodeToType(exceptionCode)
						: exceptionCode,
					Message: exceptionMessage || faultString
				}
			},
			message: `SOAP Fault: ${exceptionMessage || faultString}`,
			statusCode: 500
		},
		id: faultCode,
		service: serviceName || 'Unknown'
	}];
}

// =============================================================================
// PATTERN 7: Unmatched/Duplicate Record Error Factory
// =============================================================================
// Creates standardized error objects for records that failed to match during
// lookup operations (e.g., external ID not found, duplicate detection).

function createUnmatchedError(record, identifierField, serviceName, reason) {
	const identifier = record && identifierField ? (record[identifierField] || 'Unknown') : 'Unknown';
	const errorReason = reason || 'No matching record found';

	return {
		error: {
			response: {
				body: {
					Type: 'UnmatchedRecord',
					Message: `${errorReason}: ${identifierField}=${identifier}`
				}
			},
			message: `${errorReason}: ${identifierField}=${identifier}`,
			statusCode: 404
		},
		id: identifier,
		service: serviceName || 'Unknown'
	};
}

// =============================================================================
// PATTERN 8: Validation-to-Error Bridge
// =============================================================================
// Converts validation result errors (from validation.js patterns) into the
// Ohanafy standard error format for unified error reporting.

function convertValidationErrors(validationResults, serviceName) {
	if (!Array.isArray(validationResults)) return [];

	return validationResults
		.filter(item => !item.isValid || (item.errors && item.errors.length > 0))
		.map(item => {
			const errors = item.errors || [];
			const rowId = item.rowIndex !== undefined ? `Row ${item.rowIndex}` : 'Unknown';

			return {
				error: {
					response: {
						body: {
							Type: 'ValidationError',
							Message: errors.join('; ')
						}
					},
					message: `Validation failed for ${rowId}: ${errors.join('; ')}`,
					statusCode: 400
				},
				id: rowId,
				service: serviceName || 'Unknown'
			};
		});
}

// =============================================================================
// EXAMPLE: Using in a Tray script
// =============================================================================
//
// exports.step = function(input, fileInput) {
//     const results = input.results || [];
//     const errors = processBatchErrors(results, "My Integration Name");
//     return {
//         errors,
//         summary: {
//             total_errors: errors.length,
//             total_failed: results.filter(r => !r.success).length,
//             total_operations: results.length
//         }
//     };
// };
//
// // SOAP error extraction:
// // const soapErrors = extractSoapErrors(input.soapFault, "My Integration");
//
// // Unmatched record errors:
// // const unmatchedErrors = unmatchedRecords.map(r =>
// //     createUnmatchedError(r, 'External_ID__c', 'My Integration')
// // );
//
// // Validation-to-error bridge:
// // const valErrors = convertValidationErrors(validationResults, "My Integration");
