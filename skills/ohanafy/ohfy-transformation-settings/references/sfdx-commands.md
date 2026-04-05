# SFDX Commands Reference

All commands use the `sf` CLI (`@salesforce/cli`). Install: `npm install -g @salesforce/cli`

## Org Management

```bash
# List all authenticated orgs
sf org list --json

# Display details for a specific org
sf org display --target-org <alias> --json

# Authenticate new org (web browser)
sf org login web --alias <alias>

# Authenticate with JWT (CI/CD)
sf org login jwt --username <user> --jwt-key-file server.key --client-id <id> --alias <alias>
```

## Object & Field Metadata

```bash
# Describe an object (returns all field metadata)
sf sobject describe --sobject ohfy__Transformation_Setting__c --target-org <alias> --json

# List all objects in org
sf sobject list --target-org <alias> --json
```

## Metadata Retrieval (GlobalValueSet)

```bash
# Retrieve a GlobalValueSet (run from sfdx project directory)
sf project retrieve start \
  --metadata "GlobalValueSet:<value-set-name>" \
  --target-org <alias> \
  --json

# Example: retrieve the UOM GlobalValueSet
sf project retrieve start \
  --metadata "GlobalValueSet:ohfy__UOM" \
  --target-org myOrg \
  --json
```

Retrieved file location:
```
<project-dir>/force-app/main/default/globalValueSets/<value-set-name>.globalValueSet-meta.xml
```

## SOQL Queries

```bash
# Query transformation settings (all)
sf data query \
  --query "SELECT Id, ohfy__Key__c, ohfy__UOM__c, ohfy__Type__c, ohfy__Sub_Type__c FROM ohfy__Transformation_Setting__c" \
  --target-org <alias> \
  --json

# Query by sub-type
sf data query \
  --query "SELECT Id, ohfy__Key__c, ohfy__UOM__c, ohfy__Type__c, ohfy__Sub_Type__c, ohfy__Equal_To__c, ohfy__Active__c FROM ohfy__Transformation_Setting__c WHERE ohfy__Sub_Type__c = 'Beer' ORDER BY ohfy__Key__c" \
  --target-org <alias> \
  --json

# Count existing records
sf data query \
  --query "SELECT COUNT() FROM ohfy__Transformation_Setting__c WHERE ohfy__Sub_Type__c = 'Beer'" \
  --target-org <alias> \
  --json
```

## Data Import

```bash
# Import CSV via Bulk API (recommended for large sets)
sf data import bulk \
  --file transformation-settings-import.csv \
  --sobject ohfy__Transformation_Setting__c \
  --target-org <alias>

# Import via standard API (small sets)
sf data import legacy \
  --plan import-plan.json \
  --target-org <alias>
```

## Useful Flags

| Flag | Description |
|------|-------------|
| `--target-org <alias>` | Specify target org by alias or username |
| `--json` | Return machine-readable JSON output |
| `--api-version <version>` | Override API version (default: project sfdcLoginUrl) |
| `--wait <minutes>` | Wait for async operations |

## sfdx-project.json Template

Required for metadata retrieve operations:

```json
{
  "packageDirectories": [
    { "path": "force-app", "default": true }
  ],
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "59.0"
}
```

## GlobalValueSet XML Structure

Retrieved GlobalValueSet XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GlobalValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <customValue>
        <fullName>Case - 12x1 - 12oz - Can</fullName>
        <default>false</default>
        <isActive>true</isActive>
        <label>Case - 12x1 - 12oz - Can</label>
    </customValue>
    <!-- ... more values ... -->
</GlobalValueSet>
```
