---
name: salesforce-composite
description: >
  Salesforce Composite API patterns — URL encoding for external IDs, field rules for composite requests,
  External_ID__c object patterns, and batch upsert workflows.
  TRIGGER when: user builds composite or batch API requests, works with external ID upserts,
  needs URL encoding for special characters in SF API calls, or asks about composite request field rules.
---

# Salesforce Composite API Expert

## Description
Expert knowledge of Salesforce Composite API patterns including URL encoding for external IDs, field rules for composite requests, and External_ID__c object patterns. Use when building Salesforce composite/batch requests or working with external ID upserts.

## When to Use
Invoke this skill when:
- Building Salesforce composite or batch API requests
- Working with External_ID__c upsert keys
- Need URL encoding patterns for special characters (#, /, ?, &)
- Questions about composite request field rules
- External_ID__c object record structure
- Keywords: "salesforce", "composite", "upsert", "external id", "url encoding", "encodeURIComponent"

## Delegation

- **salesforce-integration-architect** — For broader integration architecture decisions beyond composite API mechanics
- **sf-apex** — For Apex-side composite request handling (HttpRequest, named credentials)
- **tray-expert** — For Tray.io workflow steps that call SF Composite API
- Do not trigger for general Salesforce REST API questions that do not involve composite/batch patterns

## Workflow

### 1. Identify the operation type
Determine whether the user needs composite request, composite batch, or single-record upsert with external ID.

### 2. Build the request structure
Construct the URL with proper `encodeURIComponent()` encoding, ensure external ID fields are not duplicated in the body, and set correct API version.

### 3. Handle batching
For bulk operations, chunk records into groups of 200 (composite batch limit) and structure subrequests with proper referenceId values.

### 4. Validate and test
Verify URL encoding for special characters, confirm field rules (upsert key not in body), and test with a single record before bulk execution.

## Reference Files
- `salesforce-api-patterns.md` - Complete Salesforce API documentation

## Quick Reference

### Critical Rules
1. **ALWAYS use `encodeURIComponent()` for external ID values in URLs**
2. **External upsert key field CANNOT be in request body**
3. **External_ID__c format**: `{service}_{field_value}` (e.g., "shopify_123")

### URL Encoding Pattern
```javascript
function buildCompositeUrl(objectType, namespace_prefix, externalIdValue) {
    const encodedValue = encodeURIComponent(externalIdValue);
    return `/services/data/v61.0/sobjects/${objectName}/${externalIdField}/${encodedValue}`;
}
```

### Common URL-Unsafe Characters
- `#` → `%23` (fragment identifier)
- `/` → `%2F` (path separator)
- `?` → `%3F` (query string)
- `&` → `%26` (parameter separator)
- ` ` → `%20` (space)

### External_ID__c Object Fields
- `External_ID__c` (upsert key): `{service}_{field_value}`
- `External_Field__c`: Field name being mapped (e.g., "product_id")
