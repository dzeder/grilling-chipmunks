# The Ozone — Ohanafy Internal Salesforce Org

Ohanafy's internal Salesforce org. Tracks all projects, milestones, work items, tasks, customers, and updates.
Visible to C-suite, investors, and customers — treat all writes with care.

## Connection

- **Alias:** `ozone`
- **Org ID:** `00D8b000002BiUsEAK`
- **User:** `daniel@ohanafy.com`

## Key Custom Objects

| Object | Label | Key Prefix | Parent |
|--------|-------|------------|--------|
| `Project__c` | Project | `a3f` | — |
| `Milestone__c` | Milestone | `a3c` | `Project__c` (via `Project__c` field) |
| `Work_Item__c` | Work Item | `a3k` | `Milestone__c` (via `Milestone__c` field) |
| `Project_Item__c` | Project Item | — | `Project__c` (via `Project__c` field) |

## Quick Commands

```bash
# List projects
sf data query --query "SELECT Id, Name, Project_Stage__c, Project_Status__c FROM Project__c ORDER BY Name" --target-org ozone

# Milestones for a project
sf data query --query "SELECT Id, Name, Phase__c, Status__c, Sort_Order__c FROM Milestone__c WHERE Project__c = '<ID>' ORDER BY Sort_Order__c" --target-org ozone

# Work items for a milestone
sf data query --query "SELECT Id, Name, Status__c, Priority__c FROM Work_Item__c WHERE Milestone__c = '<ID>' ORDER BY Sort_Order__c, Name" --target-org ozone
```

## Rules

- **No metadata pulls** unless Daniel explicitly requests it
- Confirm before any write operations — this is a production org with executive visibility
- Read operations (SOQL queries) are always safe
