---
name: qa
preamble-tier: 4
version: 2.0.0
description: |
  Systematically QA test a web application and fix bugs found. Runs QA testing,
  then iteratively fixes bugs in source code, committing each fix atomically and
  re-verifying. Use when asked to "qa", "QA", "test this site", "find bugs",
  "test and fix", or "fix what's broken".
  Proactively suggest when the user says a feature is ready for testing
  or asks "does this work?". Three tiers: Quick (critical/high only),
  Standard (+ medium), Exhaustive (+ cosmetic). Produces before/after health scores,
  fix evidence, and a ship-readiness summary. For report-only mode, use /qa-only. (gstack)
  Voice triggers (speech-to-text aliases): "quality check", "test the app", "run QA".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - WebSearch
---
