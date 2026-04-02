---
paths: ["01-tray/**"]
alwaysApply: true
---

# Tray.ai Error Handling Standards

## Error Handling Standard
```javascript
const ERROR_TYPES = {
    VALIDATION_FAILED: 'ValidationFailed',
    PROCESSING_ERROR: 'ProcessingError',
    DATA_TRANSFORMATION_ERROR: 'DataTransformationError'
};

function createErrorResponse(errorType, message, context) {
    return {
        success: false,
        error: { type: errorType, message, context, timestamp: new Date().toISOString() }
    };
}
```

## Salesforce Composite/Batch Request Response Handling

**CRITICAL**: All scripts processing Salesforce composite or batch API responses MUST follow this pattern.

Reference implementation: `/Embedded/Shopify_2GP/versions/current/scripts/scripts/Shopify_02_Products/2-execute_script/script.js`

### Required Error Types for Salesforce APIs
```javascript
const ERROR_TYPES = {
    VALIDATION_FAILED: 'ValidationFailed',
    PROCESSING_ERROR: 'ProcessingError',
    DATA_TRANSFORMATION_ERROR: 'DataTransformationError',
    SALESFORCE_API_ERROR: 'SalesforceApiError',
    AUTHENTICATION_ERROR: 'AuthenticationError',
    AUTHORIZATION_ERROR: 'AuthorizationError',
    RESOURCE_NOT_FOUND: 'ResourceNotFound',
    RATE_LIMIT_ERROR: 'RateLimitError',
    SERVER_ERROR: 'ServerError',
    SERVICE_UNAVAILABLE: 'ServiceUnavailable',
    RECORD_LOCK_ERROR: 'RecordLockError',
    DUPLICATE_ERROR: 'DuplicateError',
    BATCH_ERROR: 'BatchError',
    TIMEOUT_ERROR: 'TimeoutError'
};

// HTTP Status Code to Error Type mapping
const HTTP_STATUS_TO_ERROR_TYPE = {
    400: ERROR_TYPES.VALIDATION_FAILED,
    401: ERROR_TYPES.AUTHENTICATION_ERROR,
    403: ERROR_TYPES.AUTHORIZATION_ERROR,
    404: ERROR_TYPES.RESOURCE_NOT_FOUND,
    405: ERROR_TYPES.VALIDATION_FAILED,
    409: ERROR_TYPES.DUPLICATE_ERROR,
    412: ERROR_TYPES.BATCH_ERROR,
    415: ERROR_TYPES.VALIDATION_FAILED,
    500: ERROR_TYPES.SERVER_ERROR,
    502: ERROR_TYPES.SERVER_ERROR,
    503: ERROR_TYPES.SERVICE_UNAVAILABLE
};

// Salesforce-specific error code mappings
const SALESFORCE_ERROR_CODES = {
    INVALID_SESSION_ID: ERROR_TYPES.AUTHENTICATION_ERROR,
    REQUEST_LIMIT_EXCEEDED: ERROR_TYPES.RATE_LIMIT_ERROR,
    UNABLE_TO_LOCK_ROW: ERROR_TYPES.RECORD_LOCK_ERROR,
    DUPLICATE_VALUE: ERROR_TYPES.DUPLICATE_ERROR,
    ENTITY_IS_DELETED: ERROR_TYPES.RESOURCE_NOT_FOUND,
    REQUIRED_FIELD_MISSING: ERROR_TYPES.VALIDATION_FAILED,
    INVALID_FIELD: ERROR_TYPES.VALIDATION_FAILED,
    MALFORMED_ID: ERROR_TYPES.VALIDATION_FAILED,
    INVALID_FIELD_FOR_INSERT_UPDATE: ERROR_TYPES.VALIDATION_FAILED,
    FIELD_CUSTOM_VALIDATION_EXCEPTION: ERROR_TYPES.VALIDATION_FAILED,
    INVALID_BATCH_SIZE: ERROR_TYPES.BATCH_ERROR,
    ALL_OR_NONE_OPERATION_ROLLED_BACK: ERROR_TYPES.BATCH_ERROR,
    QUERY_TIMEOUT: ERROR_TYPES.TIMEOUT_ERROR,
    EXCEEDED_MAX_SIZE_REQUEST: ERROR_TYPES.VALIDATION_FAILED
};
```

### Retry Strategy Patterns

```javascript
// Check if error should be retried
function isRetryableError(errorCode, statusCode) {
    const retryableErrorCodes = ['UNABLE_TO_LOCK_ROW', 'REQUEST_LIMIT_EXCEEDED', 'QUERY_TIMEOUT'];
    const retryableStatusCodes = [408, 429, 500, 502, 503, 504];
    return retryableErrorCodes.includes(errorCode) || retryableStatusCodes.includes(statusCode);
}

// Get retry strategy recommendation
function getRetryStrategy(errorCode, statusCode) {
    const strategies = {
        UNABLE_TO_LOCK_ROW: {
            maxRetries: 3,
            delayMs: 2000,
            backoffMultiplier: 2,
            recommendation: 'Retry with exponential backoff, max 10 seconds wait'
        },
        REQUEST_LIMIT_EXCEEDED: {
            maxRetries: 0,
            delayMs: null,
            backoffMultiplier: 1,
            recommendation: 'Wait until 24-hour window resets or increase API limits'
        },
        INVALID_SESSION_ID: {
            maxRetries: 1,
            delayMs: 0,
            backoffMultiplier: 1,
            recommendation: 'Re-authenticate and retry once'
        }
    };

    if (strategies[errorCode]) return strategies[errorCode];

    if (statusCode === 503 || statusCode === 502) {
        return {
            maxRetries: 3,
            delayMs: 1000,
            backoffMultiplier: 2,
            recommendation: 'Service temporarily unavailable, retry with backoff'
        };
    }

    return {
        maxRetries: 0,
        delayMs: null,
        backoffMultiplier: 1,
        recommendation: 'Not retryable, fix error and resubmit'
    };
}
```

### Standard Output Format for Salesforce Operations
```javascript
// Success response structure
{
    successful_operations: [
        {
            salesforce_id: 'a0X...',
            reference_id: 'ref1',
            operation_type: 'created|updated|processed',
            http_status: 201,
            location: '/services/data/v60.0/...',
            success: true
        }
    ],
    errors: [
        {
            error: {
                response: {
                    body: {
                        Type: 'ValidationFailed',
                        Message: 'Required field missing',
                        ErrorCode: 'REQUIRED_FIELD_MISSING'
                    }
                },
                message: 'Required field missing',
                statusCode: 400,
                retryable: false,
                retryStrategy: {...}
            },
            id: 'Salesforce Operation Reference # ref2',
            service: 'Salesforce Composite API Processing',
            fields: ['Name']
        }
    ],
    summary: {
        total_operations: 10,
        successful_operations: 9,
        failed_operations: 1,
        records_created: 5,
        records_updated: 4,
        success_rate: 90
    },
    total_responses: 10,
    processed_at: '2025-10-10T14:30:00.000Z'
}
```

### Key Benefits of This Pattern
1. **Consistent error handling** across all Salesforce API operations
2. **Automatic retry logic** based on error type and HTTP status
3. **Detailed error context** with reference IDs for debugging
4. **Flexible input parsing** handles multiple composite/batch response formats
5. **Comprehensive statistics** for monitoring and reporting
6. **Retryability flags** to guide downstream error recovery logic
