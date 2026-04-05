---
name: ohfy-data-model-expert
description: |
  Expert knowledge of the Ohanafy shared data model (OHFY-Data_Model). Apply when:
  - Understanding custom object schemas, relationships, and field definitions
  - Working with metadata-driven configuration tables
  - Mapping external system data to Ohanafy objects
  - Building SOQL queries against Ohanafy objects
  - Designing new custom objects or fields that integrate with the platform
  TRIGGER when: user asks about Ohanafy custom objects, field definitions,
  picklist values, object relationships, or data model design.
  Covers: 30+ custom objects spanning CRM, supply chain, retail, accounting,
  and integration tracking. Foundation for all other SKU packages.
---

# OHFY-Data_Model Expert Skill

## Source Repository

**Repo:** `Ohanafy/OHFY-Data_Model`
**Version:** 0.1.0
**Language:** JavaScript, CSS (metadata definitions + static resources)

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-Data_Model
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

```bash
if [ ! -d /tmp/ohfy-data-model ]; then
  gh repo clone Ohanafy/OHFY-Data_Model /tmp/ohfy-data-model -- --depth 1
fi
```

Then read the relevant metadata:
- Custom objects: `force-app/main/default/objects/`
- Custom fields: `force-app/main/default/objects/*/fields/`
- Value sets: `force-app/main/default/globalValueSets/`
- Custom metadata: `force-app/main/default/customMetadata/`

## Examples

- "What fields are on the Order__c object?" -- look up field definitions in the source index
- "How does Account_Route relate to Account and Delivery?" -- trace object relationships in the data model
- "I need to add a custom field for tracking ecom order source" -- check existing fields and advise on the right object

## Workflow

### 1. Check the source index for the object or field in question
### 2. Clone the repo if deeper field-level detail is needed
### 3. Review relationships and value sets for the relevant category
### 4. Advise on schema design or SOQL query patterns

## Key Object Categories

| Category | Objects | Purpose |
|----------|---------|---------|
| **Core CRM** | Account, Contact, Activity | Customer and relationship management |
| **Supply Chain** | Account_Route, Delivery, Depletion | Distribution and logistics |
| **Retail** | Display, Display_Run, Equipment | In-store execution |
| **Performance** | Goal, Goal_Template, Incentive | Performance management |
| **Financial** | Commitment, Credit, Fee | Financial tracking |
| **Accounting** | Adjustment, Allocation, Billback | Accounting operations |
| **Integration** | Integration_Sync_Failure | Integration error tracking |
| **Configuration** | Configuration_Preference, Accounting_Mapping | Metadata-driven settings |

## Usage Pattern

1. Clone the repo if not already available
2. Read the specific object definition for the area you're working on
3. Check field definitions for data types, required fields, and relationships
4. Reference value sets for valid picklist values
5. Check custom metadata for configuration-driven behavior

## Delegates To

- **ohfy-core-expert** — For trigger and service layer behavior on these objects
- **sf-metadata** — For general Salesforce metadata patterns
- **sf-soql** — For query optimization against these objects
