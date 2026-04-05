# Tray.io Connector Discovery

Discovers, catalogs, and evaluates Tray.io platform connectors for Ohanafy relevance.

## When to Use

- Weekly automated discovery run (Monday 3am via CI)
- On-demand platform learning when evaluating new integrations
- After Tray.io platform updates to catch new connectors
- When the team asks "what connectors does Tray have for X?"

## Interface

Entry point: `skill.py:run(action, **kwargs)`

### Actions

| Action | Parameters | Returns | Model |
|--------|-----------|---------|-------|
| `discover` | — | `list[TrayConnectorEntry]` | — (API + web) |
| `score` | `connector: TrayConnectorEntry` | `RelevanceAssessment` | haiku |
| `generate_knowledge` | `connector, assessment` | `ConnectorKnowledge` | sonnet |
| `detect_opportunities` | `assessments: list` | `list[dict]` | — |

### Parameters

- `action` (required): One of `discover`, `score`, `generate_knowledge`, `detect_opportunities`
- `connector`: A `TrayConnectorEntry` instance (for score/generate_knowledge)
- `assessment`: A `RelevanceAssessment` instance (for generate_knowledge)
- `assessments`: List of assessments (for detect_opportunities)

### Returns

Typed Pydantic models defined in `schema.py`.

## Pipeline Flow

```
discover_connectors()     # Fetch all connectors from Tray docs
        │
        ▼
  diff against registry   # Skip already-cataloged connectors
        │
        ▼
  assess_relevance()      # Score each new connector (haiku)
        │
        ├── >= 0.85 ──▶ generate_knowledge() + create issue (sonnet)
        ├── >= 0.65 ──▶ create issue only
        └── < 0.65  ──▶ registry entry only (no issue)
        │
        ▼
  update registry         # Write results to tray-connectors.yaml
```

## Commands

- `python -m skills.tray_ai.discovery.commands.run_discovery` — Full pipeline
- `python -m skills.tray_ai.discovery.commands.list_connectors` — Show catalog
- `python -m skills.tray_ai.discovery.commands.assess_connector` — Score one connector

## Error Handling

See `error-codes.md`. All errors log before raising.

## Rate Limits

See `rate-limits.md`. Tray API: 120 reads/min. Claude: standard tier limits.
