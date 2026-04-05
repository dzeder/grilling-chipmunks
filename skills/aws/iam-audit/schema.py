"""Pydantic models for the IAM Audit skill."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AuditType(str, Enum):
    full_audit = "full_audit"
    role_audit = "role_audit"
    policy_audit = "policy_audit"
    user_audit = "user_audit"
    cross_account_audit = "cross_account_audit"


class Severity(str, Enum):
    critical = "CRITICAL"
    high = "HIGH"
    medium = "MEDIUM"
    low = "LOW"


class IamAuditInput(BaseModel):
    audit_type: AuditType = Field(..., description="Type of audit to perform.")
    resource_name: Optional[str] = Field(default=None, description="Specific resource to audit.")
    severity_threshold: Severity = Field(default=Severity.low, description="Minimum severity to report.")


class AuditFinding(BaseModel):
    severity: Severity
    resource_type: str
    resource_name: str
    finding: str
    recommendation: str


class AuditSummary(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class IamAuditOutput(BaseModel):
    findings: list[AuditFinding] = Field(default_factory=list)
    summary: AuditSummary = Field(default_factory=AuditSummary)
    compliant: bool = True
