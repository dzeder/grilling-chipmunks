# IAM Audit Skill

## Purpose

Audit IAM policies, roles, and users for overly permissive access patterns. This skill identifies wildcard actions, missing resource constraints, and policies that violate Ohanafy's least-privilege requirements.

## Constraints

- **Read-only** -- this skill never modifies IAM resources. It only reads and reports.
- **Wildcard detection**: Flag any policy with `Action: "*"` or `Resource: "*"`.
- **Admin detection**: Identify roles with `AdministratorAccess` or equivalent.
- **Unused credentials**: Flag access keys older than 90 days or unused roles.
- **Cross-account trust**: Flag any trust policy that allows external account access.
- **Severity levels**: CRITICAL, HIGH, MEDIUM, LOW based on blast radius.

## Supported Audits

- `full_audit` -- Scan all IAM resources in the account.
- `role_audit` -- Audit a specific role.
- `policy_audit` -- Audit a specific managed or inline policy.
- `user_audit` -- Audit a specific IAM user.
- `cross_account_audit` -- Check all trust policies for external access.

## Inputs

- `audit_type`: Type of audit to perform.
- `resource_name`: Optional specific resource to audit (role name, policy ARN, user name).
- `severity_threshold`: Minimum severity to report (default: `LOW`).

## Outputs

- `findings`: List of audit findings with severity, resource, and recommendation.
- `summary`: Counts by severity level.
- `compliant`: Boolean indicating whether all checks passed.

## Error Handling

Access denied errors indicate the audit role lacks sufficient read permissions. See `iam-permissions.md` for required permissions. See `error-codes.md` for all error codes.

## Dependencies

- Requires read-only IAM access in the target AWS account.
