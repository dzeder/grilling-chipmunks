# Tray.io Project JSON Specification (UI Import Format)

Authoritative reference for generating Tray.io project exports that import successfully
through the Tray UI (Settings > Import/Export > Import Project).

**Sources of truth:** Real working exports from Daniel's Tray workspace, `workflow_test.json`
reference export, and 85+ production project exports from `dzeder/Integrations` repo.
Validated by successful Tray UI imports (2026-04-13).

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
  "projects": [ ... ],
  "data_tables": [],
  "vector_tables": [],
  "agents": [],
  "apim_operations": []
}
```

| Field | Type | Value |
|-------|------|-------|
| `tray_export_version` | number | Always `4` |
| `export_type` | string | `"project"` for multi-workflow, `"workflow"` for single |
| `workflows` | array | Array of workflow objects |
| `projects` | array | Array of project objects (links workflows together). `[]` for single-workflow exports |
| `data_tables` | array | Always `[]` (required for import on newer Tray versions) |
| `vector_tables` | array | Always `[]` (required for import) |
| `agents` | array | Always `[]` (required for import) |
| `apim_operations` | array | Always `[]` (required for import) |

Optional top-level keys (only for Embedded/OEM solutions):
- `solution` — Embedded solution configuration (screens, auth_slots, config_slots)

---

## Typed Values

**Every property value in `properties` objects must be type-wrapped.**

```json
{ "type": "string",   "value": "text" }
{ "type": "boolean",  "value": true }
{ "type": "number",   "value": 0 }
{ "type": "integer",  "value": 200 }
{ "type": "jsonpath", "value": "$.steps.salesforce-1.response.body.totalSize" }
{ "type": "array",    "value": [ ... ] }
{ "type": "object",   "value": { ... } }
{ "type": "null",     "value": null }
```

Bare/unwrapped values cause **"Exported structure validation failed"** on import.

**`integer` vs `number`:** Use `integer` for whole numbers like `status_code`, `interval`,
HTTP response codes. Use `number` for floating-point values. Both work for whole numbers
but `integer` is preferred when the value is semantically an integer.

### Array items are also typed

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

### Fallback values on jsonpath

JSONPath values can have an optional `fallback` that provides a default when the path
resolves to undefined:

```json
{
  "type": "jsonpath",
  "value": "$.steps.trigger.body.lineNumber",
  "fallback": {
    "value": 0,
    "type": "number"
  }
}
```

### Interpolation in string values

Embed JSONPath references inside strings with `{$.path}` syntax:

```json
{ "type": "string", "value": "{$.steps.trigger.result.customer} has been processed" }
```

### Formula expressions in string values

Inline calculations with `{=expression}` syntax:

```json
{ "type": "string", "value": "{=add($.steps.http-client-1.response.body.startAt, $.steps.http-client-1.response.body.maxResults)}" }
```

### Config values are BARE (not typed)

Inside `settings.config` and `projects[].config`, values are raw primitives -- NOT
wrapped in `{ type, value }` objects:

```json
"config": {
  "Seller_ID": "2318",
  "testRun": true,
  "maxResults": "50"
}
```

---

## Connector Versions (Current as of 2026-04-13)

### Core connectors (use these versions for new projects)

| Connector | Version | Notes |
|-----------|---------|-------|
| `salesforce` | `8.8` | Use for all SF operations |
| `ftp-client` | `6.1` | SFTP/FTP downloads. **NOT** `sftp` -- the connector name is `ftp-client` |
| `boolean-condition` | `2.3` | Conditional branching |
| `script` | `3.4` | JavaScript execution |
| `scheduled` | `3.5` | Scheduled triggers |
| `slack` | `11.0` | Slack messaging |
| `alerting-trigger` | `1.1` | Error workflow triggers |
| `loop` | `1.3` | Array iteration |
| `noop` | `1.1` | Manual trigger (for testing) |
| `call-workflow` | `2.0` | Call another workflow in the same project |
| `callable-trigger` | `2.0` | Receives calls from `call-workflow` |
| `callable-workflow-response` | `1.0` | Returns response from callable workflow |
| `storage` | `1.5` | Key-value storage |
| `http-client` | `5.6` | Generic HTTP requests (NOT for SFTP) |
| `csv` | `7.0` | CSV parsing/generation |
| `terminate` | `1.1` | Stop workflow execution |
| `break-loop` | `1.1` | Exit a loop early |

### Extended connector catalog (observed in production exports)

| Connector | Version | Notes |
|-----------|---------|-------|
| `aws-lambda` | `1.1` | |
| `aws-s3` | `2.3` | |
| `branch` | `1.3` | |
| `crypto-helpers` | `4.3` | HMAC, hashing |
| `data-tables` | `1.0` | Tray Data Tables |
| `date-time-helpers` | `3.0` | |
| `delay` | `1.0` | |
| `file-helpers` | `2.6` | |
| `form-trigger` | `1.7` | Form-based trigger |
| `graphql-client` | `1.1` | |
| `json-transformer` | `1.0` | |
| `json-web-token` | `1.0` | JWT operations |
| `list-helpers` | `3.1` | |
| `math-helpers` | `2.0` | |
| `mustache` | `1.1` | Template rendering |
| `object-helpers` | `4.1` | |
| `redshift` | `1.4` | Amazon Redshift |
| `salesforce-notification` | `3.1` | SF platform events |
| `send-email` | `4.1` | |
| `sheets` | `8.1` | Google Sheets |
| `text-helpers` | `3.0` | |
| `trigger-reply` | `1.1` | HTTP response from webhook |
| `webhook` | `2.3` | Webhook trigger |
| `zip` | `1.4` | |

**Always check a recent export if unsure.** Versions drift over time.

### INVALID connector names (will fail import)

- `sftp` -- use `ftp-client`
- `tray-io-workflow-trigger` -- use `callable-trigger` + `call-workflow`
- `manual` -- use `noop`

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
  "description": "Optional description",
  "enabled": true,
  "tags": [],
  "settings": {
    "config": {},
    "alerting_workflow_id": "uuid-v4",
    "input_schema": {},
    "output_schema": {}
  },
  "steps_structure": [ ... ],
  "steps": { ... },
  "legacy_error_handling": false,
  "dependencies": []
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | Yes | UUID v4, unique per workflow |
| `created` | string | Yes | ISO 8601 with microseconds and `Z` suffix |
| `workspace_id` | string | Yes | Daniel's: `c52d79bd-5882-4b67-9e35-67fac73b367f` |
| `project_id` | string | Yes | Must match the `id` in the `projects` array |
| `group` | string | Yes | Unique UUID per workflow |
| `creator` | string | Yes | Usually same as `workspace_id` |
| `version` | object | Yes | `{ id: "uuid", created: "iso-timestamp" }` |
| `title` | string | Yes | Human-readable workflow name |
| `description` | string | No | Optional description text |
| `enabled` | boolean | Yes | `true` or `false` |
| `tags` | array | Yes | Always `[]` |
| `settings` | object | Yes | See below |
| `steps_structure` | array | Yes | Ordered flow structure |
| `steps` | object | Yes | Map of step-name to step object |
| `legacy_error_handling` | boolean | Yes | Always `false` for new projects |
| `dependencies` | array | Yes | `[]` or array of `{ id, name }` for callable workflows |

### `settings` object

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `config` | object | Yes | Project config values (BARE values, not typed). Can be `{}` |
| `input_schema` | object | Yes | Usually `{}`. Populated for callable workflows with typed input |
| `output_schema` | object | Yes | Usually `{}`. Populated for callable workflows that return data |
| `alerting_workflow_id` | string | No | UUID of the error-handling workflow. Present when a workflow designates an alerting workflow |

### `dependencies` array (for workflows that call other workflows)

```json
"dependencies": [
  {
    "id": "6e6bd500-3550-4647-90c0-becaa68c1393",
    "name": "Phase 1 — Reference Data"
  }
]
```

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

### Branch (boolean condition with true/false)
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

### Branch (manual error handling with error/success)

When a step has `"error_handling": { "strategy": "manual" }`, it becomes a branch:

```json
{
  "name": "salesforce-1",
  "type": "branch",
  "content": {
    "error": [
      { "name": "slack-1", "type": "normal", "content": {} }
    ],
    "success": [
      { "name": "storage-1", "type": "normal", "content": {} }
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

### Break (exits a loop)
```json
{
  "name": "break-loop-1",
  "type": "break",
  "content": {},
  "target": "loop-1"
}
```

The `target` field names which loop to break out of. Only present on `"type": "break"`.

### Nesting

Loops can contain branches, branches can contain loops, and all can be nested arbitrarily:

```json
{
  "name": "loop-1",
  "type": "loop",
  "content": {
    "_loop": [
      {
        "name": "boolean-condition-1",
        "type": "branch",
        "content": {
          "true": [
            { "name": "break-loop-1", "type": "break", "content": {}, "target": "loop-1" }
          ],
          "false": []
        }
      }
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
    "description": "Optional description",
    "connector": {
      "name": "connector-name",
      "version": "X.Y"
    },
    "operation": "operation_name",
    "output_schema": {},
    "error_handling": {},
    "properties": { ... }
  }
}
```

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `title` | string | Yes | Human-readable step name |
| `description` | string | No | Optional description |
| `connector` | object | Yes | `{ name: string, version: string }` |
| `operation` | string | Yes | The operation identifier |
| `output_schema` | object | Yes | `{}` or JSON Schema (enables JSONPath autocomplete in UI) |
| `error_handling` | object | Yes | `{}` or strategy object (see Error Handling section) |
| `authentication` | object | No | **Do NOT include in generated JSON** (see below) |
| `properties` | object | Yes | Typed property values |

### Step naming convention

Steps are named as `{connector-name}-{incrementing-number}`:
- `salesforce-1`, `salesforce-2`, `salesforce-3`
- `script-1`, `script-2`
- `boolean-condition-1`, `boolean-condition-2`
- `loop-1`, `loop-2`
- `ftp-client-1`, `ftp-client-2`

The trigger step is always named `trigger` (no number suffix).

---

## Error Handling

The `error_handling` field on a step controls what happens when the step fails.

### Strategies

| Value | Behavior | steps_structure effect |
|-------|----------|----------------------|
| `{}` | Default: stop workflow on error | Step is `"type": "normal"` |
| `{ "strategy": "manual" }` | Step becomes a branch with `error`/`success` paths | Step is `"type": "branch"` with `error`/`success` content |
| `{ "strategy": "automatic" }` | Platform retries automatically | Step stays `"type": "normal"` |
| `{ "target": "loop-1", "strategy": "continueLoop" }` | On error, skip to next loop iteration | Step stays `"type": "normal"` |

### Alerting workflow pattern

Set `settings.alerting_workflow_id` on a workflow to point to another workflow in the
same project that uses `alerting-trigger`. When any step in the main workflow fails
unhandled, the alerting workflow fires automatically.

---

## Authentication Objects

**Do NOT include `authentication` in generated JSON.** Connector icons come from `connector.name`,
not from auth objects. Including placeholder auth forces Tray to prompt for credential configuration
on import. Omit `authentication` entirely -- user configures auth in Tray UI after import.

Auth objects only appear in **exports from Tray** (when credentials were already configured).
They are NOT required for import.

### Auth structure (for reference when reading existing exports)

```json
"authentication": {
  "group": "uuid-of-credential-group",
  "title": "The OZone",
  "service_icon": {
    "icon_type": "url",
    "value": "//s3.amazonaws.com/images.tray.io/artisan/icons/xxx.png"
  },
  "scopes": ["refresh_token", "full", "id", "api"],
  "service_name": "salesforce",
  "service_version": 1
}
```

### Connectors that NEVER have auth

`alerting-trigger`, `boolean-condition`, `branch`, `break-loop`, `call-workflow`,
`callable-trigger`, `callable-workflow-response`, `csv`, `data-tables`,
`date-time-helpers`, `delay`, `file-helpers`, `form-trigger`, `json-transformer`,
`list-helpers`, `loop`, `math-helpers`, `mustache`, `object-helpers`,
`send-email`, `terminate`, `trigger-reply`

### Daniel's Auth Groups (for reference)

| Service | Group UUID | Title |
|---------|-----------|-------|
| Salesforce (TBM Prod) | `1eab5959-014e-4978-ae7c-51c06f7368aa` | TBM PRODUCTION OHANAFY 2025-12-15 |
| Slack | `1759fea0-ad14-4529-a2aa-96842769e89a` | Daniel's Slack |

**After import, auth must be re-mapped to the target workspace's actual credentials.**

---

## Common Step Patterns

### Manual Trigger (noop)

```json
"trigger": {
  "title": "Manual Trigger",
  "connector": { "name": "noop", "version": "1.1" },
  "operation": "trigger",
  "output_schema": {},
  "error_handling": {},
  "properties": {}
}
```

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
    "hour": { "type": "string", "value": "6" },
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

### Scheduled Trigger (cron)

```json
"trigger": {
  "title": "Scheduled Trigger",
  "connector": { "name": "scheduled", "version": "3.5" },
  "operation": "cron",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "synchronous": { "type": "boolean", "value": true },
    "public_url": { "type": "jsonpath", "value": "$.env.public_url" },
    "schedule": { "type": "string", "value": "0 6,13,17 * * *" },
    "tz": { "type": "string", "value": "US/Eastern" }
  }
}
```

### Scheduled Trigger (interval)

```json
"trigger": {
  "title": "Scheduled Trigger",
  "connector": { "name": "scheduled", "version": "3.5" },
  "operation": "simple",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "synchronous": { "type": "boolean", "value": false },
    "public_url": { "type": "jsonpath", "value": "$.env.public_url" },
    "interval": { "type": "integer", "value": 1 },
    "time_unit": { "type": "string", "value": "months" },
    "start_date": { "type": "string", "value": "2024-11-01 04:00" }
  }
}
```

### Alerting Trigger (error workflow)

```json
"trigger": {
  "title": "Alert",
  "connector": { "name": "alerting-trigger", "version": "1.1" },
  "operation": "trigger",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "include_raw_response": { "type": "boolean", "value": true }
  }
}
```

Fires when any workflow in the project errors. Typically paired with a Slack step.

### Callable Trigger (sub-workflow)

```json
"trigger": {
  "title": "Callable Trigger",
  "connector": { "name": "callable-trigger", "version": "2.0" },
  "operation": "trigger_and_respond",
  "output_schema": {},
  "error_handling": {},
  "properties": {}
}
```

### Webhook Trigger

```json
"trigger": {
  "title": "Webhook",
  "connector": { "name": "webhook", "version": "2.3" },
  "operation": "webhook",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "allow_cors": { "type": "boolean", "value": true },
    "token": { "type": "jsonpath", "value": "$.auth.token" }
  }
}
```

### Salesforce SOQL Query (raw_http_request)

Use `raw_http_request`, NOT `find_records` or `query` for SOQL.

```json
"salesforce-1": {
  "title": "Query Records",
  "connector": { "name": "salesforce", "version": "8.8" },
  "operation": "raw_http_request",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "method": { "type": "string", "value": "GET" },
    "include_raw_body": { "type": "boolean", "value": false },
    "parse_response": { "type": "string", "value": "true" },
    "url": {
      "type": "object",
      "value": {
        "endpoint": { "type": "string", "value": "services/data/v62.0/query" }
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

### Salesforce Composite API POST

For batch record operations (used by VIP SRS scripts):

```json
"salesforce-2": {
  "title": "Composite Batch",
  "connector": { "name": "salesforce", "version": "8.8" },
  "operation": "raw_http_request",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "method": { "type": "string", "value": "POST" },
    "include_raw_body": { "type": "boolean", "value": false },
    "parse_response": { "type": "string", "value": "true" },
    "url": {
      "type": "object",
      "value": {
        "endpoint": { "type": "string", "value": "services/data/v62.0/composite" }
      }
    },
    "query_parameters": { "type": "array", "value": [] },
    "body": {
      "type": "object",
      "value": {
        "raw": {
          "type": "jsonpath",
          "value": "$.steps.loop-1.value"
        }
      }
    }
  }
}
```

### Salesforce Batch Update (batch_update_records)

```json
"salesforce-2": {
  "title": "Batch Update Records",
  "connector": { "name": "salesforce", "version": "8.8" },
  "operation": "batch_update_records",
  "output_schema": {},
  "error_handling": {},
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

### Loop

```json
"loop-1": {
  "title": "Loop Batches",
  "connector": { "name": "loop", "version": "1.3" },
  "operation": "loop_array",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "array": {
      "type": "jsonpath",
      "value": "$.steps.script-1.result.batches"
    }
  }
}
```

Inside a loop, access the current item via `$.steps.loop-1.value`.

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

### FTP/SFTP Download

```json
"ftp-client-1": {
  "title": "SFTP Download",
  "connector": { "name": "ftp-client", "version": "6.1" },
  "operation": "sftp_download",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "debug": { "type": "boolean", "value": false }
  }
}
```

Step naming convention: `ftp-client-1`, `ftp-client-2`, etc.
After import, configure the path and auth in the Tray UI.

### Slack Send Message

```json
"slack-1": {
  "title": "Send message",
  "connector": { "name": "slack", "version": "11.0" },
  "operation": "send_message",
  "output_schema": {},
  "error_handling": {},
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

### Call Workflow (sub-workflow invocation)

```json
"call-workflow-1": {
  "title": "Run Phase 1",
  "connector": { "name": "call-workflow", "version": "2.0" },
  "operation": "fire_and_wait_for_response",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "workflow_id": { "type": "string", "value": "uuid-of-callable-workflow" }
  }
}
```

The called workflow must use `callable-trigger` as its trigger. If it needs to return data,
it uses `callable-workflow-response` as its last step.

### Storage (key-value persistence)

```json
"storage-1": {
  "title": "Save Watermark",
  "connector": { "name": "storage", "version": "1.5" },
  "operation": "set",
  "output_schema": {},
  "error_handling": {},
  "properties": {
    "scope": { "type": "string", "value": "Current Workflow" },
    "key": { "type": "string", "value": "lastRunDate" },
    "value": { "type": "jsonpath", "value": "$.steps.script-1.result.runDate" }
  }
}
```

Scopes: `"Current Workflow"`, `"Current Project"`, `"Account"`

---

## Projects Array

Links workflows together into a named project:

```json
"projects": [
  {
    "id": "uuid-matching-project_id-in-workflows",
    "version": null,
    "name": "Project Name",
    "config": {},
    "workflows": ["workflow-uuid-1", "workflow-uuid-2"],
    "dependencies": [],
    "installation_source_id": null,
    "installation_version_id": null
  }
]
```

| Key | Type | Notes |
|-----|------|-------|
| `id` | string | Must match `project_id` in each workflow |
| `version` | string/null | `"1.0"` or `null` |
| `name` | string | Project display name |
| `config` | object | Project-level config (BARE values, not typed). Can be `{}` |
| `workflows` | array | Array of workflow UUID strings in order |
| `dependencies` | array | Always `[]` |
| `installation_source_id` | string/null | Always `null` for user-created projects |
| `installation_version_id` | string/null | Always `null` for user-created projects |

The `projects` array always contains exactly 1 project object for `export_type: "project"`,
and is `[]` for `export_type: "workflow"`.

---

## Standard Project Pattern: Main + Error Handler

Most Ohanafy integrations follow this two-workflow pattern:

**Workflow 1 (Main):** Scheduled trigger > query > condition > transform > update > notify
**Workflow 2 (Error):** Alerting trigger > Slack DM with error details and log URL

The error workflow Slack message should include:
- Workflow name + "Errored"
- Link to logs: `https://app.tray.io/workspaces/{ws_id}/projects/{proj_id}/workflows/{wf_id}/logs?steps={failing_step}`
- The word "errored" for Slack search

Set `settings.alerting_workflow_id` on the main workflow to point to the error workflow's UUID.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| API/sync format wrapper | Use flat format (no `projectId`/`exportData`) |
| Bare property values | Wrap every value as `{ "type": "...", "value": ... }` |
| `find_records` for SOQL | Use `raw_http_request` with GET to `services/data/v62.0/query` |
| `$.steps.sf.result.records` | Use `$.steps.sf.response.body.records` for raw_http_request |
| `{ Id, Field: val }` batch format | Use `{ object_id, fields: [{ key, value }] }` |
| Missing `body: { none: null }` | Required on GET raw_http_request |
| Missing `file_output: false` | Required on script steps |
| `"type": "trigger"` in steps_structure | Use `"type": "normal"` for trigger steps |
| `const`/`let` in scripts | Use `var` for Tray runtime compatibility |
| Wrong connector versions | Check table above; versions drift |
| `sftp` connector name | Use `ftp-client` -- `sftp` is NOT a valid connector name |
| `http-client` for SFTP | Use `ftp-client@6.1` with `sftp_download` operation |
| `tray-io-workflow-trigger` | NOT valid for import -- use `callable-trigger@2.0` + `call-workflow@2.0` |
| `salesforce@8.7` | Update to `8.8` (as of 2026-04) |
| Human-readable UUIDs | ALL IDs must be valid UUID v4 (use `crypto.randomUUID()`) |
| Missing top-level arrays | `data_tables`, `vector_tables`, `agents`, `apim_operations` are all required |
| Including `authentication` on steps | Do NOT include -- forces auth config prompt on import. Icons come from `connector.name` |
| Typed values in `config` | Config values are BARE primitives, not `{ type, value }` wrapped |
| `hour`/`minute` as numbers | Must be strings in scheduled trigger properties |
