---
name: tray-errors
description: Tray.io error handling patterns — ERROR_TYPES enum, retry strategies, Salesforce-specific error codes, standard response structures, and batch error normalization.
---

# Tray.io Error Handling Expert

## Description
Expert knowledge of error handling patterns for Tray.io scripts, including ERROR_TYPES constants, retry strategies, Salesforce-specific error codes, and standard response structures. Use when implementing error handling, retry logic, or processing Salesforce API responses.

## When to Use
Invoke this skill when:
- Implementing error handling in Tray scripts
- Processing Salesforce composite/batch API responses
- Need ERROR_TYPES constants and error classification
- Determining retry strategies for different error types
- Questions about retryable vs non-retryable errors
- Standard response structure for Salesforce operations
- Keywords: "error", "retry", "ERROR_TYPES", "exception", "salesforce error", "composite response"

## Reference Files
- `error-handling-patterns.md` - Complete error handling documentation

## Quick Reference

### Core ERROR_TYPES
```javascript
const ERROR_TYPES = {
    VALIDATION_FAILED: 'ValidationFailed',
    PROCESSING_ERROR: 'ProcessingError',
    SALESFORCE_API_ERROR: 'SalesforceApiError',
    AUTHENTICATION_ERROR: 'AuthenticationError',
    RATE_LIMIT_ERROR: 'RateLimitError',
    RECORD_LOCK_ERROR: 'RecordLockError',
    DUPLICATE_ERROR: 'DuplicateError'
};
```

### Retryable Errors
- `UNABLE_TO_LOCK_ROW` - Retry with exponential backoff
- `REQUEST_LIMIT_EXCEEDED` - Wait for 24hr window
- `QUERY_TIMEOUT` - Retry with backoff
- HTTP 503/502 - Service temporarily unavailable

### Standard Response Structure
```javascript
{
    successful_operations: [...],
    errors: [{
        error: { response, message, statusCode, retryable, retryStrategy },
        id: 'Salesforce Operation Reference # ref',
        service: 'Salesforce Composite API Processing'
    }],
    summary: { total_operations, success_rate, ... }
}
```
