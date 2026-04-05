# S3 Manager Skill

## Purpose

Manage S3 buckets and objects following Ohanafy naming conventions and security policies. All buckets must follow the `ohanafy-{env}-{purpose}` naming pattern. Public buckets are strictly prohibited.

## Constraints

- **Naming**: All buckets must follow `ohanafy-{env}-{purpose}` (e.g., `ohanafy-prod-uploads`).
- **No public access**: `BlockPublicAccess` is enforced on every bucket. No exceptions.
- **Encryption**: Server-side encryption with AWS KMS (SSE-KMS) is mandatory.
- **Versioning**: Enabled by default on all buckets.
- **Lifecycle rules**: Objects older than 90 days in dev/staging auto-transition to Glacier.
- **Logging**: Access logging enabled, sent to `ohanafy-{env}-access-logs` bucket.
- **Tags**: All buckets must include `ohanafy:environment`, `ohanafy:team`, and `ohanafy:purpose` tags.

## Supported Operations

- `create_bucket` -- Create a new S3 bucket with all Ohanafy defaults.
- `delete_bucket` -- Delete an empty bucket (prod requires approval).
- `upload_object` -- Upload an object with server-side encryption.
- `download_object` -- Download an object by key.
- `list_objects` -- List objects with optional prefix filter.
- `set_lifecycle` -- Configure lifecycle rules.

## Inputs

- `bucket_purpose`: Purpose identifier for naming (e.g., `uploads`, `exports`).
- `environment`: Target environment (`dev`, `staging`, `prod`).
- `operation`: The S3 operation to perform.
- `key`: Object key (for object operations).
- `body`: Object content (for uploads).

## Outputs

- `bucket_name`: Full bucket name generated from convention.
- `operation_result`: Success or failure details.
- `object_url`: S3 URI for uploaded objects.

## Error Handling

Bucket creation failures roll back any partially created resources. Access denied errors surface the specific IAM permission that is missing. See `error-codes.md` for details.

## Dependencies

- `iam-audit` skill for verifying bucket policies.
- `secrets-manager` skill for KMS key references.
