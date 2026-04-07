# Tray.io Expert Guide

> The authoritative reference for all Tray.io work in the Ohanafy monorepo.
> **Read this before answering any Tray question.** Do not guess when this guide has the answer.

---

## Table of Contents

1. [Platform Architecture](#1-platform-architecture)
2. [Key Concepts](#2-key-concepts)
3. [Workflow Building](#3-workflow-building)
4. [Connector Reference](#4-connector-reference)
5. [Authentication Patterns](#5-authentication-patterns)
6. [Script Connector Patterns](#6-script-connector-patterns)
7. [Tray Embedded (OEM)](#7-tray-embedded-oem)
8. [Error Handling](#8-error-handling)
9. [Billing & Task Credits](#9-billing--task-credits)
10. [Security](#10-security)
11. [Lifecycle Management](#11-lifecycle-management)
12. [Ohanafy Integration Patterns](#12-ohanafy-integration-patterns)
13. [Connector Operations Quick Reference](#13-connector-operations-quick-reference)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Platform Architecture

Tray.io is the **Universal Automation Cloud** — an iPaaS that lets you build low-code automations and templatize them as integrations for end users.

### Hierarchy

```
Organization
  └── Workspace (dev, prod, department)
        └── Project (groups workflows for one purpose)
              └── Workflow (sequence of connector steps)
                    └── Step (single connector operation)
```

**Organization** — Top-level account. Manages billing, users, security policies, and audit logging across all workspaces. Billing is aggregated across all regions and workspaces.

**Workspace** — Organizational subdivision by department, team, or environment. Each workspace has its own authentications, projects, and usage limits. Users can only access auths in their assigned workspace. Use separate workspaces for dev vs. prod.

**Project** — A collection of workflows that together accomplish a specific integration goal. Projects are the unit of export/import for environment promotion. They can be converted into Solutions for end-user distribution.

**Workflow** — A sequence of steps built on a canvas. Workflows start with a trigger and execute steps in order, with branching and looping. Each workflow has its own logs, settings, and error handling configuration.

**Step** — A single operation from a connector. Each step takes inputs (from previous steps, config, or hardcoded values) and produces outputs accessible via JSONPath.

### Data Flow Between Steps

Data flows through **JSONPath references**:

```
$.steps.trigger.result.body.records[0].Name
$.steps.salesforce-1.result.body.id
$.config.batchSize
$.auth.access_token
$.env.workflow_uuid
```

**Key JSONPath patterns:**
- `$.steps.<step-name>.<response-path>` — Output from a previous step
- `$.config.<key>` — Project-level config variable
- `$.auth.<field>` — Authentication credential field
- `$.env.<var>` — Environment variable (workflow_uuid, execution_log_url)
- `$.steps.<loop-name>.value.<field>` — Current iteration value in a loop

### Execution Model

1. **Trigger fires** → Tray creates an execution
2. **Steps execute sequentially** (unless inside parallel loops)
3. Each step **consumes 1 task** (billing unit)
4. Step outputs are available to all subsequent steps via JSONPath
5. **Error handling** per step: stop workflow, continue, or route to error branch
6. **Logs** capture inputs/outputs for every step execution

---

## 2. Key Concepts

### Triggers (Workflow Initiators)

| Trigger | When to Use | Notes |
|---------|-------------|-------|
| **Webhook** | Real-time events from external systems | UUID-based URL, validate with HMAC/CSRF |
| **Scheduled** | Periodic polling or batch jobs | Cron syntax, minimum 5-minute intervals |
| **Manual** | Testing and on-demand execution | Click "Run" in UI |
| **Callable** | Invoked by another workflow | Acts as a reusable function, receives input params |
| **Service Trigger** | Pre-built event listeners | Salesforce CDC, Shopify webhooks, etc. |
| **Form** | User-submitted data | Built-in form builder, generates structured payloads |
| **Email** | Inbound email processing | Parses sender, subject, body, attachments |
| **Alerting** | Error handling | Triggered when another workflow fails |
| **Pub/Sub** | Internal message bus | Decouple producers from consumers |
| **Queue** | Rate-controlled processing | Ordered, throttled execution |

**Best practice:** Prefer Callable triggers over webhooks for internal workflow-to-workflow communication. Use API Management over raw webhooks for external-facing endpoints (better auth, rate limiting, audit).

### Connectors

Tray provides **700+ pre-built connectors** for SaaS services, databases, cloud providers, and utilities.

**Connector categories:**
- **Service connectors** — Salesforce, Slack, Shopify, QuickBooks, NetSuite, Xero, etc.
- **AI connectors** — Anthropic (Claude), OpenAI, AWS Bedrock, Merlin suite
- **Core/Helper connectors** — Boolean Condition, Loop, Branch, Script, Data Storage, HTTP Client, CSV, JSON, XML
- **Trigger connectors** — Webhook, Scheduled, Manual, Callable, Queue

Each connector exposes **operations** — pre-built actions like "Create Record", "Find Records", "Send Message". Operations have typed input schemas and structured output schemas.

### Operations

An operation is a single action on a connector:
- **Input schema** — Required and optional fields with types, validation, and dynamic lookups
- **Output schema** — Structured response including status, body, and metadata
- **DDL (Dynamic Dropdown Lists)** — Some operations are "lookup" helpers that populate dropdowns in the UI (e.g., list_objects for Salesforce, list_channels for Slack)

### Config Variables

Project-level variables accessible via `$.config.<key>`. Use for:
- Environment-specific values (API URLs, org IDs)
- Feature flags and toggles
- Batch sizes and rate limits
- Field mappings and picklist translations

**Never hardcode values that change between environments.** Always use config.

### Data Storage

Built-in key-value store with three scopes:
- **Workflow** — Isolated to a single workflow (watermarks, cursors)
- **Project** — Shared across workflows in a project (cross-workflow state)
- **Account** — Shared across all workflows (global config, feature flags)

Operations: `set`, `get`, `delete`, `list`, `atomic_increment`

**Best practice:** Use Workflow scope for watermarks and delta sync cursors. Use Project scope for cross-workflow coordination. Avoid Account scope unless truly global.

### Callable Workflows

Workflows that act as reusable functions:
- Invoked via `Call Workflow` step from another workflow
- Accept typed input parameters
- Return structured output via `Callable Response` step
- Run in the **same execution context** (shared auth scope)
- Support concurrent execution

**When to use:** Extract repeated logic (e.g., "upsert to Salesforce with retry") into a callable workflow, then invoke from multiple parent workflows.

---

## 3. Workflow Building

### Step Configuration

Every step has:
1. **Connector** — Which service to use
2. **Operation** — Which action to perform
3. **Input mapping** — Map data from previous steps, config, or hardcoded values
4. **Error handling** — What to do on failure (stop, continue, branch)
5. **Output** — Structured response accessible via JSONPath

### Branching

**Boolean Condition** connector evaluates conditions:
- Operators: equals, not_equals, contains, starts_with, ends_with, greater_than, less_than, is_empty, is_not_empty, regex_match
- Combine with **All** (AND) or **Any** (OR) logic
- Routes to **True** or **False** branches

### Looping

**Loop Collection** connector iterates over arrays:
- Input: JSONPath to an array (e.g., `$.steps.salesforce-1.result.body.records`)
- Each iteration exposes `$.steps.<loop-name>.value` (current item)
- Options: `concurrent: true` for parallel execution (use with caution — respect rate limits)
- Use **Break** step to exit early

### Error Handling Per Step

Three options for each step:
1. **Stop workflow** — Halt execution, mark as failed, trigger alerting workflow
2. **Continue** — Ignore the error, proceed to next step (step output is the error)
3. **Error branch** — Route to a separate path for custom error handling

**Best practice:** Never use "continue" without logging the error. Always have an alerting workflow in production.

### Testing & Debugging

- **Test run** — Execute workflow with sample data, inspect step-by-step outputs
- **Use Output** — Manually set a step's output from a test run (pins the output for subsequent step testing)
- **Logs** — Every execution is logged with inputs, outputs, timing, and errors
- **Isolated step testing** — Run individual steps to verify connector configuration

---

## 4. Connector Reference

### 4.1 Connector Architecture (from source)

All Tray connectors follow this structure:

```
connector-name/
├── connectors/
│   └── connector-name/
│       ├── operation-name/
│       │   ├── schema.js    — Input/output schema definition
│       │   ├── model.js     — HTTP config, validation, transformation
│       │   └── response.sample.json
│       ├── connector.js     — Connector metadata
│       ├── global_model.js  — Base URL, auth headers, global settings
│       └── global_schema.js — Shared schemas
├── helpers/                 — Reusable schemas, models, lookups
├── manifest.toml            — Lambda config, auth flags
└── connectors.json          — Complete operation definitions
```

**Schema types:**
```javascript
{
  required: boolean,
  type: 'string' | 'integer' | 'boolean' | 'array' | 'object',
  description: 'User-facing help text',
  lookup: { url, body },     // Dynamic dropdown
  enum: ['val1', 'val2'],    // Fixed options
  default: 'value',
  format: 'datetime' | 'email' | 'file' | 'html',
  advanced: true             // Hidden by default in UI
}
```

### 4.2 Salesforce Connector (v8.6+)

**Auth:** OAuth 2.0 (access_token + instance_url)
**56 operations** organized by category:

**CRUD:**
| Operation | Description | Batch Support |
|-----------|-------------|:---:|
| `create_record` | Create any SObject | No |
| `update_record` | Update by ID | No |
| `upsert_record` | Create or update by external ID | No |
| `delete_record` | Delete by ID | No |
| `find_records` | SOQL query with pagination | No |
| `query` | Raw SOQL execution | No |
| `sosl_query` | Full-text search (SOSL) | No |
| `count_records` | Count by SOQL WHERE | No |
| `merge_records` | Merge duplicate records | No |
| `convert_lead` | Lead → Contact/Account/Opportunity | No |

**Batch operations (up to 200 records):**
| Operation | Description |
|-----------|-------------|
| `batch_create_records` | Create up to 200 records atomically |
| `batch_update_records` | Update up to 200 records |
| `batch_delete_records` | Delete up to 200 records |
| `bulk_update_records` | Large-scale updates (Bulk API 2.0) |
| `bulk_upsert_records` | Large-scale upsert (Bulk API 2.0) |

**Bulk Data API 2.0 (jobs):**
| Operation | Description |
|-----------|-------------|
| `create_query_job` | Start async bulk query |
| `get_job_info` | Check job status |
| `get_query_job_results` | Retrieve completed results |
| `list_query_jobs` | List all jobs |
| `delete_query_job` | Cancel/abort job |

**Reports & Analytics:**
`execute_report_sync`, `execute_report_async`, `execute_report_query`, `list_reports`, `list_report_types`, `get_instance_results`, `list_report_instances`

**Files:**
`upload_attachment`, `download_attachment`, `upload_file`, `download_file`, `upload_and_link_file`

**Metadata:**
`describe_global`, `get_object_type`, `get_picklist_item_details`, `so_object_describe`, `so_object_info`, `get_user_info`

**Custom Fields:**
`create_custom_field`, `update_custom_field`, `delete_custom_field`

**Consent:**
`get_consent`, `write_consent`

**Key schema — find_records:**
```javascript
{
  object: { required: true, lookup: 'list_objects' },
  where: { type: 'string', description: 'SOQL WHERE clause' },
  limit: { type: 'integer', default: 100 },
  offset: { type: 'integer', default: 0 }
}
// Response: { total, next_page_offset, records: [...] }
```

**Pagination:** Offset-based (`limit` + `offset`), returns `next_page_offset`.

### 4.3 QuickBooks Connector (v3.4+)

**Auth:** OAuth 2.0 (access_token + realm_id)
**69 operations**

**Core entities and operations:**

| Entity | Create | Get | Update | Delete | List |
|--------|:---:|:---:|:---:|:---:|:---:|
| Customer | ✓ | ✓ | ✓ | — | ✓ |
| Invoice | ✓ | ✓ | ✓ | — | ✓ |
| Bill | ✓ | ✓ | ✓ | — | ✓ |
| Vendor | ✓ | ✓ | ✓ | — | ✓ |
| Employee | ✓ | ✓ | ✓ | — | ✓ |
| Payment | ✓ | ✓ | — | — | ✓ |
| Purchase | ✓ | ✓ | ✓ | ✓ | ✓ |
| Transfer | ✓ | ✓ | ✓ | ✓ | ✓ |
| Account | ✓ | ✓ | ✓ | — | ✓ |
| Item | ✓ | ✓ | ✓ | — | ✓ |
| Credit Memo | ✓ | ✓ | ✓ | — | ✓ |

**Key patterns:**
- Customer create has rich schema: addresses (billing/shipping), phone formats, taxable flag, job hierarchy, payment method, sales terms
- Invoice lines support `DetailType: SalesItemLineDetail` with item refs, quantity, unit price, tax codes
- Extensive DDL operations for populating dropdowns (accounts, items, terms, payment methods, tax codes, classes, departments)

**API base:** `POST /v3/company/{realm_id}/<entity>`

### 4.4 AWS S3 Connector (v1.0)

**Auth:** IAM Access Key + Secret Key + Region
**12 operations**

| Operation | Description |
|-----------|-------------|
| `put_object_file` | Upload file object |
| `put_object_text` | Upload text content |
| `get_object` | Download object |
| `head_object` | Get metadata without body |
| `delete_object` | Delete single object |
| `delete_multiple_objects` | Batch delete |
| `list_objects` | List with pagination (continuation token) |
| `list_buckets` | List all buckets |
| `get_bucket_location` | Get bucket region |
| `get_object_signed_url` | Generate temporary access URL |
| `put_object_acl` | Set access control |

**Key patterns:**
- ACL options: private, public-read, public-read-write, authenticated-read, bucket-owner-read, bucket-owner-full-control
- Metadata: custom key-value pairs attached to objects
- Pagination: continuation token-based
- Signed URLs: temporary access with configurable expiry

### 4.5 Slack Connector (v4.0+)

**Auth:** OAuth 2.0 (Bearer token)
**32 operations**

**Messaging:**
- `send_message` — Post to channel/user (supports blocks, attachments, threads, scheduled posts; max 20 attachments)
- `send_ephemeral_message` — Visible only to one user
- `send_response_message` — Reply to slash commands
- `update_message` — Edit existing message
- `delete_scheduled_message` — Cancel scheduled post
- `create_pin` — Pin message to channel
- `add_reminder` — Set user reminder

**Channels:**
- `create_conversation` — Create DM/group/channel
- `archive_conversation`, `leave_conversation`
- `get_conversation_info`, `conversation_exists`
- `set_conversation_topic`, `set_conversation_purpose`
- `invite_user_to_conversation`

**Users:**
- `get_user`, `get_user_by_email`
- `set_profile` — Update user profile
- `list_users` — All workspace users

**Block Kit validation:** The connector validates Block Kit JSON syntax before sending. Invalid block JSON throws a `UserInputError`.

### 4.6 Shopify Connector (v4.0+)

**Auth:** OAuth 2.0 (API version 2021-07)
**69 operations**

**Products:** create, get, delete, list, count + variants, images, metafields
**Orders:** create, get, delete, list, count, cancel, close + fulfillments, draft orders
**Customers:** create, get, delete, list, count + account activation, order history
**Inventory:** create/delete levels, get/list items, location-based stock
**Collections:** get, list products in collection

**Key patterns:**
- **Pagination:** Cursor-based JWT tokens (from Link header `page_info` parameter)
- **Order validation:** Line items must have either `variant_id` (existing) OR `title + price` (custom)
- **Product options:** Maximum 3 option definitions per product
- **Raw HTTP disabled:** Shopify TOS requires using typed operations

### 4.7 NetSuite Connector (v3.0+)

**Auth:** Token-Based Authentication (TBA) — consumer key/secret + token ID/secret + account ID
**21 operations**

**CRUD:** `create_record`, `get_record`, `update_record`, `upsert_record`, `delete_record`
**Query:** `find_records` (conditions-based), `filter_records` (advanced), `execute_suiteql` (SQL-like)
**Metadata:** `list_record_types`, `list_record_fields`, `list_field_options`
**Transform:** `transform_record` (convert between record types, e.g., Sales Order → Fulfillment)
**Utility:** `raw_http_request`

**Key patterns:**
- Dynamic schemas — input fields are determined by `record_type` selection
- SuiteQL — SQL-like query language for complex queries
- Record transformation — native support for order-to-fulfillment, quote-to-order, etc.
- Conditions use `[field, operator, value]` triplets with `all`/`any` matching

### 4.8 Xero Connector (v2.0+)

**Auth:** OAuth 2.0 (access_token + `xero-tenant-id` header)
**49 operations**

**Invoices:** create/update, get, delete, list, email, notes, attachments, URL
**Bank:** transactions (create/update, get, list, attachments), transfers (create, get, list)
**Contacts:** create, update, get, list
**Payments:** apply, get, delete, list
**Accounts & Items:** get, list, chart of accounts

**Key patterns:**
- **Tenant ID required** on every request (multi-org support)
- **Rate limits** exposed in response headers: `x-daylimit-remaining`, `x-minlimit-remaining`, `x-appminlimit-remaining`
- **Modified-since** filtering via `If-Modified-Since` header for delta sync
- **Multi-currency** support for international suppliers

### 4.9 HTTP Client Connector (v1.0)

**Auth:** Bearer token, Basic Auth, or custom headers
**7 operations:** GET, POST, PUT, PATCH, DELETE, HEAD + content type list

**Body types:** form_urlencoded, form_data (multipart with files), JSON, raw (XML), binary

Use HTTP Client as a fallback when no dedicated connector exists, or for custom APIs. Prefer dedicated connectors when available — they handle auth refresh, pagination, and error parsing automatically.

### 4.10 Core/Helper Connectors

| Connector | Purpose | Key Operations |
|-----------|---------|---------------|
| **Script** | Custom JavaScript (Node.js) | Single `run` operation; lodash, moment-timezone, crypto, Buffer, URL available |
| **Boolean Condition** | Branching logic | Evaluate conditions with All (AND) / Any (OR) |
| **Loop Collection** | Iterate arrays | Sequential or concurrent iteration |
| **Branch** | Multi-path routing | Route to named branches |
| **Break** | Exit loop early | Conditional loop termination |
| **Call Workflow** | Invoke callable workflow | Pass params, receive response |
| **Data Storage** | Key-value store | set, get, delete, list, atomic_increment |
| **Data Mapper** | Transform values | Map between formats without code |
| **CSV Editor** | CSV manipulation | Parse, generate, transform CSV data |
| **JSON Transformer** | JSON manipulation | JMESPath and JSONPath transforms |
| **Delay** | Pause execution | Wait N seconds (use sparingly — consumes task) |
| **Terminate** | Stop workflow | Force stop with status code |
| **List Helpers** | Array operations | Pluck, flatten, unique, sort, filter |
| **Text Helpers** | String operations | Replace, split, join, regex, template |
| **Date & Time Helpers** | Date operations | Parse, format, diff, add/subtract |
| **Math Helper** | Arithmetic | Calculate, round, aggregate |
| **Object Helpers** | Object manipulation | Merge, pick, omit, flatten |
| **Encryption Helper** | Crypto operations | Encrypt, decrypt, hash, HMAC |

---

## 5. Authentication Patterns

### Authentication Types by Connector

| Pattern | Connectors | How It Works |
|---------|-----------|--------------|
| **OAuth 2.0** | Salesforce, QuickBooks, Slack, Shopify, Xero | Tray handles token refresh automatically |
| **Token-Based Auth (TBA)** | NetSuite | Consumer key/secret + token ID/secret + account ID |
| **IAM Credentials** | AWS S3, Lambda, SQS | Access Key + Secret Key + Region |
| **API Key** | Many services | Key in header or query param |
| **Basic Auth** | SMTP, FTP, JDBC | Username + password, base64 encoded |

### Authentication Scoping

| Scope | Visibility | Use Case |
|-------|-----------|----------|
| **Personal** | Only the creator | Development and testing |
| **Workspace** | All users in workspace | Production workflows |
| **Organization** | All users across workspaces | Shared services (Slack, email) |

### Best Practices

1. **Always use `$.auth` references** — Never hardcode credentials or tokens
2. **Use workspace-scoped auths for production** — Personal auths break when the creator leaves
3. **Separate auths per environment** — Dev auth should never point to production
4. **Monitor token expiry** — OAuth tokens auto-refresh, but check for auth failures in error handling
5. **Use Named Credentials in Salesforce** — For Salesforce-to-external callouts, configure Named Credentials rather than storing API keys in custom settings

---

## 6. Script Connector Patterns

The Script connector runs Node.js code inside Tray workflows. It's the power tool for complex data transformations.

### Available Libraries (Pre-installed)

- **lodash** — Array/object manipulation, deep cloning, grouping
- **moment-timezone** — Date parsing, formatting, timezone conversion
- **crypto** — Hashing (SHA256, MD5), HMAC, encryption
- **Buffer** — Binary data handling
- **URL** — URL parsing and construction

No other libraries are available. Do not attempt to `require()` anything else.

### Functional Programming Rules

These are **mandatory** for all Tray scripts in the Ohanafy monorepo:

1. **`exports.step` is orchestration only** — No function definitions inside exports.step. It should only call helper functions and return a result.

2. **All helpers defined below exports.step** — Functions are hoisted, so define them after the main orchestration block.

3. **Pure functions** — No side effects. Functions take inputs and return outputs. No mutations of external state.

4. **Immutable data** — Use spread operator, `Object.assign({}, ...)`, or lodash's `_.cloneDeep()`. Never mutate input parameters.

5. **No console.log in production** — Use structured output for debugging information.

### Script Template

```javascript
exports.step = function(input) {
  // Orchestration only — call helpers, return result
  const validated = validateInput(input);
  const transformed = transformRecords(validated.records);
  const batched = buildBatches(transformed, validated.config.batchSize);

  return {
    success: true,
    batches: batched,
    summary: {
      total: validated.records.length,
      transformed: transformed.length,
      batches: batched.length
    }
  };
};

// --- Helper functions below ---

function validateInput(input) {
  if (!input.records || !Array.isArray(input.records)) {
    throw new Error('records must be an array');
  }
  return {
    records: input.records,
    config: input.config || {}
  };
}

function transformRecords(records) {
  return records.map(record => ({
    ...record,
    Name: (record.Name || '').trim(),
    Amount: parseFloat(record.Amount) || 0
  }));
}

function buildBatches(records, batchSize = 200) {
  const batches = [];
  for (let i = 0; i < records.length; i += batchSize) {
    batches.push(records.slice(i, i + batchSize));
  }
  return batches;
}
```

### Pattern Library

11 production-tested modules in `integrations/patterns/`:

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `script-scaffold.js` | Starter template | CONFIG, FIELD_MAPPINGS, STATUS_MAP, 4-phase flow |
| `soql-query-builder.js` | SOQL construction | escapeSOQLValue, formatInClause (2000-value limit), buildSOQLQuery |
| `batch-processing.js` | Array operations | chunkArray, groupBy, deduplicateBy, buildCompositeRequest |
| `data-mapping.js` | Field transformation | evaluateConditions (AND/OR), applyFieldRules (toNumber, concat, replace, date) |
| `error-handling.js` | SF error extraction | hasErrors, extractErrorsFromResult, extractAllErrors + SF error type map |
| `validation.js` | Input validation | Required fields, type checks, format patterns (email, phone, SF ID, zip) |
| `string-manipulation.js` | Text processing | Proper casing, address cleaning, phone formatting, SOQL sanitization |
| `csv-output.js` | Fixed-width output | formatAlpha, formatDate, formatNumeric (EDI-style records) |
| `date-time.js` | Date handling | parseDateFlexible (handles MM/DD, DD/MM, ISO), toSalesforceDate (no external libs) |
| `lookup-maps.js` | Map/Set utilities | createLookupMap, createReverseLookupMap, createStatusMap, partitioning |
| `output-structuring.js` | Result envelopes | createSuccessOutput, createErrorOutput, buildSummary |

**Always start from `script-scaffold.js`** when creating a new integration script. Copy the 4-phase pattern (validate → transform → batch → output) and customize.

---

## 7. Tray Embedded (OEM)

Tray Embedded lets ISVs (like Ohanafy) offer integrations to their customers through a white-labeled marketplace.

### Architecture

```
Ohanafy App
  └── Embedded Marketplace (React UI)
        └── Solutions (templatized integrations)
              └── Solution Instances (per-customer activation)
                    └── Config Wizard (customer configures their instance)
                          ├── Auth Slots (customer authenticates their accounts)
                          └── Config Slots (customer sets preferences)
```

### Key Concepts

**Solution** — A Project converted into a templatized integration. Published solutions are available for end users to activate. Lifecycle states: Draft → Live → Changed.

**Solution Instance** — A customer's personalized activation of a solution. Each instance has its own config values, authentications, and workflow instances.

**Config Wizard** — UI that guides customers through setting up their instance. Contains screens with auth slots and config slots.

**Auth Slots** — Places where customers authenticate their own accounts (e.g., their Salesforce org, their QuickBooks company).

**Config Slots** — Places where customers provide preferences (e.g., which Salesforce object to sync, batch size, notification channel). Can be:
- Text input
- Dropdown (static list or dynamic via callConnector)
- Boolean toggle
- Hidden (pre-configured by the ISV)

**End Users** — Customers who activate solution instances. They have their own auths, instances, and logs. Separate from Tray org users.

### Embedded API

Three APIs for programmatic control:

1. **Users API (GraphQL)** — Register/manage end users, create/manage solution instances
2. **Auths API** — Create, retrieve, delete authentications for end users
3. **Connectors API** — Call individual connector operations on behalf of end users

**Master Token** — Organization-level API key for Embedded API access. Store in AWS Secrets Manager, never in code.

**Endpoints by region:**
- US: `https://tray.io/graphql`
- EU: `https://eu1.tray.io/graphql`
- AP: `https://ap1.tray.io/graphql`

### Config Wizard Custom JavaScript

5 event types for dynamic behavior:

| Event | When It Fires | Common Use |
|-------|--------------|------------|
| `CONFIG_SLOT_MOUNT` | Slot renders on screen | Populate dynamic dropdowns |
| `CONFIG_SLOT_VALUE_CHANGED` | User changes a value | Show/hide dependent fields |
| `CONFIG_SLOT_STATUS_CHANGED` | Slot validation state changes | Update UI based on validation |
| `AUTH_SLOT_MOUNT` | Auth slot renders | Pre-fill auth fields |
| `AUTH_SLOT_VALUE_CHANGED` | Auth credential changes | Validate credentials, update dependent dropdowns |

**`callConnector`** — Fetches live data from services to populate dynamic dropdowns (e.g., list Salesforce objects, list Slack channels). Returns a promise with the connector response.

See `skills/tray/tray-embedded-customjs/` for pattern guides:
- `dynamic-dropdown.md` — Fetch options from an API
- `dependent-dropdown.md` — Options change based on another slot
- `show-hide-dependency.md` — Toggle visibility
- `input-validation.md` — Validate user input
- `array-of-objects.md` — Repeatable form rows

### Publishing Flow

1. Build workflows in a Project
2. Add config slots for customer-configurable values
3. Add auth slots for customer authentications
4. Create Solution from Project
5. Configure Config Wizard screens (reorder, add UI elements)
6. Publish Solution (pre-publish screen shows breaking vs. non-breaking changes)
7. End users activate Solution Instances through your marketplace

---

## 8. Error Handling

### Error Types (Ohanafy Standard)

All Tray scripts processing Salesforce APIs must use this enumeration:

```javascript
const ERROR_TYPES = {
  ValidationFailed:    'VALIDATION_FAILED',
  AuthenticationError: 'AUTHENTICATION_ERROR',
  RecordNotFound:      'RECORD_NOT_FOUND',
  DuplicateRecord:     'DUPLICATE_RECORD',
  RecordLocked:        'RECORD_LOCKED',
  FieldError:          'FIELD_ERROR',
  LimitExceeded:       'LIMIT_EXCEEDED',
  InvalidReference:    'INVALID_REFERENCE',
  TriggerError:        'TRIGGER_ERROR',
  BatchError:          'BATCH_ERROR',
  TimeoutError:        'TIMEOUT_ERROR',
  NetworkError:        'NETWORK_ERROR',
  UnknownError:        'UNKNOWN_ERROR',
  PartialSuccess:      'PARTIAL_SUCCESS'
};
```

### Salesforce Error Code Mapping

| SF Error Code | Error Type | Retry? | Notes |
|--------------|------------|:---:|-------|
| `UNABLE_TO_LOCK_ROW` | RecordLocked | Yes (3x, 2s backoff) | Concurrent update conflict |
| `REQUEST_LIMIT_EXCEEDED` | LimitExceeded | Yes (exponential backoff) | API call limits hit |
| `INVALID_CROSS_REFERENCE_KEY` | InvalidReference | No | Bad lookup relationship |
| `INVALID_ID_FIELD` | FieldError | No | Malformed Salesforce ID |
| `MALFORMED_ID` | FieldError | No | ID format error |
| `DUPLICATE_VALUE` | DuplicateRecord | No | Unique constraint violation |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | ValidationFailed | No | Validation rule failure |
| `REQUIRED_FIELD_MISSING` | FieldError | No | Missing required field |
| `STRING_TOO_LONG` | FieldError | No | Field length exceeded |

### HTTP Status Code Mapping

| Status | Error Type | Retry? |
|--------|-----------|:---:|
| 400 | ValidationFailed | No |
| 401 | AuthenticationError | No (re-auth needed) |
| 403 | AuthenticationError | No (insufficient permissions) |
| 404 | RecordNotFound | No |
| 409 | DuplicateRecord | No |
| 429 | LimitExceeded | Yes (respect Retry-After header) |
| 500 | UnknownError | Yes (1x) |
| 502/503/504 | NetworkError | Yes (3x with backoff) |

### Retry Strategy

```javascript
function retryWithBackoff(fn, maxRetries = 3, baseDelay = 2000) {
  let attempt = 0;
  while (attempt < maxRetries) {
    try {
      return fn();
    } catch (err) {
      attempt++;
      if (attempt >= maxRetries || !isRetryable(err)) throw err;
      const delay = baseDelay * Math.pow(2, attempt - 1);
      // In Tray Script connector, you cannot sleep
      // Instead, use workflow-level retry with Delay step
    }
  }
}
```

**Important:** The Script connector cannot sleep/wait. For retries, use workflow-level patterns: add a Delay step between retry attempts, or use the Loop connector with a Break condition on success.

### Workflow-Level Error Handling

1. **Per-step error branches** — Route failures to error-specific logic
2. **Alerting workflow** — Dedicated workflow triggered on failure, sends Slack/email notifications
3. **Dead letter queue** — Store failed payloads in Data Storage for manual replay
4. **Idempotency** — Use event IDs to prevent duplicate processing on retry

---

## 9. Billing & Task Credits

### How Tasks Are Counted

**1 task = 1 step execution.** This is the primary billing metric.

| Action | Tasks |
|--------|:---:|
| Trigger fires (webhook, schedule, etc.) | 1 |
| Each connector operation executes | 1 |
| Each loop iteration | 1 |
| Each boolean condition evaluation | 1 |
| Each Call Workflow invocation | 1 |
| Callable workflow trigger (receiving end) | 1 |
| Connectivity API `Call Connector` | 1 |
| Connector retries (automatic) | 0 (free) |

**Not charged:** Automatic connector retries. If Tray retries a failed HTTP call internally, you are not billed for the retry attempts.

### AI Token Billing

AI connector usage (Anthropic, OpenAI, Bedrock, Merlin) is billed by tokens:
- Input tokens (prompt) + output tokens (response) = total tokens
- Tokens convert to tasks using a customer-specific ratio (contact Tray support for your ratio)
- Merlin IDP: 1 unit per page processed

### Cost Optimization

1. **Minimize steps** — Combine logic in Script connector rather than using many small steps
2. **Use boolean conditions wisely** — Each evaluation costs 1 task
3. **Batch before looping** — Process arrays in Script connector, not with Loop + individual connector calls
4. **Skip-if-running** — Prevent concurrent executions of polling workflows (avoids double-processing)
5. **Delta sync** — Use watermarks (Data Storage) to only process changed records
6. **Concurrent loops cautiously** — Parallel execution is faster but consumes tasks at the same rate

### Monitoring

- **Insights Hub** — Near real-time metrics on task runs, data volume, active workflows
- **Alerts** at 80% and 100% of task entitlements
- **Workspace limits** — Set per-workspace monthly task caps to isolate dev from prod costs
- **Data retention** by plan: Pro (7 days), Team (30 days), Enterprise (180 days)

---

## 10. Security

### Authentication Security

- **Data encrypted at rest** — All credentials encrypted in storage
- **Additional encryption** for API keys and access tokens
- **Never hardcode credentials** — Always use `$.auth` references
- **AAA Framework** via API Management: Authenticate → Authorize → Audit

### Encryption Tools

| Tool | Purpose |
|------|---------|
| **Crypto Helpers** | Encrypt/decrypt, HMAC, hash within workflows |
| **PGP Encryption** | File-level encryption for data in transit |
| **JWT Helper** | Sign and verify JSON Web Tokens |

### Webhook Security

- Webhook URLs are UUID-based (unguessable, but not authenticated)
- Add **CSRF token** validation in headers
- Better: convert webhooks to **managed APIs** with access controls
- For Ohanafy: always validate **HMAC-SHA256** signatures on inbound webhooks

### Log Security

| Plan | Retention | Options |
|------|-----------|---------|
| Pro | 7 days | — |
| Team | 7-30 days | 180-day add-on |
| Enterprise | 30 days | Ghost processing (24hr only, no visible logs) |

**Log streaming** — Send execution data to your own SIEM regardless of retention settings.

### Network Security

- **On-premise agent** — For connecting to systems behind firewalls
- **VPN connectivity** — AWS VPN integration for private network access
- **IP whitelisting** — Available on Enterprise plans

### Ohanafy-Specific Security Rules

1. No credentials in code — AWS Secrets Manager only
2. No customer PII in workflow logs
3. Tray webhooks must validate HMAC-SHA256 signatures
4. Master Token stored in AWS Secrets Manager (`tray/master-token`)
5. Customer Salesforce orgs are read-only by default

---

## 11. Lifecycle Management

### Environment Strategy

**For standard workflows (Workspace-based):**
```
Dev Workspace → Test/QA → Prod Workspace
```
- Export project from dev workspace
- Import to prod workspace
- Re-map authentications to production credentials
- Config variables automatically separate per workspace

**For Embedded solutions (Multi-org):**
```
Dev Tray Org → Staging Tray Org → Prod Tray Org
```
- Each environment has its own Master Token
- Custom services and connectors must be re-mapped during promotion
- Use test End Users in staging to avoid billing impact

### Project Export/Import

1. **Export** — Download project as JSON (includes workflows, config, steps)
2. **Import** — Upload JSON to target workspace/org
3. **Re-map** — Update authentications, config variables, and custom service references

### Version Control (Ohanafy convention)

Projects use the 4-level hierarchy in the monorepo:

```
01-tray/[Workspace]/[ProjectName_UUID]/versions/current/scripts/
```

**Rules:**
- Never rename UUID-based directory names (breaks sync)
- Never edit `project-metadata.json` manually (sync-managed)
- Always work within `versions/current/` directory
- Use `tray-sync.js` for all sync operations

### Monitoring After Deployment

1. Check Insights Hub for task run success rates
2. Verify error rates are within acceptable thresholds
3. Monitor Data Storage for dead-letter entries
4. Check Slack alerting channel for workflow failures
5. Review billing dashboard for unexpected task consumption

---

## 12. Ohanafy Integration Patterns

### The Consolidation Pattern

Ohanafy's primary integration philosophy: **Replace scattered multi-workflow chains with a single Master Script Connector.**

Before: 8-22 workflows per integration (hard to maintain, expensive in tasks)
After: 1-2 workflows with a Master Script handling all logic

### 3-Layer Architecture

```
Layer 1: Tray Connector Operations (pure connector calls)
Layer 2: OHFY Business Logic (reusable validation/transformation)
Layer 3: Org-Specific Configuration (field mappings, picklists)
```

### 4-Phase Script Pattern

Every integration script follows:

```
Phase 1: Extract & Validate
  → Receive data from trigger/connector
  → Validate required fields, types, formats
  → Reject invalid records with structured errors

Phase 2: Transform
  → Apply field mappings (source → target)
  → Apply business rules (status mapping, calculations)
  → Normalize data (dates, currencies, addresses)

Phase 3: Execute
  → Build Salesforce Composite API requests
  → Batch into groups of 200
  → Execute with error handling per batch

Phase 4: Process Results
  → Separate successes from failures
  → Build summary statistics
  → Route errors to dead-letter / alerting
  → Return structured output
```

### Integration Types

| Type | Trigger | Example | Pattern |
|------|---------|---------|---------|
| **EDI** | S3 event / scheduled | 850/810/856 document processing | S3 → Script → Salesforce |
| **Accounting Sync** | Scheduled (15-30 min) | QuickBooks ↔ Salesforce bidirectional | Parallel extract → compare → sync |
| **Real-time Pipeline** | Webhook | Order creation, status updates | Webhook → validate → transform → SF |
| **Batch Sync** | Scheduled (daily) | Inventory levels, price updates | SOQL query → transform → external API |

### Production Working Examples

Two complete implementations are documented in `docs/integration-guides/CONSOLIDATED_SCENARIO_EXAMPLES.md`:

1. **EDI Processing** — Replaces 8 workflows. Discovery → Processing → Transform → SF Sync → Outbound Generation → Results. S3 trigger, 810/856 parsing, UPC mapping, bulk upsert.

2. **QuickBooks Sync** — Replaces 22 workflows. Parallel extraction from SF + QBO → Apply business logic → Bidirectional sync → Reconciliation → Notifications.

### Salesforce Composite API Best Practices

When writing scripts that call Salesforce:

1. **URL-encode external IDs** — `encodeURIComponent(externalId)` for IDs with special characters (#, /, ?, &, =, +, space)
2. **Batch into groups of 200** — Composite API limit per request
3. **Handle partial success** — Some records may succeed while others fail in the same batch
4. **Chunk IN clause values** — SOQL IN clause supports max 2000 values; chunk larger sets
5. **Use namespace prefix** — Ohanafy fields use `ohfy__` prefix (e.g., `ohfy__Order__c`)
6. **Rate limit between batches** — Add 1-second delay between Composite API calls

---

## 13. Connector Operations Quick Reference

### Ohanafy's Active Connectors

Based on known production usage:

| Connector | Primary Use | Key Operations |
|-----------|-------------|----------------|
| **Salesforce** | Core CRM/ERP | find_records, batch_create, batch_update, upsert, query |
| **AWS S3** | File storage (EDI, exports) | get_object, put_object_file, list_objects |
| **AWS Lambda** | Custom compute | invoke |
| **QuickBooks** | Accounting sync | create_invoice, create_customer, find |
| **Slack** | Notifications & alerting | send_message |
| **Google Sheets** | Reporting, config | get_rows, add_row, update_row |
| **GitHub** | CI/CD, issue tracking | create_issue, get_repository |
| **HTTP Client** | Custom API calls | get_request, post_request |
| **Script** | Data transformation | (custom JS) |
| **Data Storage** | State management | set, get, atomic_increment |

### Full Connector Catalog

See `knowledge-base/tray/connector-catalog.md` for the curated catalog of 40+ connectors relevant to Ohanafy.

For the complete list of 700+ connectors, refer to the connectors-master reference at `/Users/danielzeder/Downloads/connectors-master/` (782 connector directories with full schemas).

---

## 14. Troubleshooting

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Workflow not triggering | Webhook URL changed, schedule paused | Check trigger config, verify webhook URL |
| Auth expired | OAuth token refresh failed | Re-authenticate in Tray UI, check scopes |
| Partial batch failure | Some records have validation errors | Check error response, fix data, retry failed records |
| High task consumption | Loop over large arrays | Consolidate into Script connector |
| Timeout on Salesforce query | SOQL query too complex | Add filters, use indexed fields, paginate |
| Data Storage key not found | Wrong scope or key spelling | Verify scope (workflow/project/account) and key |
| Config variable empty | Not set in target workspace | Set config vars after project import |
| Script connector error | Syntax error or unavailable library | Check for typos, only use pre-installed libs |

### Debugging Checklist

1. **Check workflow logs** — Inspect step-by-step inputs/outputs
2. **Verify auth** — Is the authentication active and correctly scoped?
3. **Test step in isolation** — Run individual steps to pinpoint failures
4. **Check Data Storage** — Are watermarks/cursors in expected state?
5. **Review config variables** — Are all required values set?
6. **Check Insights** — Are task runs spiking? Are there unusual error rates?
7. **Inspect error response** — What's the actual error code and message?

### Getting Help

- **Tray Support:** Create a ticket via Help Center
- **Tray Academy:** Guided learning at tray.ai/academy
- **Tray Community:** Community forums at tray.ai/community
- **Ohanafy Internal:** Check `skills/tray/` skills for pattern-specific guidance

---

## Appendix: File Reference

| Resource | Path |
|----------|------|
| This guide | `skills/tray/tray-expert/tray-expert-guide.md` |
| Architecture reference | `skills/tray/tray-expert/architecture-reference.md` |
| Connector catalog | `knowledge-base/tray/connector-catalog.md` |
| Capability matrix | `knowledge-base/tray/capability-matrix.md` |
| Connector operations guide | `docs/integration-guides/TRAY_CONNECTOR_OPERATIONS.md` |
| Integration master guide | `docs/integration-guides/OHFY_INTEGRATION_MASTER_GUIDE.md` |
| JSON structure guide | `docs/integration-guides/Tray-AI-Project-JSON-Structure-Guide.md` |
| Scenario examples | `docs/integration-guides/CONSOLIDATED_SCENARIO_EXAMPLES.md` |
| Script patterns | `docs/integration-guides/SCRIPT_CONSOLIDATION_PATTERNS.md` |
| Pattern library | `integrations/patterns/` (11 JS modules) |
| Connectors source | `/Users/danielzeder/Downloads/connectors-master/` (782 connectors) |
| Embedded sample app | `integrations/tray/` (React + Express) |
| Sync script | `scripts/sync-tray-connectors.sh` |
| Error patterns | `skills/tray/tray-errors/error-handling-patterns.md` |
| Webhook patterns | `skills/tray/tray-webhook-handler/workflow-patterns.md` |
| Embedded JS patterns | `skills/tray/tray-embedded-customjs/patterns/` (7 guides) |
| Discovery scoring | `skills/tray/tray-discovery/scoring.md` |
