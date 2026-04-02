# CSV Format Specification

This document defines the expected CSV format for Salesforce object and field definitions.

## Required Columns

Every CSV must include these columns:

| Column | Description | Example | Validation |
|--------|-------------|---------|------------|
| `Object` | Object API name | `ohfy__Item__c`, `Account`, `Mandate__c` | Must end with `__c` for custom objects |
| `Field_Label` | Human-readable field label | `Product Name`, `Total Amount` | Max 40 characters |
| `API_Name` | Field API name | `Product_Name__c`, `Total_Amount__c` | Max 40 chars (excluding `__c`), alphanumeric + underscore only |
| `Type` | Salesforce field type | `Text`, `Number`, `Picklist`, `MasterDetail` | Must match one of 28 valid field types |
| `Notes` | Description or configuration hints | `Product identifier from supplier` | Optional, free text |

---

## Optional Columns (Simple Field Types)

These columns provide additional configuration for simple field types (Text, Number, Date, etc.):

| Column | Applies To | Description | Example |
|--------|------------|-------------|---------|
| `Length` | Text, TextArea, LongTextArea, EncryptedText, Html | Character limit | `255`, `32768` |
| `Precision` | Number, Currency, Percent | Total digits | `18`, `10` |
| `Scale` | Number, Currency, Percent, Location | Decimal places | `2`, `4` |
| `Required` | All types | Is field required | `true`, `false` |
| `Unique` | Text, Email, Number, Phone, Url | Enforce uniqueness | `true`, `false` |
| `ExternalId` | Text, Email, Number | Mark as external ID | `true`, `false` |
| `DefaultValue` | Text, Number, Currency, Percent, Checkbox, Date, DateTime | Default value | `0`, `true`, `2025-01-01` |
| `VisibleLines` | LongTextArea, Html, Multiselect Picklist | UI display lines | `3`, `5` |
| `MaskChar` | EncryptedText | Mask character | `asterisk`, `X` |
| `MaskType` | EncryptedText | Mask pattern | `all`, `lastFour`, `creditCard` |

---

## Complex Field Types (Interactive Setup Required)

These field types cannot be fully configured via CSV columns. The skill will prompt for configuration:

### Formula Fields
**CSV Columns**: Object, Field_Label, API_Name, Type=Formula, Notes
**Interactive Prompts**:
- Formula expression (e.g., `FirstName & " " & LastName`)
- Return type (Text, Number, Date, DateTime, Checkbox, Currency, Percent)
- Blank handling (BlankAsBlank or BlankAsZero)
- Decimal places (if numeric return type)

### Lookup / MasterDetail Fields
**CSV Columns**: Object, Field_Label, API_Name, Type=Lookup or MasterDetail, Notes
**Interactive Prompts**:
- Related object API name (e.g., `Account`, `ohfy__Item__c`)
- Relationship name (e.g., `Accounts`, `Items`)
- Delete constraint (SetNull, Restrict, Cascade) - Lookup only
- Allow reparenting (true/false) - MasterDetail only

### Roll-Up Summary Fields
**CSV Columns**: Object, Field_Label, API_Name, Type=Summary, Notes
**Interactive Prompts**:
- Child object API name (e.g., `Mandate_Item__c`)
- Field to aggregate (e.g., `Quantity_Fulfilled__c`)
- Aggregation operation (SUM, COUNT, MIN, MAX)
- Filter criteria (optional)

### Picklist / MultiselectPicklist Fields
**CSV Columns**: Object, Field_Label, API_Name, Type=Picklist, Notes
**Interactive Prompts**:
- Comma-separated picklist values (e.g., `BOTTLE, CAN, KEG`)
- Alphabetically sort values (true/false)
- Restricted to list (true/false)
- Default value (optional)
- Controlling field (optional, for dependent picklists)

### Hierarchy Fields
**CSV Columns**: Object=User, Field_Label, API_Name, Type=Hierarchy, Notes
**Interactive Prompts**:
- Relationship name (e.g., `Direct_Reports`)

### ExternalLookup Fields
**CSV Columns**: Object, Field_Label, API_Name, Type=ExternalLookup, Notes
**Interactive Prompts**:
- External object API name (must end with `__x`)
- Relationship name

### IndirectLookup Fields
**CSV Columns**: Object, Field_Label, API_Name, Type=IndirectLookup, Notes
**Interactive Prompts**:
- Related object API name
- Relationship name
- External ID field name on parent object

---

## CSV Format Rules

### General Rules
- **Header row required**: First row must contain column names
- **Case-sensitive columns**: Use exact column names (`API_Name`, not `api_name` or `Api_Name`)
- **No empty rows**: Skip blank rows or rows with all empty cells
- **Consistent object grouping**: Group fields by object for clarity (not required, but recommended)

### Field Naming Rules
- **API Name format**: Letters, numbers, underscores only
- **API Name start**: Must start with a letter
- **API Name end**: Custom fields must end with `__c`
- **API Name length**: Max 40 characters (excluding `__c` suffix)
- **Label length**: Max 40 characters
- **Reserved words**: Avoid Apex/Salesforce reserved words (Id, Name, OwnerId, etc.)

### Type Validation
Must be one of these 28 valid types (case-insensitive):
- **Basic Text**: Text, TextArea, LongTextArea, Html, EncryptedText, Email, Phone, Url
- **Numeric**: Number, Currency, Percent
- **Date/Time**: Date, DateTime, Time
- **Selection**: Checkbox, Picklist, MultiselectPicklist
- **Relationship**: Lookup, MasterDetail, Hierarchy, ExternalLookup, IndirectLookup
- **Calculated**: Formula, Summary
- **Special**: AutoNumber, Location

### Object Naming Rules
- **Custom object suffix**: Must end with `__c` for custom objects
- **Standard objects**: Use exact API name (Account, Contact, User, etc.)
- **Namespace prefix**: Include if using managed package namespace (e.g., `ohfy__Item__c`)

---

## Example CSV Structure

### Minimal Valid CSV
```csv
Object,Field_Label,API_Name,Type,Notes
Mandate__c,Activity Name,Activity_Name__c,Text,"From activity_name field"
Mandate__c,Start Date,Start_Date__c,Date,"Campaign start date"
Mandate__c,Ship Number,Ship_Number__c,Number,"Shipment tracking number"
```

### Complete CSV with Optional Columns
```csv
Object,Field_Label,API_Name,Type,Length,Precision,Scale,Required,Unique,ExternalId,DefaultValue,Notes
ohfy__Item__c,Product Name,Product_Name__c,Text,255,,,true,false,false,,"Primary product identifier"
ohfy__Item__c,Unit Price,Unit_Price__c,Currency,,18,2,true,false,false,0.00,"Base product price"
ohfy__Item__c,Consumer Pack Count,Consumer_Pack_Count__c,Number,,18,0,false,false,false,1,"Units per consumer pack"
ohfy__Item__c,Retail Start Date,Retail_Start_Date__c,Date,,,,,,,,"Product launch date"
ohfy__Item__c,Active,Active__c,Checkbox,,,,,,,true,"Is product active"
```

### Mixed Simple and Complex Fields
```csv
Object,Field_Label,API_Name,Type,Length,Required,Notes
Product__c,SKU,SKU__c,Text,100,true,"Unique product SKU"
Product__c,Base Price,Base_Price__c,Currency,,true,"Standard pricing"
Product__c,Account,Account__c,MasterDetail,,"Interactive: Link to Account (parent)"
Product__c,Total Revenue,Total_Revenue__c,Formula,,"Interactive: SUM child order amounts"
Product__c,Status,Status__c,Picklist,,"Interactive: Active, Inactive, Discontinued"
```

---

## CSV Validation Checklist

Before generating scripts, the skill validates:

 **Required Columns**:
- [ ] Object column present and not empty
- [ ] Field_Label column present and not empty
- [ ] API_Name column present and not empty
- [ ] Type column present and valid field type

 **Field Naming**:
- [ ] API_Name contains only letters, numbers, underscores
- [ ] API_Name starts with letter
- [ ] API_Name length ≤ 40 characters (excluding `__c`)
- [ ] Field_Label length ≤ 40 characters

 **Type-Specific**:
- [ ] Text fields have Length column or default to 255
- [ ] Number/Currency/Percent fields have Precision and Scale
- [ ] MasterDetail fields reference valid parent object
- [ ] Formula fields have valid return type configured

 **Object Validation**:
- [ ] Custom objects end with `__c`
- [ ] Standard objects use exact API names
- [ ] Object names are consistent across rows

---

## Common CSV Errors and Fixes

### Error: "Missing required column"
**Fix**: Ensure CSV has Object, Field_Label, API_Name, Type, Notes columns

### Error: "Invalid field type"
**Fix**: Check Type column matches one of 28 valid field types (see list above)

### Error: "API_Name too long"
**Fix**: Shorten API_Name to 40 characters or less (excluding `__c` suffix)

### Error: "API_Name contains invalid characters"
**Fix**: Use only letters, numbers, and underscores; must start with letter

### Error: "Missing precision for Number field"
**Fix**: Add Precision and Scale columns for Number/Currency/Percent fields

### Error: "Missing length for Text field"
**Fix**: Add Length column for Text fields or let skill default to 255

---

## Source
- [Salesforce Field Name Limits](https://www.asagarwal.com/salesforce-api-name-character-limits-for-different-metadata-types/)
- [Metadata API CustomField](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
