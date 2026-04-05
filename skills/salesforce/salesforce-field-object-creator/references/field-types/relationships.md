# Relationship Field Types

This reference covers 5 Salesforce relationship field types for linking objects.

## Field Types in This Category

1. **Lookup** - Loosely-coupled relationship (optional)
2. **MasterDetail** - Tightly-coupled relationship (required, cascading)
3. **Hierarchy** - Self-referencing relationship on User object
4. **ExternalLookup** - Lookup to external data source
5. **IndirectLookup** - Lookup using external ID field

---

## 1. Lookup

**Description**: Optional relationship linking two objects

**Metadata Properties**:
```javascript
{
  "Field": "Account__c",
  "Object": "Custom_Object__c",
  "Type": "Lookup",
  "Options": [
    { "key": "label", "value": "Account" },
    { "key": "type", "value": "Lookup" },
    { "key": "referenceTo", "value": "Account" },                    // Required: related object API name
    { "key": "relationshipName", "value": "Custom_Objects" },        // Required: relationship name
    { "key": "deleteConstraint", "value": "SetNull" }                // Optional: SetNull, Restrict, Cascade
  ]
}
```

**Required**: `label`, `type`, `referenceTo`, `relationshipName`
**Optional**: `deleteConstraint`, `description`, `inlineHelpText`, `required`

**Delete Constraints**:
- `SetNull` (default) - Clear lookup when parent deleted
- `Restrict` - Prevent parent deletion if children exist
- `Cascade` - Delete children when parent deleted (rare for Lookup)

**Interactive Setup Required**: Skill will prompt for:
- Related object API name
- Relationship name
- Delete constraint preference

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Custom_Object__c,Account,Account__c,Lookup,"Interactive: Link to Account object"
```

---

## 2. MasterDetail

**Description**: Required parent-child relationship with cascading behavior

**Metadata Properties**:
```javascript
{
  "Field": "Parent_Account__c",
  "Object": "Mandate__c",
  "Type": "MasterDetail",
  "Options": [
    { "key": "label", "value": "Parent Account" },
    { "key": "type", "value": "MasterDetail" },
    { "key": "referenceTo", "value": "Account" },                    // Required: parent object
    { "key": "relationshipName", "value": "Mandates" },              // Required: relationship name
    { "key": "reparentableMasterDetail", "value": "false" }          // Optional: allow reparenting
  ]
}
```

**Required**: `label`, `type`, `referenceTo`, `relationshipName`
**Optional**: `reparentableMasterDetail`, `description`, `inlineHelpText`

**Key Characteristics**:
- **Required field**: Cannot be null (always has parent)
- **Cascade delete**: Deleting parent deletes all children
- **Sharing inheritance**: Child inherits parent's sharing settings
- **Roll-Up Summary**: Parent can have roll-up summary fields on children
- **Object sharing model**: Child object must use "ControlledByParent" sharing

**Limits**:
- Maximum 2 master-detail relationships per object
- Cannot be created on objects with existing data (must be empty)
- Cannot change to Lookup after creation (destructive change)

**Interactive Setup Required**: Skill will prompt for:
- Parent object API name
- Relationship name
- Allow reparenting (true/false)

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Mandate__c,Parent Account,Parent_Account__c,MasterDetail,"Interactive: Link to Account (parent)"
Mandate_Item__c,Mandate,Mandate__c,MasterDetail,"Interactive: Link to Mandate__c (parent)"
```

---

## 3. Hierarchy

**Description**: Self-referencing relationship (User object only)

**Metadata Properties**:
```javascript
{
  "Field": "Manager__c",
  "Object": "User",
  "Type": "Hierarchy",
  "Options": [
    { "key": "label", "value": "Manager" },
    { "key": "type", "value": "Hierarchy" },
    { "key": "referenceTo", "value": "User" },                       // Always "User" for Hierarchy
    { "key": "relationshipName", "value": "Direct_Reports" }         // Required: relationship name
  ]
}
```

**Required**: `label`, `type`, `referenceTo` (must be "User"), `relationshipName`
**Optional**: `description`, `inlineHelpText`

**Notes**:
- **Only on User object**: Cannot create on custom objects
- **Self-referencing**: Always links User to User
- **Organizational hierarchy**: Build management structures
- **Recursive queries**: Can query up/down hierarchy with SOQL

**Use Case**: Organizational chart, manager-employee relationships

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
User,Manager,Manager__c,Hierarchy,"Interactive: Self-referencing User hierarchy"
```

---

## 4. ExternalLookup

**Description**: Lookup to external object via Salesforce Connect

**Metadata Properties**:
```javascript
{
  "Field": "External_System_Record__c",
  "Object": "Custom_Object__c",
  "Type": "ExternalLookup",
  "Options": [
    { "key": "label", "value": "External System Record" },
    { "key": "type", "value": "ExternalLookup" },
    { "key": "referenceTo", "value": "External_Object__x" },         // Required: external object
    { "key": "relationshipName", "value": "Related_Records" }        // Required: relationship name
  ]
}
```

**Required**: `label`, `type`, `referenceTo` (external object ending in `__x`), `relationshipName`
**Optional**: `description`, `inlineHelpText`

**Prerequisites**:
- Salesforce Connect enabled in org
- External data source configured
- External object created (ends with `__x`)

**Notes**:
- Links Salesforce object to external system data
- External object must exist before creating field
- Real-time data access (no local storage)

**Interactive Setup Required**: Skill will prompt for:
- External object API name (must end with `__x`)
- Relationship name

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Custom_Object__c,External System Record,External_System_Record__c,ExternalLookup,"Interactive: Link to external object"
```

---

## 5. IndirectLookup

**Description**: Lookup using external ID field as link

**Metadata Properties**:
```javascript
{
  "Field": "Partner_Account__c",
  "Object": "Custom_Object__c",
  "Type": "IndirectLookup",
  "Options": [
    { "key": "label", "value": "Partner Account" },
    { "key": "type", "value": "IndirectLookup" },
    { "key": "referenceTo", "value": "Account" },                    // Required: related object
    { "key": "relationshipName", "value": "Partner_Records" },       // Required: relationship name
    { "key": "externalId", "value": "External_ID__c" }               // Required: external ID field on parent
  ]
}
```

**Required**: `label`, `type`, `referenceTo`, `relationshipName`, `externalId`
**Optional**: `description`, `inlineHelpText`

**Prerequisites**:
- Parent object must have an External ID field marked as unique
- External ID field specified must exist on parent object

**Use Case**:
- Integration scenarios where external system uses IDs
- Link records without knowing Salesforce IDs
- Upsert operations using external identifiers

**Interactive Setup Required**: Skill will prompt for:
- Related object API name
- Relationship name
- External ID field name on parent object

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Custom_Object__c,Partner Account,Partner_Account__c,IndirectLookup,"Interactive: Link via external ID"
```

---

## Relationship Comparison

| Feature | Lookup | MasterDetail | Hierarchy | ExternalLookup | IndirectLookup |
|---------|--------|--------------|-----------|----------------|----------------|
| **Required** | Optional | Required | Optional | Optional | Optional |
| **Delete Cascade** | No (default) | Yes (always) | No | No | No |
| **Sharing** | Independent | Inherited | Independent | Independent | Independent |
| **Roll-Up Summary** | No | Yes | No | No | No |
| **Objects** | Any to Any | Any to Any | User to User only | Salesforce to External | Any to Any |
| **Link Method** | Salesforce ID | Salesforce ID | Salesforce ID | External object ID | External ID field |

---

## Common Patterns

### Standard Lookup Pattern
```javascript
{
  "Field": "Contact__c",
  "Object": "Custom_Object__c",
  "Type": "Lookup",
  "Options": [
    { "key": "referenceTo", "value": "Contact" },
    { "key": "relationshipName", "value": "Custom_Objects" },
    { "key": "deleteConstraint", "value": "SetNull" }
  ]
}
```

### Parent-Child MasterDetail Pattern
```javascript
{
  "Field": "Order__c",
  "Object": "Order_Item__c",
  "Type": "MasterDetail",
  "Options": [
    { "key": "referenceTo", "value": "Order__c" },
    { "key": "relationshipName", "value": "Order_Items" }
  ]
}
```

### Integration Indirect Lookup Pattern
```javascript
{
  "Field": "Linked_Product__c",
  "Object": "Integration_Record__c",
  "Type": "IndirectLookup",
  "Options": [
    { "key": "referenceTo", "value": "Product2" },
    { "key": "relationshipName", "value": "Integration_Records" },
    { "key": "externalId", "value": "External_Product_ID__c" }
  ]
}
```

---

## Source
- [CustomField - Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
- [Relationship Types](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/relationships_among_objects.htm)
- [The 6 Types of Relationships in Salesforce](https://www.salesforceben.com/relationships-in-salesforce/)
