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

TOTAL_HUMAN=$(echo "$DATA" | awk -F',' '{sum += $5} END {printf "%.1f", sum}')
TOTAL_AI=$(echo "$DATA" | awk -F',' '{sum += $6} END {printf "%.1f", sum}')
ENTRIES=$(echo "$DATA" | wc -l | tr -d ' ')

if [ "$(echo "$TOTAL_HUMAN > 0" | bc)" -eq 1 ]; then
  SAVINGS=$(echo "scale=1; (1 - $TOTAL_AI / $TOTAL_HUMAN) * 100" | bc)
else
  SAVINGS="N/A"
fi

echo "Entries:            $ENTRIES"
echo "Human Estimate:     ${TOTAL_HUMAN}h"
echo "AI Actual:          ${TOTAL_AI}h"
echo "Time Saved:         ${SAVINGS}%"
echo ""
echo "--- Details ---"
echo "$DATA" | awk -F',' '{printf "#%-4s %-40s %6sh human / %6sh AI (%s%%)\n", $2, $3, $5, $6, $7}'
