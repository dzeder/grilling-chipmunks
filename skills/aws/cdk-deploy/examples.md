# CDK Deploy Examples

## Deploy a stack to dev

```python
from skills.aws.cdk_deploy.skill import run
from skills.aws.cdk_deploy.schema import CdkDeployInput

result = await run(CdkDeployInput(
    stack_name="ohanafy-dev-api-stack",
    environment="dev",
))
# result.deployment_status -> "UPDATE_COMPLETE"
```

## Deploy with context overrides

```python
result = await run(CdkDeployInput(
    stack_name="ohanafy-staging-worker-stack",
    environment="staging",
    context_overrides={"instance_count": "3", "enable_autoscaling": "true"},
))
```

## Run synth and Checkov only (no deploy)

```python
from skills.aws.cdk_deploy.skill import synth, checkov_scan

template_dir = await synth(CdkDeployInput(
    stack_name="ohanafy-prod-api-stack",
    environment="prod",
))
report = await checkov_scan(template_dir)
```
