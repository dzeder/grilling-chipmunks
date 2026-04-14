#!/bin/bash
# Inject local telemetry data into an open PR's body.
# Only fills fields that are currently empty — never overwrites agent-provided values.
#
# Usage:
#   ./scripts/pr-telemetry-inject.sh          # inject into current branch's PR
#   ./scripts/pr-telemetry-inject.sh --dry-run # show what would change without updating
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    *) shift ;;
  esac
done

# Verify gh CLI is available and a PR exists
if ! command -v gh &>/dev/null; then
  echo "gh CLI not found — skipping telemetry injection" >&2
  exit 0
fi

PR_BODY=$(gh pr view --json body -q .body 2>/dev/null || echo "")
if [ -z "$PR_BODY" ]; then
  echo "No open PR found for this branch — skipping telemetry injection" >&2
  exit 0
fi

if ! echo "$PR_BODY" | grep -qi "AI Telemetry"; then
  echo "PR body has no AI Telemetry section — skipping" >&2
  exit 0
fi

# Harvest telemetry data
HARVEST_JSON=$("$SCRIPT_DIR/pr-telemetry-harvest.sh" --json 2>/dev/null || echo "{}")

# Extract values from JSON (portable: no jq dependency)
extract() {
  local key="$1"
  echo "$HARVEST_JSON" | grep -o "\"${key}\": *[^,}]*" | sed 's/.*: *//;s/"//g;s/ *$//' || echo ""
}

FILES_CHANGED=$(extract "files_changed")
FILES_ADDED=$(extract "files_added")
FILES_DELETED=$(extract "files_deleted")
LINES_ADDED=$(extract "lines_added")
LINES_DELETED=$(extract "lines_deleted")
SKILLS_USED=$(extract "skills_used")
AI_ACTUAL_MIN=$(extract "ai_actual_min")

# Fill a telemetry field only if the value cell is empty/whitespace.
# Matches: "| Field Name | |" or "| Field Name |   |"
fill_if_empty() {
  local field_name="$1"
  local value="$2"
  [ -z "$value" ] && return
  # Use perl for reliable regex — sed varies across macOS/Linux
  PR_BODY=$(echo "$PR_BODY" | perl -pe "
    s/(\|\s*\Q${field_name}\E\s*\|)\s*\|/\$1 ${value} |/i
  ")
}

ORIGINAL_BODY="$PR_BODY"

fill_if_empty "Files Changed / Added / Deleted" "${FILES_CHANGED} (${FILES_ADDED} added, ${FILES_DELETED} deleted)"
fill_if_empty "Lines Added / Deleted" "+${LINES_ADDED} / -${LINES_DELETED}"

if [ -n "$SKILLS_USED" ]; then
  fill_if_empty "Skills Used" "$SKILLS_USED"
fi

if [ -n "$AI_ACTUAL_MIN" ] && [ "$AI_ACTUAL_MIN" != "0" ]; then
  fill_if_empty "AI Actual (min)" "$AI_ACTUAL_MIN"
fi

if [ "$PR_BODY" = "$ORIGINAL_BODY" ]; then
  echo "No empty telemetry fields to fill — PR body already populated" >&2
  exit 0
fi

if [ "$DRY_RUN" = true ]; then
  echo "=== Dry Run: Would inject these values ==="
  echo "Files Changed / Added / Deleted: ${FILES_CHANGED} (${FILES_ADDED} added, ${FILES_DELETED} deleted)"
  echo "Lines Added / Deleted: +${LINES_ADDED} / -${LINES_DELETED}"
  [ -n "$SKILLS_USED" ] && echo "Skills Used: $SKILLS_USED"
  [ -n "$AI_ACTUAL_MIN" ] && [ "$AI_ACTUAL_MIN" != "0" ] && echo "AI Actual (min): $AI_ACTUAL_MIN"
  exit 0
fi

# Update PR body
gh pr edit --body "$PR_BODY"
echo "Telemetry fields injected into PR body"
