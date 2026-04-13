#!/bin/bash
# Harvest PR telemetry from local gstack timeline + git diff
# Usage:
#   ./scripts/pr-telemetry-harvest.sh              # Human-readable
#   ./scripts/pr-telemetry-harvest.sh --json        # JSON output
#   ./scripts/pr-telemetry-harvest.sh --branch NAME # Override branch
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
GSTACK_HOME="${GSTACK_HOME:-$HOME/.gstack}"
FORMAT="text"
BRANCH_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) FORMAT="json"; shift ;;
    --branch) BRANCH_OVERRIDE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Resolve slug and branch (same logic as gstack-slug)
cd "$REPO_DIR"
SLUG_BIN="$REPO_DIR/.claude/skills/gstack/bin/gstack-slug"
if [ -f "$SLUG_BIN" ]; then
  eval "$("$SLUG_BIN" 2>/dev/null)" 2>/dev/null || true
fi
SLUG="${SLUG:-$(basename "$REPO_DIR" | tr -cd 'a-zA-Z0-9._-')}"
# Use raw branch name (with slashes) for timeline matching — gstack-slug sanitizes
# it but timeline.jsonl stores the original git branch name
RAW_BRANCH="${BRANCH_OVERRIDE:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')}"
BRANCH="$RAW_BRANCH"

# --- Git diff stats ---
BASE=$(git rev-parse --verify origin/main 2>/dev/null || git rev-parse --verify main 2>/dev/null || echo "")
if [ -n "$BASE" ]; then
  SHORTSTAT=$(git diff --shortstat "${BASE}...HEAD" 2>/dev/null || echo "")
  FILES_CHANGED=$(echo "$SHORTSTAT" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo "0")
  INSERTIONS=$(echo "$SHORTSTAT" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
  DELETIONS=$(echo "$SHORTSTAT" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo "0")
  FILES_ADDED=$(git diff --diff-filter=A --name-only "${BASE}...HEAD" 2>/dev/null | wc -l | tr -d ' ')
  FILES_MODIFIED=$(git diff --diff-filter=M --name-only "${BASE}...HEAD" 2>/dev/null | wc -l | tr -d ' ')
  FILES_DELETED=$(git diff --diff-filter=D --name-only "${BASE}...HEAD" 2>/dev/null | wc -l | tr -d ' ')
else
  FILES_CHANGED=0; INSERTIONS=0; DELETIONS=0; FILES_ADDED=0; FILES_MODIFIED=0; FILES_DELETED=0
fi
NET_LOC=$((INSERTIONS - DELETIONS))

# --- gstack timeline data ---
TIMELINE_FILE="$GSTACK_HOME/projects/$SLUG/timeline.jsonl"
SKILLS_USED=""
TOTAL_DURATION_S=0
SESSION_COUNT=0
FIRST_TS=""
LAST_TS=""

if [ -f "$TIMELINE_FILE" ]; then
  # Extract branch-specific completed events
  BRANCH_DATA=$(grep "\"branch\":\"${BRANCH}\"" "$TIMELINE_FILE" 2>/dev/null | grep '"event":"completed"' || true)

  if [ -n "$BRANCH_DATA" ]; then
    # Unique skills
    SKILLS_USED=$(echo "$BRANCH_DATA" | grep -o '"skill":"[^"]*"' | sed 's/"skill":"//;s/"//' | sort -u | tr '\n' ', ' | sed 's/,$//')

    # Total duration
    TOTAL_DURATION_S=$(echo "$BRANCH_DATA" | grep -o '"duration_s":[0-9.]*' | sed 's/"duration_s"://' | awk '{sum+=$1} END {printf "%.0f", sum}')

    # Session count
    SESSION_COUNT=$(echo "$BRANCH_DATA" | grep -o '"session":"[^"]*"' | sort -u | wc -l | tr -d ' ')

    # First and last timestamps (from all branch events, not just completed)
    ALL_BRANCH=$(grep "\"branch\":\"${BRANCH}\"" "$TIMELINE_FILE" 2>/dev/null || true)
    FIRST_TS=$(echo "$ALL_BRANCH" | grep -o '"ts":"[^"]*"' | head -1 | sed 's/"ts":"//;s/"//')
    LAST_TS=$(echo "$ALL_BRANCH" | grep -o '"ts":"[^"]*"' | tail -1 | sed 's/"ts":"//;s/"//')
  fi
fi

AI_ACTUAL_MIN=$((TOTAL_DURATION_S / 60))

# --- Output ---
if [ "$FORMAT" = "json" ]; then
  cat <<EOF
{
  "branch": "$BRANCH",
  "diff": {
    "files_changed": $FILES_CHANGED,
    "files_added": $FILES_ADDED,
    "files_modified": $FILES_MODIFIED,
    "files_deleted": $FILES_DELETED,
    "lines_added": $INSERTIONS,
    "lines_deleted": $DELETIONS,
    "net_loc": $NET_LOC
  },
  "timing": {
    "first_event_ts": "$FIRST_TS",
    "last_event_ts": "$LAST_TS",
    "total_skill_duration_s": $TOTAL_DURATION_S,
    "ai_actual_min": $AI_ACTUAL_MIN,
    "session_count": $SESSION_COUNT
  },
  "skills_used": "$SKILLS_USED",
  "agents_used": ""
}
EOF
else
  echo "=== PR Telemetry: $BRANCH ==="
  echo ""
  echo "--- Diff Stats ---"
  echo "Files Changed:    $FILES_CHANGED ($FILES_ADDED added, $FILES_MODIFIED modified, $FILES_DELETED deleted)"
  echo "Lines Added:      +$INSERTIONS"
  echo "Lines Deleted:    -$DELETIONS"
  echo "Net LOC:          $NET_LOC"
  echo ""
  echo "--- AI Session ---"
  if [ -n "$SKILLS_USED" ]; then
    echo "Skills Used:      $SKILLS_USED"
    echo "AI Actual:        ${AI_ACTUAL_MIN} min (${TOTAL_DURATION_S}s total skill time)"
    echo "Sessions:         $SESSION_COUNT"
    [ -n "$FIRST_TS" ] && echo "First Activity:   $FIRST_TS"
    [ -n "$LAST_TS" ] && echo "Last Activity:    $LAST_TS"
  else
    echo "No gstack timeline data found for branch '$BRANCH'"
    echo "(Timeline file: $TIMELINE_FILE)"
  fi
fi
