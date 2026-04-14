---
name: investigate
preamble-tier: 2
version: 1.0.0
description: |
  Systematic debugging with root cause investigation. Four phases: investigate,
  analyze, hypothesize, implement. Iron Law: no fixes without root cause.
  Use when asked to "debug this", "fix this bug", "why is this broken",
  "investigate this error", or "root cause analysis".
  Proactively invoke this skill (do NOT debug directly) when the user reports
  errors, 500 errors, stack traces, unexpected behavior, "it was working
  yesterday", or is troubleshooting why something stopped working. (gstack)
chains_to:
  - review
  - ship
context_requires:
  conditional:
    - condition: "customer is set"
      path: "customers/{customer}/known-issues.md"
    - condition: "customer is set"
      path: "customers/{customer}/profile.md"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
  - WebSearch
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking debug scope boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking debug scope boundary..."
---
