#!/bin/bash
set -euo pipefail

# update-gstack.sh — Pull latest gstack from upstream and show what changed
# Usage:
#   bash scripts/update-gstack.sh              # preview changes (dry run)
#   bash scripts/update-gstack.sh --apply      # apply the update

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GSTACK_DIR="${REPO_ROOT}/.claude/skills/gstack"
TMP_DIR="/tmp/gstack-upstream-$$"
MODE="${1:---preview}"

echo "Fetching latest gstack from garrytan/gstack..."
gh repo clone garrytan/gstack "$TMP_DIR" -- --depth 1 2>/dev/null
UPSTREAM_VERSION=$(cat "$TMP_DIR/VERSION" 2>/dev/null || echo "unknown")
LOCAL_VERSION=$(cat "$GSTACK_DIR/VERSION" 2>/dev/null || echo "unknown")

echo ""
echo "Local version:    ${LOCAL_VERSION}"
echo "Upstream version: ${UPSTREAM_VERSION}"
echo ""

if [ "$LOCAL_VERSION" = "$UPSTREAM_VERSION" ]; then
  echo "Already up to date."
  rm -rf "$TMP_DIR"
  exit 0
fi

# Remove .git and compiled binaries from upstream before comparing
rm -rf "$TMP_DIR/.git"
rm -f "$TMP_DIR/bin/gstack-global-discover" 2>/dev/null

# Show what changed
echo "Changes from ${LOCAL_VERSION} -> ${UPSTREAM_VERSION}:"
echo "=================================================="
echo ""

# Diff the directories (excluding binaries and .git)
DIFF_OUTPUT=$(diff -rq "$GSTACK_DIR" "$TMP_DIR" \
  --exclude='.git' \
  --exclude='dist' \
  --exclude='node_modules' \
  --exclude='gstack-global-discover' \
  --exclude='.DS_Store' \
  2>/dev/null || true)

if [ -z "$DIFF_OUTPUT" ]; then
  echo "No file differences found (versions differ but content is the same)."
  rm -rf "$TMP_DIR"
  exit 0
fi

# Categorize changes
NEW_FILES=$(echo "$DIFF_OUTPUT" | grep "Only in $TMP_DIR" | sed "s|Only in $TMP_DIR|  + |; s|: |/|" || true)
REMOVED_FILES=$(echo "$DIFF_OUTPUT" | grep "Only in $GSTACK_DIR" | sed "s|Only in $GSTACK_DIR|  - |; s|: |/|" || true)
CHANGED_FILES=$(echo "$DIFF_OUTPUT" | grep "^Files.*differ$" | sed 's|Files ||; s| and .*| |; s|'"$GSTACK_DIR/"'|  ~ |' || true)

if [ -n "$NEW_FILES" ]; then
  echo "New files upstream:"
  echo "$NEW_FILES"
  echo ""
fi

if [ -n "$REMOVED_FILES" ]; then
  echo "Files removed upstream (you have, they don't):"
  echo "$REMOVED_FILES"
  echo ""
fi

if [ -n "$CHANGED_FILES" ]; then
  echo "Modified files:"
  echo "$CHANGED_FILES"
  echo ""
fi

# Show CHANGELOG diff if it exists
if [ -f "$TMP_DIR/CHANGELOG.md" ] && [ -f "$GSTACK_DIR/CHANGELOG.md" ]; then
  echo "Changelog updates:"
  echo "------------------"
  diff "$GSTACK_DIR/CHANGELOG.md" "$TMP_DIR/CHANGELOG.md" | head -40 || true
  echo ""
fi

if [ "$MODE" = "--apply" ]; then
  echo "Applying update..."
  
  # Backup current version
  BACKUP_DIR="/tmp/gstack-backup-${LOCAL_VERSION}-$$"
  cp -R "$GSTACK_DIR" "$BACKUP_DIR"
  echo "  Backed up current version to: ${BACKUP_DIR}"
  
  # Copy upstream over local (preserving any local-only files)
  rsync -av --delete \
    --exclude='.git' \
    --exclude='dist/' \
    --exclude='node_modules/' \
    --exclude='gstack-global-discover' \
    "$TMP_DIR/" "$GSTACK_DIR/"
  
  echo ""
  echo "Updated to ${UPSTREAM_VERSION}."
  echo "Backup at: ${BACKUP_DIR}"
  echo ""
  echo "Next steps:"
  echo "  1. Review changes: git diff .claude/skills/gstack/"
  echo "  2. Rebuild browser: cd .claude/skills/gstack && ./setup"
  echo "  3. Commit: git add .claude/skills/gstack && git commit -m 'chore: update gstack to ${UPSTREAM_VERSION}'"
else
  echo "This was a preview. To apply the update, run:"
  echo "  bash scripts/update-gstack.sh --apply"
fi

rm -rf "$TMP_DIR"
