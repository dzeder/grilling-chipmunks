#!/bin/bash
# Unified health check for the riyadh monorepo
# Usage:
#   bash scripts/doctor.sh                   # full check (all 7 sections)
#   bash scripts/doctor.sh --quick           # fast check (prereqs, symlinks, agents, GH Actions)
#   bash scripts/doctor.sh --create-issues   # full check + file GitHub issues for failures

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# Validate we're in the right repo
if [ ! -f CLAUDE.md ] || [ ! -d agents ] || [ ! -d .claude/skills ]; then
    echo "❌ Not in the riyadh monorepo root"
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
        gh_user=$(gh auth status 2>&1 | grep -oE 'Logged in to github.com as [^ ]+' | awk '{print $NF}' || true)
        if [ -n "$gh_user" ]; then
            echo "   ✅ gh ${gh_ver} (authenticated as ${gh_user})"
        else
            echo "   ⚠️  gh ${gh_ver} (not authenticated — run 'gh auth login')"
            GH_AUTH_OK=false
            issues=$((issues + 1))
            missing+="- \`gh\` installed but not authenticated\n"
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
            if [ -e "$skill_file" ]; then
                valid=$((valid + 1))
            else
                broken=$((broken + 1))
                local target
                target=$(readlink "$skill_file" 2>/dev/null || echo "unknown")
                broken_list+="   ❌ ${skill_name} → ${target}\n"
                broken_md+="- \`${skill_name}\` → \`${target}\`\n"
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
            "$(printf "${broken} of ${total} skill symlinks in \`.claude/skills/\` are broken:\n\n%b\nClaude Code cannot discover these skills until the symlinks are fixed.\n\n**How to fix:** Re-run \`bash scripts/update-gstack.sh\` or \`bash scripts/update-sf-skills.sh\`, then verify with \`bash scripts/doctor.sh --quick\`." "$broken_md")"
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

    echo "$output" | sed 's/^/   /'

    if [ "$exit_code" -eq 0 ]; then
        record_pass
    else
        # Extract failure count from summary line
        local fail_count
        fail_count=$(echo "$output" | grep -oE 'Fail: [0-9]+' | awk '{print $2}' || echo "?")
        record_fail
        queue_issue \
            "Doctor: ${fail_count} skills failing lint" \
            "$(printf "\`scripts/lint-skills.sh\` reports ${fail_count} skill(s) failing structural checks.\n\nRun \`bash scripts/lint-skills.sh\` for full details.\n\nSee \`docs/SKILL_TEMPLATE.md\` for required structure.")"
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
        missing_count=$(echo "$output" | grep -c '^MISSING' 2>/dev/null || echo "0")
        anchor_count=$(echo "$output" | grep -c '^ANCHOR' 2>/dev/null || echo "0")
        forbidden_count=$(echo "$output" | grep -c '^FORBIDDEN' 2>/dev/null || echo "0")
        echo "   ❌ ${issue_count} hygiene issues (${missing_count} missing links, ${anchor_count} broken anchors, ${forbidden_count} forbidden patterns)"
        record_fail
        queue_issue \
            "Doctor: ${issue_count} repo hygiene issues" \
            "$(printf "\`tools/check_repo_hygiene.py\` found ${issue_count} issue(s):\n\n| Type | Count |\n|------|-------|\n| Missing link targets | ${missing_count} |\n| Broken anchors | ${anchor_count} |\n| Forbidden patterns | ${forbidden_count} |\n\nMost are missing \`references/*.md\` files that skills link to but haven't been created yet.\n\nRun \`python3 tools/check_repo_hygiene.py\` for full details.")"
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
# Section 7: Install Health (delegated)
# ─────────────────────────────────────────────

check_install_health() {
    section 7 "Install Health"

    if [ ! -f tools/install.py ]; then
        echo "   ❌ tools/install.py not found"
        record_fail
        return
    fi

    local exit_code=0
    local output
    output=$(python3 tools/install.py --diagnose 2>&1) || exit_code=$?

    echo "$output" | sed 's/^/   /'

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

echo "🩺 Doctor — Riyadh Monorepo Health Check"
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
    skip_section 7 "Install Health"
else
    check_install_health
fi

# Create issues for failures if requested
if $CREATE_ISSUES; then
    section 8 "Issue Tracking"
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

exit $([ "$FAIL" -eq 0 ] && echo 0 || echo 1)
