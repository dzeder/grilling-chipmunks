# Workflow Script Template: Evaluate Statuses

## Overview

This script processes Salesforce Metadata API `checkStatus` SOAP responses to determine job completion status and classify errors. It distinguishes between fatal errors (workflow failure) and acceptable errors (e.g., duplicate object/field already exists).

## When to Use This Template

Use this template for the **third step** in a Salesforce metadata creation workflow:
- After polling `checkStatus` with extracted job IDs
- To determine if all async jobs have completed
- To identify which errors are acceptable vs. fatal
- As loop condition exit criteria (continue polling until jobsComplete=true)

## Script Purpose

**Input**: SOAP XML response from Metadata API checkStatus operation (parsed to JSON)
**Output**: Status flags and categorized errors
**Key Operations**:
1. Parse checkStatus results from SOAP envelope
2. Determine if all jobs are complete (done="true")
3. Classify errors as acceptable or fatal
4. Return standardized error objects for downstream handling

## Code Structure Pattern

### Orchestration-Only exports.step

```javascript
exports.step = function(input, fileInput) {
    const body = input.body;

    // Parse results from SOAP response
    const results = parseCheckStatusResults(body);

    // Check if all jobs are done (regardless of success/error state)
    const jobsComplete = areAllJobsDone(results);

    // Extract fatal errors (non-acceptable error states)
    const fatalErrors = extractFatalErrors(results);

    // All successful if no fatal errors
    const allSuccessful = fatalErrors.length === 0;

    return {
        jobsComplete,
        allSuccessful,
        errors: fatalErrors
    };
};
```

**Key Principle**: Orchestrate job completion and error classification logic through pure helper functions.

### Constants for Error Classification

```javascript
// Acceptable error codes that indicate the object already exists (treat as success)
const ACCEPTABLE_ERROR_CODES = [
    'DUPLICATE_DEVELOPER_NAME',  // Custom object/field API name already exists
    'DUPLICATE_VALUE'            // Duplicate value constraint (less common for metadata)
];

// Error type constant for standardized error objects
const ERROR_TYPE = 'MetadataApiError';
```

**Why Constants Matter**: Centralizes error classification logic, making it easy to add new acceptable error codes as business requirements evolve.

### Helper Functions (All Defined Below exports.step)

#### 1. Parse CheckStatus Results

```javascript
/**
 * Parses the checkStatus results from the SOAP envelope
 * @param {Object} responseBody - The parsed SOAP response body
 * @returns {Array} - Array of result objects
 */
function parseCheckStatusResults(responseBody) {
    try {
        const results = responseBody["soapenv:Envelope"]["soapenv:Body"]["checkStatusResponse"].result;
        return Array.isArray(results) ? results : [results];
    } catch (error) {
        // Return empty array if parsing fails - will be treated as incomplete
        return [];
    }
}
```

**Pattern**: Returns empty array on parse failure, allowing workflow to retry polling.

#### 2. Check Job Completion

```javascript
/**
 * Checks if all jobs in the results are complete (done="true")
 * @param {Array} results - Array of result objects
 * @returns {boolean} - True if all jobs are done
 */
function areAllJobsDone(results) {
    if (results.length === 0) {
        return false;
    }
    return results.every(isJobDone);
}

/**
 * Checks if a single job is done
 * @param {Object} result - Single result object
 * @returns {boolean} - True if job is done
 */
function isJobDone(result) {
    return result.done === "true";
}
```

**Pattern**: Decomposed into testable units - `areAllJobsDone` for array logic, `isJobDone` for single job.

#### 3. Extract Fatal Errors

```javascript
/**
 * Extracts fatal errors from results (errors that are not acceptable)
 * @param {Array} results - Array of result objects
 * @returns {Array} - Array of standardized error objects
 */
function extractFatalErrors(results) {
    return results
        .filter(isFatalError)
        .map(createStandardizedError);
}

/**
 * Determines if a result represents a fatal error
 * @param {Object} result - Single result object
 * @returns {boolean} - True if this is a fatal error
 */
function isFatalError(result) {
    // Not an error at all
    if (result.state !== "Error") {
        return false;
    }

    // Check if it's an acceptable error code
    return !isAcceptableError(result.statusCode);
}

/**
 * Checks if an error code is in the acceptable list
 * @param {string} statusCode - The error status code
 * @returns {boolean} - True if the error is acceptable
 */
function isAcceptableError(statusCode) {
    return ACCEPTABLE_ERROR_CODES.includes(statusCode);
}
```

**Pattern**: Filter-map pipeline - filter to fatal errors, map to standardized format.

#### 4. Create Standardized Error Objects

```javascript
/**
 * Creates a standardized error object from a result
 * @param {Object} result - Single result object with error
 * @returns {Object} - Standardized error object matching Tray patterns
 */
function createStandardizedError(result) {
    return {
        error: {
            response: {
                body: {
                    Type: ERROR_TYPE,
                    Message: result.message || 'Unknown error',
                    ErrorCode: result.statusCode || 'UNKNOWN_ERROR'
                }
            },
            message: result.message || 'Unknown error',
            statusCode: result.statusCode || 'UNKNOWN_ERROR'
        },
        id: result.id || 'Unknown ID',
        service: 'Salesforce Metadata API checkStatus'
    };
}
```

**Pattern**: Matches Tray error handling standard (see `.claude/rules/tray-error-handling.md`) with nested response structure.

## CheckStatus Response Structure

### Typical Metadata API CheckStatus Response

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <checkStatusResponse xmlns="http://soap.sforce.com/2006/04/metadata">
      <result>
        <done>true</done>
        <id>0AfXXXXXXXXXXXXXXX</id>
        <state>Completed</state>
      </result>
      <result>
        <done>true</done>
        <id>0AfYYYYYYYYYYYYYYY</id>
        <state>Error</state>
        <statusCode>DUPLICATE_DEVELOPER_NAME</statusCode>
        <message>An object with this API name already exists</message>
      </result>
    </checkStatusResponse>
  </soapenv:Body>
</soapenv:Envelope>
```

### Parsed JSON Structure

```json
{
  "soapenv:Envelope": {
    "soapenv:Body": {
      "checkStatusResponse": {
        "result": [
          {
            "done": "true",
            "id": "0AfXXXXXXXXXXXXXXX",
            "state": "Completed"
          },
          {
            "done": "true",
            "id": "0AfYYYYYYYYYYYYYYY",
            "state": "Error",
            "statusCode": "DUPLICATE_DEVELOPER_NAME",
            "message": "An object with this API name already exists"
          }
        ]
      }
    }
  }
}
```

## Job States

### Standard States

- **Queued**: Job is waiting to be processed
- **InProgress**: Job is currently executing
- **Completed**: Job finished successfully
- **Error**: Job failed with error (check statusCode for details)

### Done Flag

- `done="false"` - Job still processing (continue polling)
- `done="true"` - Job finished (may be Completed or Error state)

## Error Classification Strategy

### Acceptable Errors (Treat as Success)

These error codes indicate the desired end state already exists:

```javascript
const ACCEPTABLE_ERROR_CODES = [
    'DUPLICATE_DEVELOPER_NAME',  // Object/field API name already exists
    'DUPLICATE_VALUE'            // Duplicate value (rare for metadata)
];
```

**Rationale**: If a field/object already exists with the exact configuration, the workflow goal is achieved. Creating is idempotent.

### Fatal Errors (Workflow Failure)

All other error codes are fatal:
- `INVALID_FIELD_TYPE` - Field type not supported
- `INVALID_PICKLIST_VALUE` - Picklist value configuration error
- `INVALID_METADATA` - Malformed metadata
- `INSUFFICIENT_ACCESS` - Permission issues
- Custom errors from validation rules

## Complete Working Example

**Source**: `/Users/derekhsquires/Documents/Ohanafy/Integrations/01-tray/Embedded/MCBC_Shelf_Execution_PRODUCTION/versions/current/scripts/90_MCBC_Shelf_Execution_Custom_Objects/3-evaluate_statuses/script.js`

**What it does**: Evaluates custom object creation job statuses, treating duplicate object names as success (idempotent operation).

**Full implementation**:

```javascript
// Acceptable error codes that indicate the object already exists (treat as success)
const ACCEPTABLE_ERROR_CODES = [
    'DUPLICATE_DEVELOPER_NAME',  // Custom object/field API name already exists
    'DUPLICATE_VALUE'            // Duplicate value constraint (less common for metadata)
];

// Error type constant for standardized error objects
const ERROR_TYPE = 'MetadataApiError';

/**
 * Main orchestration function - processes checkStatus response
 * @param {Object} input - Contains body property with SOAP response
 * @param {Array} fileInput - File inputs (not used)
 * @returns {Object} - { jobsComplete, allSuccessful, errors }
 */
exports.step = function(input, fileInput) {
    const body = input.body;

    // Parse results from SOAP response
    const results = parseCheckStatusResults(body);

    // Check if all jobs are done (regardless of success/error state)
    const jobsComplete = areAllJobsDone(results);

    // Extract fatal errors (non-acceptable error states)
    const fatalErrors = extractFatalErrors(results);

    // All successful if no fatal errors
    const allSuccessful = fatalErrors.length === 0;

    return {
        jobsComplete,
        allSuccessful,
        errors: fatalErrors
    };
};

/**
 * Parses the checkStatus results from the SOAP envelope
 * @param {Object} responseBody - The parsed SOAP response body
 * @returns {Array} - Array of result objects
 */
function parseCheckStatusResults(responseBody) {
    try {
        const results = responseBody["soapenv:Envelope"]["soapenv:Body"]["checkStatusResponse"].result;
        return Array.isArray(results) ? results : [results];
    } catch (error) {
        // Return empty array if parsing fails - will be treated as incomplete
        return [];
    }
}

/**
 * Checks if all jobs in the results are complete (done="true")
 * @param {Array} results - Array of result objects
 * @returns {boolean} - True if all jobs are done
 */
function areAllJobsDone(results) {
    if (results.length === 0) {
        return false;
    }
    return results.every(isJobDone);
}

/**
 * Checks if a single job is done
 * @param {Object} result - Single result object
 * @returns {boolean} - True if job is done
 */
function isJobDone(result) {
    return result.done === "true";
}

/**
 * Extracts fatal errors from results (errors that are not acceptable)
 * @param {Array} results - Array of result objects
 * @returns {Array} - Array of standardized error objects
 */
function extractFatalErrors(results) {
    return results
        .filter(isFatalError)
        .map(createStandardizedError);
}

/**
 * Determines if a result represents a fatal error
 * @param {Object} result - Single result object
 * @returns {boolean} - True if this is a fatal error
 */
function isFatalError(result) {
    // Not an error at all
    if (result.state !== "Error") {
        return false;
    }

    // Check if it's an acceptable error code
    return !isAcceptableError(result.statusCode);
}

/**
 * Checks if an error code is in the acceptable list
 * @param {string} statusCode - The error status code
 * @returns {boolean} - True if the error is acceptable
 */
function isAcceptableError(statusCode) {
    return ACCEPTABLE_ERROR_CODES.includes(statusCode);
}

/**
 * Creates a standardized error object from a result
 * @param {Object} result - Single result object with error
 * @returns {Object} - Standardized error object matching Tray patterns
 */
function createStandardizedError(result) {
    return {
        error: {
            response: {
                body: {
                    Type: ERROR_TYPE,
                    Message: result.message || 'Unknown error',
                    ErrorCode: result.statusCode || 'UNKNOWN_ERROR'
                }
            },
            message: result.message || 'Unknown error',
            statusCode: result.statusCode || 'UNKNOWN_ERROR'
        },
        id: result.id || 'Unknown ID',
        service: 'Salesforce Metadata API checkStatus'
    };
}
```

## Common Customizations

### Adding More Acceptable Error Codes

Extend the constant as business requirements emerge:

```javascript
const ACCEPTABLE_ERROR_CODES = [
    'DUPLICATE_DEVELOPER_NAME',
    'DUPLICATE_VALUE',
    'FIELD_INTEGRITY_EXCEPTION',  // Field already exists with different config
    'CUSTOM_METADATA_LIMIT_EXCEEDED'  // Custom metadata type limit (non-fatal for some use cases)
];
```

### Detailed Error Reporting

If you need to capture acceptable errors for reporting:

```javascript
exports.step = function(input, fileInput) {
    const body = input.body;
    const results = parseCheckStatusResults(body);
    const jobsComplete = areAllJobsDone(results);
    const fatalErrors = extractFatalErrors(results);
    const acceptableErrors = extractAcceptableErrors(results);  // New function

    return {
        jobsComplete,
        allSuccessful: fatalErrors.length === 0,
        errors: fatalErrors,
        warnings: acceptableErrors  // For logging/monitoring
    };
};

function extractAcceptableErrors(results) {
    return results
        .filter(result => result.state === "Error" && isAcceptableError(result.statusCode))
        .map(createStandardizedError);
}
```

### Adding Retry Logic for Incomplete Jobs

If checkStatus call fails, return appropriate flags:

```javascript
function parseCheckStatusResults(responseBody) {
    try {
        const results = responseBody["soapenv:Envelope"]["soapenv:Body"]["checkStatusResponse"].result;
        return Array.isArray(results) ? results : [results];
    } catch (error) {
        console.error("Failed to parse checkStatus response:", error);
        // Return empty array - areAllJobsDone will return false, triggering retry
        return [];
    }
}
```

### Job Progress Tracking

Calculate completion percentage for long-running batches:

```javascript
exports.step = function(input, fileInput) {
    const body = input.body;
    const results = parseCheckStatusResults(body);
    const jobsComplete = areAllJobsDone(results);
    const fatalErrors = extractFatalErrors(results);
    const progress = calculateProgress(results);

    return {
        jobsComplete,
        allSuccessful: fatalErrors.length === 0,
        errors: fatalErrors,
        progressPercentage: progress
    };
};

function calculateProgress(results) {
    if (results.length === 0) return 0;
    const doneCount = results.filter(isJobDone).length;
    return Math.round((doneCount / results.length) * 100);
}
```

## Testing Considerations

### Test Cases

1. **All Jobs Complete (Success)**: All done="true", state="Completed"
2. **All Jobs Complete (Acceptable Errors)**: All done="true", some state="Error" with DUPLICATE_DEVELOPER_NAME
3. **All Jobs Complete (Fatal Errors)**: All done="true", some state="Error" with INVALID_FIELD_TYPE
4. **Jobs In Progress**: Some done="false", state="Queued" or "InProgress"
5. **Malformed Response**: Missing checkStatusResponse structure
6. **Mixed States**: Some complete, some in progress, some error

### Sample Test Input (All Complete, One Acceptable Error)

```json
{
  "body": {
    "soapenv:Envelope": {
      "soapenv:Body": {
        "checkStatusResponse": {
          "result": [
            {
              "done": "true",
              "id": "0AfXX0000000001AAA",
              "state": "Completed"
            },
            {
              "done": "true",
              "id": "0AfXX0000000002AAA",
              "state": "Error",
              "statusCode": "DUPLICATE_DEVELOPER_NAME",
              "message": "Custom object 'Mandate__c' already exists"
            }
          ]
        }
      }
    }
  }
}
```

### Expected Output

```json
{
  "jobsComplete": true,
  "allSuccessful": true,
  "errors": []
}
```

### Sample Test Input (Fatal Error)

```json
{
  "body": {
    "soapenv:Envelope": {
      "soapenv:Body": {
        "checkStatusResponse": {
          "result": {
            "done": "true",
            "id": "0AfXX0000000001AAA",
            "state": "Error",
            "statusCode": "INVALID_FIELD_TYPE",
            "message": "Field type 'InvalidType' is not supported"
          }
        }
      }
    }
  }
}
```

### Expected Output

```json
{
  "jobsComplete": true,
  "allSuccessful": false,
  "errors": [
    {
      "error": {
        "response": {
          "body": {
            "Type": "MetadataApiError",
            "Message": "Field type 'InvalidType' is not supported",
            "ErrorCode": "INVALID_FIELD_TYPE"
          }
        },
        "message": "Field type 'InvalidType' is not supported",
        "statusCode": "INVALID_FIELD_TYPE"
      },
      "id": "0AfXX0000000001AAA",
      "service": "Salesforce Metadata API checkStatus"
    }
  ]
}
```

## Tray.ai Functional Programming Requirements

- **Pure functions**: All helper functions return same output for same input
- **No side effects**: Only console.error for logging (acceptable in Tray)
- **Immutability**: No mutation of input objects
- **Composition**: Small, focused functions composed into larger logic
- **No imports**: Uses only built-in JavaScript Array methods

## Integration with Workflow

### Workflow Loop Pattern

```yaml
Step: Loop Until Complete
Type: Loop Connector
Condition: $.steps.evaluate_statuses.jobsComplete === false
Max Iterations: 20
Delay Between Iterations: 10 seconds
Steps:
  1. HTTP - CheckStatus Request (embed jobIds from step 2)
  2. Script - Evaluate Statuses (this template)
```

### Conditional Branching After Loop

```yaml
Step: Branch on Success
Type: Branch Connector
Condition: $.steps.evaluate_statuses.allSuccessful === true
If True:
  - Log Success
  - Continue to next workflow step
If False:
  - Format Error Message
  - Send Alert
  - Terminate Workflow
```

### Error Handling Branch

```yaml
Step: Process Fatal Errors
Condition: $.steps.evaluate_statuses.errors.length > 0
Actions:
  - Map errors to readable format
  - Log to storage connector
  - Send notification
  - Return structured error response
```

## Output Structure for Downstream Steps

### Success Case

```json
{
  "jobsComplete": true,
  "allSuccessful": true,
  "errors": []
}
```

### Acceptable Error Case (Idempotent)

```json
{
  "jobsComplete": true,
  "allSuccessful": true,
  "errors": [],
  "warnings": [
    {
      "error": {
        "response": {
          "body": {
            "Type": "MetadataApiError",
            "Message": "Custom field 'Account.Test__c' already exists",
            "ErrorCode": "DUPLICATE_DEVELOPER_NAME"
          }
        }
      },
      "id": "0AfXX0000000001AAA",
      "service": "Salesforce Metadata API checkStatus"
    }
  ]
}
```

### Fatal Error Case

```json
{
  "jobsComplete": true,
  "allSuccessful": false,
  "errors": [
    {
      "error": {
        "response": {
          "body": {
            "Type": "MetadataApiError",
            "Message": "Insufficient access rights on object id",
            "ErrorCode": "INSUFFICIENT_ACCESS"
          }
        },
        "message": "Insufficient access rights on object id",
        "statusCode": "INSUFFICIENT_ACCESS"
      },
      "id": "0AfXX0000000001AAA",
      "service": "Salesforce Metadata API checkStatus"
    }
  ]
}
```

### In Progress Case

```json
{
  "jobsComplete": false,
  "allSuccessful": false,
  "errors": []
}
```

## Related Resources

- Previous step template: `2-extract-jobids.md`
- Tray error handling patterns: `.claude/rules/tray-error-handling.md`
- Salesforce Metadata API error codes: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_statuscode.htm
- CSV output standard: `.claude/rules/tray-csv-output.md` (for error reporting)
