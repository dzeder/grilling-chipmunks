# Show/Hide Slot Based on Dependency

Controls one slot's visibility based on the value of another slot on the same screen.

## When to Use

A config field should only appear when a specific condition is met — e.g. show an "API Key" field only when "Use custom endpoint" checkbox is checked, or show "Custom object name" only when "Object type" dropdown is set to "Custom".

## Key Concept

Custom JS on slot B receives events from ALL slots on the same screen. Listen for `CONFIG_SLOT_VALUE_CHANGED` on the controlling slot and return a new state with `status: 'HIDDEN'` or `status: 'VISIBLE'`.

## Complete Pattern

```javascript
const SLOT_ID = tray.env.slotExternalId;
const CONTROLLING_SLOT = 'external_CONTROLLING_SLOT_ID';

tray.on('CONFIG_SLOT_MOUNT', async ({ event, previousWizardState }) => {
  if (event.data.externalId !== SLOT_ID) return;

  const controlValue = previousWizardState.values[CONTROLLING_SLOT];
  const shouldShow = controlValue === 'TARGET_VALUE';

  if (!shouldShow) {
    return {
      status: 'HIDDEN',
      jsonSchema: { type: 'string' },
      value: undefined,
      validation: {}
    };
  }

  return {
    status: 'VISIBLE',
    jsonSchema: {
      type: 'string',
      title: 'DEPENDENT_FIELD_TITLE'
    },
    value: previousWizardState.values[SLOT_ID] || '',
    validation: {}
  };
});

tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, previousSlotState, previousWizardState }) => {
  // Listen for changes on the CONTROLLING slot
  if (event.data.externalId === CONTROLLING_SLOT) {
    const shouldShow = event.data.value === 'TARGET_VALUE';

    if (!shouldShow) {
      return {
        status: 'HIDDEN',
        jsonSchema: { type: 'string' },
        value: undefined,
        validation: {}
      };
    }

    return {
      status: 'VISIBLE',
      jsonSchema: {
        type: 'string',
        title: 'DEPENDENT_FIELD_TITLE'
      },
      value: previousWizardState.values[SLOT_ID] || '',
      validation: {}
    };
  }

  return;
});
```

## Variants

**Boolean checkbox control** — replace the condition:
```javascript
const shouldShow = Boolean(event.data.value);
// or: event.data.value === true
```

**Multiple trigger values** — show for any of several values:
```javascript
const showValues = ['custom', 'advanced', 'other'];
const shouldShow = showValues.includes(event.data.value);
```

**Multiple controlling slots** — listen for both:
```javascript
tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, previousSlotState, previousWizardState }) => {
  if (event.data.externalId === 'external_slot_a' || event.data.externalId === 'external_slot_b') {
    const valA = event.data.externalId === 'external_slot_a'
      ? event.data.value
      : previousWizardState.values['external_slot_a'];
    const valB = event.data.externalId === 'external_slot_b'
      ? event.data.value
      : previousWizardState.values['external_slot_b'];
    const shouldShow = valA === 'x' && valB === 'y';
    // ... return VISIBLE or HIDDEN
  }
  return;
});
```
