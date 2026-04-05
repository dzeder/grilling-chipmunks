# Webhook Handler Rate Limits

## Incoming Webhook Throughput

| Metric | Limit | Notes |
|--------|-------|-------|
| Requests per second | 100 | Per webhook endpoint |
| Requests per minute | 3,000 | Sustained throughput cap |
| Payload size | 1 MB | Per request; reject larger payloads |
| Concurrent connections | 50 | Per handler instance |

## Tray.io Outbound Limits

Tray workflows generating webhooks are subject to their own execution limits:

| Metric | Limit | Notes |
|--------|-------|-------|
| Workflow executions | 1,000/hour | Per workspace |
| Webhook step timeout | 30 seconds | If handler does not respond in time, Tray retries |
| Tray auto-retry | 3 attempts | Exponential backoff on 5xx responses |

## Agent Dispatch Limits

| Metric | Limit | Notes |
|--------|-------|-------|
| Events queued per agent | 500 | Backpressure applied beyond this |
| Agent processing timeout | 60 seconds | Event re-queued if not acknowledged |
| Dead-letter queue size | 10,000 | Events moved here after max retries |

## Backoff Strategy

- Return HTTP 429 when incoming rate exceeds the per-second limit.
- Tray will retry with exponential backoff (built-in behavior).
- Internal dispatch uses exponential backoff: base 500ms, max 30s, 5 retries.
- After all retries exhausted, notify `#ops-alerts` and move event to dead-letter queue.
