# IAM Audit Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `IAM-001` | Access denied to IAM APIs | Ensure the audit role has required read permissions. See `iam-permissions.md`. |
| `IAM-002` | Role not found | Verify the role name exists in the target account. |
| `IAM-003` | Policy not found | Verify the policy ARN is correct. |
| `IAM-004` | User not found | Verify the IAM user name exists. |
| `IAM-005` | Rate limited by AWS IAM API | Retry with exponential backoff. Audit will resume automatically. |
| `IAM-006` | Invalid policy document | The policy JSON could not be parsed. Check for syntax errors. |
| `IAM-007` | Audit timeout | Large accounts may exceed timeout. Use targeted audits instead of full_audit. |
| `IAM-008` | Cross-account access denied | Cannot read trust policies in external accounts. Audit local trust policies only. |
