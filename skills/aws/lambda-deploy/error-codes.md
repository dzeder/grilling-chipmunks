# Lambda Deploy Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `LDEP-001` | Lambda Powertools not found in dependencies | Add `aws-lambda-powertools` to requirements.txt or package.json. |
| `LDEP-002` | CDK synth failed | Check CDK stack definition for syntax errors. |
| `LDEP-003` | Checkov security scan failed | Review Checkov output and fix flagged resources. |
| `LDEP-004` | Deployment failed | Check CloudFormation events for root cause. Automatic rollback triggered. |
| `LDEP-005` | Memory allocation exceeds limit | Reduce memory_mb to 3008 or below. |
| `LDEP-006` | Timeout exceeds limit | Reduce timeout_seconds to 900 or below. |
| `LDEP-007` | Invalid function naming convention | Use pattern `ohanafy-{env}-{service}-{function}`. |
| `LDEP-008` | Secrets found in environment variables | Move secrets to AWS Secrets Manager via the `secrets-manager` skill. |
| `LDEP-009` | Production deployment without approval | Production deployments require manual approval gate. |
| `LDEP-010` | Health check failed post-deploy | Function deployed but CloudWatch metrics show errors. Investigate logs. |
