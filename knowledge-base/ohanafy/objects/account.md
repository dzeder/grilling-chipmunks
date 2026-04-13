# Account (standard object with ohfy customizations)

Standard Salesforce Account extended by the Ohanafy managed package with custom fields, record types, triggers, and picklists.

## Quick facts

- **Namespace:** Standard object with ohfy__ custom fields
- **Triggers:** ohfy.AccountTrigger (managed, uses ServiceLocator pattern)
- **External ID:** `ohfy__External_ID__c` (managed field)
- **Key custom fields:** Market__c, Premise_Type__c, Retail_Type__c, Chain_Banner__c, Store_Number__c, Is_Active__c

## AccountTrigger blocker

`ohfy.AccountTrigger` fires on AfterUpdate and calls `AccountTriggerMethods` via the ServiceLocator pattern. In subscriber orgs where `AccountTriggerMethods` class is not deployed:

- **INSERT succeeds** — AfterInsert handler may not call the missing class
- **UPDATE fails** — `ServiceLocator.ServiceLocatorException: Invalid implementation class: AccountTriggerMethods`

This means:
- First data load (creates) works fine
- Second data load (upserts = updates) fails on every Account record
- **Hard blocker for daily sync idempotency** — Ohanafy engineering must deploy the missing class or update the ServiceLocator config

### Workaround

In Tray/pipeline, set `allOrNone=false` and log Account update errors separately. Account creates succeed; updates accumulate until the trigger is fixed.

## Record types

Record types affect field access, picklist values, and business logic:

| Record Type | DeveloperName | Use Case |
|-------------|---------------|----------|
| Chain_Banner | `Chain_Banner` | Parent accounts for retail chains |
| Customer | `Customer` | Supplier's direct buyer (distributor/wholesaler) |
| Distributed_Customer | `Distributed_Customer` | Distributor's retail customer (bar, store, restaurant) |

- **Integration user must have all needed record types assigned** on their profile
- Chain Banners: set `ohfy__Is_Chain_Banner__c = true`, `Type = 'Chain Banner'`
- Customers (supplier perspective): `Type = 'Customer'`, `ohfy__Retail_Type__c = 'Distributor'`
- Distributed Customers: `Type = 'Distributed Customer'`, link to Chain_Banner via `ohfy__Chain_Banner__r`

## Picklist gotchas

### ohfy__Market__c (RESTRICTED)

Restricted picklist — values vary by org. Always describe the field before building crosswalks. Not all source data values will have a match (e.g., 14 of 46 VIP Class of Trade codes have no matching picklist value: Military, E-Commerce, CBD/THC, etc.).

### AccountSource (NOT restricted)

The API accepts any string value. Custom values (e.g., `VIP SRS`) work for tagging but won't appear in picklist dropdowns until manually added via Setup.

## External ID

`ohfy__External_ID__c` is the managed external ID field. Note this is different from other objects:
- Account: `ohfy__External_ID__c` (managed)
- Contact: `External_ID__c` (unmanaged custom)
- Most VIP objects: `VIP_External_ID__c` (unmanaged custom)

Always check the field name per object — don't assume consistency.

## Discovered in

- VIP SRS Phase 5b (2026-04-10): AccountTrigger blocker discovered on Account re-upsert
- VIP SRS Phase 5b (2026-04-10): Supplier perspective clarified (distributors = Customers, retailers = Distributed Customers)
- VIP SRS Phase 5e (2026-04-13): AccountTrigger blocks Chain Banner UPDATES on second E2E run
