---
name: pair-agent
version: 0.1.0
description: |
  Pair a remote AI agent with your browser. One command generates a setup key and
  prints instructions the other agent can follow to connect. Works with OpenClaw,
  Hermes, Codex, Cursor, or any agent that can make HTTP requests. The remote agent
  gets its own tab with scoped access (read+write by default, admin on request).
  Use when asked to "pair agent", "connect agent", "share browser", "remote browser",
  "let another agent use my browser", or "give browser access". (gstack)
  Voice triggers (speech-to-text aliases): "pair agent", "connect agent", "share my browser", "remote browser access".
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion

---
