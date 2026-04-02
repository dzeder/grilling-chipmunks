# Input Validation

Validates user input on a config slot and blocks wizard progression with error messages.

## When to Use

A config field needs client-side validation — e.g. email format, required fields, regex patterns, numeric ranges, URL format.

## Key Concept

Return `validation: { status: 'ERROR', message: '...' }` to block the "Next"/"Finish" button. Return `validation: {}` to clear the error and allow progression.

## Complete Pattern

```javascript
const SLOT_ID = tray.env.slotExternalId;

tray.on('CONFIG_SLOT_MOUNT', async ({ event, previousWizardState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  return {
    status: 'VISIBLE',
    jsonSchema: { type: 'string', title: 'FIELD_TITLE' },
    value: previousWizardState.values[SLOT_ID] || '',
    validation: {}
  };
});

tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, previousSlotState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  const value = event.data.value;
  const error = validate(value);

  return {
    ...previousSlotState,
    status: 'VISIBLE',
    value: value,
    validation: error ? { status: 'ERROR', message: error } : {}
  };
});

// --- Validation function (customize as needed) ---
function validate(value) {
  if (!value || value.trim() === '') {
    return 'This field is required.';
  }
  return null; // valid
}
```

## Common Validators

**Email:**
```javascript
function validate(value) {
  if (!value || value.trim() === '') return 'Email is required.';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(value)) return '"' + value + '" is not a valid email address.';
  return null;
}
```

**URL:**
```javascript
function validate(value) {
  if (!value || value.trim() === '') return 'URL is required.';
  try { new URL(value); return null; }
  catch { return '"' + value + '" is not a valid URL.'; }
}
```

**Numeric range:**
```javascript
function validate(value) {
  const num = Number(value);
  if (isNaN(num)) return 'Must be a number.';
  if (num < 1 || num > 1000) return 'Must be between 1 and 1000.';
  return null;
}
```

**Regex pattern:**
```javascript
function validate(value) {
  if (!value || value.trim() === '') return 'This field is required.';
  const pattern = /^[A-Z]{2}-\d{4}$/;
  if (!pattern.test(value)) return 'Must match format: XX-0000 (e.g. US-1234).';
  return null;
}
```

## Cross-Slot Validation

To validate slot A's value from Custom JS on slot B (both on the same screen):

```javascript
tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, previousSlotState, previousWizardState }) => {
  const VALIDATED_SLOT = 'external_OTHER_SLOT';

  if (event.data.externalId === VALIDATED_SLOT) {
    const error = validate(event.data.value);
    return {
      ...previousSlotState,
      validation: error ? { status: 'ERROR', message: error } : {}
    };
  }
  return;
});
```
