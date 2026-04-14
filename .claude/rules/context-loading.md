---
globs:
  - "customers/**/*"
  - "skills/ohanafy/**/*"
  - "integrations/**/*"
---

# Context Loading Protocol

Before starting any task, determine what context to pre-load.

## Workspace context (check first)

If `.context/workspace.md` exists and was created today, read it first. It contains:
- Active customer and integration
- Which environment to target
- Which context files have already been loaded
- Suggested branch name

This was set by `/kickoff`. Use it instead of branch-name parsing when available.

## Customer context (branch or task mentions a customer)

Parse the branch name: if it matches `dzeder/<customer>-*`, match against `customers/` directories.

If a customer is identified:
- Read `customers/<customer>/profile.md` for org topology, SKUs, external systems
- Read `customers/<customer>/orgs/<env>/org-snapshot.md` if it exists
- Check `customers/<customer>/notes.md` and `known-issues.md` for prior learnings

Known customers: `ls customers/` (exclude `_template`).

## Package context (task mentions an Ohanafy package)

If the task mentions OMS, WMS, REX, EDI, Ecom, Payments, Configure, Platform, Core, or Data Model:
- Read `skills/ohanafy/ohfy-<package>-expert/references/source-index.md`
- Check `references/last-synced.txt` — if >7 days stale, suggest refresh

## VIP SRS context (task mentions VIP, SRS, distributor data files, SFTP distribution files)

If the task mentions VIP, SRS, SLSDA, OUTDA, INVDA, CTLDA, DISTDA, ITM2DA, ITMDA, SRSCHAIN, SRSVALUE, or any VIP file type:
- Read `skills/ohanafy/ohfy-vip-srs-expert/SKILL.md` for domain coverage and routing
- Read `integrations/vip-srs/CLAUDE.md` for implementation context
- For reports/dashboards/field questions: read `integrations/vip-srs/docs/VIP_DATA_DICTIONARY.md`
- For file format questions: read `knowledge-base/vip-srs/isv-spec-overview.md`
- For coded values: read `knowledge-base/vip-srs/valid-values.md`
- For specific file types: read `knowledge-base/vip-srs/file-types/{FILE_TYPE}.md`
- For field mappings to Ohanafy: read `integrations/vip-srs/docs/VIP_AGENT_HANDOFF.md`

## Integration context (task mentions Tray, connector, sync, mapping)

- Read `integrations/patterns/README.md` for available pattern modules
- Read relevant pattern files (e.g., `batch-processing.js`, `data-mapping.js`)
- Read `docs/integration-guides/OHFY_INTEGRATION_MASTER_GUIDE.md` for methodology

## Debugging context (task mentions error, bug, failing, broken)

Load BOTH customer profile AND package source index. The source index includes:
- Trigger → Handler Map
- Service Layer Graph
- Common Patterns (bypass, batch chains, queueable)
- Cross-Object Relationships

## Session probe context (auto-detected)

If `scripts/session-context-probe.sh` output was received at session start, use it:
- Load customer profile if `customer=<name>` was detected
- Load integration context if `integration=<name>` was detected
- Check stale indexes if `stale=[...]` was reported
- Use `domains=[...]` to pre-load the most relevant routing context

This replaces keyword matching when probe data is available.

## Skill-activated context loading

When a skill is invoked via `/skillname`:
1. Read the skill's SKILL.md frontmatter
2. If `context_requires.always` lists files, load them before the skill executes
3. If `context_requires.conditional` lists files, evaluate against `.context/workspace.md`
4. If the skill has `knowledge_refs`, load those files
5. Total loaded context should not exceed 3 knowledge files per task

## Knowledge discovery

When working on a task that touches a specific domain:
1. Check `knowledge-base/INDEX.yaml` for the domain
2. Load files whose keywords match the task
3. Prefer files already referenced by the active skill's `knowledge_refs`
