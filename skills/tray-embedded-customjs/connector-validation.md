# Connector-Based Validation

Uses `callConnector` to validate that user-provided data actually exists or is valid in the target service before allowing wizard progression.

## When to Use

User enters an ID, name, or value that must be verified against a live API — e.g. validate that a Salesforce record ID exists, a Slack channel name is real, or a custom object is accessible.

## Complete Pattern

```javascript
const SLOT_ID = tray.env.slotExternalId;

tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, previousSlotState, previousWizardState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  const valueToValidate = event.data.value;
  if (!valueToValidate || valueToValidate.trim() === '') {
    return {
      ...previousSlotState,
      value: valueToValidate,
      validation: { status: 'ERROR', message: 'This field is required.' }
    };
  }

  const authId = previousWizardState.values['external_SERVICE_authentication'];
  if (!authId) {
    return {
      ...previousSlotState,
      value: valueToValidate,
      validation: {
        status: 'ERROR',
        message: 'Please authenticate with SERVICE_NAME on the previous screen first.'
      }
    };
  }

  try {
    const response = await tray.callConnector({
      connector: 'CONNECTOR_NAME',
      version: 'VERSION',
      operation: 'VALIDATION_OPERATION',
      authId: authId,
      input: { PARAM: valueToValidate }
    });

    // Check response indicates the value is valid
    if (!response || !response.result) {
      return {
        ...previousSlotState,
        value: valueToValidate,
        validation: {
          status: 'ERROR',
          message: '"' + valueToValidate + '" was not found. Please check the value.'
        }
      };
    }

    return {
      ...previousSlotState,
      value: valueToValidate,
      validation: {}
    };
  } catch (err) {
    return {
      ...previousSlotState,
      value: valueToValidate,
      validation: {
        status: 'ERROR',
        message: 'Validation failed: ' + (err.message || 'Unknown error')
      }
    };
  }
});
```

## Notes

- API calls fire on every keystroke — consider adding a debounce or minimum length check:
  ```javascript
  if (valueToValidate.length < 3) return; // skip validation for partial input
  ```
- For expensive validations, consider validating only on `CONFIG_SLOT_MOUNT` (when the screen loads) or using a separate "Validate" button slot pattern
