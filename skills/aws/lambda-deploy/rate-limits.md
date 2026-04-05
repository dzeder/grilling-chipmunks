# Lambda Deploy Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| `cdk deploy` invocations | 10 per hour | Per environment |
| Concurrent deployments | 1 | Per function |
| CloudFormation stack updates | 60 per hour | Per AWS account |
| Lambda function creates | 100 per region | Per AWS account |
| Lambda Layers published | 50 per day | Per region |

## Throttling Behavior

When rate limits are hit, the skill will retry with exponential backoff up to 3 times. If all retries fail, the deployment is aborted and a `LDEP-004` error is returned.

## Production Guardrails

- Production deployments are limited to 5 per hour to prevent rapid-fire changes.
- A cooldown period of 10 minutes is enforced between consecutive prod deployments of the same function.
