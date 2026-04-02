# Roll-Up Summary Field Setup - Interactive Prompt Guide

This guide outlines the interactive prompt flow for collecting Roll-Up Summary field configuration.

## Overview

Roll-Up Summary fields aggregate values from child records in a MasterDetail relationship. The skill must collect:
1. Child object API name
2. Field to aggregate
3. Aggregation operation (SUM, COUNT, MIN, MAX)
4. Filter criteria (optional)

**Prerequisites**: 
- MasterDetail relationship must exist
- Roll-Up Summary created on parent object
- Summarized field must exist on child object

---

## Prompt Flow

### Prompt 1: Child Object API Name

**Question**:
```
What is the child object containing the data to aggregate?

Enter the child object API name (must have MasterDetail relationship to parent).

Examples:
- Opportunity (if creating roll-up on Account)
- Order_Item__c (if creating roll-up on Order__c)
- Mandate_Item__c (if creating roll-up on Mandate__c)

Enter child object API name:
```

**Validation Rules**:
- Cannot be empty
- Must be valid Salesforce object API name
- Custom objects must end with `__c`
- Must have MasterDetail relationship to the parent object
- Cannot be the same as parent object

**Valid Examples**:
```
Opportunity                → Standard object
Order_Item__c              → Custom object
Mandate_Item__c            → Custom object
Contact                    → Standard object (if has MasterDetail to Account)
```

**Invalid Examples**:
```
[Empty]                    → Error: Child object required
opportunity                → Error: Use exact case (Opportunity)
OrderItem                  → Error: Custom objects must end with __c (Order_Item__c)
Account                    → Error: Cannot roll up to same object (Account → Account)
```

**Metadata Mapping**:
```javascript
// Part of summarizedField (format: ChildObject__c.FieldName__c)
"<child_object_api_name>.<field_to_aggregate>"
```

---

### Prompt 2: Field to Aggregate

**Question**:
```
What field on [ChildObject] should be aggregated?

Enter the field API name to aggregate.

Examples:
- Amount (for Opportunity)
- Quantity__c (for Order_Item__c)
- Id (for COUNT operations)

Enter field API name:
```

**Validation Rules**:
- Cannot be empty
- Must be valid field API name on child object
- Custom fields must end with `__c`
- For COUNT: "Id" is commonly used
- For SUM/MIN/MAX: must be numeric field (Number, Currency, Percent)

**Valid Examples**:
```
Amount                     → Standard currency field
Quantity__c                → Custom number field
Id                         → For COUNT operations
Price__c                   → Custom currency field
Rating__c                  → Custom number field
```

**Invalid Examples**:
```
[Empty]                    → Error: Field name required
amount                     → Error: Use exact case (Amount)
Quantity                   → Error: Custom fields must end with __c (Quantity__c)
Description__c             → Error: Text fields cannot be used with SUM
```

**Metadata Mapping**:
```javascript
{
  "key": "summarizedField",
  "value": "ChildObject__c.FieldName__c"  // Concatenated from Q1 + Q2
}
```

---

### Prompt 3: Aggregation Operation

**Question**:
```
What aggregation operation should be performed?

Options:
1. SUM - Sum of numeric field values
2. COUNT - Count of child records
3. MIN - Minimum value
4. MAX - Maximum value

Enter aggregation operation (1-4 or name):
```

**Validation Rules**:
- Must select one of 4 valid operations
- Accept numeric (1-4) OR operation name (case-insensitive)
- Cannot be empty
- SUM/MIN/MAX require numeric field; COUNT works with any field

**Valid Inputs**:
```
1                  → sum
SUM                → sum
sum                → sum
2                  → count
COUNT              → count
3                  → min
MIN                → min
4                  → max
MAX                → max
```

**Invalid Inputs**:
```
[Empty]            → Error: Operation required
5                  → Error: Invalid option (1-4 only)
AVERAGE            → Error: Not supported (use SUM and COUNT separately)
TOTAL              → Error: Use "SUM" for totals
```

**Metadata Mapping**:
```javascript
{
  "key": "summaryOperation",
  "value": "sum" | "count" | "min" | "max"  // Lowercase
}
```

**Operation Details**:
- **SUM**: Adds all numeric values (nulls treated as 0)
- **COUNT**: Counts number of child records matching criteria
- **MIN**: Returns smallest value (ignores nulls)
- **MAX**: Returns largest value (ignores nulls)

---

### Prompt 4: Filter Criteria (Optional)

**Question**:
```
Do you want to filter which child records are included?

Enter filter criteria in format: FieldName Operator Value
Or press Enter to skip (aggregate all records).

Examples:
- Status__c equals Completed
- Amount__c greaterThan 100
- IsActive__c equals true

Enter filter criteria (or press Enter to skip):
```

**Validation Rules**:
- Optional (press Enter to skip)
- Format: `FieldName Operator Value`
- Valid operators: equals, notEqual, greaterThan, lessThan, greaterOrEqual, lessOrEqual
- Value type must match field type

**Valid Examples**:
```
[Empty]                              → No filter (aggregate all)
Status__c equals Completed           → Text field filter
Amount__c greaterThan 100            → Numeric field filter
IsActive__c equals true              → Boolean field filter
CreatedDate greaterThan 2023-01-01   → Date field filter
```

**Invalid Examples**:
```
Status = Completed                   → Error: Use "equals" operator
Amount > 100                         → Error: Use "greaterThan" operator
Status__c equals                     → Error: Missing value
equals Completed                     → Error: Missing field name
```

**Metadata Mapping**:
```javascript
{
  "key": "summaryFilterItems",
  "value": [
    {
      "field": "Status__c",
      "operation": "equals",
      "value": "Completed"
    }
  ]
}
```

**Supported Operators**:
- `equals` - Exact match
- `notEqual` - Not equal to
- `greaterThan` - Greater than (numeric/date)
- `lessThan` - Less than (numeric/date)
- `greaterOrEqual` - Greater than or equal to
- `lessOrEqual` - Less than or equal to

---

## Complete Example Flows

### Example 1: Sum with Filter

**Scenario**: Total Completed Amount on Order__c

```
Q1: What is the child object containing the data to aggregate?
A1: Order_Item__c

Q2: What field on Order_Item__c should be aggregated?
A2: Amount__c

Q3: What aggregation operation should be performed?
A3: SUM

Q4: Do you want to filter which child records are included?
A4: Status__c equals Completed

Result Metadata:
{
  "Field": "Total_Completed_Amount__c",
  "Object": "Order__c",
  "Type": "Summary",
  "Options": [
    { "key": "label", "value": "Total Completed Amount" },
    { "key": "type", "value": "Summary" },
    { "key": "summarizedField", "value": "Order_Item__c.Amount__c" },
    { "key": "summaryOperation", "value": "sum" }
  ],
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

### Example 2: Count without Filter

**Scenario**: Count of Mandate Items on Mandate__c

```
Q1: What is the child object containing the data to aggregate?
A1: Mandate_Item__c

Q2: What field on Mandate_Item__c should be aggregated?
A2: Id

Q3: What aggregation operation should be performed?
A3: COUNT

Q4: Do you want to filter which child records are included?
A4: [Empty - no filter]

Result Metadata:
{
  "Field": "Total_Items__c",
  "Object": "Mandate__c",
  "Type": "Summary",
  "Options": [
    { "key": "label", "value": "Total Items" },
    { "key": "type", "value": "Summary" },
    { "key": "summarizedField", "value": "Mandate_Item__c.Id" },
    { "key": "summaryOperation", "value": "count" }
  ]
}
```

---

### Example 3: Maximum Value

**Scenario**: Highest Product Rating on Product__c

```
Q1: What is the child object containing the data to aggregate?
A1: Product_Review__c

Q2: What field on Product_Review__c should be aggregated?
A2: Rating__c

Q3: What aggregation operation should be performed?
A3: MAX

Q4: Do you want to filter which child records are included?
A4: [Empty - no filter]

Result Metadata:
{
  "Field": "Highest_Rating__c",
  "Object": "Product__c",
  "Type": "Summary",
  "Options": [
    { "key": "label", "value": "Highest Rating" },
    { "key": "type", "value": "Summary" },
    { "key": "summarizedField", "value": "Product_Review__c.Rating__c" },
    { "key": "summaryOperation", "value": "max" }
  ]
}
```

---

## Error Handling

### Common Validation Errors

**No MasterDetail Relationship**:
```
Error: No MasterDetail relationship found between Order__c and Order_Item__c.
Roll-Up Summary requires MasterDetail relationship.
Please create MasterDetail relationship first or use Formula field instead.
```

**Invalid Field Type for Operation**:
```
Error: Field "Description__c" is Text type, cannot use with SUM operation.
SUM requires numeric field (Number, Currency, Percent).
```

**Invalid Filter Criteria Format**:
```
Error: Filter criteria must be in format: FieldName Operator Value
You entered: Status = Completed
Correct format: Status__c equals Completed
```

### Recovery Actions

1. **Verify MasterDetail exists** before allowing roll-up creation
2. **Validate field type** matches operation (numeric for SUM/MIN/MAX)
3. **Parse filter criteria** with clear error messages
4. **Allow multiple filters** (future enhancement)

---

## Advanced Features (Future Enhancement)

### Multiple Filter Criteria
```
Enter filter criteria (one per line, or press Enter twice to finish):
1. Status__c equals Completed
2. Amount__c greaterThan 100

Result:
{
  "summaryFilterItems": [
    { "field": "Status__c", "operation": "equals", "value": "Completed" },
    { "field": "Amount__c", "operation": "greaterThan", "value": "100" }
  ]
}
```

### Relationship Validation
- Query org to verify MasterDetail relationship exists
- Suggest available child objects with MasterDetail
- List available fields on child object for aggregation

### Operation Recommendations
- Suggest SUM for currency/number fields
- Recommend COUNT for boolean/checkbox fields
- Propose MIN/MAX for rating/score fields

---

## Source
- [Roll-Up Summary Fields - Trailhead](https://trailhead.salesforce.com/content/learn/modules/point_click_business_logic/roll_up_summary_fields)
- [CustomField Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
- [Summary Field Considerations](https://help.salesforce.com/s/articleView?id=sf.fields_about_roll_up_summary_fields.htm)
