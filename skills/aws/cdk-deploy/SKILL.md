# CDK Deploy Skill

## Purpose

Synthesize and deploy AWS CDK stacks with mandatory Checkov security scanning. Every infrastructure change at Ohanafy goes through CDK. No manual CloudFormation or console changes.

## Constraints

- **CDK v2** only. CDK v1 constructs are not supported.
- **Checkov must pass** -- all synthesized templates are scanned before deployment. Failed scans block deployment.
- **Stack naming**: `ohanafy-{env}-{service}-stack` (e.g., `ohanafy-prod-api-stack`).
- **Context values**: Environment-specific context is loaded from `cdk.json` -- never hardcoded.
- **Approval gates**: Production deployments require explicit approval via `--require-approval broadening`.
- **Diff before deploy**: `cdk diff` output is captured and logged before every deployment.
- **Tags**: All stacks auto-tagged with `ohanafy:environment`, `ohanafy:team`, `ohanafy:managed-by=cdk`.

## Workflow

1. Run `cdk synth` to generate CloudFormation templates.
2. Run Checkov scan on generated `cdk.out/` templates.
3. Run `cdk diff` and log changes.
4. Deploy via `cdk deploy` with appropriate approval settings.
5. Verify stack status is `CREATE_COMPLETE` or `UPDATE_COMPLETE`.

## Inputs

- `stack_name`: Name of the CDK stack.
- `environment`: Target environment (`dev`, `staging`, `prod`).
- `context_overrides`: Optional CDK context key-value pairs.
- `skip_diff`: Skip the diff step (default: `false`).

## Outputs

- `stack_arn`: ARN of the deployed stack.
- `deployment_status`: Stack status after deployment.
- `checkov_report`: Summary of Checkov scan results.
- `diff_output`: Output of `cdk diff` (if not skipped).

## Error Handling

Checkov failures return detailed findings with remediation guidance. CloudFormation failures trigger rollback. See `error-codes.md` for the full catalog.

## Dependencies

- Checkov CLI must be installed in the execution environment.
- AWS CDK CLI v2.x must be available.
