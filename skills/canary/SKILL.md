---
name: canary
preamble-tier: 2
version: 1.0.0
description: |
  Post-deploy canary monitoring. Watches the live app for console errors,
  performance regressions, and page failures using the browse daemon. Takes
  periodic screenshots, compares against pre-deploy baselines, and alerts
  on anomalies. Use when: "monitor deploy", "canary", "post-deploy check",
  "watch production", "verify deploy". (gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - AskUserQuestion
---
