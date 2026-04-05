# Lambda Deploy Skill

## Purpose

Deploy AWS Lambda functions using CDK infrastructure-as-code. This skill enforces Ohanafy standards: all Lambdas must use AWS Lambda Powertools for observability, structured logging, and tracing. Direct CloudFormation or SAM deployments are not supported.

## Constraints

- **CDK only** -- no raw CloudFormation, SAM, or Serverless Framework.
- **Lambda Powertools required** -- every function must include `aws-lambda-powertools` for structured logging, tracing, and metrics.
- **Runtime**: Python 3.12+ or Node.js 20+.
- **Memory**: Default 256 MB, max 3008 MB. Must be justified above 1024 MB.
- **Timeout**: Default 30s, max 900s. Functions exceeding 60s require async invocation patterns.
- **Environment variables**: Never hardcode secrets. Use Secrets Manager references via the `secrets-manager` skill.
- **Naming**: `ohanafy-{env}-{service}-{function}` (e.g., `ohanafy-prod-orders-process`).
- **Layers**: Shared dependencies must use Lambda Layers managed through CDK.

## Workflow

1. Validate function configuration against Ohanafy standards.
2. Check that Lambda Powertools is included in dependencies.
3. Run `cdk synth` to generate CloudFormation template.
4. Run Checkov security scan on synthesized template.
5. Deploy via `cdk deploy` with approval gates for production.
6. Verify deployment health via CloudWatch metrics.

## Inputs

- `function_name`: Name of the Lambda function.
- `runtime`: Python or Node.js runtime version.
- `handler`: Entry point (e.g., `app.handler`).
- `memory_mb`: Memory allocation in MB.
- `timeout_seconds`: Function timeout.
- `environment`: Target environment (`dev`, `staging`, `prod`).
- `env_vars`: Dictionary of non-secret environment variables.
- `layers`: Optional list of Lambda Layer ARNs.

## Outputs

- `function_arn`: ARN of the deployed Lambda.
- `version`: Published version number.
- `deployment_status`: Success or failure with details.
- `cloudwatch_log_group`: Log group for the function.

## Error Handling

All errors are logged via Lambda Powertools structured logging. Failed deployments trigger automatic rollback to the previous version. See `error-codes.md` for the full error catalog.

## Dependencies

- `cdk-deploy` skill for infrastructure deployment.
- `secrets-manager` skill for credential injection.
- `iam-audit` skill for post-deploy permission validation.
