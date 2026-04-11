---
name: kickoff
version: 1.0.0
description: |
  Guided workspace setup wizard. Asks what integration and which customer,
  then writes .context/workspace.md so downstream skills know the working
  context automatically.
  TRIGGER when: user says "kickoff", "start work", "new session", "set up
  context", or begins a session without clear context.
  DO NOT TRIGGER when: context is already established (branch matches
  dzeder/<customer>-* and .context/workspace.md exists and is fresh).
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

# Kickoff

Guided workspace setup wizard. Two questions, then you are ready to work.

## When This Skill Owns the Task

- Starting a new work session with no established context
- Switching to a different customer or integration mid-session
- User explicitly says "kickoff", "start work", or "set up context"
- Session begins and `.context/workspace.md` is missing or stale (>24h)

## Delegate Elsewhere

| Scenario | Route to |
|----------|----------|
| Already have context, need to connect an SF org | /org-connect |
| Want to brainstorm a new product idea | /office-hours |
| Want to resume previous work (have a checkpoint) | /checkpoint |
| Want to debug an issue | /investigate |

## Step 0: Check Existing Context

Before asking anything, check if context already exists:

1. Read `.context/workspace.md` (if it exists)
2. Check the current branch with `git branch --show-current`

If `.context/workspace.md` exists and was written today, AND the branch matches
the workspace customer/integration, present a summary:

> **Active workspace:** [customer] / [integration] on branch `dzeder/[branch]`
>
> Ready to continue? Or `/kickoff` again to change context.

If context is stale or missing, proceed to Step 1.

## Step 1: Integration — What Are You Working On?

Use AskUserQuestion:

**"What are you working on?"**

Options:
1. Existing integration
2. New integration
3. Not integration work (general task)

### Path A: Existing Integration

Discover integrations by scanning two sources:

**Project-level integrations:**
```bash
ls -d integrations/*/ 2>/dev/null | grep -v -E "(patterns|marketplace-ui|tray)/"
```

**Customer-level integrations** — parse each `customers/*/integrations.md` for
active integration entries (look for tables with integration names, methods, and
statuses).

Merge into a deduplicated list. Present as numbered options:

**"Which integration?"**

Example:
1. VIP SRS (integrations/vip-srs/) — SFTP-to-Salesforce, 9 file types
2. GP Analytics (Gulf) — Tray.io bidirectional sync
3. Fintech sync (Beverage Market) — Outbound customer number sync

After selection, read the integration's README.md or CLAUDE.md for context.

### Path B: New Integration

Ask the category:

**"What type of integration?"**

Options:
1. ERP / Accounting (QuickBooks, NetSuite, SAP, etc.)
2. Warehouse / Logistics (WMS, 3PL, shipping)
3. E-commerce (Shopify, WooCommerce, BigCommerce)
4. Data / Analytics (BI tools, data warehouse)
5. EDI (X12, AS2, VAN)
6. Beverage data (VIP, IRI, Nielsen, etc.)
7. Other external system

Then ask free-text:

**"What system are you integrating with? Give a name and brief description."**

Record the answers. Do NOT scaffold the integration project inline — that is a
separate task suggested in the hub menu.

### Path C: Not Integration Work

Ask:

**"What are you working on?"**

Options:
1. Customer debugging / support
2. Ohanafy package development
3. Infrastructure / DevOps
4. Documentation
5. Something else — let me describe it

## Step 2: Customer — Who Is This For?

Discover customers dynamically:

```bash
ls -d customers/*/ 2>/dev/null | grep -v _template | sed 's|customers/||;s|/||'
```

Read each customer's `profile.md` to get display names and tiers.

Use AskUserQuestion:

**"Which customer?"**

Options (dynamically built, example):
1. Gulf Distributing (Enterprise)
2. The Beverage Market (Sandbox)
3. Shipyard Brewing (Supplier)
4. New customer
5. No specific customer (internal / platform work)

### Path A: Existing Customer

Read their profile:
```bash
cat customers/<customer>/profile.md
```

Then ask about environment:

**"Which environment?"**

Options:
1. Production
2. Sandbox
3. Both
4. Not sure yet

### Path B: New Customer

Ask:

**"What type of company?"**

Options:
1. Supplier (brewery, winery, distillery)
2. Wholesaler / Distributor
3. Retailer
4. Other

Then ask for the customer name (free-text). Do NOT create the customer directory
inline — suggest it in the hub menu.

### Path C: No Specific Customer

Skip the environment question. Note `customer: internal` in workspace context.

## Step 3: Write Workspace Context

Create `.context/workspace.md` with collected information:

```markdown
---
created: YYYY-MM-DDTHH:MM:SS
customer: <customer-slug>
customer_display: <Customer Display Name>
integration: <integration-slug>
integration_type: existing | new
work_type: integration | debugging | package-dev | infra | docs | other
environment: production | sandbox | both | tbd
branch_suggestion: dzeder/<customer>-<integration>
---

# Active Workspace

## Customer: <Customer Display Name>
- **Profile:** customers/<customer>/profile.md
- **Integrations:** customers/<customer>/integrations.md
- **Environment:** <env>

## Integration: <integration name>
- **Source:** integrations/<integration>/ (or "new — not yet scaffolded")
- **Type:** <category>
- **Status:** <from integrations.md or "new">

## Loaded Context Files
- customers/<customer>/profile.md
- customers/<customer>/integrations.md
- integrations/<integration>/CLAUDE.md (if exists)
- integrations/<integration>/README.md (if exists)

## Suggested Branch
`dzeder/<customer>-<integration>`
```

Adjust the template based on what was collected — omit sections that don't apply
(e.g., no integration section for general work).

## Step 4: Hub Menu — What Next?

Present context-aware next steps. Use AskUserQuestion:

**"Workspace ready. What would you like to do next?"**

### Existing integration + existing customer:
1. `/org-connect` — Connect to [customer] [env] org
2. `/investigate` — Debug an issue with this integration
3. `/tray-expert` — Review or modify Tray workflows
4. Just start working

### New integration + existing customer:
1. `/org-connect` — Connect to [customer] [env] org
2. `/tray-expert` — Design the integration workflow
3. `/office-hours` — Think through the approach first
4. Just start working

### New integration + new customer:
1. Create customer directory from template
2. `/org-connect` — Connect to the new org
3. `/office-hours` — Think through the approach first
4. Just start working

### Not integration work:
1. `/investigate` — Debug an issue
2. `/health` — Code quality check
3. `/review` — Code review
4. Just start working

If the user selects a skill, invoke it. If they choose "just start working",
the workspace context is set and they can begin.

## Anti-Patterns

- Do NOT ask more than 4 questions total — this should take 30 seconds
- Do NOT create customer directories or integration scaffolds inline — suggest as next steps
- Do NOT overwrite a fresh workspace.md without confirming
- Do NOT skip the hub menu — funneling into the right next skill is the point
- Do NOT hardcode customer or integration lists — always scan dynamically

## Integration with Context Loading

This skill works WITH `.claude/rules/context-loading.md`, not replacing it:

1. Pre-populates `.context/workspace.md` so context-loading has a reliable source
2. Loads integration-specific context that context-loading does not cover
3. Sets up the branch naming so context-loading fires correctly on subsequent sessions

## Verification

After running:
- [ ] `.context/workspace.md` exists with valid YAML frontmatter
- [ ] Customer profile was read (if customer selected)
- [ ] Integration docs were read (if existing integration)
- [ ] Branch suggestion follows `dzeder/<customer>-<task>` convention
- [ ] Hub menu presented relevant next steps
