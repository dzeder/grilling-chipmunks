# Date and Time Field Types

This reference covers 3 Salesforce field types for date and time data.

## Field Types in This Category

1. **Date** - Calendar date without time component
2. **DateTime** - Calendar date with time component
3. **Time** - Time of day without date component

---

## 1. Date

**Description**: Calendar date field (no time component)

**Metadata Properties**:
```javascript
{
  "Field": "Retail_Start_Date__c",
  "Object": "ohfy__Item__c",
  "Type": "Date",
  "Options": [
    { "key": "label", "value": "Retail Start Date" },
    { "key": "type", "value": "Date" }
  ]
}
```

**Required**: `label`, `type`
**Optional**: `description`, `inlineHelpText`, `required`, `defaultValue`

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required
ohfy__Item__c,Retail Start Date,Retail_Start_Date__c,Date,false
```

---

## 2. DateTime

**Description**: Calendar date with time component (timezone-aware)

**Metadata Properties**:
```javascript
{
  "Field": "Last_Sync__c",
  "Object": "Integration_Log__c",
  "Type": "DateTime",
  "Options": [
    { "key": "label", "value": "Last Sync" },
    { "key": "type", "value": "DateTime" }
  ]
}
```

**Required**: `label`, `type`
**Optional**: `description`, `inlineHelpText`, `required`, `defaultValue`

**Notes**: Stores in UTC, displays in user's timezone

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required
Integration_Log__c,Last Sync,Last_Sync__c,DateTime,false
```

---

## 3. Time

**Description**: Time of day without date component

**Metadata Properties**:
```javascript
{
  "Field": "Store_Opening_Time__c",
  "Object": "Location__c",
  "Type": "Time",
  "Options": [
    { "key": "label", "value": "Store Opening Time" },
    { "key": "type", "value": "Time" }
  ]
}
```

**Required**: `label`, `type`
**Optional**: `description`, `inlineHelpText`, `required`, `defaultValue`

**Format**: HH:MM:SS.SSS (24-hour format)

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Required
Location__c,Store Opening Time,Store_Opening_Time__c,Time,false
```

---

## Source
[Metadata Field Types](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_field_types.htm)
