# Gulf Distributing — Integration Inventory

External systems connected to Gulf's Ohanafy instance.

## Active Integrations

| Integration | Direction | Method | Frequency | Status |
|-------------|-----------|--------|-----------|--------|
| VIP (DB2/AS400) | Inbound | Azure Postgres staging DB | Migration batches | Active migration |
| GP Analytics | Bidirectional | Tray.io | Scheduled | Active |

## Tray.io Projects

| Project | Workflows | Purpose | Last Modified |
|---------|-----------|---------|---------------|
| <!-- fill --> | <!-- fill --> | GP Analytics sync | <!-- fill --> |

## Credentials & Authentication

| System | Auth Method | Named Credential | Notes |
|--------|-------------|-----------------|-------|
| VIP staging DB | Postgres credentials | N/A | Azure-hosted, connection string in vault |
| GP Analytics | <!-- fill --> | <!-- fill --> | Via Tray.io connector |

## Integration Patterns Used

- [ ] batch-processing.js
- [ ] data-mapping.js
- [ ] soql-query-builder.js
- [ ] error-handling.js
- [ ] csv-output.js

## Sync Patterns

### VIP → Ohanafy Migration
- Source: VIP DB2/AS400 data staged in Azure Postgres
- Target: Ohanafy production org
- Method: Batch migration scripts (see `scripts/migrations/vip-to-ohanafy/`)
- Key entities: Items (~8,743), Brands (~927), Accounts, Orders

### GP Analytics ↔ Ohanafy
- Placements and depletions data
- Via Tray.io integration workflows
