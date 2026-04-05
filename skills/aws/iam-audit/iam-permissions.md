# IAM Audit IAM Permissions

## Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListRoles",
        "iam:ListUsers",
        "iam:ListPolicies",
        "iam:ListAttachedRolePolicies",
        "iam:ListAttachedUserPolicies",
        "iam:ListRolePolicies",
        "iam:ListUserPolicies",
        "iam:GetRole",
        "iam:GetUser",
        "iam:GetPolicy",
        "iam:GetPolicyVersion",
        "iam:GetRolePolicy",
        "iam:GetUserPolicy",
        "iam:ListAccessKeys",
        "iam:GetAccessKeyLastUsed",
        "iam:GenerateCredentialReport",
        "iam:GetCredentialReport"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "access-analyzer:ListFindings",
        "access-analyzer:GetFinding"
      ],
      "Resource": "*"
    }
  ]
}
```

## Least Privilege Notes

- All actions are **read-only**. No IAM modification permissions.
- `Resource: "*"` is required because IAM is a global service and list operations cannot be scoped.
- Access Analyzer integration provides additional cross-account findings.
