# S3 Manager Examples

## Create a bucket

```python
from skills.aws.s3_manager.skill import run
from skills.aws.s3_manager.schema import S3ManagerInput

result = await run(S3ManagerInput(
    bucket_purpose="uploads",
    environment="dev",
    operation="create_bucket",
))
# result.bucket_name -> "ohanafy-dev-uploads"
```

## Upload an object

```python
result = await run(S3ManagerInput(
    bucket_purpose="exports",
    environment="staging",
    operation="upload_object",
    key="reports/2026-04-01.csv",
    body=b"col1,col2\nval1,val2",
))
```

## List objects with prefix

```python
result = await run(S3ManagerInput(
    bucket_purpose="exports",
    environment="prod",
    operation="list_objects",
    prefix="reports/2026-04/",
))
```
