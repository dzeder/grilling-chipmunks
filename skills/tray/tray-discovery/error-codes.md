# Discovery Skill Error Codes

All errors log before raising.

## DiscoveryError

Base exception for all discovery operations.

| Code | Meaning | Recovery |
|------|---------|----------|
| `DISCOVERY_UNKNOWN_ACTION` | Unrecognized action passed to `run()` | Check supported actions: discover, score, generate_knowledge, detect_opportunities |
| `DISCOVERY_UNEXPECTED` | Catch-all for unhandled exceptions | Review logs, check service status |

## FetchError

Raised when connector discovery from the Tray platform fails.

| Code | Meaning | Recovery |
|------|---------|----------|
| `FETCH_API_ERROR` | Tray API unreachable or returned error | Check Tray status page, retry with backoff |
| `FETCH_RATE_LIMITED` | Hit Tray API rate limits (120 reads/min) | Wait and retry with exponential backoff |
| `FETCH_WEB_ERROR` | Failed to fetch Tray documentation page | Check URL, retry. Non-blocking — API data is primary |
| `FETCH_PARSE_ERROR` | Could not parse connector data from response | Check response format, may indicate API change |

## ScoringError

Raised when relevance assessment fails.

| Code | Meaning | Recovery |
|------|---------|----------|
| `SCORING_API_ERROR` | Claude API call failed during scoring | Retry with backoff. Check ANTHROPIC_API_KEY |
| `SCORING_INVALID_RESPONSE` | Claude returned non-parseable scoring output | Retry. If persistent, review scoring prompt |

## KnowledgeError

Raised when knowledge generation fails.

| Code | Meaning | Recovery |
|------|---------|----------|
| `KNOWLEDGE_API_ERROR` | Claude API call failed during generation | Retry with backoff |
| `KNOWLEDGE_WRITE_ERROR` | Could not write knowledge file to disk | Check permissions on knowledge-base/tray-platform/ |

## RegistryError

Raised when registry operations fail.

| Code | Meaning | Recovery |
|------|---------|----------|
| `REGISTRY_READ_ERROR` | Could not read tray-connectors.yaml | Check file exists and is valid YAML |
| `REGISTRY_WRITE_ERROR` | Could not update tray-connectors.yaml | Check file permissions |
| `REGISTRY_DUPLICATE` | Connector already exists in registry | Not a true error — skip and continue |
