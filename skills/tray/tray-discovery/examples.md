# Examples

## Example: High-Relevance Connector (Salesforce)

**Discovered entry:**
```yaml
name: salesforce
display_name: Salesforce
category: crm
operations: [create_record, update_record, query, bulk_upsert, get_metadata]
operation_count: 15
```

**Assessment:**
```yaml
overall_score: 0.95
dimensions:
  - supply_chain_fit: 0.90 (Ohanafy's entire CRM layer)
  - existing_stack_synergy: 1.00 (already active)
  - customer_value: 0.95 (all customer data lives here)
  - operational_efficiency: 0.90 (automates record sync)
  - data_enrichment: 0.85 (feeds analytics/DataCloud)
opportunity_type: optimize_existing
current_usage: active
```

**Result:** Knowledge file generated + GitHub issue created.

## Example: Medium-Relevance Connector (ShipStation)

**Discovered entry:**
```yaml
name: shipstation
display_name: ShipStation
category: edi_supply_chain
operations: [create_order, get_rates, create_label, track_shipment]
operation_count: 8
```

**Assessment:**
```yaml
overall_score: 0.72
dimensions:
  - supply_chain_fit: 0.85 (shipping/logistics for DTC)
  - existing_stack_synergy: 0.50 (not currently used)
  - customer_value: 0.75 (benefits retailers doing DTC)
  - operational_efficiency: 0.70 (could automate fulfillment)
  - data_enrichment: 0.50 (tracking data)
opportunity_type: new_integration
current_usage: not_configured
```

**Result:** GitHub issue created for team triage. No knowledge file.

## Example: Low-Relevance Connector (TikTok Ads)

**Discovered entry:**
```yaml
name: tiktok-ads
display_name: TikTok Ads
category: other
operations: [create_campaign, get_analytics, manage_audience]
operation_count: 6
```

**Assessment:**
```yaml
overall_score: 0.15
dimensions:
  - supply_chain_fit: 0.0 (no supply chain connection)
  - existing_stack_synergy: 0.0 (not in Ohanafy's stack)
  - customer_value: 0.20 (some beverage brands advertise)
  - operational_efficiency: 0.10 (not a current workflow)
  - data_enrichment: 0.15 (ad metrics not useful)
opportunity_type: not_relevant
current_usage: not_configured
```

**Result:** Cataloged in registry only. No issue, no knowledge file.
