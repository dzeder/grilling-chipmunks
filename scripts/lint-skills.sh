#!/bin/bash
# Lint all skills for consistency against the skill template
# Usage:
#   bash scripts/lint-skills.sh              # lint all skills
#   bash scripts/lint-skills.sh sf-apex      # lint one skill
#   bash scripts/lint-skills.sh --summary    # compact output

set -euo pipefail

SKILLS_DIR="skills"
TARGET="${1:-}"
SUMMARY=false
[[ "$TARGET" == "--summary" ]] && SUMMARY=true && TARGET=""

PASS=0
WARN=0
FAIL=0
TOTAL=0
REPORT=""

lint_skill() {
    local skill_dir="$1"
    local skill_name=$(basename "$skill_dir")
    local skill_file="${skill_dir}/SKILL.md"
    local checks_passed=0
    local checks_warned=0
    local checks_failed=0
    local details=""

    if [ ! -f "$skill_file" ]; then
        details+="  FAIL: No SKILL.md found\n"
        checks_failed=$((checks_failed + 1))
        if ! $SUMMARY; then
            echo "--- ${skill_name} ---"
            echo -e "$details"
        fi
        REPORT+="${skill_name}: FAIL (no SKILL.md)\n"
        FAIL=$((FAIL + 1))
        TOTAL=$((TOTAL + 1))
        return
    fi

    # Check 1: YAML frontmatter with name field
    if head -5 "$skill_file" | grep -q "^name:"; then
        checks_passed=$((checks_passed + 1))
    else
        details+="  FAIL: Missing 'name' in YAML frontmatter\n"
        checks_failed=$((checks_failed + 1))
    fi

    # Check 2: Description with trigger rules
    if grep -qi "trigger when" "$skill_file" 2>/dev/null; then
        checks_passed=$((checks_passed + 1))
    else
        details+="  WARN: No TRIGGER WHEN rules in description\n"
        checks_warned=$((checks_warned + 1))
    fi

    # Check 3: Delegate/handoff section
    if grep -qi "delegate\|hand.off\|route to\|do not trigger" "$skill_file" 2>/dev/null; then
        checks_passed=$((checks_passed + 1))
    else
        details+="  WARN: No delegation/handoff section found\n"
        checks_warned=$((checks_warned + 1))
    fi

    # Check 4: Examples or scenarios
    if grep -qi "example\|when to use\|scenario\|use case" "$skill_file" 2>/dev/null; then
        checks_passed=$((checks_passed + 1))
    else
        details+="  WARN: No examples or use-case section\n"
        checks_warned=$((checks_warned + 1))
    fi

    # Check 5: Workflow or steps
    if grep -qi "workflow\|step [0-9]\|### [0-9]" "$skill_file" 2>/dev/null; then
        checks_passed=$((checks_passed + 1))
    else
        details+="  WARN: No workflow/steps section\n"
        checks_warned=$((checks_warned + 1))
    fi

    # Check 6: Scoring rubric (optional but tracked)
    if grep -qi "score\|rubric\|points\|scoring" "$skill_file" 2>/dev/null; then
        checks_passed=$((checks_passed + 1))
    else
        details+="  INFO: No scoring rubric (optional)\n"
    fi

    # Check 7: References directory
    if [ -d "${skill_dir}/references" ]; then
        checks_passed=$((checks_passed + 1))

        # Check staleness of source index
        local last_synced="${skill_dir}/references/last-synced.txt"
        if [ -f "$last_synced" ]; then
            local sync_date=$(head -1 "$last_synced" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || echo "")
            if [ -n "$sync_date" ]; then
                local days_old=$(( ($(date +%s) - $(date -j -f "%Y-%m-%d" "$sync_date" +%s 2>/dev/null || date -d "$sync_date" +%s 2>/dev/null || echo "0")) / 86400 ))
                if [ "$days_old" -gt 14 ]; then
                    details+="  WARN: Source index stale (${days_old} days old)\n"
                    checks_warned=$((checks_warned + 1))
                fi
            fi
        fi
    else
        details+="  INFO: No references/ directory\n"
    fi

    # Determine overall status
    local status="PASS"
    if [ "$checks_failed" -gt 0 ]; then
        status="FAIL"
        FAIL=$((FAIL + 1))
    elif [ "$checks_warned" -gt 0 ]; then
        status="WARN"
        WARN=$((WARN + 1))
    else
        PASS=$((PASS + 1))
    fi
    TOTAL=$((TOTAL + 1))

    if $SUMMARY; then
        local icon="✓"
        [ "$status" == "WARN" ] && icon="△"
        [ "$status" == "FAIL" ] && icon="✗"
        REPORT+="  ${icon} ${skill_name} (${checks_passed}P/${checks_warned}W/${checks_failed}F)\n"
    else
        echo "--- ${skill_name} [${status}] ---"
        echo "  Passed: ${checks_passed}  Warned: ${checks_warned}  Failed: ${checks_failed}"
        if [ -n "$details" ]; then
            echo -e "$details"
        fi
    fi
}

echo "=== Skill Lint Report ==="
echo "Template: docs/SKILL_TEMPLATE.md"
echo ""

if [ -n "$TARGET" ]; then
    # Lint single skill
    if [ -d "${SKILLS_DIR}/${TARGET}" ]; then
        lint_skill "${SKILLS_DIR}/${TARGET}"
    else
        echo "Skill not found: ${TARGET}"
        exit 1
    fi
else
    # Lint all skills
    for skill_dir in "${SKILLS_DIR}"/*/; do
        [ -d "$skill_dir" ] || continue
        lint_skill "$skill_dir"
    done
fi

echo ""
echo "=== Summary ==="
if $SUMMARY; then
    echo -e "$REPORT"
fi
echo "Total: ${TOTAL}  Pass: ${PASS}  Warn: ${WARN}  Fail: ${FAIL}"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
