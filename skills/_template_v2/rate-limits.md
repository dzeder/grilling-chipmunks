# Rate Limits — {skill-name}

## API Limits

| API | Limit | Window | Notes |
|-----|-------|--------|-------|
| {API name} | {N} requests | per {period} | {additional notes} |

## Retry Policy

- Max attempts: 3
- Backoff: exponential with jitter
- Base delay: 2 seconds
- Max delay: 30 seconds
- Retry on: 429 (rate limit), 503 (service unavailable), timeout

## Usage Tracking

Track API usage per skill invocation. Log to CloudWatch:
- `skill/{skill-name}/api_calls` — count per invocation
- `skill/{skill-name}/rate_limit_hits` — rate limit encounters
