"""
Pydantic schemas for Tray.ai Webhook Handler payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WebhookEvent(BaseModel):
    """Incoming webhook event payload from Tray.ai."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(
        ...,
        description="Event type for routing (e.g., sf.record.changed, schedule.triggered)",
    )
    source: str = Field(
        ..., description="Origin service or workflow name"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the event was emitted",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (workflow ID, execution ID, etc.)",
    )


class WebhookValidationResult(BaseModel):
    """Result of webhook validation and routing."""

    valid: bool
    event_id: str | None = None
    routed_to: str | None = None
    error: str | None = None


class WebhookRegistration(BaseModel):
    """Registration entry for a webhook endpoint."""

    name: str = Field(..., description="Webhook handler name")
    path: str = Field(..., description="URL path to listen on")
    secret_ref: str = Field(
        ..., description="Vault reference to shared HMAC secret"
    )
    event_types: list[str] = Field(
        ..., description="Event types this handler accepts"
    )
    target_agent: str = Field(
        ..., description="Ohanafy agent to route events to"
    )
    enabled: bool = Field(default=True)
