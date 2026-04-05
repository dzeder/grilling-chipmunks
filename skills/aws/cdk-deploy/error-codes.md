# CDK Deploy Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `CDK-001` | `cdk synth` failed | Check CDK app for syntax or construct errors. |
| `CDK-002` | Checkov scan found critical findings | Fix all CRITICAL and HIGH severity findings before deploying. |
| `CDK-003` | `cdk diff` failed | Stack may not exist yet or credentials may be invalid. |
| `CDK-004` | CloudFormation deployment failed | Check stack events for root cause. Rollback is automatic. |
| `CDK-005` | Stack naming convention violation | Use pattern `ohanafy-{env}-{service}-stack`. |
| `CDK-006` | Production deployment without approval | Set `--require-approval broadening` for prod. |
| `CDK-007` | CDK version mismatch | Ensure CDK CLI v2.x is installed. |
| `CDK-008` | Missing required tags | Stack must include `ohanafy:environment`, `ohanafy:team`, `ohanafy:managed-by`. |
| `CDK-009` | Context value not found | Check `cdk.json` for required context keys. |
| `CDK-010` | Stack in ROLLBACK_COMPLETE state | Delete the failed stack before redeploying. |
