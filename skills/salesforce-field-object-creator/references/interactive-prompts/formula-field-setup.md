# Formula Field Setup - Interactive Prompt Guide

This guide outlines the interactive prompt flow for collecting Formula field configuration from users.

## Overview

Formula fields are calculated read-only fields that derive values from other fields using expressions. The skill must collect:
1. Formula expression
2. Return type (data type)
3. Blank handling preference
4. Decimal places (if numeric)

---

## Prompt Flow

### Prompt 1: Formula Expression

**Question**:
```
What is the formula expression for this field?

Examples:
- Text concatenation: FirstName & " " & LastName
- Numeric calculation: Price__c * Quantity__c
- Conditional logic: IF(Amount__c > 10000, "High Value", "Standard")
- Date math: CloseDate - TODAY()
- Cross-object: Account.AnnualRevenue / Account.NumberOfEmployees

Enter your formula expression:
```

**Validation Rules**:
- Cannot be empty
- Must be valid Salesforce formula syntax
- Field references must use API names (with `__c` for custom fields)
- String literals must be in double quotes
- Cross-object references use dot notation (e.g., `Account.Name`)

**Valid Examples**:
```
FirstName & " " & LastName
(Price__c * Quantity__c) * (1 - Discount__c)
IF(Status__c = "Active", "Open", "Closed")
CreatedDate + 30
SQRT(POW(Width__c, 2) + POW(Height__c, 2))
```

**Invalid Examples**:
```
[Empty]                                    → Error: Formula expression required
Price * Quantity                           → Error: Use API names (Price__c, Quantity__c)
IF Status = Active THEN Open              → Error: Invalid syntax (use IF(condition, true, false))
'Text in single quotes'                   → Error: Use double quotes for strings
```

**Metadata Mapping**:
```javascript
{
  "key": "formula",
  "value": "<user_input>"
}
```

---

### Prompt 2: Return Type

**Question**:
```
What is the return type for this formula?

Options:
1. Text - Text string
2. Number - Numeric value
3. Currency - Currency value
4. Percent - Percentage value
5. Date - Calendar date
6. DateTime - Date and time
7. Checkbox - Boolean true/false

Enter return type (1-7 or name):
```

**Validation Rules**:
- Must select one of 7 valid options
- Accept numeric input (1-7) OR type name (case-insensitive)
- Cannot be empty

**Valid Inputs**:
```
1              → Text
Text           → Text
text           → Text
3              → Currency
Currency       → Currency
7              → Checkbox
checkbox       → Checkbox
```

**Invalid Inputs**:
```
[Empty]        → Error: Return type required
8              → Error: Invalid option (1-7 only)
String         → Error: Use "Text" for text return type
Integer        → Error: Use "Number" for numeric values
```

**Metadata Mapping**:
```javascript
{
  "key": "returnType",
  "value": "Text" | "Number" | "Currency" | "Percent" | "Date" | "DateTime" | "Checkbox"
}
```

---

### Prompt 3: Blank Handling (Numeric Return Types Only)

**Conditional**: Only ask if return type is Number, Currency, or Percent

**Question**:
```
How should blank values be handled in this formula?

Options:
1. BlankAsBlank - Treat blanks as blank (default)
2. BlankAsZero - Treat blanks as zero

Enter preference (1-2 or name):
```

**Validation Rules**:
- Only two valid options
- Accept numeric (1-2) OR name (case-insensitive)
- Optional for non-numeric return types (skip this prompt)

**Valid Inputs**:
```
1                  → BlankAsBlank
BlankAsBlank       → BlankAsBlank
blankasblank       → BlankAsBlank
2                  → BlankAsZero
BlankAsZero        → BlankAsZero
[Empty]            → Default to BlankAsBlank
```

**Invalid Inputs**:
```
3                  → Error: Invalid option (1-2 only)
null               → Error: Use "BlankAsBlank" or "BlankAsZero"
```

**Metadata Mapping**:
```javascript
{
  "key": "formulaTreatBlanksAs",
  "value": "BlankAsBlank" | "BlankAsZero"
}
```

---

### Prompt 4: Decimal Places (Numeric Return Types Only)

**Conditional**: Only ask if return type is Number, Currency, or Percent

**Question**:
```
How many decimal places should be displayed? (0-18)

Default: 2 for Currency/Percent, 0 for Number

Enter decimal places:
```

**Validation Rules**:
- Must be integer between 0 and 18
- Default to 2 for Currency/Percent, 0 for Number if empty
- Only applicable for numeric return types

**Valid Inputs**:
```
0              → 0 decimal places
2              → 2 decimal places (currency/percent default)
18             → 18 decimal places (maximum)
[Empty]        → Default (2 for Currency/Percent, 0 for Number)
```

**Invalid Inputs**:
```
-1             → Error: Must be 0-18
19             → Error: Must be 0-18
2.5            → Error: Must be integer
two            → Error: Must be numeric
```

**Metadata Mapping**:
```javascript
{
  "key": "scale",
  "value": 0-18  // Integer
}
```

---

## Complete Example Flow

**Scenario**: Creating "Total Price" formula field on Order_Item__c

```
Q1: What is the formula expression for this field?
A1: Unit_Price__c * Quantity__c

Q2: What is the return type for this formula?
A2: Currency

Q3: How should blank values be handled in this formula?
A3: BlankAsZero

Q4: How many decimal places should be displayed?
A4: 2

Result Metadata:
{
  "Field": "Total_Price__c",
  "Object": "Order_Item__c",
  "Type": "Formula",
  "Options": [
    { "key": "label", "value": "Total Price" },
    { "key": "type", "value": "Formula" },
    { "key": "formula", "value": "Unit_Price__c * Quantity__c" },
    { "key": "returnType", "value": "Currency" },
    { "key": "formulaTreatBlanksAs", "value": "BlankAsZero" },
    { "key": "scale", "value": 2 }
  ]
}
```

---

## Error Handling

### Common Validation Errors

**Empty Formula Expression**:
```
Error: Formula expression cannot be empty. Please enter a valid Salesforce formula.
Example: FirstName & " " & LastName
```

**Invalid Return Type**:
```
Error: Invalid return type. Please select one of:
Text, Number, Currency, Percent, Date, DateTime, Checkbox
```

**Invalid Decimal Places**:
```
Error: Decimal places must be an integer between 0 and 18.
You entered: <invalid_input>
```

### Recovery Actions

1. **Re-prompt** with validation error message
2. **Provide examples** of valid input
3. **Suggest correction** based on detected pattern
4. **Allow user to cancel** and return to main flow

---

## Advanced Features (Future Enhancement)

### Formula Syntax Validation
- Parse formula to validate field references exist
- Check cross-object references for valid relationships
- Validate function usage (SQRT, IF, TEXT, etc.)

### Formula Builder Assistant
- Suggest common formulas based on return type
- Auto-complete field references
- Template library for common patterns

### Return Type Inference
- Analyze formula to suggest appropriate return type
- Warn if formula result may not match selected return type

---

## Source
- [Formula Fields - Salesforce Help](https://help.salesforce.com/s/articleView?id=sf.customize_functions.htm)
- [CustomField Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
