# Ohanafy Object Knowledge

Per-object field-level knowledge learned from real org usage. This is the **human context layer** — gotchas, picklist values, business meaning, and patterns that can't be derived from the schema alone.

## What belongs here

- Field gotchas discovered during debugging (e.g., "Order_Item uses `Is_Draft__c` not `Status__c`")
- Picklist values and their business meaning
- Status lifecycle and valid transitions
- Relationship patterns and dependency chains
- Cross-object interactions that aren't obvious from the schema

## What does NOT belong here

- Field names and types (auto-synced in `skills/ohanafy/ohfy-data-model-expert/references/source-index.md`)
- Trigger/service code details (curated in `skills/ohanafy/ohfy-core-expert/references/`)
- Customer-specific customizations (belong in `customers/<name>/customizations.md`)

## Objects documented

- [ohfy__Order__c](order.md) — Orders (sales, credits, transfers)
- [ohfy__Order_Item__c](order-item.md) — Line items on orders
