#!/bin/bash
# Update vendored claude-code-best-practice from upstream
# Usage:
#   bash scripts/update-best-practices.sh              # preview changes
#   bash scripts/update-best-practices.sh --apply       # apply update

set -euo pipefail

UPSTREAM_REPO="shanraisshan/claude-code-best-practice"
LOCAL_DIR="references/claude-code-best-practices"
VERSION_FILE="${LOCAL_DIR}/VERSION"
STAGING_DIR="/tmp/ccbp-update-staging"
APPLY=false

[[ "${1:-}" == "--apply" ]] && APPLY=true

echo "=== Claude Code Best Practices Update Check ==="
echo ""

# Get current vendored version
if [ -f "$VERSION_FILE" ]; then
    CURRENT_HASH=$(cat "$VERSION_FILE" | tr -d '[:space:]')
    echo "Current version: ${CURRENT_HASH:0:8}"
else
    CURRENT_HASH="none"
    echo "Current version: not tracked"
fi

# Clone upstream
echo "Fetching upstream from $UPSTREAM_REPO..."
rm -rf "$STAGING_DIR"
git clone --depth 50 "https://github.com/${UPSTREAM_REPO}.git" "$STAGING_DIR" 2>/dev/null

UPSTREAM_HASH=$(cd "$STAGING_DIR" && git log --format='%H' -1)
echo "Upstream version: ${UPSTREAM_HASH:0:8}"
echo ""

if [ "$CURRENT_HASH" == "$UPSTREAM_HASH" ]; then
    echo "Already up to date."
    rm -rf "$STAGING_DIR"
    exit 0
fi

# Show what changed
echo "=== Changes since last sync ==="
if [ "$CURRENT_HASH" != "none" ]; then
    cd "$STAGING_DIR"
    git log --oneline "${CURRENT_HASH}..HEAD" 2>/dev/null || echo "(cannot show log — hash too old or rebased)"
    cd - > /dev/null
else
    echo "(first sync — no diff available)"
fi
echo ""

# Dirs we vendor
VENDOR_DIRS=("best-practice" "tips" "implementation" "orchestration-workflow:orchestration" "reports")
VENDOR_REPORTS=("claude-skills-for-larger-mono-repos.md" "claude-agent-memory.md" "claude-agent-command-skill.md" "claude-advanced-tool-use.md")

echo "=== Files that would change ==="
for entry in "${VENDOR_DIRS[@]}"; do
    src="${entry%%:*}"
    dst="${entry##*:}"
    [ "$src" == "$dst" ] || true
    
    if [ "$src" == "reports" ]; then
        for report in "${VENDOR_REPORTS[@]}"; do
            if [ -f "$STAGING_DIR/$src/$report" ]; then
                if [ -f "$LOCAL_DIR/$dst/$report" ]; then
                    if ! diff -q "$LOCAL_DIR/$dst/$report" "$STAGING_DIR/$src/$report" > /dev/null 2>&1; then
                        echo "  CHANGED: $dst/$report"
                    fi
                else
                    echo "  NEW: $dst/$report"
                fi
            fi
        done
    elif [ -d "$STAGING_DIR/$src" ]; then
        for f in "$STAGING_DIR/$src"/*.md; do
            fname=$(basename "$f")
            if [ -f "$LOCAL_DIR/$dst/$fname" ]; then
                if ! diff -q "$LOCAL_DIR/$dst/$fname" "$f" > /dev/null 2>&1; then
                    echo "  CHANGED: $dst/$fname"
                fi
            else
                echo "  NEW: $dst/$fname"
            fi
        done
    fi
done
echo ""

if ! $APPLY; then
    echo "Run with --apply to update."
    rm -rf "$STAGING_DIR"
    exit 0
fi

echo "=== Applying update ==="

# Backup current
BACKUP_DIR="/tmp/ccbp-backup-$(date +%Y%m%d-%H%M%S)"
cp -r "$LOCAL_DIR" "$BACKUP_DIR"
echo "Backed up current to $BACKUP_DIR"

# Copy fresh files
for entry in "${VENDOR_DIRS[@]}"; do
    src="${entry%%:*}"
    dst="${entry##*:}"
    
    if [ "$src" == "reports" ]; then
        mkdir -p "$LOCAL_DIR/$dst"
        for report in "${VENDOR_REPORTS[@]}"; do
            [ -f "$STAGING_DIR/$src/$report" ] && cp "$STAGING_DIR/$src/$report" "$LOCAL_DIR/$dst/$report"
        done
    elif [ -d "$STAGING_DIR/$src" ]; then
        mkdir -p "$LOCAL_DIR/$dst"
        cp "$STAGING_DIR/$src"/*.md "$LOCAL_DIR/$dst/"
    fi
done

# Update version
echo "$UPSTREAM_HASH" > "$VERSION_FILE"

echo ""
echo "Updated to ${UPSTREAM_HASH:0:8}"
echo "Review changes with: git diff references/claude-code-best-practices/"

rm -rf "$STAGING_DIR"
