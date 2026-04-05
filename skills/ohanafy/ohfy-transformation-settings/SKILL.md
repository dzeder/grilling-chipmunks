---
name: ohfy-transformation-settings
description: >
  Interactive SFDX-connected workflow for creating Ohanafy `ohfy__Transformation_Setting__c`
  import CSVs. Connects to a live Salesforce org, discovers existing state, computes deltas,
  and produces only net-new transformation setting records. Use when onboarding new product
  sub-types or UOM combinations. Triggers on: "create transformation settings",
  "generate transformation settings CSV", "add transformation settings for [product]",
  "new product UOM settings", "onboard [sub-type] in Ohanafy".
  TRIGGER when: user asks to create, generate, or import transformation settings,
  onboard new product sub-types or UOM combinations, or produce net-new
  ohfy__Transformation_Setting__c CSV records.
---

# Ohanafy Transformation Settings Builder — SFDX Interactive Workflow

## Overview

`ohfy__Transformation_Setting__c` records define unit-of-measure conversion pairs used across
Ohanafy for inventory, ordering, and product management. Each row maps one UOM to its equivalent
value in a base UOM (`Fluid Ounce(s)` for volume, `Pound(s)` for weight).

This workflow connects to a live Salesforce org, queries existing state, computes deltas, and
generates only **net-new** records — never duplicating what already exists.

---

## Unified Key Format

Replaces the old v1/v2 variants entirely. All keys use this format:

| Type | Format | Example |
|------|--------|---------|
| Volume | `Fluid Ounce(s){UOM}` | `Fluid Ounce(s)Case - 12x1 - 12oz - Can` |
| Weight | `Weight{SubType}{UOM}Pound(s)` | `WeightBeerCase - 12x1 - 12oz - CanPound(s)` |

---

## 9-Step Workflow

### Step 1 — Connect to Salesforce Org

Ask the user for their target org alias or username.

```bash
python3 scripts/sfdx_connect.py --target-org <alias>
```

- Verifies `sf` CLI is installed
- Runs `sf org list` to find the org
- Confirms with `sf org display` (instanceUrl, username, connectedStatus)

**Gate**: Display org details. Ask user: "Is this the correct org? (yes/no)"

---

### Step 2 — Discover Field Mappings

```bash
python3 scripts/sfdx_describe_object.py --target-org <alias>
```

- Describes `ohfy__Transformation_Setting__c`
- Extracts metadata for all key fields
- **Auto-discovers the GlobalValueSet name** from `ohfy__UOM__c` field describe

**Gate**: Display field metadata table. Note the `global_value_set_name` from output — needed in Step 3.

---

### Step 3 — Query Existing UOM Picklist

Use the `global_value_set_name` from Step 2:

```bash
python3 scripts/sfdx_retrieve_globalvalueset.py \
  --target-org <alias> \
  --value-set-name <global_value_set_name> \
  --output /tmp/existing-uoms.json
```

- Creates temp `sfdx-project.json` in `/tmp/ohfy-uom-retrieve/`
- Retrieves GlobalValueSet via Metadata API
- Parses XML → JSON array of active picklist values

**Gate**: Show count of existing UOM values and a sample. Ask user to confirm before continuing.

---

### Step 4 — Confirm Mappings

Claude-orchestrated step — no script needed.

Display:
1. Key field metadata from Step 2
2. Existing UOM picklist values from Step 3
3. Available CONVERSIONS from `scripts/generate_transformation_settings.py`

Ask user:
- Which **sub-type(s)** to generate (e.g. `Beer`, `Wine`, `Spirits`)
- Which **UOM(s)** to include (or confirm "all available UOMs")

**Gate**: User confirms sub-type and UOM list before proceeding.

---

### Step 5 — Create Net-New UOM Subtypes File

```bash
python3 scripts/generate_net_new_uom.py \
  --existing /tmp/existing-uoms.json \
  --desired "Case - 12x1 - 12oz - Can" "Case - 12x1 - 16oz - Can" \
  --output /tmp/net-new-uoms.txt
```

- Compares desired UOMs against the existing GlobalValueSet
- Outputs only values not yet in Salesforce

**This is a manual-only step.** The user must add net-new values in Salesforce Setup:
`Setup → Picklist Value Sets → [GlobalValueSet name] → New`

**Gate**: Show net-new list. Confirm user has added them (or that the list is empty) before proceeding.

---

### Step 6 — Query Existing Transformation Settings

```bash
python3 scripts/sfdx_query_existing.py \
  --target-org <alias> \
  --sub-type "Beer" \
  --output /tmp/existing-settings.json
```

- SOQL query on `ohfy__Transformation_Setting__c`
- Filtered by sub-type (or all records if no filter)
- Outputs existing `ohfy__Key__c` values for delta computation

**Gate**: Show record count and a sample of existing keys. Ask user to confirm.

---

### Step 7 — Show Delta

```bash
python3 scripts/compute_delta.py \
  --existing /tmp/existing-settings.json \
  --desired-sub-type "Beer" \
  --output /tmp/delta.json
```

Uses unified key format to compute:
- `existing_matched` — records that already exist (will be skipped)
- `net_new` — records to be created
- `existing_mismatched_keys` — existing keys that don't match any expected pattern

Render result as a markdown delta table:

| Category | Count |
|----------|-------|
| Expected total | N |
| Already exists (skip) | N |
| Net-new to create | N |
| Unexpected existing keys | N |

**Gate**: User reviews delta and confirms net-new count before generating CSV.

---

### Step 8 — Create Import CSV

```bash
python3 scripts/generate_transformation_settings.py \
  --sub-type "Beer" \
  --uoms "Case - 12x1 - 12oz - Can" "Case - 12x1 - 16oz - Can" \
  --existing-keys-file /tmp/delta.json \
  --output /tmp/beer-transformation-settings-net-new.csv
```

- Generates only net-new records (existing keys excluded)
- Uses unified key format
- Output CSV has 9 columns, all quoted

Column order:
```
"_","ohfy__Equal_To_UOM__c","ohfy__Measurement_System__c","ohfy__Sub_Type__c","ohfy__Type__c","ohfy__UOM__c","ohfy__Active__c","ohfy__Equal_To__c","ohfy__Key__c"
```

**Gate**: Show row count and sample rows. Ask user to review before import.

---

### Step 9 — Validate

Claude-orchestrated checklist before handing off the CSV:

- [ ] Row count = (number of net-new UOMs) × 2
- [ ] All UOM picklist values exist in GlobalValueSet (from Step 3)
- [ ] Every UOM has exactly 2 rows (1 Volume + 1 Weight)
- [ ] All `ohfy__Sub_Type__c` values match user-supplied sub-type
- [ ] All keys use unified format (not v1/v2)
- [ ] Column `ohfy__Transformation_Math__c` is **not** present

---

## Quick Reference: All Scripts

| Script | Purpose | Step |
|--------|---------|------|
| `scripts/sfdx_connect.py` | Verify sf CLI, confirm target org | 1 |
| `scripts/sfdx_describe_object.py` | Describe object, discover GlobalValueSet name | 2 |
| `scripts/sfdx_retrieve_globalvalueset.py` | Retrieve GlobalValueSet XML → JSON | 3 |
| `scripts/generate_net_new_uom.py` | Compute net-new UOM picklist values | 5 |
| `scripts/sfdx_query_existing.py` | SOQL query existing records | 6 |
| `scripts/compute_delta.py` | Compare expected vs existing | 7 |
| `scripts/generate_transformation_settings.py` | Write net-new import CSV | 8 |

## Reference Files

- **`references/uom-conversions.md`** — UOM → fl oz and lb equivalents, measurement system
- **`references/sfdx-commands.md`** — All `sf` CLI commands used in this workflow

## Delegation

- **ohfy-data-model-expert** — For questions about the `ohfy__Transformation_Setting__c` object schema or related objects
- **ohfy-core-expert** — For trigger framework behavior when records are inserted
- **org-connect** — For connecting to the target Salesforce org if not already authenticated
- **sf-deploy** — For deploying metadata changes (e.g., new GlobalValueSet values via metadata API)
- Do not trigger this skill for general UOM questions that do not involve creating transformation setting records

## Examples

- "Create transformation settings for Beer sub-type with Case - 12x1 - 12oz - Can UOMs"
- "Generate a net-new transformation settings CSV for the Wine sub-type on the Gulf production org"
- "Onboard Spirits UOMs — we need volume and weight conversions for all new case sizes"

## Prerequisites

```bash
# Install sf CLI
npm install -g @salesforce/cli

# Authenticate org
sf org login web --alias <alias>

# Verify
sf org display --target-org <alias> --json
```
