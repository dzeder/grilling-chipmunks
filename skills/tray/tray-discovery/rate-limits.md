# Rate Limits

## Tray.io API

- 120 reads per minute (from skills/tray-ai/connector/rate-limits.md)
- Discovery pipeline batches connector detail calls to stay under this limit
- On 429 response: exponential backoff (2s base, 2x multiplier, max 30s)

## Claude API

- Standard tier limits apply
- Haiku (scoring): lightweight calls, unlikely to hit limits
- Sonnet (knowledge gen): larger prompts, batch carefully if many high-relevance connectors

## WebFetch

- Tray documentation pages: 1 request per second (polite crawling)
- Cache responses locally during a single pipeline run to avoid redundant fetches

## Pipeline Guidance

A typical discovery run processes ~200-400 connectors:
- Discovery phase: 1-5 web fetches (listing pages), well within limits
- Scoring phase: ~200-400 haiku calls, ~1-2 minutes at standard rates
- Knowledge phase: ~10-30 sonnet calls (only high-relevance), ~2-5 minutes
- Total expected runtime: ~5-10 minutes for a full run
