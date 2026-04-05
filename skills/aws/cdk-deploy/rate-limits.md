# CDK Deploy Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| `cdk deploy` invocations | 10 per hour | Per environment |
| Concurrent stack updates | 1 | Per stack |
| CloudFormation API calls | 60 per minute | Per AWS account |
| Checkov scans | 20 per hour | Per execution environment |

## Throttling Behavior

CloudFormation throttling triggers automatic retry with exponential backoff. The skill waits for in-progress stack updates to complete before initiating new ones.

## Production Guardrails

- Maximum 3 production deployments per hour.
- 15-minute cooldown between consecutive prod deployments of the same stack.
- All prod deployments logged to audit trail.
