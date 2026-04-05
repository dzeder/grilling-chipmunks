---
name: checkpoint
preamble-tier: 2
version: 1.0.0
description: |
  Save and resume working state checkpoints. Captures git state, decisions made,
  and remaining work so you can pick up exactly where you left off — even across
  Conductor workspace handoffs between branches.
  Use when asked to "checkpoint", "save progress", "where was I", "resume",
  "what was I working on", or "pick up where I left off".
  Proactively suggest when a session is ending, the user is switching context,
  or before a long break. (gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---
