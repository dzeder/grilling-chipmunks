#!/usr/bin/env bash
# Context hierarchy validation script
# Checks CLAUDE.md size, broken links, staleness, and structure
# Exit non-zero if critical issues found (for CI integration)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0
WARNINGS=0

red() { printf '\033[0;31m%s\033[0m\n' "$1"; }
yellow() { printf '\033[0;33m%s\033[0m\n' "$1"; }
green() { printf '\033[0;32m%s\033[0m\n' "$1"; }
blue() { printf '\033[0;34m%s\033[0m\n' "$1"; }

echo "=== Context Hierarchy Validation ==="
echo "Repo: $REPO_ROOT"
echo ""

# 1. CLAUDE.md line count
echo "--- Entry Point ---"
CLAUDE_LINES=$(wc -l < "$REPO_ROOT/CLAUDE.md" 2>/dev/null || echo 0)
if [ "$CLAUDE_LINES" -gt 200 ]; then
  red "FAIL: CLAUDE.md is $CLAUDE_LINES lines (max 200)"
  ERRORS=$((ERRORS + 1))
elif [ "$CLAUDE_LINES" -gt 150 ]; then
  yellow "WARN: CLAUDE.md is $CLAUDE_LINES lines (target <150)"
  WARNINGS=$((WARNINGS + 1))
else
  green "PASS: CLAUDE.md is $CLAUDE_LINES lines"
fi

# 2. Subdirectory CLAUDE.md files
echo ""
echo "--- Progressive Disclosure ---"
SUBDIR_COUNT=$(find "$REPO_ROOT" -name "CLAUDE.md" -not -path "$REPO_ROOT/CLAUDE.md" -not -path "*/node_modules/*" | wc -l | tr -d ' ')
if [ "$SUBDIR_COUNT" -lt 3 ]; then
  red "FAIL: Only $SUBDIR_COUNT subdirectory CLAUDE.md files (need 3+)"
  ERRORS=$((ERRORS + 1))
else
  green "PASS: $SUBDIR_COUNT subdirectory CLAUDE.md files"
fi

# Check for rules directory
if [ -d "$REPO_ROOT/.claude/rules" ]; then
  RULES_COUNT=$(find "$REPO_ROOT/.claude/rules" -name "*.md" | wc -l | tr -d ' ')
  green "PASS: .claude/rules/ exists with $RULES_COUNT rule files"
else
  red "FAIL: No .claude/rules/ directory"
  ERRORS=$((ERRORS + 1))
fi

# Check for docs index
if [ -f "$REPO_ROOT/docs/README.md" ] || [ -f "$REPO_ROOT/docs/index.md" ]; then
  green "PASS: docs/ has an index file"
else
  yellow "WARN: No docs/README.md or docs/index.md"
  WARNINGS=$((WARNINGS + 1))
fi

# 3. Key index files
echo ""
echo "--- Index Files ---"
for INDEX_FILE in "agents/README.md" "docs/SKILL_CATALOG.md" "integrations/CLAUDE.md" "references/README.md"; do
  if [ -f "$REPO_ROOT/$INDEX_FILE" ]; then
    green "PASS: $INDEX_FILE exists"
  else
    yellow "WARN: Missing $INDEX_FILE"
    WARNINGS=$((WARNINGS + 1))
  fi
done

# 4. Settings security
echo ""
echo "--- Security ---"
if grep -q "settings.local.json" "$REPO_ROOT/.gitignore" 2>/dev/null; then
  green "PASS: settings.local.json is gitignored"
else
  red "FAIL: .claude/settings.local.json is NOT gitignored"
  ERRORS=$((ERRORS + 1))
fi

# 5. Source index freshness
echo ""
echo "--- Freshness ---"
SYNCED_FILE="$REPO_ROOT/references/ohanafy-index/last-synced.txt"
if [ -f "$SYNCED_FILE" ]; then
  SYNCED_DATE=$(head -1 "$SYNCED_FILE" 2>/dev/null || echo "unknown")
  if [ "$(uname)" = "Darwin" ]; then
    SYNCED_EPOCH=$(date -j -f "%Y-%m-%d" "$SYNCED_DATE" "+%s" 2>/dev/null || echo 0)
  else
    SYNCED_EPOCH=$(date -d "$SYNCED_DATE" "+%s" 2>/dev/null || echo 0)
  fi
  NOW_EPOCH=$(date "+%s")
  DAYS_OLD=$(( (NOW_EPOCH - SYNCED_EPOCH) / 86400 ))
  if [ "$DAYS_OLD" -gt 7 ]; then
    yellow "WARN: Source indexes are $DAYS_OLD days old (last: $SYNCED_DATE)"
    WARNINGS=$((WARNINGS + 1))
  else
    green "PASS: Source indexes synced $DAYS_OLD days ago ($SYNCED_DATE)"
  fi
else
  yellow "WARN: No last-synced.txt found"
  WARNINGS=$((WARNINGS + 1))
fi

# 6. Summary
echo ""
echo "=== Summary ==="
if [ "$ERRORS" -gt 0 ]; then
  red "$ERRORS errors, $WARNINGS warnings"
  exit 1
else
  if [ "$WARNINGS" -gt 0 ]; then
    yellow "0 errors, $WARNINGS warnings"
  else
    green "All checks passed!"
  fi
  exit 0
fi
