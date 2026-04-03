# daniels-ohanafy Roadmap

## Current State (v1.0)
- 61 skills across Salesforce, integration, Ohanafy SKU, and domain areas
- 17 agents spanning FDE, PS, integration, and domain specialties
- gstack vendored with sync script + weekly GitHub Action
- Claude Code best practices vendored with sync script + weekly GitHub Action
- 11 integration patterns from DHS production code
- 15 VIP-to-Ohanafy migration scripts + 5 playbooks
- Gulf case study docs (60KB guide, ERD, schema refs)
- 10 CI/CD workflows from pricing repo
- org-connect skill + connect-org.sh for live Salesforce debugging
- 10 SKU expert skills with clone-on-demand pattern

## Near-Term (Next 2 Weeks)
- [ ] Run `gstack ./setup` in a test project and validate
- [ ] Wire up sf-skills installer (`install.py`) for fresh environments
- [ ] Connect to an actual Salesforce org and test org-connect workflow
- [x] Deduplicate `tray-expert` vs `tray-architecture` (overlapping scope)
- [ ] Add coworker (DHS) as collaborator on the repo
- [x] Audit all skills against best-practice docs for pattern compliance
- [ ] Test GitHub Actions in a real PR cycle

## Medium-Term (1-2 Months)
- [ ] Build connector-specific skills: `tray-netsuite`, `tray-qbo`, `tray-ukg-pro`
- [ ] Option 2: Weekly index sync for Ohanafy source repos (script + Action ready in `docs/ohanafy-source-sync-roadmap.md`)
- [ ] Create Ohanafy brand/voice skill for customer-facing docs
- [ ] Per-customer project templates (scaffolding from org-connect output)
- [ ] Add pre-commit hooks for skill schema validation
- [ ] Build integration test suite for skills (trigger-rule coverage)

## Longer-Term (3-6 Months)
- [ ] Option 3: Git submodules for Ohanafy source repos (evaluated after Option 2 stabilizes)
- [ ] Multi-agent orchestration: FDE strategist delegates to SKU experts automatically
- [ ] Operational learning system: capture debugging patterns as new skills
- [ ] Skill quality scoring dashboard (trigger accuracy, user corrections)
- [ ] Webhook-driven sync from Ohanafy repos (Option 4)
- [ ] Cross-customer pattern library: reusable integration recipes
- [ ] Claude Code best-practice compliance linter (auto-check skill frontmatter, agent config)

## Upstream Dependencies

| Dependency | Source | Sync Method | Check Frequency |
|-----------|--------|-------------|-----------------|
| gstack | garrytan/gstack | `scripts/update-gstack.sh` | Weekly (Action) |
| Best practices | shanraisshan/claude-code-best-practice | `scripts/update-best-practices.sh` | Weekly (Action) |
| sf-skills | Jaganpro/sf-skills | `scripts/update-sf-skills.sh` (preview) | Weekly (Action → Issue) |
| DHS Integrations | dhsOhanafy/Integrations | Manual (vendored) | As needed |
| Ohanafy source | Ohanafy/* (54 repos) | Clone-on-demand → weekly index | Evolving |

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-02 | Monorepo over multi-repo | Skills improve alongside project code — feedback loop problem solved |
| 2026-04-02 | Vendor gstack without .git | Submodules too painful for daily use; VERSION-based sync is simpler |
| 2026-04-02 | Clone-on-demand for Ohanafy source | Don't vendor 54 repos; clone to /tmp/ when needed |
| 2026-04-02 | Advisory-only hooks | Blocking hooks frustrate developers; warn but don't block |
| 2026-04-02 | Vendor best-practice docs | Need offline access + stability; weekly sync catches updates |
