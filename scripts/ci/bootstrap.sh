#!/usr/bin/env bash
#
# bootstrap.sh — Ohanafy AI Ops scaffold
#
# Creates all directories and placeholder files.
# Idempotent: safe to run multiple times.
#
# Usage: bash ci-cd/scripts/bootstrap.sh

set -euo pipefail

echo "Ohanafy AI Ops — Bootstrap"
echo "=========================="

# --- Directories ---
echo "Creating directories..."

DIRS=(
  agents/_template/prompts/examples
  agents/support agents/salesforce agents/docs agents/ci-cd agents/watchers agents/content
  skills/_template/tests
  skills/salesforce/soql-query/tests skills/salesforce/apex-deploy/tests
  skills/salesforce/flow-builder/tests skills/salesforce/permission-set-manager/tests
  skills/salesforce/metadata-backup/tests
  skills/tray-ai/connector/tests skills/tray-ai/webhook-handler/tests
  skills/tray-ai/error-recovery/tests skills/tray-ai/workflow-template/tests
  skills/tray-ai/workflows
  skills/aws/lambda-deploy/tests skills/aws/s3-manager/tests
  skills/aws/cdk-deploy/tests skills/aws/iam-audit/tests
  skills/aws/rds-query/tests skills/aws/secrets-manager/tests
  skills/claude/prompt-loader/tests skills/claude/context-manager/tests
  skills/claude/tool-use/tests skills/claude/model-router/tests
  skills/docs/md-generator/tests skills/docs/docx-builder/tests
  skills/docs/html-publisher/tests skills/docs/diff-summarizer/tests
  skills/content-watcher/commands skills/content-watcher/monitor
  skills/content-watcher/github skills/content-watcher/tests
  ci-cd/pipelines ci-cd/scripts ci-cd/templates
  docs/internal docs/external docs/customer-specific docs/templates
  knowledge-base/salesforce knowledge-base/beverage-supply-chain
  knowledge-base/industry-insights knowledge-base/customer-specific
  registry
  watchers/digest watchers/adoption-queue
  evals/datasets evals/scorers evals/results
  tests/fixtures/sf_responses tests/fixtures/claude_responses
  tests/fixtures/tray_payloads tests/fixtures/aws_events
  tests/unit/skills tests/unit/agents
  tests/integration/salesforce tests/integration/aws tests/integration/flows
  tests/e2e
)

for dir in "${DIRS[@]}"; do
  mkdir -p "$dir"
done

# --- .gitkeep in empty leaf dirs ---
echo "Adding .gitkeep files..."

GITKEEP_DIRS=(
  agents/support agents/salesforce agents/docs agents/ci-cd agents/watchers agents/content
  agents/_template/prompts/examples
  skills/_template/tests
  docs/internal docs/external docs/customer-specific
  knowledge-base/customer-specific
  watchers/digest
  evals/datasets evals/scorers evals/results
  tests/fixtures/sf_responses tests/fixtures/claude_responses
  tests/fixtures/tray_payloads tests/fixtures/aws_events
  tests/integration/salesforce tests/integration/aws tests/integration/flows
  tests/e2e
)

for dir in "${GITKEEP_DIRS[@]}"; do
  [ ! -f "$dir/.gitkeep" ] && touch "$dir/.gitkeep"
done

# --- Verify key files ---
echo ""
echo "Checking key files..."

KEY_FILES=(
  CLAUDE.md TESTING.md README.md .env.example
  requirements.txt package.json pytest.ini .gitignore
  watchers/repos.yaml
  registry/content-sources.yaml registry/ohanafy-repos.yaml
  knowledge-base/beverage-supply-chain/glossary.md
  agents/_template/agent.py agents/_template/tools.py agents/_template/config.yaml
  skills/_template/SKILL.md skills/_template/skill.py skills/_template/schema.py
  skills/content-watcher/SKILL.md
  ci-cd/scripts/discover-repos.py
  tests/conftest.py
)

MISSING=0
for f in "${KEY_FILES[@]}"; do
  if [ -f "$f" ]; then
    echo "  ✓ $f"
  else
    echo "  ✗ $f (MISSING)"
    MISSING=$((MISSING + 1))
  fi
done

# --- Pipelines ---
echo ""
echo "Checking CI/CD pipelines..."
for p in main.yml pr.yml staging.yml sf-deploy.yml aws-deploy.yml watchers.yml content-watcher.yml; do
  if [ -f "ci-cd/pipelines/$p" ]; then
    echo "  ✓ ci-cd/pipelines/$p"
  else
    echo "  ✗ ci-cd/pipelines/$p (MISSING)"
    MISSING=$((MISSING + 1))
  fi
done

echo ""
if [ "$MISSING" -eq 0 ]; then
  echo "✓ Bootstrap complete. All files present."
else
  echo "⚠ Bootstrap complete with $MISSING missing files."
  echo "  Run the scaffold again or create missing files manually."
fi

echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and fill in credentials"
echo "  2. Run: python ci-cd/scripts/discover-repos.py"
echo "  3. Export Tray workflows to skills/tray-ai/workflows/"
echo "  4. Run the onboarding interview"
