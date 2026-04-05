# Dependent Dropdown

A dropdown whose options are fetched dynamically and change based on the value of another slot on the same screen.

## When to Use

One dropdown feeds into another — e.g. user selects "Account" or "Lead" in an object type dropdown, and a second dropdown populates with fields for that object type. Or user selects a workspace, and a channel dropdown loads channels for that workspace.

## Key Concept: The LOADING → STATUS_CHANGED Pattern

When slot B depends on slot A (both on the same screen):

1. Slot A value changes → Custom JS on slot B catches this in `CONFIG_SLOT_VALUE_CHANGED`
2. Slot B returns `status: 'LOADING'` (does NOT fetch yet)
3. This triggers `CONFIG_SLOT_STATUS_CHANGED` on slot B
4. In `CONFIG_SLOT_STATUS_CHANGED`, slot B fetches data and returns `status: 'VISIBLE'` with the new options

This two-step pattern is a Tray best practice to avoid race conditions.

## Complete Pattern

```javascript
const SLOT_ID = tray.env.slotExternalId;
const PARENT_SLOT = 'external_PARENT_SLOT_ID';

tray.on('CONFIG_SLOT_MOUNT', async ({ event, previousWizardState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  const parentValue = previousWizardState.values[PARENT_SLOT];

  // If parent has no value yet, stay in loading state
  if (!parentValue) {
    return {
      status: 'LOADING',
      jsonSchema: { type: 'string' },
      value: undefined,
      validation: {}
    };
  }

  // Parent already has a value (e.g. restoring a saved config) — fetch immediately
  return await fetchAndRender(parentValue, previousWizardState);
});

tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, previousSlotState, previousWizardState }) => {
  // When PARENT changes, trigger a re-fetch via LOADING
  if (event.data.externalId === PARENT_SLOT) {
    if (!event.data.value) {
      return {
        status: 'HIDDEN',
        jsonSchema: { type: 'string' },
        value: undefined,
        validation: {}
      };
    }

    // Step 1: Set to LOADING (triggers CONFIG_SLOT_STATUS_CHANGED)
    return {
      status: 'LOADING',
      jsonSchema: { type: 'string' },
      value: undefined,
      validation: {}
    };
  }

  return;
});

tray.on('CONFIG_SLOT_STATUS_CHANGED', async ({ event, previousWizardState }) => {
  if (event.data.externalId !== SLOT_ID) return;
  if (event.data.status !== 'LOADING') return;

  // Step 2: Now fetch the data
  const parentValue = previousWizardState.values[PARENT_SLOT];
  if (!parentValue) return;

  return await fetchAndRender(parentValue, previousWizardState);
});

async function fetchAndRender(parentValue, previousWizardState) {
  const authId = previousWizardState.values['external_SERVICE_authentication'];

  if (!authId) {
    return {
      status: 'VISIBLE',
      jsonSchema: { type: 'string', title: 'CHILD_FIELD_TITLE' },
      value: '',
      validation: {
        status: 'ERROR',
        message: 'Please authenticate on the previous screen first.'
      }
    };
  }

  try {
    const response = await tray.callConnector({
      connector: 'CONNECTOR_NAME',
      version: 'VERSION',
      operation: 'OPERATION_NAME',
      authId: authId,
      input: { PARENT_PARAM: parentValue }
    });

    const items = response.data || response.result || [];
    const options = items.map(item => ({
      text: item.name || String(item.id),
      value: String(item.id)
    }));

    const schema = { type: 'string', title: 'CHILD_FIELD_TITLE' };
    if (options.length > 0) {
      schema.enum = options.map(o => o.value);
      schema.enumNames = options.map(o => o.text);
    }

    return {
      status: 'VISIBLE',
      jsonSchema: schema,
      value: previousWizardState.values[SLOT_ID] || '',
      validation: {}
    };
  } catch (err) {
    return {
      status: 'VISIBLE',
      jsonSchema: { type: 'string', title: 'CHILD_FIELD_TITLE' },
      value: '',
      validation: {
        status: 'ERROR',
        message: 'Failed to load options. Check your authentication.'
      }
    };
  }
}
```

## Customization Points

| Placeholder | Replace With |
|---|---|
| `external_PARENT_SLOT_ID` | External ID of the controlling dropdown |
| `external_SERVICE_authentication` | Auth slot External ID |
| `PARENT_PARAM` | The input parameter name that takes the parent value |
| `CHILD_FIELD_TITLE` | Display label for this dependent dropdown |
