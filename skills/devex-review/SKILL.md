---
name: devex-review
preamble-tier: 3
version: 1.0.0
description: |
  Live developer experience audit. Uses the browse tool to actually TEST the
  developer experience: navigates docs, tries the getting started flow, times
  TTHW, screenshots error messages, evaluates CLI help text. Produces a DX
  scorecard with evidence. Compares against /plan-devex-review scores if they
  exist (the boomerang: plan said 3 minutes, reality says 8). Use when asked to
  "test the DX", "DX audit", "developer experience test", or "try the
  onboarding". Proactively suggest after shipping a developer-facing feature. (gstack)
  Voice triggers (speech-to-text aliases): "dx audit", "test the developer experience", "try the onboarding", "developer experience test".
allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
  - WebSearch
---
