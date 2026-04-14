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

## Project Structure

```
skills/               # 115+ skills organized by pillar (see docs/SKILL_CATALOG.md)
agents/               # 19 specialist agents (see agents/README.md)
integrations/         # Tray patterns, marketplace UI (see integrations/CLAUDE.md)
customers/            # Per-customer Salesforce configs
knowledge-base/       # Domain knowledge (beverage, SF, industry)
registry/             # Repo registry, content sources, team ownership — **check before touching any product repo**
watchers/             # Repo monitoring configs and adoption queue
evals/                # Agent evaluation datasets, scorers, results (IMMUTABLE)
docs/                 # Guides, templates, case studies (see docs/README.md)
references/           # Vendored upstream mirrors (see references/README.md)
shared/               # Validators, LSP engine, code analyzer
scripts/              # 23+ utility scripts
tests/                # Unit, integration, E2E, eval tests
```

## Directory Rules

- New agent → copy `agents/_template/`, add evals in `evals/agents/`
- New skill → copy `skills/_template_v2/` into correct pillar
- New tracked repo → add to `watchers/repos.yaml`
- New content source → add to `registry/content-sources.yaml`
- New prompt → add to `skills/claude/prompts/` with semver, add eval case
- All IaC → `skills/aws/cdk/`
- Tray configs → `skills/tray/`

## Artifact Routing

| What | Where |
|------|-------|
| Skills, agents, patterns, knowledge | This repo (`daniels-ohanafy`) |
| Built artifacts (Tray exports, SF metadata) | `dzeder/daniels-ohanafy-artifacts` |
| Legacy Tray exports (reference only) | `dzeder/Integrations` (read-only) |
| Per-customer Salesforce configs | This repo (`customers/`) |

Never commit built artifacts to this repo.

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
- HTML artifacts: use Ohanafy 2025 brand template (`docs/templates/demo-template.html`)
- Documentation: MD for internal, branded HTML for external, DOCX for client deliverables

## Never Do

- Modify `evals/results/` — **IMMUTABLE** append-only (85% target, 75% hard fail, run on every PR)
- Deploy to prod SF or AWS prod without explicit instruction
- Hardcode any credential or secret
- Use opus for anything except evals/critical decisions
- Skip evals for a new agent or prompt
- Write CloudFormation directly
- Query SF production org from skill code
- Build a new Tray workflow without checking existing ones first
- Modify, deploy to, or write data/metadata to any connected customer Salesforce org without explicit user authorization — no `sf project deploy`, no `sf data update`, no `sf apex run`, no destructive changes

## Hooks

PostToolUse validators auto-run on file writes (Apex LSP, Flow validation, LWC linting, metadata checks). These are advisory — they warn but don't block.

## Improving Skills

Edit skill files directly in `skills/<pillar>/<skill-name>/SKILL.md`. Commit with the project change. Templates: `docs/SKILL_TEMPLATE.md`, `docs/AGENT_TEMPLATE.md`. Lint: `bash scripts/lint-skills.sh`.

## Deep Dives

| Topic | Location |
|-------|----------|
| Full skill catalog (115+) | `docs/SKILL_CATALOG.md` |
| Agent roster & teams | `agents/README.md` |
| Integration patterns | `integrations/CLAUDE.md` |
| Documentation index | `docs/README.md` |
| Upstream references | `references/README.md` |
| Skill routing matrix | `docs/SKILL_ROUTING_MATRIX.md` |
| Skill template | `docs/SKILL_TEMPLATE.md` |
| Agent template | `docs/AGENT_TEMPLATE.md` |
| Source sync roadmap | `docs/ohanafy-source-sync-roadmap.md` |
| Repo registry | `registry/ohanafy-repos.yaml` |
| Compounding knowledge | `docs/SKILL_TEMPLATE.md` (learned_from spec) |

## Skill Routing (quick reference)

When the user's request matches a skill, invoke it FIRST via the Skill tool.

### Step 1: Compound Requests (check first — most specific wins)

Multi-domain or multi-step requests match these patterns before falling through to single-domain:

- "Design + build + test [integration]" → `/tray-expert` (drives the chain)
- "Fix [integration/Tray] that talks to Salesforce" → `/investigate` (debugging trumps domain)
- "Build a Tray workflow for [Ohanafy package]" → `/tray-expert` (integration leads)
- "Set up [customer] end-to-end" → `/kickoff` (setup before implementation)
- "Build an Agentforce agent" → invoke `fde-strategist` agent (multi-agent orchestration)
- "Full review / review gauntlet" → `/autoplan` (runs all review perspectives)
- "Ship and document" → `/ship` then `/document-release`
- "Debug and fix and ship" → `/investigate` (debug first, then chain)
- Complex multi-domain requests → invoke `orchestrator` agent (see `agents/orchestrator.md`)

### Step 2: Single-Domain Routing

- Product ideas, brainstorming → `/office-hours`
- Bugs, errors → `/investigate`
- Ship, deploy, PR → `/ship`
- QA, test the site → `/qa`
- Code review → `/review`
- Update docs after shipping → `/document-release`
- Weekly retro → `/retro`
- Design system → `/design-consultation`
- Visual audit, design polish → `/design-review`
- Architecture review → `/plan-eng-review`
- Save progress, resume → `/checkpoint`
- Code quality, health check → `/health`
- GitHub Actions, CI/CD → `/github-agent`
- Data import → `/data-harmonizer`
- Org debugging, connect SF org → `/org-connect`
- Datadog, monitoring, observability → `/datadog-expert`
- Start new work, set up context → `/kickoff`

### Step 3: Ambiguity Fallback

If no pattern matches or multiple patterns tie:
1. Check `.context/workspace.md` for active customer/integration context
2. Check current branch name for customer or domain clues
3. Consult `docs/skill-index.yaml` for trigger keyword matching
4. If still ambiguous, ask: "This touches [A] and [B]. Which should I focus on first?"

Full routing: `docs/SKILL_ROUTING_MATRIX.md` | Skill index: `docs/skill-index.yaml` | Chains: `docs/skill-chains.yaml`
