# Relevance Scoring

How the Tray Discovery pipeline scores connector relevance to Ohanafy.

## Scoring Model

Uses Claude haiku for fast classification (0.0 - 1.0 scale).
Weighted multi-dimension scoring — overall score is the weighted sum.

## Score Thresholds

- >= 0.85 — High relevance. Auto-generate knowledge file + create GitHub issue.
- >= 0.65 — Medium relevance. Create GitHub issue for team triage.
- < 0.65 — Low relevance. Catalog in registry, no issue created.

## Scoring Dimensions

### supply_chain_fit (weight: 0.30)
- Directly supports beverage distribution workflows
- 3-tier distribution, TTB compliance, depletions, allocation
- Logistics, shipping, warehouse management, EDI
- Inventory tracking, order management

### existing_stack_synergy (weight: 0.25)
- Integrates with Salesforce (Ohanafy's CRM)
- Integrates with AWS services (S3, Lambda, RDS)
- Integrates with QuickBooks (accounting sync)
- Integrates with Slack, Google Sheets, or other active Ohanafy services
- Complements existing Tray workflows in skills/tray-ai/workflows/

### customer_value (weight: 0.20)
- Benefits Ohanafy's customers: distributors, suppliers, retailers
- Enables customer-facing integrations or self-service
- Improves data flow between customer systems and Ohanafy

### operational_efficiency (weight: 0.15)
- Automates a currently manual process at Ohanafy
- Reduces time-to-value for common operations
- Replaces fragile custom code with a managed connector

### data_enrichment (weight: 0.10)
- Adds data signals useful for analytics or reporting
- Enables AI/ML features with richer input data
- Supports DataCloud or similar enrichment pipelines

## Anti-Patterns

- Generic developer tools with no supply chain connection → score low
- Connectors for industries unrelated to beverage distribution → score 0
- Deprecated or sunset connectors → score 0
- Social media advertising platforms (unless tied to DTC ecommerce) → score low
- Connectors that duplicate functionality already active in Ohanafy's stack → score as optimize_existing, not new_integration
