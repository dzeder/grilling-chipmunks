# IAM Audit Examples

## Run a full account audit

```python
from skills.aws.iam_audit.skill import run
from skills.aws.iam_audit.schema import IamAuditInput

result = await run(IamAuditInput(
    audit_type="full_audit",
))
print(f"Compliant: {result.compliant}")
print(f"Critical findings: {result.summary.critical}")
```

## Audit a specific role

```python
result = await run(IamAuditInput(
    audit_type="role_audit",
    resource_name="ohanafy-prod-api-execution-role",
))
for finding in result.findings:
    print(f"[{finding.severity}] {finding.finding}")
```

## Audit with severity threshold

```python
result = await run(IamAuditInput(
    audit_type="full_audit",
    severity_threshold="HIGH",
))
# Only CRITICAL and HIGH findings returned
```

## Cross-account trust audit

```python
result = await run(IamAuditInput(
    audit_type="cross_account_audit",
))
```
