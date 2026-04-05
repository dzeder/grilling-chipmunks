#!/bin/bash
# Vendor addyosmani/agent-skills into references/agent-skills/ (read-only mirror)
# Usage:
#   bash scripts/update-agent-skills.sh              # preview changes
#   bash scripts/update-agent-skills.sh --apply       # apply update

set -euo pipefail

UPSTREAM_REPO="addyosmani/agent-skills"
LOCAL_DIR="references/agent-skills"
VERSION_FILE="${LOCAL_DIR}/VERSION"
TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/agent-skills-upstream-XXXXXX")
APPLY=false

[[ "${1:-}" == "--apply" ]] && APPLY=true

trap 'rm -rf "$TMP_DIR"' EXIT

echo "=== Agent Skills Update Check ==="
echo "    Upstream: ${UPSTREAM_REPO}"
echo ""

# Get current vendored version
if [ -f "$VERSION_FILE" ]; then
    CURRENT_HASH=$(cat "$VERSION_FILE" | tr -d '[:space:]')
    echo "Current version: ${CURRENT_HASH:0:8}"
else
    CURRENT_HASH="none"
    echo "Current version: not tracked (first sync)"
fi

# Clone upstream
echo "Fetching upstream..."
git clone --depth 50 "https://github.com/${UPSTREAM_REPO}.git" "$TMP_DIR" 2>/dev/null

UPSTREAM_HASH=$(cd "$TMP_DIR" && git log --format='%H' -1)
echo "Upstream HEAD:   ${UPSTREAM_HASH:0:8}"
echo ""

if [ "$CURRENT_HASH" == "$UPSTREAM_HASH" ]; then
    echo "Already up to date."
    exit 0
fi

# Show what changed
echo "=== Changes since last sync ==="
if [ "$CURRENT_HASH" != "none" ]; then
    (cd "$TMP_DIR" && git log --oneline "${CURRENT_HASH}..HEAD" 2>/dev/null) || echo "(hash too old or rebased — showing last 20)"
    if [ $? -ne 0 ] 2>/dev/null; then
        (cd "$TMP_DIR" && git log --oneline -20)
    fi
else
    echo "(first sync — showing last 20 commits)"
    (cd "$TMP_DIR" && git log --oneline -20)
fi
echo ""

# Show file-level changes
echo "=== Files that would change ==="
NEW_COUNT=0
CHANGED_COUNT=0

# Compare all markdown files recursively
while IFS= read -r -d '' upstream_file; do
    rel_path="${upstream_file#$TMP_DIR/}"
    local_file="${LOCAL_DIR}/${rel_path}"

    # Skip git internals and non-content files
    [[ "$rel_path" == .git* ]] && continue
    [[ "$rel_path" == node_modules* ]] && continue
    [[ "$rel_path" == VERSION ]] && continue

    if [ ! -f "$local_file" ]; then
        echo "  NEW: ${rel_path}"
        NEW_COUNT=$((NEW_COUNT + 1))
    elif ! diff -q "$local_file" "$upstream_file" > /dev/null 2>&1; then
        echo "  CHANGED: ${rel_path}"
        CHANGED_COUNT=$((CHANGED_COUNT + 1))
    fi
done < <(find "$TMP_DIR" -type f \( -name '*.md' -o -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) -print0 2>/dev/null)

echo ""
echo "  New: ${NEW_COUNT}  Changed: ${CHANGED_COUNT}"
echo ""

if ! $APPLY; then
    echo "Run with --apply to update."
    exit 0
fi

echo "=== Applying update ==="

# Backup current if it exists
if [ -d "$LOCAL_DIR" ]; then
    BACKUP_DIR="/tmp/agent-skills-backup-$(date +%Y%m%d-%H%M%S)"
    cp -r "$LOCAL_DIR" "$BACKUP_DIR"
    echo "Backed up current to $BACKUP_DIR"
fi

# Create target directory
mkdir -p "$LOCAL_DIR"

# Sync content files (markdown, yaml, json) preserving directory structure
# Exclude git internals and node_modules
rsync -av --delete \
    --include='*/' \
    --include='*.md' \
    --include='*.yaml' \
    --include='*.yml' \
    --include='*.json' \
    --include='*.txt' \
    --exclude='*' \
    --exclude='.git/' \
    --exclude='node_modules/' \
    "$TMP_DIR/" "$LOCAL_DIR/"

# Update version
echo "$UPSTREAM_HASH" > "$VERSION_FILE"

echo ""
echo "Updated to ${UPSTREAM_HASH:0:8}"
echo "Review changes with: git diff references/agent-skills/"
