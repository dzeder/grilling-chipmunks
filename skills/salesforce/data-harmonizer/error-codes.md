# Error Codes — data-harmonizer

| Code | Message | Cause | Resolution |
|------|---------|-------|------------|
| `EMPTY_FILE` | File contains no column headers | Uploaded file is empty or header row is wrong | Check the file has data and verify header_row parameter |
| `NO_DATA` | File contains headers but no data rows | File has headers only, no records | Upload a file with actual data rows |
| `UNSUPPORTED_FORMAT` | Unsupported file type | File is not .xlsx or .csv | Convert to .xlsx or .csv before uploading |
| `MAPPING_PARSE_ERROR` | Failed to parse Claude mapping response | Claude returned malformed JSON | Retry; if persistent, check prompt template |
| `CLAUDE_API_ERROR` | Claude API request failed | Network or API issue | Check API key and retry with backoff |
| `VALIDATION_ERROR` | Invalid input parameters | Missing or malformed input | Check input against InputSchema |
| `RATE_LIMIT_ERROR` | API rate limit exceeded | Too many requests to Claude or SF | Wait and retry with exponential backoff |
| `AUTH_ERROR` | Authentication failed | Invalid Claude API key or AWS credentials | Check .env credentials and IAM permissions |
| `TIMEOUT_ERROR` | Request timed out | Large file or slow API response | Retry; consider splitting large files |
| `DYNAMODB_ERROR` | DynamoDB operation failed | Table not found or permission denied | Verify CDK stack is deployed and IAM roles are set |
| `SF_QUERY_ERROR` | Salesforce query failed | SOQL error during dupe detection | Check SF connection and scratch org availability |
| `UNEXPECTED_ERROR` | Unexpected error occurred | Unhandled exception | Check logs for stack trace, report to team |
