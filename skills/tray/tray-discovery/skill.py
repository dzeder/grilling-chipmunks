"""
Tray.io Connector Discovery Skill

Discovers connectors from the Tray.io platform, scores their relevance
to Ohanafy, and generates structured knowledge for high-value connectors.

Pipeline: discover → score → generate knowledge → detect opportunities
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic
import yaml

from .schema import (
    ConnectorCategory,
    ConnectorKnowledge,
    CurrentUsage,
    OperationDetail,
    OpportunityType,
    RelevanceAssessment,
    RegistryEntry,
    ScoringDimension,
    TrayConnectorEntry,
)

logger = logging.getLogger(__name__)

REGISTRY_FILE = Path("registry/tray-connectors.yaml")
KNOWLEDGE_DIR = Path("knowledge-base/tray-platform/connectors")
WORKFLOWS_DIR = Path("skills/tray-ai/workflows/connectors")

# Scoring dimensions and weights from scoring.md
SCORING_DIMENSIONS = [
    ("supply_chain_fit", 0.30),
    ("existing_stack_synergy", 0.25),
    ("customer_value", 0.20),
    ("operational_efficiency", 0.15),
    ("data_enrichment", 0.10),
]

# Connectors known to be active in Ohanafy's stack
KNOWN_ACTIVE_CONNECTORS = {
    "salesforce", "aws-s3", "aws-lambda", "quickbooks", "slack",
    "google-sheets", "github",
}


class DiscoveryError(Exception):
    """Base error for discovery operations."""


class FetchError(DiscoveryError):
    """Failed to fetch connector data from Tray platform."""


class ScoringError(DiscoveryError):
    """Failed to score a connector."""


class KnowledgeError(DiscoveryError):
    """Failed to generate knowledge for a connector."""


class RegistryError(DiscoveryError):
    """Failed to read/write the connector registry."""


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

TRAY_CONNECTORS_URL = "https://tray.io/documentation/connectors/browse/all/"


def _parse_connector_listing(html: str) -> list[dict]:
    """Extract connector names and links from the Tray docs listing page.

    Parses the connector browse page for connector entries.
    Returns list of {name, display_name, url} dicts.
    """
    connectors = []
    # Match connector links in the listing page
    # Pattern: links to /documentation/connectors/service/<name>/
    pattern = re.compile(
        r'href="(/documentation/connectors/service/([^/"]+)/[^"]*)"[^>]*>([^<]+)',
        re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        path, slug, display_name = match.groups()
        display_name = display_name.strip()
        if display_name and slug:
            connectors.append({
                "name": slug.lower().replace(" ", "-"),
                "display_name": display_name,
                "url": f"https://tray.io{path}",
            })

    # Deduplicate by name
    seen = set()
    unique = []
    for c in connectors:
        if c["name"] not in seen:
            seen.add(c["name"])
            unique.append(c)

    return unique


def _classify_category(name: str, description: str) -> ConnectorCategory:
    """Classify a connector into a category based on name and description.

    Simple rule-based classification — covers the common cases.
    Anything unmatched goes to OTHER for manual triage.
    """
    text = f"{name} {description}".lower()

    crm_keywords = {"salesforce", "hubspot", "zoho", "pipedrive", "dynamics", "crm", "sugar"}
    erp_keywords = {"quickbooks", "netsuite", "sage", "xero", "sap", "erp", "invoice", "accounting"}
    edi_keywords = {"edi", "shipstation", "shipbob", "freight", "logistics", "wms", "ups", "fedex", "dhl"}
    ecom_keywords = {"shopify", "bigcommerce", "woocommerce", "magento", "stripe", "square", "paypal", "ecommerce"}
    comm_keywords = {"slack", "teams", "email", "smtp", "twilio", "sms", "sendgrid", "mailchimp", "intercom"}
    storage_keywords = {"s3", "gcs", "azure-blob", "snowflake", "redshift", "bigquery", "postgres", "mysql", "mongodb", "database", "warehouse"}
    dev_keywords = {"github", "gitlab", "jira", "jenkins", "datadog", "pagerduty", "sentry", "circleci"}

    for keyword in crm_keywords:
        if keyword in text:
            return ConnectorCategory.CRM
    for keyword in erp_keywords:
        if keyword in text:
            return ConnectorCategory.ERP_ACCOUNTING
    for keyword in storage_keywords:
        if keyword in text:
            return ConnectorCategory.STORAGE_DATA
    for keyword in edi_keywords:
        if keyword in text:
            return ConnectorCategory.EDI_SUPPLY_CHAIN
    for keyword in ecom_keywords:
        if keyword in text:
            return ConnectorCategory.ECOMMERCE
    for keyword in comm_keywords:
        if keyword in text:
            return ConnectorCategory.COMMUNICATION
    for keyword in dev_keywords:
        if keyword in text:
            return ConnectorCategory.DEVELOPER_TOOLS
    return ConnectorCategory.OTHER


def discover_connectors(html_content: str | None = None) -> list[TrayConnectorEntry]:
    """Discover all available connectors from the Tray.io platform.

    If html_content is provided, parses it directly (for testing or cached pages).
    Otherwise, the caller is responsible for fetching the page via WebFetch
    and passing the content.

    Returns list of TrayConnectorEntry objects.
    """
    if html_content is None:
        raise FetchError(
            "No HTML content provided. Caller must fetch "
            f"{TRAY_CONNECTORS_URL} via WebFetch and pass the content."
        )

    raw = _parse_connector_listing(html_content)
    if not raw:
        logger.warning("No connectors parsed from HTML. Page structure may have changed.")

    now = datetime.utcnow()
    entries = []
    for item in raw:
        category = _classify_category(item["name"], item.get("description", ""))
        entry = TrayConnectorEntry(
            name=item["name"],
            display_name=item["display_name"],
            description=item.get("description", ""),
            category=category,
            documentation_url=item.get("url"),
            discovered_at=now,
            last_refreshed=now,
        )
        entries.append(entry)

    logger.info("Discovered %d connectors from Tray docs", len(entries))
    return entries


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

SCORING_PROMPT = """You are scoring a Tray.io connector for relevance to Ohanafy, a beverage supply chain SaaS company.

Ohanafy's stack: Salesforce (CRM), AWS (S3, Lambda, RDS), QuickBooks (accounting), Slack, Google Sheets, Tray.io (iPaaS).
Ohanafy's domain: 3-tier beverage distribution, order management, inventory, depletions, EDI, DTC ecommerce.

Score this connector on 5 dimensions (each 0.0-1.0):

1. supply_chain_fit (weight 0.30): Does it support beverage distribution, logistics, EDI, warehouse, inventory?
2. existing_stack_synergy (weight 0.25): Does it integrate with Salesforce, AWS, QuickBooks, Slack, or other Ohanafy services?
3. customer_value (weight 0.20): Would it benefit Ohanafy's customers (distributors, suppliers, retailers)?
4. operational_efficiency (weight 0.15): Could it automate a manual process at Ohanafy?
5. data_enrichment (weight 0.10): Does it add data signals for analytics, reporting, or AI?

Connector: {name}
Display Name: {display_name}
Category: {category}
Description: {description}
Operations: {operations}

Respond in this exact JSON format:
{{
  "dimensions": [
    {{"name": "supply_chain_fit", "score": 0.0, "reasoning": "..."}},
    {{"name": "existing_stack_synergy", "score": 0.0, "reasoning": "..."}},
    {{"name": "customer_value", "score": 0.0, "reasoning": "..."}},
    {{"name": "operational_efficiency", "score": 0.0, "reasoning": "..."}},
    {{"name": "data_enrichment", "score": 0.0, "reasoning": "..."}}
  ],
  "ohanafy_use_cases": ["use case 1", "use case 2"],
  "opportunity_type": "optimize_existing|new_integration|exploration|not_relevant",
  "rationale": "2-3 sentence summary"
}}"""


def assess_relevance(connector: TrayConnectorEntry) -> RelevanceAssessment:
    """Score a connector's relevance to Ohanafy using Claude haiku.

    Returns a RelevanceAssessment with per-dimension scores and overall weighted score.
    """
    client = anthropic.Anthropic()
    model = "claude-haiku-4-5-20251001"

    prompt = SCORING_PROMPT.format(
        name=connector.name,
        display_name=connector.display_name,
        category=connector.category.value,
        description=connector.description or "(no description available)",
        operations=", ".join(connector.operations[:20]) if connector.operations else "(unknown)",
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text

        # Extract JSON from response (handle markdown code fences)
        json_match = re.search(r"\{[\s\S]*\}", raw_text)
        if not json_match:
            raise ScoringError(f"No JSON in scoring response for {connector.name}")
        data = json.loads(json_match.group())

    except anthropic.APIError as exc:
        raise ScoringError(f"Claude API error scoring {connector.name}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ScoringError(f"Invalid JSON in scoring response for {connector.name}: {exc}") from exc

    # Build dimension scores with weights
    dimensions = []
    for dim_data in data.get("dimensions", []):
        dim_name = dim_data["name"]
        weight = dict(SCORING_DIMENSIONS).get(dim_name, 0.0)
        dimensions.append(ScoringDimension(
            name=dim_name,
            score=min(max(float(dim_data["score"]), 0.0), 1.0),
            weight=weight,
            reasoning=dim_data.get("reasoning", ""),
        ))

    # Compute weighted overall score
    overall = sum(d.score * d.weight for d in dimensions)

    # Determine current usage
    current_usage = CurrentUsage.NOT_CONFIGURED
    if connector.name in KNOWN_ACTIVE_CONNECTORS:
        current_usage = CurrentUsage.ACTIVE
    elif WORKFLOWS_DIR.exists() and (WORKFLOWS_DIR / f"{connector.name}.json").exists():
        current_usage = CurrentUsage.CONFIGURED_UNUSED

    # Parse opportunity type
    opp_raw = data.get("opportunity_type", "not_relevant")
    try:
        opportunity = OpportunityType(opp_raw)
    except ValueError:
        opportunity = OpportunityType.NOT_RELEVANT

    return RelevanceAssessment(
        connector_name=connector.name,
        overall_score=round(overall, 3),
        dimensions=dimensions,
        rationale=data.get("rationale", ""),
        ohanafy_use_cases=data.get("ohanafy_use_cases", []),
        current_usage=current_usage,
        opportunity_type=opportunity,
        model_used=model,
    )


# ---------------------------------------------------------------------------
# Knowledge generation
# ---------------------------------------------------------------------------

KNOWLEDGE_PROMPT = """Generate a structured knowledge file for this Tray.io connector.
Context: Ohanafy is a beverage supply chain SaaS using Salesforce, AWS, QuickBooks, Slack, Tray.io.

Connector: {name}
Display Name: {display_name}
Category: {category}
Description: {description}
Relevance Score: {score}
Use Cases: {use_cases}
Rationale: {rationale}

Write a concise knowledge document with these sections:

1. Summary (1 paragraph): What this connector does and why it matters for Ohanafy
2. Key Operations (table format): Operation name | Description | Ohanafy use case
3. Recommended Workflows: Numbered list of Tray workflows Ohanafy could build
4. Integration Notes: Technical details — auth type, rate limits, gotchas

Respond in this exact JSON format:
{{
  "summary": "...",
  "operations": [{{"name": "...", "description": "...", "use_case": "..."}}],
  "recommended_workflows": ["workflow 1", "workflow 2"],
  "integration_notes": "..."
}}"""


def generate_knowledge(
    connector: TrayConnectorEntry,
    assessment: RelevanceAssessment,
) -> ConnectorKnowledge:
    """Generate a structured knowledge artifact for a high-relevance connector.

    Uses Claude sonnet for reasoning-tier generation.
    """
    client = anthropic.Anthropic()
    model = "claude-sonnet-4-20250514"

    prompt = KNOWLEDGE_PROMPT.format(
        name=connector.name,
        display_name=connector.display_name,
        category=connector.category.value,
        description=connector.description or "(no description available)",
        score=assessment.overall_score,
        use_cases=", ".join(assessment.ohanafy_use_cases),
        rationale=assessment.rationale,
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text

        json_match = re.search(r"\{[\s\S]*\}", raw_text)
        if not json_match:
            raise KnowledgeError(f"No JSON in knowledge response for {connector.name}")
        data = json.loads(json_match.group())

    except anthropic.APIError as exc:
        raise KnowledgeError(f"Claude API error generating knowledge for {connector.name}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise KnowledgeError(f"Invalid JSON in knowledge response for {connector.name}: {exc}") from exc

    ops = [
        OperationDetail(
            name=op.get("name", ""),
            description=op.get("description", ""),
            use_case=op.get("use_case", ""),
        )
        for op in data.get("operations", [])
    ]

    return ConnectorKnowledge(
        connector_name=connector.name,
        summary=data.get("summary", ""),
        operations_detail=ops,
        ohanafy_relevance=assessment.rationale,
        recommended_workflows=data.get("recommended_workflows", []),
        integration_notes=data.get("integration_notes", ""),
    )


def write_knowledge_file(knowledge: ConnectorKnowledge) -> Path:
    """Write a knowledge artifact to the knowledge-base directory.

    Returns the path of the written file.
    """
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    path = KNOWLEDGE_DIR / f"{knowledge.connector_name}.md"

    ops_table = "| Operation | Description | Ohanafy Use Case |\n|-----------|-------------|------------------|\n"
    for op in knowledge.operations_detail:
        ops_table += f"| {op.name} | {op.description} | {op.use_case} |\n"

    workflows = "\n".join(f"{i+1}. {w}" for i, w in enumerate(knowledge.recommended_workflows))

    content = f"""# {knowledge.connector_name.replace('-', ' ').title()}

## Summary

{knowledge.summary}

## Why It's Relevant to Ohanafy

{knowledge.ohanafy_relevance}

## Key Operations

{ops_table}

## Recommended Workflows

{workflows}

## Integration Notes

{knowledge.integration_notes}

---
*Generated by Tray Discovery agent on {knowledge.generated_at.strftime('%Y-%m-%d')}*
"""

    path.write_text(content)
    logger.info("Wrote knowledge file: %s", path)
    return path


# ---------------------------------------------------------------------------
# Opportunity detection
# ---------------------------------------------------------------------------


def detect_opportunities(assessments: list[RelevanceAssessment]) -> list[dict]:
    """Compare assessments against current usage to identify integration gaps.

    Returns list of opportunity dicts with connector_name, opportunity_type,
    score, and description.
    """
    opportunities = []

    # Load current connector configs
    active_names = set(KNOWN_ACTIVE_CONNECTORS)
    if WORKFLOWS_DIR.exists():
        for p in WORKFLOWS_DIR.glob("*.json"):
            active_names.add(p.stem)

    for a in assessments:
        if a.overall_score < 0.65:
            continue

        if a.current_usage == CurrentUsage.NOT_CONFIGURED and a.overall_score >= 0.65:
            opportunities.append({
                "connector_name": a.connector_name,
                "opportunity_type": a.opportunity_type.value,
                "score": a.overall_score,
                "use_cases": a.ohanafy_use_cases,
                "description": f"Not configured but scored {a.overall_score:.2f}. {a.rationale}",
            })
        elif a.current_usage == CurrentUsage.CONFIGURED_UNUSED:
            opportunities.append({
                "connector_name": a.connector_name,
                "opportunity_type": "optimize_existing",
                "score": a.overall_score,
                "use_cases": a.ohanafy_use_cases,
                "description": f"Configured but unused. Scored {a.overall_score:.2f}. {a.rationale}",
            })

    opportunities.sort(key=lambda o: o["score"], reverse=True)
    logger.info("Detected %d opportunities", len(opportunities))
    return opportunities


# ---------------------------------------------------------------------------
# Registry I/O
# ---------------------------------------------------------------------------


def load_registry() -> dict:
    """Load the tray-connectors.yaml registry."""
    if not REGISTRY_FILE.exists():
        raise RegistryError(f"Registry file not found: {REGISTRY_FILE}")
    return yaml.safe_load(REGISTRY_FILE.read_text())


def save_registry(data: dict) -> None:
    """Write the tray-connectors.yaml registry."""
    REGISTRY_FILE.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
    logger.info("Updated registry: %s", REGISTRY_FILE)


def update_registry(
    connector: TrayConnectorEntry,
    assessment: RelevanceAssessment,
) -> None:
    """Add or update a connector entry in the registry."""
    data = load_registry()
    connectors = data.get("connectors", [])

    entry = RegistryEntry(
        name=connector.name,
        display_name=connector.display_name,
        category=connector.category.value,
        relevance_score=assessment.overall_score,
        opportunity_type=assessment.opportunity_type.value,
        current_usage=assessment.current_usage.value,
        last_assessed=assessment.assessed_at.strftime("%Y-%m-%d"),
        tags=connector.tags,
    ).model_dump()

    # Replace existing entry or append
    replaced = False
    for i, existing in enumerate(connectors):
        if existing.get("name") == connector.name:
            connectors[i] = entry
            replaced = True
            break
    if not replaced:
        connectors.append(entry)

    data["connectors"] = connectors
    save_registry(data)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(action: str, **kwargs: Any) -> Any:
    """Entry point for the skill runner."""
    actions = {
        "discover": discover_connectors,
        "score": assess_relevance,
        "generate_knowledge": generate_knowledge,
        "detect_opportunities": detect_opportunities,
    }
    fn = actions.get(action)
    if fn is None:
        raise DiscoveryError(f"Unknown action: {action}. Supported: {list(actions.keys())}")
    try:
        return fn(**kwargs)
    except DiscoveryError:
        raise
    except Exception as exc:
        logger.error("Discovery action '%s' failed: %s", action, exc)
        raise DiscoveryError(f"Unexpected error in {action}: {exc}") from exc
