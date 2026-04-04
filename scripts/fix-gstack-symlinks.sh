#!/bin/bash
# Normalize gstack skill symlinks to use relative paths.
# Fixes breakage caused by gstack's setup/gstack-relink scripts which
# create absolute symlinks (designed for ~/.claude installs, not vendored repos).
#
# Usage:
#   bash scripts/fix-gstack-symlinks.sh           # fix and report
#   bash scripts/fix-gstack-symlinks.sh --check   # dry-run, exit 1 if any need fixing

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

CHECK_ONLY=false
for arg in "$@"; do
    case "$arg" in
        --check) CHECK_ONLY=true ;;
    esac
done

FIXED=0
BROKEN=0
SKIPPED=0

for skill_dir in .claude/skills/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    skill_file="${skill_dir}SKILL.md"

    # Skip gstack source directory itself
    [ "$skill_name" = "gstack" ] && continue

    # Only process symlinks
    [ -L "$skill_file" ] || continue

    target=$(readlink "$skill_file" 2>/dev/null || true)

    # Check if it's an absolute path pointing to a gstack skill
    if [[ "$target" == /* ]] && [[ "$target" == *"/gstack/"* ]]; then
        if [ -f ".claude/skills/gstack/${skill_name}/SKILL.md" ]; then
            if $CHECK_ONLY; then
                echo "NEEDS FIX: ${skill_name} → ${target}"
                BROKEN=$((BROKEN + 1))
            else
                rm "$skill_file"
                ln -s "../gstack/${skill_name}/SKILL.md" "$skill_file"
                FIXED=$((FIXED + 1))
                echo "  ✅ ${skill_name}"
            fi
        else
            echo "  ⚠️  ${skill_name}: no gstack source found, skipping"
            SKIPPED=$((SKIPPED + 1))
        fi
    # Also catch broken symlinks that point to gstack paths
    elif [ ! -e "$skill_file" ] && [[ "$target" == *"/gstack/"* ]]; then
        if [ -f ".claude/skills/gstack/${skill_name}/SKILL.md" ]; then
            if $CHECK_ONLY; then
                echo "NEEDS FIX: ${skill_name} → ${target} (broken)"
                BROKEN=$((BROKEN + 1))
            else
                rm "$skill_file"
                ln -s "../gstack/${skill_name}/SKILL.md" "$skill_file"
                FIXED=$((FIXED + 1))
                echo "  ✅ ${skill_name}"
            fi
        else
            echo "  ⚠️  ${skill_name}: no gstack source found, skipping"
            SKIPPED=$((SKIPPED + 1))
        fi
    fi
done

if $CHECK_ONLY; then
    if [ "$BROKEN" -gt 0 ]; then
        echo "${BROKEN} symlink(s) need fixing. Run: bash scripts/fix-gstack-symlinks.sh"
        exit 1
    else
        echo "All gstack symlinks are relative."
        exit 0
    fi
fi

echo ""
if [ "$FIXED" -gt 0 ]; then
    echo "Fixed ${FIXED} symlink(s) to use relative paths."
fi
if [ "$SKIPPED" -gt 0 ]; then
    echo "Skipped ${SKIPPED} (no gstack source)."
fi
if [ "$FIXED" -eq 0 ] && [ "$SKIPPED" -eq 0 ]; then
    echo "All gstack symlinks already use relative paths."
fi
