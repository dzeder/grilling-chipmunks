# Security Checklist

Quick reference for Ohanafy application security. Adapted from `addyosmani/agent-skills` security checklist with Ohanafy-specific additions.

## Pre-Commit Checks

- [ ] No secrets in code (`git diff --cached | grep -i "password\|secret\|api_key\|token"`)
- [ ] `.gitignore` covers: `.env`, `.env.local`, `*.pem`, `*.key`
- [ ] `.env.example` uses placeholder values (not real secrets)
- [ ] All credentials stored in AWS Secrets Manager

## Ohanafy-Specific Security

### Salesforce
- [ ] FLS/CRUD checks enforced on all DML operations
- [ ] No hardcoded org credentials — use Named Credentials
- [ ] Customer orgs are read-only unless explicitly authorized
- [ ] No prod org credentials in this repo
- [ ] API version >= v56.0

### Tray
- [ ] Webhook endpoints validate HMAC signatures
- [ ] No hardcoded connector auth tokens
- [ ] Tray workspace credentials in Secrets Manager, not code

### AWS
- [ ] No public S3 buckets
- [ ] Lambda functions use Powertools for structured logging
- [ ] No customer PII in logs
- [ ] CDK TypeScript only (no raw CloudFormation)
- [ ] Read replica only for production DB queries

### LLM Trust Boundaries
- [ ] No unsanitized external data injected into prompts
- [ ] No customer PII passed to LLM APIs
- [ ] Model routing follows policy (haiku/sonnet/opus tiers)

## Authentication

- [ ] Passwords hashed with bcrypt (>=12 rounds), scrypt, or argon2
- [ ] Session cookies: `httpOnly`, `secure`, `sameSite: 'lax'`
- [ ] Rate limiting on login endpoints
- [ ] JWT tokens validated (signature, expiration, issuer)

## Authorization

- [ ] Every protected endpoint checks authentication
- [ ] Every resource access checks ownership/role (prevents IDOR)
- [ ] API keys scoped to minimum necessary permissions

## Input Validation

- [ ] All user input validated at system boundaries
- [ ] Validation uses allowlists (not denylists)
- [ ] SQL queries parameterized (no string concatenation)
- [ ] HTML output encoded (use framework auto-escaping)
- [ ] File uploads: type restricted, size limited, content verified

## Data Protection

- [ ] Sensitive fields excluded from API responses
- [ ] Sensitive data not logged (passwords, tokens, PII)
- [ ] HTTPS for all external communication
- [ ] Database backups encrypted

## Dependency Security

```bash
npm audit                        # Audit dependencies
npm audit --audit-level=critical # Check critical only
npm audit fix                    # Auto-fix where possible
```

## OWASP Top 10 Quick Reference

| # | Vulnerability | Prevention |
|---|---|---|
| 1 | Broken Access Control | Auth checks on every endpoint, ownership verification |
| 2 | Cryptographic Failures | HTTPS, strong hashing, no secrets in code |
| 3 | Injection | Parameterized queries, input validation |
| 4 | Insecure Design | Threat modeling, spec-driven development |
| 5 | Security Misconfiguration | Security headers, minimal permissions, audit deps |
| 6 | Vulnerable Components | `npm audit`, keep deps updated, minimal deps |
| 7 | Auth Failures | Strong passwords, rate limiting, session management |
| 8 | Data Integrity Failures | Verify updates/dependencies, signed artifacts |
| 9 | Logging Failures | Log security events, don't log secrets or PII |
| 10 | SSRF | Validate/allowlist URLs, restrict outbound requests |

## Learned From

Adapted from `addyosmani/agent-skills` security-checklist (2026-04-09), extended with Ohanafy platform-specific controls.
