# IAM Audit Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Full account audit | 2 per hour | Per AWS account |
| Targeted audits (role/policy/user) | 30 per hour | Per AWS account |
| Cross-account audit | 5 per hour | Per AWS account |
| IAM API calls | 100 per second | Per AWS account (AWS limit) |

## Throttling Behavior

IAM API throttling triggers automatic retry with exponential backoff. Large accounts with 1000+ roles may take several minutes for a full audit.

## Scheduling

- Full audits should be scheduled weekly via EventBridge.
- Targeted audits run on-demand after IAM changes.
