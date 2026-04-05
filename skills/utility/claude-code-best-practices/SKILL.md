---
name: claude-code-best-practices
description: |
  Reference guide for Claude Code best practices — skills authoring, subagent patterns,
  memory management, MCP configuration, orchestration workflows, and power-user tips.
  Apply when:
  - Creating or improving skills, agents, or commands
  - Setting up MCP servers or Claude Code configuration
  - Designing multi-agent orchestration workflows
  - Reviewing whether our patterns follow current best practices
  DO NOT TRIGGER when:
  - Working on Salesforce-specific code (use sf-* skills)
  - Working on integration code (use tray-*/ohfy-* skills)
  - Debugging live org issues (use org-connect)
---

## Reference Material

All vendored from [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice).

### Core Best Practices (read these first)
- `references/claude-code-best-practices/best-practice/claude-skills.md` — Skill authoring patterns
- `references/claude-code-best-practices/best-practice/claude-subagents.md` — Subagent design
- `references/claude-code-best-practices/best-practice/claude-commands.md` — Command patterns
- `references/claude-code-best-practices/best-practice/claude-memory.md` — Memory management
- `references/claude-code-best-practices/best-practice/claude-mcp.md` — MCP server configuration
- `references/claude-code-best-practices/best-practice/claude-settings.md` — Settings and permissions
- `references/claude-code-best-practices/best-practice/claude-power-ups.md` — Advanced techniques

### Implementation Guides
- `references/claude-code-best-practices/implementation/claude-skills-implementation.md`
- `references/claude-code-best-practices/implementation/claude-subagents-implementation.md`
- `references/claude-code-best-practices/implementation/claude-commands-implementation.md`
- `references/claude-code-best-practices/implementation/claude-agent-teams-implementation.md`
- `references/claude-code-best-practices/implementation/claude-scheduled-tasks-implementation.md`

### Orchestration
- `references/claude-code-best-practices/orchestration/orchestration-workflow.md` — Multi-agent coordination patterns

### Reports (deep dives)
- `references/claude-code-best-practices/reports/claude-skills-for-larger-mono-repos.md` — Monorepo skill organization
- `references/claude-code-best-practices/reports/claude-agent-memory.md` — Agent memory architecture
- `references/claude-code-best-practices/reports/claude-advanced-tool-use.md` — Advanced tool patterns

### Tips
- `references/claude-code-best-practices/tips/` — Collected tips from Boris Cherny, Thariq, and others

## Keeping Up to Date

```bash
# Preview what changed upstream
bash scripts/update-best-practices.sh

# Apply the update
bash scripts/update-best-practices.sh --apply
```

Weekly GitHub Action also checks automatically and opens a PR if upstream has changes.

## Examples

- "I want to create a new skill for Tray error handling" -- consult skill authoring patterns before writing
- "How should I structure subagents for the FDE team?" -- review subagent design and monorepo organization
- "Is our CLAUDE.md following best practices?" -- compare against memory vs CLAUDE.md tradeoffs guidance

## When to Consult

Before creating a new skill or agent, read:
1. `claude-skills.md` for skill authoring patterns
2. `claude-subagents.md` for agent design
3. `claude-skills-for-larger-mono-repos.md` for monorepo-specific guidance

Before changing CLAUDE.md or settings, read:
1. `claude-settings.md` for configuration patterns
2. `claude-memory.md` for memory vs CLAUDE.md tradeoffs
