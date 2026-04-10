# Shipyard Brewing Company — Integration Inventory

External systems connected to this customer's Ohanafy instance.

## Active Integrations

| Integration | Direction | Method | Frequency | Status |
|-------------|-----------|--------|-----------|--------|
| VIP SRS (9 file types) | Inbound | SFTP → Tray.io → SF Composite API | Daily | Scripts complete, Tray build next |

<!-- Direction: Inbound (to SF), Outbound (from SF), Bidirectional -->
<!-- Method: Tray.io, SF Connect, REST API, SFTP, Manual -->
<!-- Frequency: Real-time, Hourly, Daily, Weekly, On-demand -->

## VIP SRS Integration Details

**Source:** 9 gzipped CSV files delivered daily via SFTP from VIP
**Target:** 14 Ohanafy Salesforce objects
**Source code:** `integrations/vip-srs/`
**Spec:** `.context/attachments/VIP_AGENT_HANDOFF.md`

### File Types

| File | Target Objects | Rows/Day |
|------|---------------|----------|
| SRSCHAIN | Account (Chain Banners) | ~6,633 |
| ITM2DA | Item_Line__c, Item_Type__c, Item__c | ~65 |
| DISTDA | Location__c | ~13 (1 after filtering) |
| ITMDA | Item__c (enrichment) | ~102 |
| OUTDA | Account (Outlets), Contact (Buyers) | ~36,587 (filtered by dist) |
| SLSDA | Depletion__c, Placement__c | ~110 |
| INVDA | Inventory__c, Inventory_History__c, Inventory_Adjustment__c | ~656 |
| CTLDA | Allocation__c | ~24 |
| SRSVALUE | Not loaded — used as crosswalk reference | ~177 |

### Load Order

Phase 1 (parallel): SRSCHAIN, ITM2DA, DISTDA
Phase 2 (parallel): ITMDA, OUTDA
Phase 3: INVDA
Phase 4: SLSDA, CTLDA
Cleanup: Stale record deletion

## Tray.io Projects

| Project | Workflows | Purpose | Last Modified |
|---------|-----------|---------|---------------|
| VIP_SRS_Shipyard_SANDBOX | TBD | Sandbox integration | Building |

## Credentials & Authentication

| System | Auth Method | Named Credential | Notes |
|--------|-------------|-----------------|-------|
| VIP SFTP | TBD | TBD | SFTP endpoint for file pickup |
| Salesforce | SF Connected App | TBD | Tray.io → SF via Composite API |

## Integration Patterns Used

- `integrations/patterns/script-scaffold.js` — Base template for all scripts
- `integrations/patterns/batch-processing.js` — 25-record chunking for SF Composite API
- `integrations/patterns/validation.js` — Required field validation
- `integrations/patterns/string-manipulation.js` — Title case, phone formatting
- `integrations/patterns/date-time.js` — YYYYMMDD → YYYY-MM-DD conversion

## Known Integration Issues

- **AccountTriggerMethods missing:** Blocks Account AfterUpdate (upserts). See `known-issues.md`.
- **Item lookup filter chain:** Depletion__c.Item__c requires Finished Good RT + Type__c + UOM__c + Packaging_Type__c + Transformation_Setting__c. See `customizations.md`.
