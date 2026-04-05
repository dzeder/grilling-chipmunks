# Webhook Handler Workflow Patterns

## Pattern 1: Signature-First Gateway

Every webhook request passes through HMAC validation before any business logic. This mirrors the n8n webhook node's built-in auth verification.

```
Request -> HMAC Validate -> Parse Payload -> Route to Agent
              |
              v (fail)
         Reject 401 + notify #ops-alerts
```

**Rule:** Never process an unsigned or incorrectly signed payload.

## Pattern 2: Fan-Out Routing (from Tray)

A single webhook endpoint can receive multiple event types. The handler inspects `event_type` and fans out to different agents, similar to Tray's "Branch" connector.

```
Webhook Endpoint
    |
    +-- sf.record.changed    --> Salesforce Agent
    +-- schedule.triggered   --> Scheduler Agent
    +-- manual.triggered     --> Manual Agent
    +-- (unknown)            --> #ops-alerts
```

## Pattern 3: Idempotency via Event ID (from n8n)

n8n deduplicates webhook deliveries using execution IDs. We use `event_id` to ensure the same event is not processed twice.

- Store processed `event_id` values in a short-lived cache (TTL: 1 hour).
- On duplicate delivery, return 200 OK without re-processing.
- Log the duplicate for observability.

## Pattern 4: Dead-Letter Queue (from Temporal)

Temporal uses a dead-letter queue for activities that exhaust retries. We apply the same for webhooks that cannot be routed or processed.

```
Webhook -> Parse -> Route -> Agent
                      |
                      v (max retries exceeded)
                Dead-Letter Queue + #ops-alerts notification
```

Events in the dead-letter queue can be manually inspected and replayed.

## Pattern 5: Request Buffering (from Tray)

Tray workflows may burst webhooks during high-volume operations (e.g., bulk SF data loads). The handler buffers incoming requests and processes them at a controlled rate.

- Accept and enqueue immediately (return 202 Accepted).
- Process from the queue at the configured throughput limit.
- Apply backpressure when the queue depth exceeds the threshold.

## Pattern 6: Webhook Registration as Config

Webhook handler configurations are stored as JSON in `skills/tray-ai/workflows/webhooks/`, following the same pattern as connector configs.

```json
{
  "name": "sf-cdc-handler",
  "path": "/webhooks/sf-cdc",
  "secret_ref": "vault://ohanafy/webhook-sf-secret",
  "event_types": ["sf.record.changed"],
  "target_agent": "salesforce_agent",
  "enabled": true
}
```
