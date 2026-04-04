---
name: setup-browser-cookies
preamble-tier: 1
version: 1.0.0
description: |
  Import cookies from your real Chromium browser into the headless browse session.
  Opens an interactive picker UI where you select which cookie domains to import.
  Use before QA testing authenticated pages. Use when asked to "import cookies",
  "login to the site", or "authenticate the browser". (gstack)
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---
