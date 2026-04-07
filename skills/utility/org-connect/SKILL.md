---
name: org-connect
description: |
  Connect to a Salesforce org, retrieve metadata, and generate an org snapshot.
  TRIGGER when:
  - User wants to connect to a Salesforce org for debugging
  - User asks about what's deployed in an org
  - User needs to understand org state (triggers, flows, validation rules)
  - User wants to debug API errors against a live org
  - User says "connect to ohanafy", "connect to [customer] org", "pull down [org]"
  DO NOT TRIGGER when:
  - User is working purely with source code (use ohfy-* SKU skills instead)
  - User is asking about Salesforce concepts generically (use sf-* skills)
---

# Org Connect Skill

Connect to a live Salesforce org, retrieve all metadata, detect installed Ohanafy packages, and generate a snapshot for debugging and analysis.

## Quick Start

### Connect to a new org
```bash
bash scripts/connect-org.sh <customer-name> [--sandbox|--production] [--type customer|template|sandbox]
```

Examples:
```bash
bash scripts/connect-org.sh gulf --production --type customer
bash scripts/connect-org.sh ohanafy --sandbox --type sandbox
bash scripts/connect-org.sh snb-hubs --sandbox --type customer
```

### Check already-connected orgs
```bash
sf org list
```

### Re-retrieve latest metadata from a connected org
```bash
sf project retrieve start --target-org <alias> --manifest ./package.xml
```

## CRITICAL: Read-Only Operations Only

Customer orgs are **read-only by default**. Do not write to any customer org unless the user explicitly authorizes it in the current conversation.

**Allowed operations:**
- `sf org list` — check connected orgs
- `sf project retrieve start` — pull metadata down
- `sf data query` — read data via SOQL
- `sf org display` — view org info
- `sf org open` — open org in browser

**Prohibited operations (unless user explicitly authorizes):**
- `sf project deploy start` — deploy metadata
- `sf data update record` / `sf data create record` / `sf data delete record` — any DML
- `sf apex run` — anonymous Apex that modifies data
- Any destructive metadata operations (delete components, overwrite configs)

## What the Script Does

1. **Creates project directory** under `customers/<name>/orgs/<env>/`
2. **Authenticates** via browser login (or reuses existing auth)
3. **Generates manifest** from the org with wildcard retrieval for critical types
4. **Retrieves all metadata** — Apex, triggers, flows, objects, fields, validation rules, LWC, etc.
5. **Detects installed OHFY packages** — scans for OMS, WMS, REX, Ecom, Payments, etc.
6. **Generates org-snapshot.md** — metadata summary with counts, object details, quick commands

## Using the Snapshot

After connecting, read `customers/<name>/orgs/<env>/org-snapshot.md` for a quick overview:
- What's deployed (counts of classes, triggers, flows, etc.)
- Which OHFY SKU packages are installed
- Per-object field and validation rule counts
- Quick commands for testing and querying

## Customer Context

Before diving into metadata, read the customer profile for context:
```bash
cat customers/<name>/profile.md
```
This tells you their installed SKUs, org topology, data profile, external systems, and any migration history. When you learn something new about a customer during debugging, write it to their `customers/<name>/notes.md`.

## Debugging Workflow

When a user reports an issue (e.g., "orders are failing on Gulf prod"):

### Step 0: Read the customer profile
```bash
cat customers/gulf/profile.md
```

### Step 1: Check if org is connected
```bash
sf org list | grep gulf
```

### Step 2: Read the snapshot
Read `customers/gulf/orgs/production/org-snapshot.md` for context on what's deployed.

### Step 3: Read relevant metadata
Based on the error, read the specific metadata:

**Validation rule errors:**
```bash
# Find validation rules on the object
find customers/gulf/orgs/production/force-app -path "*Order__c/validationRules*" -name "*.xml"
```

**Trigger errors:**
```bash
# Read triggers for the object
find customers/gulf/orgs/production/force-app -name "*.trigger" | grep -i order
```

**Flow errors:**
```bash
# Find record-triggered flows
find customers/gulf/orgs/production/force-app -name "*.flow-meta.xml" | grep -i order
```

### Step 4: Cross-reference with SKU skills
Use the relevant `ohfy-*-expert` skill to understand the expected behavior, then compare with what's actually deployed.

### Step 5: Refresh if stale
If the snapshot might be outdated:
```bash
cd customers/gulf/orgs/production
sf project retrieve start --target-org gulf-production --manifest ./package.xml
```

## Connecting SKU Skills to Live Orgs

The `ohfy-*-expert` skills reference GitHub source (what should be deployed). This skill gives you the live org (what is actually deployed). Use both together:

| Need | Use |
|------|-----|
| "What does the OMS code do?" | `ohfy-oms-expert` (clones from GitHub) |
| "What's deployed in Gulf prod?" | `org-connect` (reads from live org) |
| "Why is this order failing?" | Both — compare expected vs actual |
| "What validation rules are active?" | `org-connect` (read from retrieved metadata) |
| "How does the trigger framework work?" | `ohfy-core-expert` (design patterns) |

## Org Directory Structure

After connecting:
```
customers/gulf/orgs/production/
├── sfdx-project.json
├── package.xml
├── org-snapshot.md          # Generated summary
└── force-app/main/default/
    ├── classes/              # All Apex classes
    ├── triggers/             # All Apex triggers
    ├── flows/                # All Flow definitions
    ├── objects/              # Objects with fields + validation rules
    ├── lwc/                  # Lightning Web Components
    ├── layouts/              # Page layouts
    ├── profiles/             # Profiles
    ├── permissionsets/       # Permission sets
    └── ...
```
