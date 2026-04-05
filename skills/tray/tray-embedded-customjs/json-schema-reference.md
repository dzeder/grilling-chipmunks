# JSON Schema Quick Reference

The `jsonSchema` property in slot state follows JSON Schema standard. The config wizard RJSF renderer translates schema types into form controls.

## Supported Types

### String (text input)
```json
{ "type": "string", "title": "Label" }
```

### String with default
```json
{ "type": "string", "title": "Label", "default": "fallback value" }
```

### Dropdown (static options)
```json
{
  "type": "string",
  "title": "Label",
  "enum": ["val1", "val2", "val3"],
  "enumNames": ["Display Name 1", "Display Name 2", "Display Name 3"]
}
```
`enum` = stored values. `enumNames` = display labels (same order). Both arrays must be same length.

### Boolean (checkbox)
```json
{ "type": "boolean", "title": "Enable feature", "default": false }
```

### Number
```json
{ "type": "number", "title": "Limit" }
```

### Array of strings
```json
{ "type": "array", "title": "Tags", "items": { "type": "string" } }
```
Renders as a list with an "Add" button. Each item is a simple text input.

### Array of objects (repeatable form group)
```json
{
  "type": "array",
  "title": "Mappings",
  "description": "Optional help text for the entire array",
  "items": {
    "type": "object",
    "title": "Mapping",
    "required": ["field_a", "field_b"],
    "additionalProperties": false,
    "properties": {
      "field_a": { "type": "string", "title": "Field A" },
      "field_b": { "type": "string", "title": "Field B" },
      "optional_field": { "type": "string", "title": "Optional" }
    }
  },
  "minItems": 0
}
```

**Critical rules for array-of-objects:**
- `additionalProperties: false` — suppresses "Add Property To Object" button
- Use `title` only on properties (not `description`) — avoids label duplication
- `title` on items object replaces raw index labels (0, 1, 2...)
- `required` array marks fields with a red asterisk
- `minItems: 0` allows empty arrays; `minItems: 1` forces at least one row

### Dropdown within array-of-objects
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "status": {
        "type": "string",
        "title": "Status",
        "enum": ["active", "paused"],
        "enumNames": ["Active", "Paused"]
      },
      "name": { "type": "string", "title": "Name" }
    }
  }
}
```

## Properties Reference

| Property | Effect |
|---|---|
| `type` | Controls rendered widget (`string`, `number`, `boolean`, `array`, `object`) |
| `title` | Field label displayed to user |
| `description` | Help text (avoid on properties inside objects — causes duplication) |
| `default` | Pre-filled value |
| `enum` | Array of valid values → renders as dropdown |
| `enumNames` | Display labels for enum values (same order) |
| `required` | Array of property names that must be filled (on object type) |
| `additionalProperties` | Set `false` on objects to prevent arbitrary property addition |
| `minItems` / `maxItems` | Min/max array length |
| `format` | Hints like `"email"` (may trigger browser-native validation — use sparingly) |
