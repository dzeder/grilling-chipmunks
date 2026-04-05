# Relevance Scoring

How the content watcher scores transcript relevance to Ohanafy.

## Scoring Model

Uses Claude haiku for fast classification (0.0 - 1.0 scale).

## Score Thresholds

- >= 0.85 — High relevance. Auto-create GitHub issue.
- >= 0.65 — Medium relevance. Create issue, team triages.
- < 0.65 — Low relevance. Log but do not create issue.

## Scoring Criteria

### beverage_industry (weight: high)
- Mentions 3-tier distribution, TTB, depletions, distributor relationships
- Pricing models, allocation strategies, chain authorization
- Specific beverage categories: wine, beer, spirits

### product_strategy (weight: medium)
- B2B SaaS pricing, customer success patterns
- Vertical SaaS strategies relevant to Ohanafy's market
- Data-driven product decisions

### salesforce (weight: medium)
- SF platform updates affecting Ohanafy's implementation
- Apex, Flows, LWC patterns applicable to beverage supply chain
- SF DevOps and CI/CD improvements

### ai_dev_tools (weight: medium)
- Claude/Anthropic updates and new capabilities
- Agent framework improvements (pydantic-ai, langgraph)
- Prompt engineering patterns applicable to support/docs agents

## Anti-Patterns

- Generic "AI is changing everything" content → score low
- Content about industries unrelated to beverage → score 0
- Pure marketing content with no actionable insights → score low
