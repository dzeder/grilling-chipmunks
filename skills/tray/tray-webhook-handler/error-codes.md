# Webhook Handler Error Codes

All errors notify `#ops-alerts` before raising.

## HMACValidationError

Raised when the HMAC signature on an incoming webhook does not match.

| Code | Meaning | Recovery |
|------|---------|----------|
| `HMAC_SIGNATURE_MISMATCH` | Computed HMAC does not match `X-Tray-Signature` header | Verify shared secret matches between Tray workflow and handler config |
| `HMAC_MISSING_HEADER` | `X-Tray-Signature` header not present in request | Ensure Tray workflow is configured to send signatures |
| `HMAC_SECRET_NOT_FOUND` | Shared secret reference could not be resolved from vault | Check `secret_ref` in webhook registration |

## PayloadError

Raised when the webhook body is malformed or fails validation.

| Code | Meaning | Recovery |
|------|---------|----------|
| `PAYLOAD_INVALID_JSON` | Request body is not valid JSON | Check upstream workflow output format |
| `PAYLOAD_SCHEMA_FAILED` | JSON is valid but does not match `WebhookEvent` schema | Verify required fields: `event_id`, `event_type`, `source` |
| `PAYLOAD_EMPTY` | Request body is empty | Check Tray workflow trigger configuration |
| `PAYLOAD_TOO_LARGE` | Payload exceeds maximum allowed size (1 MB default) | Split large payloads or increase limit in config |

## RoutingError

Raised when no agent is registered for the incoming event type.

| Code | Meaning | Recovery |
|------|---------|----------|
| `ROUTE_UNKNOWN_EVENT_TYPE` | `event_type` not found in the routing table | Register an agent for this event type or update the route table |
| `ROUTE_AGENT_UNAVAILABLE` | Target agent is registered but not responding | Check agent health; may need restart or scaling |
| `ROUTE_DISPATCH_FAILED` | Agent accepted the event but returned an error | Inspect agent logs for the specific failure |
