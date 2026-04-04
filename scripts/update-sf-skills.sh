#!/bin/bash
set -euo pipefail

# update-sf-skills.sh — Preview upstream sf-skills changes (cherry-pick only, no auto-apply)
# Usage:
#   bash scripts/update-sf-skills.sh              # show what changed upstream
#   bash scripts/update-sf-skills.sh --mark-reviewed   # update version marker to current upstream HEAD

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UPSTREAM_REPO="Jaganpro/sf-skills"
VERSION_FILE="${REPO_ROOT}/skills/.sf-skills-upstream-version"
TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/sf-skills-upstream-XXXXXX")
MODE="${1:---preview}"

trap 'rm -rf "$TMP_DIR"' EXIT

echo "=== sf-skills Upstream Check ==="
echo "    Upstream: ${UPSTREAM_REPO}"
echo ""

# Read current version marker
if [ -f "$VERSION_FILE" ]; then
    CURRENT_HASH=$(cat "$VERSION_FILE" | tr -d '[:space:]')
    echo "Last reviewed: ${CURRENT_HASH:0:8}"
else
    CURRENT_HASH="none"
    echo "Last reviewed: not tracked (first run)"
fi

# Clone upstream
echo "Fetching upstream..."
git clone --depth 100 "https://github.com/${UPSTREAM_REPO}.git" "$TMP_DIR"
UPSTREAM_HASH=$(cd "$TMP_DIR" && git log --format='%H' -1)
echo "Upstream HEAD: ${UPSTREAM_HASH:0:8}"
echo ""

if [ "$CURRENT_HASH" == "$UPSTREAM_HASH" ]; then
    echo "Already up to date. No new upstream changes."
    exit 0
fi

# If --mark-reviewed, just update the version marker
if [ "$MODE" == "--mark-reviewed" ]; then
    echo "$UPSTREAM_HASH" > "$VERSION_FILE"
    echo "Version marker updated to ${UPSTREAM_HASH:0:8}"
    echo "This means: you've reviewed upstream through this commit."
    exit 0
fi

# === Commit log ===
echo "=== Upstream commits since last review ==="
if [ "$CURRENT_HASH" != "none" ]; then
    if ! (cd "$TMP_DIR" && git log --oneline "${CURRENT_HASH}..HEAD" 2>/dev/null); then
        echo "(hash ${CURRENT_HASH:0:8} not in shallow clone — showing last 20 commits)"
        (cd "$TMP_DIR" && git log --oneline -20)
    fi
else
    echo "(first run — showing last 20 commits)"
    (cd "$TMP_DIR" && git log --oneline -20)
fi
echo ""

# === Per-skill diff ===
echo "=== Skill-by-skill changes ==="

NEW_COUNT=0
CHANGED_COUNT=0
UNCHANGED_COUNT=0

for upstream_skill_dir in "$TMP_DIR"/skills/sf-*/; do
    [ -d "$upstream_skill_dir" ] || continue
    skill_name=$(basename "$upstream_skill_dir")
    local_skill_dir="${REPO_ROOT}/skills/${skill_name}"

    if [ ! -d "$local_skill_dir" ]; then
        echo "  + NEW: ${skill_name}"
        NEW_COUNT=$((NEW_COUNT + 1))
        continue
    fi

    # Compare the two directories
    DIFF_OUTPUT=$(diff -rq "$local_skill_dir" "$upstream_skill_dir" \
        --exclude='.DS_Store' \
        --exclude='__pycache__' \
        2>/dev/null || true)

    if [ -z "$DIFF_OUTPUT" ]; then
        UNCHANGED_COUNT=$((UNCHANGED_COUNT + 1))
        continue
    fi

    CHANGED_COUNT=$((CHANGED_COUNT + 1))
    echo "  ~ CHANGED: ${skill_name}"

    # Break down what changed
    CHANGED_FILES=$(echo "$DIFF_OUTPUT" | grep "^Files.*differ$" || true)
    NEW_FILES=$(echo "$DIFF_OUTPUT" | grep "Only in $upstream_skill_dir" || true)
    REMOVED_FILES=$(echo "$DIFF_OUTPUT" | grep "Only in $local_skill_dir" || true)

    if [ -n "$CHANGED_FILES" ]; then
        echo "$CHANGED_FILES" | while read -r line; do
            # Extract just the relative filename
            fname=$(echo "$line" | sed "s|.*${skill_name}/||; s| and .*||; s| differ||")
            echo "      modified: ${fname}"
        done
    fi
    if [ -n "$NEW_FILES" ]; then
        echo "$NEW_FILES" | while read -r line; do
            fname="${line##*: }"
            echo "      new upstream: ${fname}"
        done
    fi
    if [ -n "$REMOVED_FILES" ]; then
        echo "$REMOVED_FILES" | while read -r line; do
            fname="${line##*: }"
            echo "      local only: ${fname}"
        done
    fi
done
echo ""

# === Agents diff ===
echo "=== Agent changes ==="
AGENT_CHANGES=false
for upstream_agent in "$TMP_DIR"/agents/*.md; do
    [ -f "$upstream_agent" ] || continue
    agent_name=$(basename "$upstream_agent")
    local_agent="${REPO_ROOT}/agents/${agent_name}"

    if [ ! -f "$local_agent" ]; then
        echo "  + NEW: ${agent_name}"
        AGENT_CHANGES=true
    elif ! diff -q "$local_agent" "$upstream_agent" > /dev/null 2>&1; then
        echo "  ~ CHANGED: ${agent_name}"
        AGENT_CHANGES=true
    fi
done
if [ "$AGENT_CHANGES" = false ]; then
    echo "  (no changes)"
fi
echo ""

# === Shared infrastructure diff ===
echo "=== Shared infrastructure ==="
INFRA_CHANGES=false
for dir in shared tools tests; do
    if [ -d "$TMP_DIR/$dir" ] && [ -d "$REPO_ROOT/$dir" ]; then
        DIFF_OUTPUT=$(diff -rq "$REPO_ROOT/$dir" "$TMP_DIR/$dir" \
            --exclude='.DS_Store' \
            --exclude='__pycache__' \
            --exclude='node_modules' \
            2>/dev/null || true)
        if [ -n "$DIFF_OUTPUT" ]; then
            CHANGE_COUNT=$(echo "$DIFF_OUTPUT" | wc -l | tr -d ' ')
            echo "  ~ ${dir}/: ${CHANGE_COUNT} file(s) differ"
            INFRA_CHANGES=true
        fi
    elif [ -d "$TMP_DIR/$dir" ] && [ ! -d "$REPO_ROOT/$dir" ]; then
        echo "  + ${dir}/: new upstream (not present locally)"
        INFRA_CHANGES=true
    fi
done
if [ "$INFRA_CHANGES" = false ]; then
    echo "  (no changes)"
fi
echo ""

# === Summary ===
echo "=== Summary ==="
echo "  New skills:       ${NEW_COUNT}"
echo "  Changed skills:   ${CHANGED_COUNT}"
echo "  Unchanged skills: ${UNCHANGED_COUNT}"
echo ""
echo "This is PREVIEW ONLY. sf-skills uses cherry-pick workflow."
echo ""
echo "To cherry-pick improvements:"
echo "  git remote add sf-skills-upstream https://github.com/${UPSTREAM_REPO}.git"
echo "  git fetch sf-skills-upstream"
echo "  git cherry-pick <sha>"
echo ""
echo "After reviewing, update the version marker:"
echo "  bash scripts/update-sf-skills.sh --mark-reviewed"
