# Dynamic Dropdown via callConnector

Fetches data from a connector API using the end user's auth and renders as a dropdown select.

## When to Use

User wants a config slot that shows a dropdown populated from live data in a third-party service (e.g. list of Salesforce objects, Salesloft cadences, HubSpot lists, Slack channels).

## Requirements

- An auth slot on a previous screen with a known External ID
- The connector name, version, and operation to call
- Knowledge of the response shape to extract `text`/`value` pairs

## Complete Pattern

```javascript
const SLOT_ID = tray.env.slotExternalId;

tray.on('CONFIG_SLOT_MOUNT', async ({ event, previousSlotState, previousWizardState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  // Get auth ID from a previous wizard screen
  const authId = previousWizardState.values['external_SERVICE_authentication'];

  if (!authId) {
    return {
      status: 'VISIBLE',
      jsonSchema: { type: 'string', title: 'FIELD_TITLE' },
      value: '',
      validation: {
        status: 'ERROR',
        message: 'Please authenticate with SERVICE_NAME on the previous screen first.'
      }
    };
  }

  let options = [];
  try {
    const response = await tray.callConnector({
      connector: 'CONNECTOR_NAME',   // e.g. 'salesforce', 'salesloft', 'hubspot'
      version: 'VERSION',            // e.g. '8.7'
      operation: 'OPERATION_NAME',   // e.g. 'list_cadences', 'find_records'
      authId: authId,
      input: {}                      // operation-specific input object
    });

    // Adjust based on actual response shape
    const items = response.data || response.result || [];
    options = items.map(item => ({
      text: item.name || item.label || String(item.id),
      value: String(item.id)
    }));
  } catch (err) {
    console.log('callConnector failed:', err);
    return {
      status: 'VISIBLE',
      jsonSchema: { type: 'string', title: 'FIELD_TITLE' },
      value: '',
      validation: {
        status: 'ERROR',
        message: 'Failed to fetch data from SERVICE_NAME. Check your authentication.'
      }
    };
  }

  const schema = {
    type: 'string',
    title: 'FIELD_TITLE'
  };

  if (options.length > 0) {
    schema.enum = options.map(o => o.value);
    schema.enumNames = options.map(o => o.text);
  }

  // Restore saved value if present
  const savedValue = previousWizardState.values[SLOT_ID] || '';

  return {
    status: 'VISIBLE',
    jsonSchema: schema,
    value: savedValue,
    validation: {}
  };
});
```

## Customization Points

| Placeholder | Replace With |
|---|---|
| `external_SERVICE_authentication` | Auth slot External ID from a previous screen |
| `CONNECTOR_NAME` | Programmatic connector name (e.g. `salesforce`) |
| `VERSION` | Connector version (e.g. `8.7`) |
| `OPERATION_NAME` | Snake_case operation name (e.g. `find_records`) |
| `FIELD_TITLE` | Display label for the dropdown |
| `response.data` | Adjust path to match actual API response shape |

## Finding Connector Details

1. **Connector name:** In the workflow builder, the grey step title (e.g. `salesforce-1`) minus the `-1` suffix
2. **Version:** Show Advanced Settings at bottom of step input panel → `Connector Version` field
3. **Operation:** The operation name in the step input panel, converted to snake_case (e.g. `Find records` → `find_records`)
4. **Input shape:** Run the operation in a test workflow, inspect debug output for the Input JSON
