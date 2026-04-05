# Testing Strategy — Ohanafy AI Ops

## Four Testing Layers

### Unit Tests (`tests/unit/`)

Zero external calls. All mocked. Every push.

**Skills:** Mock external client, test input/output, test every error type, test retry.
**Agents:** Mock all skills AND Claude, test routing/escalation/PII-not-in-logs.
**Coverage:** 90% skills, 85% agent logic.

### Integration Tests (`tests/integration/`)

LocalStack for AWS, SF scratch org.
Mark: `@pytest.mark.integration`. Run on PR open.
Never use production. Never use personal sandbox.

### E2E Tests (`tests/e2e/`)

Real Claude, real SF sandbox, real AWS staging.
Mark: `@pytest.mark.e2e`. Run on merge to staging only. ~$2-5/run.

Must cover:
- Support happy path
- Compliance escalation
- Doc generation
- Unknown customer handling

### Evals (`evals/`)

Golden dataset per agent. Hard checks + Claude Haiku rubric scoring.
Pass rate: 85% target, 75% hard fail. CI exits code 1 on failure.
Run on every PR. `evals/results/` is immutable — never delete.

## Running Tests

```bash
# Unit tests only (default)
pytest

# Integration tests (requires LocalStack or SF scratch org)
pytest -m integration

# E2E tests (requires real credentials, staging env only)
pytest -m e2e

# Evals only
pytest -m eval

# Everything
pytest -m ""

# With coverage
pytest --cov --cov-report=html
```

## Fixtures

See `tests/conftest.py` for shared fixtures:
- `sf_scratch_org` — session, skips if SF_CI_SCRATCH_ORG_URL not set
- `sf_sandbox` — session, skips if CI_ENV != staging
- `localstack_s3` — function, boto3 at localhost:4566
- `test_bucket` — function, creates+tears down S3 bucket
- `mock_claude` — patches anthropic.Anthropic, returns canned response
- `real_anthropic_client` — session, skips if no ANTHROPIC_API_KEY

## Fixture Data

- `tests/fixtures/sf_responses/` — Canned Salesforce API responses
- `tests/fixtures/claude_responses/` — Canned Claude API responses
- `tests/fixtures/tray_payloads/` — Tray.ai webhook/event payloads
- `tests/fixtures/aws_events/` — AWS event payloads (Lambda, S3, etc.)
