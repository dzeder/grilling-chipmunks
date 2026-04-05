"""
Tray.ai Webhook Handler Skill

Handles incoming webhooks from Tray.ai workflows. Validates HMAC
signatures and routes payloads to the appropriate Ohanafy agent.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any

from .schema import WebhookEvent, WebhookValidationResult

logger = logging.getLogger(__name__)


class HMACValidationError(Exception):
    """HMAC signature verification failed."""


class PayloadError(Exception):
    """Webhook payload is malformed or fails schema validation."""


class RoutingError(Exception):
    """No agent registered for the given event type."""


def _notify_ops_alerts(message: str) -> None:
    """Send notification to #ops-alerts. Stub -- wire to Slack connector."""
    logger.error("[#ops-alerts] %s", message)


def validate_hmac(
    payload_bytes: bytes,
    signature: str,
    secret: str,
) -> bool:
    """
    Validate HMAC-SHA256 signature of a webhook payload.

    Args:
        payload_bytes: Raw request body bytes.
        signature: Value from X-Tray-Signature header.
        secret: Shared secret for HMAC computation.

    Returns:
        True if signature is valid.

    Raises:
        HMACValidationError: If signature does not match.
    """
    computed = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, signature):
        _notify_ops_alerts("HMAC validation failed for incoming webhook")
        raise HMACValidationError("Signature mismatch")
    return True


def parse_payload(raw_body: bytes) -> WebhookEvent:
    """
    Parse and validate a webhook payload.

    Raises:
        PayloadError: If the body is not valid JSON or fails schema validation.
    """
    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        _notify_ops_alerts(f"Webhook payload is not valid JSON: {exc}")
        raise PayloadError(f"Invalid JSON: {exc}") from exc

    try:
        return WebhookEvent(**data)
    except Exception as exc:
        _notify_ops_alerts(f"Webhook payload schema validation failed: {exc}")
        raise PayloadError(f"Schema validation failed: {exc}") from exc


# Agent routing registry -- maps event_type to handler function name.
_ROUTE_TABLE: dict[str, str] = {
    "sf.record.changed": "salesforce_agent",
    "schedule.triggered": "scheduler_agent",
    "manual.triggered": "manual_agent",
}


def route_event(event: WebhookEvent) -> str:
    """
    Route a validated webhook event to the appropriate agent.

    Returns:
        Name of the agent the event was dispatched to.

    Raises:
        RoutingError: If no agent is registered for the event type.
    """
    agent = _ROUTE_TABLE.get(event.event_type)
    if agent is None:
        _notify_ops_alerts(f"No agent registered for event type: {event.event_type}")
        raise RoutingError(f"Unknown event type: {event.event_type}")

    logger.info("Routing event %s to agent %s", event.event_id, agent)
    # TODO: dispatch to actual agent runtime
    return agent


def handle_webhook(
    raw_body: bytes,
    signature: str,
    secret: str,
) -> WebhookValidationResult:
    """
    Full webhook handling pipeline: validate -> parse -> route.
    """
    try:
        validate_hmac(raw_body, signature, secret)
        event = parse_payload(raw_body)
        agent = route_event(event)
        return WebhookValidationResult(
            valid=True,
            event_id=event.event_id,
            routed_to=agent,
        )
    except (HMACValidationError, PayloadError, RoutingError):
        raise
    except Exception as exc:
        _notify_ops_alerts(f"Webhook handling failed unexpectedly: {exc}")
        raise PayloadError(f"Unexpected error: {exc}") from exc


def run(action: str, **kwargs: Any) -> Any:
    """Entry point for the skill runner."""
    actions = {
        "handle": handle_webhook,
        "validate_hmac": validate_hmac,
        "parse": parse_payload,
        "route": route_event,
    }
    fn = actions.get(action)
    if fn is None:
        _notify_ops_alerts(f"Unknown webhook action: {action}")
        raise PayloadError(f"Unknown action: {action}")
    return fn(**kwargs)
