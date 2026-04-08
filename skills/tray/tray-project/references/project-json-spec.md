# Tray.io Project JSON Specification (UI Import Format)

Authoritative reference for generating Tray.io project exports that import successfully
through the Tray UI (Settings > Import/Export > Import Project).

**Source of truth:** Real working export from Daniel's `TBM-Draft-Invoice-Item-Work-Around`
project, validated by successful Tray UI import (2026-04-07).

---

## CRITICAL: Two Export Formats Exist

| Format | Used By | Top-Level Structure |
|--------|---------|-------------------|
| **UI/Flat** | Tray UI export/import | `{ tray_export_version, export_type, workflows, projects }` |
| **API/Sync** | Tray API, sync tools | `{ projectId, version, exportData: { ... } }` |

**These are NOT interchangeable.** The dzeder/Integrations repo contains API/sync format.
The Tray UI import requires flat format. This spec covers **flat/UI format only**.

---

## Top-Level Structure

```json
{
  "tray_export_version": 4,
  "export_type": "project",
  "workflows": [ ... ],
  "projects": [ ... ]
}
```

| Field | Type | Value |
|-------|------|-------|
| `tray_export_version` | number | Always `4` |
| `export_type` | string | `"project"` for multi-workflow, `"workflow"` for single |
| `workflows` | array | Array of workflow objects |
| `projects` | array | Array of project objects (links workflows together) |

No other top-level fields. No `data_tables`, `vector_tables`, `agents`, `apim_operations`,
`solution`, or wrapper objects.

---

## Typed Values

**Every property value in `properties` objects must be type-wrapped.**

```json
{ "type": "string",   "value": "text" }
{ "type": "boolean",  "value": true }
{ "type": "number",   "value": 0 }
{ "type": "jsonpath", "value": "$.steps.salesforce-1.response.body.totalSize" }
{ "type": "array",    "value": [ ... ] }
{ "type": "object",   "value": { ... } }
{ "type": "null",     "value": null }
```

Bare/unwrapped values cause **"Exported structure validation failed"** on import.

Array items are also typed:
```json
{
  "type": "array",
  "value": [
    {
      "type": "object",
      "value": {
        "key": { "type": "string", "value": "q" },
        "value": { "type": "string", "value": "SELECT Id FROM Account" }
      }
    }
  ]
}
```

---

## Connector Versions (Current as of 2026-04)

| Connector | Version | Notes |
|-----------|---------|-------|
| `salesforce` | `8.7` | Use for all SF operations |
| `boolean-condition` | `2.3` | Conditional branching |
| `script` | `3.4` | JavaScript execution |
| `scheduled` | `3.5` | Scheduled triggers |
| `slack` | `11.0` | Slack messaging |
| `alerting-trigger` | `1.1` | Error workflow triggers |
| `loop` | `1.3` | Array iteration |
| `storage` | varies | Key-value storage |

**Always check a recent export if unsure.** Versions drift over time.

---

## Workflow Object

```json
{
  "id": "uuid-v4",
  "created": "2026-04-08T00:00:00.000000Z",
  "workspace_id": "uuid-v4",
  "project_id": "uuid-v4",
  "group": "uuid-v4",
  "creator": "uuid-v4",
  "version": {
    "id": "uuid-v4",
    "created": "2026-04-08T00:00:00.000000Z"
  },
  "title": "Workflow Name",
  "enabled": true,
  "tags": [],
  "settings": {
    "config": {},
    "input_schema": {},
    "output_schema": {}
  },
  "steps_structure": [ ... ],
  "steps": { ... },
  "legacy_error_handling": false,
  "dependencies": []
}
```

| Field | Notes |
|-------|-------|
| `project_id` | Must match the `id` in the `projects` array |
| `workspace_id` | Daniel's: `c52d79bd-5882-4b67-9e35-67fac73b367f` |
| `creator` | Usually same as `workspace_id` |
| `group` | Unique UUID per workflow |
| `legacy_error_handling` | Always `false` for new projects |
| `dependencies` | Always `[]` for standalone workflows |

---

## steps_structure

Defines execution flow. Each entry is one of:

### Normal step
```json
{ "name": "salesforce-1", "type": "normal", "content": {} }
```

### Trigger (also uses "normal" type)
```json
{ "name": "trigger", "type": "normal", "content": {} }
```

### Branch (boolean condition)
```json
{
  "name": "boolean-condition-1",
  "type": "branch",
  "content": {
    "true": [
      { "name": "script-1", "type": "normal", "content": {} }
    ],
    "false": [
      { "name": "slack-2", "type": "normal", "content": {} }
    ]
  }
}
```

### Loop
```json
{
  "name": "loop-1",
  "type": "loop",
  "content": {
    "_loop": [
      { "name": "salesforce-2", "type": "normal", "content": {} }
    ]
  }
}
```

**Every name in steps_structure must have a corresponding entry in the `steps` object.**

---

## Step Objects

Each step in the `steps` object follows this structure:

```json
{
  "step-name": {
    "title": "Human-Readable Title",
    "connector": {
      "name": "connector-name",
      "version": "X.Y"
    },
    "operation": "operation_name",
    "output_schema": {},
    "error_handling": {},
    "authentication": { ... },
    "properties": { ... }
  }
}
```

`output_schema` can be `{}` (empty) or a JSON Schema describing the step's output.
Populated output schemas enable JSONPath autocomplete in the Tray UI but are optional.

`error_handling` is `{}` for default behavior.

---

## Authentication Objects

Every step that connects to an external service needs an inline `authentication` object:

```json
"authentication": {
  "group": "uuid-of-auth-credential",
  "title": "Human-readable credential name",
  "service_icon": {
    "icon_type": "url",
    "value": "https://s3.amazonaws.com/images.tray.io/artisan/icons/{icon-uuid}.png"
  },
  "scopes": ["full", "refresh_token"],
  "service_name": "salesforce",
  "service_version": 1
}
```

### Daniel's Auth Groups

| Service | Group UUID | Title |
|---------|-----------|-------|
| Salesforce (TBM Prod) | `1eab5959-014e-4978-ae7c-51c06f7368aa` | TBM PRODUCTION OHANAFY 2025-12-15 |
| Slack | `1759fea0-ad14-4529-a2aa-96842769e89a` | Daniel's Slack |

### Service Icons

| Service | Icon URL |
|---------|----------|
| Salesforce | `https://s3.amazonaws.com/images.tray.io/artisan/icons/dd966f42-81e8-4770-a3d8-d095ca41ab45.png` |
| Slack | `https://s3.amazonaws.com/images.tray.io/artisan/icons/6632c308-2cd1-4f68-8128-e521e552a66b.png` |

### Scopes by Service

**Salesforce:** `["full", "refresh_token"]`, `service_version: 1`

**Slack (37 scopes):**
```json
["reminders:read", "links:write", "users:read.email", "pins:read", "team:read",
 "channels:write.topic", "reminders:write", "calls:read", "commands",
 "reactions:write", "users:read", "groups:write", "mpim:history", "pins:write",
 "mpim:write", "mpim:read", "users:write", "channels:manage", "emoji:read",
 "im:read", "usergroups:read", "dnd:read", "channels:read", "reactions:read",
 "im:history", "users.profile:read", "im:write", "files:write", "links:read",
 "files:read", "chat:write", "groups:history", "channels:history",
 "usergroups:write", "groups:read", "channels:write.invites"]
```
`service_version: 5`

**After import, auth must be re-mapped to the target workspace's actual credentials.**

---

## Common Step Patterns

### Scheduled Trigger (daily)

```json
"trigger": {
  "title": "Scheduled Trigger",
  "connector": { "name": "scheduled", "version": "3.5" },
  "operation": "daily",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "synchronous": { "type": "boolean", "value": false },
    "public_url": { "type": "jsonpath", "value": "$.env.public_url" },
    "hour": { "type": "string", "value": "19" },
    "minute": { "type": "string", "value": "0" },
    "day_of_week": {
      "type": "object",
      "value": {
        "monday":    { "type": "boolean", "value": true },
        "tuesday":   { "type": "boolean", "value": true },
        "wednesday": { "type": "boolean", "value": true },
        "thursday":  { "type": "boolean", "value": true },
        "friday":    { "type": "boolean", "value": true },
        "saturday":  { "type": "boolean", "value": true },
        "sunday":    { "type": "boolean", "value": true }
      }
    },
    "tz": { "type": "string", "value": "EST5EDT" }
  }
}
```

**`hour` and `minute` are strings, not numbers.** All 7 day_of_week booleans required.

### Alerting Trigger (error workflow)

```json
"trigger": {
  "title": "Alert",
  "connector": { "name": "alerting-trigger", "version": "1.1" },
  "operation": "trigger",
  "output_schema": {},
  "error_handling": {},
  "properties": {}
}
```

Fires when any workflow in the project errors. Typically paired with a single Slack step.

### Salesforce SOQL Query (raw_http_request)

Use `raw_http_request`, NOT `find_records` or `query`.

```json
"salesforce-1": {
  "title": "Query Records",
  "connector": { "name": "salesforce", "version": "8.7" },
  "operation": "raw_http_request",
  "output_schema": {},
  "error_handling": {},
  "authentication": { ... },
  "properties": {
    "method": { "type": "string", "value": "GET" },
    "include_raw_body": { "type": "boolean", "value": false },
    "parse_response": { "type": "string", "value": "true" },
    "url": {
      "type": "object",
      "value": {
        "endpoint": { "type": "string", "value": "services/data/v60.0/query" }
      }
    },
    "query_parameters": {
      "type": "array",
      "value": [
        {
          "type": "object",
          "value": {
            "key": { "type": "string", "value": "q" },
            "value": { "type": "string", "value": "SELECT Id FROM Account WHERE ..." }
          }
        }
      ]
    },
    "body": {
      "type": "object",
      "value": {
        "none": { "type": "null", "value": null }
      }
    }
  }
}
```

**Result paths:**
- Records: `$.steps.salesforce-1.response.body.records`
- Count: `$.steps.salesforce-1.response.body.totalSize`
- Done flag: `$.steps.salesforce-1.response.body.done`

### Salesforce Batch Update

```json
"salesforce-2": {
  "title": "Batch Update Records",
  "connector": { "name": "salesforce", "version": "8.7" },
  "operation": "batch_update_records",
  "output_schema": {},
  "error_handling": {},
  "authentication": { ... },
  "properties": {
    "object": { "type": "string", "value": "ohfy__Order_Item__c" },
    "error_handling": { "type": "string", "value": "rollback_fail" },
    "batch_update_list": {
      "type": "jsonpath",
      "value": "$.steps.script-1.result[0].batch_update_list"
    }
  }
}
```

**batch_update_list item format:**
```json
{
  "object_id": "001xx000003abc",
  "fields": [
    { "key": "Field__c", "value": false },
    { "key": "Status__c", "value": "Processed" }
  ]
}
```

NOT `{ Id: "...", Field__c: false }`. The `{ object_id, fields: [{ key, value }] }` shape
is required by the Tray Salesforce connector.

**Result check:** `$.steps.salesforce-2.hasErrors` (boolean) for success/failure branching.

### Boolean Condition

```json
"boolean-condition-1": {
  "title": "Has Results?",
  "connector": { "name": "boolean-condition", "version": "2.3" },
  "operation": "boolean_condition",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "conditions": {
      "type": "array",
      "value": [
        {
          "type": "object",
          "value": {
            "value1": { "type": "jsonpath", "value": "$.steps.salesforce-1.response.body.totalSize" },
            "comparison_type": { "type": "string", "value": ">" },
            "value2": { "type": "number", "value": 0 }
          }
        }
      ]
    },
    "strictness": { "type": "string", "value": "All" }
  }
}
```

Comparison types: `">"`, `"<"`, `"==="`, `"!=="`, `">="`, `"<="`, `"contains"`, `"does_not_contain"`

### Script Step

```json
"script-1": {
  "title": "Transform Data",
  "connector": { "name": "script", "version": "3.4" },
  "operation": "execute",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "variables": {
      "type": "array",
      "value": [
        {
          "type": "object",
          "value": {
            "name": { "type": "string", "value": "data" },
            "value": { "type": "jsonpath", "value": "$.steps.salesforce-1.response.body.records" }
          }
        }
      ]
    },
    "script": {
      "type": "string",
      "value": "exports.step = function(input, fileInput) {\n  var records = input.data;\n  // transform...\n  return result;\n};"
    },
    "file_output": { "type": "boolean", "value": false }
  }
}
```

**Key details:**
- Data is passed via `variables` array, NOT direct input
- Each variable has `name` (accessed as `input.name`) and `value` (jsonpath)
- `file_output` must be present and `false` unless generating files
- Function signature: `exports.step = function(input, fileInput)`
- Use `var` not `const`/`let` for Tray script runtime compatibility
- Result accessed via `$.steps.script-1.result` (or `$.steps.script-1.result[0]` for arrays)

### Slack Send Message

```json
"slack-1": {
  "title": "Send message",
  "connector": { "name": "slack", "version": "11.0" },
  "operation": "send_message",
  "output_schema": {},
  "error_handling": {},
  "authentication": { ... },
  "properties": {
    "use_user_token": { "type": "boolean", "value": false },
    "username": { "type": "string", "value": "Tray.io" },
    "parse": { "type": "string", "value": "none" },
    "link_names": { "type": "boolean", "value": false },
    "reply_broadcast": { "type": "boolean", "value": false },
    "channel": { "type": "string", "value": "U05UL218VA5" },
    "text": { "type": "string", "value": "Message text here" }
  }
}
```

For DMs, `channel` is the Slack user ID (e.g., `U05UL218VA5` for Daniel).
All 5 boolean/string properties (`use_user_token`, `username`, `parse`, `link_names`,
`reply_broadcast`) should be included.

---

## Projects Array

Links workflows together into a named project:

```json
"projects": [
  {
    "id": "uuid-matching-project_id-in-workflows",
    "version": null,
    "parent_project_id": null,
    "type": null,
    "name": "Project Name",
    "config": {},
    "workflows": ["workflow-uuid-1", "workflow-uuid-2"],
    "dependencies": [],
    "installation_source_id": null,
    "installation_version_id": null,
    "installation_guide": null
  }
]
```

The `id` here must match `project_id` in each workflow object.
The `workflows` array contains the `id` of each workflow in order.

---

## Standard Project Pattern: Main + Error Handler

Most Ohanafy integrations follow this two-workflow pattern:

**Workflow 1 (Main):** Scheduled trigger > query > condition > transform > update > notify
**Workflow 2 (Error):** Alerting trigger > Slack DM with error details and log URL

The error workflow Slack message should include:
- Workflow name + "Errored"
- Link to logs: `https://app.tray.io/workspaces/{ws_id}/projects/{proj_id}/workflows/{wf_id}/logs?steps={failing_step}`
- The word "errored" for Slack search

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| API/sync format wrapper | Use flat format (no `projectId`/`exportData`) |
| Bare property values | Wrap every value as `{ "type": "...", "value": ... }` |
| `find_records` for SOQL | Use `raw_http_request` with GET to `services/data/v60.0/query` |
| `cron` scheduled operation | Use `daily` with typed day_of_week object |
| `$.steps.sf.result.records` | Use `$.steps.sf.response.body.records` for raw_http_request |
| `{ Id, Field: val }` batch format | Use `{ object_id, fields: [{ key, value }] }` |
| Missing `body: { none: null }` | Required on GET raw_http_request |
| Missing `file_output: false` | Required on script steps |
| `"type": "trigger"` in steps_structure | Use `"type": "normal"` for trigger steps |
| `const`/`let` in scripts | Use `var` for Tray runtime compatibility |
| Wrong connector versions | Check table above; versions drift |
