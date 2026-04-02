# Basic Text and Data Field Types

This reference covers 8 Salesforce field types for text and data storage.

## Field Types in This Category

1. **Text** - Single-line text up to 255 characters
2. **TextArea** - Multi-line text up to 255 characters
3. **LongTextArea** - Multi-line text up to 131,072 characters
4. **Html** - Rich text with HTML formatting up to 131,072 characters
5. **EncryptedText** - Encrypted text up to 175 characters
6. **Email** - Email address with validation
7. **Phone** - Phone number field
8. **Url** - URL with validation

---

## 1. Text

**Description**: Single-line text field, most common field type

**Metadata Properties**:
```javascript
{
  "Field": "Product_Name__c",
  "Object": "ohfy__Item__c",
  "Type": "Text",
  "Options": [
    { "key": "label", "value": "Product Name" },
    { "key": "type", "value": "Text" },
    { "key": "length", "value": "255" }          // Required: 1-255
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Text"
- `length` - Character limit (1-255)

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text shown to users
- `required` - true/false (default: false)
- `unique` - true/false (default: false)
- `externalId` - true/false (default: false)
- `defaultValue` - Default text value

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Length,Required,Unique
ohfy__Item__c,Product Name,Product_Name__c,Text,255,true,false
```

---

## 2. TextArea

**Description**: Multi-line text field up to 255 characters

**Metadata Properties**:
```javascript
{
  "Field": "Short_Description__c",
  "Object": "ohfy__Item__c",
  "Type": "TextArea",
  "Options": [
    { "key": "label", "value": "Short Description" },
    { "key": "type", "value": "TextArea" }
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "TextArea"

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false (default: false)
- `defaultValue` - Default text value

**Notes**:
- Always 255 characters (no length parameter)
- Displays as multi-line text box in UI
- No rich text formatting support

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required
ohfy__Item__c,Short Description,Short_Description__c,TextArea,false
```

---

## 3. LongTextArea

**Description**: Multi-line text field for extensive text up to 131,072 characters

**Metadata Properties**:
```javascript
{
  "Field": "Ingredients_and_Fermentation_Sources__c",
  "Object": "ohfy__Item__c",
  "Type": "LongTextArea",
  "Options": [
    { "key": "label", "value": "Ingredients and Fermentation Sources" },
    { "key": "type", "value": "LongTextArea" },
    { "key": "length", "value": "32768" },        // Required: 256-131,072
    { "key": "visibleLines", "value": 3 }         // Optional: default 3
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "LongTextArea"
- `length` - Character limit (256-131,072)

**Optional**:
- `visibleLines` - Number of visible lines in UI (default: 3)
- `description` - Field description
- `inlineHelpText` - Help text
- `defaultValue` - Default text value

**Notes**:
- Use for detailed descriptions, notes, or long-form content
- Not searchable in standard search (use Text for searchable content)
- No rich text formatting support

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Length,Notes
ohfy__Item__c,Ingredients and Fermentation Sources,Ingredients_and_Fermentation_Sources__c,LongTextArea,32768,Detailed ingredient list
```

---

## 4. Html

**Description**: Rich text field with HTML formatting up to 131,072 characters

**Metadata Properties**:
```javascript
{
  "Field": "Product_Details__c",
  "Object": "ohfy__Item__c",
  "Type": "Html",
  "Options": [
    { "key": "label", "value": "Product Details" },
    { "key": "type", "value": "Html" },
    { "key": "length", "value": "32768" },        // Required: 256-131,072
    { "key": "visibleLines", "value": 5 }         // Optional: default 5
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Html"
- `length` - Character limit (256-131,072)

**Optional**:
- `visibleLines` - Number of visible lines in UI (default: 5)
- `description` - Field description
- `inlineHelpText` - Help text

**Notes**:
- Supports rich text editor in UI (bold, italic, links, lists, etc.)
- Stores HTML markup
- Good for formatted product descriptions, announcements

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Length
ohfy__Item__c,Product Details,Product_Details__c,Html,32768
```

---

## 5. EncryptedText

**Description**: Encrypted text field masked in UI and encrypted at rest

**Metadata Properties**:
```javascript
{
  "Field": "API_Key__c",
  "Object": "Account",
  "Type": "EncryptedText",
  "Options": [
    { "key": "label", "value": "API Key" },
    { "key": "type", "value": "EncryptedText" },
    { "key": "length", "value": "175" },          // Required: 1-175
    { "key": "maskChar", "value": "asterisk" },   // Optional: asterisk or X
    { "key": "maskType", "value": "all" }         // Optional: all, lastFour, creditCard, etc.
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "EncryptedText"
- `length` - Character limit (1-175, shorter than Text due to encryption overhead)

**Optional**:
- `maskChar` - Masking character: "asterisk" (default) or "X"
- `maskType` - Masking pattern:
  - "all" - Mask entire value (default)
  - "lastFour" - Show last 4 characters
  - "creditCard" - Show last 4, mask others in groups of 4
  - "nino" - UK National Insurance Number pattern
  - "ssn" - US Social Security Number pattern
  - "sin" - Canadian Social Insurance Number pattern
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false

**Notes**:
- Use for sensitive data (API keys, tokens, credentials)
- Encrypted at rest using platform encryption
- Users with "View Encrypted Data" permission can see unmasked values
- Cannot be used as external ID or unique field

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Length,Notes
Account,API Key,API_Key__c,EncryptedText,175,Client API credential
```

---

## 6. Email

**Description**: Email address field with built-in validation

**Metadata Properties**:
```javascript
{
  "Field": "Support_Email__c",
  "Object": "Account",
  "Type": "Email",
  "Options": [
    { "key": "label", "value": "Support Email" },
    { "key": "type", "value": "Email" }
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Email"

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false
- `unique` - true/false
- `externalId` - true/false

**Notes**:
- Automatically validates email format (user@domain.com)
- UI displays as clickable mailto: link
- Use for email addresses that need validation

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required,Unique
Account,Support Email,Support_Email__c,Email,true,true
```

---

## 7. Phone

**Description**: Phone number field with flexible formatting

**Metadata Properties**:
```javascript
{
  "Field": "Support_Phone__c",
  "Object": "Account",
  "Type": "Phone",
  "Options": [
    { "key": "label", "value": "Support Phone" },
    { "key": "type", "value": "Phone" }
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Phone"

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false

**Notes**:
- Stores up to 40 characters
- No automatic formatting or validation (accepts any string)
- UI displays as clickable tel: link on mobile
- Use for phone numbers that need click-to-call functionality

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required
Account,Support Phone,Support_Phone__c,Phone,false
```

---

## 8. Url

**Description**: URL field with validation and clickable links

**Metadata Properties**:
```javascript
{
  "Field": "Website__c",
  "Object": "Account",
  "Type": "Url",
  "Options": [
    { "key": "label", "value": "Website" },
    { "key": "type", "value": "Url" }
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Url"

**Optional**:
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false
- `defaultValue` - Default URL value

**Notes**:
- Stores up to 255 characters
- Validates URL format (http:// or https:// prefix)
- UI displays as clickable hyperlink
- Use for web addresses, documentation links, external resources

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required,DefaultValue
Account,Website,Website__c,Url,false,https://example.com
```

---

## Common Patterns for Text Fields

### External ID Pattern
Any text field can be marked as External ID for upsert operations:
```javascript
{
  "Field": "Supplier_SKU__c",
  "Object": "ohfy__Item__c",
  "Type": "Text",
  "Options": [
    { "key": "label", "value": "Supplier SKU" },
    { "key": "type", "value": "Text" },
    { "key": "length", "value": "100" },
    { "key": "unique", "value": "true" },
    { "key": "externalId", "value": "true" }
  ]
}
```

### Required Field Pattern
Make field required for data quality:
```javascript
{
  "Options": [
    { "key": "label", "value": "Product Name" },
    { "key": "type", "value": "Text" },
    { "key": "length", "value": "255" },
    { "key": "required", "value": "true" }
  ]
}
```

### Unique Field Pattern
Prevent duplicate values:
```javascript
{
  "Options": [
    { "key": "label", "value": "Serial Number" },
    { "key": "type", "value": "Text" },
    { "key": "length", "value": "50" },
    { "key": "unique", "value": "true" }
  ]
}
```

---

## Source
- [CustomField - Metadata API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
- [Metadata Field Types](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_field_types.htm)
- [Custom Field Types - Salesforce Help](https://help.salesforce.com/s/articleView?id=platform.custom_field_types.htm)
