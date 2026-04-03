# OHFY-Utilities Source Index
> Last synced: 2026-04-03T12:19:04Z | Commit: d109a8e | Repo: Ohanafy/OHFY-Utilities

## Apex Classes (22 production, 3 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| ContextManager | public | ContextManager is a singleton class that manages the context of the current exec |
| ContextManager_T | public |  |
| E_LookupController | public | The class is the underlying controller that holds methods in suppor |
| E_LookupController_T | public |  |
| U_SendEmailService | public | Service class for sending emails with custom HTML templates. |
| U_SendEmailService_T | public |  |
| U_ParseErrorMessage | global | A utility class for parsing custom error messages embedded within a larger error |
| U_ParseErrorMessage_T | public |  |
| U_FieldUtility | global | A Utility class for interacting with fields that are in fieldSets. Additionally, |
| U_FieldUtility_T | public |  |
| E_FieldsetCustomizationMDT | public | A Utility class for interacting with the Fieldset_Customization__md |
| UtilityMethods | public | Utility class providing general-purpose helper methods for common operations. |
| UtilityMethods_T | public |  |
| U_GlobalDescribeCache | global | Class to handle caching of global describe information. |
| U_GlobalDescribeCache_T | public |  |
| U_ObjectUtility | global | Utility class that is used to obtain records and its fields dynamically. |
| U_ObjectUtility_T | public | Test class for U_ObjectUtility |
| QueryService | public | Service class for building and executing SOQL queries using a fluent builder pat |
| QueryService_T | public |  |
| U_UserUtil | global | Utility class for retrieving portal user information. |
| U_UserUtil_T | public |  |
| U_UserUtilityExceptions | global | Exception classes for U_UserUtil operations. |

## Triggers

_No triggers found._

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| U_SendEmailService | sendEmailWithTemplate | `public static void sendEmailWithTemplate(` |
| QueryService | newBuilder | `public static QueryBuilder newBuilder(List<String> fields, String objectName) ` |
| QueryService | toSoql | `public String toSoql() ` |
| QueryService | execute | `public List<SObject> execute(System.AccessLevel level) ` |
| QueryService | execute | `public List<SObject> execute() ` |
| QueryService | execute | `public List<SObject> execute(Map<String, Object> binds, System.AccessLevel level) ` |
| QueryService | execute | `public List<SObject> execute(Map<String, Object> binds) ` |
| QueryService | fields | `public QueryBuilder fields(List<String> fields) ` |
| QueryService | addField | `public QueryBuilder addField(String field) ` |
| QueryService | filters | `public QueryBuilder filters(List<String> filters) ` |
| QueryService | addFilter | `public QueryBuilder addFilter(String filter) ` |
| QueryService | groupBy | `public QueryBuilder groupBy(List<String> groupBy) ` |
| QueryService | addGroupBy | `public QueryBuilder addGroupBy(String groupBy) ` |
| QueryService | orderBy | `public QueryBuilder orderBy(List<String> orderBy) ` |
| QueryService | addOrderBy | `public QueryBuilder addOrderBy(String orderBy) ` |
| QueryService | limitAmount | `public QueryBuilder limitAmount(Integer limitAmount) ` |
| QueryService | objectName | `public QueryBuilder objectName(String objectName) ` |
| QueryService | build | `public QueryService build() ` |

## Custom Objects & Fields

_No custom objects found._

