# Secrets Manager Skill

## Purpose

Manage secrets in AWS Secrets Manager. All credentials, API keys, and sensitive configuration at Ohanafy must be stored here -- never in code, environment variables, config files, or version control.

## Constraints

- **All creds go here** -- no exceptions. Secrets must never appear in source code, CI logs, or environment variable definitions.
- **Naming**: `ohanafy/{env}/{service}/{secret-name}` (e.g., `ohanafy/prod/api/database-url`).
- **Encryption**: All secrets encrypted with Ohanafy-managed KMS keys.
- **Rotation**: Secrets must have rotation enabled. Default rotation period is 30 days.
- **Versioning**: AWS Secrets Manager automatically versions secrets. Use staging labels for blue/green.
- **Access logging**: All secret access is logged via CloudTrail.
- **No plaintext output**: The skill never returns secret values in logs or structured output. Values are returned only to the calling function in memory.

## Supported Operations

- `create_secret` -- Create a new secret with automatic rotation configured.
- `get_secret` -- Retrieve a secret value (returned in memory, never logged).
- `update_secret` -- Update a secret value (triggers new version).
- `delete_secret` -- Schedule secret deletion (30-day recovery window).
- `rotate_secret` -- Trigger immediate rotation.
- `list_secrets` -- List secret names (not values) by prefix.

## Inputs

- `service`: Service name for the secret path.
- `secret_name`: Secret identifier.
- `environment`: Target environment.
- `operation`: The operation to perform.
- `secret_value`: Value for create/update operations.

## Outputs

- `secret_arn`: ARN of the secret.
- `version_id`: Version identifier.
- `operation_result`: Success or failure status.

## Dependencies

- KMS keys managed by the `cdk-deploy` skill.
