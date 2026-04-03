# Skill Routing Matrix

Cross-skill handoff rules. When a skill encounters work outside its scope, route to the correct skill instead of attempting it inline.

## Salesforce Core Handoffs

| From | Trigger | Route To |
|------|---------|----------|
| **sf-apex** | Flow XML or Flow orchestration | **sf-flow** |
| **sf-apex** | LWC JavaScript/HTML/CSS | **sf-lwc** |
| **sf-apex** | SOQL-only query tuning | **sf-soql** |
| **sf-apex** | Deploying or validating to org | **sf-deploy** |
| **sf-apex** | Custom object/field metadata | **sf-metadata** |
| **sf-flow** | Apex invocable action needed | **sf-apex** |
| **sf-flow** | Custom objects referenced in flow | **sf-metadata** |
| **sf-flow** | Deploy flow to org | **sf-deploy** |
| **sf-lwc** | Apex controller/wire adapter | **sf-apex** |
| **sf-lwc** | Custom object schema questions | **sf-metadata** |
| **sf-lwc** | Deploy component to org | **sf-deploy** |
| **sf-soql** | Query needs Apex wrapper | **sf-apex** |
| **sf-soql** | Data Cloud SQL (not SOQL) | **sf-datacloud-retrieve** |
| **sf-metadata** | Permission set analysis | **sf-permissions** |
| **sf-metadata** | Deploy metadata to org | **sf-deploy** |
| **sf-metadata** | Flow XML in metadata | **sf-flow** |
| **sf-testing** | Agent conversation testing | **sf-ai-agentforce-testing** |
| **sf-testing** | Debug log analysis | **sf-debug** |
| **sf-deploy** | Apex test failures blocking deploy | **sf-testing** |
| **sf-deploy** | Connected App/OAuth setup | **sf-connected-apps** |

## Salesforce AI / Agentforce Handoffs

| From | Trigger | Route To |
|------|---------|----------|
| **sf-ai-agentforce** | Agent Script DSL (.agent files) | **sf-ai-agentscript** |
| **sf-ai-agentforce** | Agent testing/conversation QA | **sf-ai-agentforce-testing** |
| **sf-ai-agentforce** | Persona design/utterance libraries | **sf-ai-agentforce-persona** |
| **sf-ai-agentscript** | Agent config via Setup UI | **sf-ai-agentforce** |
| **sf-ai-agentforce-testing** | Fix agent behavior | **sf-ai-agentscript** |
| **sf-ai-agentforce-testing** | Apex unit tests (not agent tests) | **sf-testing** |
| **sf-ai-agentforce-observability** | Session tracing from Data Cloud | **sf-datacloud-retrieve** |

## Data Cloud Handoffs

| From | Trigger | Route To |
|------|---------|----------|
| **sf-datacloud** (orchestrator) | Connect phase | **sf-datacloud-connect** |
| **sf-datacloud** | Prepare phase (streams, DLOs) | **sf-datacloud-prepare** |
| **sf-datacloud** | Harmonize phase (DMOs, identity) | **sf-datacloud-harmonize** |
| **sf-datacloud** | Segment phase | **sf-datacloud-segment** |
| **sf-datacloud** | Act phase (activations) | **sf-datacloud-act** |
| **sf-datacloud** | Retrieve phase (SQL, search) | **sf-datacloud-retrieve** |
| **sf-datacloud-*** | Standard CRM SOQL | **sf-soql** |
| **sf-datacloud-*** | STDM/session tracing | **sf-ai-agentforce-observability** |

## Integration Handoffs

| From | Trigger | Route To |
|------|---------|----------|
| **sf-integration** | Connected App/OAuth config | **sf-connected-apps** |
| **sf-integration** | Apex callout code | **sf-apex** |
| **sf-integration** | Data import/export operations | **sf-data** |
| **sf-connected-apps** | Named Credentials for callouts | **sf-integration** |
| **sf-connected-apps** | Permission policies | **sf-permissions** |
| **tray-expert** | Salesforce API errors in workflow | **sf-integration** |
| **tray-expert** | Script code patterns | **tray-script-generator** |
| **tray-expert** | Error handling patterns | **tray-errors** |
| **tray-expert** | Workflow diagrams | **tray-diagrams** |
| **tray-script-generator** | Tray connector operations | **tray-expert** |
| **tray-script-generator** | Salesforce Composite API | **salesforce-composite** |
| **tray-script-generator** | CSV output formatting | **csv-output** |

## Ohanafy SKU Handoffs

| From | Trigger | Route To |
|------|---------|----------|
| **ohfy-core-expert** | Order-specific logic | **ohfy-oms-expert** |
| **ohfy-core-expert** | Warehouse operations | **ohfy-wms-expert** |
| **ohfy-core-expert** | Payment processing | **ohfy-payments-expert** |
| **ohfy-core-expert** | EDI interchange | **ohfy-edi-expert** |
| **ohfy-core-expert** | Object/field schema details | **ohfy-data-model-expert** |
| **ohfy-oms-expert** | Core trigger/service patterns | **ohfy-core-expert** |
| **ohfy-oms-expert** | Warehouse fulfillment | **ohfy-wms-expert** |
| **ohfy-oms-expert** | Payment settlement | **ohfy-payments-expert** |
| **ohfy-wms-expert** | Core trigger/service patterns | **ohfy-core-expert** |
| **ohfy-edi-expert** | Order creation from EDI | **ohfy-oms-expert** |
| Any **ohfy-*** | Platform services | **ohfy-platform-expert** |
| Any **ohfy-*** | System configuration | **ohfy-configure-expert** |

## UKG Handoffs

| From | Trigger | Route To |
|------|---------|----------|
| **ukg-expert** | API debugging (401/403, rate limits) | **ukg-api-debug** |
| **ukg-expert** | Field mapping to Salesforce | **ukg-field-mapper** |
| **ukg-field-mapper** | Salesforce target field questions | **ohfy-data-model-expert** |

## Cross-Domain Handoffs

| From | Trigger | Route To |
|------|---------|----------|
| Any skill | Live org debugging needed | **org-connect** |
| Any skill | Diagram/visualization needed | **sf-diagram-mermaid** |
| Any skill | PNG/SVG image output | **sf-diagram-nanobananapro** |
| Any skill | Security/credential concern | **security** |
| Any **sf-*** | Ohanafy-specific object behavior | Check **ohfy-core-expert** first |
| Any **tray-*** | Salesforce API patterns | Check **salesforce-composite** first |

## How to Use This Matrix

1. When a skill encounters work outside its scope, check this matrix
2. The "From" column is the skill currently active
3. The "Trigger" column describes what the skill encountered
4. The "Route To" column is the skill that should handle it
5. If no match exists, check the skill's own "Delegate Elsewhere" section
6. If still no match, ask the user which skill to use
