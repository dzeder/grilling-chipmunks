# Calculated Field Types

This reference covers 2 Salesforce calculated field types that derive values from other fields.

## Field Types in This Category

1. **Formula** - Calculated field based on formula expression
2. **Summary** (Roll-Up Summary) - Aggregate calculations on child records

---

## 1. Formula

**Description**: Read-only field calculated from formula expression

**Metadata Properties**:
```javascript
{
  "Field": "Full_Name__c",
  "Object": "Contact",
  "Type": "Formula",
  "Options": [
    { "key": "label", "value": "Full Name" },
    { "key": "type", "value": "Formula" },
    { "key": "formula", "value": "FirstName & \" \" & LastName" },              // Required: formula expression
    { "key": "formulaTreatBlanksAs", "value": "BlankAsBlank" },                // Optional: BlankAsBlank or BlankAsZero
    { "key": "returnType", "value": "Text" }                                    // Required: return type
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Formula"
- `formula` - Formula expression
- `returnType` - Data type of formula result

**Optional**:
- `formulaTreatBlanksAs` - How to handle blank values:
  - `BlankAsBlank` (default) - Treat blanks as blank
  - `BlankAsZero` - Treat blanks as zero (numeric formulas)
- `description` - Field description
- `inlineHelpText` - Help text
- `scale` - Decimal places (for Number/Currency/Percent return types)

**Return Types**:
- `Text` - Text string
- `Number` - Numeric value
- `Currency` - Currency value
- `Percent` - Percentage value
- `Date` - Calendar date
- `DateTime` - Date and time
- `Checkbox` - Boolean true/false

**Formula Syntax**:
- **Text concatenation**: `FirstName & " " & LastName`
- **Math operations**: `(Price__c * Quantity__c) * (1 - Discount__c)`
- **Conditional logic**: `IF(Status__c = "Active", "Open", "Closed")`
- **Date calculations**: `CloseDate - TODAY()`
- **Cross-object references**: `Account.Industry`

**Interactive Setup Required**: Skill will prompt for:
- Formula expression
- Return type
- Blank handling (BlankAsBlank or BlankAsZero)
- Decimal places (if numeric return type)

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Contact,Full Name,Full_Name__c,Formula,"Interactive: Enter formula expression"
ohfy__Item__c,Total Weight,Total_Weight__c,Formula,"Interactive: Calculate from unit weight * quantity"
```

**Common Formula Examples**:
```javascript
// Text concatenation
"formula": "FirstName & \" \" & LastName"

// Numeric calculation
"formula": "Price__c * Quantity__c"

// Conditional
"formula": "IF(Amount__c > 10000, \"High Value\", \"Standard\")"

// Date math
"formula": "CreatedDate + 30"

// Cross-object
"formula": "Account.AnnualRevenue / Account.NumberOfEmployees"
```

---

## 2. Summary (Roll-Up Summary)

**Description**: Aggregate calculation on child records (MasterDetail relationships only)

**Metadata Properties**:
```javascript
{
  "Field": "Total_Quantity_Fulfilled__c",
  "Object": "Mandate__c",
  "Type": "Summary",
  "Options": [
    { "key": "label", "value": "Total Quantity Fulfilled" },
    { "key": "type", "value": "Summary" },
    { "key": "summarizedField", "value": "Mandate_Item__c.Quantity_Fulfilled__c" },  // Required: child field
    { "key": "summaryOperation", "value": "sum" }                                     // Required: operation type
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Summary"
- `summarizedField` - Child object field to aggregate (format: `ChildObject__c.FieldName__c`)
- `summaryOperation` - Aggregation operation

**Optional**:
- `summaryFilterItems` - Filter criteria for which child records to include
- `description` - Field description
- `inlineHelpText` - Help text

**Summary Operations**:
- `sum` - Sum of numeric field values
- `count` - Count of child records
- `min` - Minimum value
- `max` - Maximum value

**Prerequisites**:
- **MasterDetail relationship required**: Roll-up summary only works on parent objects with master-detail children
- Must be created on parent object
- Summarized field must exist on child object

**Filter Criteria** (optional):
```javascript
{
  "summaryFilterItems": [
    {
      "field": "Status__c",
      "operation": "equals",
      "value": "Completed"
    }
  ]
}
```

**Interactive Setup Required**: Skill will prompt for:
- Child object API name
- Field to aggregate
- Aggregation operation (SUM, COUNT, MIN, MAX)
- Filter criteria (optional)

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Mandate__c,Total Quantity Fulfilled,Total_Quantity_Fulfilled__c,Summary,"Interactive: SUM of Mandate_Item__c.Quantity_Fulfilled__c"
Order__c,Total Order Amount,Total_Order_Amount__c,Summary,"Interactive: SUM of Order_Item__c.Amount__c"
```

**Common Roll-Up Patterns**:
```javascript
// Sum child amounts
{
  "summarizedField": "Order_Item__c.Amount__c",
  "summaryOperation": "sum"
}

// Count child records
{
  "summarizedField": "Contact.Id",
  "summaryOperation": "count"
}

// Maximum value
{
  "summarizedField": "Opportunity.Amount",
  "summaryOperation": "max"
}

// Minimum value
{
  "summarizedField": "Product_Review__c.Rating__c",
  "summaryOperation": "min"
}

// Filtered sum (only completed)
{
  "summarizedField": "Invoice__c.Amount__c",
  "summaryOperation": "sum",
  "summaryFilterItems": [
    {
      "field": "Status__c",
      "operation": "equals",
      "value": "Completed"
    }
  ]
}
```

---

## Formula vs Summary Comparison

| Feature | Formula | Summary |
|---------|---------|---------|
| **Calculation** | Expression-based | Aggregation-based |
| **Data Source** | Same record + related | Child records |
| **Editability** | Read-only (always) | Read-only (always) |
| **Relationship Req** | Any (or none) | MasterDetail required |
| **Performance** | Calculated on display | Calculated on save |
| **Use Cases** | Text concat, math, conditionals | SUM, COUNT, MIN, MAX |

---

## Source
- [CustomField - Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
- [Formula Field Types](https://help.salesforce.com/s/articleView?id=sf.customize_functions.htm)
- [Roll-Up Summary Fields - Trailhead](https://trailhead.salesforce.com/content/learn/modules/point_click_business_logic/roll_up_summary_fields)
