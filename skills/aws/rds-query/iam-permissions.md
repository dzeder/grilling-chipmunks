# RDS Query IAM Permissions

## Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances",
        "rds:DescribeDBClusters",
        "rds-db:connect"
      ],
      "Resource": [
        "arn:aws:rds:*:*:db:ohanafy-*",
        "arn:aws:rds:*:*:cluster:ohanafy-*",
        "arn:aws:rds-db:*:*:dbuser:*/ohanafy_readonly"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:ohanafy/rds/*"
    }
  ]
}
```

## Least Privilege Notes

- RDS actions scoped to `ohanafy-*` instances and clusters.
- Database user is `ohanafy_readonly` with SELECT-only grants.
- Secrets Manager access limited to `ohanafy/rds/*` secret paths.
- No `rds:ModifyDBInstance` or write actions granted.
