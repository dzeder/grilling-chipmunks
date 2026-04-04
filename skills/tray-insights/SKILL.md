---
name: tray-insights
description: >
  Query Tray Insights API for project usage metrics and execution analytics.
  TRIGGER when: user asks about Tray project usage data, execution KPIs,
  time-series trends, success/failure rates, task run volume, or needs
  data-driven prioritization for architecture diagrams. Automatically invoke
  when creating architecture diagrams, analyzing workflow performance,
  investigating execution issues, or prioritizing development work based on
  usage patterns.
---

# Tray Insights Skill

This skill enables Claude to query the Tray Insights API through a CLI tool to retrieve project usage metrics, execution KPIs, and time-series analytics data.

## When to Use This Skill

Automatically invoke this skill when:
- **Creating architecture diagrams** - Enrich diagrams with real usage data and prioritize high-traffic workflows
- **Analyzing workflow performance** - Investigate execution success rates, failure patterns, and throughput
- **Prioritizing development work** - Identify high-value projects based on execution volume and user activity
- **Troubleshooting** - Examine time-series data to identify execution anomalies or trends
- **Reporting** - Generate usage reports showing project activity and performance metrics

## CLI Tool Location

The Tray Insights CLI is located at:
```
04-utilities/tools/tray-insights/
```

## Available Commands

### 1. List Projects

Get metadata and usage stats for all Tray projects:

```bash
node 04-utilities/tools/tray-insights/src/index.js list-projects --json
```

**Returns:**
- Project IDs, names, and workspace associations
- Metadata for all accessible projects

**Use for:**
- Discovering project IDs for further queries
- Getting overview of all projects in workspace

### 2. Get Execution Metrics

Get KPIs (success rate, error rate, activity levels) for a specific project:

```bash
node 04-utilities/tools/tray-insights/src/index.js get-metrics <project-id> --days <number> --json
```

**Parameters:**
- `<project-id>` (required) - The project UUID
- `--days <number>` (optional) - Date range in days (default: 180)
- `--json` (optional) - Output as JSON instead of formatted text

**Returns:**
```json
{
  "data": {
    "kpis": [
      {
        "name": "Solutions",
        "value": 27,
        "percentageChange": 4
      },
      {
        "name": "Active Workflows",
        "value": 417,
        "percentageChange": -8
      },
      {
        "name": "Task Runs",
        "value": 8436844,
        "percentageChange": -23
      },
      {
        "name": "Data Volume",
        "value": 62291789546,
        "unit": "B",
        "percentageChange": -11
      }
    ]
  }
}
```

**Use for:**
- Identifying high-volume workflows for architecture diagrams
- Detecting performance degradation (negative percentageChange)
- Prioritizing optimization efforts based on task run volume

### 3. Get Time-Series Data

Get execution time-series for trend visualization:

```bash
node 04-utilities/tools/tray-insights/src/index.js get-timeseries <project-id> --interval <type> --days <number> --json
```

**Parameters:**
- `<project-id>` (required) - The project UUID
- `--interval <type>` (optional) - Time interval: hour, day, week, month (default: day)
- `--days <number>` (optional) - Date range in days (default: 180)
- `--json` (optional) - Output as JSON instead of formatted text

**Returns:**
```json
{
  "data": {
    "timeseries": [
      {
        "name": "successful",
        "id": "successful",
        "totalValue": 93090,
        "series": [
          {
            "value": ["2026-02-13T21:00:00Z", 464]
          }
        ]
      },
      {
        "name": "failed",
        "id": "failed",
        "totalValue": 541,
        "series": [
          {
            "value": ["2026-02-13T21:00:00Z", 3]
          }
        ]
      }
    ]
  }
}
```

**Use for:**
- Visualizing execution trends over time
- Identifying peak usage periods
- Detecting anomalies or sudden changes in execution patterns

## Output Interpretation

### KPI Metrics Structure

Each KPI includes:
- **name**: Metric name (Solutions, Active Workflows, Task Runs, Data Volume, etc.)
- **value**: Current value for the period
- **percentageChange**: Change vs previous period (positive = increase, negative = decrease)
- **unit**: Optional unit (e.g., "B" for bytes)

### Time-Series Structure

Each series includes:
- **name/id**: Series type (successful, failed, terminated, stopped)
- **totalValue**: Sum of all values in the period
- **series**: Array of `[timestamp, value]` pairs

## Integration with Architecture Diagrams

When creating architecture diagrams:

1. **Query project metrics** to identify high-priority workflows
2. **Annotate diagrams** with execution volume and success rates
3. **Prioritize focus areas** based on task run volume
4. **Highlight issues** where failure rates are high

Example workflow:
```bash
# Get all projects
node 04-utilities/tools/tray-insights/src/index.js list-projects --json

# Get metrics for top projects
node 04-utilities/tools/tray-insights/src/index.js get-metrics <project-id> --days 30 --json

# Analyze trends
node 04-utilities/tools/tray-insights/src/index.js get-timeseries <project-id> --interval week --days 90 --json
```

## Error Handling

The CLI includes graceful error handling:

- **401 Authentication**: "Authentication failed: Invalid or expired TRAY_INSIGHTS_TOKEN"
- **404 Not Found**: "Resource not found: ... Verify project ID and workspace access"
- **429 Rate Limit**: "Rate limit exceeded: Too many requests"
- **Network errors**: "Network error: Cannot reach Tray Insights API"

If the API is unavailable, inform the user that usage data cannot be retrieved at this time.

## Configuration

The CLI requires `TRAY_INSIGHTS_TOKEN` in the `.env` file at:
```
04-utilities/tools/tray-insights/.env
```

If not configured, the CLI will display setup instructions.

## Best Practices

1. **Always use --json flag** when invoking from Claude for easier parsing
2. **Cache results** - API responses can be saved and reused within a session to reduce API calls
3. **Filter by date range** - Use shorter date ranges (--days 30) for recent activity analysis
4. **Check for errors** - Always handle potential API failures gracefully
5. **Respect rate limits** - Avoid making rapid successive calls to the API

## Example Usage in Claude Workflow

**Scenario: Creating architecture diagram for order processing**

```bash
# Step 1: Find order processing project ID
node 04-utilities/tools/tray-insights/src/index.js list-projects --json | grep -i "order"

# Step 2: Get recent metrics (30 days)
node 04-utilities/tools/tray-insights/src/index.js get-metrics abc123-project-id --days 30 --json

# Step 3: Analyze the JSON output
# - Task Runs: 125,000 executions
# - Success Rate: 98.5%
# - Active Workflows: 12

# Step 4: Create diagram annotated with:
# "Order Processing System (125K executions/month, 98.5% success rate)"
```

This data-driven approach ensures architecture diagrams focus on the most important and heavily-used workflows.

## Delegation

Do not trigger this skill for:
- General Tray.io workflow design or Q&A -- delegate to `tray-expert`
- Generating Mermaid diagrams (after fetching data here) -- hand off to `tray-diagrams`
- Tray script generation or debugging -- delegate to `tray-script-generator` or `tray-errors`
- Salesforce-specific analytics or reporting -- delegate to `sf-data`
