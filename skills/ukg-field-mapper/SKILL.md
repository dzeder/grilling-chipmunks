---
name: ukg-field-mapper
description: |
  UKG field mapping assistant. Generates and validates field mappings between
  UKG API responses and Salesforce custom objects. Lists available fields by
  entity, generates mapping tables with data type conversions, and flags
  product-specific differences.
  TRIGGER when: user asks to "map UKG fields", "field mapping", "what fields
  does UKG return", "UKG to Salesforce mapping", "add a field to the sync",
  "what data can we get from UKG". Proactively invoke when the user is working
  on field mappings or asking about available UKG data fields.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Write
  - Edit
  - WebSearch
  - AskUserQuestion
---

# UKG Field Mapping Assistant

You help build and validate field mappings between UKG APIs and Salesforce (Ohanafy) custom objects.

## Phase 1: Load Knowledge Base

Read both documents:

1. Read `ukg-expert-reference.html` — for complete field inventories by entity and product
2. Read `ukg-ohanafy-integration-design.html` — for the Salesforce data model (target objects and fields)

```bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo '.')"
ls -la "$ROOT"/ukg-expert-reference.html "$ROOT"/ukg-ohanafy-integration-design.html 2>/dev/null
```

## Examples

- "What employee fields can we get from UKG Pro WFM?" -- list the full field inventory for the employee entity, grouped by required vs nice-to-have
- "Create a field mapping table for schedule sync" -- generate a UKG-to-Salesforce mapping table with data types, transforms, and external ID strategy
- "Can we also sync the employee's supervisor name?" -- check if the field exists in UKG's API, verify the target SF field, and generate the mapping row

## Delegation

Do not trigger this skill for:
- General UKG questions about API endpoints, auth, or admin -- delegate to `ukg-expert`
- Debugging UKG API errors or sync failures -- delegate to `ukg-api-debug`
- Salesforce field/object creation metadata -- delegate to `salesforce-field-object-creator`
- Tray.io workflow design for the sync -- delegate to `tray-expert`

## Workflow

### 1. Load the UKG and Salesforce reference docs
Read `ukg-expert-reference.html` for field inventories and `ukg-ohanafy-integration-design.html` for the target Salesforce data model.

### 2. Classify the request
Determine whether the user wants to list fields, generate a mapping, add a field, validate existing mappings, or compare product differences.

### 3. Generate or validate the mapping
Produce a mapping table in the standard format (UKG API Field, UKG Type, SF Object.Field, SF Type, Transform) with appropriate data type conversions and null handling.

### 4. Flag gaps and next steps
Identify unmappable fields, product-specific unknowns, and questions for the customer discovery call.

## Phase 2: Understand the Request

Determine what the user needs:

1. **List available fields** — "What fields can we get from UKG for employees/schedules/timeoff?"
2. **Generate a mapping table** — "Create a field mapping for [entity]"
3. **Add a field** — "Can we also sync [field X]?"
4. **Validate a mapping** — "Is this mapping correct?"
5. **Compare products** — "What fields differ between Pro HCM and Pro WFM?"

If unclear, ask via AskUserQuestion:
- Which entity? (Employee, Schedule, TimeOff, Accrual)
- Which UKG product? (Pro HCM, Pro WFM, Ready — or "we don't know yet")
- Any specific fields they're interested in?

## Phase 3: Generate or Validate Mapping

### When listing available fields:
- Pull the field inventory from the expert reference doc for the requested entity
- Group by: required for integration, nice-to-have, product-specific
- Note which fields are nullable, which have different names across products

### When generating a mapping table:
Use this format (matches the design doc template):

| UKG API Field | UKG Type | SF Object.Field | SF Type | Transform |
|---|---|---|---|---|
| `fieldName` | String | `Object__c.Field__c` | Text | Direct copy / Parse date / Map values / etc. |

Include these columns:
- **UKG API Field:** Exact API field path (e.g., `primaryJob.departmentName`)
- **UKG Type:** Data type in UKG response (String, Integer, Date, DateTime, Boolean, Number)
- **SF Object.Field:** Target Salesforce object and field API name
- **SF Type:** Salesforce field type (Text, Number, Date, DateTime, Picklist, Checkbox, Email, Lookup)
- **Transform:** How to convert — "Direct copy", "Parse ISO date", "Map: Active→Active, Terminated→Terminated", "Concatenate firstName + lastName", "Convert to UTC", etc.

### When adding a field:
1. Check if the field exists in UKG's API for the relevant product
2. Check if a target Salesforce field already exists on the custom object
3. If the SF field doesn't exist, recommend creating it with appropriate type and length
4. Generate the mapping row

### Common transforms to flag:
- **Date/DateTime:** UKG returns ISO 8601; Salesforce DateTime is UTC. Convert timezone.
- **Status mapping:** UKG statuses (Active, Inactive, Terminated, Pre-Hire) → Salesforce picklist values
- **Null handling:** UKG may return null for optional fields. Define default values or leave blank.
- **Name fields:** UKG may provide `firstName` + `lastName` separately or `fullName` combined. Salesforce Name field is auto-populated.
- **External IDs:** `personNumber` → `UKG_Person_ID__c`, composite keys for schedule/timeoff records

### Product-specific differences:
When the UKG product is unknown, show both Pro HCM and Pro WFM field names:

| Concept | Pro HCM Field | Pro WFM Field | Notes |
|---|---|---|---|
| Employee ID | `employeeIdentity.employeeId` | `personNumber` | Different identifiers — need cross-system mapping if both products are used |
| Department | `departmentCode` | `primaryJob.departmentName` | HCM uses codes, WFM uses names |
| Job Title | `jobTitle` | `primaryJob.jobName` | Similar but different field paths |
| Hire Date | `originalHireDate` | `hireDate` | HCM also has `lastHireDate` for rehires |
| Status | `status` | `employmentStatus` | Same values, different field name |

## Phase 4: Output

Present the mapping table in clean Markdown format.

If the user asks you to save or update a mapping document, write it to a file in the project root (e.g., `ukg-field-mapping.md` or update the design doc).

Always end with:
- **Gaps:** Fields we can't map yet (depend on UKG product confirmation)
- **Questions for Gulf Distributing:** Specific field questions to ask on the discovery call
- **Next steps:** What needs to happen before this mapping is finalized
