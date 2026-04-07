# OHFY-Payments Source Index
> Last synced: 2026-04-07T12:29:08Z | Commit: 738a2e1 | Repo: Ohanafy/OHFY-Payments

## Apex Classes (20 production, 2 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| BA_Invoice_EmailDispatchPmt | public |  |
| AccountFulfillmentLocationController | public |  |
| InvoiceFulfillmentLocationController | public |  |
| P_MerchantControllerPmt | public | Updates the Merchant Status when a new payments user begins an appl |
| P_MerchantControllerPmt_T | public |  |
| P_ProcessingAgreementControllerPmt | public |  |
| P_ProcessingAgreementControllerPmt_T | public |  |
| QA_CreatePaymentMethodPmt | public |  |
| QA_CreatePaymentMethodPmt_T | public | Created by alexsomer on 3/12/24. |
| TA_Account_BI_ProcessingFeeHandlerPmt | global |  |
| TA_Account_BI_ProcessingFeeHandlerPmt_T | public |  |
| TA_Account_BU_ProcessingFeeHandlerPmt | global |  |
| TA_Account_BU_ProcessingFeeHandlerPmt_T | public |  |
| TA_Invoice_AU_EmailDispatchPmt | global |  |
| TA_Invoice_AU_EmailDispatchPmt_T | public |  |
| TA_Invoice_BI_PaymentFieldsSetter | global |  |
| TA_Invoice_BI_PaymentFieldsSetter_T | public |  |
| TA_PaymentMethodPmt_BI_DefaultChecker | global |  |
| TA_PaymentMethodPmt_BI_DefaultChecker_T | public |  |
| U_GetRecordData | public |  |

## Triggers (1)

| Trigger | sObject | Events |
|---------|---------|--------|
| PaymentMethodPmtTrigger | Payment_Method_Pmt__c |  |

## Trigger → Handler Map

> **Coverage Limitations:** This map captures static patterns only (direct class
> instantiation, method calls visible in trigger body). Dynamic dispatch, factory
> patterns, and conditional handler resolution are not captured.

| Trigger | sObject | Handler Class | Call Pattern |
|---------|---------|---------------|-------------|
| PaymentMethodPmtTrigger | Payment_Method_Pmt__c | MetadataTriggerHandler | new ClassName() |

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| TA_Account_BI_ProcessingFeeHandlerPmt | beforeInsert | `global static void beforeInsert(List<Account> newList) ` |
| TA_Account_BU_ProcessingFeeHandlerPmt | beforeUpdate | `global static void beforeUpdate(List<Account> newList, List<Account> oldList) ` |

## Service Layer Graph (one level deep)

> **Coverage Limitations:** Captures static patterns only: `new *Service(`,
> `ServiceLocator.getInstance(`, `System.enqueueJob`. Dynamic dispatch and
> factory patterns are not captured. Treat as a starting map, not exhaustive.

| Service Class | Calls / Instantiates | Pattern |
|--------------|---------------------|---------|

## Cross-Object Relationships (8)

| From Object | Field | Type | To Object |
|-------------|-------|------|-----------|
| Location__c | Payment_Configuration_Pmt__c | Lookup | Payment_Configuration_Pmt__c |
| Order__c | Payment_Method_Pmt__c | Lookup | Payment_Method_Pmt__c |
| Payment_Method_Pmt__c | Customer_Pmt__c | MasterDetail | Account |
| Payment_Method_Pmt__c | Payment_Configuration_Pmt__c | Lookup | Payment_Configuration_Pmt__c |
| Payment_Pmt__c | Customer_Pmt__c | Lookup | Account |
| Payment_Pmt__c | Invoice_Lookup_Pmt__c | Lookup | Order__c |
| Payment_Pmt__c | Payment_Configuration_Pmt__c | Lookup | Payment_Configuration_Pmt__c |
| Payment_Pmt__c | Payment_Method_Pmt__c | Lookup | Payment_Method_Pmt__c |

## Custom Objects & Fields

## Common Patterns

| Pattern | Files Using It | Notes |
|---------|---------------|-------|
| Trigger Bypass | 0 | Classes referencing bypass mechanisms |
| Service Locator | 0 | Classes using service locator pattern |
| Batch/Schedulable | 2 | Classes implementing batch or schedulable |
| Queueable | 0 | Classes using async queueable jobs |
| Platform Events | 0 | Classes publishing or subscribing to events |

## Test Coverage Summary

| Metric | Count |
|--------|-------|
| Production classes | 12 |
| Test/Mock/Stub classes | 10 |
| Test-to-production ratio | 83% |

### Classes Without Apparent Test Coverage (2)

- `BA_Invoice_EmailDispatchPmt`
- `U_GetRecordData`

## Known Gotchas

_No known gotchas recorded yet. This section is populated by operational learnings from debugging sessions._

