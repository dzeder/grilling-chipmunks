# Array of Objects (Repeatable Form Group)

Renders a dynamic list where users add/remove rows. Each row is a structured object with individual form fields per property.

## When to Use

User wants end users to configure a list of structured items — e.g. field mappings, cadence-to-campaign mappings, notification rules, key-value pairs with metadata.

## Critical Schema Rules

- **Always set `additionalProperties: false`** on the items object — without this, the wizard renders an unwanted "Add Property To Object" button
- **Use `title` only** on individual properties — adding `description` causes label duplication (label appears twice: once on the left, once on the right)
- **Set `title` on the items object** (e.g. `"Mapping"`) — this replaces the raw array index (0, 1, 2...) as the row label

## Complete Pattern

```javascript
const SLOT_ID = tray.env.slotExternalId;

const ITEMS_SCHEMA = {
  type: 'array',
  title: 'ARRAY_TITLE',
  description: 'ARRAY_DESCRIPTION',
  items: {
    type: 'object',
    title: 'ITEM_TITLE',
    required: ['REQUIRED_FIELD_1', 'REQUIRED_FIELD_2'],
    additionalProperties: false,
    properties: {
      FIELD_1: {
        type: 'string',
        title: 'Field 1 Label'
      },
      FIELD_2: {
        type: 'string',
        title: 'Field 2 Label'
      },
      OPTIONAL_FIELD: {
        type: 'string',
        title: 'Optional Field Label'
      }
    }
  },
  minItems: 0
};

const DEFAULT_VALUE = [
  { FIELD_1: '', FIELD_2: '', OPTIONAL_FIELD: '' }
];

tray.on('CONFIG_SLOT_MOUNT', async ({ event, previousSlotState, previousWizardState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  let existingValue = DEFAULT_VALUE;
  try {
    const raw = previousWizardState.values[SLOT_ID];
    if (raw) {
      const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
      if (Array.isArray(parsed) && parsed.length > 0) {
        existingValue = parsed;
      }
    }
  } catch (e) {
    existingValue = DEFAULT_VALUE;
  }

  return {
    status: 'VISIBLE',
    jsonSchema: ITEMS_SCHEMA,
    value: existingValue,
    validation: {}
  };
});

tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, previousSlotState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  const items = event.data.value;
  if (!Array.isArray(items)) return;

  // Validate required fields per row
  for (let i = 0; i < items.length; i++) {
    const item = items[i];

    if (!item.FIELD_1 || item.FIELD_1.trim() === '') {
      return {
        ...previousSlotState,
        status: 'VISIBLE',
        value: items,
        validation: {
          status: 'ERROR',
          message: 'Row ' + (i + 1) + ': FIELD_1_LABEL is required.'
        }
      };
    }

    if (!item.FIELD_2 || item.FIELD_2.trim() === '') {
      return {
        ...previousSlotState,
        status: 'VISIBLE',
        value: items,
        validation: {
          status: 'ERROR',
          message: 'Row ' + (i + 1) + ': FIELD_2_LABEL is required.'
        }
      };
    }
  }

  // Duplicate detection (optional — on a unique field)
  const uniqueValues = items.map(i => i.FIELD_1).filter(v => v && v.trim() !== '');
  const dupes = uniqueValues.filter((v, idx) => uniqueValues.indexOf(v) !== idx);
  if (dupes.length > 0) {
    return {
      ...previousSlotState,
      status: 'VISIBLE',
      value: items,
      validation: {
        status: 'ERROR',
        message: 'Duplicate value found: "' + dupes[0] + '".'
      }
    };
  }

  return {
    ...previousSlotState,
    status: 'VISIBLE',
    value: items,
    validation: {}
  };
});
```

## Workflow-Side Parsing

The config value arrives as a JSON string in the workflow. Parse it with a Script connector:

```javascript
exports.step = function(input) {
  const rawMappings = input.config_property_name;
  let mappings = [];
  try {
    mappings = JSON.parse(rawMappings);
  } catch (e) {
    mappings = [];
  }
  return { mappings: mappings };
};
```

Then use a Loop connector to iterate through `$.steps.script-1.result.mappings`.

## Variant: Dropdown Fields Within Array Items

To render a property as a dropdown instead of text input, use `enum`/`enumNames`:

```javascript
properties: {
  status: {
    type: 'string',
    title: 'Status',
    enum: ['active', 'paused', 'archived'],
    enumNames: ['Active', 'Paused', 'Archived']
  }
}
```

To populate dropdowns dynamically via `callConnector`, fetch the data in `CONFIG_SLOT_MOUNT` and build the `enum`/`enumNames` arrays before returning the schema. See `references/dynamic-dropdown.md` for the fetch pattern.
