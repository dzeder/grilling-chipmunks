# Screen Visibility Toggle

Toggle entire wizard screens on or off based on checkbox or dropdown values.

## When to Use

The config wizard has optional screens that should only appear when the user opts in — e.g. "Enable advanced settings" checkbox shows Screen 3, or a "Integration type" dropdown shows different screens per selection.

## Key Concept

Use `tray.emit("TOGGLE_SCREENS_VISIBILITY", [...])` to show/hide screens. Screen IDs come from `solutionInfo.screens[index].id`.

**Screen index mapping:**
- `solutionInfo.screens[0].id` = "Not visible to users" screen (hidden configs)
- `solutionInfo.screens[1].id` = Screen 1
- `solutionInfo.screens[2].id` = Screen 2
- etc.

## Complete Pattern

```javascript
const SLOT_ID = tray.env.slotExternalId;

tray.on('CONFIG_SLOT_MOUNT', async ({ event, previousWizardState, solutionInfo }) => {
  if (event.data.externalId !== SLOT_ID) return;

  // Set initial screen visibility based on saved values
  tray.emit("TOGGLE_SCREENS_VISIBILITY", [
    {
      screenId: solutionInfo.screens[2].id,
      isVisible: Boolean(previousWizardState.values['external_enable_advanced'])
    },
    {
      screenId: solutionInfo.screens[3].id,
      isVisible: Boolean(previousWizardState.values['external_enable_notifications'])
    }
  ]);

  return {
    status: 'VISIBLE',
    jsonSchema: event.data.jsonSchema,
    value: event.data.value,
    validation: {}
  };
});

tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, solutionInfo }) => {
  if (event.data.externalId === 'external_enable_advanced') {
    tray.emit("TOGGLE_SCREENS_VISIBILITY", [
      { screenId: solutionInfo.screens[2].id, isVisible: Boolean(event.data.value) }
    ]);
  }

  if (event.data.externalId === 'external_enable_notifications') {
    tray.emit("TOGGLE_SCREENS_VISIBILITY", [
      { screenId: solutionInfo.screens[3].id, isVisible: Boolean(event.data.value) }
    ]);
  }

  return;
});
```

## Variant: Dropdown-Driven Screen Selection

Show different screens depending on a dropdown value:

```javascript
tray.on('CONFIG_SLOT_VALUE_CHANGED', async ({ event, solutionInfo }) => {
  if (event.data.externalId === 'external_integration_type') {
    const val = event.data.value;
    tray.emit("TOGGLE_SCREENS_VISIBILITY", [
      { screenId: solutionInfo.screens[2].id, isVisible: val === 'salesforce' },
      { screenId: solutionInfo.screens[3].id, isVisible: val === 'hubspot' },
      { screenId: solutionInfo.screens[4].id, isVisible: val === 'custom_api' }
    ]);
  }
  return;
});
```
