# RDS Query Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Queries per minute | 60 | Per database |
| Concurrent connections | 10 | Per environment |
| Max result set size | 10 MB | Per query |
| Max rows returned | 10,000 | Per query |
| Query timeout | 120 seconds | Per query |

## Throttling Behavior

When the connection pool is exhausted, new queries are queued for up to 30 seconds. If a connection does not become available, the query fails with `RDS-007`.

## Production Guardrails

- Production queries are logged to CloudWatch with the query hash (not the full query) for audit.
- Queries scanning more than 100,000 rows trigger a warning.
