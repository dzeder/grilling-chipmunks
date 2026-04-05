# daniels-ohanafy

Unified monorepo for Ohanafy development — combines [gstack](https://github.com/garrytan/gstack) (general-purpose workflow skills) with Salesforce-specific domain skills, agents, and project workspaces.

## Structure

```
skills/                    # 97 skills — Salesforce, Tray.io, UKG, workflow, QA, design
agents/                    # 17 specialist agents (FDE, PS, Integration, Domain, Support)
projects/                  # Integration project workspaces (Core, NetSuite, QBO, Xero, Rehrig)
customers/                 # Per-customer Salesforce configs and knowledge
integrations/patterns/     # 11 production-tested JS modules for integration scripts
references/                # Claude Code best practices, ecosystem watch, Ohanafy source indexes
docs/                      # Whitepapers, integration guides, templates, architecture
scripts/                   # 23 utility scripts — setup, deploy, sync, lint, doctor
shared/                    # Hook validators, LSP engine, code analyzer
tools/                     # Installer and hygiene checker
tests/                     # Validator and registry contract tests
.claude/skills/gstack/     # gstack — planning, review, ship, QA, browser automation
```

## Skills

97 skills organized by domain:

| Category | Prefix | Examples |
|----------|--------|----------|
| **Salesforce** | `sf-*` | sf-apex, sf-flow, sf-lwc, sf-soql, sf-metadata, sf-deploy, sf-testing, sf-integration, sf-permissions, sf-debug |
| **Ohanafy SKU experts** | `ohfy-*` | ohfy-core-expert, ohfy-oms-expert, ohfy-wms-expert, ohfy-rex-expert, ohfy-ecom-expert, ohfy-edi-expert, ohfy-payments-expert, ohfy-configure-expert, ohfy-data-model-expert, ohfy-platform-expert |
| **Integration** | `tray-*` | tray-expert, tray-script-generator, tray-errors, tray-diagrams, tray-insights, tray-embedded-customjs |
| **Domain** | `ukg-*` | ukg-expert, ukg-api-debug, ukg-field-mapper |
| **Workflow** | (gstack) | browse, qa, review, ship, canary, benchmark, investigate, design-consultation, design-shotgun, design-html |
| **Utility** | — | org-connect, github-agent, claude-code-best-practices, security, checkpoint, health |

Each SKU expert skill includes a pre-built source index (`references/source-index.md`) with trigger-handler maps, service layer graphs, cross-object relationships, and test coverage summaries.

## Agents

17 specialist agents in `agents/`:

| Team | Agents |
|------|--------|
| **FDE (Salesforce)** | fde-strategist, fde-engineer, fde-qa-engineer, fde-release-engineer, fde-experience-specialist |
| **Professional Services** | ps-technical-architect, ps-solution-architect |
| **Integration** | salesforce-integration-architect, edi-processing-specialist, tray-script-generator, tray-script-tester, ohanafy-data-model, domain-specialist-designer, progressive-disclosure-executor |
| **Domain** | beverage-erp-expert |
| **Support** | documentation-consolidation-specialist, integration-guide-curator |

## Integration Patterns

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
- `script-scaffold.js` — Full validate-transform-batch-output starter template

## Projects & Customers

**Projects** (`projects/`) — shared technical work (integrations, reports, LWC):
- `ohanafy-core/` — Main Salesforce org
- `netsuite-ohanafy/` — NetSuite integration
- `qbo-ohanafy/` — QuickBooks Online integration
- `xero-ohanafy/` — Xero integration
- `rehrig-ohanafy/` — Rehrig integration

**Customers** (`customers/`) — per-customer Salesforce configurations and knowledge:
- Each customer has a `profile.md` (org topology, SKUs, data profile, external systems)
- Per-environment metadata in `orgs/` (populated by `connect-org.sh`)
- Copy `_template/` to create a new customer

## Setup

```bash
# 1. Clone
git clone git@github.com:dzeder/daniels-ohanafy.git
cd daniels-ohanafy

# 2. Build gstack browser binary
cd .claude/skills/gstack && ./setup && cd ../../..

# 3. Install Salesforce skills + hooks into ~/.claude/
bash tools/install.sh
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/doctor.sh` | Health check — validates setup, GitHub config, dependencies |
| `scripts/sync-ohanafy-index.sh` | Refresh Ohanafy SKU source indexes |
| `scripts/lint-skills.sh` | Check all skills for template compliance |
| `scripts/connect-org.sh` | Connect to a live Salesforce org |
| `scripts/check-ecosystem.sh` | Check upstream repos for relevant changes |
| `scripts/update-gstack.sh` | Update gstack to latest version |
| `scripts/update-best-practices.sh` | Refresh Claude Code best practices reference |

## Adding New Skills

Create a new directory under `skills/` with the appropriate prefix:

| Prefix | Domain |
|--------|--------|
| `sf-*` | Salesforce |
| `tray-*` | Tray.io |
| `ohfy-*` | Ohanafy SKU |
| `ukg-*` | UKG |
| `ns-*` | NetSuite |
| `qbo-*` | QuickBooks Online |
| `xero-*` | Xero |

Each skill needs a `SKILL.md` with YAML frontmatter (name, description) and trigger rules. See `docs/SKILL_TEMPLATE.md` for the required structure.

## License

MIT
