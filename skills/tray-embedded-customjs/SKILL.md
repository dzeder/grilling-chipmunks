---
name: tray-embedded-customjs
description: "Generate production-ready Custom JavaScript code for Tray.ai Embedded solution config wizards. Use when the user wants to: create Custom JS for a Tray Embedded config slot, build dynamic dropdowns using callConnector, render array-of-objects forms via JSON Schema, show/hide slots based on dependencies, validate config slot input data, toggle config wizard screen visibility, customize data mapping with dynamic lookups, or any task involving Tray Embedded solution config wizard behavior controlled by JavaScript. Triggers include mentions of: Tray.ai Custom JS, config wizard customization, Embedded solution slots, callConnector, CONFIG_SLOT_MOUNT, CONFIG_SLOT_VALUE_CHANGED, Tray solution editor, config slot JSON Schema, partner__ CSS classes, or Tray Embedded advanced config wizard."
---

# Tray Embedded Custom JS Skill

Generate Custom JavaScript for Tray.ai Embedded solution config wizards. Custom JS controls slot behavior (rendering, validation, visibility, dynamic data) in the end-user config wizard.

## Workflow

1. **Gather requirements** using `AskUserTool` (see Intake Questions below)
2. **Read the relevant pattern** from `references/` based on the identified use case
3. **Generate code** following the architecture rules and the pattern
4. **Deliver** the Custom JS code with implementation instructions

## Intake Questions

Before generating any Custom JS, use `AskUserTool` to gather specifications. Ask in batches of 2-3 questions max per turn.

### Batch 1: Use Case

Ask the user:
- **What use case?** Options: dynamic dropdown, array-of-objects form, show/hide slot dependencies, input validation, data mapping customization, screen visibility toggle, authentication validation, other
- **Which slot?** What is the External ID of the config slot this Custom JS will be attached to? (must start with `external_`)

### Batch 2: Slot Details

Based on use case, ask:
- **For dynamic dropdown:** Which connector/version/operation? Is there an auth slot dependency? What is the auth slot External ID?
- **For array-of-objects:** What properties per object? Which are required? Any enum/dropdown fields within the object?
- **For show/hide:** Which slot controls visibility? What values trigger show vs hide? What is the dependent slot's External ID?
- **For validation:** What field is being validated? What validation rules (email, phone, regex, connector-based)?
- **For screen toggle:** Which screens should toggle? What controls the toggle (checkbox, dropdown value)?

### Batch 3: Dependencies & Details

- **Does this slot depend on values from other slots or auth slots on previous screens?** If so, what are their External IDs?
- **Should the slot start with a default value?** What should it be?
- **Any custom validation messages needed?**

## Use Case → Reference File

After identifying the use case, read the corresponding reference file before generating code:

- **Dynamic dropdown** (fetch options from API) → See [references/dynamic-dropdown.md](references/dynamic-dropdown.md)
- **Array of objects** (repeatable form rows with add/remove) → See [references/array-of-objects.md](references/array-of-objects.md)
- **Show/hide dependency** (toggle slot visibility based on another slot) → See [references/show-hide-dependency.md](references/show-hide-dependency.md)
- **Input validation** (email, regex, required field checks) → See [references/input-validation.md](references/input-validation.md)
- **Screen visibility toggle** (show/hide entire wizard screens) → See [references/screen-visibility.md](references/screen-visibility.md)
- **Connector-based validation** (verify data via API call) → See [references/connector-validation.md](references/connector-validation.md)
- **Dependent dropdown** (options change based on another slot's value) → See [references/dependent-dropdown.md](references/dependent-dropdown.md)
- **JSON Schema rendering** (quick reference for all schema types) → See [references/json-schema-reference.md](references/json-schema-reference.md)

For combined use cases (e.g. array-of-objects with dropdown fields populated via callConnector), read both relevant files.

## Architecture Rules

### The Tray JavaScript Class

All Custom JS interacts with slots through the `tray` object:

- **Events:** `tray.on(eventName, callback)` — listen to slot lifecycle events
- **Functions:** `tray.callConnector({...})` — invoke any Tray connector operation
- **Environment variables:** `tray.env.slotExternalId` — the current slot's External ID (plus any custom env vars defined in the editor)

### Events (5 total)

| Event | Fires When |
|---|---|
| `CONFIG_SLOT_MOUNT` | Config slot loads onto screen (status starts as `LOADING`) |
| `CONFIG_SLOT_VALUE_CHANGED` | Config slot value changes |
| `CONFIG_SLOT_STATUS_CHANGED` | Config slot status changes (e.g. `HIDDEN` → `VISIBLE`) |
| `AUTH_SLOT_MOUNT` | Auth slot loads onto screen |
| `AUTH_SLOT_VALUE_CHANGED` | Auth slot value changes (new authentication selected) |

Custom JS on slot B will hear events from ALL slots on the SAME screen. Always use `event.data.externalId` to filter.

### Event Callback Arguments

Every event callback receives `{ event, previousSlotState, previousWizardState }`:

**`event`** — type + data about the triggering slot:
```javascript
{
  "type": "CONFIG_SLOT_MOUNT",
  "data": {
    "externalId": "external_my_slot",
    "jsonSchema": { "type": "string" },
    "status": "LOADING"
  }
}
```

**`previousSlotState`** — current state of THIS slot (the one Custom JS is on):
```javascript
{
  "externalId": "external_my_slot",
  "jsonSchema": {},
  "status": "LOADING"
}
```

**`previousWizardState`** — state of the entire wizard across ALL screens:
```javascript
{
  "currentScreen": { "index": 1, "status": "VISIBLE" },
  "values": {
    "external_some_auth": "auth-uuid-here",
    "external_some_config": "user-entered-value"
  },
  "validation": {}
}
```

### Slot State (Return Value)

Return a new state object to modify the slot, or return nothing/undefined to keep current state:

```javascript
{
  status: 'VISIBLE',           // 'VISIBLE' | 'HIDDEN' | 'LOADING'
  jsonSchema: { type: 'string', title: 'My Field' },
  value: 'some value',         // any type matching the schema
  validation: {},              // {} = no error; { status: 'ERROR', message: '...' } = error
  className: 'my-custom-class' // optional CSS class
}
```

### callConnector

Invoke any Tray connector operation using the end user's auth. Returns a Promise. Input does NOT need JSON stringification (unlike the GraphQL API version).

```javascript
const result = await tray.callConnector({
  connector: 'salesforce',     // programmatic connector name
  version: '8.7',              // connector version string
  operation: 'find_records',   // snake_case operation name
  authId: previousWizardState.values['external_sf_auth'],
  input: { object: 'Lead', limit: 10 }
});
```

### Screen Visibility Toggle

```javascript
tray.emit("TOGGLE_SCREENS_VISIBILITY", [
  { screenId: solutionInfo.screens[2].id, isVisible: true },
  { screenId: solutionInfo.screens[3].id, isVisible: false }
]);
// Index 0 = "Not visible to users" screen, 1 = Screen 1, etc.
```

## Best Practices

1. **Always filter by slot ID:** `if (event.data.externalId !== tray.env.slotExternalId) return;` at the top of every handler (except when intentionally listening to another slot)
2. **Show LOADING for dependent slots:** When slot depends on another slot on the same screen, set status to `LOADING` first, then use `CONFIG_SLOT_STATUS_CHANGED` to execute fetch logic
3. **Use environment variables:** Define `slotExternalId` (set by default) and custom env vars in the editor's right panel to avoid hardcoding
4. **Spread previousSlotState:** When returning partial updates in `CONFIG_SLOT_VALUE_CHANGED`, spread `...previousSlotState` to preserve schema
5. **Handle missing auth gracefully:** Always check if `authId` exists before calling `callConnector`; show a descriptive error if missing
6. **Parse existing values on mount:** In `CONFIG_SLOT_MOUNT`, check `previousWizardState.values[SLOT_ID]` for saved data from a prior session; handle both string (JSON-serialized) and native types
7. **No external imports:** Custom JS runs in a sandboxed environment; only `tray` object and standard JS available

## Config Wizard CSS

Tray uses a closed set of `partner__` prefixed CSS classes. Do NOT invent class names.

Available classes: `partner__screen`, `partner__screen--first`, `partner__screen--last`, `partner__screen__header`, `partner__screen__header__title`, `partner__screen__header__description`, `partner__screen__items`, `partner__item__title`, `partner__item--auth`, `partner__item--config`, `partner__item--public-url`, `partner__message--error`, `partner__field__checkbox`, `partner__field__radio`, `partner__button--cancel`, `partner__button--previous`, `partner__button--finish`, `partner__button--next`, `partner__button--add`, `partner__footer`, `partner__footer__button-group`, `partner__footer__step-indicator`, `partner__footer__step-indicator__dot`, `partner__footer__step-indicator__dot--active`

CSS constraints:
- Only simple styling (colors, fonts, border-radius, borders) — layout changes may break
- Max 2 levels nesting; some properties need `!important`
- Global unless wrapped in `#partner__<solution_id> { ... }`
- Set Embedded ID in Account settings → Embedded settings first
- Edit CSS in Account settings → Customization → Edit & Preview
- Changes take up to 1 hour to propagate
