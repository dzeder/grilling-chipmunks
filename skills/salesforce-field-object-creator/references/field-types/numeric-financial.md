# Numeric and Financial Field Types

This reference covers 3 Salesforce field types for numeric and financial data.

## Field Types in This Category

1. **Number** - Numeric values with configurable precision and scale
2. **Currency** - Currency values with organization-wide currency settings
3. **Percent** - Percentage values displayed with % symbol

---

## 1. Number

**Description**: Numeric field with configurable decimal places

**Metadata Properties**:
```javascript
{
  "Field": "Consumer_Pack_Count__c",
  "Object": "ohfy__Item__c",
  "Type": "Number",
  "Options": [
    { "key": "label", "value": "Consumer Pack Count" },
    { "key": "type", "value": "Number" },
    { "key": "precision", "value": 18 },          // Required: total digits (max 18)
    { "key": "scale", "value": 0 }                // Required: decimal places (max precision)
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Number"
- `precision` - Total number of digits (1-18)
- `scale` - Number of decimal places (0 to precision value)

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false
- `unique` - true/false
- `externalId` - true/false
- `defaultValue` - Default numeric value

**Precision and Scale Examples**:
```
precision: 18, scale: 0  → Integer: 999,999,999,999,999,999
precision: 18, scale: 2  → Decimal: 9,999,999,999,999,999.99
precision: 10, scale: 2  → Decimal: 99,999,999.99
precision: 5, scale: 2   → Decimal: 999.99
```

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Precision,Scale,Required
ohfy__Item__c,Consumer Pack Count,Consumer_Pack_Count__c,Number,18,0,false
ohfy__Item__c,Primary Unit Volume,Primary_Unit_Volume__c,Number,18,4,false
```

---

## 2. Currency

**Description**: Currency field with automatic formatting and multi-currency support

**Metadata Properties**:
```javascript
{
  "Field": "Unit_Price__c",
  "Object": "ohfy__Item__c",
  "Type": "Currency",
  "Options": [
    { "key": "label", "value": "Unit Price" },
    { "key": "type", "value": "Currency" },
    { "key": "precision", "value": 18 },          // Required: total digits (max 18)
    { "key": "scale", "value": 2 }                // Required: decimal places (typically 2)
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Currency"
- `precision` - Total number of digits (1-18)
- `scale` - Number of decimal places (typically 2 for currency)

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false
- `defaultValue` - Default currency value

**Notes**:
- Automatically formatted with currency symbol based on org settings
- Supports multi-currency if enabled in org
- Negative values displayed in parentheses
- Use for prices, costs, revenue, financial metrics

**Common Currency Configurations**:
```
precision: 18, scale: 2  → $9,999,999,999,999,999.99 (standard pricing)
precision: 16, scale: 2  → $99,999,999,999,999.99 (large transactions)
precision: 10, scale: 2  → $99,999,999.99 (typical business use)
```

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Precision,Scale,Required
ohfy__Item__c,Unit Price,Unit_Price__c,Currency,18,2,true
ohfy__Item__c,Wholesale Cost,Wholesale_Cost__c,Currency,18,2,false
```

---

## 3. Percent

**Description**: Percentage field displayed with % symbol

**Metadata Properties**:
```javascript
{
  "Field": "Alcohol_Content__c",
  "Object": "ohfy__Item__c",
  "Type": "Percent",
  "Options": [
    { "key": "label", "value": "Alcohol Content" },
    { "key": "type", "value": "Percent" },
    { "key": "precision", "value": 18 },          // Required: total digits (max 18)
    { "key": "scale", "value": 2 }                // Required: decimal places
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Percent"
- `precision` - Total number of digits (1-18)
- `scale` - Number of decimal places

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false
- `defaultValue` - Default percentage value (e.g., 0.05 for 5%)

**Notes**:
- Stored as decimal (0.05 = 5%)
- Displayed with % symbol in UI
- Use for rates, percentages, ratios
- Common scale values: 0 (whole %), 1 (one decimal), 2 (two decimals)

**Storage vs Display**:
```
Stored: 0.05    → Displayed: 5%
Stored: 0.125   → Displayed: 12.5%
Stored: 1.00    → Displayed: 100%
```

**Common Percent Configurations**:
```
precision: 3, scale: 0  → 0-100% (whole percentages)
precision: 5, scale: 2  → 0-100.00% (two decimal precision)
precision: 6, scale: 3  → 0-100.000% (three decimal precision)
```

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Precision,Scale,DefaultValue
ohfy__Item__c,Alcohol Content,Alcohol_Content__c,Percent,5,2,0
ohfy__Item__c,Discount Rate,Discount_Rate__c,Percent,3,0,0
```

---

## Common Patterns for Numeric Fields

### Integer Pattern (No Decimals)
For whole numbers like quantities, counts:
```javascript
{
  "Field": "Quantity__c",
  "Object": "Order_Item__c",
  "Type": "Number",
  "Options": [
    { "key": "label", "value": "Quantity" },
    { "key": "type", "value": "Number" },
    { "key": "precision", "value": 18 },
    { "key": "scale", "value": 0 },
    { "key": "required", "value": "true" }
  ]
}
```

### Decimal Pattern (2 Decimal Places)
For measurements, weights, dimensions:
```javascript
{
  "Field": "Weight_LBS__c",
  "Object": "ohfy__Item__c",
  "Type": "Number",
  "Options": [
    { "key": "label", "value": "Weight (LBS)" },
    { "key": "type", "value": "Number" },
    { "key": "precision", "value": 18 },
    { "key": "scale", "value": 2 }
  ]
}
```

### High Precision Pattern (4 Decimal Places)
For precise measurements, scientific data:
```javascript
{
  "Field": "Volume_ML__c",
  "Object": "ohfy__Item__c",
  "Type": "Number",
  "Options": [
    { "key": "label", "value": "Volume (ML)" },
    { "key": "type", "value": "Number" },
    { "key": "precision", "value": 18 },
    { "key": "scale", "value": 4 }
  ]
}
```

### Currency with Default Pattern
For prices with default values:
```javascript
{
  "Field": "Base_Price__c",
  "Object": "Product__c",
  "Type": "Currency",
  "Options": [
    { "key": "label", "value": "Base Price" },
    { "key": "type", "value": "Currency" },
    { "key": "precision", "value": 18 },
    { "key": "scale", "value": 2 },
    { "key": "defaultValue", "value": "0.00" }
  ]
}
```

### Percentage with Validation Pattern
For percentages with typical precision:
```javascript
{
  "Field": "Completion_Rate__c",
  "Object": "Project__c",
  "Type": "Percent",
  "Options": [
    { "key": "label", "value": "Completion Rate" },
    { "key": "type", "value": "Percent" },
    { "key": "precision", "value": 5 },
    { "key": "scale", "value": 2 },
    { "key": "defaultValue", "value": "0" }
  ]
}
```

---

## Validation Considerations

### Precision Limits
- Maximum precision: 18 digits total
- Scale cannot exceed precision
- Integer fields: scale = 0
- Financial data: typically scale = 2

### Default Values
- Must match field's scale (e.g., scale=2 requires "123.45" not "123.4")
- Percent defaults stored as decimal (5% = 0.05)
- Currency defaults should match expected precision

### Display Behavior
- Number: Displayed as entered (1000 or 1,000 based on locale)
- Currency: Always includes currency symbol and thousands separator
- Percent: Always includes % symbol

---

## Source
- [CustomField - Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
- [Metadata Field Types](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_field_types.htm)
- [Custom Field Types - Salesforce Help](https://help.salesforce.com/s/articleView?id=platform.custom_field_types.htm)
