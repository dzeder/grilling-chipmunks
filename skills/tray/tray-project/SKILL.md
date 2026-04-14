---
name: tray-project
description: >
  Generate importable Tray.io project JSON exports from workflow specifications.
  Covers the complete project structure: workflows, steps, connectors, auth objects,
  typed values, and the projects array. TRIGGER when: user asks to create a Tray project,
  generate a Tray workflow JSON, build an importable Tray export, or scaffold a new
  Tray integration as JSON. DO NOT TRIGGER when: user wants to write a Tray script step
  (use tray-script-generator), design a workflow conceptually (use tray-expert in Build
  mode), or create a Mermaid diagram (use tray-diagrams).
metadata:
  version: "1.0.0"
  scoring: "100 points across 5 categories"
---

# tray-project: Tray Project JSON Generator

Generate complete, importable Tray.io project JSON exports that can be imported directly
through the Tray UI (Settings > Import/Export > Import Project).

## When This Skill Owns the Task

- User asks to create a Tray project JSON from a workflow description
- User wants to scaffold a new integration as an importable Tray export
- User needs to fix or regenerate a broken Tray project export
- User wants to add a workflow to an existing project export
- User is building a project under `integrations/tray/Embedded/`

## Delegate Elsewhere

| Scenario | Route to |
|----------|----------|
| Writing the JavaScript for a script step | [tray-script-generator](../tray-script-generator/SKILL.md) |
| Conceptual workflow design / Q&A | [tray-expert](../tray-expert/SKILL.md) |
| Mermaid diagram of a workflow | [tray-diagrams](../tray-diagrams/SKILL.md) |
| Error handling patterns | [tray-errors](../tray-errors/SKILL.md) |
| Deployment validation | [deploy-prep](../deploy-prep/SKILL.md) |
| Tray Embedded config wizard JS | [tray-embedded-customjs](../tray-embedded-customjs/SKILL.md) |

## Required Context to Gather First

1. **What the workflow does** — trigger type, data flow, connectors needed
2. **Salesforce objects/fields** — check `knowledge-base/ohanafy/objects/` for field names
3. **Target customer/org** — determines auth group UUIDs (check memory for Daniel's defaults)
4. **Existing Tray projects** — check `integrations/tray/Embedded/` to avoid duplication (Tray-First Rule)

## Workflow

### Step 1: Load Reference Material

Read these before generating any JSON:

```
# Authoritative format reference (from real working export)
references/project-json-spec.md

# Auth details for Daniel's workspace
# (check memory: reference_tray_auth_details.md)

# Existing projects to avoid duplication
ls integrations/tray/Embedded/
```

### Step 2: Design the Workflow Structure

Map out the steps before writing JSON:

1. Identify the trigger type (scheduled daily, webhook, manual, alerting-trigger)
2. List each step in order with connector, operation, and data flow
3. Identify branch points (boolean conditions)
4. Identify loops (batch processing)
5. Determine error handling strategy (error workflow? inline branching?)

### Step 3: Generate UUIDs

Every workflow, project, version, and group needs a unique UUID. Generate them as
plausible v4 UUIDs. The `project_id` in each workflow must match the `id` in the
`projects` array.

### Step 4: Build the JSON

Follow the flat export format exactly. See `references/project-json-spec.md` for the
complete specification. Key rules:

1. **Flat top-level** — no `projectId`/`version`/`exportData` wrapper
2. **Typed values** — every property value wrapped as `{ "type": "...", "value": ... }`
3. **Correct connector versions** — see spec for current versions
4. **No authentication objects** — omit `authentication` on all steps. Icons come from `connector.name`. User configures auth after import.
5. **steps_structure matches steps** — every name in structure must exist in steps object
6. **Trigger is `"type": "normal"`** in steps_structure (not `"trigger"`)
7. **Config values are bare** — `settings.config` uses raw primitives, NOT typed wrappers
8. **Valid UUID v4** — every `id`, `project_id`, `group`, `creator`, `version.id` must be valid UUID v4

### Step 5: Create Supporting Files

For each project, create the standard directory structure:

```
integrations/tray/Embedded/{ProjectName}/
  versions/current/
    raw-exports/
      project-export.json      # The importable JSON
    scripts/
      01_Main/                 # Workflow number + name
        1-{step_name}/
          script.js            # Extracted JS (matches inline script)
          input.json           # Test input fixture
          output.json          # Expected output fixture
```

### Step 6: Validate

```bash
# Syntax check
node -e "JSON.parse(require('fs').readFileSync('project-export.json','utf8'))"

# Test any script steps
node -e "var s = require('./script.js'); console.log(JSON.stringify(s.step(require('./input.json')), null, 2))"
```

### Step 7: Post-Import Checklist

After the user imports, they must:
1. Map Salesforce authentication to the target org
2. Map Slack authentication
3. Set any config variables (e.g., Slack user ID)
4. Enable both workflows
5. Test with manual trigger before relying on schedule

## Scoring Rubric

| Category | Points | Criteria |
|----------|--------|----------|
| Structure | 25 | Flat format, all required top-level fields (incl. data_tables etc.), valid UUID v4 references, projects array links correctly |
| Typed Values | 25 | Every property value correctly wrapped, correct types for jsonpath/string/boolean/number/integer/object/array/null. Config values bare. |
| Connectors | 20 | Correct versions, correct operations, correct property schemas. No invalid connectors (sftp, tray-io-workflow-trigger). |
| Auth Handling | 15 | Authentication OMITTED from all steps. No placeholder auth objects. User configures after import. |
| Completeness | 15 | steps_structure matches steps, error workflow included, step naming convention followed, scripts extracted |

| Score | Tier | Meaning |
|-------|------|---------|
| 90-100 | Excellent | Imports on first try, all files created |
| 75-89 | Good | Minor property issues, imports after small fix |
| 60-74 | Partial | Structure correct but missing auth or wrong connector versions |
| <60 | Insufficient | Wrong format (API wrapper), bare values, won't import |

## Examples

### Use this skill when:
- "Create a Tray project that syncs orders from Salesforce to Slack every night"
- "Generate the JSON for a Tray workflow that processes webhooks from Shopify"
- "Build me a Tray project with a main workflow and error handler"
- "Scaffold a new integration under integrations/tray/Embedded/"

### Do NOT use this skill when:
- "Write a JavaScript transform for my Tray script step" — use [tray-script-generator](../tray-script-generator/SKILL.md)
- "How does Tray handle authentication?" — use [tray-expert](../tray-expert/SKILL.md)
- "Draw a diagram of this Tray workflow" — use [tray-diagrams](../tray-diagrams/SKILL.md)
- "Check if my Tray script is production-ready" — use [deploy-prep](../deploy-prep/SKILL.md)
