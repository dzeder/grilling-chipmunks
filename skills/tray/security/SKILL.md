---
name: security
description: >
  Security and secret management — token rotation, .env protection, credential handling,
  emergency response protocols, and secure integration patterns.
  TRIGGER when: user manages API tokens, credentials, or .env files, asks about secret rotation,
  reports a leaked secret, or needs security audit guidance for integrations.
---

# Security & Secret Management Expert

## Description
Expert knowledge of security protocols, secret management, token rotation, and credential handling. Use when working with .env files, API tokens, or security configurations.

## When to Use
Invoke this skill when:
- Managing API tokens or credentials
- Questions about .env file handling
- Token rotation policies and procedures
- Security emergency response (leaked secrets)
- Access control and token permissions
- Automated secret protection setup
- Keywords: "token", "secret", ".env", "credentials", "rotation", "security", "API key"

## Delegation

- **tray-expert** — For Tray.io-specific token configuration and workspace credential management
- **sf-deploy** — For Salesforce Named Credential and Connected App security setup
- **org-connect** — For authenticating to Salesforce orgs securely
- Do not trigger for general Salesforce permission/profile configuration (use sf-metadata)

## Workflow

### 1. Assess the security context
Identify what type of secret or credential is involved (Tray token, SF Named Credential, API key, .env variable) and the environment (dev, staging, production).

### 2. Check current state
Verify .gitignore coverage, review existing secret storage, and confirm no credentials are committed to version control.

### 3. Apply the appropriate protocol
Follow the token rotation schedule, set up environment-specific tokens, or execute emergency response steps for leaked secrets.

### 4. Verify and document
Confirm the secret is properly stored, rotated, and scoped. Document the rotation in the security log.

## Reference Files
- `security-protocols.md` - Complete security documentation

## Quick Reference

### Critical Security Rules
1. **NEVER commit .env files** (always in .gitignore)
2. **Rotate tokens quarterly minimum**
3. **Use environment-specific tokens** (dev/staging/prod)
4. **Limit token scope** to minimum required
5. **Production secrets** in AWS Secrets Manager only

### Token Types (Tray)
- `TRAY_MASTER_TOKEN` - API operations
- `TRAY_ADMIN_TOKEN` - Admin dashboard
- `TRAY_WORKSPACE_ID` - Workspace identifier

### Emergency Response (Leaked Secrets)
1. **Immediate** (5 min): Rotate ALL tokens
2. **Verify** (15 min): Check git history
3. **Remediate** (1 hour): Document and review
4. **Post-incident** (24 hour): Security review

### Files Never Committed
- `.env`
- `credentials.json`
- `**/secrets/**`
- Private keys
