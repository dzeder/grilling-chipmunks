---
name: cso
preamble-tier: 2
version: 2.0.0
description: |
  Chief Security Officer mode. Infrastructure-first security audit: secrets archaeology,
  dependency supply chain, CI/CD pipeline security, LLM/AI security, skill supply chain
  scanning, plus OWASP Top 10, STRIDE threat modeling, and active verification.
  Two modes: daily (zero-noise, 8/10 confidence gate) and comprehensive (monthly deep
  scan, 2/10 bar). Trend tracking across audit runs.
  Use when: "security audit", "threat model", "pentest review", "OWASP", "CSO review". (gstack)
  Voice triggers (speech-to-text aliases): "see-so", "see so", "security review", "security check", "vulnerability scan", "run security".
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Agent
  - WebSearch
  - AskUserQuestion
---
