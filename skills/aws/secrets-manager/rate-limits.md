# Secrets Manager Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| GetSecretValue | 10,000 per second | Per AWS account |
| CreateSecret | 50 per hour | Per AWS account |
| UpdateSecret | 100 per hour | Per AWS account |
| RotateSecret | 10 per hour | Per secret |
| DeleteSecret | 20 per hour | Per AWS account |
| ListSecrets | 100 per minute | Per AWS account |

## Throttling Behavior

Secrets Manager API calls are retried with exponential backoff on throttling. The `GetSecretValue` call supports caching via the AWS Secrets Manager caching client to reduce API calls.

## Caching

- Secret values are cached for 5 minutes by default.
- Cache TTL can be configured per service.
- Cache is invalidated on secret rotation.
