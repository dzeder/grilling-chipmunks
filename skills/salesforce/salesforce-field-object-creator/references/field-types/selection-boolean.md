# Selection and Boolean Field Types

This reference covers 3 Salesforce field types for selections and boolean values.

## Field Types in This Category

1. **Checkbox** - Boolean true/false field
2. **Picklist** - Single-select dropdown list
3. **MultiselectPicklist** - Multi-select dropdown list

---

## 1. Checkbox

**Description**: Boolean field for true/false values

**Metadata Properties**:
```javascript
{
  "Field": "Active__c",
  "Object": "Product__c",
  "Type": "Checkbox",
  "Options": [
    { "key": "label", "value": "Active" },
    { "key": "type", "value": "Checkbox" },
    { "key": "defaultValue", "value": "false" }      // Optional: true or false
  ]
}
```

**Required**: `label`, `type`
**Optional**: `defaultValue` (true/false), `description`, `inlineHelpText`

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,DefaultValue
Product__c,Active,Active__c,Checkbox,true
```

---

## 2. Picklist

**Description**: Single-select dropdown with predefined values

**Metadata Properties**:
```javascript
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
    "sorted": true,                                   // Alphabetically sort values in UI
    "value": [
      { "full_name": "BOTTLE", "default": false, "label": "BOTTLE" },
      { "full_name": "CAN", "default": false, "label": "CAN" },
      { "full_name": "KEG", "default": true, "label": "KEG" }    // default: true for default value
    ],
    "value_set_parameters": [
      { "key": "restricted", "value": "true" }        // true = restrict to list, false = allow custom
    ]
  }
}
```

**Required**: `label`, `type`, `value_set` with `value` array
**Optional**: `description`, `inlineHelpText`, `required`

**Value Set Properties**:
- `sorted` - Alphabetically sort values (true/false)
- `value` - Array of picklist values
  - `full_name` - API name of value
  - `label` - Display label
  - `default` - Is default value (true/false, only one can be true)
- `value_set_parameters` - Array with `restricted` setting
  - `restricted: true` - Users can only select from list
  - `restricted: false` - Users can enter custom values

**Interactive Setup Required**: Skill will prompt for picklist values

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required,Notes
ohfy__Item__c,Container Type,Container_Type__c,Picklist,false,"Interactive: Enter values BOTTLE, CAN, KEG"
```

---

## 3. MultiselectPicklist

**Description**: Multi-select dropdown allowing multiple values

**Metadata Properties**:
```javascript
{
  "Field": "Distribution_Channels__c",
  "Object": "Product__c",
  "Type": "MultiselectPicklist",
  "Options": [
    { "key": "label", "value": "Distribution Channels" },
    { "key": "type", "value": "MultiselectPicklist" },
    { "key": "visibleLines", "value": 4 }            // Optional: lines shown in UI (default: 4)
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

**Required**: `label`, `type`, `value_set` with `value` array
**Optional**: `visibleLines`, `description`, `inlineHelpText`

**Notes**:
- Values stored as semicolon-separated string: "Retail;Online"
- Maximum 100 values in list
- Maximum 4,096 characters for selected values combined

**Interactive Setup Required**: Skill will prompt for picklist values

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Product__c,Distribution Channels,Distribution_Channels__c,MultiselectPicklist,"Interactive: Enter channel list"
```

---

## Controlling and Dependent Picklists

**Controlling Picklist**: Parent picklist that filters dependent picklist values
**Dependent Picklist**: Child picklist filtered by controlling picklist value

### Example: State filters City
```javascript
// Controlling Picklist (State)
{
  "Field": "State__c",
  "Object": "Location__c",
  "Type": "Picklist",
  "value_set": {
    "value": [
      { "full_name": "CA", "label": "California" },
      { "full_name": "NY", "label": "New York" }
    ]
  }
}

// Dependent Picklist (City)
{
  "Field": "City__c",
  "Object": "Location__c",
  "Type": "Picklist",
  "Options": [
    { "key": "controllingField", "value": "State__c" }    // References controlling field
  ],
  "value_set": {
    // Dependency mapping defined via interactive prompts
  }
}
```

**Interactive Setup**: Skill will prompt for:
- Controlling field name
- Dependent value mappings (which cities show for which states)

---

## Source
- [Metadata Field Types](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_field_types.htm)
- [Picklist Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_picklist.htm)
