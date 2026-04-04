#!/bin/bash
set -euo pipefail

# sync-ohanafy-index.sh — Build source indexes for Ohanafy SKU repos
#
# Clones each OHFY-* repo (shallow), extracts a structured markdown index
# of classes, triggers, methods, fields, and LWC components, then writes
# it to the matching skill's references/ directory.
#
# Designed to be run by agents when they need fresh data — not on a schedule.
#
# Usage:
#   bash scripts/sync-ohanafy-index.sh                    # sync all mapped repos
#   bash scripts/sync-ohanafy-index.sh --repo OHFY-OMS    # sync single repo
#   bash scripts/sync-ohanafy-index.sh --discover          # list all org repos, flag unmapped
#   bash scripts/sync-ohanafy-index.sh --dry-run           # show what would change
#   bash scripts/sync-ohanafy-index.sh --dry-run --repo X  # preview single repo

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_BASE="/tmp/ohanafy-sync-$$"
ORG="Ohanafy"

# --- Repo → Skill mapping ---
# Using "REPO:SKILL" colon-delimited entries (bash 3.2 compatible)

PRIMARY_ENTRIES=(
  "OHFY-Core:ohfy-core-expert"
  "OHFY-Data_Model:ohfy-data-model-expert"
  "OHFY-Platform:ohfy-platform-expert"
  "OHFY-OMS:ohfy-oms-expert"
  "OHFY-WMS:ohfy-wms-expert"
  "OHFY-REX:ohfy-rex-expert"
  "OHFY-Ecom:ohfy-ecom-expert"
  "OHFY-Payments:ohfy-payments-expert"
  "OHFY-EDI:ohfy-edi-expert"
  "OHFY-Configure:ohfy-configure-expert"
)

# UI repos fold into parent skill as "## Frontend" section
UI_ENTRIES=(
  "OHFY-OMS-UI:ohfy-oms-expert"
  "OHFY-WMS-UI:ohfy-wms-expert"
  "OHFY-REX-UI:ohfy-rex-expert"
  "OHFY-PLTFM-UI:ohfy-platform-expert"
)

# Secondary repos fold into parent skill's index
SECONDARY_ENTRIES=(
  "OHFY-Service_Locator:ohfy-platform-expert"
  "OHFY-Planogram:ohfy-rex-expert"
)

# Standalone repos → references/ohanafy-index/
STANDALONE_REPOS=("OHFY-Utilities" "OHFY-CICD" "OHFY-SF-Perf" "OHFY-Workflows")

# Known repos to skip
SKIP_REPOS=("OHFY-AI" "OHFY-AI-D" "OHFY-CRMA" "OHFY-Offline" "OHFY-Integrations" "OHFY-ProdDev" "OHFY-Utility")

# --- Lookup helpers (bash 3.2 compatible) ---

lookup_primary() {
  local repo="$1"
  for entry in "${PRIMARY_ENTRIES[@]}"; do
    if [ "${entry%%:*}" = "$repo" ]; then
      echo "${entry#*:}"
      return 0
    fi
  done
  return 1
}

lookup_ui() {
  local repo="$1"
  for entry in "${UI_ENTRIES[@]}"; do
    if [ "${entry%%:*}" = "$repo" ]; then
      echo "${entry#*:}"
      return 0
    fi
  done
  return 1
}

lookup_secondary() {
  local repo="$1"
  for entry in "${SECONDARY_ENTRIES[@]}"; do
    if [ "${entry%%:*}" = "$repo" ]; then
      echo "${entry#*:}"
      return 0
    fi
  done
  return 1
}

is_in_list() {
  local needle="$1"
  shift
  for item in "$@"; do
    if [ "$item" = "$needle" ]; then
      return 0
    fi
  done
  return 1
}

is_mapped() {
  local repo="$1"
  lookup_primary "$repo" >/dev/null 2>&1 && return 0
  lookup_ui "$repo" >/dev/null 2>&1 && return 0
  lookup_secondary "$repo" >/dev/null 2>&1 && return 0
  is_in_list "$repo" "${STANDALONE_REPOS[@]}" && return 0
  return 1
}

# --- Parse args ---
MODE="sync"
TARGET_REPO=""
DRY_RUN=false

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)
      TARGET_REPO="$2"
      shift 2
      ;;
    --discover)
      MODE="discover"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: bash scripts/sync-ohanafy-index.sh [--repo REPO] [--discover] [--dry-run]"
      exit 1
      ;;
  esac
done

# --- Cleanup on exit ---
cleanup() {
  rm -rf "$TMP_BASE"
}
trap cleanup EXIT

mkdir -p "$TMP_BASE"

# --- Discover mode ---
if [ "$MODE" = "discover" ]; then
  echo "=== Ohanafy Org Repos ==="
  echo ""

  ALL_REPOS=$(gh repo list "$ORG" --limit 100 --json name,updatedAt,defaultBranchRef \
    --jq '.[] | "\(.name)\t\(.updatedAt[:10])\t\(.defaultBranchRef.name // "NO_BRANCH")"' 2>/dev/null | sort)

  mapped_count=0
  unmapped_count=0
  skipped_count=0
  non_ohfy_count=0
  mapped_lines=""
  unmapped_lines=""
  skipped_lines=""
  non_ohfy_lines=""

  while IFS="$(printf '\t')" read -r name updated branch; do
    [ -z "$name" ] && continue

    # Check if OHFY- prefix
    case "$name" in
      OHFY-*)
        ;;
      *)
        non_ohfy_count=$((non_ohfy_count + 1))
        non_ohfy_lines="${non_ohfy_lines}  ${name} (${updated})\n"
        continue
        ;;
    esac

    # Check if in skip list
    if is_in_list "$name" "${SKIP_REPOS[@]}"; then
      skipped_count=$((skipped_count + 1))
      skipped_lines="${skipped_lines}  ${name} — skipped (${updated}, branch=${branch})\n"
      continue
    fi

    # Check if mapped
    if is_mapped "$name"; then
      local_target=""
      local_target=$(lookup_primary "$name" 2>/dev/null || lookup_ui "$name" 2>/dev/null || lookup_secondary "$name" 2>/dev/null || echo "references/ohanafy-index/")
      mapped_count=$((mapped_count + 1))
      mapped_lines="${mapped_lines}  ${name} -> ${local_target} (${updated})\n"
    else
      unmapped_count=$((unmapped_count + 1))
      unmapped_lines="${unmapped_lines}  ${name} (${updated}, branch=${branch})\n"
    fi
  done <<< "$ALL_REPOS"

  echo "Mapped ($mapped_count):"
  printf '%s' "$mapped_lines"
  echo ""

  if [ "$unmapped_count" -gt 0 ]; then
    echo "Unmapped ($unmapped_count) — consider adding skills or mappings:"
    printf '%s' "$unmapped_lines"
    echo ""
  fi

  if [ "$skipped_count" -gt 0 ]; then
    echo "Skipped ($skipped_count):"
    printf '%s' "$skipped_lines"
    echo ""
  fi

  echo "Non-OHFY ($non_ohfy_count):"
  printf '%s' "$non_ohfy_lines"
  echo ""

  total=$((mapped_count + unmapped_count + skipped_count + non_ohfy_count))
  echo "Total: $total repos in org"
  exit 0
fi

# --- Extractor functions ---
# All use BSD-compatible grep/sed (no -P flag, no Perl regex)

# Extract Apex class info: name, access modifier, first Javadoc line
extract_apex_classes() {
  local src_dir="$1"
  local cls_files
  cls_files=$(find "$src_dir" -name "*.cls" -not -name "*Test*" -not -name "*Mock*" -not -name "*Stub*" 2>/dev/null | sort || true)
  local test_count
  test_count=$(find "$src_dir" -name "*.cls" \( -name "*Test*" -o -name "*Mock*" -o -name "*Stub*" \) 2>/dev/null | wc -l | tr -d ' ')
  local total_count=0
  if [ -n "$cls_files" ]; then
    total_count=$(echo "$cls_files" | wc -l | tr -d ' ')
  fi

  if [ "$total_count" = "0" ]; then
    echo "## Apex Classes"
    echo ""
    echo "_No Apex classes found._"
    echo ""
    return
  fi

  echo "## Apex Classes ($total_count production, $test_count test/mock excluded)"
  echo ""
  echo "| Class | Access | Description |"
  echo "|-------|--------|-------------|"

  echo "$cls_files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    local classname
    classname=$(basename "$f" .cls)

    # Extract access modifier
    local access="public"
    local class_line
    class_line=$(grep -m1 -E '(public|global|private)[[:space:]]' "$f" 2>/dev/null || echo "")
    case "$class_line" in
      *global*) access="global" ;;
    esac

    # Extract description from Javadoc or @description
    local desc=""
    # Try Javadoc: first line after /**
    desc=$(sed -n '/\/\*\*/,/\*\//{ /\/\*\*/d; /\*\//d; p; }' "$f" 2>/dev/null | head -1 | sed 's/^[[:space:]]*\*[[:space:]]*//' | sed 's/[|]/-/g' | head -c 80)
    # Strip @description prefix if present
    desc="${desc#@description}"
    desc="${desc#@Description}"
    desc="${desc#"${desc%%[![:space:]]*}"}"
    # Fallback: @description annotation outside Javadoc
    if [ -z "$desc" ]; then
      desc=$(grep -m1 -i '@description' "$f" 2>/dev/null | sed 's/.*@[Dd]escription[[:space:]]*//' | sed 's/[|]/-/g' | head -c 80 || true)
    fi
    # Strip trailing whitespace and colons
    desc=$(echo "$desc" | sed 's/^[[:space:]:]*//' | sed 's/[[:space:]:]*$//')

    echo "| $classname | $access | $desc |"
  done

  echo ""
}

# Extract trigger info: name, sObject, events
extract_triggers() {
  local src_dir="$1"
  local trigger_files
  trigger_files=$(find "$src_dir" -name "*.trigger" 2>/dev/null | sort || true)
  local count=0
  if [ -n "$trigger_files" ]; then
    count=$(echo "$trigger_files" | wc -l | tr -d ' ')
  fi

  if [ "$count" = "0" ]; then
    echo "## Triggers"
    echo ""
    echo "_No triggers found._"
    echo ""
    return
  fi

  echo "## Triggers ($count)"
  echo ""
  echo "| Trigger | sObject | Events |"
  echo "|---------|---------|--------|"

  echo "$trigger_files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    local trigger_line
    trigger_line=$(grep -m1 -E 'trigger[[:space:]]+[A-Za-z_]+[[:space:]]+on[[:space:]]+[A-Za-z_]' "$f" 2>/dev/null || echo "")
    if [ -n "$trigger_line" ]; then
      local tname sobject events
      tname=$(echo "$trigger_line" | sed -E 's/trigger[[:space:]]+([^ ]+)[[:space:]]+on.*/\1/')
      sobject=$(echo "$trigger_line" | sed -E 's/.*on[[:space:]]+([^ (]+).*/\1/')
      # Extract events between parentheses
      events=$(echo "$trigger_line" | sed -n 's/.*(\(.*\)).*/\1/p' | sed 's/,/, /g')
      echo "| $tname | $sobject | $events |"
    fi
  done

  echo ""
}

# Extract public/global method signatures from service classes
extract_service_methods() {
  local src_dir="$1"
  local svc_files
  svc_files=$(find "$src_dir" -name "*.cls" \( -name "*Service*" -o -name "*Svc*" -o -name "*Handler*" -o -name "*Helper*" \) \
    -not -name "*Test*" -not -name "*Mock*" 2>/dev/null | sort || true)
  local count=0
  if [ -n "$svc_files" ]; then
    count=$(echo "$svc_files" | wc -l | tr -d ' ')
  fi

  if [ "$count" = "0" ]; then
    echo "## Service Methods"
    echo ""
    echo "_No service classes found._"
    echo ""
    return
  fi

  echo "## Service Methods"
  echo ""
  echo "| Class | Method | Signature |"
  echo "|-------|--------|-----------|"

  echo "$svc_files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    local classname
    classname=$(basename "$f" .cls)

    # Extract public/global method signatures
    grep -E '^[[:space:]]*(public|global)[[:space:]]+(static[[:space:]]+)?[A-Za-z_<>]+[[:space:]]+[a-zA-Z_]+[[:space:]]*\(' "$f" 2>/dev/null | while IFS= read -r line; do
      # Extract method name
      local method_name
      method_name=$(echo "$line" | sed -E 's/.*[[:space:]]([a-zA-Z_]+)[[:space:]]*\(.*/\1/')
      # Skip constructors
      if [ "$method_name" = "$classname" ]; then
        continue
      fi
      # Clean up signature
      local sig
      sig=$(echo "$line" | sed 's/^[[:space:]]*//' | sed 's/{[[:space:]]*$//' | sed 's/[|]/-/g' | cut -c1-120)
      echo "| $classname | $method_name | \`$sig\` |"
    done
  done

  echo ""
}

# Extract custom object fields from .field-meta.xml files
extract_object_fields() {
  local src_dir="$1"
  local obj_dirs
  obj_dirs=$(find "$src_dir" -type d -name "objects" 2>/dev/null | head -1)

  if [ -z "$obj_dirs" ] || [ ! -d "$obj_dirs" ]; then
    echo "## Custom Objects & Fields"
    echo ""
    echo "_No custom objects found._"
    echo ""
    return
  fi

  echo "## Custom Objects & Fields"
  echo ""

  find "$obj_dirs" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | while read -r obj_dir; do
    local obj_name
    obj_name=$(basename "$obj_dir")
    local fields_dir="$obj_dir/fields"

    if [ ! -d "$fields_dir" ]; then
      return 0  # continue in subshell
    fi

    local field_count
    field_count=$(find "$fields_dir" -name "*.field-meta.xml" 2>/dev/null | wc -l | tr -d ' ')

    if [ "$field_count" = "0" ]; then
      return 0
    fi

    echo "### $obj_name ($field_count fields)"
    echo ""
    echo "| Field | Type | Required | Reference |"
    echo "|-------|------|----------|-----------|"

    find "$fields_dir" -name "*.field-meta.xml" 2>/dev/null | sort | while read -r field_file; do
      local field_name field_type required ref_to
      field_name=$(basename "$field_file" .field-meta.xml)
      # BSD-compatible XML value extraction
      field_type=$(sed -n 's/.*<type>\(.*\)<\/type>.*/\1/p' "$field_file" 2>/dev/null | head -1)
      required=$(sed -n 's/.*<required>\(.*\)<\/required>.*/\1/p' "$field_file" 2>/dev/null | head -1)
      ref_to=$(sed -n 's/.*<referenceTo>\(.*\)<\/referenceTo>.*/\1/p' "$field_file" 2>/dev/null | head -1)
      [ -z "$required" ] && required="false"
      echo "| $field_name | $field_type | $required | $ref_to |"
    done

    echo ""
  done
}

# Extract LWC component info from a UI repo
extract_lwc_components() {
  local src_dir="$1"
  local lwc_base
  lwc_base=$(find "$src_dir" -type d -name "lwc" 2>/dev/null | head -1)

  if [ -z "$lwc_base" ] || [ ! -d "$lwc_base" ]; then
    return
  fi

  local component_dirs
  component_dirs=$(find "$lwc_base" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort || true)
  local count=0
  if [ -n "$component_dirs" ]; then
    count=$(echo "$component_dirs" | wc -l | tr -d ' ')
  fi

  if [ "$count" = "0" ]; then
    return
  fi

  echo "## LWC Components ($count)"
  echo ""
  echo "| Component | Public API (@api) | Description |"
  echo "|-----------|-------------------|-------------|"

  echo "$component_dirs" | while IFS= read -r comp_dir; do
    [ -z "$comp_dir" ] && continue
    local comp_name
    comp_name=$(basename "$comp_dir")
    local js_file="$comp_dir/$comp_name.js"

    if [ ! -f "$js_file" ]; then
      echo "| $comp_name | | |"
      continue
    fi

    # Extract @api property names (BSD-compatible)
    local api_props
    api_props=$(grep '@api' "$js_file" 2>/dev/null | sed 's/.*@api[[:space:]]*//' | sed 's/[;=[:space:]].*//' | tr '\n' ', ' | sed 's/,$//' | sed 's/,/, /g')

    # Extract JSDoc description
    local desc=""
    desc=$(sed -n '/\/\*\*/,/\*\//{ /\/\*\*/d; /\*\//d; p; }' "$js_file" 2>/dev/null | head -1 | sed 's/^[[:space:]]*\*[[:space:]]*//' | sed 's/^@[Dd]escription[[:space:]:]*//;s/[|]/-/g' | head -c 60)

    echo "| $comp_name | $api_props | $desc |"
  done

  echo ""
}

# --- Enhanced extraction functions (Deep Knowledge Layer) ---

# Extract trigger → handler mapping: what class does each trigger call?
extract_trigger_handler_map() {
  local src_dir="$1"
  local trigger_files
  trigger_files=$(find "$src_dir" -name "*.trigger" 2>/dev/null | sort || true)
  local count=0
  if [ -n "$trigger_files" ]; then
    count=$(echo "$trigger_files" | wc -l | tr -d ' ')
  fi

  if [ "$count" = "0" ]; then
    return
  fi

  echo "## Trigger → Handler Map"
  echo ""
  echo "> **Coverage Limitations:** This map captures static patterns only (direct class"
  echo "> instantiation, method calls visible in trigger body). Dynamic dispatch, factory"
  echo "> patterns, and conditional handler resolution are not captured."
  echo ""
  echo "| Trigger | sObject | Handler Class | Call Pattern |"
  echo "|---------|---------|---------------|-------------|"

  echo "$trigger_files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    local tname sobject
    local trigger_line
    trigger_line=$(grep -m1 -E 'trigger[[:space:]]+[A-Za-z_]+[[:space:]]+on[[:space:]]+[A-Za-z_]' "$f" 2>/dev/null || echo "")
    [ -z "$trigger_line" ] && continue

    tname=$(echo "$trigger_line" | sed -E 's/trigger[[:space:]]+([^ ]+)[[:space:]]+on.*/\1/')
    sobject=$(echo "$trigger_line" | sed -E 's/.*on[[:space:]]+([^ (]+).*/\1/')

    # Look for handler class references in trigger body
    # Pattern 1: new ClassName(
    local handlers
    handlers=$(grep -oE 'new[[:space:]]+[A-Z][A-Za-z_0-9]+[[:space:]]*\(' "$f" 2>/dev/null | sed 's/new[[:space:]]*//' | sed 's/[[:space:]]*(//' | sort -u | tr '\n' ', ' | sed 's/,$//')
    local pattern="new ClassName()"
    if [ -z "$handlers" ]; then
      # Pattern 2: ClassName.methodName(
      handlers=$(grep -oE '[A-Z][A-Za-z_0-9]+\.[a-z][A-Za-z_0-9]*[[:space:]]*\(' "$f" 2>/dev/null | sed 's/[[:space:]]*(//' | sort -u | head -5 | tr '\n' ', ' | sed 's/,$//')
      pattern="Class.method()"
    fi
    if [ -z "$handlers" ]; then
      handlers="(body too complex to parse)"
      pattern="unknown"
    fi
    echo "| $tname | $sobject | $handlers | $pattern |"
  done

  echo ""
}

# Extract service layer graph: one level deep, direct calls only
extract_service_graph() {
  local src_dir="$1"
  local svc_files
  svc_files=$(find "$src_dir" -name "*.cls" \( -name "*Service*" -o -name "*Svc*" -o -name "*Handler*" \) \
    -not -name "*Test*" -not -name "*Mock*" -not -name "*Stub*" 2>/dev/null | sort || true)
  local count=0
  if [ -n "$svc_files" ]; then
    count=$(echo "$svc_files" | wc -l | tr -d ' ')
  fi

  if [ "$count" = "0" ]; then
    return
  fi

  echo "## Service Layer Graph (one level deep)"
  echo ""
  echo "> **Coverage Limitations:** Captures static patterns only: \`new *Service(\`,"
  echo "> \`ServiceLocator.getInstance(\`, \`System.enqueueJob\`. Dynamic dispatch and"
  echo "> factory patterns are not captured. Treat as a starting map, not exhaustive."
  echo ""
  echo "| Service Class | Calls / Instantiates | Pattern |"
  echo "|--------------|---------------------|---------|"

  echo "$svc_files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    local classname
    classname=$(basename "$f" .cls)

    local deps=""
    local dep_pattern=""

    # Pattern: new *Service( or new *Handler(
    local new_deps
    new_deps=$(grep -oE 'new[[:space:]]+[A-Z][A-Za-z_0-9]*(Service|Svc|Handler)[[:space:]]*\(' "$f" 2>/dev/null | sed 's/new[[:space:]]*//' | sed 's/[[:space:]]*(//' | sort -u | tr '\n' ', ' | sed 's/,$//')

    # Pattern: ServiceLocator.getInstance(
    local locator_deps
    locator_deps=$(grep -oE "ServiceLocator\.[a-zA-Z_]+\(" "$f" 2>/dev/null | sed 's/(//' | sort -u | tr '\n' ', ' | sed 's/,$//')

    # Pattern: System.enqueueJob(new ClassName
    local queue_deps
    queue_deps=$(grep -oE 'System\.enqueueJob[[:space:]]*\([[:space:]]*new[[:space:]]+[A-Z][A-Za-z_0-9]+' "$f" 2>/dev/null | sed 's/.*new[[:space:]]*//' | sort -u | tr '\n' ', ' | sed 's/,$//')

    if [ -n "$new_deps" ]; then
      deps="$new_deps"
      dep_pattern="new Instance()"
    fi
    if [ -n "$locator_deps" ]; then
      [ -n "$deps" ] && deps="$deps, "
      deps="${deps}${locator_deps}"
      dep_pattern="${dep_pattern:+$dep_pattern, }ServiceLocator"
    fi
    if [ -n "$queue_deps" ]; then
      [ -n "$deps" ] && deps="$deps, "
      deps="${deps}${queue_deps}"
      dep_pattern="${dep_pattern:+$dep_pattern, }enqueueJob"
    fi

    if [ -n "$deps" ]; then
      echo "| $classname | $deps | $dep_pattern |"
    fi
  done

  echo ""
}

# Extract cross-object relationship summary from field metadata
extract_relationship_summary() {
  local src_dir="$1"
  local obj_dirs
  obj_dirs=$(find "$src_dir" -type d -name "objects" 2>/dev/null | head -1)

  if [ -z "$obj_dirs" ] || [ ! -d "$obj_dirs" ]; then
    return
  fi

  local has_relationships=false
  local rel_lines=""

  find "$obj_dirs" -name "*.field-meta.xml" 2>/dev/null | while read -r field_file; do
    local ref_to
    ref_to=$(sed -n 's/.*<referenceTo>\(.*\)<\/referenceTo>.*/\1/p' "$field_file" 2>/dev/null | head -1)
    [ -z "$ref_to" ] && continue

    local rel_type
    rel_type=$(sed -n 's/.*<type>\(.*\)<\/type>.*/\1/p' "$field_file" 2>/dev/null | head -1)

    # Get parent object name from directory path
    local obj_name
    obj_name=$(basename "$(dirname "$(dirname "$field_file")")")
    local field_name
    field_name=$(basename "$field_file" .field-meta.xml)

    echo "$obj_name|$field_name|$rel_type|$ref_to"
  done | sort -u > "$TMP_BASE/relationships.tmp"

  local rel_count
  rel_count=$(wc -l < "$TMP_BASE/relationships.tmp" 2>/dev/null | tr -d ' ')

  if [ "$rel_count" = "0" ] || [ -z "$rel_count" ]; then
    return
  fi

  echo "## Cross-Object Relationships ($rel_count)"
  echo ""
  echo "| From Object | Field | Type | To Object |"
  echo "|-------------|-------|------|-----------|"

  while IFS='|' read -r obj field rel ref; do
    [ -z "$obj" ] && continue
    echo "| $obj | $field | $rel | $ref |"
  done < "$TMP_BASE/relationships.tmp"

  echo ""
}

# Extract common Apex patterns
extract_common_patterns() {
  local src_dir="$1"

  echo "## Common Patterns"
  echo ""

  # TriggerBypass usage
  local bypass_count
  bypass_count=$(grep -rl "TriggerBypass\|Bypass_Trigger\|bypassTrigger\|BYPASS" "$src_dir" --include="*.cls" 2>/dev/null | wc -l | tr -d ' ')

  # ServiceLocator usage
  local locator_count
  locator_count=$(grep -rl "ServiceLocator\|Service_Locator" "$src_dir" --include="*.cls" 2>/dev/null | wc -l | tr -d ' ')

  # Batch/Schedulable chains
  local batch_count
  batch_count=$(find "$src_dir" -name "*.cls" 2>/dev/null | xargs grep -l "Database\.executeBatch\|System\.scheduleBatch\|implements[[:space:]]*Schedulable\|implements[[:space:]]*Database\.Batchable" 2>/dev/null | wc -l | tr -d ' ')

  # Queueable
  local queue_count
  queue_count=$(find "$src_dir" -name "*.cls" 2>/dev/null | xargs grep -l "System\.enqueueJob\|implements[[:space:]]*Queueable" 2>/dev/null | wc -l | tr -d ' ')

  # Platform events
  local event_count
  event_count=$(grep -rl "EventBus\.publish\|__e" "$src_dir" --include="*.cls" 2>/dev/null | wc -l | tr -d ' ')

  echo "| Pattern | Files Using It | Notes |"
  echo "|---------|---------------|-------|"
  echo "| Trigger Bypass | $bypass_count | Classes referencing bypass mechanisms |"
  echo "| Service Locator | $locator_count | Classes using service locator pattern |"
  echo "| Batch/Schedulable | $batch_count | Classes implementing batch or schedulable |"
  echo "| Queueable | $queue_count | Classes using async queueable jobs |"
  echo "| Platform Events | $event_count | Classes publishing or subscribing to events |"
  echo ""
}

# Test coverage summary
extract_test_coverage_summary() {
  local src_dir="$1"

  local prod_count
  prod_count=$(find "$src_dir" -name "*.cls" -not -name "*Test*" -not -name "*Mock*" -not -name "*Stub*" -not -name "*_T.cls" 2>/dev/null | wc -l | tr -d ' ')

  local test_count
  test_count=$(find "$src_dir" -name "*.cls" \( -name "*Test*" -o -name "*_T.cls" -o -name "*Mock*" -o -name "*Stub*" \) 2>/dev/null | wc -l | tr -d ' ')

  local ratio="N/A"
  if [ "$prod_count" -gt 0 ] 2>/dev/null; then
    # Bash integer math: multiply by 100 first for percentage
    ratio="$((test_count * 100 / prod_count))%"
  fi

  echo "## Test Coverage Summary"
  echo ""
  echo "| Metric | Count |"
  echo "|--------|-------|"
  echo "| Production classes | $prod_count |"
  echo "| Test/Mock/Stub classes | $test_count |"
  echo "| Test-to-production ratio | $ratio |"
  echo ""

  # List production classes without apparent test coverage
  local untested=""
  local untested_count=0
  find "$src_dir" -name "*.cls" -not -name "*Test*" -not -name "*Mock*" -not -name "*Stub*" -not -name "*_T.cls" 2>/dev/null | sort | while IFS= read -r f; do
    local classname
    classname=$(basename "$f" .cls)
    # Check if a test class exists for this class
    local has_test=false
    if find "$src_dir" -name "${classname}_T.cls" -o -name "${classname}Test.cls" -o -name "${classname}_Test.cls" 2>/dev/null | grep -q .; then
      has_test=true
    fi
    if [ "$has_test" = "false" ]; then
      echo "$classname"
    fi
  done > "$TMP_BASE/untested.tmp" 2>/dev/null

  untested_count=$(wc -l < "$TMP_BASE/untested.tmp" 2>/dev/null | tr -d ' ')
  if [ "$untested_count" -gt 0 ] 2>/dev/null && [ "$untested_count" -lt 50 ]; then
    echo "### Classes Without Apparent Test Coverage ($untested_count)"
    echo ""
    head -30 "$TMP_BASE/untested.tmp" | while read -r cls; do
      echo "- \`$cls\`"
    done
    if [ "$untested_count" -gt 30 ]; then
      echo "- ... and $((untested_count - 30)) more"
    fi
    echo ""
  elif [ "$untested_count" -ge 50 ] 2>/dev/null; then
    echo "_${untested_count} classes without apparent test coverage (too many to list)._"
    echo ""
  fi
}

# --- Sync a single repo ---
sync_repo() {
  local repo="$1"
  local skill_dir="$2"  # relative to skills/ or "standalone:PATH"
  local is_ui="${3:-false}"

  local clone_dir="$TMP_BASE/$repo"

  echo "  Cloning $ORG/$repo..."
  if ! gh repo clone "$ORG/$repo" "$clone_dir" -- --depth 1 2>/dev/null; then
    echo "  FAILED to clone $ORG/$repo — skipping"
    return 1
  fi

  local commit_sha
  commit_sha=$(cd "$clone_dir" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")

  # Determine force-app path (standard SFDX structure)
  local src_path="$clone_dir"
  if [ -d "$clone_dir/force-app/main/default" ]; then
    src_path="$clone_dir/force-app/main/default"
  elif [ -d "$clone_dir/force-app" ]; then
    src_path="$clone_dir/force-app"
  fi

  # Determine output directory
  local out_dir
  case "$skill_dir" in
    standalone:*)
      out_dir="$REPO_ROOT/${skill_dir#standalone:}"
      ;;
    *)
      out_dir="$REPO_ROOT/skills/$skill_dir/references"
      ;;
  esac
  mkdir -p "$out_dir"

  local index_file="$out_dir/source-index.md"
  local synced_file="$out_dir/last-synced.txt"

  if [ "$is_ui" = "true" ]; then
    # UI repo: append LWC section to existing index
    local ui_section="$TMP_BASE/${repo}-ui-section.md"
    {
      echo ""
      echo "## Frontend: $repo"
      echo ""
      extract_lwc_components "$src_path"
    } > "$ui_section"

    if $DRY_RUN; then
      echo "  [dry-run] Would append UI section from $repo to $index_file"
      local lwc_count
      lwc_count=$(grep -c "^|" "$ui_section" 2>/dev/null || echo "0")
      lwc_count=$((lwc_count > 1 ? lwc_count - 1 : 0))
      echo "  [dry-run] $lwc_count LWC components found"
    else
      cat "$ui_section" >> "$index_file"
      echo "  Appended $repo LWC components to $index_file"
    fi
    return 0
  fi

  # Primary repo: generate full index (write to temp, atomic move on success)
  local index_content="$TMP_BASE/${repo}-index.md"
  {
    echo "# $repo Source Index"
    echo "> Last synced: $(date -u +%Y-%m-%dT%H:%M:%SZ) | Commit: $commit_sha | Repo: $ORG/$repo"
    echo ""
    extract_apex_classes "$src_path"
    extract_triggers "$src_path"
    extract_trigger_handler_map "$src_path"
    extract_service_methods "$src_path"
    extract_service_graph "$src_path"
    extract_relationship_summary "$src_path"
    extract_object_fields "$src_path"
    extract_common_patterns "$src_path"
    extract_test_coverage_summary "$src_path"
    echo "## Known Gotchas"
    echo ""
    echo "_No known gotchas recorded yet. This section is populated by operational learnings from debugging sessions._"
    echo ""
  } > "$index_content"

  if $DRY_RUN; then
    local lines
    lines=$(wc -l < "$index_content" | tr -d ' ')
    local tables
    tables=$(grep -c "^|" "$index_content" 2>/dev/null || echo "0")
    echo "  [dry-run] Would write $index_file ($lines lines, $tables table rows)"
    echo "  [dry-run] Sections: $(grep "^## " "$index_content" | sed 's/## //' | tr '\n' ', ' | sed 's/,$//')"
  else
    cp "$index_content" "$index_file"
    echo "Last synced: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$synced_file"
    echo "Commit: $commit_sha" >> "$synced_file"
    echo "Repo: $ORG/$repo" >> "$synced_file"
    echo "  Wrote $index_file"
  fi

  return 0
}

# --- Main sync loop ---
echo "=== Ohanafy Source Index Sync ==="
echo ""

SYNCED=0
FAILED=0
FAILED_LIST=""

sync_one_primary() {
  local repo="$1"
  local skill
  skill=$(lookup_primary "$repo")

  echo "[$repo -> $skill]"
  if sync_repo "$repo" "$skill" false; then
    # Check for UI counterpart
    for entry in "${UI_ENTRIES[@]}"; do
      local ui_repo="${entry%%:*}"
      local ui_skill="${entry#*:}"
      if [ "$ui_skill" = "$skill" ]; then
        echo "  [$ui_repo -> $skill (UI)]"
        sync_repo "$ui_repo" "$skill" true || true
      fi
    done

    # Check for secondary repos
    for entry in "${SECONDARY_ENTRIES[@]}"; do
      local sec_repo="${entry%%:*}"
      local sec_skill="${entry#*:}"
      if [ "$sec_skill" = "$skill" ]; then
        echo "  [$sec_repo -> $skill (secondary)]"
        sync_repo "$sec_repo" "$skill" false || true
      fi
    done

    SYNCED=$((SYNCED + 1))
  else
    FAILED=$((FAILED + 1))
    FAILED_LIST="$FAILED_LIST $repo"
  fi
  echo ""
}

if [ -n "$TARGET_REPO" ]; then
  # Single repo mode
  skill=""
  if skill=$(lookup_primary "$TARGET_REPO" 2>/dev/null); then
    sync_one_primary "$TARGET_REPO"
  elif skill=$(lookup_ui "$TARGET_REPO" 2>/dev/null); then
    echo "[$TARGET_REPO -> $skill (UI)]"
    sync_repo "$TARGET_REPO" "$skill" true || FAILED=$((FAILED + 1))
  elif skill=$(lookup_secondary "$TARGET_REPO" 2>/dev/null); then
    echo "[$TARGET_REPO -> $skill (secondary)]"
    sync_repo "$TARGET_REPO" "$skill" false || FAILED=$((FAILED + 1))
  elif is_in_list "$TARGET_REPO" "${STANDALONE_REPOS[@]}"; then
    echo "[$TARGET_REPO -> references/ohanafy-index/$TARGET_REPO/]"
    sync_repo "$TARGET_REPO" "standalone:references/ohanafy-index/$TARGET_REPO" false || FAILED=$((FAILED + 1))
  else
    echo "Unknown repo: $TARGET_REPO"
    echo ""
    echo "Known primary repos:"
    for entry in "${PRIMARY_ENTRIES[@]}"; do echo "  ${entry%%:*}"; done
    echo ""
    echo "Known UI repos:"
    for entry in "${UI_ENTRIES[@]}"; do echo "  ${entry%%:*}"; done
    echo ""
    echo "Known secondary repos:"
    for entry in "${SECONDARY_ENTRIES[@]}"; do echo "  ${entry%%:*}"; done
    echo ""
    echo "Known standalone repos:"
    for repo in "${STANDALONE_REPOS[@]}"; do echo "  $repo"; done
    exit 1
  fi
else
  # Sync all primary repos (each pulls its UI and secondary repos)
  for entry in "${PRIMARY_ENTRIES[@]}"; do
    repo="${entry%%:*}"
    sync_one_primary "$repo"
  done

  # Sync standalone repos
  for repo in "${STANDALONE_REPOS[@]}"; do
    echo "[$repo -> references/ohanafy-index/$repo/]"
    if sync_repo "$repo" "standalone:references/ohanafy-index/$repo" false; then
      SYNCED=$((SYNCED + 1))
    else
      FAILED=$((FAILED + 1))
      FAILED_LIST="$FAILED_LIST $repo"
    fi
    echo ""
  done
fi

# --- Summary ---
echo "=== Summary ==="
echo "Synced: $SYNCED"
if [ $FAILED -gt 0 ]; then
  echo "Failed: $FAILED ($FAILED_LIST)"
fi
if $DRY_RUN; then
  echo ""
  echo "This was a dry run. Remove --dry-run to write index files."
fi
