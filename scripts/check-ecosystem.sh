#!/bin/bash
# Check high-value Claude Code ecosystem repos for changes worth reviewing
# Usage:
#   bash scripts/check-ecosystem.sh              # show digest
#   bash scripts/check-ecosystem.sh --json       # output as JSON (for CI)

set -euo pipefail

JSON=false
[[ "${1:-}" == "--json" ]] && JSON=true

MARKER_DIR="references/ecosystem-watch"
STAGING_DIR="/tmp/ecosystem-check-staging"
mkdir -p "$MARKER_DIR"

# Repos worth monitoring and why
# 1. anthropics/claude-code — official harness (hooks, features, CLI changes)
# 2. hesreallyhim/awesome-claude-code — curated community patterns
REPOS=(
    "anthropics/claude-code|Claude Code CLI (official harness)"
    "hesreallyhim/awesome-claude-code|Community patterns and plugins"
)

echo "=== Cheyenne Ecosystem Watch ==="
echo "Checking ${#REPOS[@]} upstream sources for changes..."
echo ""

CHANGES_FOUND=false
DIGEST=""

for entry in "${REPOS[@]}"; do
    REPO="${entry%%|*}"
    LABEL="${entry##*|}"
    SAFE_NAME=$(echo "$REPO" | tr '/' '-')
    MARKER_FILE="${MARKER_DIR}/${SAFE_NAME}.last-checked"

    # Get last-checked hash
    if [ -f "$MARKER_FILE" ]; then
        LAST_HASH=$(cat "$MARKER_FILE" | tr -d '[:space:]')
    else
        LAST_HASH="none"
    fi

    # Get current upstream HEAD
    UPSTREAM_HASH=$(git ls-remote "https://github.com/${REPO}.git" HEAD 2>/dev/null | cut -f1 || echo "unreachable")

    if [ "$UPSTREAM_HASH" == "unreachable" ]; then
        echo "  SKIP: ${REPO} — could not reach upstream"
        continue
    fi

    if [ "$LAST_HASH" == "$UPSTREAM_HASH" ]; then
        echo "  OK: ${REPO} — no changes since last check"
        continue
    fi

    CHANGES_FOUND=true
    echo "  NEW: ${REPO} — changes detected"

    # Clone shallow to get commit log
    CLONE_DIR="${STAGING_DIR}/${SAFE_NAME}"
    rm -rf "$CLONE_DIR"
    git clone --depth 30 "https://github.com/${REPO}.git" "$CLONE_DIR" 2>/dev/null

    # Get recent commits (since last check, or last 10 if first run)
    if [ "$LAST_HASH" != "none" ]; then
        COMMIT_LOG=$(cd "$CLONE_DIR" && git log --oneline "${LAST_HASH}..HEAD" 2>/dev/null || echo "(hash too old — showing last 10)")
        if [ "$COMMIT_LOG" == "(hash too old — showing last 10)" ]; then
            COMMIT_LOG=$(cd "$CLONE_DIR" && git log --oneline -10)
        fi
    else
        COMMIT_LOG=$(cd "$CLONE_DIR" && git log --oneline -10)
    fi

    # Build digest entry
    ENTRY="### ${LABEL} (\`${REPO}\`)

**Previous:** \`${LAST_HASH:0:8}\`
**Current:** \`${UPSTREAM_HASH:0:8}\`

Recent commits:
\`\`\`
${COMMIT_LOG}
\`\`\`
"
    DIGEST="${DIGEST}${ENTRY}
"

    # Update marker
    echo "$UPSTREAM_HASH" > "$MARKER_FILE"
done

rm -rf "$STAGING_DIR"

echo ""

if ! $CHANGES_FOUND; then
    echo "No ecosystem changes detected. All quiet."
    exit 0
fi

echo "=== Digest ==="
echo ""
echo "$DIGEST"

if $JSON; then
    # Output JSON for CI consumption
    ESCAPED_DIGEST=$(echo "$DIGEST" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
    echo ""
    echo "::set-output name=digest::${ESCAPED_DIGEST}"
    echo "::set-output name=has_changes::true"
fi
