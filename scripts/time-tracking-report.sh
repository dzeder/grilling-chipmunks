#!/bin/bash
# Generate time tracking summary from .time-tracking/log.csv
# Usage:
#   ./scripts/time-tracking-report.sh                    # Full summary
#   ./scripts/time-tracking-report.sh --milestone M0     # Filter by milestone
#   ./scripts/time-tracking-report.sh --type feature     # Filter by type
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV="$(dirname "$SCRIPT_DIR")/.time-tracking/log.csv"

if [ ! -f "$CSV" ]; then
  echo "Error: $CSV not found"
  exit 1
fi

LINES=$(tail -n +2 "$CSV" | grep -vc '^$' || true)

if [ "$LINES" -eq 0 ]; then
  echo "No time tracking entries yet."
  echo "Add entries to .time-tracking/log.csv to see reports."
  exit 0
fi

# Parse args
FILTER=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --milestone) FILTER="$2"; shift 2 ;;
    --type) FILTER="$2"; shift 2 ;;
    *) shift ;;
  esac
done

echo "=== Time Tracking Report ==="
echo ""

if [ -n "$FILTER" ]; then
  DATA=$(tail -n +2 "$CSV" | grep -i "$FILTER" || true)
  echo "Filter: $FILTER"
else
  DATA=$(tail -n +2 "$CSV")
fi

if [ -z "$DATA" ]; then
  echo "No entries match filter."
  exit 0
fi

# CSV columns (1-indexed):
# 1=date, 2=pr_number, 3=branch, 4=description, 5=type,
# 6=human_estimate_hrs, 7=ai_actual_min, 8=tokens_used, 9=est_cost_usd, 10=time_saved_pct,
# 11=files_changed, 12=files_added, 13=files_deleted, 14=lines_added, 15=lines_deleted,
# 16=skills_used, 17=agents_used

TOTAL_HUMAN=$(echo "$DATA" | awk -F',' '{sum += $6} END {printf "%.1f", sum}')
TOTAL_AI_MIN=$(echo "$DATA" | awk -F',' '{sum += $7} END {printf "%.0f", sum}')
TOTAL_AI_HRS=$(echo "$DATA" | awk -F',' '{sum += $7/60} END {printf "%.1f", sum}')
TOTAL_TOKENS=$(echo "$DATA" | awk -F',' '{sum += $8} END {printf "%.0f", sum}')
TOTAL_COST=$(echo "$DATA" | awk -F',' '{sum += $9} END {printf "%.2f", sum}')
TOTAL_LINES_ADDED=$(echo "$DATA" | awk -F',' '{sum += $14} END {printf "%.0f", sum}')
TOTAL_LINES_DELETED=$(echo "$DATA" | awk -F',' '{sum += $15} END {printf "%.0f", sum}')
ENTRIES=$(echo "$DATA" | wc -l | tr -d ' ')

if [ "$(echo "$TOTAL_HUMAN > 0" | bc)" -eq 1 ]; then
  SAVINGS=$(echo "scale=1; (1 - $TOTAL_AI_HRS / $TOTAL_HUMAN) * 100" | bc)
else
  SAVINGS="N/A"
fi

echo "Entries:            $ENTRIES"
echo "Human Estimate:     ${TOTAL_HUMAN}h"
echo "AI Actual:          ${TOTAL_AI_MIN}min (${TOTAL_AI_HRS}h)"
echo "Time Saved:         ${SAVINGS}%"
echo "Tokens Used:        $TOTAL_TOKENS"
echo "Est. Cost:          \$$TOTAL_COST"
echo "Lines:              +$TOTAL_LINES_ADDED / -$TOTAL_LINES_DELETED"
echo ""
echo "--- Details ---"
echo "$DATA" | awk -F',' '{printf "#%-4s %-45s %5sh human / %4smin AI  +%s/-%s lines  skills: %s\n", $2, $4, $6, $7, $14, $15, $16}'
