---
name: csv-output
description: >
  Tray CSV output structure — columns/rows format, fixed-width formatting, record generation,
  and bulk output patterns for Tray.io scripts. TRIGGER when: user asks about CSV formatting,
  bulk export structure, csv_data wrapper, or structured file output in Tray scripts.
---

# Tray CSV Output Structure Expert

## Description
Expert knowledge of the standardized CSV-compatible output structure for Tray.io scripts. Use when generating CSV data, bulk operations, or structured outputs for Tray file operations.

## When to Use
Invoke this skill when:
- Generating CSV output from Tray scripts
- Structuring bulk operation results
- Creating parent/child record outputs
- Need csv_data array wrapper pattern
- Questions about CSV column structure
- Keywords: "csv", "bulk export", "csv_data", "file generation", "structured output"

## Reference Files
- `csv-output-patterns.md` - Complete CSV output documentation

## Quick Reference

### Standard Structure
```javascript
{
    status: 'success|warning|error',
    csv_data: [
        {
            record_type: 'Object__c',
            external_lookup_field: 'External_ID__c',
            columns: [{ name: 'Field_1__c' }, { name: 'Field_2__c' }],
            column_count: 2,
            rows: [/* data */]
        }
    ],
    errors: [],
    summary: {}
}
```

### Helper Function
```javascript
function createStructuredOutput(columns, rows, recordType, externalLookupField) {
    return {
        record_type: recordType,
        external_lookup_field: externalLookupField,
        columns: columns,
        column_count: columns.length,
        rows: rows
    };
}
```

## Delegate Elsewhere

- **deploy-prep** — For validating CSV output format before deployment
- **tray-expert** — For Tray.io workflow architecture questions beyond CSV structure
- **salesforce-composite** — For Salesforce API batch operations (not CSV file output)

### Workflow
1. Confirm data sets with user (parent/child records)
2. Wrap outputs in `csv_data` array
3. Include record_type and external_lookup_field
