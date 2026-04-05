# RDS Query Examples

## Execute a simple query

```python
from skills.aws.rds_query.skill import run
from skills.aws.rds_query.schema import RdsQueryInput

result = await run(RdsQueryInput(
    database="ohanafy_orders",
    query="SELECT id, status, created_at FROM orders WHERE status = 'pending' LIMIT 100",
    environment="prod",
))
print(f"Found {result.row_count} rows in {result.execution_time_ms}ms")
```

## Describe a table

```python
result = await run(RdsQueryInput(
    database="ohanafy_orders",
    operation="describe_table",
    table_name="orders",
    environment="staging",
))
for col in result.columns:
    print(f"{col.name}: {col.data_type}")
```

## Explain a query

```python
result = await run(RdsQueryInput(
    database="ohanafy_orders",
    query="SELECT * FROM orders WHERE customer_id = 12345",
    operation="explain_query",
    environment="dev",
))
```

## Validate before executing

```python
from skills.aws.rds_query.skill import validate

errors = await validate(RdsQueryInput(
    database="ohanafy_orders",
    query="DELETE FROM orders WHERE id = 1",  # will fail
    environment="dev",
))
# errors -> ["Query contains blocked DDL/DML statements. Only SELECT is allowed."]
```
