# Lambda Deploy IAM Permissions

## Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:PublishVersion",
        "lambda:GetFunction",
        "lambda:ListVersionsByFunction",
        "lambda:AddPermission",
        "lambda:GetLayerVersion"
      ],
      "Resource": "arn:aws:lambda:*:*:function:ohanafy-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents"
      ],
      "Resource": "arn:aws:cloudformation:*:*:stack/ohanafy-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::*:role/ohanafy-lambda-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:DescribeLogGroups"
      ],
      "Resource": "*"
    }
  ]
}
```

## Least Privilege Notes

- All Lambda resources are scoped to `ohanafy-*` prefix.
- `iam:PassRole` is restricted to Ohanafy Lambda execution roles only.
- `logs:*` is limited to create and describe operations.
