# Daniel's Ohanafy Monorepo

Unified skills, agents, and projects for Ohanafy development.

## gstack skills (workflow layer)

Use `/browse` for all web browsing. Never use `mcp__claude-in-chrome__*` tools when `/browse` is available.

Available gstack skills: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/design-consultation`, `/design-shotgun`, `/design-html`, `/review`, `/ship`, `/land-and-deploy`, `/canary`, `/benchmark`, `/browse`, `/connect-chrome`, `/qa`, `/qa-only`, `/design-review`, `/setup-browser-cookies`, `/setup-deploy`, `/retro`, `/investigate`, `/document-release`, `/codex`, `/autoplan`, `/careful`, `/freeze`, `/guard`, `/unfreeze`, `/learn`.

## Salesforce skills (domain layer)

33 Salesforce-specific skills in `skills/`. These activate based on file patterns:
- `.cls`, `.trigger` -> sf-apex
- `.flow-meta.xml` -> sf-flow
- `/lwc/**/*.js`, `.html` -> sf-lwc
- `.soql` -> sf-soql
- `.agent` -> sf-ai-agentscript
- `.object-meta.xml`, `.field-meta.xml` -> sf-metadata
- `.namedCredential-meta.xml` -> sf-integration

## Domain skills

Additional domain-specific skills in `skills/`:
- **ukg-expert** — UKG API, data model, authentication, scheduling
- **ukg-api-debug** — UKG API debugging and troubleshooting
- **ukg-field-mapper** — UKG-to-Ohanafy field mapping
- **tray-expert** — Tray.io iPaaS patterns for beverage industry integrations

## Agents

8 specialist agents in `agents/`:
- **fde-strategist** — Planning and delegation (read-only, spawns other agents)
- **fde-engineer** — Agentforce implementation (Apex, Agent Scripts, metadata)
- **fde-qa-engineer** — Test execution, debug logs, observability
- **fde-release-engineer** — Deployment, Connected Apps, CI/CD
- **fde-experience-specialist** — Conversation design, persona, LWC UI
- **ps-technical-architect** — Backend Apex, integrations, data modeling
- **ps-solution-architect** — Metadata design, Flows, security, architecture docs
- **beverage-erp-expert** — Beverage distribution domain (VIP, Encompass, DSD, three-tier)

## Project structure

```
projects/
  ohanafy-core/           # Main Salesforce org
  netsuite-ohanafy/       # NetSuite integration
  qbo-ohanafy/            # QuickBooks Online integration
  xero-ohanafy/           # Xero integration
  rehrig-ohanafy/         # Rehrig integration
```

## Integration code

```
integrations/
  tray/                   # Tray.io GraphQL integration layer
  marketplace-ui/         # React marketplace components (SolutionGrid, config, JWT)
```

## Migration scripts

Production-tested ETL scripts in `scripts/migrations/vip-to-ohanafy/`:
- Wave-based SF Bulk API migration with resume and dry-run
- Loaders for POs, invoices, contacts, inventory, keg shells, route customers
- Data comparison and validation tools

## Reference docs

- `docs/case-studies/gulf-vip-to-ohanafy/` — Complete VIP-to-Ohanafy data mapping (60KB guide + ERD + schema refs)
- `docs/templates/` — Document templates with Ohanafy branding

## Conventions

- Salesforce CLI: use `sf` (never `sfdx`)
- API version: v62.0+ (never below v56.0)
- Apex: bulkify everything, check FLS/CRUD, use service layer pattern
- Flows: follow naming conventions in sf-flow skill
- LWC: use SLDS, wire adapters, LMS for cross-component communication
- Tests: 85%+ Apex coverage target, meaningful assertions

## Hooks

PostToolUse validators auto-run on file writes (Apex LSP, Flow validation, LWC linting, metadata checks). These are advisory — they warn but don't block.

## Improving skills

When a skill gives bad advice or misses something, fix it directly:
1. Edit the skill file in `skills/<skill-name>/SKILL.md`
2. Commit with the project change that revealed the gap
3. The improvement is live immediately for all future work
