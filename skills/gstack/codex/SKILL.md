---
name: codex
preamble-tier: 3
version: 1.0.0
description: |
  OpenAI Codex CLI wrapper — three modes. Code review: independent diff review via
  codex review with pass/fail gate. Challenge: adversarial mode that tries to break
  your code. Consult: ask codex anything with session continuity for follow-ups.
  The "200 IQ autistic developer" second opinion. Use when asked to "codex review",
  "codex challenge", "ask codex", "second opinion", or "consult codex". (gstack)
  Voice triggers (speech-to-text aliases): "code x", "code ex", "get another opinion".
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---
