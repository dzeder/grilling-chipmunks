---
paths: ["01-tray/**"]
alwaysApply: false
---

# Tray CSV-Compatible Output Structure Standard

**CRITICAL**: When the user requests output that will be used for Tray.ai CSV operations (file generation, data export, bulk operations), you MUST use this standardized structure with all CSV outputs wrapped in a `csv_data` array.

## Workflow
1. **Confirm the data sets** with the user (e.g., parent/child records, orders/order items)
2. **Wrap all structured outputs** in a `csv_data` array

## Standard Structure
```javascript
{
    status: 'success|warning|error',
    csv_data: [
        {
            record_type: 'Parent_Object__c',
            external_lookup_field: 'External_ID__c',
            columns: [{ name: 'Field_1__c' }, { name: 'Field_2__c' }],
            column_count: 2,
            rows: [{ /* parent records */ }]
        },
        {
            record_type: 'Child_Object__c',
            external_lookup_field: 'Child_External_ID__c',
            columns: [{ name: 'Parent__r.External_ID__c' }, { name: 'Field__c' }],
            column_count: 2,
            rows: [{ /* child records */ }]
        }
    ],
    errors: [],
    summary: { /* statistics */ }
}
```

## Helper Function Pattern
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

## Usage Example
```javascript
// Define columns as constants at top of file
const ORDER_COLUMNS = [
    { name: 'Account__c' },
    { name: 'Order_Date__c' },
    { name: 'External_ID__c' }
];

const ORDER_ITEM_COLUMNS = [
    { name: 'Order__r.External_ID__c' },
    { name: 'Product__c' },
    { name: 'Quantity__c' },
    { name: 'Order_Item_External_ID__c' }
];

// In output function - wrap in csv_data array
return {
    status,
    csv_data: [
        createStructuredOutput(ORDER_COLUMNS, orders, 'Order__c', 'External_ID__c'),
        createStructuredOutput(ORDER_ITEM_COLUMNS, orderItems, 'Order_Item__c', 'Order_Item_External_ID__c')
    ],
    errors,
    summary
};
```

## Benefits
- **Self-documenting**: `record_type` and `external_lookup_field` indicate Salesforce target
- **CSV-ready**: `columns` array provides header row for CSV generation
- **Validation-friendly**: `column_count` enables quick integrity checks
- **Iterable**: `csv_data` array allows downstream loops to process each object type
- **Consistent**: Same structure across all Tray scripts for downstream processing

## Reference Implementation
See: `/Embedded/MCBC_Shelf_Execution/versions/current/scripts/10_MCBC_Shelf_Execution_Process_Records/2-process_records/script.js`
