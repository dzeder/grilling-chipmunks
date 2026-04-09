---
name: ship
preamble-tier: 4
version: 1.1.0
description: |
  Ship workflow: detect + merge base branch, run tests, review diff, bump VERSION,
  update CHANGELOG, commit, push, create PR. Use when asked to "ship", "deploy",
  "push to main", "create a PR", "merge and push", or "get it deployed".
  Proactively invoke this skill (do NOT push/PR directly) when the user says code
  is ready, asks about deploying, wants to push code up, or asks to create a PR. (gstack)
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/shipping-and-launch/SKILL.md
    adapted: "2026-04-09"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
  - WebSearch
---

# Pre-Ship Checklist

## Code Quality
- [ ] All tests pass (unit, integration, e2e)
- [ ] Build succeeds with no warnings
- [ ] Lint and type checking pass
- [ ] Code reviewed and approved
- [ ] No TODO comments that should be resolved before launch
- [ ] No `console.log` debugging statements in production code
- [ ] Error handling covers expected failure modes

## Security
- [ ] No secrets in code or version control
- [ ] Dependencies audited — no critical vulnerabilities
- [ ] Input validation on all user-facing endpoints
- [ ] Authentication and authorization checks in place

## Ohanafy-Specific
- [ ] Salesforce: FLS/CRUD checks, API version >= v56.0, no prod org credentials
- [ ] Tray: HMAC webhook validation, no hardcoded connector auth
- [ ] AWS: Secrets Manager for credentials, no public S3 buckets
- [ ] No customer PII in logs

## Rollback Strategy

Every deployment needs a rollback plan before it happens:

**When to roll back immediately:**
- Error rate increases > 2x baseline
- Data integrity issues detected
- Security vulnerability discovered
- User-reported issues spike

**Rollback steps:**
1. Disable feature flag (if applicable) OR revert commit and redeploy
2. Verify rollback: health check, error monitoring
3. Communicate: notify team of rollback and reason

## Post-Deploy Verification

In the first hour after deploy:
1. Check health endpoints return 200
2. Check error monitoring (no new error types)
3. Check latency (no regression)
4. Test the critical user flow manually
5. Verify logs are flowing and readable
