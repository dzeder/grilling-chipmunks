# Security and Secret Management Rules

**Purpose**: Critical security requirements and secret management protocol
**Audience**: AI assistants and developers handling sensitive credentials
**Related**: @.claude/docs/environment.md - Environment setup

---

## CRITICAL SECURITY REQUIREMENTS

### 1. Never Commit Secrets

**Absolute Requirements**:
- `.env` is in `.gitignore` and must **NEVER** be committed to git
- Use `.env.example` for templates (no actual values)
- Verified clean: .env has never been in git history (audited 2025-12-15)

**Files That Must Never Be Committed**:
- `.env` - Environment variables with secrets
- `credentials.json` - API credentials
- `**/secrets/**` - Any secrets directory
- Private keys, certificates with private keys
- Authentication tokens in any format

---

### 2. Token Rotation Policy

**Quarterly Minimum**:
- Rotate all tokens **every 3 months** (minimum)
- Document rotation dates in team password manager
- Set calendar reminders for rotation schedule

**Immediate Rotation Required**:
- If compromise suspected
- If token accidentally committed to git
- If employee with token access leaves team
- If security audit recommends rotation

**Rotation Process**:
1. Generate new token in Tray Dashboard
2. Update `.env` with new token
3. Test integration tools with new token
4. Revoke old token in Tray Dashboard
5. Document rotation date in password manager

---

### 3. Access Control

**Environment-Specific Tokens**:
- Use separate tokens for dev/staging/prod environments
- **Never** use production tokens in development
- **Never** share tokens between environments

**Minimum Required Scope**:
- Limit token permissions to minimum required scope
- Review token permissions quarterly
- Remove unnecessary permissions immediately

**Secret Storage**:
- **Development**: `.env` file (local only, gitignored)
- **Staging**: AWS Secrets Manager
- **Production**: AWS Secrets Manager (NOT .env files)

---

### 4. Automated Protection (Planned)

**Status**: Planned - See audit F-014

**Features When Implemented**:
- Pre-commit hooks will scan for secrets before git operations
- Automated detection using 18 secret patterns
- Blocks commits containing API keys, tokens, credentials
- Alerts developer immediately if secret detected

**Patterns Detected** (when implemented):
- API keys (Tray, AWS, Google, etc.)
- OAuth tokens
- Private keys
- Database credentials
- JWT secrets
- HMAC secrets
- Password hashes

---

### 5. Emergency Response Procedures

**If Secrets Leaked to Git**:

1. **Immediate Action** (within 5 minutes):
   - Rotate ALL potentially compromised tokens immediately
   - Revoke old tokens in all services
   - Alert security team

2. **Verify Exposure** (within 15 minutes):
   ```bash
   # Check git history for .env exposure
   git log --all --full-history -- .env

   # Check for any secrets in history
   git log --all --full-history -p | grep -i "TRAY_MASTER_TOKEN"
   ```

3. **Remediation** (within 1 hour):
   - If secrets in git history: Contact security team
   - If production secrets exposed: Escalate to incident response
   - Document incident in security log
   - Review access logs for unauthorized usage

4. **Post-Incident** (within 24 hours):
   - Conduct security review
   - Update secret management procedures
   - Implement additional controls if needed
   - Train team on lessons learned

**Contact Information**:
- **Security Team**: [Contact method]
- **Incident Response**: [Contact method]

---

## Obtaining Credentials

### TRAY_MASTER_TOKEN
1. Navigate to **Tray Dashboard** → **Settings** → **API Tokens**
2. Click **Create Master Token**
3. Copy token immediately (only shown once)
4. Add to `.env` file
5. **Never** commit `.env` to git

### TRAY_ADMIN_TOKEN
1. Navigate to **Tray Dashboard** → **Admin** → **API Tokens**
2. Click **Create Admin Token**
3. Copy token immediately (only shown once)
4. Add to `.env` file
5. **Never** commit `.env` to git

### TRAY_WORKSPACE_ID
**Option 1**: From Tray Dashboard
- Navigate to **Workspace Settings**
- Copy workspace ID from settings

**Option 2**: Run workspace discovery
```bash
node 04-utilities/tools/sync-tools/workspace-discovery.js
```

---

## Security Checklist

Before committing any changes:
- [ ] No `.env` file staged for commit
- [ ] No hardcoded secrets in code
- [ ] No credentials in comments
- [ ] No secrets in log statements
- [ ] All secrets in `.env` or AWS Secrets Manager
- [ ] `.env` is in `.gitignore`

Before deploying to production:
- [ ] All production secrets in AWS Secrets Manager
- [ ] No `.env` files in production containers
- [ ] Token permissions reviewed and minimized
- [ ] Token rotation schedule documented
- [ ] Access logs enabled and monitored

---

## See Also

- @.claude/docs/environment.md - Environment variable setup
- `.env.example` - Template for environment variables (no secrets)
- Tray Dashboard - Token generation and management
- AWS Secrets Manager - Production secret storage
