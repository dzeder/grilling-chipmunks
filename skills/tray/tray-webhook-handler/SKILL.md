# Tray.ai Webhook Handler Skill

## Purpose

Handle incoming webhooks from Tray.ai workflows and external services. Validate HMAC signatures to ensure authenticity. Route validated payloads to the appropriate Ohanafy agent for processing.

## Important Constraints

- **No CLI exists.** All configuration is stored as JSON in `skills/tray-ai/workflows/`.
- **Tray-first rule:** Always check existing webhook handlers before creating new ones.
- **All errors must notify `#ops-alerts`.**
- **Every incoming webhook must pass HMAC validation** before any processing occurs.

## Capabilities

- Receive HTTP webhook payloads from Tray.ai workflow triggers.
- Validate HMAC-SHA256 signatures using shared secrets.
- Parse and validate payloads against registered schemas.
- Route validated events to the correct Ohanafy agent based on event type.
- Log all webhook activity for audit and debugging.

## Webhook Sources

| Source | Trigger Type | Typical Payload |
|--------|-------------|-----------------|
| Salesforce | Platform Event / Change Data Capture | Record change JSON |
| Tray Scheduler | Cron-based schedule trigger | Schedule metadata |
| Manual | Tray UI manual trigger | User-supplied JSON |
| External | Third-party service callback | Varies by service |

## HMAC Validation Flow

1. Extract `X-Tray-Signature` header from incoming request.
2. Compute HMAC-SHA256 of the raw request body using the shared secret.
3. Compare computed signature with the header value (constant-time).
4. Reject with `HMACValidationError` if signatures do not match.

## Routing

After validation, the handler inspects the payload's `event_type` field and dispatches to the registered agent. Unknown event types are logged and sent to `#ops-alerts`.

## Error Handling

All errors raise typed exceptions (`HMACValidationError`, `PayloadError`, `RoutingError`) and send notifications to `#ops-alerts`. See `error-codes.md` for details.

## Dependencies

- `pydantic` for payload validation.
- `hmac` and `hashlib` from Python stdlib for signature verification.
- Ohanafy agent router for event dispatch.
