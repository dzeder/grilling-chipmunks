# Workflow Script Template: Extract JobIds

## Overview

This script parses the SOAP response from Salesforce Metadata API `create` operations to extract `asyncProcessId` values. These IDs are used to poll the status of asynchronous metadata creation jobs.

## When to Use This Template

Use this template for the **second step** in a Salesforce metadata creation workflow:
- After submitting a `create` request to the Metadata API
- Before polling job status with `checkStatus` operations
- When handling multiple async job IDs from batch operations

## Script Purpose

**Input**: SOAP XML response from Metadata API create operation (parsed to JSON)
**Output**: XML string containing `<cmd:asyncProcessId>` elements for checkStatus request
**Key Operations**:
1. Navigate nested SOAP envelope structure
2. Handle both single and multiple result responses
3. Extract asyncProcessId values
4. Format as XML elements for next workflow step

## Code Structure Pattern

### Orchestration-Only exports.step

```javascript
exports.step = function(input, fileInput) {
  const body = input.body;
  const jobIds = generateJobIdXml(body);
  return {
    jobIds
  };
};
```

**Key Principle**: Minimal orchestration - delegate XML parsing and generation to helper function.

### Helper Functions (All Defined Below exports.step)

#### Single Helper Function Pattern

```javascript
/**
 * Extracts async process IDs from Salesforce Metadata API create response
 * and generates the asyncProcessId XML elements
 * @param {Object} responseBody - The parsed response body from the create operation
 * @returns {string} - XML elements for asyncProcessId tags
 */
function generateJobIdXml(responseBody) {
  try {
    const results = responseBody["soapenv:Envelope"]["soapenv:Body"]
      .createResponse.result;
    
    // Handle both single result and array of results
    const resultArray = Array.isArray(results) ? results : [results];
    
    return resultArray
      .map(result => `<cmd:asyncProcessId>${result.id}</cmd:asyncProcessId>`)
      .join('\n');
  } catch (error) {
    console.error("Error extracting job IDs:", error);
    return '';
  }
}
```

## SOAP Response Structure

### Typical Metadata API Create Response

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <createResponse xmlns="http://soap.sforce.com/2006/04/metadata">
      <result>
        <done>false</done>
        <id>0AfXXXXXXXXXXXXXXX</id>
        <state>Queued</state>
      </result>
      <result>
        <done>false</done>
        <id>0AfYYYYYYYYYYYYYYY</id>
        <state>Queued</state>
      </result>
    </createResponse>
  </soapenv:Body>
</soapenv:Envelope>
```

### Parsed JSON Structure (Tray HTTP Connector)

```json
{
  "soapenv:Envelope": {
    "soapenv:Body": {
      "createResponse": {
        "result": [
          {
            "done": "false",
            "id": "0AfXXXXXXXXXXXXXXX",
            "state": "Queued"
          },
          {
            "done": "false",
            "id": "0AfYYYYYYYYYYYYYYY",
            "state": "Queued"
          }
        ]
      }
    }
  }
}
```

### Single Result Response

When creating only one object/field, `result` is an object, not an array:

```json
{
  "soapenv:Envelope": {
    "soapenv:Body": {
      "createResponse": {
        "result": {
          "done": "false",
          "id": "0AfXXXXXXXXXXXXXXX",
          "state": "Queued"
        }
      }
    }
  }
}
```

## Generated Output Format

### Multiple Job IDs

```xml
<cmd:asyncProcessId>0AfXXXXXXXXXXXXXXX</cmd:asyncProcessId>
<cmd:asyncProcessId>0AfYYYYYYYYYYYYYYY</cmd:asyncProcessId>
```

### Usage in CheckStatus Request

This output gets embedded into the checkStatus SOAP request body:

```xml
<soapenv:Body>
  <cmd:checkStatus>
    <cmd:asyncProcessId>0AfXXXXXXXXXXXXXXX</cmd:asyncProcessId>
    <cmd:asyncProcessId>0AfYYYYYYYYYYYYYYY</cmd:asyncProcessId>
  </cmd:checkStatus>
</soapenv:Body>
```

## Complete Working Example

**Source**: `/Users/derekhsquires/Documents/Ohanafy/Integrations/01-tray/Embedded/MCBC_Shelf_Execution_PRODUCTION/versions/current/scripts/90_MCBC_Shelf_Execution_Custom_Objects/2-extract_jobids/script.js`

**What it does**: Extracts async process IDs from custom object creation response, supporting both single and batch operations.

**Full implementation**:

```javascript
exports.step = function(input, fileInput) {
  const body = input.body;
  const jobIds = generateJobIdXml(body);
  return {
    jobIds
  };
};

/**
 * Extracts async process IDs from Salesforce Metadata API create response
 * and generates the asyncProcessId XML elements
 * @param {Object} responseBody - The parsed response body from the create operation
 * @returns {string} - XML elements for asyncProcessId tags
 */
function generateJobIdXml(responseBody) {
  try {
    const results = responseBody["soapenv:Envelope"]["soapenv:Body"]
      .createResponse.result;
    
    // Handle both single result and array of results
    const resultArray = Array.isArray(results) ? results : [results];
    
    return resultArray
      .map(result => `<cmd:asyncProcessId>${result.id}</cmd:asyncProcessId>`)
      .join('\n');
  } catch (error) {
    console.error("Error extracting job IDs:", error);
    return '';
  }
}
```

## Error Handling Patterns

### Try-Catch Pattern

Always wrap SOAP parsing in try-catch to handle malformed responses:

```javascript
function generateJobIdXml(responseBody) {
  try {
    // Parsing logic
  } catch (error) {
    console.error("Error extracting job IDs:", error);
    return '';  // Return empty string to avoid breaking workflow
  }
}
```

### Graceful Degradation

Return empty string instead of throwing errors - allows workflow to continue and fail at checkStatus step with clearer error message.

## Common Customizations

### Adding Result Validation

If you need to validate that IDs were successfully extracted:

```javascript
function generateJobIdXml(responseBody) {
  try {
    const results = responseBody["soapenv:Envelope"]["soapenv:Body"]
      .createResponse.result;
    
    const resultArray = Array.isArray(results) ? results : [results];
    
    // Validate all results have IDs
    const validResults = resultArray.filter(result => result.id);
    
    if (validResults.length === 0) {
      console.error("No valid job IDs found in response");
      return '';
    }
    
    return validResults
      .map(result => `<cmd:asyncProcessId>${result.id}</cmd:asyncProcessId>`)
      .join('\n');
  } catch (error) {
    console.error("Error extracting job IDs:", error);
    return '';
  }
}
```

### Returning Additional Metadata

If you need job state information for logging:

```javascript
exports.step = function(input, fileInput) {
  const body = input.body;
  const jobIds = generateJobIdXml(body);
  const jobMetadata = extractJobMetadata(body);
  
  return {
    jobIds,
    metadata: jobMetadata
  };
};

function extractJobMetadata(responseBody) {
  try {
    const results = responseBody["soapenv:Envelope"]["soapenv:Body"]
      .createResponse.result;
    
    const resultArray = Array.isArray(results) ? results : [results];
    
    return resultArray.map(result => ({
      id: result.id,
      state: result.state,
      done: result.done === "true"
    }));
  } catch (error) {
    return [];
  }
}
```

### Handling Different Response Formats

For different Metadata API operations (update, delete, etc.):

```javascript
function generateJobIdXml(responseBody, operationType = 'create') {
  try {
    // Adjust response path based on operation
    const responsePath = `${operationType}Response`;
    const results = responseBody["soapenv:Envelope"]["soapenv:Body"]
      [responsePath].result;
    
    const resultArray = Array.isArray(results) ? results : [results];
    
    return resultArray
      .map(result => `<cmd:asyncProcessId>${result.id}</cmd:asyncProcessId>`)
      .join('\n');
  } catch (error) {
    console.error(`Error extracting job IDs from ${operationType}:`, error);
    return '';
  }
}
```

## Testing Considerations

### Test Cases

1. **Single Result**: Response with one job ID
2. **Multiple Results**: Response with array of job IDs
3. **Malformed Response**: Missing envelope structure
4. **Missing IDs**: Results without id field
5. **Empty Response**: No results array

### Sample Test Input (input.json)

```json
{
  "body": {
    "soapenv:Envelope": {
      "soapenv:Body": {
        "createResponse": {
          "result": [
            {
              "done": "false",
              "id": "0AfXX0000000001AAA",
              "state": "Queued"
            },
            {
              "done": "false",
              "id": "0AfXX0000000002AAA",
              "state": "Queued"
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
  "jobIds": "<cmd:asyncProcessId>0AfXX0000000001AAA</cmd:asyncProcessId>\n<cmd:asyncProcessId>0AfXX0000000002AAA</cmd:asyncProcessId>"
}
```

## Tray.ai Functional Programming Requirements

- **Pure function**: generateJobIdXml always returns same output for same input
- **No side effects**: Only console.error for logging (acceptable in Tray context)
- **Immutability**: No mutation of responseBody object
- **No imports**: Uses only built-in JavaScript Array methods

## Integration with Workflow

### Workflow Step Sequence

1. **Previous Step**: HTTP connector with Salesforce Metadata API create operation
   - Connector should parse XML response to JSON
   - Pass parsed body to this script step

2. **This Step**: Extract Job IDs script
   - Input: `$.steps.http_create.body`
   - Output: `jobIds` string for next step

3. **Next Step**: HTTP connector with checkStatus operation
   - Embed `$.steps.extract_jobids.jobIds` into SOAP body
   - Use template from `3-evaluate-statuses.md`

### Tray Workflow Configuration

```yaml
Step: Execute Script - Extract Job IDs
Connector: script
Operation: execute
Input Variables:
  body: $.steps.create_custom_objects.body
Output:
  jobIds: (string) XML elements for checkStatus request
```

## Next Steps in Workflow

After extracting job IDs:
1. **Embed in checkStatus request** SOAP body
2. **Poll status** with loop until all jobs complete (done="true")
3. **Evaluate results** using template `3-evaluate-statuses.md` to classify errors

## Related Resources

- Previous step template: `1-define-objects-and-fields.md`
- Next step template: `3-evaluate-statuses.md`
- Salesforce Metadata API documentation: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/
- Tray error handling patterns: `.claude/rules/tray-error-handling.md`
