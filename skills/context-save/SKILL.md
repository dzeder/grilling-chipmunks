---
name: context-save
preamble-tier: 2
version: 1.0.0
description: |
  Save working context. Captures git state, decisions made, and remaining work
  so any future session can pick up without losing a beat.
  Use when asked to "save progress", "save state", "context save", or
  "save my work". Pair with /context-restore to resume later.
  Formerly /checkpoint — renamed because Claude Code treats /checkpoint as a
  native rewind alias in current environments, which was shadowing this skill.
  (gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
triggers:
  - save progress
  - save state
  - save my work
  - context save
---
