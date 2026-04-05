"""IAM Audit Skill -- Audit IAM policies for overly permissive access."""

from __future__ import annotations

from typing import Any

from schema import IamAuditInput, IamAuditOutput, AuditFinding


async def run(input_data: IamAuditInput) -> IamAuditOutput:
    """Run an IAM audit based on the specified audit type."""
    # TODO: Implement IAM audit logic
    raise NotImplementedError("iam-audit skill not yet implemented")


def check_wildcard_actions(policy_document: dict[str, Any]) -> list[AuditFinding]:
    """Check a policy document for wildcard actions."""
    findings: list[AuditFinding] = []
    # TODO: Implement wildcard detection
    return findings


def check_wildcard_resources(policy_document: dict[str, Any]) -> list[AuditFinding]:
    """Check a policy document for wildcard resources."""
    findings: list[AuditFinding] = []
    # TODO: Implement wildcard resource detection
    return findings


async def validate(input_data: IamAuditInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    return errors
