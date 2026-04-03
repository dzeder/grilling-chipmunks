# OHFY-Configure Source Index
> Last synced: 2026-04-03T12:19:03Z | Commit: 6b3a154 | Repo: Ohanafy/OHFY-Configure

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

## Custom Objects & Fields

