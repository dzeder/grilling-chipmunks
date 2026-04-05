# Pattern Categories Reference

**Source**: Extracted from SKILL.md v2.0.0
**Full implementations**: See `../patterns.json` (52 patterns)

## Salesforce Integration Patterns

**Composite Response Handler** (`salesforce_composite_response_handler`)
- Processes Salesforce composite/batch API responses
- Comprehensive error extraction and classification
- Success/failure separation with detailed tracking
- Production reference: `Shopify_2GP/.../2-execute_script/script.js` (530 lines)

**URL Encoding** (`salesforce_url_encoding`)
- Properly encode external ID values for composite URLs
- Handle special characters (#, /, ?, &, =, +, space)
- Prevent URL truncation and parsing errors
- Example: `1019#HRB` -> `1019%23HRB`

**Composite Request Builder** (`composite_request_builder`)
- Build multi-record upsert requests
- Reference ID management
- External ID field handling
- Namespace prefix integration

## Error Handling Patterns

**Error Types Enumeration** (`error_types_enumeration`)
```javascript
const ERROR_TYPES = {
    VALIDATION_FAILED: 'ValidationFailed',
    PROCESSING_ERROR: 'ProcessingError',
    SALESFORCE_API_ERROR: 'SalesforceApiError',
    AUTHENTICATION_ERROR: 'AuthenticationError',
    RATE_LIMIT_ERROR: 'RateLimitError',
    SERVER_ERROR: 'ServerError'
};
```

**Retry Strategy Pattern** (`retry_strategy_pattern`)
- Determine retryability based on error code and HTTP status
- Configure retry parameters (maxRetries, delayMs, backoffMultiplier)
- Provide actionable recommendations
- Support exponential backoff

**HTTP Status Mapping** (`http_status_to_error_type_mapping`)
- Map HTTP status codes to error types
- Classify client errors (4xx) vs server errors (5xx)
- Determine retryability
- Fallback error handling

## Data Processing Patterns

**Lookup Map Builder** (`lookup_map_builder`)
- Create O(1) lookup structures
- Handle missing keys gracefully
- Support multiple lookup fields
- Memory-efficient implementation

**Chunking Strategy** (`chunk_splitter`)
- Split large payloads into 400KB chunks
- Calculate payload size accurately
- Maintain data integrity across chunks
- Track chunk metadata

**Filter-Reduce Chain** (`filter_reduce_chain`)
- Chain functional operations
- Immutable data flow
- Composable transformations
- Clear data lineage

**Error Deduplication** (`unique_set_deduplication`)
- Remove duplicate errors using Set
- JSON stringify for comparison
- Preserve error details
- Track deduplication metrics

## Functional Programming Patterns

**Pure Function Template** (`pure_function_template`)
- No side effects
- Deterministic output
- Immutable data handling
- Testable in isolation

**Orchestration-Only Pattern** (`orchestration_only_exports_step`)
- Keep `exports.step` minimal
- Call pre-defined helpers
- No inline function definitions
- Clear data flow

**Immutable Data Transformation** (`immutable_transformation`)
- Use spread operator for copying
- Never mutate input parameters
- Return new objects/arrays
- Preserve original data

## Pattern Counts by Category

| Category | Count |
|----------|-------|
| Salesforce Integration | 12 |
| Error Handling | 10 |
| Data Processing | 15 |
| Functional Programming | 8 |
| Utilities | 7 |
| **Total** | **52** |
