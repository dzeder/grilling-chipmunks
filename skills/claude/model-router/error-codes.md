# Model Router Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `MR-001` | Unknown task type | Use a recognized task type. See SKILL.md for the list. |
| `MR-002` | Opus requested for non-evaluation task | Opus is reserved for evaluations only. |
| `MR-003` | Model override attempted in production | Overrides are disabled in prod. Remove override_model. |
| `MR-004` | Rate limit exceeded for model tier | Wait and retry, or use a lower tier. |
| `MR-005` | Agent not authorized for model tier | Check agent permissions for the requested model. |
| `MR-006` | Estimated tokens exceed model context | Reduce input size or use context trimming. |
| `MR-007` | Cost budget exceeded for agent | Agent has exceeded its daily cost budget. |
