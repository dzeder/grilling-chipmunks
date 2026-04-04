#!/bin/bash
# Normalize gstack skill symlinks and ensure skills/ discovery directory is populated.
# Fixes two issues:
#   1. gstack's setup/gstack-relink scripts create absolute symlinks
#   2. gstack skills missing from skills/ (where Claude Code discovers them)
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

# ── Part 1: Fix .claude/skills/ symlinks (absolute → relative) ──

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
                echo "NEEDS FIX: .claude/skills/${skill_name} → ${target}"
                BROKEN=$((BROKEN + 1))
            else
                rm "$skill_file"
                ln -s "../gstack/${skill_name}/SKILL.md" "$skill_file"
                FIXED=$((FIXED + 1))
                echo "  ✅ .claude/skills/${skill_name}"
            fi
        else
            echo "  ⚠️  ${skill_name}: no gstack source found, skipping"
            SKIPPED=$((SKIPPED + 1))
        fi
    # Also catch broken symlinks that point to gstack paths
    elif [ ! -e "$skill_file" ] && [[ "$target" == *"/gstack/"* ]]; then
        if [ -f ".claude/skills/gstack/${skill_name}/SKILL.md" ]; then
            if $CHECK_ONLY; then
                echo "NEEDS FIX: .claude/skills/${skill_name} → ${target} (broken)"
                BROKEN=$((BROKEN + 1))
            else
                rm "$skill_file"
                ln -s "../gstack/${skill_name}/SKILL.md" "$skill_file"
                FIXED=$((FIXED + 1))
                echo "  ✅ .claude/skills/${skill_name}"
            fi
        else
            echo "  ⚠️  ${skill_name}: no gstack source found, skipping"
            SKIPPED=$((SKIPPED + 1))
        fi
    fi
done

# ── Part 2: Ensure skills/ discovery directory has entries for all gstack skills ──
# Claude Code discovers skills from skills/ at the repo root.
# Without entries there, gstack slash commands (/ship, /browse, etc.) won't work.

for gstack_skill_dir in .claude/skills/gstack/*/; do
    [ -d "$gstack_skill_dir" ] || continue
    skill_name=$(basename "$gstack_skill_dir")
    gstack_skill_file="${gstack_skill_dir}SKILL.md"
    [ -f "$gstack_skill_file" ] || continue

    discovery_dir="skills/${skill_name}"
    discovery_file="${discovery_dir}/SKILL.md"

    # Skip if already exists and is valid
    if [ -f "$discovery_file" ]; then
        continue
    fi

    if $CHECK_ONLY; then
        echo "NEEDS FIX: skills/${skill_name}/ missing (skill not discoverable)"
        BROKEN=$((BROKEN + 1))
    else
        mkdir -p "$discovery_dir"
        ln -s "../../.claude/skills/gstack/${skill_name}/SKILL.md" "$discovery_file"
        FIXED=$((FIXED + 1))
        echo "  ✅ skills/${skill_name}/ (discoverable)"
    fi
done

if $CHECK_ONLY; then
    if [ "$BROKEN" -gt 0 ]; then
        echo "${BROKEN} symlink(s) need fixing. Run: bash scripts/fix-gstack-symlinks.sh"
        exit 1
    else
        echo "All gstack symlinks are relative and discoverable."
        exit 0
    fi
fi

echo ""
if [ "$FIXED" -gt 0 ]; then
    echo "Fixed ${FIXED} symlink(s)."
fi
if [ "$SKIPPED" -gt 0 ]; then
    echo "Skipped ${SKIPPED} (no gstack source)."
fi
if [ "$FIXED" -eq 0 ] && [ "$SKIPPED" -eq 0 ]; then
    echo "All gstack symlinks already correct and discoverable."
fi
