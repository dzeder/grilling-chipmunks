# S3 Manager Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `S3M-001` | Bucket name violates naming convention | Use pattern `ohanafy-{env}-{purpose}`. |
| `S3M-002` | Bucket already exists | Use a different purpose identifier or check existing buckets. |
| `S3M-003` | Public access configuration detected | Remove any public access settings. Public buckets are prohibited. |
| `S3M-004` | Encryption not enabled | Ensure SSE-KMS encryption is configured. This should be automatic. |
| `S3M-005` | Bucket not empty on delete | Remove all objects before deleting a bucket. |
| `S3M-006` | Access denied | Check IAM permissions in `iam-permissions.md`. |
| `S3M-007` | Object key exceeds 1024 bytes | Shorten the object key. |
| `S3M-008` | Missing required tags | All buckets require `ohanafy:environment`, `ohanafy:team`, `ohanafy:purpose` tags. |
| `S3M-009` | Production deletion without approval | Prod bucket deletions require manual approval. |
| `S3M-010` | Invalid lifecycle configuration | Check lifecycle rule syntax against AWS documentation. |
