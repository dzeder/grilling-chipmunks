"""
Eval dataset for the data-harmonizer skill.

Each case is a synthetic Excel file with known correct mappings.
Replace these stubs with anonymized real customer data during discovery sprint.

The `recorded_output` field contains a pre-recorded agent output that the
scorer evaluates against the expected values. Update these when the agent
behavior changes significantly.
"""

EVAL_CASES = [
    {
        "name": "basic_account_import",
        "description": "Simple retailer list with standard column names",
        "tags": ["basic", "account", "standard-columns"],
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
        "recorded_output": {
            "mappings": [
                {"source_column": "Store Name", "target_object": "Account", "target_field": "Name", "confidence": "high", "rationale": "Direct name match to Account.Name"},
                {"source_column": "City", "target_object": "Account", "target_field": "BillingCity", "confidence": "high", "rationale": "Standard city field"},
                {"source_column": "State", "target_object": "Account", "target_field": "BillingState", "confidence": "high", "rationale": "Standard state field"},
                {"source_column": "Zip", "target_object": "Account", "target_field": "BillingPostalCode", "confidence": "high", "rationale": "Zip code to postal code"},
                {"source_column": "Phone Number", "target_object": "Account", "target_field": "Phone", "confidence": "medium", "rationale": "Phone Number likely maps to Phone"},
                {"source_column": "Type", "target_object": "Account", "target_field": "Type", "confidence": "medium", "rationale": "Account type classification"},
            ],
            "unmapped_columns": [],
            "validation_issues": [],
        },
    },
    {
        "name": "depletion_report_nonstandard",
        "description": "Depletion data with beverage-industry-specific column names",
        "tags": ["industry-specific", "depletion", "nonstandard-columns"],
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
        "recorded_output": {
            "mappings": [
                {"source_column": "Outlet", "target_object": "Account", "target_field": "Name", "confidence": "medium", "rationale": "Outlet is a retail account name in beverage distribution"},
                {"source_column": "House", "target_object": "Distributor__c", "target_field": "Name", "confidence": "medium", "rationale": "House is distributor name in beverage industry"},
                {"source_column": "Cases Sold", "target_object": "Depletion__c", "target_field": "Volume__c", "confidence": "high", "rationale": "Cases Sold maps to volume/depletion quantity"},
                {"source_column": "Reporting Week", "target_object": "Depletion__c", "target_field": "Report_Period__c", "confidence": "medium", "rationale": "Week-based reporting period"},
                {"source_column": "Brand", "target_object": "Product2", "target_field": "Name", "confidence": "medium", "rationale": "Brand name maps to product"},
            ],
            "unmapped_columns": ["Internal Notes"],
            "validation_issues": [],
        },
    },
    {
        "name": "product_catalog_with_dupes",
        "description": "Product list with duplicate SKUs that should be flagged",
        "tags": ["product", "duplicates", "validation"],
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
        "recorded_output": {
            "mappings": [
                {"source_column": "Item Name", "target_object": "Product2", "target_field": "Name", "confidence": "high", "rationale": "Item Name is the product name"},
                {"source_column": "UPC", "target_object": "Product2", "target_field": "ProductCode", "confidence": "high", "rationale": "UPC barcode is the standard product code"},
                {"source_column": "Category", "target_object": "Product2", "target_field": "Family", "confidence": "medium", "rationale": "Category maps to product family"},
                {"source_column": "Size", "target_object": "Product2", "target_field": "Size__c", "confidence": "low", "rationale": "Size may map to a custom size field"},
                {"source_column": "Active", "target_object": "Product2", "target_field": "IsActive", "confidence": "medium", "rationale": "Active flag maps to IsActive"},
            ],
            "unmapped_columns": [],
            "validation_issues": [
                {"type": "duplicate", "column": "UPC", "value": "012345678902", "rows": [2, 4], "message": "Duplicate UPC: 012345678902 (rows 2, 4)"},
                {"type": "duplicate", "column": "UPC", "value": "012345678901", "rows": [1, 6], "message": "Duplicate UPC: 012345678901 (rows 1, 6)"},
            ],
        },
    },
    {
        "name": "mixed_data_ambiguous_columns",
        "description": "File with ambiguous columns that should be marked low-confidence or unmapped",
        "tags": ["ambiguous", "edge-case", "low-confidence"],
        "input": {
            "file_path": "evals/agents/data-harmonizer/fixtures/mixed_ambiguous.csv",
            "customer_id": "eval-customer-004",
        },
        "expected_mappings": {
            "Name": {"target_object": "Account", "target_field": "Name", "min_confidence": "medium"},
        },
        "expected_unmapped": ["Code", "Value", "Notes"],
        "recorded_output": {
            "mappings": [
                {"source_column": "Name", "target_object": "Account", "target_field": "Name", "confidence": "medium", "rationale": "Name likely refers to account or entity name"},
                {"source_column": "Region", "target_object": "Account", "target_field": "Region__c", "confidence": "low", "rationale": "Region could map to a custom region field"},
            ],
            "unmapped_columns": ["Code", "Value", "Notes"],
            "validation_issues": [],
        },
    },
]
