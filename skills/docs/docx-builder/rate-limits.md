# DOCX Builder Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Document generation | 50 per hour | Per user |
| Template listing | 100 per hour | Per user |
| Validation | 200 per hour | Per user |

## Notes

- DOCX generation is CPU-bound (python-docx runs locally).
- Large documents with many images may take several seconds.
- Rate limits prevent abuse in automated pipelines.
