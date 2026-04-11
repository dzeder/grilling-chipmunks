# VIP SRS Expert — Source Index

> Last synced: 2026-04-10 | Source: ISV Spec v6.0 (Jan 2023) + 22 PDF file specs

## Knowledge Base

- `knowledge-base/vip-srs/README.md` — Master index of all 22 file types
- `knowledge-base/vip-srs/valid-values.md` — Complete coded field value reference
- `knowledge-base/vip-srs/isv-spec-overview.md` — File format conventions, SFTP, naming
- `knowledge-base/vip-srs/file-types/*.md` — Per-file detailed field layouts
- `knowledge-base/vip-srs/appendices/*.md` — Repack logic, zero sales, summary inventory, depletion warehouse, retroactive discounts

## Integration Implementation

- `integrations/vip-srs/docs/VIP_AGENT_HANDOFF.md` — THE source of truth for VIP-to-Ohanafy mapping
- `integrations/vip-srs/CLAUDE.md` — Technical implementation context
- `integrations/vip-srs/ROADMAP.md` — Project history, gotchas, key decisions
- `integrations/vip-srs/shared/constants.js` — Crosswalk maps and external ID prefixes
- `integrations/vip-srs/shared/external-ids.js` — Key generators for all 12 object types
- `integrations/vip-srs/scripts/*.js` — 10 production transform scripts + E2E runner
- `integrations/vip-srs/tests/fixtures/*.csv` — Sample data files

## Salesforce Metadata

- `customers/shipyard-ros2/deploy-v2/` — VIP custom fields and permission set
