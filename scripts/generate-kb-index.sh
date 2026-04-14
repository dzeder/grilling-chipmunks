#!/usr/bin/env bash
# generate-kb-index.sh — Scan knowledge-base/ and emit a structured YAML index
# Usage: bash scripts/generate-kb-index.sh > knowledge-base/INDEX.yaml
# Works on macOS default bash (v3) — no associative arrays.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KB_DIR="$REPO_ROOT/knowledge-base"

if [[ ! -d "$KB_DIR" ]]; then
  echo "ERROR: knowledge-base/ not found at $KB_DIR" >&2
  exit 1
fi

# --- Lookup helpers (macOS bash v3 compatible) ---
get_description() {
  case "$1" in
    vip-srs)              echo "VIP Supplier Reporting System file specifications and coded values" ;;
    ohanafy)              echo "Ohanafy platform objects, features, and integration points" ;;
    salesforce)           echo "Salesforce ecosystem, object model, and flow documentation" ;;
    tray)                 echo "Tray.io connectors, capabilities, and integration patterns" ;;
    beverage-supply-chain) echo "Beverage industry terminology and supply chain concepts" ;;
    industry-insights)    echo "Market analysis, competitive landscape, and technology trends" ;;
    *)                    echo "Knowledge base articles for $1" ;;
  esac
}

get_skills() {
  case "$1" in
    vip-srs)              echo "ohfy-vip-srs-expert, tray-expert, data-harmonizer" ;;
    ohanafy)              echo "ohfy-core-expert, ohfy-data-model-expert, ohfy-oms-expert, ohfy-wms-expert, ohfy-payments-expert" ;;
    salesforce)           echo "sf-apex, sf-flow, sf-metadata, sf-integration, sf-deploy" ;;
    tray)                 echo "tray-expert, tray-script-generator, tray-errors" ;;
    beverage-supply-chain) echo "beverage-erp-expert, office-hours" ;;
    industry-insights)    echo "office-hours, content-watcher" ;;
    *)                    echo "" ;;
  esac
}

# --- Header ---
echo "# Knowledge Base Index — auto-generated $(date +%Y-%m-%d)"
echo "# Re-generate: bash scripts/generate-kb-index.sh > knowledge-base/INDEX.yaml"
echo ""
echo "domains:"

# Collect top-level domain directories (sorted)
for dir in $(find "$KB_DIR" -mindepth 1 -maxdepth 1 -type d | sort); do
  domain="$(basename "$dir")"
  desc="$(get_description "$domain")"
  skills="$(get_skills "$domain")"

  echo "  $domain:"
  echo "    description: \"$desc\""
  if [[ -n "$skills" ]]; then
    echo "    relevant_skills: [${skills}]"
  else
    echo "    relevant_skills: []"
  fi
  echo "    files:"

  # Find all .md files under this domain, sorted by path
  while IFS= read -r filepath; do
    [[ -f "$filepath" ]] || continue

    # Relative path from repo root
    relpath="${filepath#${REPO_ROOT}/}"

    # Extract first H1 or H2 heading
    heading=""
    while IFS= read -r line; do
      if echo "$line" | grep -qE '^##?[[:space:]]+'; then
        heading="$(echo "$line" | sed -E 's/^##?[[:space:]]+//')"
        break
      fi
    done < "$filepath"

    # Fallback: use filename without extension
    if [[ -z "$heading" ]]; then
      heading="$(basename "$filepath" .md)"
    fi

    # Extract summary: first 2 non-empty, non-heading, non-comment lines
    summary=""
    count=0
    while IFS= read -r line; do
      # Skip blank lines
      [[ -z "$line" ]] && continue
      # Skip headings
      echo "$line" | grep -qE '^#' && continue
      # Skip HTML comments
      echo "$line" | grep -qE '^\<\!--' && continue
      # Skip horizontal rules
      [[ "$line" == "---" ]] && continue
      # Skip table separator lines
      echo "$line" | grep -qE '^\|[-|: ]+\|$' && continue
      # Escape double quotes for YAML safety
      escaped="$(echo "$line" | sed 's/"/\\"/g')"
      if [[ $count -eq 0 ]]; then
        summary="$escaped"
      else
        summary="$summary $escaped"
      fi
      count=$((count + 1))
      [[ $count -ge 2 ]] && break
    done < "$filepath"

    # Truncate summary to 200 chars
    if [[ ${#summary} -gt 200 ]]; then
      summary="${summary:0:197}..."
    fi

    echo "      - path: \"$relpath\""
    echo "        heading: \"$heading\""
    if [[ -n "$summary" ]]; then
      echo "        summary: \"$summary\""
    fi
  done < <(find "$KB_DIR/$domain" -name "*.md" -type f | sort)

  echo ""
done
