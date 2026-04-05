"""
Eval dataset for the data-harmonizer skill.

Each case is a synthetic Excel file with known correct mappings.
Replace these stubs with anonymized real customer data during discovery sprint.
"""

EVAL_CASES = [
    {
        "name": "basic_account_import",
        "description": "Simple retailer list with standard column names",
        "input": {
            "file_path": "evals/agents/data-harmonizer/fixtures/basic_accounts.csv",
            "customer_id": "eval-customer-001",
            "target_object": "Account",
        },
        "expected_mappings": {
            "Store Name": {"target_object": "Account", "target_field": "Name", "min_confidence": "high"},
            "City": {"target_object": "Account", "target_field": "BillingCity", "min_confidence": "high"},
            "State": {"target_object": "Account", "target_field": "BillingState", "min_confidence": "high"},
            "Phone Number": {"target_object": "Account", "target_field": "Phone", "min_confidence": "medium"},
        },
        "expected_unmapped": [],
    },
    {
        "name": "depletion_report_nonstandard",
        "description": "Depletion data with beverage-industry-specific column names",
        "input": {
            "file_path": "evals/agents/data-harmonizer/fixtures/depletions_nonstandard.csv",
            "customer_id": "eval-customer-002",
        },
        "expected_mappings": {
            "Cases Sold": {"target_object": "Depletion__c", "target_field": "Volume__c", "min_confidence": "high"},
            "Reporting Week": {"target_object": "Depletion__c", "target_field": "Report_Period__c", "min_confidence": "medium"},
            "House": {"target_object": "Distributor__c", "target_field": "Name", "min_confidence": "medium"},
            "Outlet": {"target_object": "Account", "target_field": "Name", "min_confidence": "medium"},
        },
        "expected_unmapped": ["Internal Notes"],
    },
    {
        "name": "product_catalog_with_dupes",
        "description": "Product list with duplicate SKUs that should be flagged",
        "input": {
            "file_path": "evals/agents/data-harmonizer/fixtures/products_with_dupes.csv",
            "customer_id": "eval-customer-003",
            "target_object": "Product2",
        },
        "expected_mappings": {
            "Item Name": {"target_object": "Product2", "target_field": "Name", "min_confidence": "high"},
            "UPC": {"target_object": "Product2", "target_field": "ProductCode", "min_confidence": "high"},
            "Category": {"target_object": "Product2", "target_field": "Family", "min_confidence": "medium"},
        },
        "expected_validation_issues": {
            "min_duplicate_warnings": 2,
        },
    },
    {
        "name": "mixed_data_ambiguous_columns",
        "description": "File with ambiguous columns that should be marked low-confidence or unmapped",
        "input": {
            "file_path": "evals/agents/data-harmonizer/fixtures/mixed_ambiguous.csv",
            "customer_id": "eval-customer-004",
        },
        "expected_mappings": {
            "Name": {"target_object": "Account", "target_field": "Name", "min_confidence": "medium"},
        },
        "expected_unmapped": ["Code", "Value", "Notes"],
    },
]
