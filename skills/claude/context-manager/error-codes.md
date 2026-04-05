# Context Manager Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `CTX-001` | Agent ID not found | Register the agent before tracking usage. |
| `CTX-002` | Budget exceeded | Trim context or reduce prompt size. |
| `CTX-003` | Invalid usage category | Use one of: system, user, assistant, tool. |
| `CTX-004` | Content is empty for estimate/record | Provide non-empty content. |
| `CTX-005` | Trim failed -- no trimmable messages | System prompts cannot be trimmed. |
| `CTX-006` | Model tier not recognized | Use haiku, sonnet, or opus. |
| `CTX-007` | Session expired | Start a new session for the agent. |
