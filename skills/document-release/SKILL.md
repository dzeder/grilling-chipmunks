---
name: document-release
preamble-tier: 2
version: 1.0.0
description: |
  Post-ship documentation update. Reads all project docs, cross-references the
  diff, updates README/ARCHITECTURE/CONTRIBUTING/CLAUDE.md to match what shipped,
  polishes CHANGELOG voice, cleans up TODOS, and optionally bumps VERSION. Use when
  asked to "update the docs", "sync documentation", or "post-ship docs".
  Proactively suggest after a PR is merged or code is shipped. (gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---
