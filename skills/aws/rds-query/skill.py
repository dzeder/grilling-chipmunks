"""RDS Query Skill -- Query RDS read replicas safely."""

from __future__ import annotations

import re
from typing import Any

from schema import RdsQueryInput, RdsQueryOutput


BLOCKED_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


async def run(input_data: RdsQueryInput) -> RdsQueryOutput:
    """Execute a read-only query against an RDS read replica."""
    # TODO: Implement query execution
    raise NotImplementedError("rds-query skill not yet implemented")


async def validate(input_data: RdsQueryInput) -> list[str]:
    """Pre-flight validation. Block DDL/DML and enforce limits."""
    errors: list[str] = []
    if BLOCKED_PATTERNS.search(input_data.query):
        errors.append("Query contains blocked DDL/DML statements. Only SELECT is allowed.")
    if input_data.max_rows > 10000:
        errors.append("max_rows exceeds 10000 limit.")
    if input_data.timeout_seconds > 120:
        errors.append("timeout_seconds exceeds 120s limit.")
    return errors
