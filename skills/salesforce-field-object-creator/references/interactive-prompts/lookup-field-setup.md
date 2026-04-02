# Lookup/MasterDetail Field Setup - Interactive Prompt Guide

This guide outlines the interactive prompt flow for collecting Lookup and MasterDetail relationship field configuration.

## Overview

Relationship fields link two Salesforce objects together. The skill must collect:
1. Related object API name (parent object)
2. Relationship name
3. Delete constraint (Lookup) or reparenting permission (MasterDetail)

---

## Prompt Flow

### Prompt 1: Related Object API Name

**Question**:
```
What object should this relationship field link to?

Enter the API name of the related (parent) object.

Examples:
- Account
- Contact
- Order__c (custom object)
- Product2

Enter related object API name:
```

**Validation Rules**:
- Cannot be empty
- Must be valid Salesforce object API name
- Custom objects must end with `__c`
- Standard objects use exact API name (Account, Contact, etc.)
- Cannot reference the same object (except for Hierarchy on User)

**Valid Examples**:
```
Account                    → Standard object
Contact                    → Standard object
Order__c                   → Custom object
Product2                   → Standard object (special case)
Mandate__c                 → Custom object
```

**Invalid Examples**:
```
[Empty]                    → Error: Related object required
account                    → Error: Use exact case (Account)
Order                      → Error: Custom objects must end with __c (Order__c)
My_Object                  → Error: Custom objects must end with __c (My_Object__c)
```

**Metadata Mapping**:
```javascript
{
  "key": "referenceTo",
  "value": "<object_api_name>"
}
```

---

### Prompt 2: Relationship Name

**Question**:
```
What is the relationship name?

This is used to query related records (e.g., Account.Mandates__r).
Typically the plural form of the child object name.

Examples:
- For Mandate__c → Account: "Mandates"
- For Order_Item__c → Order__c: "Order_Items"
- For Contact → Account: "Contacts"

Enter relationship name:
```

**Validation Rules**:
- Cannot be empty
- Must be valid Salesforce API name format (alphanumeric + underscores)
- Cannot contain spaces or special characters (except underscore)
- Cannot start with a number
- Must be unique within the object

**Valid Examples**:
```
Mandates                   → Simple plural
Order_Items                → Plural with underscore
Custom_Objects             → Multi-word relationship
Related_Accounts           → Descriptive name
```

**Invalid Examples**:
```
[Empty]                    → Error: Relationship name required
Related Objects            → Error: No spaces allowed (use Related_Objects)
123_Items                  → Error: Cannot start with number
Items!                     → Error: No special characters (except underscore)
```

**Metadata Mapping**:
```javascript
{
  "key": "relationshipName",
  "value": "<relationship_name>"
}
```

---

### Prompt 3A: Delete Constraint (Lookup Fields Only)

**Conditional**: Only for Type = "Lookup"

**Question**:
```
What should happen when the parent record is deleted?

Options:
1. SetNull (default) - Clear the lookup field (set to null)
2. Restrict - Prevent parent deletion if children exist
3. Cascade - Delete child records when parent is deleted (rare)

Enter delete constraint (1-3 or name):
```

**Validation Rules**:
- Must select one of 3 valid options
- Accept numeric (1-3) OR name (case-insensitive)
- Optional (defaults to SetNull if empty)

**Valid Inputs**:
```
1                  → SetNull
SetNull            → SetNull
setnull            → SetNull
2                  → Restrict
Restrict           → Restrict
3                  → Cascade
Cascade            → Cascade
[Empty]            → Default to SetNull
```

**Invalid Inputs**:
```
4                  → Error: Invalid option (1-3 only)
Delete             → Error: Use "Cascade" for delete behavior
Clear              → Error: Use "SetNull" to clear field
```

**Metadata Mapping**:
```javascript
{
  "key": "deleteConstraint",
  "value": "SetNull" | "Restrict" | "Cascade"
}
```

**Behavior Explanation**:
- **SetNull**: When parent deleted, lookup field becomes blank (most common)
- **Restrict**: Cannot delete parent if any children reference it (data protection)
- **Cascade**: Deletes all child records when parent deleted (use with caution)

---

### Prompt 3B: Allow Reparenting (MasterDetail Fields Only)

**Conditional**: Only for Type = "MasterDetail"

**Question**:
```
Should users be allowed to reparent (change the parent record)?

Options:
1. No (default) - Parent cannot be changed after creation (recommended)
2. Yes - Allow changing parent record

Enter preference (1-2 or yes/no):
```

**Validation Rules**:
- Accept numeric (1-2), yes/no, or true/false (case-insensitive)
- Optional (defaults to false/No)
- Reparenting is restricted and should be carefully considered

**Valid Inputs**:
```
1                  → false (no reparenting)
2                  → true (allow reparenting)
No                 → false
no                 → false
Yes                → true
yes                → true
false              → false
true               → true
[Empty]            → Default to false
```

**Invalid Inputs**:
```
3                  → Error: Invalid option (1-2, yes/no, true/false)
allow              → Error: Use "yes" or "true"
deny               → Error: Use "no" or "false"
```

**Metadata Mapping**:
```javascript
{
  "key": "reparentableMasterDetail",
  "value": true | false  // Boolean
}
```

**Warning for MasterDetail**:
```
⚠️  MasterDetail relationships have important characteristics:
- Required field (cannot be null)
- Child records deleted when parent deleted (cascade delete)
- Child inherits parent sharing settings
- Maximum 2 master-detail relationships per object
- Cannot be created on objects with existing data
```

---

## Complete Example Flows

### Example 1: Lookup Field

**Scenario**: Creating "Account" lookup on Custom_Object__c

```
Q1: What object should this relationship field link to?
A1: Account

Q2: What is the relationship name?
A2: Custom_Objects

Q3: What should happen when the parent record is deleted?
A3: SetNull

Result Metadata:
{
  "Field": "Account__c",
  "Object": "Custom_Object__c",
  "Type": "Lookup",
  "Options": [
    { "key": "label", "value": "Account" },
    { "key": "type", "value": "Lookup" },
    { "key": "referenceTo", "value": "Account" },
    { "key": "relationshipName", "value": "Custom_Objects" },
    { "key": "deleteConstraint", "value": "SetNull" }
  ]
}
```

---

### Example 2: MasterDetail Field

**Scenario**: Creating "Order" master-detail on Order_Item__c

```
Q1: What object should this relationship field link to?
A1: Order__c

Q2: What is the relationship name?
A2: Order_Items

Q3: Should users be allowed to reparent (change the parent record)?
A3: No

Result Metadata:
{
  "Field": "Order__c",
  "Object": "Order_Item__c",
  "Type": "MasterDetail",
  "Options": [
    { "key": "label", "value": "Order" },
    { "key": "type", "value": "MasterDetail" },
    { "key": "referenceTo", "value": "Order__c" },
    { "key": "relationshipName", "value": "Order_Items" },
    { "key": "reparentableMasterDetail", "value": false }
  ]
}
```

---

## Error Handling

### Common Validation Errors

**Invalid Related Object**:
```
Error: Object "MyObject" not found. Custom objects must end with __c.
Did you mean: MyObject__c?
```

**Duplicate Relationship Name**:
```
Error: Relationship name "Contacts" already exists on Account.
Please choose a unique relationship name.
```

**Invalid Delete Constraint**:
```
Error: Invalid delete constraint. Please select one of:
SetNull, Restrict, Cascade
```

### Recovery Actions

1. **Verify object exists** before prompting for relationship name
2. **Suggest relationship name** based on object name (pluralize)
3. **Warn about MasterDetail implications** before confirming
4. **Allow user to cancel** and switch to Lookup if MasterDetail is too restrictive

---

## Advanced Features (Future Enhancement)

### Object Validation
- Query org metadata to verify related object exists
- Check for circular relationship dependencies
- Validate max 2 MasterDetail relationships per object

### Relationship Name Suggestions
- Auto-suggest plural form of child object
- Check for naming conflicts
- Follow naming conventions (e.g., append "_r" for relationships)

### Delete Constraint Recommendations
- Suggest SetNull for optional relationships
- Recommend Restrict for critical parent records
- Warn about Cascade implications (data loss risk)

---

## Source
- [Relationship Types - Salesforce](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/relationships_among_objects.htm)
- [CustomField Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
- [The 6 Types of Relationships](https://www.salesforceben.com/relationships-in-salesforce/)
