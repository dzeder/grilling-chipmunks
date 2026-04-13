#!/usr/bin/env bash
#
# purge-vip-data.sh — Delete all VIP SRS integration test data from a Salesforce org.
#
# Dry-run by default. Pass --execute to actually delete records.
# Deletes in reverse dependency order (children before parents).
#
# Usage:
#   bash purge-vip-data.sh                                    # dry-run, default org
#   bash purge-vip-data.sh --execute                          # delete from default org
#   bash purge-vip-data.sh --target-org my-sandbox            # dry-run, custom org
#   bash purge-vip-data.sh --dist-id FL01 --execute           # delete only FL01 records
#   bash purge-vip-data.sh --include-references --execute     # also delete Item_Line/Item_Type
#   bash purge-vip-data.sh --config config/gulf.json          # use a different customer config

set -euo pipefail

# =============================================================================
# DEFAULTS
# =============================================================================

TARGET_ORG="shipyard-ros2-sandbox"
DIST_ID=""
EXECUTE=false
INCLUDE_REFS=false
CONFIG_FILE=""

# =============================================================================
# PARSE ARGS
# =============================================================================

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-org)   TARGET_ORG="$2"; shift 2 ;;
    --dist-id)      DIST_ID="$2"; shift 2 ;;
    --config)       CONFIG_FILE="$2"; shift 2 ;;
    --execute)      EXECUTE=true; shift ;;
    --include-references) INCLUDE_REFS=true; shift ;;
    -h|--help)
      echo "Usage: bash purge-vip-data.sh [--config FILE] [--target-org ORG] [--dist-id ID] [--include-references] [--execute]"
      echo ""
      echo "  --config FILE            Customer config JSON (default: config/shipyard.json)"
      echo "  --target-org ORG         Salesforce org alias (overrides config)"
      echo "  --dist-id ID             Filter by distributor ID (overrides config)"
      echo "  --include-references     Also delete Item_Line__c and Item_Type__c (shared reference data)"
      echo "  --execute                Actually delete records. Without this, dry-run only."
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# =============================================================================
# LOAD CONFIG (if --config or default exists, CLI args override)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CONFIG="${SCRIPT_DIR}/../config/shipyard.json"

if [[ -n "$CONFIG_FILE" ]]; then
  # Resolve relative paths
  [[ "$CONFIG_FILE" != /* ]] && CONFIG_FILE="$(pwd)/$CONFIG_FILE"
  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
  fi
elif [[ -f "$DEFAULT_CONFIG" ]]; then
  CONFIG_FILE="$DEFAULT_CONFIG"
fi

if [[ -n "$CONFIG_FILE" ]]; then
  # Extract values from JSON using node (available since we're in a Node project)
  _cfg_org=$(node -e "var c=require('$CONFIG_FILE'); console.log((c.salesforce||{}).orgAlias||'')" 2>/dev/null || true)
  _cfg_dist=$(node -e "var c=require('$CONFIG_FILE'); console.log(c.targetDistributorId||'')" 2>/dev/null || true)
  # Config provides defaults — only apply if CLI didn't set them explicitly
  # We detect "CLI didn't set" by checking if the value is still the hardcoded default
  if [[ "$TARGET_ORG" == "shipyard-ros2-sandbox" && -n "$_cfg_org" ]]; then
    TARGET_ORG="$_cfg_org"
  fi
  if [[ -z "$DIST_ID" && -n "$_cfg_dist" ]]; then
    DIST_ID="$_cfg_dist"
  fi
fi

# =============================================================================
# HELPERS
# =============================================================================

TOTAL_FOUND=0
TOTAL_DELETED=0

query_ids() {
  local sobject="$1"
  local where_clause="$2"
  local soql="SELECT Id FROM ${sobject} WHERE ${where_clause}"

  # Query and extract only 18-char Salesforce IDs from CSV output
  sf data query \
    --target-org "$TARGET_ORG" \
    --query "$soql" \
    --result-format csv \
    2>/dev/null | grep -E '^[a-zA-Z0-9]{15,18}$' || true
}

delete_records() {
  local sobject="$1"
  local label="$2"
  local where_clause="$3"

  echo "--- ${label} (${sobject}) ---"

  local ids
  ids=$(query_ids "$sobject" "$where_clause")
  local count=0
  if [[ -n "$ids" ]]; then
    count=$(echo "$ids" | wc -l | tr -d ' ')
  fi

  if [[ "$count" -eq 0 ]]; then
    echo "  Found: 0 records. Skipping."
    echo ""
    return
  fi

  echo "  Found: ${count} records"
  TOTAL_FOUND=$((TOTAL_FOUND + count))

  if [[ "$EXECUTE" == "false" ]]; then
    echo "  [DRY RUN] Would delete ${count} records."
    echo ""
    return
  fi

  # Write IDs to a temp CSV for bulk delete
  local tmpfile
  tmpfile=$(mktemp /tmp/vip-purge-XXXXXX.csv)
  echo "Id" > "$tmpfile"
  echo "$ids" >> "$tmpfile"

  if [[ "$count" -le 200 ]]; then
    # Small count — delete record by record via sf data delete record
    local deleted=0
    while IFS= read -r id; do
      [[ -z "$id" ]] && continue
      if sf data delete record \
        --target-org "$TARGET_ORG" \
        --sobject "$sobject" \
        --record-id "$id" 2>/dev/null; then
        deleted=$((deleted + 1))
      else
        echo "  WARN: Failed to delete ${sobject} ${id}"
      fi
    done <<< "$ids"
    echo "  Deleted: ${deleted}/${count}"
    TOTAL_DELETED=$((TOTAL_DELETED + deleted))
  else
    # Large count — use bulk delete
    echo "  Using bulk delete for ${count} records..."
    if sf data delete bulk \
      --target-org "$TARGET_ORG" \
      --sobject "$sobject" \
      --file "$tmpfile" \
      --wait 10 2>/dev/null; then
      echo "  Deleted: ${count} (bulk)"
      TOTAL_DELETED=$((TOTAL_DELETED + count))
    else
      echo "  ERROR: Bulk delete failed for ${sobject}"
    fi
  fi

  rm -f "$tmpfile"
  echo ""
}

# =============================================================================
# BANNER
# =============================================================================

echo "============================================"
echo "VIP SRS Data Purge"
echo "============================================"
echo "Target org:    ${TARGET_ORG}"
echo "Dist filter:   ${DIST_ID:-ALL}"
echo "References:    ${INCLUDE_REFS}"
echo "Mode:          $(if $EXECUTE; then echo 'EXECUTE'; else echo 'DRY RUN'; fi)"
echo "============================================"
echo ""

if [[ "$EXECUTE" == "true" ]]; then
  echo "*** WARNING: This will permanently delete records. ***"
  read -r -p "Type YES to confirm: " confirm
  if [[ "$confirm" != "YES" ]]; then
    echo "Aborted."
    exit 1
  fi
  echo ""
fi

# =============================================================================
# PHASE 1: Leaf/transaction records (no children depend on them)
# =============================================================================

echo "=== Phase 1: Transaction Records ==="
echo ""

if [[ -n "$DIST_ID" ]]; then
  delete_records "ohfy__Placement__c" "Placements (PLC:${DIST_ID})" "VIP_External_ID__c LIKE 'PLC:${DIST_ID}:%'"
  delete_records "ohfy__Depletion__c" "Depletions (DEP:${DIST_ID})" "VIP_External_ID__c LIKE 'DEP:${DIST_ID}:%'"
  delete_records "ohfy__Allocation__c" "Allocations (ALC:${DIST_ID})" "VIP_External_ID__c LIKE 'ALC:${DIST_ID}:%'"
  delete_records "ohfy__Inventory_Adjustment__c" "Inventory Adjustments (IVA:${DIST_ID})" "VIP_External_ID__c LIKE 'IVA:${DIST_ID}:%'"
  delete_records "ohfy__Inventory_History__c" "Inventory History (IVH:${DIST_ID})" "VIP_External_ID__c LIKE 'IVH:${DIST_ID}:%'"
else
  delete_records "ohfy__Placement__c" "Placements (PLC:*)" "VIP_External_ID__c LIKE 'PLC:%'"
  delete_records "ohfy__Depletion__c" "Depletions (DEP:*)" "VIP_External_ID__c LIKE 'DEP:%'"
  delete_records "ohfy__Allocation__c" "Allocations (ALC:*)" "VIP_External_ID__c LIKE 'ALC:%'"
  delete_records "ohfy__Inventory_Adjustment__c" "Inventory Adjustments (IVA:*)" "VIP_External_ID__c LIKE 'IVA:%'"
  delete_records "ohfy__Inventory_History__c" "Inventory History (IVH:*)" "VIP_External_ID__c LIKE 'IVH:%'"
fi

# =============================================================================
# PHASE 2: Mid-tier records
# =============================================================================

echo "=== Phase 2: Mid-Tier Records ==="
echo ""

if [[ -n "$DIST_ID" ]]; then
  delete_records "ohfy__Inventory__c" "Inventory (IVT:${DIST_ID})" "VIP_External_ID__c LIKE 'IVT:${DIST_ID}:%'"
  delete_records "Contact" "Contacts (CON:${DIST_ID})" "External_ID__c LIKE 'CON:${DIST_ID}:%'"
else
  delete_records "ohfy__Inventory__c" "Inventory (IVT:*)" "VIP_External_ID__c LIKE 'IVT:%'"
  delete_records "Contact" "Contacts (CON:*)" "External_ID__c LIKE 'CON:%'"
fi

# =============================================================================
# PHASE 3: Parent records
# =============================================================================

echo "=== Phase 3: Parent Records ==="
echo ""

if [[ -n "$DIST_ID" ]]; then
  delete_records "Account" "Accounts — Outlets (ACT:${DIST_ID})" "ohfy__External_ID__c LIKE 'ACT:${DIST_ID}:%'"
  # Chains are not distributor-specific, only delete if no dist filter
  echo "--- Chains (CHN:*) ---"
  echo "  Skipped: Chains are not distributor-specific. Run without --dist-id to include."
  echo ""
  delete_records "ohfy__Location__c" "Locations (LOC:${DIST_ID})" "VIP_External_ID__c LIKE 'LOC:${DIST_ID}'"
  delete_records "ohfy__Item__c" "Items (ITM:*)" "ohfy__VIP_External_ID__c LIKE 'ITM:%'"
else
  delete_records "Account" "Accounts — Outlets (ACT:*)" "ohfy__External_ID__c LIKE 'ACT:%'"
  delete_records "Account" "Accounts — Chains (CHN:*)" "ohfy__External_ID__c LIKE 'CHN:%'"
  delete_records "ohfy__Location__c" "Locations (LOC:*)" "VIP_External_ID__c LIKE 'LOC:%'"
  delete_records "ohfy__Item__c" "Items (ITM:*)" "ohfy__VIP_External_ID__c LIKE 'ITM:%'"
fi

# =============================================================================
# PHASE 4: Reference records (optional)
# =============================================================================

if [[ "$INCLUDE_REFS" == "true" ]]; then
  echo "=== Phase 4: Reference Records ==="
  echo ""
  # Item_Type and Item_Line don't have VIP external IDs — they're created by Name.
  # Delete all (they only exist because of VIP data loads in a test sandbox).
  delete_records "ohfy__Item_Type__c" "Item Types (all)" "Id != null"
  delete_records "ohfy__Item_Line__c" "Item Lines (all)" "Id != null"
else
  echo "=== Phase 4: Reference Records ==="
  echo "  Skipped: Pass --include-references to delete Item_Type__c and Item_Line__c"
  echo ""
fi

# =============================================================================
# SUMMARY
# =============================================================================

echo "============================================"
echo "Summary"
echo "============================================"
echo "Total found:   ${TOTAL_FOUND}"
if [[ "$EXECUTE" == "true" ]]; then
  echo "Total deleted: ${TOTAL_DELETED}"
else
  echo "Mode:          DRY RUN (pass --execute to delete)"
fi
echo "============================================"
