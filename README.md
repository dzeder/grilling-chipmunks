# Ohanafy AI Ops

The AI operations framework for Ohanafy — beverage supply chain SaaS. Combines [gstack](https://github.com/garrytan/gstack) workflow skills with Salesforce domain skills, agents, integration patterns, and knowledge infrastructure.

## Structure

```
skills/                    # 114 skills organized by pillar
  gstack/                  #   36 workflow skills (browse, qa, ship, review, etc.)
  salesforce/              #   36 SF skills (apex, flow, lwc, soql, data-harmonizer, etc.)
  ohanafy/                 #   11 SKU expert skills (core, oms, wms, rex, edi, etc.)
  tray/                    #    9 integration skills (tray-expert, csv-output, etc.)
  aws/                     #    7 AWS infrastructure (CDK, Lambda, S3, IAM, RDS, Secrets)
  claude/                  #    4 Claude AI skills (model-router, prompt-loader, etc.)
  docs/                    #    4 doc generation (docx-builder, html-publisher, etc.)
  ukg/                     #    3 UKG domain skills
  content-watcher/         #    1 content monitoring (podcast/YouTube → GitHub issues)
  utility/                 #    3 meta skills (org-connect, github-agent, best-practices)
agents/                    # 17 specialist agents (FDE, PS, Integration, Domain, Support)
integrations/patterns/     # 11 production-tested JS modules for integration scripts
knowledge-base/            # Domain knowledge (beverage supply chain, SF schema, industry)
registry/                  # Repo registry, content sources, team ownership
watchers/                  # 25+ watched GitHub repos with adoption scoring
evals/                     # Agent quality evaluation (datasets, scorers, results)
projects/                  # Integration project workspaces (Core, NetSuite, QBO, Xero, Rehrig)
customers/                 # Per-customer Salesforce configs and knowledge
docs/                      # Integration guides, templates, case studies
references/                # Claude Code best practices, ecosystem watch, Ohanafy source indexes
shared/                    # Hook validators, LSP engine, code analyzer
scripts/                   # 25+ utility scripts — setup, deploy, sync, lint, doctor
tests/                     # Unit, integration, E2E, eval tests (4-layer strategy)
```

## Skills

114 skills organized into 10 pillars:

| Pillar | Count | Key Skills |
|--------|-------|------------|
| **gstack** | 36 | browse, qa, review, ship, canary, investigate, design-consultation, office-hours, checkpoint, health |
| **salesforce** | 36 | sf-apex, sf-flow, sf-lwc, sf-soql, sf-metadata, sf-deploy, sf-testing, sf-integration, data-harmonizer |
| **ohanafy** | 11 | ohfy-core-expert, ohfy-oms-expert, ohfy-wms-expert, ohfy-rex-expert, ohfy-edi-expert, ohfy-payments-expert |
| **tray** | 9 | tray-expert, tray-script-generator, tray-errors, tray-diagrams, tray-insights, csv-output |
| **aws** | 7 | cdk-deploy, lambda-deploy, s3-manager, iam-audit, rds-query, secrets-manager |
| **claude** | 4 | model-router, prompt-loader, context-manager, tool-use |
| **docs** | 4 | diff-summarizer, docx-builder, html-publisher, md-generator |
| **ukg** | 3 | ukg-expert, ukg-api-debug, ukg-field-mapper |
| **content-watcher** | 1 | content-watcher (podcast/YouTube monitoring) |
| **utility** | 3 | org-connect, github-agent, claude-code-best-practices |

Each Ohanafy SKU expert skill includes a pre-built source index with trigger-handler maps, service layer graphs, cross-object relationships, and test coverage summaries.

## Agents

17 specialist agents in `agents/`:

| Team | Agents |
|------|--------|
| **FDE (Salesforce)** | fde-strategist, fde-engineer, fde-qa-engineer, fde-release-engineer, fde-experience-specialist |
| **Professional Services** | ps-technical-architect, ps-solution-architect |
| **Integration** | salesforce-integration-architect, edi-processing-specialist, tray-script-generator, tray-script-tester, ohanafy-data-model, domain-specialist-designer, progressive-disclosure-executor |
| **Domain** | beverage-erp-expert |
| **Support** | documentation-consolidation-specialist, integration-guide-curator |

## Key Rules

- **Model routing:** haiku (classification) → sonnet (reasoning) → opus (evals only)
- **Tray-first:** Check existing Tray workflows before building new ones
- **Customer context:** Load full customer data before every support response
- **Security:** No creds in code. AWS Secrets Manager only. No prod direct access.
- **Evals:** 85% pass rate target, 75% hard fail. Results are immutable.

## Setup

```bash
# 1. Clone
git clone git@github.com:dzeder/daniels-ohanafy.git
cd daniels-ohanafy

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Configure credentials
cp .env.example .env
# Fill in API keys

# 4. Build gstack browser binary
cd .claude/skills/gstack && ./setup && cd ../../..

# 5. Install Salesforce skills + hooks
bash tools/install.sh

# 6. Run health check
bash scripts/doctor.sh
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/doctor.sh` | Health check — validates setup, GitHub config, dependencies |
| `scripts/sync-ohanafy-index.sh` | Refresh Ohanafy SKU source indexes |
| `scripts/lint-skills.sh` | Check all skills for template compliance |
| `scripts/connect-org.sh` | Connect to a live Salesforce org |
| `scripts/check-ecosystem.sh` | Check upstream repos for relevant changes |
| `scripts/ci/discover-repos.py` | Auto-discover Ohanafy repos, populate registry |
| `scripts/ci/health-check.js` | Verify dependencies, credentials, connectivity |

## Schedules

| Job | Schedule | Channel |
|-----|----------|---------|
| Repo Watcher | Every Monday 8am UTC | #ai-ops-updates |
| Content Watcher | Daily 6am UTC | GitHub issues |

## Commit Format

```
type(scope): description
```

Types: `feat` | `fix` | `agent` | `skill` | `docs` | `ci` | `eval` | `chore`
Scopes: `salesforce` | `tray` | `aws` | `claude` | `docs` | `support` | `watchers` | `content`

See [CLAUDE.md](CLAUDE.md) for the complete guide.

## License

MIT
