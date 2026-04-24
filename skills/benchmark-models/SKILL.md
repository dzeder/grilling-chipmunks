---
name: benchmark-models
preamble-tier: 1
version: 1.0.0
description: |
  Cross-model benchmark for gstack skills. Runs the same prompt through Claude,
  GPT (via Codex CLI), and Gemini side-by-side — compares latency, tokens, cost,
  and optionally quality via LLM judge. Answers "which model is actually best
  for this skill?" with data instead of vibes. Separate from /benchmark, which
  measures web page performance. Use when: "benchmark models", "compare models",
  "which model is best for X", "cross-model comparison", "model shootout". (gstack)
  Voice triggers (speech-to-text aliases): "compare models", "model shootout", "which model is best".
triggers:
  - cross model benchmark
  - compare claude gpt gemini
  - benchmark skill across models
  - which model should I use
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---
