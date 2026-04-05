# Model Router Rate Limits

| Model Tier | Requests/min | Tokens/min | Daily Budget |
|------------|-------------|------------|--------------|
| Haiku | 1,000 | 2,000,000 | Unlimited |
| Sonnet | 200 | 1,000,000 | $500/day |
| Opus | 20 | 200,000 | $100/day |

## Throttling Behavior

- Haiku: Virtually unlimited for classification workloads.
- Sonnet: Queued with priority when rate limited. Retry after 5s.
- Opus: Strict enforcement. Queued requests are rejected if daily budget is exceeded.

## Cost Controls

- Per-agent daily cost budgets are enforced.
- Alerts fire at 80% of daily budget.
- Budget resets at midnight UTC.
