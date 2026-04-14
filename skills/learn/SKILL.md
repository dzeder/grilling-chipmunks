---
name: learn
preamble-tier: 2
version: 1.0.0
description: |
  Manage project learnings. Review, search, prune, and export what gstack
  has learned across sessions. Use when asked to "what have we learned",
  "show learnings", "prune stale learnings", or "export learnings".
  Proactively suggest when the user asks about past patterns or wonders
  "didn't we fix this before?"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Glob
  - Grep
---

# Learn Skill

Manage project learnings and routing feedback.

## Routing Feedback Mode

When the user says "wrong skill", "should have been X", "that wasn't the right routing",
or "mis-routed":

1. Ask what the original request was (or infer from conversation context)
2. Ask which skill was invoked and which should have been used
3. Ask why the routing was wrong (what signal should have triggered the correct skill)
4. Append the entry to `docs/routing-feedback.yaml`:

```yaml
- date: "YYYY-MM-DD"
  request: "the original request"
  routed_to: wrong-skill-name
  should_have_been: correct-skill-name
  reason: "why the routing was wrong"
```

5. Check if 3+ similar feedback entries exist (same `should_have_been` or same pattern).
   If so, suggest adding a new compound routing rule to the CLAUDE.md routing table.
6. Confirm the feedback was recorded.

## Standard Mode

When the user asks about learnings, show learnings from the memory system and
any project-specific notes in `customers/*/notes.md`.
