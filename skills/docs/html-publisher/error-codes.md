# HTML Publisher Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `HP-001` | Page title is empty | Provide a non-empty page title. |
| `HP-002` | Slug is empty or invalid | Provide a valid URL slug (lowercase, hyphens only). |
| `HP-003` | MDX syntax error | Fix MDX/JSX syntax in the content. |
| `HP-004` | Docusaurus build failed | Check build output for specific errors. |
| `HP-005` | Broken internal link detected | Fix or remove the broken link reference. |
| `HP-006` | S3 upload failed | Check IAM permissions and S3 bucket configuration. |
| `HP-007` | CloudFront invalidation failed | Check CloudFront distribution ID and permissions. |
| `HP-008` | Image not found in static/ | Ensure referenced images exist in the static directory. |
| `HP-009` | Version not found | Check that the specified version exists in versioned_docs/. |
| `HP-010` | Node.js or Docusaurus not installed | Install Node.js 20+ and run `npm install`. |
