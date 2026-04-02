# Tray.ai Project JSON Structure Guide for LLM Analysis

## Overview

This document provides a comprehensive guide for Large Language Models (LLMs) to deeply understand and analyze Tray.ai project JSON exports. Tray.ai is an integration platform as a service (iPaaS) that allows users to create complex automation workflows between various applications and services.

## High-Level Project Structure

Every Tray.ai project JSON export follows this top-level structure:

```json
{
  "tray_export_version": 4,
  "export_type": "project", 
  "workflows": [...],
  "solution": {...}
}
```

### Core Components

1. **`tray_export_version`**: Integer indicating the export format version (currently 4)
2. **`export_type`**: String, always "project" for project exports
3. **`workflows`**: Array of workflow objects that contain the actual automation logic
4. **`solution`** (optional): Embedded solution configuration for packaged deployments

---

## Workflow Structure

### Workflow Object Schema

```json
{
  "id": "uuid",
  "created": "ISO8601-timestamp",
  "workspace_id": "uuid", 
  "project_id": "uuid",
  "group": "uuid",
  "creator": "uuid",
  "version": {
    "id": "uuid",
    "created": "ISO8601-timestamp"
  },
  "title": "Human readable workflow name",
  "enabled": boolean,
  "tags": ["array", "of", "strings"],
  "settings": {
    "config": {...},
    "input_schema": {...},
    "output_schema": {...}
  },
  "steps_structure": [...],
  "steps": {...}
}
```

### Key Workflow Properties

- **`id`**: Unique identifier for the workflow
- **`title`**: Human-readable name describing the workflow's purpose
- **`enabled`**: Boolean indicating if the workflow is active
- **`version`**: Current active version of the workflow and all its components
- **`settings.config`**: Project-level configuration variables and parameters
- **`steps_structure`**: Hierarchical representation of workflow execution flow
- **`steps`**: Detailed configuration for each step/connector in the workflow

---

## Steps Structure Analysis

The `steps_structure` array defines the execution flow and control logic:

### Step Types

1. **`normal`**: Standard connector step (API calls, transformations, etc.)
2. **`loop`**: Iteration over arrays/collections 
3. **`branch`**: Conditional logic (if/else)
4. **`break`**: Flow control to exit loops
5. **`trigger`**: Workflow entry point

### Flow Control Patterns

```json
{
  "name": "loop-1",
  "type": "loop", 
  "content": {
    "_loop": [
      {
        "name": "salesforce-1",
        "type": "normal",
        "content": {}
      },
      {
        "name": "boolean-condition-1", 
        "type": "branch",
        "content": {
          "true": [{"name": "break-loop-1", "type": "break"}],
          "false": []
        }
      }
    ]
  }
}
```

### Common Flow Patterns to Recognize

- **Data Processing Loops**: `loop` → `connector` → `condition` → `break/continue`
- **Error Handling**: `branch` conditions checking API responses
- **Batch Processing**: Nested loops for handling large datasets
- **Parallel Processing**: Multiple branches with independent logic paths

---

## Steps Configuration Deep Dive

The `steps` object contains detailed configuration for each named step from `steps_structure`:

### Universal Step Properties

```json
{
  "step-name": {
    "title": "Human readable step name",
    "connector": {
      "name": "connector-type",
      "version": "semantic-version"
    },
    "operation": "specific-operation-name",
    "output_schema": {...},
    "error_handling": {...},
    "properties": {...}
  }
}
```

### Connector Types and Operations

#### 1. **Script Connector** (`name: "script"`)
- **Purpose**: Custom JavaScript/Python code execution
- **Key Properties**:
  - `variables`: Array of input variables with JSONPath references
  - `script`: String containing the actual code
  - `file_output`: Boolean for file generation capability

**Example Script Structure**:
```javascript
exports.step = function(input, fileInput) {
  // Access input variables: input.variableName
  // fileInput parameter exists but is not commonly used
  // Custom business logic here
  return result;
};
```

#### 2. **Boolean Condition** (`name: "boolean-condition"`)
- **Purpose**: Conditional logic and decision making
- **Key Properties**:
  - `conditions`: Array of comparison objects
  - `strictness`: "All" (AND) or "Any" (OR) logic

#### 3. **Loop Connector** (`name: "loop"`)
- **Purpose**: Iteration over arrays and collections
- **Key Properties**:
  - `array`: JSONPath to the array to iterate
  - `concurrent`: Boolean for parallel processing

#### 4. **API Connectors** (Salesforce, QuickBooks, etc.)
- **Purpose**: Integration with external services
- **Key Properties**:
  - `operation`: Specific API operation (create, update, query, etc.)
  - **Authentication**: Handled separately by Tray platform (not visible in project JSON)
  - Request/response mapping via JSONPath

#### 5. **Storage Connector** (`name: "storage"`)
- **Purpose**: Temporary data storage and retrieval
- **Operations**: `set`, `get`, `atomic_increment`, etc.

#### 6. **Trigger Connectors**
- **Scheduled** (`name: "scheduled"`): Cron-based time triggers
- **Webhook** (`name: "webhook"`): HTTP endpoint triggers (no special security patterns required)
- **Manual** (`name: "manual"`): User-initiated triggers via Tray UI

### JSONPath Usage Patterns

Tray.ai extensively uses JSONPath for data mapping:

- **Step References**: `$.steps.step-name.response.body.field`
- **Config References**: `$.config.configKey`
- **Loop Context**: `$.steps.loop-name.value.field`
- **Trigger Data**: `$.steps.trigger.data.field`

---

## Project Configuration Analysis

The `settings.config` object contains project-level configuration:

### Common Configuration Patterns

```json
{
  "config": {
    "dev": true,
    "testMode": true,
    "company": "CompanyCode",
    "accountUrl": "api.service.com",
    "customFields": [...],
    "queryFilters": "SOQL/API filters",
    "cronSchedule": "0 3,9,15,21 * * *",
    "limits": {
      "qboCount": 500,
      "limit": 5
    }
  }
}
```

### Configuration Categories

1. **Environment Settings**: `dev`, `testMode`, `testRun`
2. **Integration Parameters**: API URLs, company codes, account mappings
3. **Business Logic**: Custom fields, query filters, processing rules
4. **Performance Settings**: Batch sizes, rate limits, concurrency
5. **Scheduling**: Cron expressions, frequency settings

---

## Embedded Solution Structure

For packaged integrations, the `solution` object provides deployment configuration:

```json
{
  "solution": {
    "id": "uuid",
    "name": "Solution Name", 
    "description": "Every six hours syncs your...",
    "project_id": "uuid",
    "tags": ["admin", "quickbooks"],
    "custom_fields": {
      "image": "https://cdn.logo.svg",
      "documentation": "https://docs.url"
    },
    "view_schema": {
      "version": 6,
      "screens": [...],
      "slots": [...]
    }
  }
}
```

### Configuration Schema Components

1. **Screens**: UI configuration for user setup
2. **Slots**: Configuration parameters with types and validation
3. **Usage Tracking**: References to which workflows use which config values
4. **External IDs**: Mappings for configuration deployment

---

## Analysis Strategies for LLMs

### 1. **Identify Integration Purpose**
- Read workflow titles and descriptions
- Analyze config object for business context
- Look for API connector types to identify integrated systems

### 2. **Map Data Flow**
- Trace JSONPath references between steps
- Identify source and destination systems
- Document transformation logic in script steps

### 3. **Understand Business Logic**
- Analyze boolean conditions for decision points
- Review script steps for custom processing
- Identify error handling patterns

### 4. **Document Architecture**
- Count and categorize connectors
- Map workflow dependencies (call-workflow steps)
- Identify parallel vs sequential processing

### 5. **Extract Configuration Requirements**
- List all config object properties
- Identify required vs optional settings
- Document external system requirements

### 6. **Performance Analysis**
- Identify loops and potential bottlenecks
- Check for concurrent processing capabilities
- Review rate limiting and batch size configurations

---

## Common Integration Patterns

### 1. **Scheduled Data Sync**
```
Trigger (scheduled) → Query Source → Transform → Update Destination → Handle Errors
```

### 2. **Webhook Processing**
```
Trigger (webhook) → Validate Payload → Process Data → Multiple Destinations
```

### 3. **Batch Processing**
```
Query Data → Loop (Items) → Process Each → Conditional Logic → Error Storage
```

### 4. **Real-time Sync**
```
Trigger → Immediate Processing → Bidirectional Updates → Status Reporting
```

---

## Script Extraction and Analysis

### JavaScript Function Pattern
All Tray.ai scripts follow this pattern:
```javascript
/** 
 * @param {Input} input Value comes from the "Variables" field 
 * @param {Array.<FileInput>} fileInput Value comes from the "Files" field (rarely used)
 */
exports.step = function(input, fileInput) {
  // Access input variables: input.variableName
  // fileInput parameter exists but is typically unused
  // Process business logic
  // Return result object
  return result;
};
```

### Common Script Purposes
1. **Data Transformation**: Converting formats, calculating values
2. **Business Logic**: Custom rules and validation
3. **API Body Building**: Constructing complex API requests  
4. **Conditional Processing**: Complex decision logic
5. **Error Handling**: Custom error processing and logging

---

## Error Handling Patterns

### Standard Error Configuration
```json
{
  "error_handling": {
    "continue_on_error": true,
    "max_retries": 3,
    "retry_delay": 1000
  }
}
```

### Error Handling in Tray
- **Platform-Level**: Tray automatically handles retries and rate limiting errors
- **Workflow-Level**: Custom error handling can be configured per step
- **Common Strategies**:
  1. **Continue on Error**: Process next item if current fails
  2. **Error Storage**: Log failures to storage connector for later review
  3. **Custom Error Logic**: Use boolean conditions to handle specific error types
  4. **Graceful Termination**: Break loops or workflows when critical errors occur

---

## Testing and Validation Patterns

### Test Workflows
Test workflows in Tray projects are **standalone workflows** designed for:

1. **Connector Testing**: Testing individual API connectors and their configurations
2. **Step Pattern Validation**: Validating small sequences of steps before integrating into main workflows
3. **Data Transformation Testing**: Testing script logic and data mapping
4. **Configuration Validation**: Ensuring config parameters work correctly across environments

### Identifying Test Workflows
Look for workflows with titles containing:
- "Test" 
- "Debug"
- "Dev"
- "Validation"
- "Sandbox"

### Test Workflow Characteristics
- **Simplified Flow**: Usually linear execution without complex loops
- **Manual Triggers**: Typically use manual triggers for on-demand testing
- **Development Mode**: Often have `dev: true` or `testMode: true` in config
- **Isolated Logic**: Test specific functionality without side effects
- **Debug Output**: May include extra logging or storage steps for debugging

### Testing Strategy in Tray
- **No Native Test Framework**: Tray doesn't have automated testing capabilities
- **Manual Execution**: Tests are run using the "test run" button in Tray UI  
- **Individual Workflow Testing**: Each workflow can be tested independently
- **Environment Isolation**: Test workflows should use sandbox/dev environments

---

## Questions to Guide Analysis

When analyzing a Tray.ai project JSON, consider these questions:

### Business Context
- What business problem does this integration solve?
- Which systems are being integrated?
- What data is being synchronized?
- How frequently does synchronization occur?

### Technical Implementation
- What triggers initiate the workflows?
- How is data transformed between systems?
- What error handling strategies are employed?
- Are there performance optimization techniques used?

### Configuration Management
- What parameters can be configured by end users?
- Are there environment-specific settings (dev/prod)?
- How are API credentials and authentication handled?
- What customization options are available?

### Dependencies and Requirements
- What external systems are required?
- Are there API rate limits or quotas to consider?
- What permissions or access levels are needed?
- Are there data volume or processing time constraints?

---

## Best Practices for LLM Analysis

1. **Start with High-Level Structure**: Understand the project purpose before diving into details
2. **Follow Data Flow**: Trace data from trigger through transformation to destination  
3. **Identify Key Components**: Focus on scripts, conditions, and API connectors first
4. **Separate Production from Testing**: Distinguish between production workflows and test/debug workflows
5. **Understand Platform Capabilities**: Remember that Tray handles authentication, rate limiting, and retries automatically
6. **Document Dependencies**: Note all external system requirements and configurations
7. **Consider Scale**: Analyze for performance implications and bottlenecks
8. **Extract Business Rules**: Document the business logic embedded in conditions and scripts
9. **Map Configuration**: Understand what can be customized vs hardcoded values
10. **Version Context**: The version object represents the current active state of all workflow components

---

## Extracting Business Logic for Documentation

When creating documentation and architectural diagrams, focus on these key areas:

### 1. **Business Process Flow**
- **Entry Points**: Identify all trigger types and their purposes
- **Data Sources**: Map where data originates (which APIs, databases, files)
- **Transformations**: Document how data is modified in script steps
- **Destinations**: Identify where processed data is sent
- **Decision Points**: Map all boolean conditions and their business logic

### 2. **Configuration Dependencies** 
- **Environment Settings**: Document dev vs production configurations
- **Business Parameters**: Extract business rules from config objects
- **Integration Settings**: Document API endpoints, query filters, batch sizes
- **Customization Points**: Identify what end-users can configure

### 3. **Error Handling Strategy**
- **Failure Points**: Identify where errors are most likely to occur
- **Recovery Logic**: Document how the system handles different error types
- **Business Impact**: Understand what happens when specific steps fail
- **Monitoring**: Identify logging and storage patterns for failed operations

### 4. **Performance Characteristics**
- **Batch Processing**: Document loop patterns and batch sizes
- **Scheduling**: Extract timing information from cron expressions
- **Concurrency**: Identify parallel processing capabilities
- **Rate Limiting**: Understand throughput constraints

### 5. **Security and Compliance**
- **Data Handling**: Document sensitive data processing patterns
- **Environment Isolation**: Understand test vs production data separation
- **Audit Trail**: Identify logging and tracking mechanisms

This guide provides the foundation for deep analysis of any Tray.ai project JSON structure. Use it as a reference to understand the relationships between components and extract meaningful insights about integration architecture and business logic.