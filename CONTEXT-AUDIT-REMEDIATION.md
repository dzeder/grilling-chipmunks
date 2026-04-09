# Context Audit Remediation Plan

**Repo:** daniels-ohanafy | **Date:** 2026-04-08 | **Current Grade:** C (62%) | **Target Grade:** B+ (80%+)

---

## Phase 1: Entry Point & Context Budget (Week 1)

*Impact: +15-20% overall score. Fixes the root cause — every conversation pays the 490-line tax today.*

### 1.1 — Refactor CLAUDE.md to ~150 lines
- **Priority:** P1 — Critical | **Type:** Agent-fixable | **Impact:** +2pts Entry Point, +1pt Budget
- **Current:** 490 lines — monolithic manual
- **Target:** ~150 lines — concise map with pointers
- **Keep:**
  - Title + one-line description (2 lines)
  - Stack table (7 lines)
  - Model Routing (4 lines)
  - Security Rules (9 lines)
  - Project Structure tree with one-liner per dir (18 lines)
  - Conventions (14 lines)
  - Never Do (11 lines)
  - Directory Rules (8 lines)
  - Artifact Routing table (8 lines)
  - Hooks (3 lines)
  - Improving Skills (5 lines)
  - Pointers to deep-dive docs (15 lines)
- **Move out:**
  - Skill catalog (lines 34-158) → `docs/SKILL_CATALOG.md`
  - Agent roster (lines 159-191) → `agents/README.md`
  - Integration patterns list (lines 193-205) → `integrations/README.md`
  - Integration reference docs list (lines 207-217) → `docs/README.md`
  - Knowledge base list (lines 219-225) → keep 1-line pointer
  - Registry details (lines 227-233) → keep 1-line pointer
  - Watchers details (lines 235-241) → keep 1-line pointer
  - Evals details (lines 243-253) → keep 1-line pointer
  - Upstream References table (lines 254-271) → `references/README.md`
  - Compounding Knowledge (lines 273-285) → `docs/SKILL_TEMPLATE.md` (already there)
  - PR Metrics Convention (lines 350-364) → `docs/PR_METRICS.md`
  - Org Connect section (lines 396-424) → `docs/ORG_CONNECT.md` or `customers/README.md`
  - Context Loading Protocol (lines 428-463) → `.claude/rules/context-loading.md`
  - Skill Routing rules (lines 466-490) → `.claude/rules/skill-routing.md`
  - Tray-First Rule (lines 332-334) → `.claude/rules/tray-first.md`

### 1.2 — Create docs/SKILL_CATALOG.md
- **Priority:** P1 — Critical | **Type:** Agent-fixable | **Impact:** +1pt Entry Point
- Extract full skill catalog from CLAUDE.md
- Organize by pillar with one-line descriptions
- Include file-pattern → skill activation mapping

### 1.3 — Create agents/README.md
- **Priority:** P2 — Recommended | **Type:** Agent-fixable | **Impact:** +0.5pt Progressive Disclosure
- Extract agent roster from CLAUDE.md
- Add team organization, selection guide, template reference
- Link to evals/agents/ for quality metrics

### 1.4 — Create docs/README.md
- **Priority:** P2 — Recommended | **Type:** Agent-fixable | **Impact:** +0.5pt Progressive Disclosure
- Index of all docs with categorized list and one-line descriptions
- Categories: Templates, Guides, Strategy, References

---

## Phase 2: Rules & Progressive Disclosure (Week 2)

*Impact: +10-12% overall score. Moves context injection from monolithic to scoped.*

### 2.1 — Create .claude/rules/skill-routing.md
- **Priority:** P1 — Critical | **Type:** Agent-fixable | **Impact:** +1pt Progressive Disclosure
- Glob-scoped skill activation rules:
  - `*.cls`, `*.trigger` → sf-apex
  - `*.flow-meta.xml` → sf-flow
  - `lwc/**/*.js` → sf-lwc
  - `integrations/**/*.js` → integration patterns
  - `customers/**/*` → customer context loading

### 2.2 — Create .claude/rules/context-loading.md
- **Priority:** P2 — Recommended | **Type:** Agent-fixable | **Impact:** +0.5pt Budget
- Move Context Loading Protocol from CLAUDE.md
- Customer context (branch parsing, profile.md, org-snapshot.md)
- Package context (source indexes by SKU name)
- Integration context (patterns, master guide)
- Debugging context (combined customer + package)

### 2.3 — Create .claude/rules/integration-patterns.md
- **Priority:** P2 — Recommended | **Type:** Agent-fixable | **Impact:** +0.5pt Infra
- Glob: `integrations/patterns/*.js`
- Rules: use script-scaffold.js, validate-transform-batch-output flow
- Rules: never duplicate existing modules
- Rules: test with test-script skill

### 2.4 — Create .claude/rules/tray-first.md
- **Priority:** P3 — Nice to have | **Type:** Agent-fixable | **Impact:** +0.25pt Budget
- Glob: `skills/tray/**/*`, `integrations/**/*`
- Tray-First Rule: check existing workflows before building new ones

### 2.5 — Create integrations/CLAUDE.md
- **Priority:** P2 — Recommended | **Type:** Agent-fixable | **Impact:** +0.5pt Progressive Disclosure
- Pattern modules overview, scaffold usage, Tray-First reminder
- Link to master guide, artifact routing

---

## Phase 3: Infrastructure & Security (Week 2-3)

*Impact: +5-8% overall score. Closes infrastructure gaps and a security hygiene issue.*

### 3.1 — Gitignore settings.local.json
- **Priority:** P1 — Critical | **Type:** Requires user | **Impact:** +0.5pt Infra
- Add `.claude/settings.local.json` to `.gitignore`
- Verify no secrets already committed via `git log -p -- .claude/settings.local.json`

### 3.2 — Align hooks with documentation
- **Priority:** P2 — Recommended | **Type:** Requires user | **Impact:** +0.5pt Infra
- CLAUDE.md says "PostToolUse validators auto-run" but settings.json only has SessionStart
- Either add PostToolUse hooks to settings.json OR update CLAUDE.md to remove the claim
- Recommended hooks:
  - PostToolUse Write/Edit on `*.cls` → Apex LSP validation
  - PostToolUse Write/Edit on `*.flow-meta.xml` → Flow validation
  - PostToolUse Write/Edit on `lwc/**/*` → LWC linting

### 3.3 — Create references/README.md
- **Priority:** P3 — Nice to have | **Type:** Agent-fixable | **Impact:** +0.5pt Budget
- Explain these are auto-synced upstream mirrors
- List each reference with source repo, sync schedule, update script
- Prevents agents from treating vendored content as project docs

---

## Phase 4: Maintainability (Week 3)

*Impact: +5-7% overall score. Prevents context rot.*

### 4.1 — Create scripts/validate-context.sh
- **Priority:** P2 — Recommended | **Type:** Agent-fixable | **Impact:** +1pt Maintainability
- Check CLAUDE.md line count (warn if >200)
- Validate internal links in all markdown files
- Check references/last-synced.txt for staleness (>7 days)
- Verify subdirectory CLAUDE.md files exist for major dirs
- Exit non-zero for CI integration

### 4.2 — Fix 52 broken internal links
- **Priority:** P2 — Recommended | **Type:** Agent-fixable | **Impact:** +0.5pt Maintainability
- Run link validator to identify all 52
- For each: check if target renamed (git log), update or remove
- Focus on links within CLAUDE.md and docs/ first (highest traffic)

---

## Phase 5: Architecture (Week 4)

*Impact: +3-5% overall score. Requires human design intent — can't be fully automated.*

### 5.1 — Create docs/ARCHITECTURE.md
- **Priority:** P1 — Critical | **Type:** Requires user | **Impact:** +1pt Architectural Legibility
- System overview: daniels-ohanafy as the "brain"
- Layer diagram: Skills → Agents → Patterns → Knowledge Base
- Data flow: typical integration task lifecycle
- External system map: Salesforce, Tray.ai, AWS, GitHub
- Key decisions and rationale
- Evolution strategy

### 5.2 — Create docs/decisions/README.md (ADR directory)
- **Priority:** P3 — Nice to have | **Type:** Requires user | **Impact:** +0.5pt Architectural Legibility
- ADR template: Status, Context, Decision, Consequences
- Seed with 3-5 retrospective ADRs:
  - Why Tray-first?
  - Why pillar-based skill organization?
  - Why source indexes instead of full repo clones?
  - Why separate artifacts repo?
  - Why this agent team structure?

---

## Projected Impact

| Phase | Actions | Estimated Score Gain | New Score |
|-------|---------|---------------------|-----------|
| Current | — | — | 62% (C) |
| Phase 1 | 4 actions | +12% | 74% (C+) |
| Phase 2 | 5 actions | +8% | 82% (B) |
| Phase 3 | 3 actions | +5% | 87% (B+) |
| Phase 4 | 2 actions | +4% | 91% (A) |
| Phase 5 | 2 actions | +3% | 94% (A) |

## Execution Notes

- **Phases 1-2 are agent-fixable** — Claude can scaffold all files with `auto-fix`
- **Phase 3 requires user decisions** on gitignore and hook configuration
- **Phase 5 requires human design intent** — ARCHITECTURE.md needs the architect's perspective
- **Phase 1 is the highest ROI** — refactoring CLAUDE.md alone improves every category
- All phases can run independently; order is by impact, not dependency
