# Diff Summarizer Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Diff summarization | 50 per hour | Per user |
| Commit range summarization | 30 per hour | Per user |
| Release notes generation | 10 per hour | Per user |
| Breaking change detection | 50 per hour | Per user |

## Notes

- Summarization uses Claude Sonnet via the model-router skill, so API rate limits apply.
- Large diffs (>10,000 lines) consume more tokens and may take longer.
- Caching is applied per commit range -- repeated requests return cached results.

## Cost

- Average cost per summarization: ~$0.01 (Sonnet, ~2000 tokens).
- Release notes generation: ~$0.05 (longer output).
