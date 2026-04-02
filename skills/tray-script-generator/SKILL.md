# Tray.io Script Generation Skill

**Version**: 2.1.0
**Last Updated**: 2026-03-06
**Purpose**: Production-grade Tray.io script generation with comprehensive patterns, templates, and examples

## Skill Overview

Enables generation of production-verified Tray.io scripts following patterns extracted from real Ohanafy integrations. All patterns, templates, and examples are sourced from working production code in the `/Embedded` directory.

## When To Use This Skill

- Generating a new Tray.io script step
- Refactoring an existing script to follow FP patterns
- Debugging Salesforce composite API errors
- Building lookup-map-based data transformation pipelines
- Any task requiring `exports.step` in a Tray.io context

## Core Capabilities

### 1. Pattern Library (52 Patterns)
- **Salesforce Integration**: Composite API, batch operations, error handling, URL encoding
- **Error Handling**: Type enumeration, retry strategies, HTTP status mapping, deduplication
- **Data Processing**: Lookup maps, chunking, filtering, aggregation, transformation
- **Functional Programming**: Pure functions, immutability, composition, orchestration
- **Utilities**: Namespace handling, field building, validation, metadata generation

Full implementations in `patterns.json`. Category breakdown in `references/pattern-categories.md`.

### 2. Template Library (12 Templates)
Complete production code templates in `templates.json`:
- Salesforce Response Handler (530 lines)
- Lookup Map Transformation (261 lines)
- Statistics Aggregation (69 lines)
- URL Encoding, Chunking Strategy, Error Deduplication, Namespace Field Builder
- Filter-Reduce Chain, Retry Strategy, HTTP Status Mapping, Composite Request Builder, Input Validation

### 3. Production Examples (10 Examples)
Verified input/output examples in `examples.json`. Annotated examples in `references/usage-examples.md`.

## Available Libraries

**CRITICAL** — only these are available in Tray.ai scripts:
- `lodash` - Data manipulation and functional utilities
- `moment-timezone` - Date/time handling and timezone conversion
- `crypto` - Cryptographic operations (hashing, UUIDs, etc.)
- `Buffer` - Binary data handling
- `URL` - URL parsing and construction

**NOT AVAILABLE**: axios, cheerio, uuid, xml-js, or any other external libraries.

## Mandatory Script Structure

```javascript
// 1. Constants at top
const CONFIG = {
    SALESFORCE_API_VERSION: 'v61.0',
    MAX_RETRIES: 3
};

// 2. Orchestration-only exports.step
exports.step = function({data = [], configuration = {}}, fileInput) {
    const validated = validateInput(data);
    const processed = transformData(validated);
    return formatOutput(processed);
};

// 3. ALL helper functions defined below exports.step
function validateInput(data) { /* ... */ }
function transformData(validated) { /* ... */ }
function formatOutput(processed) { /* ... */ }
```

## Core FP Rules

**DO**:
- Define ALL helper functions below `exports.step`
- Use pure functions (same input = same output)
- Maintain immutability — never mutate input parameters
- Use destructured parameters for 3-5 variables; object parameters for 6+
- Include comprehensive error handling and return structured responses
- Use `encodeURIComponent()` for Salesforce external IDs

**DO NOT**:
- Define functions inside `exports.step`
- Use `import` or `require` for unavailable libraries
- Mutate input parameters or existing objects
- Use imperative loops (use `.map`, `.filter`, `.reduce`)
- Include side effects (`console.log`, etc.)
- Throw exceptions without proper handling

## Salesforce-Specific Rules

### URL Encoding
All external ID values in composite URLs MUST be URL encoded. See the `salesforce-composite` skill for full encoding reference and `buildCompositeUrl` implementation.

```javascript
// CORRECT
const encodedValue = encodeURIComponent(externalIdValue);
const url = `/services/data/v61.0/sobjects/${objectName}/${externalIdField}/${encodedValue}`;
```

Characters requiring encoding: `#` -> `%23`, `/` -> `%2F`, `?` -> `%3F`, `&` -> `%26`, `=` -> `%3D`, `+` -> `%2B`, ` ` -> `%20`

### Namespace Handling
```javascript
function buildFieldName(baseName, namespace_prefix) {
    return namespace_prefix ? `${namespace_prefix}${baseName}` : baseName;
}
// buildFieldName('Item__c', 'ohfy__') -> 'ohfy__Item__c'
```

### External_ID__c Record Pattern
```javascript
function buildExternalIdRecord(service, item, itemReferenceId) {
    return {
        External_ID__c: `${service}_${item.gpa_id}`,
        External_Field__c: 'product_id',
        Item__c: `@{${itemReferenceId}.id}`
    };
}
```

## Error Response Structure

See the `tray-errors` skill for full error handling patterns including `ERROR_TYPES`, retry strategies, and `normalizeBatchErrors`. Canonical shape:

```javascript
{
    error: {
        response: {
            body: {
                Type: 'ValidationFailed',
                Message: 'Descriptive error message',
                ErrorCode: 'SALESFORCE_ERROR_CODE'
            }
        },
        message: 'Human-readable message',
        statusCode: 400,
        retryable: false,
        retryStrategy: {
            maxRetries: 0,
            delayMs: null,
            backoffMultiplier: 1,
            recommendation: 'Not retryable, fix error and resubmit'
        }
    },
    id: 'Reference identifier',
    service: 'Service name',
    fields: ['field1', 'field2']
}
```

## Script Generation Workflow

1. **Understand Requirements** — clarify input structure, expected output, complexity, applicable patterns
2. **Select Patterns** — reference `patterns.json`, `templates.json`, `examples.json`
3. **Generate Structure** — constants -> orchestration -> helpers
4. **Implement Error Handling** — use ERROR_TYPES, retry strategies, standardized response shape
5. **Validate** — pure functions, immutability, orchestration-only step, error coverage, sample data

## Common Pitfalls

```javascript
// WRONG: inline function in exports.step
exports.step = function(input) {
    const process = (data) => { /* ... */ };
    return process(input.data);
};

// CORRECT: call pre-defined helper
exports.step = function(input) {
    return processData(input.data);
};
function processData(data) { /* ... */ }
```

```javascript
// WRONG: mutate input
function processItems(items) { items.push(newItem); return items; }

// CORRECT: return new array
function processItems(items) { return [...items, newItem]; }
```

## Performance Notes

- Salesforce composite requests: 400KB limit — use `chunk_splitter` pattern
- Build lookup maps once before iteration — O(1) lookups, no nested loops
- Avoid unnecessary intermediate objects in hot paths

## Quality Checklist

- [ ] Constants defined at top; `exports.step` is orchestration-only
- [ ] All helpers defined below `exports.step`; no inline definitions
- [ ] All functions are pure; no input mutation; no side effects
- [ ] ERROR_TYPES used; retry strategies implemented; standardized error responses
- [ ] External IDs URL encoded; namespace handling present
- [ ] Sample input/output documented; edge cases considered

## References

- `references/pattern-categories.md` — all 52 pattern descriptions by category
- `references/usage-examples.md` — annotated input/output examples
- `patterns.json` — full pattern implementations (52 patterns)
- `templates.json` — full production code templates (12 templates)
- `examples.json` — all verified examples with input/output (10 examples)

## Production Source Files

| Integration | Path | What It Demonstrates |
|-------------|------|----------------------|
| Shopify_2GP | `/Embedded/Shopify_2GP/.../2-execute_script/script.js` | 530-line composite response handler |
| GP_Analytics_2GP | `/Embedded/GP_Analytics_2GP/.../5-new_create_csv_rows/script.js` | Lookup maps, URL encoding |
| CSV_Upload_v1 | `/Embedded/CSV_Upload_v1/.../1-process_results/script.js` | Statistics aggregation |

## Version History

- **2.1.0** (2026-03-06): Trimmed to ~350 lines; extracted pattern-categories and usage-examples to `references/`; replaced inline URL encoding and error handling sections with cross-references to `salesforce-composite` and `tray-errors` skills
- **2.0.0** (2025-01-25): Complete rewrite; 52 patterns; 12 templates; 10 examples; production source references
- **1.0.0**: Initial implementation guide

---

**Maintained By**: Derek Squires / Ohanafy Integration Team
**Production Status**: All patterns verified against working production code
