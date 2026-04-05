# Tool Use Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `TU-001` | Tool not registered | Register the tool before using it. |
| `TU-002` | Input validation failed | Fix input data to match the tool's schema. |
| `TU-003` | Output validation failed | Fix tool implementation to return valid output. |
| `TU-004` | Schema definition not found | Verify the Pydantic model class path. |
| `TU-005` | Tool name collision | Use a unique tool name. |
| `TU-006` | Invalid schema format | Ensure the schema is a valid Pydantic BaseModel. |
| `TU-007` | Tool execution error | Check the underlying tool implementation for errors. |
| `TU-008` | Tool result too large | Truncate results to stay within token budget. |
