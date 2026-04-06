# Gulf Distributing — Notes

Running notes from debugging sessions, design decisions, and gotchas.

<!-- Add entries with dates. Most recent first. -->

## 2026-04-06 — E2E Validation: OMS Invoice Debugging Session

### Context Loading Protocol walkthrough

Simulated a customer debugging session on branch `dzeder/gulf-oms-fix` to validate the full context loading chain. Findings below.

### Invoice__c vs Order__c naming convention

The OMS codebase uses **Invoice__c** internally (Invoice__c, Invoice_Item__c, Invoice_Fee__c) while the integration layer and Core data model use **Order__c** (ohfy__Order__c, ohfy__Order_Item__c). This is not a bug — Invoice is the OMS-specific object that represents a driver-facing sales order, while Order is the broader platform concept.

| Context | Object Name | Namespace |
|---------|------------|-----------|
| OMS Apex code | Invoice__c, Invoice_Item__c, Invoice_Fee__c | unmanaged (OMS package) |
| Core data model | ohfy__Order__c, ohfy__Order_Item__c | ohfy (managed) |
| Integration guides | ohfy__Order__c, ohfy__Order_Item__c | ohfy (external API) |
| Migration scripts | ohfy__Invoice__c | ohfy (namespaced) |

When debugging OMS issues, search for both `Invoice` and `Order` patterns in the source indexes.

### Trigger chain for Invoice_Item__c

The OMS trigger chain for Invoice_Item__c (from source index):
1. **InvoiceItemTrigger** (entry point) → fires on all DML events
2. **InvoiceItemTriggerService** (dispatcher) → routes to event-specific methods via `enabledMethods` set
3. **InvoiceItemBeforeInsert** / **InvoiceItemBeforeUpdate** / etc. (handlers) → business logic
4. Key handler classes: `InvoiceItem_BI_PreventDuplicateIIs`, `InvoiceItem_BI_AutoApplyPromotions`, `InvoiceItem_AU_UpdateKegDeposit`

The `enabledMethods` parameter allows per-method bypass — check `E_Invoice_StatusValidationBypass` for the bypass mechanism.

### Context loading gaps found and fixed

| Gap | Fix |
|-----|-----|
| Gulf CLAUDE.md had 5 broken skill paths (missing `ohanafy/` pillar dir) | Fixed all 5 paths |
| Template CLAUDE.md had same broken path pattern | Fixed |
| `notes.md` missing (referenced in loading order step 5) | Created |
| `customizations.md` missing (expected by template) | Created |
| No `orgs/production/` or `orgs/cam-sandbox/` directories | Created with mock snapshot |
| OMS source index missing Trigger→Handler Map, Service Layer Graph, Cross-Object Relationships, Common Patterns, Test Coverage Summary sections | Documented — requires re-running `sync-ohanafy-index.sh` with enhanced extraction (see roadmap) |
