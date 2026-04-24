---
name: context-restore
preamble-tier: 2
version: 1.0.0
description: |
  Restore working context saved earlier by /context-save. Loads the most recent
  saved state (across all branches by default) so you can pick up where you
  left off — even across Conductor workspace handoffs.
  Use when asked to "resume", "restore context", "where was I", or
  "pick up where I left off". Pair with /context-save.
  Formerly /checkpoint resume — renamed because Claude Code treats /checkpoint
  as a native rewind alias in current environments. (gstack)
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - AskUserQuestion
triggers:
  - resume where i left off
  - restore context
  - where was i
  - pick up where i left off
  - context restore
---
