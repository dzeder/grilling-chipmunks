# RDS Query Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `RDS-001` | Blocked DDL/DML statement | Only SELECT queries are allowed. Remove INSERT/UPDATE/DELETE/DDL. |
| `RDS-002` | Query timeout exceeded | Optimize query or increase timeout (max 120s). |
| `RDS-003` | Result set exceeds max rows | Add LIMIT clause or reduce max_rows parameter. |
| `RDS-004` | Connection to read replica failed | Check VPC connectivity and security groups. |
| `RDS-005` | Database not found | Verify the database name exists on the read replica. |
| `RDS-006` | Credentials not found in Secrets Manager | Ensure database credentials exist in Secrets Manager. |
| `RDS-007` | Connection pool exhausted | Wait and retry. Max 10 concurrent connections. |
| `RDS-008` | Primary instance connection attempted | The skill detected a writer endpoint. Only reader endpoints are allowed. |
| `RDS-009` | SQL syntax error | Fix the SQL query syntax. |
| `RDS-010` | Permission denied on table | The database user lacks SELECT permission on the target table. |
