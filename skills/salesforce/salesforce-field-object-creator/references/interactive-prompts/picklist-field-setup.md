# Picklist Field Setup - Interactive Prompt Guide

This guide outlines the interactive prompt flow for collecting Picklist and MultiselectPicklist field configuration.

## Overview

Picklist fields provide dropdown selection lists. The skill must collect:
1. Picklist values (comma-separated)
2. Alphabetically sort values (true/false)
3. Restricted to list (true/false)
4. Default value (optional)
5. Controlling field (optional, for dependent picklists)

---

## Prompt Flow

### Prompt 1: Picklist Values

**Question**:
```
Enter the picklist values (comma-separated).

Examples:
- BOTTLE, CAN, KEG
- Active, Inactive, Pending
- High, Medium, Low

Enter picklist values:
```

**Validation Rules**:
- Cannot be empty
- Values separated by commas
- Leading/trailing whitespace trimmed from each value
- Duplicate values not allowed
- Maximum 1,000 values per picklist
- Each value max 255 characters

**Valid Examples**:
```
BOTTLE, CAN, KEG                          → 3 values
Active, Inactive, Pending, Archived       → 4 values
High,Medium,Low                           → 3 values (no spaces)
Red, Blue, Green                          → 3 values
```

**Invalid Examples**:
```
[Empty]                                   → Error: Values required
BOTTLE; CAN; KEG                          → Error: Use commas, not semicolons
Active, Active, Pending                   → Error: Duplicate value "Active"
```

**Metadata Mapping**:
```javascript
{
  "value_set": {
    "value": [
      { "full_name": "BOTTLE", "default": false, "label": "BOTTLE" },
      { "full_name": "CAN", "default": false, "label": "CAN" },
      { "full_name": "KEG", "default": false, "label": "KEG" }
    ]
  }
}
```

**Processing**:
1. Split by comma
2. Trim whitespace
3. Create value object for each: `{ full_name, label, default: false }`

---

### Prompt 2: Alphabetically Sort Values

**Question**:
```
Should the picklist values be alphabetically sorted in the UI?

Options:
1. Yes - Sort values alphabetically
2. No - Display in the order entered (default)

Enter preference (1-2 or yes/no):
```

**Validation Rules**:
- Accept numeric (1-2), yes/no, or true/false (case-insensitive)
- Optional (defaults to false)

**Valid Inputs**:
```
1                  → true (alphabetically sorted)
2                  → false (order as entered)
Yes                → true
yes                → true
No                 → false
no                 → false
true               → true
false              → false
[Empty]            → Default to false
```

**Invalid Inputs**:
```
3                  → Error: Invalid option (1-2, yes/no, true/false)
sort               → Error: Use "yes" or "true"
```

**Metadata Mapping**:
```javascript
{
  "value_set": {
    "sorted": true | false  // Boolean
  }
}
```

**Note**: If sorted = true, Salesforce UI displays values alphabetically regardless of entry order.

---

### Prompt 3: Restricted to List

**Question**:
```
Should users be restricted to selecting only values from this list?

Options:
1. Yes (recommended) - Users can only select from list (restricted picklist)
2. No - Users can enter custom values (unrestricted picklist)

Enter preference (1-2 or yes/no):
```

**Validation Rules**:
- Accept numeric (1-2), yes/no, or true/false (case-insensitive)
- Optional (defaults to true - restricted)
- Unrestricted picklists are rare and generally discouraged

**Valid Inputs**:
```
1                  → true (restricted)
2                  → false (unrestricted)
Yes                → true
yes                → true
No                 → false
no                 → false
true               → true
false              → false
[Empty]            → Default to true
```

**Invalid Inputs**:
```
3                  → Error: Invalid option (1-2, yes/no, true/false)
allow              → Error: Use "no" or "false" for unrestricted
```

**Metadata Mapping**:
```javascript
{
  "value_set": {
    "value_set_parameters": [
      { "key": "restricted", "value": "true" | "false" }  // String, not boolean
    ]
  }
}
```

**Recommendation**:
```
⚠️  Unrestricted picklists allow users to enter any value.
This can lead to data quality issues and reporting inconsistencies.
Recommended: Restrict to list (option 1)
```

---

### Prompt 4: Default Value (Optional)

**Question**:
```
Do you want to set a default value?

Available values:
1. BOTTLE
2. CAN
3. KEG

Enter default value number, name, or press Enter to skip:
```

**Validation Rules**:
- Optional (press Enter to skip)
- Must be one of the values from Prompt 1
- Accept numeric index or exact value name (case-sensitive)
- Only one value can be default

**Valid Inputs**:
```
[Empty]            → No default
1                  → BOTTLE (first value)
BOTTLE             → BOTTLE (exact match)
KEG                → KEG (exact match)
```

**Invalid Inputs**:
```
4                  → Error: Invalid index (1-3 only)
bottle             → Error: Case-sensitive (use "BOTTLE")
OTHER              → Error: Value not in list
```

**Metadata Mapping**:
```javascript
{
  "value_set": {
    "value": [
      { "full_name": "BOTTLE", "default": false, "label": "BOTTLE" },
      { "full_name": "CAN", "default": false, "label": "CAN" },
      { "full_name": "KEG", "default": true, "label": "KEG" }  // default: true
    ]
  }
}
```

**Note for MultiselectPicklist**: Default value not supported (skip this prompt for multiselect).

---

### Prompt 5: Controlling Field (Optional - Dependent Picklists)

**Question**:
```
Is this a dependent picklist (filtered by another picklist)?

Enter the controlling field API name, or press Enter to skip:

Examples:
- State__c (controls City__c)
- Category__c (controls Subcategory__c)

Enter controlling field API name (or press Enter to skip):
```

**Validation Rules**:
- Optional (press Enter for independent picklist)
- Must be valid field API name on same object
- Controlling field must be a Picklist (not MultiselectPicklist)
- Cannot create circular dependencies

**Valid Inputs**:
```
[Empty]                    → Independent picklist
State__c                   → Dependent on State__c
Category__c                → Dependent on Category__c
Status__c                  → Dependent on Status__c
```

**Invalid Inputs**:
```
state                      → Error: Use exact case (State__c)
State                      → Error: Custom fields must end with __c (State__c)
Description__c             → Error: Controlling field must be Picklist type
```

**Metadata Mapping**:
```javascript
{
  "Options": [
    { "key": "controllingField", "value": "State__c" }
  ]
}
```

**Advanced Dependency Mapping** (future enhancement):
```
If controlling field specified, prompt for value mappings:

For each controlling value, which dependent values should be available?

State: CA (California)
  Available City values: 1,2,3 (San Francisco, Los Angeles, San Diego)

State: NY (New York)
  Available City values: 4,5 (New York City, Buffalo)
```

---

## Complete Example Flows

### Example 1: Simple Picklist

**Scenario**: Container Type picklist on ohfy__Item__c

```
Q1: Enter the picklist values (comma-separated).
A1: BOTTLE, CAN, KEG

Q2: Should the picklist values be alphabetically sorted in the UI?
A2: Yes

Q3: Should users be restricted to selecting only values from this list?
A3: Yes

Q4: Do you want to set a default value?
A4: KEG

Q5: Is this a dependent picklist (filtered by another picklist)?
A5: [Empty - no controlling field]

Result Metadata:
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
      { "full_name": "KEG", "default": true, "label": "KEG" }
    ],
    "value_set_parameters": [
      { "key": "restricted", "value": "true" }
    ]
  }
}
```

---

### Example 2: MultiselectPicklist

**Scenario**: Distribution Channels multiselect on Product__c

```
Q1: Enter the picklist values (comma-separated).
A1: Retail, Wholesale, Online, Direct

Q2: Should the picklist values be alphabetically sorted in the UI?
A2: No

Q3: Should users be restricted to selecting only values from this list?
A3: Yes

Q4: [SKIP - MultiselectPicklist does not support default values]

Q5: Is this a dependent picklist (filtered by another picklist)?
A5: [Empty - no controlling field]

Result Metadata:
{
  "Field": "Distribution_Channels__c",
  "Object": "Product__c",
  "Type": "MultiselectPicklist",
  "Options": [
    { "key": "label", "value": "Distribution Channels" },
    { "key": "type", "value": "MultiselectPicklist" },
    { "key": "visibleLines", "value": 4 }
  ],
  "value_set": {
    "sorted": false,
    "value": [
      { "full_name": "Retail", "default": false, "label": "Retail" },
      { "full_name": "Wholesale", "default": false, "label": "Wholesale" },
      { "full_name": "Online", "default": false, "label": "Online" },
      { "full_name": "Direct", "default": false, "label": "Direct" }
    ],
    "value_set_parameters": [
      { "key": "restricted", "value": "true" }
    ]
  }
}
```

---

### Example 3: Dependent Picklist

**Scenario**: City dependent on State

```
Q1: Enter the picklist values (comma-separated).
A1: San Francisco, Los Angeles, New York City, Buffalo

Q2: Should the picklist values be alphabetically sorted in the UI?
A2: Yes

Q3: Should users be restricted to selecting only values from this list?
A3: Yes

Q4: Do you want to set a default value?
A4: [Empty - no default]

Q5: Is this a dependent picklist (filtered by another picklist)?
A5: State__c

Result Metadata:
{
  "Field": "City__c",
  "Object": "Location__c",
  "Type": "Picklist",
  "Options": [
    { "key": "label", "value": "City" },
    { "key": "type", "value": "Picklist" },
    { "key": "controllingField", "value": "State__c" }
  ],
  "value_set": {
    "sorted": true,
    "value": [
      { "full_name": "San Francisco", "default": false, "label": "San Francisco" },
      { "full_name": "Los Angeles", "default": false, "label": "Los Angeles" },
      { "full_name": "New York City", "default": false, "label": "New York City" },
      { "full_name": "Buffalo", "default": false, "label": "Buffalo" }
    ],
    "value_set_parameters": [
      { "key": "restricted", "value": "true" }
    ]
  }
}

Note: Dependency value mappings require additional configuration via Salesforce UI or Metadata API.
```

---

## Error Handling

### Common Validation Errors

**Empty Values List**:
```
Error: Picklist values cannot be empty. Please enter at least one value.
Example: Active, Inactive, Pending
```

**Duplicate Values**:
```
Error: Duplicate value detected: "Active"
Each picklist value must be unique.
```

**Invalid Default Value**:
```
Error: Default value "OTHER" not found in picklist values.
Available values: BOTTLE, CAN, KEG
```

**Invalid Controlling Field**:
```
Error: Field "Description__c" is not a Picklist type.
Controlling field must be a Picklist field.
```

### Recovery Actions

1. **Re-prompt** with validation error and examples
2. **List available values** when asking for default
3. **Verify controlling field type** before accepting
4. **Remove duplicates** automatically and confirm with user

---

## Advanced Features (Future Enhancement)

### Global Picklist Value Sets
```
Do you want to use a Global Picklist Value Set?
Global picklists can be shared across multiple fields.

Enter Global Picklist API name, or press Enter to create field-specific picklist:
```

### Dependent Picklist Mapping
```
Configure dependency mappings for State → City:

State: CA (California)
  Select available cities: 1,2,3
  1. San Francisco
  2. Los Angeles
  3. San Diego

State: NY (New York)
  Select available cities: 4,5
  4. New York City
  5. Buffalo
```

### Value Import from CSV
```
Do you want to import values from a CSV file?
1. Enter values manually
2. Import from CSV file

If CSV: Provide file path with columns: value, label, default
```

---

## Source
- [Picklist Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_picklist.htm)
- [Dependent Picklists](https://help.salesforce.com/s/articleView?id=sf.fields_dependent_field_considerations.htm)
- [Global Picklist Value Sets](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_globalpicklist.htm)
