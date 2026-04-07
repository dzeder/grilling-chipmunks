# OHFY-Configure Source Index
> Last synced: 2026-04-07T12:29:11Z | Commit: 6b3a154 | Repo: Ohanafy/OHFY-Configure

## Apex Classes (10 production, 10 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| OHFYAccountDataService | public | Data service for account-related operations - DYNAMIC UI API ONLY |
| OHFYConfigurationController | global | Controller for OHFY Configuration management |
| OHFYConfigurationDataService | public | Core configuration data service - delegates to domain-specific serv |
| OHFYDashboardDataService | public | Data service for dashboard and activity-related operations |
| OHFYDataFactory | public | Factory class for creating sample data objects |
| OHFYLocationDataService | public | Data service for location-related operations |
| OHFYPackageInstallHandler | global | Package installation handler for OHFY Configuration |
| OHFYProductDataService | public | Data service for product-related operations |
| OHFYRouteDataService | public | Data service for route-related operations |
| OHFYSchemaUtility | public | Utility class for detecting OHFY-Core schema objects and fields |

## Triggers

_No triggers found._

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| OHFYAccountDataService | getAccountStatuses | `public static List<AccountStatusWrapper> getAccountStatuses() ` |
| OHFYAccountDataService | getAccountTypes | `public static List<AccountTypeWrapper> getAccountTypes() ` |
| OHFYAccountDataService | getPricelistGroups | `public static List<PricelistGroupWrapper> getPricelistGroups() ` |
| OHFYAccountDataService | getAssignmentRules | `public static List<AssignmentRuleWrapper> getAssignmentRules() ` |
| OHFYAccountDataService | getAccountRecordTypes | `public static List<RecordTypeWrapper> getAccountRecordTypes() ` |
| OHFYAccountDataService | processUILayoutData | `public static List<FieldMetadataWrapper> processUILayoutData(String layoutData, String recordTypeId) ` |
| OHFYAccountDataService | enhanceFieldMetadata | `public static List<FieldMetadataWrapper> enhanceFieldMetadata(String processedFieldsJson, String recordTypeId) ` |
| OHFYAccountDataService | createAccount | `public static String createAccount(Map<String, Object> accountData, String recordTypeId) ` |
| OHFYConfigurationDataService | createAccount | `public static String createAccount(Map<String, Object> accountData, String recordTypeId) ` |
| OHFYDashboardDataService | compare | `public Integer compare(Map<String, Object> a1, Map<String, Object> a2) ` |
| OHFYDashboardDataService | compare | `public Integer compare(Map<String, Object> a1, Map<String, Object> a2) ` |
| OHFYPackageInstallHandler | onInstall | `global void onInstall(InstallContext context) ` |
| OHFYProductDataService | getProductCountForCategory | `public static Integer getProductCountForCategory(String categoryId) ` |

## Service Layer Graph (one level deep)

> **Coverage Limitations:** Captures static patterns only: `new *Service(`,
> `ServiceLocator.getInstance(`, `System.enqueueJob`. Dynamic dispatch and
> factory patterns are not captured. Treat as a starting map, not exhaustive.

| Service Class | Calls / Instantiates | Pattern |
|--------------|---------------------|---------|

## Custom Objects & Fields

## Common Patterns

| Pattern | Files Using It | Notes |
|---------|---------------|-------|
| Trigger Bypass | 0 | Classes referencing bypass mechanisms |
| Service Locator | 0 | Classes using service locator pattern |
| Batch/Schedulable | 0 | Classes implementing batch or schedulable |
| Queueable | 0 | Classes using async queueable jobs |
| Platform Events | 0 | Classes publishing or subscribing to events |

## Test Coverage Summary

| Metric | Count |
|--------|-------|
| Production classes | 10 |
| Test/Mock/Stub classes | 10 |
| Test-to-production ratio | 100% |

## Known Gotchas

_No known gotchas recorded yet. This section is populated by operational learnings from debugging sessions._

