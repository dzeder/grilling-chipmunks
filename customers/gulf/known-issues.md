# Gulf Distributing — Known Issues

Running log of known issues, workarounds, and resolutions for Gulf.

## Open Issues

### GULF-001: FIELD_CUSTOM_VALIDATION_EXCEPTION on mixed keg deposit invoices

- **Reported:** 2026-04-06
- **Severity:** High — blocks driver invoice creation in the field
- **Symptom:** Drivers get `FIELD_CUSTOM_VALIDATION_EXCEPTION` when creating invoices that combine keg deposit items with standard product items. Fires intermittently, only on invoices with 10+ line items.
- **Affected objects:** `ohfy__Invoice_Item__c`, `ohfy__Invoice__c`
- **Validation rule:** `VR_Invoice_Item_Mixed_Deposit_Check` (see `customers/gulf/orgs/production/org-snapshot.md`)
- **Trigger chain:**
  1. `InvoiceItemTrigger` fires on `Invoice_Item__c` insert
  2. → `InvoiceItemTriggerService.beforeInsert()` dispatches to enabled methods
  3. → `InvoiceItemBeforeInsert` runs validation logic
  4. → `VR_Invoice_Item_Mixed_Deposit_Check` validation rule fires when item type is `Keg` and invoice has 10+ line items
- **Cross-references:**
  - OMS source index: `skills/ohanafy/ohfy-oms-expert/references/source-index.md` — see `InvoiceItemTriggerService`, `InvoiceItemBeforeInsert`, `InvoiceItem_AU_UpdateKegDeposit`
  - Core source index: `skills/ohanafy/ohfy-core-expert/references/source-index.md` — trigger framework patterns, `U_OrderStatusValidationBypass` bypass mechanism
- **Hypothesis:** The validation rule checks `Invoice_Item__c` count per invoice but does not account for the batch insert context — when 10+ items are inserted in a single DML, the count query includes the items being inserted, causing a false positive on the deposit fee association check.
- **Workaround:** Split mixed keg/standard orders into separate invoices (confirmed by field team).
- **Next steps:** Review `VR_Invoice_Item_Mixed_Deposit_Check` rule definition; check if `E_Invoice_StatusValidationBypass` can temporarily bypass; coordinate fix with Ohanafy engineering.

## Resolved Issues

<!-- Move issues here when resolved. Add resolution date and what fixed it. -->

## Recurring Patterns

<!-- Issues that keep coming back. Document the pattern so agents recognize it faster. -->
