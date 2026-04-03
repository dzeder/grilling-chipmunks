# Agent Template

Standard structure for all agents in this repo. Use when creating new agents or auditing existing ones.

## Required Agent Definition Structure

```markdown
---
name: agent-name
description: >
  What this agent does. Include concrete examples of tasks it handles.
model: opus | sonnet
permissionMode: plan | acceptEdits
tools: [list of allowed tools]
disallowedTools: [explicit exclusions]
skills:
  - skill-1
  - skill-2
maxTurns: 15-20
---

# Agent Name — Role Title

One paragraph describing the agent's role and how it fits into the team structure.

## Responsibilities

Numbered list of what this agent does.

## Delegates To

| Situation | Agent | Why |
|-----------|-------|-----|
| [scenario] | [agent-name] | [reason] |

Required. If the agent is fully self-contained, state "This agent does not delegate."

## Does Not Handle

Bullet list of things this agent explicitly does NOT do. Prevents scope creep.

- [thing] — route to [other-agent] instead
- [thing] — out of scope for this pod

## When Blocked

What to do when the agent hits a blocker:

1. If missing context → ask the user via AskUserQuestion
2. If missing org access → escalate to [agent] or pause and report
3. If the task is outside scope → hand off to [agent]

## Completion Criteria

How to know the agent's work is done:

- [ ] [concrete deliverable 1]
- [ ] [concrete deliverable 2]
- [ ] [quality gate: e.g., "tests pass", "scoring rubric > 75"]

## Workflow

Step-by-step process the agent follows.
```

## Agent Quality Checklist

A well-defined agent has:

- [ ] YAML frontmatter with `name`, `description`, `model`, `permissionMode`, `tools`
- [ ] "Delegates To" section with concrete handoff rules
- [ ] "Does Not Handle" section with explicit exclusions
- [ ] "When Blocked" section with escalation paths
- [ ] "Completion Criteria" with measurable deliverables
- [ ] Scoped tool access (only tools the agent actually needs)
- [ ] Appropriate `maxTurns` (15 for focused tasks, 20 for complex orchestration)

## Model Selection Guide

| Model | Use when |
|-------|----------|
| **opus** | Architecture decisions, complex planning, multi-agent orchestration, code review |
| **sonnet** | Code generation, script creation, documentation, focused implementation |

## Permission Mode Guide

| Mode | Use when |
|------|----------|
| **plan** | Agent should research and plan but NOT edit files (strategists, architects) |
| **acceptEdits** | Agent needs to create or modify files (engineers, generators) |
