# Quickstart: Common Workflows

Four workflows you'll use most. Each tells the agent what to do — just describe your task and the right skills activate automatically.

---

## 1. Add a New Customer

```bash
# 1. Create customer directory from template
cp -r customers/_template customers/<customer-name>

# 2. Connect to their Salesforce org
bash scripts/connect-org.sh <customer-name> --production --type customer

# 3. Edit the profile with org topology, SKUs, external systems
#    The agent will populate this interactively if you describe the customer
```

**Key files to populate:**
- `customers/<name>/profile.md` — org topology, installed SKUs, data profile
- `customers/<name>/integrations.md` — external systems, sync schedules
- `customers/<name>/known-issues.md` — gotchas and workarounds

**Skills that activate:** `org-connect`, `ohfy-*-expert` (based on SKUs)

---

## 2. Build a Tray Integration

```
"Build a Tray integration that syncs orders from <source> to Salesforce for <customer>"
```

The agent will:
1. Check existing Tray workflows (Tray-First Rule — never duplicate)
2. Load integration patterns from `integrations/patterns/`
3. Follow the master guide (`docs/integration-guides/OHFY_INTEGRATION_MASTER_GUIDE.md`)
4. Use `script-scaffold.js` as the starting template
5. Apply validate → transform → batch → output flow

**Key references:**
- `integrations/patterns/` — 11 reusable JS modules
- `docs/integration-guides/OHFY_BUSINESS_LOGIC_LIBRARY.md` — field validation rules
- `docs/integration-guides/CONSOLIDATED_SCENARIO_EXAMPLES.md` — real examples

**Skills that activate:** `tray-expert`, `tray-script-generator`, `salesforce-composite`, `csv-output`

---

## 3. Debug a Customer Issue

```
"Customer <name> is seeing <error> when <action> — investigate"
```

The agent will automatically:
1. Load customer profile (`customers/<name>/profile.md`)
2. Load the relevant package source index (e.g., `ohfy-oms-expert` for order issues)
3. Check known issues (`customers/<name>/known-issues.md`)
4. Connect to the org if needed (`sf org list` to check)
5. Read triggers, validation rules, and flows for the affected object

**Context Loading Protocol** (automatic based on keywords):
- Customer name in branch/task → loads customer profile
- Package name (OMS, WMS, REX, etc.) → loads source index
- Error/bug/failing → loads both customer profile AND source index

**Skills that activate:** `investigate`, `ohfy-*-expert`, `org-connect`, `sf-debug`

---

## 4. Build a Salesforce Component

```
"Build an LWC that displays <data> on the <object> record page"
```

The agent will:
1. Check the customer's org metadata (if customer-specific)
2. Load the relevant source index for existing patterns
3. Follow SLDS, wire adapters, LMS conventions
4. Generate Apex controller + LWC + test classes

**Key conventions:**
- Apex: bulkify, check FLS/CRUD, service layer pattern
- LWC: SLDS design system, wire adapters, LMS for cross-component
- Tests: 85%+ coverage target, meaningful assertions
- Deploy: `sf-deploy` skill handles scratch org → sandbox → prod pipeline

**Skills that activate:** `sf-lwc`, `sf-apex`, `sf-metadata`, `sf-testing`, `sf-deploy`

---

## Prerequisites

Before any real work, ensure:

```bash
# Health check — verifies all dependencies and credentials
bash scripts/doctor.sh

# Verify source indexes are fresh (should be <7 days old)
cat references/last-synced.txt

# Check connected orgs
sf org list
```

## Skill Activation

You don't need to invoke skills manually. Describe your task naturally and the right skills activate based on keywords, file patterns, and context. See `docs/SKILL_ROUTING_MATRIX.md` for the full routing table.
