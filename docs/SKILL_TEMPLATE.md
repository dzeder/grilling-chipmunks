# Skill Template

Standard structure for all skills in this repo. Use when creating new skills or auditing existing ones.

## Required SKILL.md Structure

```markdown
---
name: skill-name
description: >
  One-paragraph description. Must include:
  - TRIGGER when: conditions that activate this skill
  - DO NOT TRIGGER when: conditions that should route elsewhere (with skill names)
learned_from:                          # optional — upstream repos that inspired this skill
  - repo: owner/repo-name             # GitHub repo (must be in watchers/repos.yaml)
    file: path/to/pattern.md           # specific file that informed this skill
    adapted: "YYYY-MM-DD"             # when the adaptation was made
metadata:
  version: "1.0.0"
  scoring: "N points across M categories" (if applicable)
---

# skill-name: Full Title

One-line summary of what this skill does and when to use it.

## When This Skill Owns the Task

Bullet list of scenarios where this skill is the right choice.

## Delegate Elsewhere

| Scenario | Route to |
|----------|----------|
| description of case | [skill-name](../skill-name/SKILL.md) |

This section is required. If the skill has no handoffs, state "This skill is self-contained."

## Required Context to Gather First

What information the skill needs before it can act (questions to ask, files to read, etc.)

## Workflow

Step-by-step process the skill follows. Number the steps.

## Scoring Rubric (if applicable)

Use 0-100 scale with 4 tiers:

| Score | Tier | Meaning |
|-------|------|---------|
| 90-100 | Excellent | Production-ready, no issues |
| 75-89 | Good | Minor improvements needed |
| 60-74 | Partial | Significant gaps, needs work |
| <60 | Insufficient | Major rework required |

Break the 100 points into named categories relevant to the domain.

## Examples

At least one "when to use" and one "when NOT to use" example.

### Use this skill when:
- [concrete scenario]

### Do NOT use this skill when:
- [concrete scenario] — use [other-skill] instead
```

## Upstream Lineage (`learned_from`)

When a skill was inspired by or adapted from an upstream pattern, add a `learned_from` entry to the frontmatter. This enables the compounding knowledge loop:

1. **Watcher** detects upstream changes in `watchers/repos.yaml` repos
2. **Lineage check** finds YOUR skills that cite the changed repo
3. **PR/issue** flags those skills for review — you may want to adapt the improvement
4. **You adapt** (or not) and the cycle repeats

```yaml
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/error-recovery.md
    adapted: "2026-04-04"
  - repo: shanraisshan/claude-code-best-practice
    file: best-practice/claude-skills.md
    adapted: "2026-03-15"
```

Rules:
- `repo` must be a repo tracked in `watchers/repos.yaml`
- `file` is the specific upstream file (helps you find it when upstream changes)
- `adapted` is when you incorporated the pattern (absolute date, not relative)
- Multiple entries are fine — a skill can draw from many sources
- Only add when genuinely useful — not every skill needs lineage

## Required Directory Structure

```
skills/skill-name/
  SKILL.md              # Main skill definition (required)
  references/           # Supporting docs (optional but recommended)
    source-index.md     # For ohfy-* skills: auto-generated from sync
    last-synced.txt     # For ohfy-* skills: sync timestamp
    *.md                # Domain-specific references
```

## Quality Checklist

Run `bash scripts/lint-skills.sh` to check all skills. A passing skill has:

- [ ] YAML frontmatter with `name`, `description`, and trigger/no-trigger rules
- [ ] "Delegate Elsewhere" section with cross-links to related skills
- [ ] At least one example of when to use and when not to use
- [ ] Scoring rubric (for skills that produce scored output)
- [ ] Workflow section with numbered steps
- [ ] References directory (for domain-specific skills)

## Scoring System Conventions

All scored skills should use the 0-100 scale to keep reports comparable. Break points into categories:

- **Salesforce skills**: categories like bulkification, security, testing, maintainability
- **Integration skills**: categories like error handling, idempotency, performance, logging
- **Design skills**: categories like consistency, accessibility, hierarchy, responsiveness

The total across categories should equal the max score stated in frontmatter metadata.
