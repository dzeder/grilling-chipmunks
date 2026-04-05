# Markdown Generator Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Document generation | 100 per hour | Per user |
| Document validation | 500 per hour | Per user |
| Navigation generation | 100 per hour | Per user |

## Notes

- Markdown generation is a local operation with no external API calls.
- Rate limits exist to prevent runaway automation loops.
- Bulk generation (more than 20 docs at once) should use batch mode.
