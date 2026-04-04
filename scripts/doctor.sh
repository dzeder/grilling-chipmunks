#!/bin/bash
# Unified health check for the monorepo
# Usage:
#   bash scripts/doctor.sh                   # full check (all 10 sections)
#   bash scripts/doctor.sh --quick           # fast check (prereqs, symlinks, agents, GH Actions)
#   bash scripts/doctor.sh --create-issues   # full check + file GitHub issues for failures

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# Validate we're in the right repo
if [ ! -f CLAUDE.md ] || [ ! -d agents ] || [ ! -d .claude/skills ]; then
    echo "❌ Not in the monorepo root (expected CLAUDE.md, agents/, .claude/skills/)"
    exit 1
fi

# Parse args
QUICK=false
CREATE_ISSUES=false
for arg in "$@"; do
    case "$arg" in
        --quick) QUICK=true ;;
        --create-issues) CREATE_ISSUES=true ;;
    esac
done

# State
PASS=0
FAIL=0
WARN=0
TOTAL=0
GH_AUTH_OK=true
ISSUE_LABEL="doctor"

# Issue queue — parallel arrays
declare -a ISSUE_TITLES=()
declare -a ISSUE_BODIES=()

# ─────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────

section() {
    echo ""
    echo "$1. $2"
}

record_pass() { PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1)); }
record_fail() { FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); }
record_warn() { WARN=$((WARN + 1)); TOTAL=$((TOTAL + 1)); }

skip_section() {
    section "$1" "$2"
    echo "   ⏭️  Skipped (--quick)"
}

queue_issue() {
    local title="$1"
    local body="$2"
    ISSUE_TITLES+=("$title")
    ISSUE_BODIES+=("$body")
}

# ─────────────────────────────────────────────
# Section 1: Prerequisites
# ─────────────────────────────────────────────

check_prerequisites() {
    section 1 "Prerequisites"
    local issues=0
    local missing=""

    # gh CLI
    if command -v gh &>/dev/null; then
        local gh_ver
        gh_ver=$(gh --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
        local gh_user
        # Parse gh auth status — pick the active account only
        local gh_status
        gh_status=$(gh auth status 2>&1 || true)
        gh_user=$(echo "$gh_status" | grep -E 'Active account: true' -B5 | grep -oE 'Logged in to github.com (as|account) [^ ]+' | head -1 | awk '{print $NF}' || true)
        # Strip trailing parenthetical if present (e.g. "(keyring)" or "(GH_TOKEN)")
        gh_user="${gh_user%(*}"
        gh_user="${gh_user% }"

        if [ -n "$gh_user" ]; then
            echo "   ✅ gh ${gh_ver} (authenticated as ${gh_user})"
        elif [ -n "${GH_TOKEN:-}" ]; then
            echo "   ✅ gh ${gh_ver} (authenticated via GH_TOKEN)"
        else
            echo "   ⚠️  gh ${gh_ver} (not authenticated — run 'gh auth login')"
            GH_AUTH_OK=false
            issues=$((issues + 1))
            missing+="- \`gh\` installed but not authenticated\n"
        fi

        # Token scope validation (only if authenticated)
        if $GH_AUTH_OK; then
            # Extract scopes for the active account (appears after "Active account: true")
            local scopes
            scopes=$(echo "$gh_status" | awk '/Active account: true/{found=1} found && /Token scopes:/{print; exit}' | sed "s/.*Token scopes: '//;s/'$//" || true)
            if [ -n "$scopes" ]; then
                local required_scopes=("repo")
                local missing_scopes=""
                for scope in "${required_scopes[@]}"; do
                    if ! echo "$scopes" | grep -qw "$scope"; then
                        missing_scopes+="${scope}, "
                    fi
                done
                if [ -n "$missing_scopes" ]; then
                    echo "   ⚠️  Token missing scopes: ${missing_scopes%, }"
                    issues=$((issues + 1))
                else
                    local scope_count
                    scope_count=$(echo "$scopes" | tr ',' '\n' | wc -l | tr -d ' ')
                    echo "   ✅ Token scopes OK (${scope_count} scopes)"
                fi
            fi
        fi
    else
        echo "   ❌ gh not installed"
        GH_AUTH_OK=false
        issues=$((issues + 1))
        missing+="- \`gh\` CLI not installed\n"
    fi

    # sf CLI
    if command -v sf &>/dev/null; then
        local sf_ver
        sf_ver=$(sf --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")
        echo "   ✅ sf ${sf_ver}"
    else
        echo "   ❌ sf not installed"
        issues=$((issues + 1))
        missing+="- \`sf\` (Salesforce CLI) not installed\n"
    fi

    # node
    if command -v node &>/dev/null; then
        local node_ver
        node_ver=$(node --version 2>/dev/null | tr -d 'v' || echo "unknown")
        echo "   ✅ node ${node_ver}"
    else
        echo "   ❌ node not installed"
        issues=$((issues + 1))
        missing+="- \`node\` not installed\n"
    fi

    # python3
    if command -v python3 &>/dev/null; then
        local py_ver
        py_ver=$(python3 --version 2>/dev/null | awk '{print $2}' || echo "unknown")
        echo "   ✅ python3 ${py_ver}"
    else
        echo "   ❌ python3 not installed"
        issues=$((issues + 1))
        missing+="- \`python3\` not installed\n"
    fi

    if [ "$issues" -eq 0 ]; then
        record_pass
    elif [ "$issues" -le 1 ] && ! $GH_AUTH_OK; then
        record_warn
    else
        record_fail
        queue_issue \
            "Doctor: missing prerequisites" \
            "$(printf "The following prerequisites are missing or misconfigured:\n\n%b\n\nRun \`bash scripts/doctor.sh\` to re-check after fixing." "$missing")"
    fi
}

# ─────────────────────────────────────────────
# Section 2: Symlink Health
# ─────────────────────────────────────────────

check_symlinks() {
    section 2 "Symlink Health"
    local total=0
    local valid=0
    local broken=0
    local broken_list=""
    local broken_md=""

    for skill_dir in .claude/skills/*/; do
        [ -d "$skill_dir" ] || continue
        local skill_file="${skill_dir}SKILL.md"
        local skill_name
        skill_name=$(basename "$skill_dir")

        # Skip gstack directory itself (contains real files, not symlinks)
        [ "$skill_name" = "gstack" ] && continue

        total=$((total + 1))

        if [ -L "$skill_file" ]; then
            local target
            target=$(readlink "$skill_file" 2>/dev/null || echo "unknown")
            if [ ! -e "$skill_file" ]; then
                broken=$((broken + 1))
                broken_list+="   ❌ ${skill_name} → ${target}\n"
                broken_md+="- \`${skill_name}\` → \`${target}\`\n"
            elif [[ "$target" == /* ]]; then
                broken=$((broken + 1))
                broken_list+="   ⚠️  ${skill_name} → ${target} (absolute path — not portable)\n"
                broken_md+="- \`${skill_name}\` → \`${target}\` (absolute path)\n"
            else
                valid=$((valid + 1))
            fi
        elif [ -f "$skill_file" ]; then
            valid=$((valid + 1))
        else
            broken=$((broken + 1))
            broken_list+="   ❌ ${skill_name} (no SKILL.md)\n"
            broken_md+="- \`${skill_name}\` — no SKILL.md\n"
        fi
    done

    if [ "$broken" -eq 0 ]; then
        echo "   ✅ ${valid}/${total} skill symlinks valid"
        record_pass
    else
        echo "   ❌ ${valid}/${total} valid, ${broken} broken:"
        echo -e "$broken_list"
        record_fail
        queue_issue \
            "Doctor: ${broken} broken skill symlinks" \
            "$(printf "${broken} of ${total} skill symlinks in \`.claude/skills/\` are broken:\n\n%b\nClaude Code cannot discover these skills until the symlinks are fixed.\n\n**How to fix:** Run \`bash scripts/fix-gstack-symlinks.sh\` to normalize symlinks, then verify with \`bash scripts/doctor.sh --quick\`." "$broken_md")"
    fi
}

# ─────────────────────────────────────────────
# Section 3: Agent Definitions
# ─────────────────────────────────────────────

check_agents() {
    section 3 "Agent Definitions"
    local total=0
    local valid=0
    local invalid=0
    local invalid_list=""
    local invalid_md=""

    for agent_file in agents/*.md; do
        [ -f "$agent_file" ] || continue
        local agent_name
        agent_name=$(basename "$agent_file" .md)
        total=$((total + 1))

        local issues=""

        # Check frontmatter delimiters exist
        local delimiter_count
        delimiter_count=$(grep -c '^---' "$agent_file" 2>/dev/null || echo "0")
        if [ "$delimiter_count" -lt 2 ]; then
            issues+="missing YAML frontmatter"
        else
            local frontmatter
            frontmatter=$(awk '/^---/{c++;next}c==1{print}' "$agent_file")

            if ! echo "$frontmatter" | grep -q '^name:'; then
                issues+="missing name field"
            fi

            if ! echo "$frontmatter" | grep -q '^description:'; then
                [ -n "$issues" ] && issues+=", "
                issues+="missing description field"
            fi
        fi

        local body_lines
        body_lines=$(awk '/^---/{c++}c>=2 && !/^---/' "$agent_file" | grep -c '[^ ]' 2>/dev/null || echo "0")
        if [ "$body_lines" -eq 0 ]; then
            [ -n "$issues" ] && issues+=", "
            issues+="empty body"
        fi

        if [ -z "$issues" ]; then
            valid=$((valid + 1))
        else
            invalid=$((invalid + 1))
            invalid_list+="   ❌ ${agent_name}: ${issues}\n"
            invalid_md+="- \`${agent_name}\`: ${issues}\n"
        fi
    done

    if [ "$invalid" -eq 0 ]; then
        echo "   ✅ ${valid}/${total} agents valid"
        record_pass
    else
        echo "   ❌ ${valid}/${total} valid, ${invalid} invalid:"
        echo -e "$invalid_list"
        record_fail
        queue_issue \
            "Doctor: ${invalid} invalid agent definitions" \
            "$(printf "${invalid} of ${total} agent definitions in \`agents/\` have structural issues:\n\n%b\nSee \`docs/AGENT_TEMPLATE.md\` for required structure." "$invalid_md")"
    fi
}

# ─────────────────────────────────────────────
# Section 4: Skill Lint (delegated)
# ─────────────────────────────────────────────

check_skill_lint() {
    section 4 "Skill Lint"

    if [ ! -f scripts/lint-skills.sh ]; then
        echo "   ❌ scripts/lint-skills.sh not found"
        record_fail
        return
    fi

    local exit_code=0
    local output
    output=$(bash scripts/lint-skills.sh --summary 2>&1) || exit_code=$?

    echo "$output" | while IFS= read -r line; do echo "   $line"; done

    if [ "$exit_code" -eq 0 ]; then
        record_pass
    else
        # Extract failure count from summary line
        local fail_count
        fail_count=$(echo "$output" | grep -oE 'Fail: [0-9]+' | awk '{print $2}' || echo "?")
        record_fail
        # shellcheck disable=SC2016
        queue_issue \
            "Doctor: ${fail_count} skills failing lint" \
            "$(printf '`scripts/lint-skills.sh` reports %s skill(s) failing structural checks.\n\nRun `bash scripts/lint-skills.sh` for full details.\n\nSee `docs/SKILL_TEMPLATE.md` for required structure.' "$fail_count")"
    fi
}

# ─────────────────────────────────────────────
# Section 5: Repo Hygiene (delegated)
# ─────────────────────────────────────────────

check_repo_hygiene() {
    section 5 "Repo Hygiene"

    if [ ! -f tools/check_repo_hygiene.py ]; then
        echo "   ❌ tools/check_repo_hygiene.py not found"
        record_fail
        return
    fi

    local exit_code=0
    local output
    output=$(python3 tools/check_repo_hygiene.py 2>&1) || exit_code=$?

    if [ "$exit_code" -eq 0 ]; then
        echo "   ${output}"
        record_pass
    else
        # Count issues by type from the output
        local issue_count missing_count anchor_count forbidden_count
        issue_count=$(echo "$output" | head -1 | grep -oE '[0-9]+' | head -1 || echo "0")
        missing_count=$(echo "$output" | grep -c '^MISSING' 2>/dev/null) || missing_count=0
        anchor_count=$(echo "$output" | grep -c '^ANCHOR' 2>/dev/null) || anchor_count=0
        forbidden_count=$(echo "$output" | grep -c '^FORBIDDEN' 2>/dev/null) || forbidden_count=0
        echo "   ❌ ${issue_count} hygiene issues (${missing_count} missing links, ${anchor_count} broken anchors, ${forbidden_count} forbidden patterns)"
        record_fail
        # shellcheck disable=SC2016
        queue_issue \
            "Doctor: ${issue_count} repo hygiene issues" \
            "$(printf '`tools/check_repo_hygiene.py` found %s issue(s):\n\n| Type | Count |\n|------|-------|\n| Missing link targets | %s |\n| Broken anchors | %s |\n| Forbidden patterns | %s |\n\nMost are missing `references/*.md` files that skills link to but haven'\''t been created yet.\n\nRun `python3 tools/check_repo_hygiene.py` for full details.' "$issue_count" "$missing_count" "$anchor_count" "$forbidden_count")"
    fi
}

# ─────────────────────────────────────────────
# Section 6: GitHub Actions Health
# ─────────────────────────────────────────────

check_github_actions() {
    section 6 "GitHub Actions"

    if ! $GH_AUTH_OK; then
        echo "   ⏭️  Skipped (gh not authenticated)"
        return
    fi

    local exit_code=0
    local output
    output=$(gh run list --limit 50 --json workflowName,status,conclusion 2>&1) || exit_code=$?

    if [ "$exit_code" -ne 0 ]; then
        echo "   ⚠️  Could not fetch workflow runs: ${output}"
        record_warn
        return
    fi

    local result
    result=$(echo "$output" | python3 -c "
import json, sys
try:
    runs = json.loads(sys.stdin.read())
    seen = {}
    for r in runs:
        name = r.get('workflowName', 'unknown')
        if name not in seen:
            seen[name] = r
    passing = sum(1 for r in seen.values() if r.get('conclusion') == 'success')
    total = len(seen)
    for name in sorted(seen):
        r = seen[name]
        conclusion = r.get('conclusion') or r.get('status') or 'unknown'
        if conclusion != 'success':
            print(f'WARN:{name}:{conclusion}')
    print(f'SUMMARY:{passing}:{total}')
except Exception as e:
    print(f'ERROR:{e}')
" 2>&1)

    local passing=0
    local gh_total=0
    local warnings=""
    local warnings_md=""

    while IFS= read -r line; do
        case "$line" in
            SUMMARY:*)
                passing=$(echo "$line" | cut -d: -f2)
                gh_total=$(echo "$line" | cut -d: -f3)
                ;;
            WARN:*)
                local wf_name wf_status
                wf_name=$(echo "$line" | cut -d: -f2)
                wf_status=$(echo "$line" | cut -d: -f3)
                warnings+="   ⚠️  ${wf_name}: ${wf_status}\n"
                warnings_md+="- **${wf_name}**: ${wf_status}\n"
                ;;
            ERROR:*)
                echo "   ⚠️  Parse error: ${line#ERROR:}"
                record_warn
                return
                ;;
        esac
    done <<< "$result"

    if [ "$gh_total" -eq 0 ]; then
        echo "   ⚠️  No workflow runs found"
        record_warn
    elif [ "$passing" -eq "$gh_total" ]; then
        echo "   ✅ ${passing}/${gh_total} workflows passing"
        record_pass
    else
        local failing=$((gh_total - passing))
        echo "   ⚠️  ${passing}/${gh_total} workflows passing"
        echo -e "$warnings"
        record_warn
        queue_issue \
            "Doctor: ${failing} GitHub Actions workflows not passing" \
            "$(printf "${failing} of ${gh_total} workflows have non-success status:\n\n%b\nCheck the Actions tab for details." "$warnings_md")"
    fi
}

# ─────────────────────────────────────────────
# Section 7: GitHub Security
# ─────────────────────────────────────────────

check_github_security() {
    section 7 "GitHub Security"

    if ! $GH_AUTH_OK; then
        echo "   ⏭️  Skipped (gh not authenticated)"
        return
    fi

    local sub_issues=0

    # Dependabot alerts
    local exit_code=0
    local alerts
    alerts=$(gh api repos/{owner}/{repo}/dependabot/alerts --jq '[.[] | select(.state == "open")] | length' 2>&1) || exit_code=$?

    if [ "$exit_code" -ne 0 ]; then
        # Dependabot might not be enabled or token lacks security_events scope
        if echo "$alerts" | grep -qi "not enabled\|disabled\|404\|403"; then
            echo "   ℹ️  Dependabot alerts not enabled"
        else
            echo "   ⚠️  Could not fetch Dependabot alerts"
        fi
    elif [ "$alerts" -eq 0 ] 2>/dev/null; then
        echo "   ✅ No open Dependabot alerts"
    else
        echo "   ⚠️  ${alerts} open Dependabot alert(s)"
        sub_issues=$((sub_issues + 1))

        # Show severity breakdown
        local severity_breakdown
        severity_breakdown=$(gh api repos/{owner}/{repo}/dependabot/alerts \
            --jq '[.[] | select(.state == "open")] | group_by(.security_advisory.severity) | map({severity: .[0].security_advisory.severity, count: length}) | sort_by(.count) | reverse | .[] | "      \(.severity): \(.count)"' 2>/dev/null || true)
        if [ -n "$severity_breakdown" ]; then
            echo "$severity_breakdown"
        fi
    fi

    # Secret scanning alerts
    exit_code=0
    local secrets
    secrets=$(gh api repos/{owner}/{repo}/secret-scanning/alerts --jq '[.[] | select(.state == "open")] | length' 2>&1) || exit_code=$?

    if [ "$exit_code" -ne 0 ]; then
        if echo "$secrets" | grep -qi "not enabled\|disabled\|404\|403"; then
            echo "   ℹ️  Secret scanning not enabled"
        else
            echo "   ⚠️  Could not fetch secret scanning alerts"
        fi
    elif [ "$secrets" -eq 0 ] 2>/dev/null; then
        echo "   ✅ No open secret scanning alerts"
    else
        echo "   ❌ ${secrets} open secret scanning alert(s) — fix immediately"
        sub_issues=$((sub_issues + 1))
    fi

    if [ "$sub_issues" -eq 0 ]; then
        record_pass
    else
        record_warn
        queue_issue \
            "Doctor: GitHub security alerts require attention" \
            "$(printf "Security alerts found in the repository.\n\nRun \`gh api repos/{owner}/{repo}/dependabot/alerts\` and \`gh api repos/{owner}/{repo}/secret-scanning/alerts\` for details.")"
    fi
}

# ─────────────────────────────────────────────
# Section 8: GitHub Repo Health
# ─────────────────────────────────────────────

check_github_repo_health() {
    section 8 "GitHub Repo Health"

    if ! $GH_AUTH_OK; then
        echo "   ⏭️  Skipped (gh not authenticated)"
        return
    fi

    local sub_issues=0

    # Branch protection on default branch
    local default_branch
    default_branch=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null || echo "main")

    local exit_code=0
    local protection
    protection=$(gh api "repos/{owner}/{repo}/branches/${default_branch}/protection" 2>&1) || exit_code=$?

    if [ "$exit_code" -ne 0 ]; then
        if echo "$protection" | grep -q "Branch not protected"; then
            echo "   ⚠️  Branch protection not enabled on ${default_branch}"
            sub_issues=$((sub_issues + 1))
        else
            echo "   ℹ️  Could not check branch protection (may require admin scope)"
        fi
    else
        local pr_required
        pr_required=$(echo "$protection" | python3 -c "
import json, sys
try:
    p = json.loads(sys.stdin.read())
    pr = p.get('required_pull_request_reviews')
    print('yes' if pr else 'no')
except:
    print('unknown')
" 2>/dev/null || echo "unknown")
        if [ "$pr_required" = "yes" ]; then
            echo "   ✅ Branch protection on ${default_branch} (PRs required)"
        elif [ "$pr_required" = "no" ]; then
            echo "   ⚠️  Branch protection on ${default_branch} (PRs not required)"
            sub_issues=$((sub_issues + 1))
        else
            echo "   ✅ Branch protection on ${default_branch}"
        fi
    fi

    # Open PRs health
    local pr_data
    pr_data=$(gh pr list --state open --json number,title,mergeable,updatedAt,headRefName,statusCheckRollup --limit 20 2>/dev/null || echo "[]")

    local pr_result
    pr_result=$(echo "$pr_data" | python3 -c "
import json, sys
from datetime import datetime, timezone
try:
    prs = json.loads(sys.stdin.read())
    total = len(prs)
    conflicted = []
    stale = []
    failing = []
    now = datetime.now(timezone.utc)
    for pr in prs:
        num = pr.get('number', '?')
        title = pr.get('title', 'unknown')[:40]
        mergeable = pr.get('mergeable', '')
        updated = pr.get('updatedAt', '')
        checks = pr.get('statusCheckRollup', []) or []

        if mergeable == 'CONFLICTING':
            conflicted.append(f'#{num} {title}')

        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                days_old = (now - updated_dt).days
                if days_old > 14:
                    stale.append(f'#{num} {title} ({days_old}d)')
            except:
                pass

        check_states = [c.get('conclusion') or c.get('status') for c in checks]
        if any(s in ('FAILURE', 'ERROR', 'ACTION_REQUIRED') for s in check_states):
            failing.append(f'#{num} {title}')

    print(f'TOTAL:{total}')
    for c in conflicted:
        print(f'CONFLICT:{c}')
    for s in stale:
        print(f'STALE:{s}')
    for f in failing:
        print(f'FAILING:{f}')
except Exception as e:
    print(f'ERROR:{e}')
" 2>&1)

    local pr_total=0
    local pr_conflicts=""
    local pr_stale=""
    local pr_failing=""
    local conflict_count=0
    local stale_count=0
    local failing_count=0

    while IFS= read -r line; do
        case "$line" in
            TOTAL:*) pr_total="${line#TOTAL:}" ;;
            CONFLICT:*)
                pr_conflicts+="      ⚠️  ${line#CONFLICT:}\n"
                conflict_count=$((conflict_count + 1))
                ;;
            STALE:*)
                pr_stale+="      💤 ${line#STALE:}\n"
                stale_count=$((stale_count + 1))
                ;;
            FAILING:*)
                pr_failing+="      ❌ ${line#FAILING:}\n"
                failing_count=$((failing_count + 1))
                ;;
            ERROR:*)
                echo "   ⚠️  PR parse error: ${line#ERROR:}"
                ;;
        esac
    done <<< "$pr_result"

    if [ "$pr_total" -eq 0 ]; then
        echo "   ✅ No open PRs"
    else
        local pr_issues=$((conflict_count + stale_count + failing_count))
        if [ "$pr_issues" -eq 0 ]; then
            echo "   ✅ ${pr_total} open PR(s), all healthy"
        else
            echo "   ⚠️  ${pr_total} open PR(s):"
            [ "$conflict_count" -gt 0 ] && echo -e "      Merge conflicts (${conflict_count}):\n${pr_conflicts}"
            [ "$failing_count" -gt 0 ] && echo -e "      Failing checks (${failing_count}):\n${pr_failing}"
            [ "$stale_count" -gt 0 ] && echo -e "      Stale >14d (${stale_count}):\n${pr_stale}"
            sub_issues=$((sub_issues + pr_issues))
        fi
    fi

    # Stale branches (no commits in 30+ days, excluding default branch)
    local stale_branches
    stale_branches=$(gh api repos/{owner}/{repo}/branches --paginate --jq '.[].name' 2>/dev/null | while read -r branch; do
        [ "$branch" = "$default_branch" ] && continue
        local last_commit_date
        last_commit_date=$(gh api "repos/{owner}/{repo}/branches/${branch}" --jq '.commit.commit.committer.date' 2>/dev/null || true)
        if [ -n "$last_commit_date" ]; then
            local days_old
            days_old=$(python3 -c "
from datetime import datetime, timezone
try:
    d = datetime.fromisoformat('${last_commit_date}'.replace('Z', '+00:00'))
    print((datetime.now(timezone.utc) - d).days)
except:
    print(0)
" 2>/dev/null || echo "0")
            if [ "$days_old" -gt 30 ]; then
                echo "${branch} (${days_old}d)"
            fi
        fi
    done 2>/dev/null || true)

    if [ -z "$stale_branches" ]; then
        echo "   ✅ No stale branches (>30 days)"
    else
        local stale_branch_count
        stale_branch_count=$(echo "$stale_branches" | wc -l | tr -d ' ')
        echo "   ⚠️  ${stale_branch_count} stale branch(es) (>30 days):"
        echo "$stale_branches" | while read -r b; do echo "      💤 ${b}"; done
        sub_issues=$((sub_issues + 1))
    fi

    if [ "$sub_issues" -eq 0 ]; then
        record_pass
    else
        record_warn
    fi
}

# ─────────────────────────────────────────────
# Section 9: GitHub Actions (detailed)
# ─────────────────────────────────────────────

check_github_actions_detailed() {
    section 9 "GitHub Actions (detailed)"

    if ! $GH_AUTH_OK; then
        echo "   ⏭️  Skipped (gh not authenticated)"
        return
    fi

    # Check for disabled workflows
    local exit_code=0
    local workflows
    workflows=$(gh api repos/{owner}/{repo}/actions/workflows --jq '.workflows[] | "\(.state)|\(.name)"' 2>&1) || exit_code=$?

    if [ "$exit_code" -ne 0 ]; then
        echo "   ⚠️  Could not fetch workflows"
        record_warn
        return
    fi

    local disabled_count=0
    local disabled_list=""
    local total_workflows=0

    while IFS= read -r line; do
        [ -z "$line" ] && continue
        total_workflows=$((total_workflows + 1))
        local state="${line%%|*}"
        local name="${line#*|}"
        if [ "$state" != "active" ]; then
            disabled_count=$((disabled_count + 1))
            disabled_list+="      ⏸️  ${name} (${state})\n"
        fi
    done <<< "$workflows"

    local active=$((total_workflows - disabled_count))
    if [ "$disabled_count" -eq 0 ]; then
        echo "   ✅ ${total_workflows} workflow(s), all active"
    else
        echo "   ℹ️  ${active}/${total_workflows} active, ${disabled_count} disabled:"
        echo -e "$disabled_list"
    fi

    # Check for workflows with high failure rate (last 10 runs each)
    local failing_workflows=""
    local fw_count=0

    while IFS= read -r line; do
        [ -z "$line" ] && continue
        local state="${line%%|*}"
        local name="${line#*|}"
        [ "$state" != "active" ] && continue

        local run_stats
        run_stats=$(gh run list --workflow "$name" --limit 10 --json conclusion --jq '[.[] | .conclusion] | {total: length, failures: [.[] | select(. == "failure")] | length} | "\(.failures)/\(.total)"' 2>/dev/null || echo "0/0")

        local failures="${run_stats%%/*}"
        local run_total="${run_stats##*/}"

        if [ "$failures" -ge 3 ] 2>/dev/null && [ "$run_total" -gt 0 ] 2>/dev/null; then
            failing_workflows+="      ⚠️  ${name}: ${failures}/${run_total} recent runs failed\n"
            fw_count=$((fw_count + 1))
        fi
    done <<< "$workflows"

    if [ "$fw_count" -gt 0 ]; then
        echo "   ⚠️  ${fw_count} workflow(s) with high failure rate:"
        echo -e "$failing_workflows"
        record_warn
    else
        echo "   ✅ No workflows with high failure rate"
        record_pass
    fi
}

# ─────────────────────────────────────────────
# Section 10: Install Health (delegated)
# ─────────────────────────────────────────────

check_install_health() {
    section 10 "Install Health"

    if [ ! -f tools/install.py ]; then
        echo "   ❌ tools/install.py not found"
        record_fail
        return
    fi

    local exit_code=0
    local output
    output=$(python3 tools/install.py --diagnose 2>&1) || exit_code=$?

    echo "$output" | while IFS= read -r line; do echo "   $line"; done

    if [ "$exit_code" -eq 0 ]; then
        record_pass
    else
        record_fail
        queue_issue \
            "Doctor: install health check failing" \
            "$(printf "\`tools/install.py --diagnose\` is reporting failures.\n\nRun \`python3 tools/install.py --diagnose\` for details, then \`python3 tools/install.py --install\` to repair.")"
    fi
}

# ─────────────────────────────────────────────
# Issue creation
# ─────────────────────────────────────────────

create_issues() {
    if [ "${#ISSUE_TITLES[@]}" -eq 0 ]; then
        return
    fi

    if ! $GH_AUTH_OK; then
        echo ""
        echo "   ⚠️  Cannot create issues — gh not authenticated"
        return
    fi

    # Ensure the 'doctor' label exists
    gh label create "$ISSUE_LABEL" --description "Auto-filed by scripts/doctor.sh" --color "D93F0B" 2>/dev/null || true

    echo ""
    echo "   Filing issues..."
    local created=0
    local skipped=0

    for i in "${!ISSUE_TITLES[@]}"; do
        local title="${ISSUE_TITLES[$i]}"
        local body="${ISSUE_BODIES[$i]}"

        # Check if an open issue with this exact title already exists
        local existing
        existing=$(gh issue list --label "$ISSUE_LABEL" --state open --search "in:title ${title}" --json number,title --jq ".[] | select(.title == \"${title}\") | .number" 2>/dev/null || true)

        if [ -n "$existing" ]; then
            echo "   ⏭️  #${existing} already open: ${title}"
            skipped=$((skipped + 1))
        else
            local issue_url
            issue_url=$(gh issue create \
                --title "$title" \
                --body "$body" \
                --label "$ISSUE_LABEL" 2>&1) || true

            if echo "$issue_url" | grep -q "github.com"; then
                echo "   📝 Created: ${issue_url}"
                created=$((created + 1))
            else
                echo "   ❌ Failed to create: ${title}"
                echo "      ${issue_url}"
            fi
        fi
    done

    echo ""
    echo "   Issues: ${created} created, ${skipped} already open"
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

echo "🩺 Doctor — Monorepo Health Check"
echo "════════════════════════════════════════"

check_prerequisites
check_symlinks
check_agents

if $QUICK; then
    skip_section 4 "Skill Lint"
    skip_section 5 "Repo Hygiene"
else
    check_skill_lint
    check_repo_hygiene
fi

check_github_actions

if $QUICK; then
    skip_section 7 "GitHub Security"
    skip_section 8 "GitHub Repo Health"
    skip_section 9 "GitHub Actions (detailed)"
    skip_section 10 "Install Health"
else
    check_github_security
    check_github_repo_health
    check_github_actions_detailed
    check_install_health
fi

# Create issues for failures if requested
if $CREATE_ISSUES; then
    section 11 "Issue Tracking"
    if [ "${#ISSUE_TITLES[@]}" -gt 0 ]; then
        create_issues
    else
        echo "   ✅ No issues to file — all checks passed"
    fi
fi

# Summary
echo ""
echo "════════════════════════════════════════"

if [ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ]; then
    echo "🩺 Result: ${PASS}/${TOTAL} passed"
elif [ "$FAIL" -eq 0 ]; then
    echo "🩺 Result: ${PASS}/${TOTAL} passed, ${WARN} warning(s)"
else
    echo "🩺 Result: ${PASS}/${TOTAL} passed, ${FAIL} failed"
    if ! $CREATE_ISSUES; then
        echo ""
        echo "   Tip: re-run with --create-issues to file GitHub issues for failures"
    fi
fi

exit "$([ "$FAIL" -eq 0 ] && echo 0 || echo 1)"
