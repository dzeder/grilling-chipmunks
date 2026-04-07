# daniels-ohanafy Roadmap

## Current State (v2.0 — Deep Knowledge Layer)
- 98 skills across Salesforce, integration, Ohanafy SKU, and domain areas
- 17 agents spanning FDE, PS, integration, and domain specialties
- gstack vendored with sync script + weekly GitHub Action
- Claude Code best practices vendored with sync script + weekly GitHub Action
- 12 integration patterns from DHS production code
- Gulf case study docs (60KB guide, ERD, schema refs)
- 15 GitHub workflows (14 original + 1 new Ohanafy sync)
- org-connect skill + connect-org.sh for live Salesforce debugging
- 10 SKU expert skills with **enhanced source indexes** (trigger maps, service graphs, relationships, patterns, test coverage)
- **Context Loading Protocol** in CLAUDE.md — agents auto-load customer + package context
- **Customer knowledge structure** — expanded templates with integrations, known issues, customization delta
- **Automated Ohanafy repo monitoring** via weekly GitHub Action

## Completed (v2.0)
- [x] Enhanced `sync-ohanafy-index.sh` with deep code intelligence (trigger maps, service graphs, cross-object relationships, common patterns, test coverage)
- [x] Context Loading Protocol added to CLAUDE.md (decision tree for auto-loading knowledge)
- [x] Customer template expanded (integrations.md, known-issues.md, customization delta, deployment history)
- [x] Gulf fleshed out as reference customer
- [x] GitHub Action for weekly Ohanafy source index sync (`sync-ohanafy-index.yml`)
- [x] Deduplicate `tray-expert` vs `tray-architecture` (overlapping scope)
- [x] Audit all skills against best-practice docs for pattern compliance

## Near-Term (Next 2 Weeks)
- [ ] Run full `sync-ohanafy-index.sh` across all 10 repos and validate output quality
- [ ] Connect to Gulf production org and populate org-snapshot.md with real metadata
- [ ] Set up `OHANAFY_SYNC_TOKEN` repo secret for automated sync workflow (see `docs/setup-ohanafy-sync-token.md`)
- [ ] Run `gstack ./setup` in a test project and validate
- [ ] Wire up sf-skills installer (`install.py`) for fresh environments
- [ ] Add coworker (DHS) as collaborator on the repo
- [ ] Test GitHub Actions in a real PR cycle
- [ ] End-to-end validation: checkout `dzeder/gulf-oms-fix`, verify agents load correct context

## Medium-Term: Self-Evolving System (Approach C)
- [ ] Post-session learning extraction: hook that appends to "Known Gotchas" section after debugging sessions
- [ ] Branch detective: hook that auto-runs Context Loading Protocol on branch checkout
- [ ] Auto-freshness: skill checks source index staleness and auto-triggers sync when >7 days
- [ ] Cross-customer pattern detection: diff customer profiles to find reusable patterns
- [ ] Build connector-specific skills: `tray-netsuite`, `tray-qbo`, `tray-ukg-pro`
- [x] Create Ohanafy brand/voice skill for customer-facing docs (installed from integrations repo)
- [ ] Add pre-commit hooks for skill schema validation
- [ ] Build integration test suite for skills (trigger-rule coverage)
- [ ] Enhance `connect-org.sh` to capture richer metadata (installed package versions, active flows, validation rules, custom fields per object)

## Future: Internal Salesforce Org Integration

Ohanafy logs all activity in an internal Salesforce org. PR and AI activity should eventually flow there too.

- [ ] Define `PR_Activity__c` custom object schema (PR number, branch, human estimate, AI time, tokens, cost, summary, labels)
- [ ] Build Tray webhook workflow: GitHub PR webhook → Tray → SF Composite API upsert to internal org
- [ ] Create `sf-internal-logger` skill for manual activity logging to the internal org
- [ ] Wire into ship workflow as post-step (after PR creation, log to SF)
- [ ] Build SF dashboard for AI velocity metrics (time saved per PR, cost trends, tokens over time, team productivity)

**Implementation path**: GitHub webhook fires on PR events → Tray receives payload → transforms using `batch-processing.js` + `data-mapping.js` patterns → upserts `PR_Activity__c` via SF Composite API. Token costs come from `skills/claude/model-router/skill.py` pricing. Time metrics come from `.time-tracking/log.csv`.

## Future: Vercel Documentation Site

Static branded HTML site showcasing what the AI ops framework does.

- [ ] Create `docs/site/` directory with `index.html` landing page (use `docs/templates/demo-template.html`)
- [ ] Generate Skill Catalog HTML (auto-generate from `scripts/lint-skills.sh` output)
- [ ] Generate Agent Roster HTML (from `agents/*/AGENT.md` frontmatter)
- [ ] Write Integration Pattern Library page (from `integrations/patterns/`)
- [ ] Write Customer Onboarding Guide
- [ ] Write Gulf case study (time-to-value story)
- [ ] Add `vercel.json` pointing `outputDirectory` to `docs/site/`
- [ ] Deploy with `vercel --prod`

**Key decision**: No framework (no Docusaurus, no MkDocs). The brand template produces zero-dependency HTML at ~30KB. Keep it simple.

## Longer-Term (3-6 Months)
- [ ] Multi-agent orchestration: FDE strategist delegates to SKU experts automatically
- [ ] Skill quality scoring dashboard (trigger accuracy, user corrections)
- [ ] Webhook-driven sync from Ohanafy repos (real-time index updates)
- [ ] Cross-customer pattern library: reusable integration recipes
- [ ] Claude Code best-practice compliance linter (auto-check skill frontmatter, agent config)

## Upstream Dependencies

| Dependency | Source | Sync Method | Check Frequency |
|-----------|--------|-------------|-----------------|
| gstack | garrytan/gstack | `scripts/update-gstack.sh` | Weekly (Action) |
| Best practices | shanraisshan/claude-code-best-practice | `scripts/update-best-practices.sh` | Weekly (Action) |
| sf-skills | Jaganpro/sf-skills | `scripts/update-sf-skills.sh` (preview) | Weekly (Action → Issue) |
| DHS Integrations | dhsOhanafy/Integrations | Manual (vendored) | As needed |
| Ohanafy source | Ohanafy/* (54 repos) | `sync-ohanafy-index.sh` + weekly Action | Weekly (Action) |

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-02 | Monorepo over multi-repo | Skills improve alongside project code — feedback loop problem solved |
| 2026-04-02 | Vendor gstack without .git | Submodules too painful for daily use; VERSION-based sync is simpler |
| 2026-04-02 | Clone-on-demand for Ohanafy source | Don't vendor 54 repos; clone to /tmp/ when needed |
| 2026-04-02 | Advisory-only hooks | Blocking hooks frustrate developers; warn but don't block |
| 2026-04-02 | Vendor best-practice docs | Need offline access + stability; weekly sync catches updates |
| 2026-04-04 | Deep Knowledge Layer (Approach B) | Source indexes need depth (triggers, services, relationships), not just class listings |
| 2026-04-04 | Context Loading Protocol | Agents should auto-load customer + package context based on branch name and task keywords |
| 2026-04-04 | Machine user PAT for sync | Single PAT with read-only org scope is simpler than per-repo deploy keys |
| 2026-04-04 | Static grep for service graphs | One level deep, static patterns only. Coverage limitations documented in index. |
| 2026-04-04 | Commit org snapshots as markdown | Committed for agent access; raw JSON gitignored. Regenerate on-demand via connect-org.sh |
| 2026-04-07 | Customer orgs read-only by default | Safety rule: never modify customer orgs unless user explicitly authorizes in conversation |
| 2026-04-07 | PR metrics on every PR | Track human estimate, AI time, tokens, cost, and time saved percentage |
| 2026-04-07 | Static HTML for Vercel site | No framework — brand template produces zero-dependency HTML. Simpler than Docusaurus/MkDocs |
| 2026-04-07 | SF internal org logging via Tray | Future: PR activity flows to internal SF org via GitHub webhook → Tray → Composite API |
