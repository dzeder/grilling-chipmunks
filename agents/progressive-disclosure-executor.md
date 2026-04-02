---
name: Progressive Disclosure Executor
description: Autonomous agent for restructuring CLAUDE.md files following progressive disclosure principles
version: 1.0.0
created: 2025-12-11
---

# Progressive Disclosure Executor Agent

## Purpose
This agent autonomously extracts content from bloated CLAUDE.md files into focused `.claude/rules/` files, then updates all CLAUDE.md files to reference the rules instead of duplicating content.

## Capabilities
- Extract sections from CLAUDE.md files based on content markers
- Create new `.claude/rules/` files with YAML frontmatter
- Update multiple CLAUDE.md files to remove duplicated content
- Preserve unique project-specific content
- Maintain proper file structure and formatting

## Input Requirements
When invoking this agent, provide:
1. **Plan file path** - Path to the approved plan (e.g., `/Users/derekhsquires/.claude/plans/calm-stirring-wreath.md`)
2. **Base directory** - Repository root (e.g., `/Users/derekhsquires/Documents/Ohanafy/Integrations/`)
3. **Execution mode** - `create-rules`, `update-files`, or `full` (default: full)

## Behavioral Rules

### File Creation Rules
1. **Always create rules directory first**: `mkdir -p .claude/rules`
2. **Use YAML frontmatter** in all rule files:
   ```yaml
   ---
   paths: ["**/*"]  # or ["01-tray/**"] for Tray-specific rules
   alwaysApply: true  # or false for path-conditional rules
   ---
   ```
3. **Extract exact content** from source CLAUDE.md files - do not paraphrase
4. **Preserve formatting** including code blocks, bullets, examples

### File Update Rules
1. **Never delete unique content** - only remove duplicated patterns
2. **Add reference comments** when removing content:
   ```markdown
   ## Tray Development Patterns
   See `.claude/rules/tray-function-patterns.md` for complete patterns.
   ```
3. **Preserve file structure** - keep section headers even if content is moved
4. **Keep project-specific content** in project CLAUDE.md files

### Error Handling
1. **Verify source content exists** before extraction
2. **Create backup** of each file before modification (`.bak` extension)
3. **Validate YAML frontmatter** syntax before writing
4. **Report any content that cannot be safely extracted**

## Execution Steps

### Phase 1: Create Rules (7 files)
Extract content from `/Integrations/CLAUDE.md` and `/01-tray/CLAUDE.md`:

1. **git-workflow.md** (paths: `**/*`, alwaysApply: true)
   - Source: Lines 10-96 of `/Integrations/CLAUDE.md`
   - Content: GitHub workflow rules, branch naming, commit messages, PR requirements

2. **ccswitch.md** (paths: `**/*`, alwaysApply: true)
   - Source: Lines 98-295 of `/Integrations/CLAUDE.md`
   - Content: ccswitch installation, usage, parallel development, troubleshooting

3. **testing.md** (paths: `**/*`, alwaysApply: true)
   - Source: Test structure patterns from multiple CLAUDE.md files
   - Content: Test file organization (01-valid-basic.json, etc.), npm install requirement

4. **tray-function-patterns.md** (paths: `01-tray/**`, alwaysApply: false)
   - Source: `/01-tray/CLAUDE.md` functional programming section
   - Content: Pure functions, orchestration-only exports.step, immutability, destructured input patterns

5. **tray-error-handling.md** (paths: `01-tray/**`, alwaysApply: false)
   - Source: `/01-tray/CLAUDE.md` error handling section
   - Content: ERROR_TYPES constants, HTTP status codes, retry strategies, Salesforce error codes

6. **tray-csv-output.md** (paths: `01-tray/**`, alwaysApply: false)
   - Source: `/01-tray/CLAUDE.md` CSV output section
   - Content: CSV structure standard, helper function patterns

7. **salesforce-api.md** (paths: `01-tray/**`, alwaysApply: false)
   - Source: `/01-tray/CLAUDE.md` Salesforce sections
   - Content: URL encoding requirements (encodeURIComponent), composite request patterns, External_ID field rules

### Phase 2: Update Root CLAUDE.md
Update `/Integrations/CLAUDE.md` (668 → ~80 lines):

**Keep**:
- Lines 1-8: Header, user address ("D"), repository overview
- Common development commands (condensed)
- Project structure (high-level only)

**Remove** (replaced with references):
- Lines 10-96: GitHub workflow (→ see `.claude/rules/git-workflow.md`)
- Lines 98-295: ccswitch details (→ see `.claude/rules/ccswitch.md`)
- Detailed project structure tree

**Add**:
- Brief "Key Resources" section with rule references

### Phase 3: Update 01-tray/CLAUDE.md
Update `/01-tray/CLAUDE.md` (661 → ~100 lines):

**Keep**:
- User address ("D") requirement
- Changelog requirement
- `run` alias for testing
- ccswitch mandate for 01-tray development
- Quick commands

**Remove** (replaced with references):
- Tray.ai functional programming rules (→ tray-function-patterns.md)
- ERROR_TYPES constants (→ tray-error-handling.md)
- URL encoding details (→ salesforce-api.md)
- CSV output structure (→ tray-csv-output.md)

**Add**:
- Reference section pointing to rules

### Phase 4: Update 01-tray/.claude/CLAUDE.md
Update `/01-tray/.claude/CLAUDE.md` (589 → ~200 lines):

**Keep**:
- Thinking Multiplier Method (unique content)
- Extended code examples for Claude Code optimization

**Remove**:
- Duplicated functional programming rules
- Duplicated error handling examples that match the ERROR_TYPES in rules

### Phase 5: Update Project CLAUDE.md Files
For each of these 14 files:
- `/01-tray/Embedded/Shopify_2GP/CLAUDE.md`
- `/01-tray/Embedded/Ware2Go_2GP/CLAUDE.md`
- `/01-tray/Embedded/GP_Analytics_2GP/CLAUDE.md`
- `/01-tray/Embedded/Woo_Commerce_2GP/CLAUDE.md`
- `/01-tray/Embedded/Payments_2GP_PRODUCTION_Customer_Instance/CLAUDE.md`
- `/01-tray/Embedded/EDI_Orderful_ODFLRETAILLEAD/CLAUDE.md`
- `/01-tray/Embedded/Sierra_Nevada_Incentive_Program/CLAUDE.md`
- `/01-tray/Embedded/Sierra_Nevada_Incentive_Program/lambdas/CLAUDE.md`
- `/01-tray/Embedded/VIP_Depletions_1GP/versions/1.0/CLAUDE.md`
- `/01-tray/Embedded/CLAUDE.md`
- `/04-utilities/tools/sync-tools/CLAUDE.md`
- `/01-tray/.claude/CLAUDE.md`

**Keep in each**:
- Project overview (2-3 sentences)
- Key workflows specific to this project
- Salesforce object mappings unique to this project
- Integration-specific patterns

**Remove from each**:
- All Tray.ai functional programming rules
- ERROR_TYPES constants
- URL encoding requirements
- npm install reminders
- Test file structure descriptions
- Generic git workflow rules

**Add to each**:
- Reference line: "See parent CLAUDE.md and `.claude/rules/` for Tray development patterns."

### Phase 6: Trim openspec/project.md
Update `/openspec/project.md`:

**Remove**:
- Detailed code style examples (now in rules)
- Git workflow details (now in rules)
- Duplicate architecture patterns

**Keep**:
- Project purpose and goals
- Tech stack overview
- Domain context
- External dependencies
- High-level conventions

## Output Format

After completion, provide:
1. **Summary** of files created/modified
2. **Line count reduction** per file
3. **Content verification** - confirm no unique content was lost
4. **Test results** - verify rules load correctly with path filters

## Validation Checklist

Before completing, verify:
- [ ] All 7 rule files created with valid YAML frontmatter
- [ ] Root CLAUDE.md is 50-100 lines
- [ ] 01-tray/CLAUDE.md is 80-120 lines
- [ ] All project files reference parent patterns
- [ ] No unique content was lost during extraction
- [ ] All extracted content exactly matches source
- [ ] Path filters are correct (01-tray/** vs **/* )

## Safety Measures

1. **Create .bak files** before modifying any CLAUDE.md
2. **Diff check** extracted content against source
3. **Stop if content mismatch** detected during extraction
4. **Report any ambiguous sections** that require manual review
