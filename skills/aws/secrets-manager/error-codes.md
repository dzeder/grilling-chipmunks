# Secrets Manager Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `SEC-001` | Secret naming convention violation | Use pattern `ohanafy/{env}/{service}/{secret-name}`. |
| `SEC-002` | Secret already exists | Use `update_secret` instead of `create_secret`. |
| `SEC-003` | Secret not found | Verify the secret path exists in the target environment. |
| `SEC-004` | Secret value is empty | Provide a non-empty secret_value for create/update. |
| `SEC-005` | KMS key not found | Ensure the Ohanafy KMS key exists in the target region. |
| `SEC-006` | Rotation configuration failed | Check the rotation Lambda function and permissions. |
| `SEC-007` | Access denied | Check IAM permissions in `iam-permissions.md`. |
| `SEC-008` | Secret pending deletion | Restore the secret or wait for deletion to complete. |
| `SEC-009` | Secret value too large | Secrets Manager limit is 64 KB per secret value. |
| `SEC-010` | Rotation Lambda not found | Deploy the rotation Lambda via the `lambda-deploy` skill. |
