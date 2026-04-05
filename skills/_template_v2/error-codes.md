# Error Codes — {skill-name}

| Code | Message | Cause | Resolution |
|------|---------|-------|------------|
| `EXAMPLE_ERROR` | Example error message | {What causes this} | {How to fix it} |
| `VALIDATION_ERROR` | Invalid input parameters | Missing or malformed input | Check input against schema |
| `RATE_LIMIT_ERROR` | API rate limit exceeded | Too many requests | Wait and retry with backoff |
| `AUTH_ERROR` | Authentication failed | Invalid or expired credentials | Check .env credentials |
| `TIMEOUT_ERROR` | Request timed out | Slow external service | Retry with increased timeout |
