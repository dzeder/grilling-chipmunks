---
paths: ["01-tray/**"]
alwaysApply: true
---

# Salesforce API Patterns

## Salesforce Composite Request URL Encoding

**CRITICAL**: All values inserted into Salesforce composite/batch request URLs MUST be properly URL encoded.

### The Problem
URL-unsafe characters (like `#`, `/`, `?`, `&`, `=`, `+`, ` `) in external ID values will be misinterpreted if not encoded:
- `#` is treated as URL fragment identifier → everything after is truncated
- `?` starts query string → creates parsing errors
- `/` is path separator → breaks URL structure
- `&` separates query parameters → malformed requests
- ` ` (space) must be encoded → invalid URLs

### The Solution
**ALWAYS use `encodeURIComponent()` for external ID values in URLs**

```javascript
// ✅ CORRECT - URL encode external ID values
function buildCompositeUrl(objectType, namespace_prefix, externalIdValue) {
    const objectName = buildObjectName(objectType, namespace_prefix);
    const externalIdField = buildExternalIdFieldName(objectType, namespace_prefix);

    // URL encode the external ID value to handle special characters
    const encodedValue = encodeURIComponent(externalIdValue);

    return `/services/data/${SALESFORCE_API_VERSION}/sobjects/${objectName}/${externalIdField}/${encodedValue}`;
}

// ❌ WRONG - Direct string interpolation without encoding
function buildCompositeUrl(objectType, namespace_prefix, externalIdValue) {
    return `/services/data/${SALESFORCE_API_VERSION}/sobjects/${objectName}/${externalIdField}/${externalIdValue}`;
    // Problem: "1019#HRB" becomes "1019" in created record
}
```

### Common URL-Unsafe Characters to Encode

| Character | Unencoded | Encoded | Issue if Not Encoded |
|-----------|-----------|---------|---------------------|
| `#` | `#` | `%23` | Treated as fragment identifier, everything after is lost |
| `/` | `/` | `%2F` | Interpreted as path separator, breaks URL structure |
| `?` | `?` | `%3F` | Starts query string, creates parsing errors |
| `&` | `&` | `%26` | Separates query parameters, malforms request |
| `=` | `=` | `%3D` | Used in query parameters, causes parsing issues |
| `+` | `+` | `%2B` | Can be interpreted as space in some contexts |
| ` ` (space) | ` ` | `%20` | Invalid in URLs |
| `%` | `%` | `%25` | Encoding character itself, must be encoded |

### When to Apply Encoding

✅ **Always encode**:
- External ID field values in PATCH URLs
- Any user-provided data inserted into URLs
- Values from external systems (GPA, Shopify, etc.)

❌ **Never encode**:
- Object names (already validated)
- Field names (already validated)
- API version strings (hardcoded)
- Namespace prefixes (validated)

### Example: Complete Implementation

```javascript
// Build composite request for Item and External_ID records
function buildCompositeRequest(products, config) {
    const compositeRequest = {
        allOrNone: false,
        compositeRequest: []
    };

    products.forEach((product, index) => {
        const itemReferenceId = `Item${index + 1}`;

        // Get external ID value (may contain special characters)
        const externalIdValue = product.pdcn || product.vip_account_identifier || product.gpa_id;

        // Build Item upsert with URL-encoded external ID
        compositeRequest.compositeRequest.push({
            method: 'PATCH',
            url: buildCompositeUrl('Item', config.namespace_prefix, externalIdValue),
            referenceId: itemReferenceId,
            body: buildItemRecord(product, config)
        });

        // Build External_ID record with URL-encoded composite value
        const externalIdFieldValue = `${config.service}_${product.gpa_id}`;

        compositeRequest.compositeRequest.push({
            method: 'PATCH',
            url: buildCompositeUrl('External_ID', config.namespace_prefix, externalIdFieldValue),
            referenceId: `ExtId${index + 1}`,
            body: buildExternalIdRecord(config.service, product, itemReferenceId)
        });
    });

    return compositeRequest;
}

// Helper: Build properly encoded composite URL
function buildCompositeUrl(objectType, namespace_prefix, externalIdValue) {
    const objectName = buildObjectName(objectType, namespace_prefix);
    const externalIdField = buildExternalIdFieldName(objectType, namespace_prefix);

    // CRITICAL: URL encode the external ID value
    const encodedValue = encodeURIComponent(externalIdValue);

    return `/services/data/v61.0/sobjects/${objectName}/${externalIdField}/${encodedValue}`;
}
```

### Validation Checklist

Before deploying any Salesforce composite request script:
- [ ] All external ID values are URL encoded with `encodeURIComponent()`
- [ ] Test cases include special characters (#, /, ?, &, =, +, space)
- [ ] Integration tests verify records created with correct values
- [ ] No direct string interpolation of user-provided data in URLs
- [ ] Error handling accounts for edge cases (null, empty, very long values)

## Salesforce Composite Request Field Rules

**CRITICAL Rules**:
- In a Salesforce composite PATCH request, the external upsert key field CANNOT be in the fields body
- External_ID__c object records should always have two fields:
  1. **External_ID__c** (upsert key in URL): Value format `{service}_{field_value}`
  2. **External_Field__c**: String of the field name being mapped (e.g., "product_id")

**Example**: When service is "shopify" and external_field__c is "product_id" with value "123":
- `External_ID__c` = "shopify_123" (used in URL)
- `External_Field__c` = "product_id" (field name)
