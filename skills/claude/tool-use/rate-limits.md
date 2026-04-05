# Tool Use Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Tool registrations | 100 per hour | Per process |
| Input validations | 10,000 per minute | Per process |
| Output validations | 10,000 per minute | Per process |
| Schema lookups | 10,000 per minute | Per process |

## Notes

- Tool registration is an in-memory operation and is fast.
- Validation uses Pydantic which is highly optimized.
- Rate limits primarily guard against infinite tool-call loops.
