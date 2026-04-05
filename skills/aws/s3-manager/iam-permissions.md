# S3 Manager IAM Permissions

## Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:PutBucketPolicy",
        "s3:PutBucketEncryption",
        "s3:PutBucketVersioning",
        "s3:PutBucketTagging",
        "s3:PutBucketLogging",
        "s3:PutBucketLifecycleConfiguration",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPolicy",
        "s3:GetBucketEncryption",
        "s3:GetBucketVersioning",
        "s3:GetBucketTagging",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::ohanafy-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::ohanafy-*/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "arn:aws:kms:*:*:key/ohanafy-*"
    }
  ]
}
```

## Least Privilege Notes

- All S3 resources scoped to `ohanafy-*` prefix.
- KMS actions limited to Ohanafy-managed keys.
- No `s3:PutBucketAcl` granted -- ACLs are disabled in favor of bucket policies.
