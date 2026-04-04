---
name: qa-only
preamble-tier: 4
version: 1.0.0
description: |
  Report-only QA testing. Systematically tests a web application and produces a
  structured report with health score, screenshots, and repro steps — but never
  fixes anything. Use when asked to "just report bugs", "qa report only", or
  "test but don't fix". For the full test-fix-verify loop, use /qa instead.
  Proactively suggest when the user wants a bug report without any code changes. (gstack)
  Voice triggers (speech-to-text aliases): "bug report", "just check for bugs".
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
  - WebSearch
---
