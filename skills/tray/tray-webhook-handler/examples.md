# Webhook Handler Examples

## 1. Salesforce Record Change Event

Incoming payload from a Tray workflow triggered by Salesforce Change Data Capture:

```json
{
  "event_id": "evt-sf-001",
  "event_type": "sf.record.changed",
  "source": "tray-workflow-sf-cdc",
  "timestamp": "2026-04-04T12:00:00Z",
  "payload": {
    "object": "Account",
    "record_id": "001xx000003DGbYAAW",
    "change_type": "UPDATE",
    "changed_fields": ["Name", "BillingCity"]
  },
  "metadata": {
    "workflow_id": "wf-abc-123",
    "execution_id": "exec-789"
  }
}
```

```python
from skills.tray_ai.webhook_handler.skill import handle_webhook

result = handle_webhook(
    raw_body=payload_bytes,
    signature=request.headers["X-Tray-Signature"],
    secret="vault-resolved-shared-secret",
)
# WebhookValidationResult(valid=True, event_id="evt-sf-001", routed_to="salesforce_agent")
```

## 2. Schedule Trigger

Tray cron-based scheduler fires a periodic sync:

```json
{
  "event_id": "evt-sched-042",
  "event_type": "schedule.triggered",
  "source": "tray-scheduler-daily-sync",
  "timestamp": "2026-04-04T06:00:00Z",
  "payload": {
    "schedule_name": "daily-sf-to-s3-sync",
    "cron": "0 6 * * *"
  },
  "metadata": {
    "workflow_id": "wf-sched-456"
  }
}
```

## 3. Manual Trigger

Operator manually triggers a workflow from the Tray UI:

```json
{
  "event_id": "evt-manual-007",
  "event_type": "manual.triggered",
  "source": "tray-ui",
  "timestamp": "2026-04-04T15:30:00Z",
  "payload": {
    "triggered_by": "daniel@ohanafy.com",
    "reason": "Ad-hoc data backfill for Q1 accounts"
  },
  "metadata": {
    "workflow_id": "wf-backfill-999"
  }
}
```

## 4. HMAC Validation Only

Validate a signature without full routing:

```python
from skills.tray_ai.webhook_handler.skill import validate_hmac

is_valid = validate_hmac(
    payload_bytes=b'{"event_id": "test"}',
    signature="expected_hmac_hex",
    secret="shared-secret",
)
```

## 5. Handling an Unknown Event Type

If an unrecognized event type arrives, the handler raises `RoutingError` and notifies `#ops-alerts`:

```python
# event_type "custom.unknown" is not in the route table
# -> RoutingError: Unknown event type: custom.unknown
# -> #ops-alerts notification sent
```
