# Lambda Deploy Examples

## Deploy a Python Lambda to dev

```python
from skills.aws.lambda_deploy.skill import run
from skills.aws.lambda_deploy.schema import LambdaDeployInput

result = await run(LambdaDeployInput(
    function_name="ohanafy-dev-orders-process",
    runtime="python3.12",
    handler="app.handler",
    memory_mb=512,
    timeout_seconds=60,
    environment="dev",
    env_vars={"LOG_LEVEL": "DEBUG"},
))
```

## Deploy a Node.js Lambda with layers

```python
result = await run(LambdaDeployInput(
    function_name="ohanafy-staging-notifications-send",
    runtime="nodejs20.x",
    handler="index.handler",
    memory_mb=256,
    timeout_seconds=30,
    environment="staging",
    layers=["arn:aws:lambda:us-east-1:123456789:layer:shared-utils:3"],
))
```

## Validate before deploying

```python
from skills.aws.lambda_deploy.skill import validate

errors = await validate(LambdaDeployInput(
    function_name="test",
    runtime="python3.12",
    environment="dev",
    memory_mb=4096,  # will fail validation
))
# errors -> ["Memory exceeds 3008 MB maximum."]
```
