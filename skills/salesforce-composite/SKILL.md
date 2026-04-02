---
name: salesforce-composite
description: Salesforce Composite API patterns — URL encoding for external IDs, field rules for composite requests, External_ID__c object patterns, and batch upsert workflows.
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
