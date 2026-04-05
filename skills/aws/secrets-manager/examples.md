# Secrets Manager Examples

## Create a secret

```python
from skills.aws.secrets_manager.skill import run
from skills.aws.secrets_manager.schema import SecretsManagerInput

result = await run(SecretsManagerInput(
    service="api",
    secret_name="database-url",
    environment="dev",
    operation="create_secret",
    secret_value="postgresql://user:pass@host:5432/db",
))
# Secret stored at: ohanafy/dev/api/database-url
```

## Retrieve a secret

```python
result = await run(SecretsManagerInput(
    service="api",
    secret_name="database-url",
    environment="prod",
    operation="get_secret",
))
```

## Rotate a secret immediately

```python
result = await run(SecretsManagerInput(
    service="api",
    secret_name="database-url",
    environment="prod",
    operation="rotate_secret",
))
```

## List secrets for a service

```python
result = await run(SecretsManagerInput(
    service="api",
    secret_name="*",
    environment="prod",
    operation="list_secrets",
))
# result.secret_names -> ["database-url", "stripe-key", "sendgrid-key"]
```
