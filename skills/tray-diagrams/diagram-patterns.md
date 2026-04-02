# Mermaid Diagram Patterns for Tray Workflows

**Purpose**: Standards for generating Mermaid diagrams to visualize Tray.io workflows
**Audience**: Developers creating visual documentation for Tray projects
**Related**: `@tray-architecture.md` - Project structure standards

---

## Overview

Tray.io workflows are documented using Mermaid diagrams that follow consistent patterns for flow direction, arrow styles, and node representation. These patterns ensure diagrams are readable and accurately represent workflow behavior.

---

## Flow Direction Standards

### Vertical Flow (Main Workflows)

**Rule**: Main workflow logic flows **vertically** (top-down)

**Why**: Top-down flow matches natural reading order and makes sequential steps easy to follow

**Example**:
```mermaid
graph TD
    A[Trigger: Webhook] --> B[Script: Validate Input]
    B --> C[Salesforce: Query Records]
    C --> D[Script: Transform Data]
    D --> E[Salesforce: Upsert Records]
    E --> F[Email: Send Notification]
```

**Use Cases**:
- Linear workflow steps
- Sequential data processing
- Main execution paths
- Trigger → Process → Output flows

---

### Horizontal Extension (Callable Workflows)

**Rule**: Callable workflows extend **horizontally** from main flow

**Why**: Horizontal branching visually distinguishes sub-workflows from main sequence

**Example**:
```mermaid
graph TD
    A[Main Workflow] --> B[Process Records]
    B --> C[Complete]

    B -.-> D[Callable: Error Handler]
    D -.-> E[Log Error]
    E -.-> F[Send Alert]
```

**Use Cases**:
- Fire-and-forget sub-workflows
- Error handling branches
- Utility workflows called from main flow
- Parallel processing branches

---

## Arrow Style Standards

### Fire and Forget (Dotted Arrows)

**Syntax**: `-.->` (dotted arrow)

**Meaning**: Workflow triggers callable workflow and continues without waiting for response

**Example**:
```mermaid
graph TD
    A[Main Process] --> B[Save to Database]
    B -.-> C[Fire-and-Forget: Send Notification]
    B --> D[Continue Main Flow]

    C -.-> E[Email Service]
```

**Use Cases**:
- Logging workflows
- Notification triggers
- Async background tasks
- Non-blocking operations

---

### Fire and Wait for Response (Bi-directional Dotted Arrows)

**Syntax**: `-.->` followed by `-.->` return path

**Meaning**: Workflow calls sub-workflow and waits for response before continuing

**Example**:
```mermaid
graph TD
    A[Main Workflow] --> B[Prepare Data]
    B -.-> C[Callable: Validate Rules]
    C -.-> D[Return Validation Result]
    D -.-> B
    B --> E[Process Valid Records]
```

**Use Cases**:
- Validation workflows that return results
- Synchronous API calls to other workflows
- Decision-making sub-workflows
- Data enrichment operations

---

### Standard Flow (Solid Arrows)

**Syntax**: `-->` (solid arrow)

**Meaning**: Sequential step-by-step execution within same workflow

**Example**:
```mermaid
graph TD
    A[Trigger] --> B[Step 1]
    B --> C[Step 2]
    C --> D[Step 3]
```

**Use Cases**:
- All sequential steps in main workflow
- Linear data transformations
- Standard execution flow

---

## Node Naming Conventions

### Node Format

**Pattern**: `[Component Type: Action Description]`

**Examples**:
- `[Trigger: Webhook]`
- `[Script: Transform Data]`
- `[Salesforce: Upsert Records]`
- `[Callable: Error Handler]`
- `[Email: Send Notification]`

### Component Types

| Type | Description | Example |
|------|-------------|---------|
| `Trigger` | Workflow initiator | `[Trigger: Scheduled Daily]` |
| `Script` | Script connector step | `[Script: Process Orders]` |
| `Salesforce` | Salesforce connector | `[Salesforce: Query Accounts]` |
| `Callable` | Callable workflow | `[Callable: Bulk Upsert]` |
| `Email` | Email connector | `[Email: Send Alert]` |
| `HTTP` | HTTP request | `[HTTP: Call External API]` |
| `Conditional` | Branch logic | `[Conditional: Check Status]` |

---

## Complete Workflow Example

### Scenario: Order Processing with Error Handling

```mermaid
graph TD
    %% Main vertical flow
    A[Trigger: Webhook - New Order] --> B[Script: Validate Order Data]
    B --> C{Conditional: Is Valid?}

    %% Valid path
    C -->|Yes| D[Salesforce: Query Product Catalog]
    D --> E[Script: Calculate Order Total]
    E --> F[Salesforce: Upsert Order Record]
    F --> G[Complete]

    %% Invalid path - fire and forget
    C -->|No| H[Script: Format Error Message]
    H -.-> I[Callable: Error Logger]
    I -.-> J[Email: Send Alert]
    H --> K[Return Error Response]

    %% Success notification - fire and forget
    G -.-> L[Callable: Send Confirmation]
    L -.-> M[Email: Order Confirmation]
```

**Flow Explanation**:
- **Vertical main flow**: Trigger → Validation → Query → Calculate → Upsert → Complete
- **Horizontal error branch**: Invalid orders trigger error logger (fire-and-forget)
- **Success notification**: Completed orders trigger confirmation email (fire-and-forget)

---

## Cursor Integration Patterns

When generating diagrams with Cursor AI, follow these patterns:

### Pattern 1: Main Workflow Diagram

**Purpose**: High-level overview of entire workflow

```markdown
Create a Mermaid diagram for this workflow:
- Main flow: vertical (top-down)
- Include all major steps
- Show conditional branches
- Use solid arrows for sequential steps
```

### Pattern 2: Detailed Script Flow

**Purpose**: Zoom into specific script logic

```markdown
Create a detailed Mermaid diagram for the script:
- Show internal function calls
- Indicate data transformations
- Use horizontal branches for helper functions
```

### Pattern 3: Error Handling View

**Purpose**: Document error paths and retry logic

```markdown
Create error handling diagram:
- Show normal path (solid arrows)
- Show error paths (dotted arrows for fire-and-forget)
- Include retry logic
- Document fallback workflows
```

---

## Best Practices

### 1. Keep Diagrams Focused

**Good**: One diagram per workflow or major component
```mermaid
graph TD
    A[Trigger] --> B[Process]
    B --> C[Complete]
```

**Avoid**: Cramming entire integration into one diagram
```mermaid
graph TD
    A[...] --> B[...] --> C[...] --> D[...] --> E[...]
    E --> F[...] --> G[...] --> H[...] --> I[...]
    I --> J[...] --> K[...] --> L[...] --> M[...]
```

### 2. Use Descriptive Node Labels

**Good**: `[Script: Transform Order Data]`
**Avoid**: `[Script 1]` or `[Transform]`

### 3. Consistent Arrow Styles

**Good**: Always use `-.->` for fire-and-forget
**Avoid**: Mixing arrow styles without clear meaning

### 4. Logical Grouping

Group related steps visually:
```mermaid
graph TD
    subgraph "Data Validation"
        A[Check Required Fields]
        B[Validate Data Types]
        C[Check Business Rules]
    end

    subgraph "Salesforce Operations"
        D[Query Records]
        E[Upsert Data]
        F[Update Related]
    end

    A --> B --> C --> D --> E --> F
```

---

## Diagram Storage Locations

### Project-Level Diagrams

**Location**: `versions/current/diagrams/`

**Files**:
- `project-overview.json` - High-level architecture
- `workflow-details/[workflow-name]-diagram.json` - Individual workflow diagrams

**Format**: JSON export from Tray.io or manually created Mermaid

### Documentation Diagrams

**Location**: `versions/current/documentation/`

**Embedded in**:
- `README.md` - Project overview diagrams
- `API.md` - API flow diagrams
- `CHANGELOG.md` - Change impact diagrams (if applicable)

---

## Generating Diagrams

### Manual Creation

```markdown
1. Identify workflow steps from Tray.io canvas
2. Map to Mermaid syntax following patterns above
3. Validate diagram renders correctly
4. Save to appropriate location
5. Reference in documentation
```

### Automated Generation (Future)

```bash
# Planned: Extract from Tray export and generate Mermaid
node scripts/generate-diagrams.js <workflow-export.json>
```

---

## See Also

- `@tray-architecture.md` - Project structure and hierarchy
- `@../CLAUDE.md` - Main Tray.io development guide
- Mermaid Documentation: https://mermaid.js.org/
- Tray.io Workflow Documentation: https://tray.io/docs
