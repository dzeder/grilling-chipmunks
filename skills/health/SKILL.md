---
name: health
preamble-tier: 2
version: 1.0.0
description: |
  Code quality dashboard. Wraps existing project tools (type checker, linter,
  test runner, dead code detector, shell linter), computes a weighted composite
  0-10 score, and tracks trends over time. Use when: "health check",
  "code quality", "how healthy is the codebase", "run all checks",
  "quality score". (gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---
