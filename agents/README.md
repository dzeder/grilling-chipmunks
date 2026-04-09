# Agents

19 specialist agents organized into 5 teams. Create new agents from `agents/_template/`.

## Salesforce / FDE Team

| Agent | Role |
|-------|------|
| **fde-strategist** | Planning and delegation (read-only, spawns other agents) |
| **fde-engineer** | Agentforce implementation (Apex, Agent Scripts, metadata) |
| **fde-qa-engineer** | Test execution, debug logs, observability |
| **fde-release-engineer** | Deployment, Connected Apps, CI/CD |
| **fde-experience-specialist** | Conversation design, persona, LWC UI |

## Professional Services

| Agent | Role |
|-------|------|
| **ps-technical-architect** | Backend Apex, integrations, data modeling |
| **ps-solution-architect** | Metadata design, Flows, security, architecture docs |

## Integration Team

| Agent | Role |
|-------|------|
| **salesforce-integration-architect** | SF Composite API, Named Credentials, platform events |
| **edi-processing-specialist** | EDI X12 (850/810/856), OpenText, Transcepta |
| **tray-script-generator** | Tray script creation from patterns |
| **tray-script-tester** | Tray script validation and testing |
| **tray-discovery** | Automated Tray connector discovery with Claude scoring |
| **ohanafy-data-model** | Ohanafy object model, relationships, field usage |
| **domain-specialist-designer** | Domain-specific integration design |
| **progressive-disclosure-executor** | Phased implementation approach |
| **content** | Content pipeline orchestrator (drives content-watcher skill) |

## Domain

| Agent | Role |
|-------|------|
| **beverage-erp-expert** | Beverage distribution (VIP, Encompass, DSD, three-tier) |

## Support

| Agent | Role |
|-------|------|
| **documentation-consolidation-specialist** | Doc organization and consolidation |
| **integration-guide-curator** | Integration guide maintenance |

## Creating a New Agent

1. Copy `agents/_template/` to `agents/<new-agent-name>.md`
2. Follow the template in `docs/AGENT_TEMPLATE.md`
3. Add evals in `evals/agents/<new-agent-name>/`
4. Pass rate: 85% target, 75% hard fail
