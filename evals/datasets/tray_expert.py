"""Eval dataset for the tray-expert skill.

Cases organized by the 3 operating modes: Q&A, Build, Review.
Each case has a pre-recorded output that the scorer evaluates against expectations.
"""

EVAL_CASES = [
    # --- Mode A: Q&A ---
    {
        "name": "qa_rbac_roles",
        "description": "Q&A about Tray.io RBAC roles and permissions",
        "tags": ["qa", "rbac", "admin"],
        "input": {
            "mode": "qa",
            "question": "What RBAC roles does Tray.io support and what can each do?",
        },
        "expected": {
            "key_terms": ["owner", "admin", "member", "permissions", "workspace"],
        },
        "recorded_output": {
            "answer": "Tray.io supports 3 RBAC roles within a workspace:\n\n| Role | Permissions |\n|------|------------|\n| **Owner** | Full control: manage billing, workspace settings, users, all projects. One owner per workspace. |\n| **Admin** | Manage users, create/edit/delete projects and workflows, configure connectors and authentications. Cannot change billing or workspace-level settings. |\n| **Member** | Create and edit own projects and workflows, use shared authentications. Cannot manage other users or workspace settings. |\n\nRoles are assigned at the workspace level. A user can have different roles in different workspaces. Admins can promote members but cannot change owner. The owner role is transferable only by the current owner.",
            "source": "tray-expert-guide.md, Section 5: User Management & RBAC",
        },
    },
    {
        "name": "qa_data_storage",
        "description": "Q&A about Tray.io Data Storage service and scope levels",
        "tags": ["qa", "data-storage", "platform"],
        "input": {
            "mode": "qa",
            "question": "How does Data Storage work in Tray.io? What are the scope levels?",
        },
        "expected": {
            "key_terms": ["workflow", "project", "account", "key-value", "scope"],
        },
        "recorded_output": {
            "answer": "Tray.io Data Storage is a built-in key-value store for persisting state between workflow runs. It supports 3 scope levels:\n\n1. **Workflow scope** (most restrictive): Data is isolated to a single workflow. Best for watermarks, last-run timestamps, and per-workflow counters. Use `$.data_storage.workflow` to access.\n\n2. **Project scope**: Data shared across all workflows within a project. Good for shared configuration and lookup tables. Use `$.data_storage.project` to access.\n\n3. **Account scope** (broadest): Data shared across all projects in the workspace/account. Use sparingly — appropriate for global configuration. Use `$.data_storage.account` to access.\n\n**Limits**: Max 256 KB per key, 10,000 keys per scope level. Keys are strings, values are JSON-serializable. Operations: get, set, delete, list. All operations are atomic.\n\n**Best practice**: Use Workflow scope for watermarks (survives re-deploys), Project scope for shared lookups, avoid Account scope unless truly global.",
            "source": "tray-expert-guide.md, Section 8: Data Storage",
        },
    },
    {
        "name": "qa_trigger_types",
        "description": "Q&A about Tray.io trigger types and when to use each",
        "tags": ["qa", "triggers", "architecture"],
        "input": {
            "mode": "qa",
            "question": "What trigger types are available in Tray.io and when should I use each?",
        },
        "expected": {
            "key_terms": ["scheduled", "webhook", "callable", "service", "polling", "cron", "interval"],
        },
        "recorded_output": {
            "answer": "Tray.io offers 4 trigger types:\n\n| Trigger | When to Use | Configuration |\n|---------|------------|---------------|\n| **Scheduled (Interval)** | Polling every N minutes/hours. Best for: checking for new records, delta sync with watermarks. Minimum interval: 5 minutes. | Set interval duration. |\n| **Scheduled (Cron)** | Specific times (daily at 2am, Mon-Fri at 8am). Best for: batch reports, EOD processing. | Cron expression + timezone. |\n| **Webhook** | Real-time event-driven. Best for: incoming API calls, external system notifications. | URL + optional CSRF token. |\n| **Service Trigger** | Connector-native events (e.g., Salesforce Platform Event, Slack message). Best for: real-time when the service supports push. | Connector-specific config. |\n| **Callable** | Invoked by another workflow. Best for: shared sub-workflows, modular architecture. | Input/output schema. |\n\n**Decision matrix**: Real-time + push support → Service Trigger. Real-time + no push → Webhook. Periodic check → Scheduled (Interval). Fixed schedule → Scheduled (Cron). Sub-workflow → Callable.\n\n**Task credits**: Scheduled triggers consume 1 task per execution. Webhooks consume 1 task per incoming request. Callable triggers consume 0 tasks (charged to the calling workflow).",
            "source": "tray-expert-guide.md, Section 10: Triggers",
        },
    },
    # --- Mode B: Build ---
    {
        "name": "build_sf_shopify_sync",
        "description": "Design a polling workflow for Salesforce-to-Shopify product sync",
        "tags": ["build", "salesforce", "shopify", "sync"],
        "input": {
            "mode": "build",
            "requirements": "Sync products from Salesforce to Shopify every 30 minutes. ~500 products. Only sync changed records.",
        },
        "expected": {
            "min_best_practices": 5,
        },
        "recorded_output": {
            "design": {
                "name": "SF-to-Shopify Product Sync",
                "trigger_type": "Scheduled (Interval) — 30 minutes",
                "steps": [
                    {"step": 1, "connector": "Data Storage", "operation": "Get watermark", "detail": "Retrieve last sync timestamp from Workflow scope"},
                    {"step": 2, "connector": "Salesforce", "operation": "SOQL Query", "detail": "SELECT Id, Name, ProductCode, ... FROM Product2 WHERE LastModifiedDate > :watermark"},
                    {"step": 3, "connector": "Script", "operation": "Transform", "detail": "Map SF fields to Shopify product schema, build lookup map by ProductCode"},
                    {"step": 4, "connector": "Loop", "operation": "Batch", "detail": "Process products in batches of 50 (Shopify API limit)"},
                    {"step": 5, "connector": "Shopify", "operation": "Upsert Product", "detail": "Create/update product by SKU (idempotent)"},
                    {"step": 6, "connector": "Data Storage", "operation": "Set watermark", "detail": "Update last sync timestamp to current time"},
                    {"step": 7, "connector": "Callable Workflow", "operation": "Alert on failure", "detail": "Trigger alerting workflow if errors > threshold"},
                ],
                "error_handling": "Manual error handler on steps 2, 4, 5. On transient failure (429, 5xx), retry with exponential backoff. On permanent failure, log to error array and continue. Alert workflow sends to #ops-alerts Slack channel.",
                "data_flow": "delta",
                "estimated_task_credits": "48 tasks/day (every 30 min = 48 executions)",
            },
            "best_practices_checked": [
                "credentials",
                "batch",
                "pagination",
                "watermark",
                "error_handling",
                "alerting",
                "staggered",
                "task_credit",
            ],
        },
    },
    {
        "name": "build_webhook_ingest",
        "description": "Design an event-driven webhook ingestion workflow",
        "tags": ["build", "webhook", "event-driven"],
        "input": {
            "mode": "build",
            "requirements": "Receive webhook events from a 3PL system, validate HMAC signature, transform payload, upsert to Salesforce.",
        },
        "expected": {
            "min_best_practices": 4,
        },
        "recorded_output": {
            "design": {
                "name": "3PL Webhook Ingest",
                "trigger_type": "Webhook — HMAC-SHA256 validated",
                "steps": [
                    {"step": 1, "connector": "Script", "operation": "Validate HMAC", "detail": "Verify X-Signature header using shared secret from Tray credential store"},
                    {"step": 2, "connector": "Script", "operation": "Parse & Validate", "detail": "Extract event type, validate required fields, reject malformed payloads"},
                    {"step": 3, "connector": "Boolean", "operation": "Route by event type", "detail": "Branch: shipment_created, shipment_updated, inventory_adjusted"},
                    {"step": 4, "connector": "Script", "operation": "Transform", "detail": "Map 3PL fields to Salesforce schema with namespace handling"},
                    {"step": 5, "connector": "Salesforce", "operation": "Composite Upsert", "detail": "Upsert records using External_ID__c (idempotent)"},
                    {"step": 6, "connector": "Script", "operation": "Build response", "detail": "Return 200 with processing summary or 4xx with error details"},
                ],
                "error_handling": "HMAC failure returns 401 immediately. Validation failure returns 400 with details. SF upsert failure triggers alert workflow and returns 500. All errors logged to sync audit object.",
            },
            "best_practices_checked": [
                "credentials",
                "error_handling",
                "alerting",
                "concurrency",
                "data_storage",
            ],
        },
    },
    # --- Mode C: Review ---
    {
        "name": "review_weak_integration",
        "description": "Review a workflow design with known security and data integrity gaps",
        "tags": ["review", "audit", "security"],
        "input": {
            "mode": "review",
            "design_summary": "Full-load sync every 5 min, no watermark, hardcoded API key in script step, no error handling, no alerting, no batch operations (individual record updates).",
        },
        "expected": {
            "min_issues": 4,
            "score_range": [2, 5],
        },
        "recorded_output": {
            "scores": {
                "authentication_security": 2,
                "data_integrity": 2,
                "workflow_architecture": 3,
                "performance_cost": 2,
                "environment_deployment": 4,
                "salesforce_specific": 3,
            },
            "overall_score": 2.7,
            "risk_level": "High",
            "issues": [
                {"severity": "critical", "dimension": "authentication_security", "detail": "Hardcoded API key in script step — must use Tray credential store with $.auth"},
                {"severity": "critical", "dimension": "data_integrity", "detail": "Full-load sync every 5 minutes with no watermark — massive waste of API calls and task credits"},
                {"severity": "critical", "dimension": "data_integrity", "detail": "No error handling on any connector steps — silent failures will cause data loss"},
                {"severity": "high", "dimension": "performance_cost", "detail": "Individual record updates instead of batch — 500x more API calls than necessary"},
                {"severity": "high", "dimension": "workflow_architecture", "detail": "No alerting workflow — production failures go unnoticed"},
                {"severity": "medium", "dimension": "workflow_architecture", "detail": "No concurrency protection — overlapping runs could cause duplicate processing"},
            ],
            "recommendations": [
                "Move API key to Tray credential store and reference via $.auth",
                "Implement delta sync with Data Storage watermark (Workflow scope)",
                "Add manual error handler on all Salesforce and external API steps",
                "Use Salesforce Composite API or Bulk API for batch operations",
                "Create alerting sub-workflow that posts to Slack #ops-alerts",
                "Add skip-if-running check at workflow start",
            ],
        },
    },
    {
        "name": "review_strong_integration",
        "description": "Review a well-designed workflow that follows best practices",
        "tags": ["review", "audit", "passing"],
        "input": {
            "mode": "review",
            "design_summary": "Delta sync with watermarks, $.auth for all credentials, batch composite upserts, error handling on all steps, alerting workflow, skip-if-running, staggered scheduling.",
        },
        "expected": {
            "min_issues": 0,
            "score_range": [7, 10],
        },
        "recorded_output": {
            "scores": {
                "authentication_security": 9,
                "data_integrity": 9,
                "workflow_architecture": 8,
                "performance_cost": 8,
                "environment_deployment": 7,
                "salesforce_specific": 8,
            },
            "overall_score": 8.2,
            "risk_level": "Low",
            "issues": [
                {"severity": "low", "dimension": "environment_deployment", "detail": "Environment promotion path not documented — recommend adding dev/staging/prod notes"},
            ],
            "recommendations": [
                "Document environment promotion path for team onboarding",
                "Consider adding sync audit logging to Salesforce custom object for compliance",
            ],
        },
    },
]
