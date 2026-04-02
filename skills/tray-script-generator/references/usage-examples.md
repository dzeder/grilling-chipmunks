# Usage Examples Reference

**Source**: Extracted from SKILL.md v2.0.0
**Full examples with implementations**: See `../examples.json` (10 examples)

## Example 1: Salesforce Composite Response Processing (Advanced)

**Source**: `Shopify_2GP/versions/current/scripts/scripts/Shopify_02_Products/2-execute_script/script.js`

**Input**:
```json
{
  "compositeResponse": [
    {
      "body": {"id": "a0X5e000001234ABC", "success": true, "created": true},
      "httpStatusCode": 201,
      "referenceId": "Item1"
    },
    {
      "body": [{"errorCode": "REQUIRED_FIELD_MISSING", "message": "Required fields are missing: [Name]"}],
      "httpStatusCode": 400,
      "referenceId": "Item2"
    }
  ]
}
```

**Output**:
```json
{
  "successful_operations": [
    {
      "salesforce_id": "a0X5e000001234ABC",
      "reference_id": "Item1",
      "operation_type": "created",
      "http_status": 201,
      "success": true
    }
  ],
  "errors": [
    {
      "error": {
        "response": {
          "body": {
            "Type": "ValidationFailed",
            "Message": "Required fields are missing: [Name]",
            "ErrorCode": "REQUIRED_FIELD_MISSING"
          }
        },
        "statusCode": 400,
        "retryable": false,
        "retryStrategy": {
          "maxRetries": 0,
          "recommendation": "Not retryable, fix error and resubmit"
        }
      },
      "id": "Salesforce Operation Reference # Item2",
      "service": "Salesforce Composite API Processing"
    }
  ],
  "summary": {
    "total_operations": 2,
    "successful_operations": 1,
    "failed_operations": 1,
    "success_rate": 50
  }
}
```

**Patterns Used**: `salesforce_composite_response_handler`, `error_types_enumeration`, `http_status_to_error_type_mapping`, `retry_strategy_pattern`

---

## Example 2: Lookup Map Transformation (Intermediate)

**Source**: `GP_Analytics_2GP/GPA_10_CORE/5-new_create_csv_rows/script.js`

**Input**:
```json
{
  "gpa_data": [
    {
      "id": "forecast_001",
      "product_gpa_id": "1019#HRB",
      "buyer_id": "BUYER123",
      "week": 4,
      "year": 2025,
      "sales_rate_per_week": 100
    }
  ],
  "ohfy_products": [{"Original_ID__c": "1019#HRB", "Product__c": "a0Y5e000001PROD1"}],
  "ohfy_accounts": [{"Original_ID__c": "BUYER123", "Account__c": "0015e000001ACCT1"}],
  "namespace_prefix": "ohfy__"
}
```

**Output**:
```json
{
  "rows": [
    {
      "External_ID__c": "forecast_001",
      "Item__c": "a0Y5e000001PROD1",
      "Account__c": "0015e000001ACCT1",
      "Week__c": 4,
      "Year__c": 2025,
      "Sales_Rate_Per_Week__c": 100
    }
  ],
  "errors": [],
  "summary": [
    {"metric": "Total Rows Processed", "count": 1},
    {"metric": "Successful Rows", "count": 1}
  ]
}
```

**Patterns Used**: `lookup_map_builder`, `filter_reduce_chain`, `error_deduplication`, `unique_set_deduplication`

---

## Example 3: Simple Statistics Aggregation (Beginner)

**Source**: `CSV_Upload_v1/04_Process_Results/1-process_results/script.js`

**Input**:
```json
{
  "orderResults": [
    {"created": 5, "updated": 3, "dataErrors": 1, "apiErrors": 0},
    {"created": 10, "updated": 7, "dataErrors": 2, "apiErrors": 1}
  ],
  "orderItemResults": [
    {"created": 20, "updated": 15, "dataErrors": 3, "apiErrors": 1}
  ]
}
```

**Output**:
```json
{
  "orderStats": {"created": 15, "updated": 10, "dataErrors": 3, "apiErrors": 1},
  "orderItemStats": {"created": 20, "updated": 15, "dataErrors": 3, "apiErrors": 1},
  "hasApiErrors": true
}
```

**Patterns Used**: `aggregation_reducer`, `percentage_calculator`, `array_spread_merge`

---

## All 10 Examples in examples.json

| # | Title | Complexity |
|---|-------|------------|
| 1 | Salesforce Composite Response Processing | Advanced |
| 2 | Lookup Map Data Transformation | Intermediate |
| 3 | Simple Statistics Aggregation | Beginner |
| 4 | URL Encoding for External IDs | Intermediate |
| 5 | Chunking Large Payloads | Intermediate |
| 6 | Error Deduplication | Beginner |
| 7 | Namespace Field Builder | Beginner |
| 8 | Filter-Reduce Chain | Intermediate |
| 9 | Retry Strategy Determination | Advanced |
| 10 | HTTP Status Error Mapping | Intermediate |
