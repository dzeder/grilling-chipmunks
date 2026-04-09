# Skill Catalog

114+ skills organized by pillar under `skills/`:

```
skills/
  gstack/          # 36 workflow skills
  salesforce/      # 36 SF skills
  ohanafy/         # 11 SKU expert skills
  tray/            # 9 integration skills
  ukg/             # 3 UKG domain skills
  aws/             # 7 AWS infrastructure skills
  claude/          # 4 Claude AI skills
  docs/            # 4 doc generation skills
  content-watcher/ # Content monitoring
  utility/         # 3 meta skills
```

## gstack (workflow layer)

Use `/browse` for all web browsing. Never use `mcp__claude-in-chrome__*` tools when `/browse` is available.

Available: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/design-consultation`, `/design-shotgun`, `/design-html`, `/review`, `/ship`, `/land-and-deploy`, `/canary`, `/benchmark`, `/browse`, `/connect-chrome`, `/qa`, `/qa-only`, `/design-review`, `/setup-browser-cookies`, `/setup-deploy`, `/retro`, `/investigate`, `/document-release`, `/codex`, `/autoplan`, `/careful`, `/freeze`, `/guard`, `/unfreeze`, `/learn`, `/checkpoint`, `/cso`, `/gstack`, `/gstack-upgrade`, `/health`.

## Salesforce (domain layer)

36 Salesforce-specific skills in `skills/salesforce/`. Activate based on file patterns:
- `.cls`, `.trigger` → sf-apex
- `.flow-meta.xml` → sf-flow
- `/lwc/**/*.js`, `.html` → sf-lwc
- `.soql` → sf-soql
- `.agent` → sf-ai-agentscript
- `.object-meta.xml`, `.field-meta.xml` → sf-metadata
- `.namedCredential-meta.xml` → sf-integration
- Excel/CSV data import → data-harmonizer

## Ohanafy SKU experts (product layer)

Each SKU skill has a pre-built source index (`references/source-index.md`) with:
- Apex classes, triggers, service methods, custom objects & fields, LWC components
- **Trigger → Handler Map** (which triggers fire on which objects, what handlers they call)
- **Service Layer Graph** (one level deep, direct calls/instantiations)
- **Cross-Object Relationships** (lookup and master-detail relationships)
- **Common Patterns** (trigger bypass, service locator, batch/schedulable, queueable, platform events)
- **Test Coverage Summary** (production vs test class ratio, untested classes)

Check `references/last-synced.txt` — if stale (>7 days), refresh with `bash scripts/sync-ohanafy-index.sh --repo REPO`. Use `--discover` to find new repos.

| Skill | Repo(s) | Domain |
|-------|---------|--------|
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

16 integration-specific skills in `skills/tray/`:
- **tray-expert** — Tray.io platform expert (Q&A, workflow design, integration audit, architecture)
- **tray-project** — Generate importable Tray project JSON exports
- **tray-embedded-customjs** — Custom JS patterns for Tray Embedded config wizards
- **tray-errors** — Tray error handling protocols
- **tray-diagrams** — Workflow visualization with Mermaid
- **tray-insights** — Project usage metrics and analytics
- **tray-script-generator** — Script scaffolding from production patterns
- **tray-discovery** — Automated Tray connector discovery pipeline
- **tray-webhook-handler** — HMAC-SHA256 webhook validation, payload parsing
- **csv-output** — CSV formatting patterns
- **salesforce-composite** — SF Composite API patterns (in `skills/salesforce/`)
- **salesforce-field-object-creator** — Field/object definition utilities (in `skills/salesforce/`)
- **ohfy-transformation-settings** — Transformation rule configuration (in `skills/ohanafy/`)
- **deploy-prep** — Deployment workflow preparation
- **test-script** — Script testing infrastructure (in `skills/gstack/`)
- **security** — Integration security patterns

## AWS (infrastructure layer)

7 skills in `skills/aws/`:
- **cdk-deploy** — Deploy CDK stacks to AWS
- **iam-audit** — Audit IAM policies for least privilege
- **lambda-deploy** — Deploy Lambda functions with validation
- **rds-query** — Query RDS databases (read-replica only)
- **s3-manager** — Manage S3 buckets and objects
- **secrets-manager** — AWS Secrets Manager integration

All IaC lives in `skills/aws/cdk/`. CDK TypeScript only — never write CloudFormation directly.

## Claude AI (intelligence layer)

4 skills in `skills/claude/`:
- **model-router** — Route requests to haiku/sonnet/opus by task complexity
- **prompt-loader** — Load and version-control prompts (semver'd YAML in `skills/claude/prompts/`)
- **context-manager** — Track token budgets per agent
- **tool-use** — Define and validate tool schemas

## Doc generation

4 skills in `skills/docs/`:
- **diff-summarizer** — Summarize git diffs into changelogs
- **docx-builder** — Generate DOCX from templates
- **html-publisher** — Publish via Docusaurus
- **md-generator** — Generate MkDocs markdown

## UKG / ERP (domain layer)

3 skills in `skills/ukg/`:
- **ukg-expert** — UKG API, data model, authentication, scheduling
- **ukg-api-debug** — UKG API debugging and troubleshooting
- **ukg-field-mapper** — UKG-to-Ohanafy field mapping

## Utility

In `skills/utility/`:
- **org-connect** — Connect to live Salesforce orgs for debugging and metadata retrieval
- **claude-code-best-practices** — Skill/agent authoring patterns and monorepo organization
- **github-agent** — GitHub Actions health audit, CI/CD best practices, repo configuration review

## Skill routing

For cross-skill handoffs, see `docs/SKILL_ROUTING_MATRIX.md`.

Key routing rules:
- Product ideas, brainstorming → office-hours
- Bugs, errors, "why is this broken" → investigate
- Ship, deploy, create PR → ship
- QA, test the site → qa
- Code review → review
- Update docs after shipping → document-release
- Weekly retro → retro
- Design system, brand → design-consultation
- Visual audit → design-review
- Architecture review → plan-eng-review
- Save progress → checkpoint
- Code quality → health
- GitHub Actions, CI/CD → github-agent
- AWS infrastructure → relevant aws skill
- Claude model routing → relevant claude skill
- Data import, Excel mapping → data-harmonizer
- Content monitoring → content-watcher
