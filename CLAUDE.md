# Daniel's Ohanafy Monorepo

The AI operations framework for Ohanafy — beverage supply chain SaaS.
Unified skills, agents, patterns, pipelines, and knowledge for all Ohanafy development.

## Stack

| Layer | Tech | Rule |
|-------|------|------|
| CRM | Salesforce Enterprise | sf CLI only, API v62.0+, scratch orgs, never prod direct |
| iPaaS | Tray.ai | JSON configs in `skills/tray/`, Tray-first rule |
| Cloud | AWS | CDK TypeScript only, Secrets Manager, Lambda Powertools |
| AI | Claude | Model routing policy below |
| CI/CD | GitHub Actions | All pipelines in `.github/workflows/` |

## Model Routing

- **haiku** → classification, routing, formatting, eval scoring
- **sonnet** → reasoning, code review, doc generation, support responses
- **opus** → evals and critical decisions only

Always use the latest available version of each tier.

## Security Rules

1. No credentials in code — AWS Secrets Manager only
2. No customer PII in logs
3. No SF production org credentials in this repo
4. No direct production DB queries — read replica only
5. No public S3 buckets
6. Tray webhooks must validate HMAC signatures
7. Customer Salesforce orgs are strictly read-only by default — never deploy, push, update, or delete metadata/data in a connected customer org unless the user explicitly authorizes writes in the current conversation

## Skills (pillar organization)

Skills are organized into pillars under `skills/`:

```
skills/
  gstack/        # 36 workflow skills (browse, qa, ship, review, etc.)
  salesforce/    # 36 SF skills (sf-apex, sf-flow, sf-lwc, data-harmonizer, etc.)
  ohanafy/       # 11 SKU expert skills (ohfy-core-expert, ohfy-oms-expert, etc.)
  tray/          # 9 integration skills (tray-expert, csv-output, deploy-prep, etc.)
  ukg/           # 3 UKG domain skills
  aws/           # 7 AWS infrastructure skills (CDK, Lambda, S3, IAM, RDS, Secrets)
  claude/        # 4 Claude AI skills (model-router, prompt-loader, context-manager, tool-use)
  docs/          # 4 doc generation skills (diff-summarizer, docx-builder, html-publisher, md-generator)
  content-watcher/ # Content monitoring (podcast/YouTube → GitHub issues)
  utility/       # 3 meta skills (org-connect, github-agent, claude-code-best-practices)
```

### gstack skills (workflow layer)

Use `/browse` for all web browsing. Never use `mcp__claude-in-chrome__*` tools when `/browse` is available.

Available gstack skills: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/design-consultation`, `/design-shotgun`, `/design-html`, `/review`, `/ship`, `/land-and-deploy`, `/canary`, `/benchmark`, `/browse`, `/connect-chrome`, `/qa`, `/qa-only`, `/design-review`, `/setup-browser-cookies`, `/setup-deploy`, `/retro`, `/investigate`, `/document-release`, `/codex`, `/autoplan`, `/careful`, `/freeze`, `/guard`, `/unfreeze`, `/learn`, `/checkpoint`, `/cso`, `/gstack`, `/gstack-upgrade`, `/health`.

### Salesforce skills (domain layer)

36 Salesforce-specific skills in `skills/salesforce/`. Activate based on file patterns:
- `.cls`, `.trigger` -> sf-apex
- `.flow-meta.xml` -> sf-flow
- `/lwc/**/*.js`, `.html` -> sf-lwc
- `.soql` -> sf-soql
- `.agent` -> sf-ai-agentscript
- `.object-meta.xml`, `.field-meta.xml` -> sf-metadata
- `.namedCredential-meta.xml` -> sf-integration
- Excel/CSV data import → data-harmonizer

### Ohanafy SKU expert skills (product layer)

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

### Integration skills (Tray / Ohanafy platform)

16 integration-specific skills in `skills/tray/`:
- **tray-expert** — Tray.io platform expert (Q&A, workflow design, integration audit, architecture)
- **tray-project** — Generate importable Tray project JSON exports (flat UI format, typed values, auth objects)
- **tray-embedded-customjs** — Custom JS patterns for Tray Embedded config wizards
- **tray-errors** — Tray error handling protocols
- **tray-diagrams** — Workflow visualization with Mermaid
- **tray-insights** — Project usage metrics and analytics
- **tray-script-generator** — Script scaffolding from production patterns
- **tray-discovery** — Automated Tray connector discovery pipeline (Claude-scored, registry-backed)
- **tray-webhook-handler** — HMAC-SHA256 webhook validation, payload parsing, event routing
- **csv-output** — CSV formatting patterns
- **salesforce-composite** — SF Composite API patterns (in `skills/salesforce/`)
- **salesforce-field-object-creator** — Field/object definition utilities (in `skills/salesforce/`)
- **ohfy-transformation-settings** — Transformation rule configuration (in `skills/ohanafy/`)
- **deploy-prep** — Deployment workflow preparation
- **test-script** — Script testing infrastructure (in `skills/gstack/`)
- **security** — Integration security patterns

### AWS skills (infrastructure layer)

7 AWS infrastructure skills in `skills/aws/`:
- **cdk-deploy** — Deploy CDK stacks to AWS
- **iam-audit** — Audit IAM policies for least privilege
- **lambda-deploy** — Deploy Lambda functions with validation
- **rds-query** — Query RDS databases (read-replica only)
- **s3-manager** — Manage S3 buckets and objects
- **secrets-manager** — AWS Secrets Manager integration

All IaC lives in `skills/aws/cdk/`. CDK TypeScript only — never write CloudFormation directly.

### Claude AI skills (intelligence layer)

4 Claude-specific skills in `skills/claude/`:
- **model-router** — Route requests to haiku/sonnet/opus based on task complexity
- **prompt-loader** — Load and version-control prompts (semver'd YAML in `skills/claude/prompts/`)
- **context-manager** — Track token budgets per agent
- **tool-use** — Define and validate tool schemas

### Doc generation skills

4 documentation skills in `skills/docs/`:
- **diff-summarizer** — Summarize git diffs into changelogs
- **docx-builder** — Generate DOCX from templates
- **html-publisher** — Publish via Docusaurus
- **md-generator** — Generate MkDocs markdown

### Domain skills (UKG / ERP)

3 UKG domain skills in `skills/ukg/`:
- **ukg-expert** — UKG API, data model, authentication, scheduling
- **ukg-api-debug** — UKG API debugging and troubleshooting
- **ukg-field-mapper** — UKG-to-Ohanafy field mapping

### Utility skills

In `skills/utility/`:
- **org-connect** — Connect to live Salesforce orgs for debugging and metadata retrieval
- **claude-code-best-practices** — Skill/agent authoring patterns and monorepo organization
- **github-agent** — GitHub Actions health audit, CI/CD best practices, repo configuration review

## Agents

19 specialist agents in `agents/`:

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
- **tray-discovery** — Automated Tray connector discovery with Claude scoring
- **ohanafy-data-model** — Ohanafy object model, relationships, field usage
- **domain-specialist-designer** — Domain-specific integration design
- **progressive-disclosure-executor** — Phased implementation approach
- **content** — Content pipeline orchestrator (drives content-watcher skill)

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

## Knowledge base

Domain knowledge in `knowledge-base/`:
- `beverage-supply-chain/glossary.md` — Industry terminology (TTB, COLA, depletions, 3-tier)
- `salesforce/object-model.md` — SF schema reference
- `salesforce/key-flows.md` — Important Salesforce Flows
- `industry-insights/` — Distribution trends, pricing models, competitive landscape

## Registry

Central configuration in `registry/`:
- `ohanafy-repos.yaml` — All Ohanafy product repos (auto-discovered via `python scripts/ci/discover-repos.py`)
- `content-sources.yaml` — Podcast/YouTube sources to monitor
- `team.yaml` — Team ownership map

**Before touching any product repo, check `registry/ohanafy-repos.yaml` first.** Know the type, SKU, and owner. Data-model changes require a migration plan.

## Watchers

Repo monitoring in `watchers/`:
- `repos.yaml` — 25+ watched GitHub repos with priority, auto-adopt rules, tags
- `adoption-queue/` — PRs proposed by adoption watcher
- `digest/` — Weekly summaries

Watcher job runs Monday 8am UTC. Content watcher runs daily 6am UTC.

## Evals

Agent quality evaluation in `evals/`:
- `datasets/` — Golden dataset definitions per agent
- `scorers/` — Eval scoring logic (hard checks + Claude Haiku rubric)
- `results/` — **IMMUTABLE** append-only eval results (never delete)
- `agents/` — Per-agent eval configs and fixtures

Pass rate: 85% target, 75% hard fail. Run on every PR.

## Upstream References (read-only mirrors)

Read-only mirrors of upstream repos live in `references/`. These are auto-synced and **safe to overwrite** — never edit them directly. Your skills in `skills/` are never touched by any sync.

| Reference | Source | Update | Schedule |
|-----------|--------|--------|----------|
| `references/claude-code-best-practices/` | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | `bash scripts/update-best-practices.sh` | Wednesdays |
| `references/agent-skills/` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `bash scripts/update-agent-skills.sh` | Thursdays |
| `.claude/skills/gstack/` | [garrytan/gstack](https://github.com/garrytan/gstack) | `bash scripts/update-gstack.sh` | Mondays |

Cherry-pick sources (issue-based, no auto-overwrite):
- [Jaganpro/sf-skills](https://github.com/Jaganpro/sf-skills) — `bash scripts/update-sf-skills.sh` (Fridays)

Key references in `references/claude-code-best-practices/`:
- `best-practice/claude-skills.md` — Skill authoring patterns
- `best-practice/claude-subagents.md` — Subagent design
- `best-practice/claude-commands.md` — Command patterns
- `reports/claude-skills-for-larger-mono-repos.md` — Monorepo skill organization

## Compounding Knowledge (`learned_from`)

Skills can declare upstream lineage so improvements compound from both our work and the community:

```yaml
# In any SKILL.md frontmatter:
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/error-recovery.md
    adapted: "2026-04-04"
```

When the watcher detects upstream changes, it checks `learned_from` lineage to flag your skills that may benefit. See `docs/SKILL_TEMPLATE.md` for full spec and `watchers/adoption-queue/README.md` for the adoption flow.

## Project structure

```
skills/               # 114 skills organized by pillar (see above)
agents/               # 17 specialist agent definitions
integrations/         # Tray patterns, marketplace UI, workflow artifacts
projects/             # Shared technical work
  ohanafy-core/         # Main Salesforce org
  netsuite-ohanafy/     # NetSuite integration
  qbo-ohanafy/          # QuickBooks Online integration
  xero-ohanafy/         # Xero integration
  rehrig-ohanafy/       # Rehrig integration
customers/            # Per-customer Salesforce metadata
  _template/            # Copy to create a new customer
  gulf/                 # Gulf Distributing
knowledge-base/       # Domain knowledge (beverage, SF, industry)
registry/             # Repo registry, content sources, team ownership
watchers/             # Repo monitoring configs and adoption queue
evals/                # Agent evaluation datasets, scorers, results
docs/                 # Guides, templates, case studies
references/           # Vendored best practices, Ohanafy source indexes
shared/               # Validators, LSP engine, code analyzer
scripts/              # 23+ utility scripts
tests/                # Unit, integration, E2E, eval tests
```

`projects/` = shared technical work (integrations, reports, LWC).
`customers/` = per-customer Salesforce/Ohanafy configurations and knowledge.

## Directory Rules

- New agent → copy `agents/_template/`, add evals in `evals/agents/`
- New skill → copy `skills/_template_v2/` into correct pillar
- New tracked repo → add to `watchers/repos.yaml`
- New content source → add to `registry/content-sources.yaml`
- New prompt → add to `skills/claude/prompts/` with semver, add eval case
- All IaC → `skills/aws/cdk/`
- Tray configs → `skills/tray/`

## Tray-First Rule

Ohanafy has extensive existing Tray workflows. Before building anything new in Tray, check existing workflows. Never duplicate. Extend or reference existing workflows where possible.

## Conventions

- Salesforce CLI: use `sf` (never `sfdx`)
- API version: v62.0+ (never below v56.0)
- Apex: bulkify everything, check FLS/CRUD, use service layer pattern
- Flows: follow naming conventions in sf-flow skill
- LWC: use SLDS, wire adapters, LMS for cross-component communication
- Tests: 85%+ Apex coverage target, meaningful assertions
- Tray scripts: use patterns from `integrations/patterns/`, follow validate-transform-batch-output flow
- Integration scripts: always use `script-scaffold.js` as starting template
- Commit format: `type(scope): description` — types: feat|fix|agent|skill|docs|ci|eval|chore
- HTML artifacts: always use Ohanafy 2025 brand template (`docs/templates/demo-template.html`) — Geist font, mellow/cork/dark-denim palette, branded header/footer. Invoke `/ohanafy-brand` skill for brand guidance.
- Documentation: MD for internal, branded HTML for external (via demo-template.html + /ohanafy-brand), DOCX for client deliverables

## PR Metrics Convention

Every PR must populate the Time Tracking table in the PR description. This is how we measure the value of AI-assisted development.

| Metric | How to estimate |
|--------|----------------|
| **Human Estimate (hrs)** | How long would a human developer take to do this work from scratch? Include research, coding, testing, and review time. |
| **AI Actual (min)** | Wall-clock minutes from session start to PR creation. |
| **Tokens Used** | Approximate input + output tokens. Estimate ~4K tokens per tool call, ~1K per response turn. |
| **Est. Cost ($)** | Use Sonnet pricing: $3/1M input, $15/1M output. If Opus was used, $15/1M input, $75/1M output. |
| **Time Saved (%)** | `((human_hrs × 60 − ai_min) / (human_hrs × 60)) × 100` |

Agents must fill these values when creating PRs. The ship skill is upstream (gstack) — don't modify it. Instead, update the PR body after creation if needed using `gh pr edit`.

Append a row to `.time-tracking/log.csv` after each PR for longitudinal tracking.

## Never Do

- Modify `evals/results/`
- Deploy to prod SF or AWS prod without explicit instruction
- Hardcode any credential or secret
- Use opus for anything except evals/critical decisions
- Skip evals for a new agent or prompt
- Write CloudFormation directly
- Query SF production org from skill code
- Build a new Tray workflow without checking existing ones first
- Modify, deploy to, or write data/metadata to any connected customer Salesforce org without explicit user authorization — customer orgs are READ-ONLY by default (retrieve only). No `sf project deploy`, no `sf data update`, no `sf apex run`, no destructive changes

## Hooks

PostToolUse validators auto-run on file writes (Apex LSP, Flow validation, LWC linting, metadata checks). These are advisory — they warn but don't block.

## Improving skills

When a skill gives bad advice or misses something, fix it directly:
1. Edit the skill file in `skills/<pillar>/<skill-name>/SKILL.md`
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
- Read `skills/ohanafy/ohfy-<package>-expert/references/source-index.md` for code intelligence
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
- AWS infrastructure, Lambda, S3, CDK → invoke relevant aws skill
- Claude model routing, prompt management → invoke relevant claude skill
- Data import, Excel mapping → invoke data-harmonizer
- Content monitoring, podcast insights → invoke content-watcher
