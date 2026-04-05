# Prompt Loader Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Prompt loads | 1,000 per minute | Per agent |
| Prompt renders | 1,000 per minute | Per agent |
| Prompt file reads | Cached after first read | Per process |

## Caching

- Prompt files are cached in memory after first load.
- Cache is invalidated when prompt file modification time changes.
- Version resolution for `latest` is re-evaluated on each call.

## Token Budget Integration

- Rendered prompts report token estimates to the `context-manager` skill.
- Prompts exceeding the agent's token budget are rejected before API call.
