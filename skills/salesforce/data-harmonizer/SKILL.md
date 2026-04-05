# data-harmonizer

Maps customer Excel/CSV files to Ohanafy's Salesforce schema using Claude Sonnet, validates data quality, and stages cleaned records for human review before import.

## When to Use

- Customer sends an Excel file that needs to be imported into Salesforce
- Onboarding a new customer whose data is in a different format
- Periodic data imports from distributors or retailers
- Checking data quality on a file before manual import

## Interface

```python
from skills.salesforce.data_harmonizer.skill import run
from skills.salesforce.data_harmonizer.schema import InputSchema

result = run(InputSchema(
    file_path="/path/to/customer-data.xlsx",
    customer_id="acme-corp",
    target_object="Account",  # optional, auto-detects if omitted
))
```

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | str | yes | Path to the Excel (.xlsx) or CSV file |
| customer_id | str | yes | Customer identifier for mapping retrieval |
| target_object | str | no | Target SF object (auto-detect if omitted) |
| sheet_name | str | no | Sheet name for multi-sheet workbooks (default: first) |
| header_row | int | no | Row number with headers, 1-indexed (default: 1) |
| dry_run | bool | no | Map and validate only, do not stage (default: false) |

## Returns

```python
{
    "status": "success" | "needs_review" | "error",
    "batch_id": "batch-abc123",
    "mapping": {
        "mappings": [...],         # column-to-field mappings with confidence
        "unmapped_columns": [...], # columns Claude couldn't map
    },
    "staged_records": [...],       # records ready for SF import
    "validation_issues": [...],    # errors and warnings
    "stats": {
        "total_rows": 100,
        "mapped_rows": 95,
        "error_rows": 3,
        "warning_rows": 5,
    },
    "error": { "code": "...", "message": "..." }  # only on error
}
```

## Confidence Levels

- **high**: Exact/near-exact match or prior approved mapping. Auto-applied.
- **medium**: Plausible synonym, sample data consistent. Flagged for review.
- **low**: Ambiguous. Marked UNMAPPED for human decision.

## Error Handling

See `error-codes.md` for full error reference.
Common errors: EMPTY_FILE (no headers), MAPPING_PARSE_ERROR (Claude response malformed), CLAUDE_API_ERROR (API failure).

## Rate Limits

See `rate-limits.md` for API limits and retry policy.

## Examples

See `examples.md` for real usage examples against Ohanafy data.

## Dependencies

- `anthropic` — Claude API client
- `boto3` — DynamoDB access for mappings and logging
- `openpyxl` — Excel file reading (for .xlsx)
- `pyyaml` — Prompt template loading
