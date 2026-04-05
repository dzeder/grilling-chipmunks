"""
Pydantic schemas for the Tray.io Connector Discovery pipeline.

Mirrors the content-watcher schema pattern: structured models for each
pipeline stage (discover → score → generate knowledge → route).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ConnectorCategory(str, Enum):
    CRM = "crm"
    ERP_ACCOUNTING = "erp_accounting"
    EDI_SUPPLY_CHAIN = "edi_supply_chain"
    ECOMMERCE = "ecommerce"
    COMMUNICATION = "communication"
    STORAGE_DATA = "storage_data"
    DEVELOPER_TOOLS = "developer_tools"
    OTHER = "other"


class CurrentUsage(str, Enum):
    ACTIVE = "active"
    CONFIGURED_UNUSED = "configured_unused"
    NOT_CONFIGURED = "not_configured"


class OpportunityType(str, Enum):
    OPTIMIZE_EXISTING = "optimize_existing"
    NEW_INTEGRATION = "new_integration"
    EXPLORATION = "exploration"
    NOT_RELEVANT = "not_relevant"


# ---------------------------------------------------------------------------
# Discovery stage
# ---------------------------------------------------------------------------


class TrayConnectorEntry(BaseModel):
    """A single connector discovered from the Tray.io platform."""

    name: str = Field(..., description="Connector identifier (e.g. 'salesforce', 'quickbooks')")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(default="", description="What the connector does")
    category: ConnectorCategory = Field(default=ConnectorCategory.OTHER)
    auth_types: list[str] = Field(default_factory=list, description="Supported auth mechanisms")
    operations: list[str] = Field(default_factory=list, description="Available operation names")
    operation_count: int = Field(default=0, description="Total number of operations")
    documentation_url: str | None = Field(default=None, description="Link to Tray docs page")
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    last_refreshed: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Scoring stage
# ---------------------------------------------------------------------------


class ScoringDimension(BaseModel):
    """Score for a single relevance dimension."""

    name: str
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = ""


class RelevanceAssessment(BaseModel):
    """Scoring result for a connector's relevance to Ohanafy."""

    connector_name: str
    overall_score: float = Field(..., ge=0.0, le=1.0)
    dimensions: list[ScoringDimension] = Field(default_factory=list)
    rationale: str = Field(default="", description="2-3 sentence explanation")
    ohanafy_use_cases: list[str] = Field(default_factory=list)
    current_usage: CurrentUsage = Field(default=CurrentUsage.NOT_CONFIGURED)
    opportunity_type: OpportunityType = Field(default=OpportunityType.NOT_RELEVANT)
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = Field(default="claude-haiku-4-5-20251001")


# ---------------------------------------------------------------------------
# Knowledge generation stage
# ---------------------------------------------------------------------------


class OperationDetail(BaseModel):
    """Structured detail for a single connector operation."""

    name: str
    description: str = ""
    use_case: str = Field(default="", description="How Ohanafy would use this")


class ConnectorKnowledge(BaseModel):
    """Generated knowledge artifact for a high-relevance connector."""

    connector_name: str
    summary: str = Field(..., description="1-paragraph overview")
    operations_detail: list[OperationDetail] = Field(default_factory=list)
    ohanafy_relevance: str = Field(default="", description="Specific connection to Ohanafy")
    recommended_workflows: list[str] = Field(default_factory=list)
    integration_notes: str = Field(default="", description="Technical implementation notes")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Pipeline run tracking
# ---------------------------------------------------------------------------


class DiscoveryRun(BaseModel):
    """Tracks a single pipeline execution."""

    run_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    connectors_discovered: int = 0
    connectors_scored: int = 0
    high_relevance_count: int = 0
    issues_created: int = 0
    knowledge_files_generated: int = 0
    errors: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Registry entry (what goes into tray-connectors.yaml)
# ---------------------------------------------------------------------------


class RegistryEntry(BaseModel):
    """Flattened entry for the tray-connectors.yaml catalog."""

    name: str
    display_name: str
    category: str
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    opportunity_type: str = "not_relevant"
    current_usage: str = "not_configured"
    last_assessed: str = ""
    tags: list[str] = Field(default_factory=list)
