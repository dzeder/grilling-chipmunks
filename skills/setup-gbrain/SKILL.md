---
name: setup-gbrain
preamble-tier: 2
version: 1.0.0
description: |
  Set up gbrain for this coding agent: install the CLI, initialize a
  local PGLite or Supabase brain, register MCP, capture per-remote trust
  policy. One command from zero to "gbrain is running, and this agent
  can call it." Use when: "setup gbrain", "connect gbrain", "start
  gbrain", "install gbrain", "configure gbrain for this machine". (gstack)
triggers:
  - setup gbrain
  - install gbrain
  - connect gbrain
  - start gbrain
  - configure gbrain
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---
