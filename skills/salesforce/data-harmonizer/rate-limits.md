# Rate Limits — data-harmonizer

## API Limits

| API | Limit | Window | Notes |
|-----|-------|--------|-------|
| Claude Sonnet | 50 requests | per minute | Per Anthropic account; mapping uses 1 call per file |
| DynamoDB reads | 25 RCU | per second | On-demand mode auto-scales, but initial burst is 25 |
| DynamoDB writes | 25 WCU | per second | On-demand mode auto-scales |
| Salesforce SOQL | 100 queries | per 24 hours | Per scratch org; dupe detection uses 1-2 queries per batch |

## Token Budget

| Component | Estimated Tokens | Notes |
|-----------|-----------------|-------|
| Prompt template | ~800 | SF schema + domain rules |
| Column headers | ~100-500 | Depends on number of columns |
| Sample rows (20) | ~1,000-3,000 | Depends on data density |
| Prior mappings (5) | ~200-500 | Few-shot examples |
| Response | ~500-2,000 | Structured JSON output |
| **Total per file** | **~2,500-7,000** | Well within Sonnet's context |

## Retry Policy

- Max attempts: 3
- Backoff: exponential with jitter
- Base delay: 2 seconds
- Max delay: 30 seconds
- Retry on: 429 (rate limit), 503 (service unavailable), timeout

## Usage Tracking

Track API usage per skill invocation. Log to CloudWatch:
- `skill/data-harmonizer/api_calls` — count per invocation
- `skill/data-harmonizer/rate_limit_hits` — rate limit encounters
- `skill/data-harmonizer/mapping_tokens` — tokens used per mapping call
