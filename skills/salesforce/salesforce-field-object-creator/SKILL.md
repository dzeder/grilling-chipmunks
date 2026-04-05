---
name: salesforce-field-object-creator
description: >
  Generate production-ready Tray workflow scripts for creating Salesforce custom objects and fields
  from CSV specifications. Supports all 28 Salesforce field types with interactive setup for complex
  fields (Formula, Lookup, MasterDetail, Summary, Picklist). Based on MCBC Salsify and MCBC Shelf
  Execution production patterns. TRIGGER when: user provides a CSV with field specs and asks to
  generate Tray scripts, needs to automate SF custom object/field creation via Tray.io, or
  references MCBC Salsify/Shelf Execution metadata patterns.
---

# Salesforce Field & Object Creator Skill

**Version**: 1.0.0
**Last Updated**: 2025-12-19
**Purpose**: Generate production-ready Tray workflow scripts for creating Salesforce custom objects and fields from CSV specifications

## Skill Overview

This skill parses CSV field specifications and generates three production-ready Tray workflow scripts that use the Salesforce Metadata API to create custom objects and fields. All patterns are based on working production code from MCBC Salsify and MCBC Shelf Execution integrations.

## When To Use This Skill

Use this skill when the user:
- Provides a CSV file with Salesforce field specifications and asks to generate Tray scripts
- Says something like "create Salesforce fields from this CSV" or "generate metadata scripts"
- Needs to automate Salesforce custom object or field creation via Tray.io workflows
- References MCBC Salsify, MCBC Shelf Execution, or similar SF metadata patterns

## Delegation

- **sf-metadata** — For creating metadata XML directly (without Tray workflow scripts)
- **sf-deploy** — For deploying the generated metadata to Salesforce orgs
- **tray-expert** — For general Tray.io workflow design questions beyond field/object creation
- **salesforce-composite** — For composite API-based metadata operations
- Do not trigger for manual Salesforce Setup UI field creation or Apex-based schema changes

## Core Capabilities

### 1. Complete Field Type Coverage (28 Types)

| Category | Types |
|----------|-------|
| Basic Text & Data | Text, TextArea, LongTextArea, Html, EncryptedText, Email, Phone, Url |
| Numeric & Financial | Number, Currency, Percent |
| Date & Time | Date, DateTime, Time |
| Selection & Boolean | Checkbox, Picklist, MultiselectPicklist |
| Relationships | Lookup, MasterDetail, Hierarchy, ExternalLookup, IndirectLookup |
| Calculated | Formula, Summary (Roll-Up) |
| Special/Advanced | AutoNumber, Location |

Full metadata specs for each type: `references/field-types/`

### 2. Field Categorization: Simple vs. Complex

**Simple fields** — fully configurable via CSV columns, no prompts needed:
Text, TextArea, LongTextArea, Html, EncryptedText, Email, Phone, Url, Number, Currency, Percent, Date, DateTime, Time, Checkbox, AutoNumber, Location

**Complex fields** — require interactive prompts:
Formula, Lookup, MasterDetail, Hierarchy, ExternalLookup, IndirectLookup, Picklist, MultiselectPicklist, Summary

Interactive prompt details: `references/interactive-prompts/`

### 3. Three Generated Scripts

| Script | Purpose | Typical Size |
|--------|---------|-------------|
| `1-define_objects_and_fields/script.js` | Build SOAP XML for Metadata API create | 850–950 lines |
| `2-extract_jobids/script.js` | Parse create response, extract async job IDs | 75–100 lines |
| `3-evaluate_statuses/script.js` | Poll job status, classify errors (acceptable vs. fatal) | 150–200 lines |

Script templates and I/O structures: `references/workflow-scripts/`

## CSV Format — Quick Reference

### Required Columns (All Fields)

| Column | Description | Example |
|--------|-------------|---------|
| `Object` | Object API name | `Mandate__c`, `Account` |
| `Field_Label` | Human-readable label (max 40 chars) | `Activity Name` |
| `API_Name` | Field API name (max 40 chars excl. `__c`) | `Activity_Name__c` |
| `Type` | One of 28 valid types (case-insensitive) | `Text`, `MasterDetail` |
| `Notes` | Description or configuration hints | `From activity_name field` |

### Optional Columns (Simple Fields)

| Column | Applies To | Example |
|--------|-----------|---------|
| `Length` | Text, TextArea, LongTextArea, EncryptedText, Html | `255` |
| `Precision` | Number, Currency, Percent | `18` |
| `Scale` | Number, Currency, Percent, Location | `2` |
| `Required` | All types | `true` |
| `Unique` | Text, Email, Number, Phone, Url | `true` |
| `ExternalId` | Text, Email, Number | `false` |
| `DefaultValue` | Text, Number, Currency, Percent, Checkbox, Date, DateTime | `0` |
| `VisibleLines` | LongTextArea, Html, MultiselectPicklist | `3` |
| `MaskChar` | EncryptedText | `asterisk` |
| `MaskType` | EncryptedText | `all`, `lastFour`, `creditCard` |

Full CSV spec and examples: `references/csv-format/`

### Complex Field Notes Conventions

Signal complex field config in the Notes column to guide interactive setup:

```
Mandate__c,Total Quantity,Total_Quantity__c,Summary,"Interactive: SUM Mandate_Item__c.Quantity_Fulfilled__c"
Mandate_Item__c,Mandate,Mandate__c,MasterDetail,"Interactive: Link to Mandate__c (parent)"
Contact,Full Name,Full_Name__c,Formula,"Interactive: FirstName & LastName"
ohfy__Item__c,Container Type,Container_Type__c,Picklist,"Interactive: BOTTLE, CAN, KEG"
```

## 7-Step Interactive Workflow

| Step | Action | Confirmation Gate |
|------|--------|-----------------|
| 1 | Parse CSV, validate structure, categorize simple/complex fields | Show counts, flag errors |
| 2 | Display unique objects, confirm API names and labels | User confirms object definitions |
| 3 | Display simple fields with full configuration | User bulk-approves simple fields |
| 4 | Interactive prompts for each complex field | User provides config per field |
| 5 | Final summary: object counts, field counts, script file paths | User confirms script generation |
| 6 | Generate all 3 scripts + supporting files | Report line counts and paths |
| 7 | Deliver validation checklist and deployment steps | — |

### Interactive Prompts by Field Type

| Type | Questions Asked |
|------|----------------|
| Formula | Expression, return type, blank handling, decimal places (if numeric) |
| Lookup | Related object, relationship name, delete constraint (SetNull/Restrict/Cascade) |
| MasterDetail | Parent object, relationship name, allow reparenting |
| Summary | Child object, field to aggregate, operation (SUM/COUNT/MIN/MAX), filter (optional) |
| Picklist / MultiselectPicklist | Values (comma-sep), sorted, restricted, default, controlling field (optional) |
| Hierarchy | Relationship name (User object only) |
| ExternalLookup | External object (ends `__x`), relationship name |
| IndirectLookup | Related object, relationship name, external ID field on parent |

Detailed prompt examples with scenarios: `references/interactive-prompts/`

## Generated Output Structure

```
90_[ObjectName]_Custom_Objects/
├── workflow-metadata.json
├── 1-define_objects_and_fields/
│   ├── script.js
│   ├── input.json
│   ├── metadata.json
│   └── package.json
├── 2-extract_jobids/
│   ├── script.js
│   └── metadata.json
└── 3-evaluate_statuses/
    ├── script.js
    └── metadata.json
```

### Script Code Pattern (All 3 Scripts)

```javascript
// Constants at top
const CONFIG = {
    SALESFORCE_API_VERSION: 'v61.0',
    ACCEPTABLE_ERROR_CODES: ['DUPLICATE_DEVELOPER_NAME']
};

// Orchestration-only exports.step
exports.step = function({csv_data, namespace_prefix, complex_field_configs}, fileInput) {
    const validated = validateInput(csv_data);
    const objects = extractObjects(validated);
    const metadata = buildMetadataXml(objects, validated, namespace_prefix, complex_field_configs);
    return formatOutput(metadata);
};

// ALL helpers defined below exports.step — no inline function definitions
function validateInput(csv_data) { /* ... */ }
function buildMetadataXml(objects, fields, namespace_prefix, configs) { /* ... */ }
```

**Rules**: Pure functions, no side effects, no import/require except pre-installed libraries (lodash, moment-timezone, crypto, Buffer, URL).

## Field Type Selection Quick Guide

| Situation | Use |
|-----------|-----|
| Single-line text, max 255 chars | Text |
| Multi-line text, max 255 chars | TextArea |
| Long descriptions / comments | LongTextArea |
| Rich text with HTML formatting | Html |
| Monetary values with currency symbol | Currency |
| Percentages (0.15 displays as 15%) | Percent |
| Date only, no time | Date |
| Date AND time | DateTime |
| Optional relationship, independent lifecycle | Lookup |
| Required relationship, child inherits parent security | MasterDetail |
| Calculation on same record's fields | Formula |
| Aggregation across child records | Summary |
| Single selection from list | Picklist |
| Multiple selections from list | MultiselectPicklist |
| Self-referential on User object | Hierarchy |

## Error Classification

| Error Code | Severity | Handling |
|-----------|----------|---------|
| `DUPLICATE_DEVELOPER_NAME` | Acceptable (non-fatal) | Script continues; field already exists |
| `FIELD_INTEGRITY_EXCEPTION` | Fatal | Create parent object first |
| `INVALID_FIELD_TYPE` | Fatal | Review field type metadata in `references/field-types/` |
| `EXCEEDED_MAX_LENGTH` | Fatal | Shorten label/API_Name (max 40 chars) in CSV |
| `INSUFFICIENT_ACCESS` | Fatal | Grant "Modify All Data" / "Manage Metadata" permissions |
| `ENTITY_IS_LOCKED` | Retryable | Wait and retry after current metadata operation completes |

## Reference Files

| Directory | Files | Contents |
|-----------|-------|---------|
| `references/field-types/` | basic-text-data.md, numeric-financial.md, date-time.md, selection-boolean.md, relationships.md, calculated.md, special-advanced.md | Complete metadata properties for all 28 field types |
| `references/csv-format/` | csv-specification.md, csv-examples.md | Full CSV spec, validation rules, 10 example CSVs |
| `references/interactive-prompts/` | formula-field-setup.md, lookup-field-setup.md, picklist-field-setup.md, rollup-field-setup.md | Step-by-step prompt examples for all complex field types |
| `references/workflow-scripts/` | 1-define-objects-and-fields.md, 2-extract-jobids.md, 3-evaluate-statuses.md | Complete script templates with I/O structures |

## Production Source References

**MCBC Salsify Integration**:
- `Embedded/MCBC_Salsify_SANDBOX/.../91_MCBC_Salsify_Custom_Fields/1-define_fields/script.js`
- 925 lines, 63 fields across 3 objects, all 28 field types

**MCBC Shelf Execution Integration**:
- `Embedded/MCBC_Shelf_Execution_PRODUCTION/.../90_MCBC_Shelf_Execution_Custom_Objects/`
- Full 3-script define/extract/evaluate pattern with async job polling

---

**Maintained By**: Derek Squires / Ohanafy Integration Team
**Production Status**: Based on working MCBC Salsify and MCBC Shelf Execution code
