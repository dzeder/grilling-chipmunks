# OHFY-Planogram Source Index
> Last synced: 2026-04-07T12:29:05Z | Commit: 47a0729 | Repo: Ohanafy/OHFY-Planogram

## Apex Classes (4 production, 3 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| PlanogramApiResponse | public | Response wrapper classes for AWS Planogram API |
| PlanogramComplianceController | public | Apex Controller for Planogram Compliance LWC |
| PlanogramResultHandler | public | Handler class for Planogram_Result__e Platform Event trigger |
| PlanogramTemplateResultHandler | public | Handler for Planogram_Template_Result__e Platform Event |

## Triggers (2)

| Trigger | sObject | Events |
|---------|---------|--------|
| PlanogramResultTrigger | Planogram_Result__e | after insert |
| PlanogramTemplateResultTrigger | Planogram_Template_Result__e | after insert |

## Trigger → Handler Map

> **Coverage Limitations:** This map captures static patterns only (direct class
> instantiation, method calls visible in trigger body). Dynamic dispatch, factory
> patterns, and conditional handler resolution are not captured.

| Trigger | sObject | Handler Class | Call Pattern |
|---------|---------|---------------|-------------|
| PlanogramResultTrigger | Planogram_Result__e | PlanogramResultHandler.handleResults | Class.method() |
| PlanogramTemplateResultTrigger | Planogram_Template_Result__e | PlanogramTemplateResultHandler.handleResults | Class.method() |

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| PlanogramResultHandler | handleResults | `public static void handleResults(List<Planogram_Result__e> events) ` |
| PlanogramTemplateResultHandler | handleResults | `public static void handleResults(List<Planogram_Template_Result__e> events) ` |

## Service Layer Graph (one level deep)

> **Coverage Limitations:** Captures static patterns only: `new *Service(`,
> `ServiceLocator.getInstance(`, `System.enqueueJob`. Dynamic dispatch and
> factory patterns are not captured. Treat as a starting map, not exhaustive.

| Service Class | Calls / Instantiates | Pattern |
|--------------|---------------------|---------|

## Cross-Object Relationships (3)

| From Object | Field | Type | To Object |
|-------------|-------|------|-----------|
| Planogram_Job__c | Planogram_Template__c | Lookup | Planogram_Template__c |
| Planogram_Job__c | Store__c | Lookup | Account |
| Planogram_Template__c | Account__c | Lookup | Account |

## Custom Objects & Fields

### Planogram_JobRequested__e (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Backend_Template_Id__c | Text | false |  |
| Org_Id__c | Text | false |  |
| Planogram_File_Id__c | Text | false |  |
| Planogram_Job_Id__c | Text | false |  |
| Planogram_Template_Id__c | Text | false |  |
| Shelf_Number__c | Text | false |  |
| Shelf_Photo_File_Ids__c | Text | false |  |
| Store__c | Text | false |  |

### Planogram_Job__c (13 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Compliance_Score__c | Number | false |  |
| External_Job_Id__c | Text | false |  |
| Issues_Json__c | LongTextArea | false |  |
| Overall_Compliance_Score__c | Number | false |  |
| Overall_Status__c | Text | false |  |
| Planogram_File_Id__c | Text | false |  |
| Planogram_Template__c | Lookup | true | Planogram_Template__c |
| Result_Json__c | LongTextArea | false |  |
| Shelf_Photo_File_Ids__c | LongTextArea | false |  |
| Status__c | Picklist | false |  |
| Store_Identifier__c | Text | false |  |
| Store__c | Lookup | false | Account |
| Test_Field__c | Text | false |  |

### Planogram_Result__e (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Compliance_Score__c | Number | false |  |
| External_Job_Id__c | Text | false |  |
| Issues_Json__c | LongTextArea | false |  |
| Overall_Compliance_Score__c | Number | false |  |
| Overall_Status__c | Text | false |  |
| Planogram_Job_Id__c | Text | false |  |
| Result_Json__c | LongTextArea | false |  |
| Status__c | Text | false |  |

### Planogram_Template_Requested__e (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ContentVersion_Id__c | Text | false |  |
| Description__c | Text | false |  |
| Org_Id__c | Text | false |  |
| Store_Id__c | Text | false |  |
| Store_Name__c | Text | false |  |
| Template_Id__c | Text | false |  |

### Planogram_Template_Result__e (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Backend_Template_Id__c | Text | false |  |
| Error_Message__c | LongTextArea | false |  |
| Metadata_Json__c | LongTextArea | false |  |
| Status__c | Text | false |  |
| Template_Id__c | Text | false |  |

### Planogram_Template__c (7 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account__c | Lookup | false | Account |
| Backend_Template_Id__c | Text | false |  |
| Metadata_Json__c | LongTextArea | false |  |
| Planogram_File_ContentVersion_Id__c | Text | false |  |
| Planogram_File_Id__c | Text | false |  |
| Status__c | Picklist | false |  |
| Store_Identifier__c | Text | false |  |

## Common Patterns

| Pattern | Files Using It | Notes |
|---------|---------------|-------|
| Trigger Bypass | 0 | Classes referencing bypass mechanisms |
| Service Locator | 0 | Classes using service locator pattern |
| Batch/Schedulable | 0 | Classes implementing batch or schedulable |
| Queueable | 0 | Classes using async queueable jobs |
| Platform Events | 5 | Classes publishing or subscribing to events |

## Test Coverage Summary

| Metric | Count |
|--------|-------|
| Production classes | 4 |
| Test/Mock/Stub classes | 3 |
| Test-to-production ratio | 75% |

### Classes Without Apparent Test Coverage (1)

- `PlanogramApiResponse`

## Known Gotchas

_No known gotchas recorded yet. This section is populated by operational learnings from debugging sessions._

