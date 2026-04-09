"""Eval dataset for the tray-discovery skill.

Cases test connector discovery, relevance scoring, knowledge generation,
and integration opportunity detection for Ohanafy's beverage supply chain domain.
"""

EVAL_CASES = [
    {
        "name": "erp_connector_discovery",
        "description": "Discover ERP connectors relevant to beverage distribution",
        "tags": ["discovery", "erp", "beverage"],
        "input": {
            "query": "Find ERP connectors for beverage distribution companies",
            "domain": "beverage_supply_chain",
        },
        "expected": {
            "must_include_connectors": ["SAP", "NetSuite"],
            "min_opportunities": 2,
        },
        "recorded_output": {
            "connectors": [
                {
                    "name": "SAP",
                    "category": "ERP",
                    "relevance_score": 0.92,
                    "rationale": "Widely used by mid-to-large beverage distributors for inventory and order management",
                },
                {
                    "name": "NetSuite",
                    "category": "ERP",
                    "relevance_score": 0.88,
                    "rationale": "Cloud ERP popular with growing beverage companies, strong inventory modules",
                },
                {
                    "name": "Sage Intacct",
                    "category": "ERP",
                    "relevance_score": 0.65,
                    "rationale": "Financial-focused ERP, less common in beverage but used by some distributors",
                },
                {
                    "name": "Acumatica",
                    "category": "ERP",
                    "relevance_score": 0.58,
                    "rationale": "Cloud ERP with distribution modules, emerging in beverage space",
                },
            ],
            "knowledge_entries": [
                {
                    "connector_name": "SAP",
                    "category": "ERP",
                    "operations": ["RFC Function Call", "BAPI Call", "IDoc Send/Receive", "OData Query"],
                    "auth_methods": ["Basic Auth", "OAuth 2.0", "Certificate"],
                    "rate_limits": "Varies by SAP system config",
                    "beverage_relevance": "Primary ERP for major distributors (RNDC, Breakthru)",
                },
                {
                    "connector_name": "NetSuite",
                    "category": "ERP",
                    "operations": ["SuiteQL Query", "Record CRUD", "Saved Search", "RESTlet Call"],
                    "auth_methods": ["Token-Based Auth", "OAuth 2.0"],
                    "rate_limits": "10 concurrent requests, 5 requests/second",
                    "beverage_relevance": "Growing adoption among craft breweries and regional distributors",
                },
                {
                    "connector_name": "Sage Intacct",
                    "category": "ERP",
                    "operations": ["CRUD Operations", "Query", "Smart Events"],
                    "auth_methods": ["Web Services Auth"],
                    "rate_limits": "100 requests/minute",
                    "beverage_relevance": "Used for financial operations by some distributors",
                },
            ],
            "opportunities": [
                {
                    "title": "SAP-to-Salesforce Inventory Sync",
                    "source": "SAP",
                    "target": "Salesforce",
                    "use_case": "Real-time inventory levels from SAP warehouse modules to Ohanafy Salesforce org for sales rep visibility",
                    "priority": "high",
                },
                {
                    "title": "NetSuite Order-to-Cash Integration",
                    "source": "Salesforce",
                    "target": "NetSuite",
                    "use_case": "Push confirmed orders from Ohanafy OMS to NetSuite for fulfillment and invoicing",
                    "priority": "high",
                },
                {
                    "title": "Sage Intacct Financial Sync",
                    "source": "Sage Intacct",
                    "target": "Salesforce",
                    "use_case": "Sync AR/AP data for customer health scoring in Ohanafy REX",
                    "priority": "medium",
                },
            ],
        },
    },
    {
        "name": "ecommerce_connector_discovery",
        "description": "Discover eCommerce connectors for DTC beverage sales",
        "tags": ["discovery", "ecommerce", "dtc"],
        "input": {
            "query": "Find eCommerce connectors for direct-to-consumer beverage sales",
            "domain": "beverage_dtc",
        },
        "expected": {
            "must_include_connectors": ["Shopify"],
            "min_opportunities": 1,
        },
        "recorded_output": {
            "connectors": [
                {
                    "name": "Shopify",
                    "category": "eCommerce",
                    "relevance_score": 0.95,
                    "rationale": "Dominant DTC platform for beverage brands, strong API, existing Ohanafy integration patterns",
                },
                {
                    "name": "WooCommerce",
                    "category": "eCommerce",
                    "relevance_score": 0.62,
                    "rationale": "WordPress-based, used by some smaller beverage brands",
                },
                {
                    "name": "BigCommerce",
                    "category": "eCommerce",
                    "relevance_score": 0.55,
                    "rationale": "B2B eCommerce features useful for wholesale, less common in beverage",
                },
            ],
            "knowledge_entries": [
                {
                    "connector_name": "Shopify",
                    "category": "eCommerce",
                    "operations": ["Product CRUD", "Order List/Get", "Inventory Adjust", "Customer CRUD", "Webhook Subscribe"],
                    "auth_methods": ["OAuth 2.0", "Private App Token"],
                    "rate_limits": "2 requests/second (REST), 50 points/second (GraphQL)",
                    "beverage_relevance": "Most Ohanafy brewery/winery customers use Shopify for DTC. Existing Shopify_2GP patterns available.",
                },
                {
                    "connector_name": "WooCommerce",
                    "category": "eCommerce",
                    "operations": ["Product CRUD", "Order CRUD", "Customer CRUD", "Webhook"],
                    "auth_methods": ["OAuth 1.0a", "API Key"],
                    "rate_limits": "No official limit, recommended <25 requests/second",
                    "beverage_relevance": "Niche usage among craft brands with WordPress sites",
                },
            ],
            "opportunities": [
                {
                    "title": "Shopify DTC Order Sync",
                    "source": "Shopify",
                    "target": "Salesforce",
                    "use_case": "Sync DTC orders from Shopify to Ohanafy OMS for unified order management across wholesale and DTC channels",
                    "priority": "high",
                },
                {
                    "title": "Shopify Inventory Sync",
                    "source": "Salesforce",
                    "target": "Shopify",
                    "use_case": "Push real-time inventory levels from Ohanafy WMS to Shopify to prevent overselling",
                    "priority": "high",
                },
            ],
        },
    },
    {
        "name": "wms_connector_discovery",
        "description": "Discover WMS connectors for warehouse operations",
        "tags": ["discovery", "wms", "warehouse"],
        "input": {
            "query": "Find warehouse management system connectors for beverage distribution",
            "domain": "beverage_warehouse",
        },
        "expected": {
            "must_include_connectors": [],
            "min_opportunities": 1,
        },
        "recorded_output": {
            "connectors": [
                {
                    "name": "HTTP Client",
                    "category": "Universal",
                    "relevance_score": 0.85,
                    "rationale": "Most WMS systems (3PL Central, Deposco, HighJump) expose REST APIs — use HTTP Client connector for flexible integration",
                },
                {
                    "name": "FTP",
                    "category": "File Transfer",
                    "relevance_score": 0.72,
                    "rationale": "Many legacy WMS systems use SFTP file drops for EDI-style integration (ASN, PO, inventory files)",
                },
                {
                    "name": "CSV Parser",
                    "category": "Data Processing",
                    "relevance_score": 0.68,
                    "rationale": "VIP/SRS-style flat file ingestion from WMS systems that export daily CSV reports",
                },
            ],
            "knowledge_entries": [
                {
                    "connector_name": "HTTP Client",
                    "category": "Universal",
                    "operations": ["GET", "POST", "PUT", "PATCH", "DELETE", "Custom Headers", "OAuth/Bearer Auth"],
                    "auth_methods": ["Bearer Token", "OAuth 2.0", "Basic Auth", "API Key Header", "Custom"],
                    "rate_limits": "N/A — depends on target API",
                    "beverage_relevance": "Primary connector for WMS API integrations. Used for 3PL Central, Deposco, HighJump REST APIs.",
                },
                {
                    "connector_name": "FTP",
                    "category": "File Transfer",
                    "operations": ["List Files", "Download File", "Upload File", "Delete File", "Move File"],
                    "auth_methods": ["Username/Password", "SSH Key"],
                    "rate_limits": "Connection-based, typically 5 concurrent connections",
                    "beverage_relevance": "Legacy EDI file exchange with distributors and 3PLs. Common for ASN, PO acknowledgment, inventory snapshots.",
                },
            ],
            "opportunities": [
                {
                    "title": "3PL Inventory File Ingest",
                    "source": "FTP/SFTP",
                    "target": "Salesforce",
                    "use_case": "Daily pickup of inventory CSV files from 3PL warehouse, transform and load into Ohanafy WMS objects",
                    "priority": "high",
                },
            ],
        },
    },
]
