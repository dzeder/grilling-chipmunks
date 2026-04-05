# S3 Manager Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Bucket creation | 10 per hour | Per AWS account |
| Object uploads | 3,500 PUT/s | Per prefix |
| Object downloads | 5,500 GET/s | Per prefix |
| List requests | 1,000 per minute | Per bucket |
| Bucket deletion | 5 per hour | Per AWS account |

## Throttling Behavior

S3 API rate limits are managed by AWS. The skill implements exponential backoff with jitter for `SlowDown` responses. Uploads exceeding 100 MB are automatically switched to multipart upload.

## Cost Awareness

- PUT/COPY/POST/LIST requests are billed. Avoid unnecessary list operations.
- Data transfer out of S3 incurs charges. Use VPC endpoints where possible.
