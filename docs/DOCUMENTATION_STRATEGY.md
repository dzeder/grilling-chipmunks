# Documentation Strategy

How we document the Ohanafy AI Operations Framework — what formats, what to write, and how it becomes the Vercel site.

## Format Matrix

| Format | Audience | When to Use | Template/Tool |
|--------|----------|-------------|---------------|
| **Markdown** | Internal / developers | Working docs, skill specs, agent configs, roadmaps | Standard MD, MkDocs-compatible frontmatter |
| **Branded HTML** | External / demos / Vercel | Integration guides, case studies, showcases, landing pages | `docs/templates/demo-template.html` + `/ohanafy-brand` skill |
| **DOCX** | Client deliverables | Proposals, SOWs, migration plans, reports | `/docx-builder` skill with python-docx |

**Rule**: Every significant piece of work should produce at least an MD doc. External-facing work should also produce branded HTML.

## Vercel Site Architecture

Static branded HTML — no framework needed. The brand template produces zero-dependency pages at ~30KB each.

```
docs/site/
├── index.html              # Landing page: What is the Ohanafy AI Ops Framework?
├── skills/
│   └── index.html          # Skill Catalog (auto-generated)
├── agents/
│   └── index.html          # Agent Roster (auto-generated)
├── patterns/
│   └── index.html          # Integration Pattern Library
├── guides/
│   ├── onboarding.html     # Customer Onboarding Guide
│   ├── integration.html    # Integration Master Guide (branded)
│   └── faq.html            # FAQ
├── case-studies/
│   └── gulf.html           # Gulf: VIP → Ohanafy migration story
└── vercel.json             # { "outputDirectory": "docs/site" }
```

**Why no framework?** Docusaurus and MkDocs add build complexity, dependency management, and upgrade churn for what is essentially a collection of standalone HTML pages. The brand template already handles typography, colors, navigation, responsive layout, and print styles. When the site grows beyond ~20 pages, revisit this decision.

## Must-Write Docs (Priority Order)

### Tier 1 — Write first (defines what this is)
1. **Ohanafy AI Operations Overview** — Landing page. What is this framework, what does it do, who is it for, what results has it delivered.
2. **Integration Pattern Library** — The 11 production JS modules in `integrations/patterns/`, with examples and when-to-use guidance.
3. **Skill Catalog** — Auto-generated from `scripts/lint-skills.sh` output. 114 skills organized by pillar with descriptions and trigger conditions.

### Tier 2 — Write next (shows depth)
4. **Agent Roster** — 19 agents with responsibilities, tools, and handoff rules. Auto-generated from `agents/*/AGENT.md` frontmatter.
5. **Customer Onboarding Guide** — How to set up a new customer: copy template, connect org, populate profile, configure integrations.
6. **Gulf Case Study** — Time-to-value story: VIP migration, 8,743 items migrated, what the AI framework enabled.

### Tier 3 — Write as needed (fills gaps)
7. **FAQ** — Common questions, troubleshooting, how to add skills/agents/customers.
8. **Configuration Guide** — How to configure the framework: registry, watchers, evals, content sources.
9. **AI Velocity Report** — Aggregate PR metrics from `.time-tracking/log.csv` into a dashboard page.

## Auto-Generation Opportunities

| What | Source | How |
|------|--------|-----|
| Skill Catalog | `scripts/lint-skills.sh` | Add `--html` flag to output branded HTML table |
| Agent Roster | `agents/*/AGENT.md` | Parse YAML frontmatter, generate HTML roster |
| Integration Patterns | `integrations/patterns/*.js` | Extract JSDoc headers, generate reference page |
| PR Metrics Dashboard | `.time-tracking/log.csv` | Aggregate CSV into summary HTML with charts |

## What NOT to Do

- Do not set up Docusaurus or MkDocs (overhead not justified yet)
- Do not repurpose `integrations/marketplace-ui/` as a doc site (it's a Tray config app)
- Do not duplicate content that lives in skills — link to the skill instead
- Do not create docs without using the brand template for external-facing output

## Documentation Workflow

1. **During development**: Write MD docs in `docs/` as you work
2. **At PR time**: Generate branded HTML for any external-facing docs using the demo template
3. **After ship**: `/document-release` skill auto-updates README, ARCHITECTURE, CHANGELOG
4. **Periodic**: Auto-generate skill catalog and agent roster HTML
5. **When ready**: Deploy `docs/site/` to Vercel
