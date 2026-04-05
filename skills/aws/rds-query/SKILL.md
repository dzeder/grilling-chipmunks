# RDS Query Skill

## Purpose

Query Amazon RDS databases safely. All queries must target read replicas -- never the production primary instance. This skill enforces query safety, timeout limits, and result size caps.

## Constraints

- **Read replica only** -- queries never execute against the primary/writer instance.
- **Never prod direct** -- production queries go exclusively through read replicas.
- **Query timeout**: Default 30s, max 120s. Long-running queries are killed automatically.
- **Result limit**: Default 1000 rows, max 10000. Use pagination for larger datasets.
- **No DDL**: `CREATE`, `ALTER`, `DROP`, `TRUNCATE` statements are blocked.
- **No DML**: `INSERT`, `UPDATE`, `DELETE` statements are blocked.
- **Connection pooling**: All connections managed via a shared pool. Max 10 concurrent connections.
- **Credentials**: Retrieved from Secrets Manager, never passed in plaintext.

## Supported Operations

- `execute_query` -- Run a SELECT query against a read replica.
- `describe_table` -- Get table schema and metadata.
- `list_tables` -- List tables in a database.
- `explain_query` -- Run EXPLAIN on a query for performance analysis.

## Inputs

- `database`: Database name.
- `query`: SQL query string (SELECT only).
- `environment`: Target environment.
- `timeout_seconds`: Query timeout (default: 30).
- `max_rows`: Maximum rows to return (default: 1000).

## Outputs

- `rows`: Query result rows.
- `columns`: Column names and types.
- `row_count`: Number of rows returned.
- `execution_time_ms`: Query execution time.

## Error Handling

Blocked queries return an error before execution. Timeouts kill the query server-side. See `error-codes.md` for all error codes.

## Dependencies

- `secrets-manager` skill for database credentials.
