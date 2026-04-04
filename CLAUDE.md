# Daniel's Ohanafy Monorepo

Unified skills, agents, patterns, and projects for Ohanafy development.

## gstack skills (workflow layer)

Use `/browse` for all web browsing. Never use `mcp__claude-in-chrome__*` tools when `/browse` is available.

Available gstack skills: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/design-consultation`, `/design-shotgun`, `/design-html`, `/review`, `/ship`, `/land-and-deploy`, `/canary`, `/benchmark`, `/browse`, `/connect-chrome`, `/qa`, `/qa-only`, `/design-review`, `/setup-browser-cookies`, `/setup-deploy`, `/retro`, `/investigate`, `/document-release`, `/codex`, `/autoplan`, `/careful`, `/freeze`, `/guard`, `/unfreeze`, `/learn`, `/checkpoint`, `/cso`, `/gstack`, `/gstack-upgrade`, `/health`.

## Salesforce skills (domain layer)

33 Salesforce-specific skills in `skills/sf-*`. Activate based on file patterns:
- `.cls`, `.trigger` -> sf-apex
- `.flow-meta.xml` -> sf-flow
- `/lwc/**/*.js`, `.html` -> sf-lwc
- `.soql` -> sf-soql
- `.agent` -> sf-ai-agentscript
- `.object-meta.xml`, `.field-meta.xml` -> sf-metadata
- `.namedCredential-meta.xml` -> sf-integration

## Ohanafy SKU expert skills (product layer)

Each SKU skill has a pre-built source index (`references/source-index.md`) with:
- Apex classes, triggers, service methods, custom objects & fields, LWC components
- **Trigger → Handler Map** (which triggers fire on which objects, what handlers they call)
- **Service Layer Graph** (one level deep, direct calls/instantiations)
- **Cross-Object Relationships** (lookup and master-detail relationships)
- **Common Patterns** (trigger bypass, service locator, batch/schedulable, queueable, platform events)
- **Test Coverage Summary** (production vs test class ratio, untested classes)

Check `references/last-synced.txt` — if stale (>7 days), refresh with `bash scripts/sync-ohanafy-index.sh --repo REPO`. Clone-on-demand remains as a deep dive fallback. Use `--discover` to find new repos in the Ohanafy org.

| Skill | Ohanafy Repo(s) | Domain |
|-------|-----------------|--------|
| **ohfy-core-expert** | OHFY-Core | Triggers, services, bypass patterns, 143 objects |
| **ohfy-data-model-expert** | OHFY-Data_Model | 30+ custom objects, field schemas, value sets |
| **ohfy-platform-expert** | OHFY-Platform | Shared platform services across all SKUs |
| **ohfy-oms-expert** | OHFY-OMS + OHFY-OMS-UI | Order management, fulfillment |
| **ohfy-wms-expert** | OHFY-WMS + OHFY-WMS-UI | Warehouse ops, inventory, picking/packing |
| **ohfy-rex-expert** | OHFY-REX + OHFY-REX-UI | Retail excellence, POS, displays |
| **ohfy-ecom-expert** | OHFY-Ecom | E-commerce, Shopify/WooCommerce |
| **ohfy-payments-expert** | OHFY-Payments | Payment processing, settlement |
| **ohfy-edi-expert** | OHFY-EDI | X12 850/810/856, B2B interchange |
| **ohfy-configure-expert** | OHFY-Configure | System config, feature flags, setup |

Source sync roadmap: `docs/ohanafy-source-sync-roadmap.md`

## Integration skills (Tray / Ohanafy platform)

13 integration-specific skills in `skills/`:
- **tray-expert** — Tray.io platform expert (Q&A, workflow design, integration audit, architecture)
- **tray-embedded-customjs** — Custom JS patterns for Tray Embedded config wizards
- **tray-errors** — Tray error handling protocols
- **tray-diagrams** — Workflow visualization with Mermaid
- **tray-insights** — Project usage metrics and analytics
- **tray-script-generator** — Script scaffolding from production patterns
- **csv-output** — CSV formatting patterns
- **salesforce-composite** — SF Composite API patterns
- **salesforce-field-object-creator** — Field/object definition utilities
- **ohfy-transformation-settings** — Transformation rule configuration
- **deploy-prep** — Deployment workflow preparation
- **test-script** — Script testing infrastructure
- **security** — Integration security patterns

## Domain skills (UKG / ERP)

- **ukg-expert** — UKG API, data model, authentication, scheduling
- **ukg-api-debug** — UKG API debugging and troubleshooting
- **ukg-field-mapper** — UKG-to-Ohanafy field mapping

## Utility skills

- **org-connect** — Connect to live Salesforce orgs for debugging and metadata retrieval
- **claude-code-best-practices** — Skill/agent authoring patterns and monorepo organization
- **github-agent** — GitHub Actions health audit, CI/CD best practices, repo configuration review

## Agents

17 specialist agents in `agents/`:

**Salesforce / FDE Team:**
- **fde-strategist** — Planning and delegation (read-only, spawns other agents)
- **fde-engineer** — Agentforce implementation (Apex, Agent Scripts, metadata)
- **fde-qa-engineer** — Test execution, debug logs, observability
- **fde-release-engineer** — Deployment, Connected Apps, CI/CD
- **fde-experience-specialist** — Conversation design, persona, LWC UI

**Professional Services:**
- **ps-technical-architect** — Backend Apex, integrations, data modeling
- **ps-solution-architect** — Metadata design, Flows, security, architecture docs

**Integration Team:**
- **salesforce-integration-architect** — SF Composite API, Named Credentials, platform events
- **edi-processing-specialist** — EDI X12 (850/810/856), OpenText, Transcepta
- **tray-script-generator** — Tray script creation from patterns
- **tray-script-tester** — Tray script validation and testing
- **ohanafy-data-model** — Ohanafy object model, relationships, field usage
- **domain-specialist-designer** — Domain-specific integration design
- **progressive-disclosure-executor** — Phased implementation approach

**Domain:**
- **beverage-erp-expert** — Beverage distribution (VIP, Encompass, DSD, three-tier)

**Support:**
- **documentation-consolidation-specialist** — Doc organization and consolidation
- **integration-guide-curator** — Integration guide maintenance

## Integration patterns

11 production-tested JS modules in `integrations/patterns/`:
- `soql-query-builder.js` — SELECT/WHERE builder, IN operator, 2000-value chunking
- `batch-processing.js` — Array chunking, groupBy, dedup, SF Composite batches
- `data-mapping.js` — Field rules engine with AND/OR logic, multi-priority resolution
- `error-handling.js` — SF Composite error extraction, SOAP fault handling
- `validation.js` — Required fields, type/length/format checks
- `string-manipulation.js` — Business name normalization, SOQL sanitization
- `csv-output.js` — Fixed-width formatters, CSV generation
- `date-time.js` — SF date formats, timezone conversion (no external libs)
- `lookup-maps.js` — Map/Set factories, status mapper, partitioning
- `output-structuring.js` — Success/error envelopes, summaries
- `script-scaffold.js` — Full validate-transform-batch-output starter

## Integration reference docs

In `docs/integration-guides/`:
- `OHFY_BUSINESS_LOGIC_LIBRARY.md` — Order processing, validation, field mappings, rollups
- `ORG_CONFIGURATION_MATRIX.md` — Multi-org setup, environment management, feature flags
- `TRAY_CONNECTOR_OPERATIONS.md` — Connector reference, operation types, error handling
- `OHFY_INTEGRATION_MASTER_GUIDE.md` — End-to-end integration methodology
- `CONSOLIDATED_SCENARIO_EXAMPLES.md` — Real integration workflows and examples
- `SCRIPT_CONSOLIDATION_PATTERNS.md` — Refactoring and consolidation strategies
- `Tray-AI-Project-JSON-Structure-Guide.md` — Tray export JSON schema breakdown

## Claude Code Best Practices (reference layer)

Vendored from [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice). Consult before creating/modifying skills, agents, or CLAUDE.md.

Key references in `references/claude-code-best-practices/`:
- `best-practice/claude-skills.md` — Skill authoring patterns
- `best-practice/claude-subagents.md` — Subagent design
- `best-practice/claude-commands.md` — Command patterns
- `reports/claude-skills-for-larger-mono-repos.md` — Monorepo skill organization

Update: `bash scripts/update-best-practices.sh` (also checked weekly via GitHub Action)

## Project structure

```
projects/
  ohanafy-core/           # Main Salesforce org
  netsuite-ohanafy/       # NetSuite integration
  qbo-ohanafy/            # QuickBooks Online integration
  xero-ohanafy/           # Xero integration
  rehrig-ohanafy/         # Rehrig integration

customers/
  _template/              # Copy to create a new customer
  gulf/                   # Gulf Distributing
    profile.md            # Org topology, SKUs, data profile, external systems
    orgs/                 # Per-environment metadata (populated by connect-org.sh)
      production/
      cam-sandbox/
```

`projects/` = shared technical work (integrations, reports, LWC).
`customers/` = per-customer Salesforce/Ohanafy configurations and knowledge.

## Conventions

- Salesforce CLI: use `sf` (never `sfdx`)
- API version: v62.0+ (never below v56.0)
- Apex: bulkify everything, check FLS/CRUD, use service layer pattern
- Flows: follow naming conventions in sf-flow skill
- LWC: use SLDS, wire adapters, LMS for cross-component communication
- Tests: 85%+ Apex coverage target, meaningful assertions
- Tray scripts: use patterns from `integrations/patterns/`, follow validate-transform-batch-output flow
- Integration scripts: always use `script-scaffold.js` as starting template

## Hooks

PostToolUse validators auto-run on file writes (Apex LSP, Flow validation, LWC linting, metadata checks). These are advisory — they warn but don't block.

## Improving skills

When a skill gives bad advice or misses something, fix it directly:
1. Edit the skill file in `skills/<skill-name>/SKILL.md`
2. Commit with the project change that revealed the gap
3. The improvement is live immediately for all future work

Templates and quality tools:
- **Skill template:** `docs/SKILL_TEMPLATE.md` — required structure for all SKILL.md files
- **Agent template:** `docs/AGENT_TEMPLATE.md` — required structure for all agent definitions
- **Routing matrix:** `docs/SKILL_ROUTING_MATRIX.md` — cross-skill handoff rules
- **Lint skills:** `bash scripts/lint-skills.sh` — check all skills for template compliance
- **Ecosystem watch:** `bash scripts/check-ecosystem.sh` — check upstream repos for relevant changes

## Org Connect (live org debugging)

Use `org-connect` skill when debugging against a live Salesforce org.

### Connect to an org
```bash
bash scripts/connect-org.sh gulf --production --type customer
bash scripts/connect-org.sh gulf-cam --sandbox --type sandbox
```

### Check connected orgs
```bash
sf org list
```

### Read customer context
```bash
cat customers/gulf/profile.md              # Customer overview, SKUs, topology
cat customers/gulf/orgs/production/org-snapshot.md  # Deployed metadata state
```

### Debugging pattern
1. Read the customer profile (`customers/<name>/profile.md`)
2. Check if org is connected (`sf org list`)
3. Read the org snapshot for metadata context
4. Read specific metadata (triggers, validation rules, flows) for the failing object
5. Cross-reference with `ohfy-*-expert` skills for expected behavior
6. Write customer-specific learnings to `customers/<name>/notes.md`
7. Refresh metadata if stale (`sf project retrieve start`)

## Context Loading Protocol

Before starting any task, determine what context to pre-load. This ensures agents have the right knowledge without being told.

### 1. Customer context (branch or task mentions a customer)

Parse the branch name: if it matches `dzeder/<customer>-*`, match the segment after the slash prefix against known customer directory names in `customers/`.

If a customer is identified (from branch name or task description):
- Read `customers/<customer>/profile.md` for org topology, SKUs, external systems
- Read `customers/<customer>/orgs/<env>/org-snapshot.md` if it exists (deployed metadata state)
- Check `customers/<customer>/notes.md` and `customers/<customer>/known-issues.md` for prior learnings

Known customers: check `ls customers/` for current list (exclude `_template`).

### 2. Package context (task mentions an Ohanafy package)

If the task mentions OMS, WMS, REX, EDI, Ecom, Payments, Configure, Platform, Core, or Data Model:
- Read `skills/ohfy-<package>-expert/references/source-index.md` for code intelligence
- Check `references/last-synced.txt` — if >7 days stale, suggest: "Source index is stale, want me to refresh with `bash scripts/sync-ohanafy-index.sh --repo OHFY-<Package>`?"

### 3. Integration context (task mentions Tray, connector, sync, mapping)

- Read `integrations/patterns/README.md` for available pattern modules
- Read relevant pattern files (e.g., `batch-processing.js`, `data-mapping.js`)
- Read `docs/integration-guides/OHFY_INTEGRATION_MASTER_GUIDE.md` for methodology

### 4. Debugging context (task mentions error, bug, failing, broken)

Load BOTH customer profile AND package source index for the affected area. The source index includes:
- Trigger → Handler Map (which triggers fire on which objects)
- Service Layer Graph (which services call which services)
- Common Patterns (bypass mechanisms, batch chains, queueable usage)
- Cross-Object Relationships

### 5. No match

If no keywords match any of the above, proceed without pre-loading. The agent will discover context as needed.

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

For cross-skill handoffs (when one skill encounters work outside its scope), see `docs/SKILL_ROUTING_MATRIX.md`.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health
- GitHub Actions, CI/CD failures, workflow issues, repo config → invoke github-agent
