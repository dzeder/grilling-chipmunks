# Special and Advanced Field Types

This reference covers 2 special Salesforce field types for unique use cases.

## Field Types in This Category

1. **AutoNumber** - Auto-incrementing unique identifier
2. **Location** (Geolocation) - Geographic coordinates (latitude/longitude)

---

## 1. AutoNumber

**Description**: Auto-incrementing field generating unique sequential identifiers

**Metadata Properties**:
```javascript
// Note: AutoNumber is typically used for Object name fields, not custom fields
// For custom field AutoNumber:
{
  "Field": "Case_Number__c",
  "Object": "Custom_Case__c",
  "Type": "AutoNumber",
  "Options": [
    { "key": "label", "value": "Case Number" },
    { "key": "type", "value": "AutoNumber" },
    { "key": "displayFormat", "value": "CASE-{0000}" },              // Required: format with {0000}
    { "key": "startingNumber", "value": 1 }                          // Optional: starting value (default: 1)
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "AutoNumber"
- `displayFormat` - Format template with `{0000}` placeholder

**Optional**:
- `startingNumber` - Starting number (1-1,000,000,000, default: 1)
- `description` - Field description
- `inlineHelpText` - Help text
- `externalId` - Mark as external ID (true/false)

**Display Format**:
- Must include `{0000}` placeholder (can be any number of zeros)
- Can include prefix/suffix text
- Examples:
  - `{0000}` → "0001", "0002", ...
  - `CASE-{000}` → "CASE-001", "CASE-002", ...
  - `MND-{0000}` → "MND-0001", "MND-0002", ...
  - `{YYYY}-{MM}-{0000}` → "2025-01-0001", "2025-01-0002", ...

**Notes**:
- Read-only after creation (system-generated)
- Guaranteed unique within object
- Not editable by users or API
- Cannot convert to other field types
- Commonly used for:
  - Object name fields (e.g., Mandate Number, Case Number)
  - Custom reference numbers
  - Sequential identifiers

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Notes
Custom_Case__c,Case Number,Case_Number__c,AutoNumber,"Format: CASE-{0000}, Starting: 1"
```

**Common AutoNumber Patterns**:
```javascript
// Simple sequential
"displayFormat": "{0000}"                    // 0001, 0002, ...

// With prefix
"displayFormat": "MND-{0000}"                // MND-0001, MND-0002, ...

// With date
"displayFormat": "{YYYY}-{0000}"             // 2025-0001, 2025-0002, ...

// Complex format
"displayFormat": "CASE-{YYYY}{MM}-{0000}"    // CASE-202501-0001, ...
```

---

## 2. Location (Geolocation)

**Description**: Compound field storing latitude and longitude coordinates

**Metadata Properties**:
```javascript
{
  "Field": "Store_Location__c",
  "Object": "Location__c",
  "Type": "Location",
  "Options": [
    { "key": "label", "value": "Store Location" },
    { "key": "type", "value": "Location" },
    { "key": "displayLocationInDecimal", "value": "true" },          // Optional: true or false
    { "key": "scale", "value": 5 }                                   // Optional: decimal precision (0-8)
  ]
}
```

**Required**:
- `label` - Field label
- `type` - "Location"

**Optional**:
- `displayLocationInDecimal` - Display format:
  - `true` (default) - Decimal degrees (37.7749, -122.4194)
  - `false` - Degrees, minutes, seconds (37° 46' 30" N, 122° 25' 10" W)
- `scale` - Decimal precision for coordinates (0-8, default: 5)
- `description` - Field description
- `inlineHelpText` - Help text
- `required` - true/false

**Compound Field Structure**:
A Location field creates 3 sub-fields automatically:
- `{Field_Name}__Latitude__s` - Latitude value
- `{Field_Name}__Longitude__s` - Longitude value
- `{Field_Name}__c` - Compound field (both values)

**Example**:
```
Field Name: Store_Location__c
Creates:
  - Store_Location__Latitude__s
  - Store_Location__Longitude__s
  - Store_Location__c (compound)
```

**Scale Precision**:
```
scale: 0  → 37° N, 122° W                    // Degrees only
scale: 2  → 37.77° N, 122.42° W              // ~1.1 km precision
scale: 5  → 37.77490° N, 122.41940° W        // ~1.1 m precision (default)
scale: 8  → 37.77490000° N, 122.41940000° W  // ~1.1 mm precision
```

**Use Cases**:
- Store/warehouse locations
- Customer addresses with geocoding
- Service territory mapping
- Proximity searches
- Distance calculations

**SOQL Distance Queries**:
```sql
// Find stores within 10 miles of coordinates
SELECT Name, Store_Location__c
FROM Location__c
WHERE DISTANCE(Store_Location__c, GEOLOCATION(37.7749, -122.4194), 'mi') < 10
```

**Example CSV Row**:
```
Object,Field_Label,API_Name,Type,Scale,Notes
Location__c,Store Location,Store_Location__c,Location,5,"Geolocation field for mapping"
```

**Common Location Patterns**:
```javascript
// Default precision (1.1 m)
{
  "Field": "Warehouse_Location__c",
  "Type": "Location",
  "Options": [
    { "key": "scale", "value": 5 },
    { "key": "displayLocationInDecimal", "value": "true" }
  ]
}

// High precision (1.1 mm)
{
  "Field": "Equipment_Location__c",
  "Type": "Location",
  "Options": [
    { "key": "scale", "value": 8 },
    { "key": "displayLocationInDecimal", "value": "true" }
  ]
}

// DMS format (degrees, minutes, seconds)
{
  "Field": "Property_Location__c",
  "Type": "Location",
  "Options": [
    { "key": "scale", "value": 5 },
    { "key": "displayLocationInDecimal", "value": "false" }
  ]
}
```

---

## Special Field Comparison

| Feature | AutoNumber | Location |
|---------|------------|----------|
| **Purpose** | Unique sequential IDs | Geographic coordinates |
| **Editable** | No (system-generated) | Yes (user/API input) |
| **Unique** | Yes (within object) | No |
| **Indexable** | Yes | No |
| **Queryable** | Yes | Yes (DISTANCE/GEOLOCATION functions) |
| **Format** | Custom template | Lat/Long compound field |
| **Use Cases** | Reference numbers, IDs | Mapping, proximity searches |

---

## Source
- [CustomField - Metadata API](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/customfield.htm)
- [Geolocation Custom Field](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/compound_fields_geolocation.htm)
- [AutoNumber Fields](https://help.salesforce.com/s/articleView?id=sf.custom_field_attributes.htm)
