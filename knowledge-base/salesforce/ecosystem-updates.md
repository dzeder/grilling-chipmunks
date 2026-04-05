---
title: "Salesforce Ecosystem Updates"
last_updated: "2026-04-05"
next_review: "2026-06-05"
confidence: high
sources:
  - "Salesforce Spring '26 Release Notes — help.salesforce.com"
  - "Salesforce Developers Blog — developer.salesforce.com/blogs/2026/01"
  - "Salesforce Ben — salesforceben.com"
  - "Salesforce Agentforce Pricing — salesforce.com/agentforce/pricing"
  - "Revenue Ops LLC — revenueopsllc.com (Connected Apps deprecation)"
  - "Agentforce Lens — agentforcelens.com (ECA migration playbook)"
  - "H2K Infosys — h2kinfosys.com (Data Cloud 2025-2026)"
maintained_by: content-watcher
ohanafy_relevance:
  - skills/ohanafy/core
  - skills/ohanafy/platform
  - skills/salesforce
  - skills/claude
---

# Salesforce Ecosystem Updates

Release-specific features, deprecations, and action items relevant to Ohanafy's Salesforce implementation. Ohanafy currently uses API v62.0 (per CLAUDE.md).

## Spring '26 Release Highlights

### Developer Features

| Feature | Status | Relevance to Ohanafy |
|---------|--------|---------------------|
| **Named Query API (GA)** | Generally Available | Define custom SOQL queries as REST API endpoints. Could replace some custom Apex REST endpoints in OHFY packages for integrations. |
| **LWC API v66.0 — Complex Template Expressions (Beta)** | Beta | JavaScript expressions in LWC templates. Would simplify UI logic in OHFY-OMS-UI, OHFY-WMS-UI, OHFY-REX-UI components. |
| **Apex Cursor Class** | GA | Query up to 50M records with server-side cursors. Useful for large depletion data exports and reporting in OHFY-Core. Max 10,000 cursor instances per 24-hour period. |
| **Flow Builder — Collapsible Decision/Loop Blocks** | GA | Visual improvement for complex flows. Helps maintain OHFY automation flows. |
| **Agentforce Canvas View** | GA | New UI surface for embedding agent interactions. Could host Ohanafy support agent. |
| **AI-Powered Flow Drafts** | GA | Generate Flow automation from natural language. Accelerates OHFY workflow development. |

### Security Changes (Action Required)

| Change | Timeline | Impact on Ohanafy |
|--------|----------|------------------|
| **Session IDs in outbound messages removed** | February 16, 2026 | Any OHFY outbound messages using session IDs must migrate to OAuth. Check `skills/ohanafy/core/references/source-index.md` for outbound message references. |
| **Connected Apps creation disabled by default** | Spring '26 (now) | New Connected Apps require Salesforce Support intervention. See deprecation section below. |
| **External Client Apps (ECAs)** replacing Connected Apps | Ongoing | Must plan migration for all OHFY integrations using Connected Apps. |

### API Version

- Spring '26 introduces API v66.0.
- Ohanafy currently targets API v62.0 (per CLAUDE.md). This is still supported but 4 versions behind.
- **Action item:** Evaluate upgrading OHFY packages to v66.0 for access to Named Query API and Apex Cursor features. Test in scratch org first.

---

## Agentforce

### Current State (April 2026)

Agentforce has gone through rapid iteration:

| Release | Date | Key Additions |
|---------|------|---------------|
| Agentforce 1.0 | Dreamforce 2024 | Initial launch — service agents, conversational AI |
| Agentforce 2dx | April 2025 (GA) | Proactive agents, multi-step processes, Agent Builder, AgentExchange |
| Agentforce 360 | Post-Dreamforce 2025 (GA) | Agent Builder, Agent Script, Agentforce Voice, Intelligent Context |
| Agentforce Contact Center | Enterprise Connect 2026 (GA) | Unified voice + digital + CRM + AI in single platform |

### Pricing Model

Salesforce offers three pricing approaches:

| Model | Cost | Best For |
|-------|------|----------|
| **Per-conversation** | $2/conversation | Low-volume, predictable usage |
| **Flex Credits** | $500 per 100K credits (standard action = 20 credits/$0.10, voice = 30 credits/$0.15) | Variable usage; recommended for most new deployments |
| **Per-user add-on** | $125/user/month (Sales, Service, Field Service) | High-volume per-user teams |
| **Agentforce 1 Edition** | $550/user/month | Full-suite agent deployment |

As of early 2026, **Flex Credits** is the recommended model for most new deployments.

Additionally, Salesforce announced a 6% pricing increase across core products, bundled with unlimited Agentforce licenses for certain editions.

### Relevance to Ohanafy

See `ai-supply-chain.md` (Agentforce section) for the detailed strategy. Key points:

- This AI Ops framework (davis-v1) and Agentforce serve different purposes and should be complementary
- Agentforce for customer-facing support agents inside Salesforce
- davis-v1 for operational intelligence, content monitoring, cross-platform orchestration outside Salesforce
- The knowledge-base files in this repo can enrich Agentforce agent context

---

## Data Cloud

### Current Capabilities (Spring '26)

| Feature | Description | Ohanafy Relevance |
|---------|------------|-------------------|
| **Zero-Copy Connectors** | Live data access from external data warehouses without ETL | Could connect Ohanafy data to analytics tools without export |
| **Unstructured Data Connectors** | Google Drive, SharePoint document ingestion | Could ingest distributor reports (PDF/Excel) into customer profiles |
| **Clean Rooms** | Privacy-safe data collaboration between orgs | Could enable supplier↔distributor data sharing without exposing PII |
| **Data 360 Related Lists** | Pull Data 360 attributes into standard SF objects | Enrich Account, Contact with unified customer context |
| **Real-Time Processing** | Updates customer profiles as data arrives | Could enable near-real-time depletion alerting |
| **Industry Data Models** | Pre-configured templates for retail, manufacturing | No beverage-specific template yet, but retail template may be adaptable |
| **Dynamic Segmentation** | Build customer segments for targeted campaigns | Segment accounts by performance, territory, distributor for targeted outreach |

### Ohanafy Opportunity

1. **Depletion analytics at scale:** Aggregate `Depletion__c` data across all customers in Data Cloud for benchmarking and trend analysis
2. **Customer 360 for distributors:** Combine SF CRM data + Tray integration data + depletion data for a complete distributor relationship view
3. **Real-time depletion alerting:** When depletion data arrives via EDI, Data Cloud can trigger actions immediately (low-stock alerts, reorder suggestions)
4. **Cross-customer insights:** Anonymous benchmarking — "your depletions in this territory are X% below average for your category"

**Blocker:** Data Cloud pricing is significant ($65K-$250K/year depending on edition). For Ohanafy's 25-person team, this is a meaningful investment. Evaluate ROI before committing.

---

## Deprecations & Breaking Changes

### Connected Apps → External Client Apps (Critical)

**Status:** Connected Apps creation disabled by default in Spring '26. Existing Connected Apps continue to work but are in maintenance mode.

**Timeline:**
- Spring '26 (now): New Connected App creation disabled by default; requires SF Support to unlock
- Future releases: SF Support will no longer unlock new Connected App creation
- Mid-2027: SOAP login capability removed from all supported API versions

**What Ohanafy Must Do:**
1. **Inventory all Connected Apps** used by OHFY packages and Tray.io integrations
2. **Plan migration to External Client Apps (ECAs)** for each integration
3. **Prioritize Tray.io connectors** — Tray's Salesforce connector likely uses a Connected App under the hood. Check with Tray on their migration timeline.
4. **Update sf CLI authentication** if any scripts use Connected App OAuth flows
5. **Test ECA migration in scratch org** before touching production

### Session ID in Outbound Messages

**Removed:** February 16, 2026. Must use OAuth instead.

**Action:** Grep OHFY-Core source-index for outbound message references. If any use session IDs, update to OAuth flow.

### API Version Retirement Schedule

Salesforce retires old API versions periodically. Current minimum supported version varies — check the official deprecation notice. Ohanafy's v62.0 target is still supported but should be tracked.

---

## Ohanafy Action Items

### Immediate (This Quarter)

- [ ] Audit Connected Apps usage across all OHFY packages and Tray integrations
- [ ] Verify no outbound messages rely on session IDs (deprecated Feb 2026)
- [ ] Test LWC Complex Template Expressions (Beta) in OHFY-OMS-UI dev org

### Near-Term (Next 2 Quarters)

- [ ] Begin Connected App → External Client App migration planning
- [ ] Evaluate API v66.0 upgrade for Named Query API and Cursor benefits
- [ ] Prototype Agentforce Canvas View for Ohanafy support agent
- [ ] Assess Data Cloud ROI for depletion analytics use case

### Long-Term (6-12 Months)

- [ ] Complete ECA migration before SOAP login removal (mid-2027)
- [ ] Evaluate Agentforce Flex Credits pricing for customer-facing support
- [ ] Explore Data Cloud industry data model (retail template) for Ohanafy
