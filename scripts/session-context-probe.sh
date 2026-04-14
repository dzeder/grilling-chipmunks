#!/usr/bin/env bash
# session-context-probe.sh — SessionStart hook that detects workspace context
# Outputs a compact one-line summary for the Claude Code hook output.
# Must complete in <5 seconds. Pure bash, no external dependencies.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

customer=""
integration=""
environment=""
domains=()
stale=()

# ─── 1. Check .context/workspace.md (fresh = <24 hours old) ─────────────────

workspace_file="$REPO_ROOT/.context/workspace.md"
if [[ -f "$workspace_file" ]]; then
  # Check freshness: file must be <86400 seconds old
  if [[ "$(uname)" == "Darwin" ]]; then
    file_age=$(( $(date +%s) - $(stat -f %m "$workspace_file") ))
  else
    file_age=$(( $(date +%s) - $(stat -c %Y "$workspace_file") ))
  fi

  if (( file_age < 86400 )); then
    # Extract YAML frontmatter fields between --- markers
    in_frontmatter=false
    while IFS= read -r line; do
      if [[ "$line" == "---" ]]; then
        if $in_frontmatter; then
          break
        else
          in_frontmatter=true
          continue
        fi
      fi
      if $in_frontmatter; then
        case "$line" in
          customer:*)   customer="$(echo "${line#customer:}" | xargs)" ;;
          integration:*) integration="$(echo "${line#integration:}" | xargs)" ;;
          environment:*) environment="$(echo "${line#environment:}" | xargs)" ;;
        esac
      fi
    done < "$workspace_file"
  fi
fi

# ─── 2. Parse branch name for customer slug ──────────────────────────────────

branch="$(git branch --show-current 2>/dev/null || true)"
if [[ -z "$customer" && -n "$branch" ]]; then
  # Match dzeder/<customer>-* pattern
  if [[ "$branch" =~ ^dzeder/([a-zA-Z0-9_-]+)- ]]; then
    candidate="${BASH_REMATCH[1]}"
    if [[ -d "$REPO_ROOT/customers/$candidate" ]]; then
      customer="$candidate"
    fi
  fi
fi

# ─── 3. Scan recent git diff for domain signals ─────────────────────────────

changed_files="$(git diff --name-only HEAD~5..HEAD 2>/dev/null || true)"
if [[ -n "$changed_files" ]]; then
  seen_salesforce=false
  seen_vip=false
  seen_tray=false
  seen_ohanafy=false
  seen_aws=false
  seen_knowledge=false

  while IFS= read -r file; do
    case "$file" in
      *.cls|*.trigger)
        if ! $seen_salesforce; then domains+=("salesforce"); seen_salesforce=true; fi
        ;;
      integrations/vip-srs/*)
        if ! $seen_vip; then domains+=("vip-srs"); seen_vip=true; fi
        ;;
      integrations/tray/*|skills/tray/*)
        if ! $seen_tray; then domains+=("tray"); seen_tray=true; fi
        ;;
      skills/ohanafy/*)
        if ! $seen_ohanafy; then domains+=("ohanafy"); seen_ohanafy=true; fi
        ;;
      skills/aws/*)
        if ! $seen_aws; then domains+=("aws"); seen_aws=true; fi
        ;;
      knowledge-base/*)
        if ! $seen_knowledge; then domains+=("knowledge"); seen_knowledge=true; fi
        ;;
    esac
  done <<< "$changed_files"

  # Also detect integration from changed files if not already set
  if [[ -z "$integration" ]] && $seen_vip; then
    integration="vip-srs"
  fi
fi

# ─── 4. Check for stale indexes (>7 days old) ────────────────────────────────

for synced_file in "$REPO_ROOT"/skills/ohanafy/*/references/last-synced.txt; do
  [[ -f "$synced_file" ]] || continue

  if [[ "$(uname)" == "Darwin" ]]; then
    synced_age=$(( $(date +%s) - $(stat -f %m "$synced_file") ))
  else
    synced_age=$(( $(date +%s) - $(stat -c %Y "$synced_file") ))
  fi

  if (( synced_age > 604800 )); then
    # Extract package name from path: skills/ohanafy/<package>/references/last-synced.txt
    pkg_path="${synced_file%/references/last-synced.txt}"
    pkg_name="${pkg_path##*/}"
    stale+=("$pkg_name")
  fi
done

# ─── 5. Output compact report ────────────────────────────────────────────────

parts=()

if [[ -n "$customer" ]]; then
  parts+=("customer=$customer")
fi

if [[ -n "$integration" ]]; then
  parts+=("integration=$integration")
fi

if [[ -n "$environment" ]]; then
  parts+=("env=$environment")
fi

if (( ${#domains[@]} > 0 )); then
  domain_str="$(IFS=,; echo "${domains[*]}")"
  parts+=("domains=[$domain_str]")
fi

if (( ${#stale[@]} > 0 )); then
  stale_str="$(IFS=,; echo "${stale[*]}")"
  parts+=("stale=[$stale_str]")
fi

if (( ${#parts[@]} > 0 )); then
  echo "Context probe: ${parts[*]}"
else
  echo "Context probe: no active context detected"
fi
