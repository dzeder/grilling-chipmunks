# HTML Publisher Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Page generation | 100 per hour | Per user |
| Site builds | 10 per hour | Per project |
| Publishes | 5 per hour | Per project |
| Validations | 200 per hour | Per user |

## Notes

- Docusaurus builds are CPU-intensive. Limit concurrent builds to 1.
- CloudFront invalidation propagation takes up to 15 minutes.
- Publish operations are throttled to prevent rapid-fire production changes.

## Deployment Pipeline

1. Generate/update pages.
2. Run validation.
3. Build locally.
4. Publish to staging S3 bucket.
5. Manual review.
6. Publish to production S3 bucket.
