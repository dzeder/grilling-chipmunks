# OHFY-Payments Source Index
> Last synced: 2026-04-03T12:19:00Z | Commit: 738a2e1 | Repo: Ohanafy/OHFY-Payments

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

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| TA_Account_BI_ProcessingFeeHandlerPmt | beforeInsert | `global static void beforeInsert(List<Account> newList) ` |
| TA_Account_BU_ProcessingFeeHandlerPmt | beforeUpdate | `global static void beforeUpdate(List<Account> newList, List<Account> oldList) ` |

## Custom Objects & Fields

