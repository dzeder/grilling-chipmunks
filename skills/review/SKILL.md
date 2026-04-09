---
name: review
preamble-tier: 4
version: 1.1.0
description: |
  Pre-landing PR review. Analyzes diff against the base branch for SQL safety, LLM trust
  boundary violations, conditional side effects, and other structural issues. Use when
  asked to "review this PR", "code review", "pre-landing review", or "check my diff".
  Proactively suggest when the user is about to merge or land code changes. (gstack)
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/code-review-and-quality/SKILL.md
    adapted: "2026-04-09"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
  - WebSearch
---

# Review Process

## Five-Axis Review

Every review evaluates code across these dimensions:

### 1. Correctness
- Does it match the spec or task requirements?
- Are edge cases handled (null, empty, boundary values)?
- Are error paths handled (not just the happy path)?
- Do tests cover the change adequately?

### 2. Readability
- Are names descriptive and consistent with project conventions?
- Is the control flow straightforward?
- Are abstractions earning their complexity?
- Any dead code artifacts (no-op variables, backwards-compat shims)?

### 3. Architecture
- Does it follow existing patterns or introduce a new one? If new, is it justified?
- Does it maintain clean module boundaries?
- Are dependencies flowing in the right direction?

### 4. Security
- Is user input validated and sanitized?
- Are secrets kept out of code, logs, and version control?
- Are SQL queries parameterized?
- Is data from external sources treated as untrusted?

### 5. Performance
- Any N+1 query patterns?
- Any unbounded loops or unconstrained data fetching?
- Any missing pagination on list endpoints?

## Ohanafy-Specific Checks

- **Salesforce:** FLS/CRUD enforcement, bulkification, API version >= v56.0
- **Tray:** HMAC signature validation on webhooks, no hardcoded auth tokens
- **AWS:** No public S3 buckets, Secrets Manager for credentials, no inline secrets in CDK
- **LLM trust boundaries:** No unsanitized external data in prompts, no customer PII in logs

## Severity Labels

| Prefix | Meaning | Author Action |
|--------|---------|---------------|
| **Critical:** | Blocks merge — security vulnerability, data loss, broken functionality | Must fix |
| *(no prefix)* | Required change | Must address before merge |
| **Nit:** | Minor, optional — formatting, style | Author may ignore |
| **FYI** | Informational only — context for future reference | No action needed |

## Review Steps

1. **Understand context** — What is this change trying to accomplish?
2. **Review tests first** — Tests reveal intent and coverage gaps
3. **Review implementation** — Walk through with the five axes
4. **Categorize findings** — Label every comment with severity
5. **Verify the verification** — What tests were run? Did the build pass?

## Red Flags

- PRs merged without any review
- "LGTM" without evidence of actual review
- Large PRs that are "too big to review properly" (split them)
- No regression tests with bug fix PRs
- Accepting "I'll fix it later" — it never happens
- AI-generated code needs more scrutiny, not less
