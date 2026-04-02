# Workflow Script Template: Define Objects and Fields

## Overview

This script generates SOAP XML payloads for the Salesforce Metadata API `create` operation. It transforms field/object definitions from CSV-parsed data structures into properly formatted XML metadata for creating custom objects and fields.

## When to Use This Template

Use this template for the **first step** in a Salesforce metadata creation workflow:
- Creating custom fields on existing objects
- Creating custom objects with configuration
- Batch metadata operations requiring SOAP XML formatting

## Script Purpose

**Input**: Array of field/object definitions with type-specific parameters
**Output**: SOAP XML payload ready for Salesforce Metadata API submission
**Key Operations**:
1. Transform JSON field definitions into Salesforce metadata structure
2. Generate properly formatted SOAP XML
3. Validate field/object configurations
4. Handle type-specific attributes (picklists, relationships, etc.)

## Code Structure Pattern

### Orchestration-Only exports.step

```javascript
exports.step = function (input, fileInput) {
  // 1. Create configuration structure
  const config = {
    customFields: FIELDS  // or customObjects: OBJECTS
  };

  // 2. Optional: Validate all fields/objects
  config.customFields.forEach((field, index) => {
    const customField = createBaseCustomField(field);
    const validation = validateCustomField(customField);
    if (!validation.isValid) {
      console.error(`Validation errors for field ${index + 1}:`, validation.errors);
    }
  });

  // 3. Generate XML payload
  const xmlPayload = generateSalesforceXML(config);
  
  return { xmlPayload };
};
```

**Key Principle**: exports.step orchestrates only - all logic delegated to helper functions defined below.

### Field Definition Constants

Define your field specifications as a constant array:

```javascript
const FIELDS = [
  {
    "Field": "Outer_Pack_UPC__c",
    "Object": "ohfy__Item__c",
    "Type": "Text",
    "Options": [
      { "key": "label", "value": "Outer Pack UPC" },
      { "key": "type", "value": "Text" },
      { "key": "length", "value": "255" }
    ]
  },
  {
    "Field": "Container_Type__c",
    "Object": "ohfy__Item__c",
    "Type": "Picklist",
    "Options": [
      { "key": "label", "value": "Container Type" },
      { "key": "type", "value": "Picklist" },
      { "key": "required", "value": false }
    ],
    "value_set": {
      "sorted": true,
      "value": [
        { "full_name": "BOTTLE", "default": false, "label": "BOTTLE" },
        { "full_name": "CAN", "default": false, "label": "CAN" },
        { "full_name": "KEG", "default": false, "label": "KEG" }
      ],
      "value_set_parameters": [
        { "key": "restricted", "value": "true" }
      ]
    }
  },
  {
    "Field": "Consumer_Pack_Count__c",
    "Object": "ohfy__Item__c",
    "Type": "Number",
    "Options": [
      { "key": "label", "value": "Consumer Pack Count" },
      { "key": "type", "value": "Number" },
      { "key": "precision", "value": 18 },
      { "key": "scale", "value": 0 }
    ]
  }
];
```

### Helper Functions (All Defined Below exports.step)

#### 1. Base Field Creator

```javascript
// Define the base custom field structure once
const createBaseCustomField = (field) => ({
  "full_name": `${field.Object}.${field.Field}`,
  "object": field.Object,
  "type": field.Type,
  "field": field.Field,
  "custom_field_parameters": field.Options || [],
  "value_set": field.value_set || default_value_set
});
```

#### 2. Field Transformer with Type-Specific Handling

```javascript
const default_value_set = { "sorted": false };

// Transform the original fields into the format expected by the connector
const customFields = FIELDS.map(field => {
  // Start with the base structure for all field types
  let customField = createBaseCustomField(field);

  // Handle picklist fields with specific values
  if (field.Type === "Picklist" || field.Type === "MultiselectPicklist") {
    if (field.value_set && field.value_set.value) {
      // For picklists with defined values, use the complete value_set from field definition
      customField = {
        ...createBaseCustomField(field),
        "value_set": field.value_set
      };
    }
  }

  return customField;
});
```

#### 3. XML Generation Function

For **Custom Objects**:

```javascript
/**
 * Generates XML metadata for a single custom object
 * @param {Object} customObject - Custom object configuration
 * @returns {string} XML metadata string
 */
function generateCustomObjectMetadata(customObject) {
  const optionalFeatures = [];

  // Optional Features
  if (customObject.enableReports !== undefined) {
    optionalFeatures.push(`            <cmd:enableReports>${customObject.enableReports}</cmd:enableReports>`);
  }
  if (customObject.enableActivities !== undefined) {
    optionalFeatures.push(`            <cmd:enableActivities>${customObject.enableActivities}</cmd:enableActivities>`);
  }
  if (customObject.enableHistory !== undefined) {
    optionalFeatures.push(`            <cmd:enableHistory>${customObject.enableHistory}</cmd:enableHistory>`);
  }

  // Object Classification
  if (customObject.enableSharing !== undefined) {
    optionalFeatures.push(`            <cmd:enableSharing>${customObject.enableSharing}</cmd:enableSharing>`);
  }
  if (customObject.enableBulkApi !== undefined) {
    optionalFeatures.push(`            <cmd:enableBulkApi>${customObject.enableBulkApi}</cmd:enableBulkApi>`);
  }
  if (customObject.enableStreamingApi !== undefined) {
    optionalFeatures.push(`            <cmd:enableStreamingApi>${customObject.enableStreamingApi}</cmd:enableStreamingApi>`);
  }

  // Search Status
  if (customObject.enableSearch !== undefined) {
    optionalFeatures.push(`            <cmd:enableSearch>${customObject.enableSearch}</cmd:enableSearch>`);
  }

  const optionalFeaturesXML = optionalFeatures.length > 0 ? '\n' + optionalFeatures.join('\n') : '';

  // Handle AutoNumber format if present
  let nameFieldXML = `            <cmd:nameField>
               <cmd:label>${customObject.nameFieldLabel}</cmd:label>
               <cmd:type>${customObject.nameFieldType}</cmd:type>`;
  
  if (customObject.nameFieldType === "AutoNumber" && customObject.nameFieldFormat) {
    nameFieldXML += `
               <cmd:displayFormat>${customObject.nameFieldFormat}</cmd:displayFormat>`;
  }
  
  nameFieldXML += `
            </cmd:nameField>`;

  return `         <cmd:metadata xsi:type="cmd:CustomObject">
            <cmd:fullName>${customObject.fullName}</cmd:fullName>
            <cmd:label>${customObject.label}</cmd:label>
            <cmd:pluralLabel>${customObject.pluralLabel}</cmd:pluralLabel>
            <cmd:deploymentStatus>${customObject.deploymentStatus}</cmd:deploymentStatus>
            <cmd:sharingModel>${customObject.sharingModel}</cmd:sharingModel>${optionalFeaturesXML}
${nameFieldXML}
         </cmd:metadata>`;
}

/**
 * Converts JSON template to Salesforce SOAP XML body
 * @param {Object} config - Configuration object with customObjects array
 * @returns {string} SOAP XML body payload
 */
function generateSalesforceXML(config) {
  const { customObjects } = config;

  // Generate metadata for all custom objects
  const metadataXML = customObjects
    .map(obj => generateCustomObjectMetadata(obj))
    .join('\n');

  return `<soapenv:Body>
      <cmd:create>
${metadataXML}
      </cmd:create>
   </soapenv:Body>`;
}
```

For **Custom Fields** (simpler structure):

The XML generation for fields is typically handled by the Tray Salesforce connector directly when you pass the transformed field array. Focus on transforming the CSV data into the connector's expected format.

#### 4. Validation Functions

```javascript
/**
 * Validates custom object configuration
 * @param {Object} customObject - Custom object to validate
 * @returns {Object} Validation result with isValid and errors
 */
function validateCustomObject(customObject) {
  const errors = [];

  if (!customObject.fullName) {
    errors.push("fullName is required");
  } else if (!customObject.fullName.endsWith('__c')) {
    errors.push("fullName must end with '__c'");
  }

  if (!customObject.label) {
    errors.push("label is required");
  }

  const validDeploymentStatuses = ["Deployed", "InDevelopment"];
  if (!validDeploymentStatuses.includes(customObject.deploymentStatus)) {
    errors.push(`deploymentStatus must be one of: ${validDeploymentStatuses.join(', ')}`);
  }

  const validSharingModels = ["ReadWrite", "Read", "Private", "ControlledByParent"];
  if (!validSharingModels.includes(customObject.sharingModel)) {
    errors.push(`sharingModel must be one of: ${validSharingModels.join(', ')}`);
  }

  const validNameFieldTypes = ["AutoNumber", "Text"];
  if (!validNameFieldTypes.includes(customObject.nameFieldType)) {
    errors.push(`nameFieldType must be one of: ${validNameFieldTypes.join(', ')}`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}
```

## Complete Working Examples

### Example 1: Custom Fields (MCBC Salsify Pattern)

**Source**: `/Users/derekhsquires/Documents/Ohanafy/Integrations/01-tray/Embedded/MCBC_Salsify_SANDBOX/versions/current/scripts/91_MCBC_Salsify_Custom_Fields/1-define_fields/script.js`

**What it does**: Defines 63 custom fields across 3 Salesforce objects (Item__c, Item_Type__c, Account) for product data management.

**Key features**:
- Handles Text, Picklist, MultiselectPicklist, Number, Date, LongTextArea field types
- Manages picklist value sets with restriction settings
- Supports precision/scale for numeric fields
- Organized by logical field groupings (packaging, dimensions, nutrition, images)

### Example 2: Custom Objects (MCBC Shelf Execution Pattern)

**Source**: `/Users/derekhsquires/Documents/Ohanafy/Integrations/01-tray/Embedded/MCBC_Shelf_Execution_PRODUCTION/versions/current/scripts/90_MCBC_Shelf_Execution_Custom_Objects/1-define_objects/script.js`

**What it does**: Creates 2 custom objects (Mandate__c, Mandate_Item__c) with master-detail relationships and full feature configuration.

**Key features**:
- AutoNumber name field with custom format
- Master-detail sharing model (ControlledByParent)
- Comprehensive optional features (Reports, Activities, History, Search, etc.)
- Validation for deployment status, sharing model, name field types

## Field Type Reference Integration

This template connects with the field type reference documents in the skill:

- **Text fields**: See `text-based-fields.md` for Text, LongTextArea, RichTextArea patterns
- **Picklist fields**: See `picklist-fields.md` for Picklist, MultiselectPicklist, value_set structure
- **Number fields**: See `number-currency-fields.md` for Number, Currency, Percent, precision/scale
- **Date fields**: See `date-time-fields.md` for Date, DateTime, Time patterns
- **Lookup fields**: See `lookup-relationship-fields.md` for Lookup, MasterDetail relationships
- **Boolean/Formula**: See `boolean-formula-fields.md` and `special-fields.md`

## Common Customizations

### Adding Dynamic Field Generation

If fields come from input rather than constants:

```javascript
exports.step = function (input, fileInput) {
  // Transform input data into field definitions
  const customFields = input.csv_rows.map(row => ({
    "Field": row.field_api_name,
    "Object": row.object_name,
    "Type": row.field_type,
    "Options": parseOptions(row)
  }));

  const config = { customFields };
  const xmlPayload = generateSalesforceXML(config);
  
  return { xmlPayload };
};

function parseOptions(row) {
  // Transform row data into Options array
  const options = [
    { "key": "label", "value": row.field_label },
    { "key": "type", "value": row.field_type }
  ];
  
  if (row.field_type === "Text") {
    options.push({ "key": "length", "value": row.field_length || "255" });
  }
  
  return options;
}
```

### Supporting Additional Field Types

Extend the transformation logic:

```javascript
const customFields = FIELDS.map(field => {
  let customField = createBaseCustomField(field);

  // Picklist handling
  if (field.Type === "Picklist" || field.Type === "MultiselectPicklist") {
    if (field.value_set && field.value_set.value) {
      customField = {
        ...createBaseCustomField(field),
        "value_set": field.value_set
      };
    }
  }
  
  // Lookup/MasterDetail handling (if needed)
  if (field.Type === "Lookup" || field.Type === "MasterDetail") {
    customField = {
      ...customField,
      "referenceTo": field.referenceTo,
      "relationshipName": field.relationshipName
    };
  }

  return customField;
});
```

## Tray.ai Functional Programming Requirements

- **Pure functions**: All helper functions must be pure (no side effects)
- **Immutability**: Never mutate input parameters - use spread operator for modifications
- **No imports**: Only use pre-installed libraries (lodash, moment-timezone, crypto, Buffer, URL)
- **Orchestration pattern**: exports.step orchestrates only, all logic in helpers below
- **Destructuring**: Use for 3-5 input parameters, object parameters for 6+

## Next Steps in Workflow

After generating the XML payload:
1. **Submit to Salesforce Metadata API** using HTTP connector with SOAP action
2. **Extract asyncProcessId values** from response using template `2-extract-jobids.md`
3. **Poll job status** and handle errors using template `3-evaluate-statuses.md`

## Related Resources

- Field type specifications: `../field-types/`
- CSV format specification: `../csv-format.md`
- Tray functional programming patterns: `.claude/rules/tray-function-patterns.md`
- Salesforce API patterns: `.claude/rules/salesforce-api.md`
