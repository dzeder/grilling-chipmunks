# Examples — data-harmonizer

Real usage examples against Ohanafy data.

## Example 1: Basic Account Import

```python
from skills.salesforce.data_harmonizer.skill import run
from skills.salesforce.data_harmonizer.schema import InputSchema

result = run(InputSchema(
    file_path="data/acme-retailers.csv",
    customer_id="acme-corp",
    target_object="Account",
))

# Expected output:
# {
#     "status": "success",
#     "batch_id": "batch-a1b2c3d4e5f6",
#     "mapping": {
#         "mappings": [
#             {"source_column": "Store Name", "target_object": "Account", "target_field": "Name",
#              "confidence": "high", "rationale": "Direct match to Account.Name"},
#             {"source_column": "City", "target_object": "Account", "target_field": "BillingCity",
#              "confidence": "high", "rationale": "Standard city field"},
#         ],
#         "unmapped_columns": [],
#     },
#     "staged_records": [...],
#     "validation_issues": [],
#     "stats": {"total_rows": 50, "mapped_rows": 50, "error_rows": 0, "warning_rows": 0}
# }
```

## Example 2: Depletion Report with Industry Jargon

```python
result = run(InputSchema(
    file_path="data/gulf-coast-depletions-w12.xlsx",
    customer_id="gulf-coast-dist",
))

# Expected output:
# {
#     "status": "needs_review",
#     "mapping": {
#         "mappings": [
#             {"source_column": "Cases Sold", "target_object": "Depletion__c",
#              "target_field": "Volume__c", "confidence": "high",
#              "rationale": "'Cases Sold' is a standard depletion volume synonym"},
#             {"source_column": "House", "target_object": "Distributor__c",
#              "target_field": "Name", "confidence": "medium",
#              "rationale": "'House' is beverage industry slang for distributor"},
#         ],
#         "unmapped_columns": ["Internal Notes"],
#     },
#     ...
# }
```

## Example 3: Dry Run (validate without staging)

```python
result = run(InputSchema(
    file_path="data/new-customer-products.csv",
    customer_id="new-customer",
    dry_run=True,
))

# staged_records will be empty in dry_run mode
# mapping and validation_issues are still populated
```

## Example 4: Error Case — Unsupported File

```python
result = run(InputSchema(
    file_path="data/report.pdf",
    customer_id="acme-corp",
))

# Expected output:
# {
#     "status": "error",
#     "error": {
#         "code": "UNSUPPORTED_FORMAT",
#         "message": "Unsupported file type: .pdf. Supported: {'.xlsx', '.csv'}"
#     }
# }
```
