# Context Manager Rate Limits

| Operation | Limit | Scope |
|-----------|-------|-------|
| Budget checks | 10,000 per minute | Per agent |
| Usage recording | 10,000 per minute | Per agent |
| Usage reports | 100 per minute | Per agent |
| Context trimming | 10 per minute | Per agent |
| Token estimation | 10,000 per minute | Per process |

## Notes

- Context manager operations are in-memory and very fast.
- Rate limits exist primarily to detect runaway loops.
- Usage data is persisted to DynamoDB every 60 seconds for durability.
