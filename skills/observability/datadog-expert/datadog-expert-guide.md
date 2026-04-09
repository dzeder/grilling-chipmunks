# Datadog Expert Guide — Ohanafy

Comprehensive knowledge base for Datadog operations at Ohanafy. This guide covers architecture, best practices, Terraform patterns, and integration setup for Ohanafy's full stack (AWS + Salesforce + Tray.ai).

---

## 1. Ohanafy DD Architecture

### Infrastructure Overview

Ohanafy manages all Datadog resources as Infrastructure-as-Code via the `DatadogTerraform` repository (HCL/Terraform). No manual dashboard or monitor creation — everything goes through Terraform.

**Key components:**

| Component | Repo | Stack | Purpose |
|-----------|------|-------|---------|
| Monitoring IaC | DatadogTerraform | HCL, Terraform | Dashboards, monitors, SLOs, log pipelines, synthetic tests |
| Log ingestion | LogIngestion | Kotlin | Collects, transforms, and routes logs to Datadog |
| Lambda tracing | Per-function | Python (datadog-lambda-python + aws-powertools) | APM traces from serverless functions |
| Tray webhooks | Tray.ai platform | JSON/REST | Workflow execution events forwarded to DD |

### Tag Taxonomy

All DD resources MUST use these standard tags:

| Tag | Values | Purpose |
|-----|--------|---------|
| `env` | `prod`, `staging`, `dev`, `sandbox` | Environment isolation |
| `service` | `oms`, `wms`, `rex`, `edi`, `ecom`, `payments`, `configure`, `platform` | Ohanafy product module |
| `team` | `engineering`, `ops`, `support` | Ownership routing |
| `sku` | `starter`, `professional`, `enterprise` | Customer tier |
| `customer` | Customer slug (e.g., `shipyard`) | Per-customer isolation (use sparingly) |

### Environments

| Environment | DD Org | Purpose |
|-------------|--------|---------|
| Production | Primary org | Live customer monitoring |
| Staging | Same org, `env:staging` tag | Pre-release validation |
| Development | Same org, `env:dev` tag | Developer testing |

---

## 2. Dashboard Best Practices

### Beverage Supply Chain Dashboards

Ohanafy's core business is beverage supply chain. Dashboards should reflect the order lifecycle:

**Order Flow Dashboard** — Track from order creation to fulfillment:
- Order creation rate (orders/min by channel: EDI, ecom, manual)
- Order processing latency (p50, p95, p99)
- Fulfillment rate (% shipped within SLA)
- Error rate by stage (validation, allocation, pick/pack, ship)

**Inventory Dashboard** — Real-time stock visibility:
- Stock levels by warehouse and SKU category
- Reorder point alerts (approaching minimum threshold)
- Allocation conflicts (over-committed inventory)
- Receiving pipeline (expected vs. actual receipts)

**EDI Processing Dashboard** — Electronic data interchange health:
- EDI file receipt rate (files/hour by trading partner)
- Parse success/failure rate
- Transform latency (file received → SF records created)
- Acknowledgment turnaround (997/999 response time)

**Tray Workflow Health Dashboard** — Integration pipeline monitoring:
- Workflow execution rate and success/failure
- Step-level latency heatmap
- Connector error breakdown (Salesforce, Slack, AWS, etc.)
- Queue depth for batch operations

**Salesforce API Dashboard** — SF org health:
- API call consumption (% of daily limit)
- Bulk API job status and duration
- Event bus throughput (Platform Events, Change Data Capture)
- Governor limit proximity alerts

### Dashboard Design Rules

1. **One dashboard per concern** — Don't mix order flow with infrastructure
2. **Top-down layout** — Summary KPIs at top, drill-down details below
3. **Consistent time ranges** — Default to last 4 hours for operational, last 7 days for trends
4. **Template variables** — Always add `env`, `service`, and `customer` template vars
5. **Annotations** — Mark deployments, incidents, and maintenance windows

---

## 3. Monitor Types & When to Use

| Monitor Type | Use When | Example |
|-------------|----------|---------|
| Metric | Threshold on a numeric metric | CPU > 80% for 5 min |
| Log | Pattern in log messages | `ERROR.*OutOfStock` in OMS logs |
| APM | Trace latency or error rate | p99 latency > 2s on order-create endpoint |
| Composite | Multiple conditions must be true | High latency AND high error rate |
| SLO Alert | SLO burn rate too fast | 99.9% availability SLO burning 10x |
| Anomaly | Deviation from baseline | Order volume 3 std dev below normal |
| Forecast | Metric will breach threshold | Disk space will fill in 48h |
| Process | Host process not running | LogIngestion service not running |
| Network | Connectivity issue | Lambda → RDS connection failures |
| Event | DD event matches condition | Deployment event followed by error spike |

### Monitor Priority Guidelines

| Priority | Response Time | Example Scenarios |
|----------|---------------|-------------------|
| P1 (Critical) | 5 min | Production order processing stopped, data loss risk |
| P2 (High) | 30 min | Degraded performance, EDI files backing up |
| P3 (Medium) | 4 hours | Non-critical service degraded, staging issues |
| P4 (Low) | Next business day | Informational, trend warnings |

### Alert Routing

| Priority | Channel | Escalation |
|----------|---------|------------|
| P1 | PagerDuty + Slack #incidents | Auto-escalate after 10 min |
| P2 | Slack #alerts + PagerDuty (low urgency) | Escalate after 1 hour |
| P3 | Slack #monitoring | Review in daily standup |
| P4 | Slack #monitoring (low noise) | Review weekly |

---

## 4. Terraform Patterns for DD Resources

### Dashboard Module

```hcl
resource "datadog_dashboard" "example" {
  title       = "[${var.env}] ${var.service} - ${var.dashboard_name}"
  description = var.description
  layout_type = "ordered"

  template_variable {
    name    = "env"
    prefix  = "env"
    default = var.env
  }

  template_variable {
    name    = "service"
    prefix  = "service"
    default = var.service
  }

  # Widget groups follow top-down pattern:
  # 1. Summary KPIs (query_value widgets)
  # 2. Time series trends
  # 3. Detail tables / top lists
}
```

### Monitor Module

```hcl
resource "datadog_monitor" "example" {
  name    = "[${var.env}] ${var.service} - ${var.monitor_name}"
  type    = var.monitor_type  # "metric alert", "log alert", "trace-analytics alert", etc.
  message = <<-EOT
    ${var.alert_message}

    {{#is_alert}}
    @slack-${var.alert_channel} @pagerduty-${var.pagerduty_service}
    {{/is_alert}}

    {{#is_warning}}
    @slack-${var.warning_channel}
    {{/is_warning}}

    {{#is_recovery}}
    @slack-${var.recovery_channel}
    {{/is_recovery}}
  EOT

  query = var.query

  monitor_thresholds {
    critical = var.critical_threshold
    warning  = var.warning_threshold
  }

  tags = concat(
    ["env:${var.env}", "service:${var.service}", "team:${var.team}"],
    var.extra_tags
  )

  notify_no_data    = var.notify_no_data
  no_data_timeframe = var.no_data_timeframe
  renotify_interval = var.renotify_interval
}
```

### SLO Module

```hcl
resource "datadog_service_level_objective" "example" {
  name        = "[${var.env}] ${var.service} - ${var.slo_name}"
  type        = "metric"  # or "monitor"
  description = var.description

  query {
    numerator   = var.good_events_query
    denominator = var.total_events_query
  }

  thresholds {
    timeframe = "7d"
    target    = var.target_7d   # e.g., 99.9
    warning   = var.warning_7d  # e.g., 99.95
  }

  thresholds {
    timeframe = "30d"
    target    = var.target_30d
    warning   = var.warning_30d
  }

  tags = ["env:${var.env}", "service:${var.service}", "team:${var.team}"]
}
```

---

## 5. Integration Setup by Stack Layer

### AWS Integration

**Lambda Monitoring:**
- Install `datadog-lambda-python` in each function's requirements
- Add DD Lambda layer for trace collection
- Set environment variables: `DD_SERVICE`, `DD_ENV`, `DD_VERSION`, `DD_TRACE_ENABLED=true`
- Use `@datadog_lambda_wrapper` decorator on handler functions
- Correlate with aws-powertools structured logging

**API Gateway:**
- Enable DD AWS integration for API GW metrics
- Custom metrics for per-route latency and error rates
- Log forwarding via DD Forwarder Lambda

**RDS:**
- Enable DD Database Monitoring for query-level insights
- Track connection pool utilization
- Slow query alerts (> 1s for OLTP, > 30s for batch)

### Salesforce Integration

**Event Monitoring:**
- Forward SF Event Monitoring logs to DD via LogIngestion pipeline
- Track API usage against daily limits
- Monitor login events for security anomalies

**Bulk API Jobs:**
- Log job creation, status, and completion events
- Alert on failed bulk jobs (especially data loads)
- Track batch processing throughput

**Governor Limits:**
- Aggregate limit consumption metrics from Apex debug logs
- Alert when any limit exceeds 80% of max

### Tray.ai Integration

**Workflow Monitoring:**
- Forward Tray execution events to DD via webhook
- Track execution count, duration, and status per workflow
- Alert on consecutive failures (> 3 in a row)
- Monitor connector-specific errors (SF auth expiry, Slack rate limits)

**Webhook Health:**
- Monitor webhook delivery latency
- Validate HMAC signatures (security requirement)
- Track retry rates and dead letter queue depth

---

## 6. MCP Server Integration

### shelfio/datadog-mcp (Community)

Open-source MCP server that exposes DD API to Claude Code:
- Query metrics and dashboards
- List and manage monitors
- Check SLO status
- View service catalog
- Browse incidents

**Setup:** Add to `.claude/settings.json` MCP configuration with DD API key and APP key from AWS Secrets Manager.

### Datadog Official MCP Server

Hosted MCP service at docs.datadoghq.com/bits_ai/mcp_server/:
- Officially supported by Datadog
- Integrated with Bits AI assistant
- Covers logs, APM, infrastructure, security

**Note:** Check current availability — the official MCP server may require specific DD plan tier.

---

## 7. Common DD Queries for Ohanafy

### Order Processing Health
```
avg:ohanafy.orders.processing_time{env:prod,service:oms} by {order_type}
```

### EDI File Backlog
```
sum:ohanafy.edi.pending_files{env:prod,service:edi} by {trading_partner}
```

### Lambda Cold Start Rate
```
sum:aws.lambda.enhanced.init_duration{env:prod,service:oms}.as_count() / sum:aws.lambda.invocations{env:prod,service:oms}.as_count() * 100
```

### SF API Limit Consumption
```
max:ohanafy.salesforce.api_calls_remaining{env:prod} / max:ohanafy.salesforce.api_calls_limit{env:prod} * 100
```

### Tray Workflow Failure Rate
```
sum:ohanafy.tray.workflow.failures{env:prod}.as_count() / sum:ohanafy.tray.workflow.executions{env:prod}.as_count() * 100
```

---

## 8. Incident Response with DD

### Triage Checklist

1. **Check the dashboard** — Is the issue visible in the relevant service dashboard?
2. **Review recent changes** — Any deployments in the last 2 hours? (DD deployment events)
3. **Correlate signals** — Are multiple monitors firing? Check composite view
4. **Check dependencies** — Is the issue in our service or a downstream dependency?
5. **Review logs** — Filter by `service` and `env` tags, look for error patterns
6. **Check traces** — Find the slow/failing trace and identify the bottleneck span

### Post-Incident

- Update monitors if the alert was missing or misconfigured
- Add missing dashboards for gaps discovered during triage
- Update SLOs if targets were unrealistic
- Document in incident timeline (DD Incident Management or Ozone SF org)
