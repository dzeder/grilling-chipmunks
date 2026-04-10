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
