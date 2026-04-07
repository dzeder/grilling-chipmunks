# Customer: Gulf Distributing

## READ-ONLY ACCESS — HARD RULE

Gulf orgs are **read-only by default**. Do not write to any Gulf org unless the user explicitly authorizes it in the current conversation.

**Allowed operations:**
- `sf org list` — check connected orgs
- `sf project retrieve start` — pull metadata down
- `sf data query` — read data via SOQL
- `sf org display` — view org info
- `sf org open` — open org in browser

**Prohibited operations (unless user explicitly authorizes):**
- `sf project deploy start` — deploy metadata
- `sf data update record` / `sf data create record` / `sf data delete record` — any DML
- `sf apex run` — anonymous Apex that modifies data
- Any destructive metadata operations (delete components, overwrite configs)

## Context loading order

When working on Gulf, read files in this order:

1. **`profile.md`** — Org topology (3 envs), 9 installed SKUs, VIP migration context
2. **`orgs/<env>/org-snapshot.md`** — Deployed metadata state (packages, objects, flows, validation rules)
3. **`integrations.md`** — VIP staging DB, GP Analytics via Tray
4. **`known-issues.md`** — Open issues, workarounds, recurring patterns
5. **`notes.md`** — Running notes from debugging sessions

## Connected orgs

Check which orgs are connected:
```bash
sf org list | grep gulf
```

Connect to an org:
```bash
bash scripts/connect-org.sh gulf --production --type customer
bash scripts/connect-org.sh gulf-cam --sandbox --type sandbox
```

After connecting, read `orgs/<env>/org-snapshot.md` for metadata counts and quick commands.

## Gulf-specific context

- **Migrating from VIP (AS400/DB2)** — migration artifacts in `docs/case-studies/gulf-vip-to-ohanafy/`
- **~8,743 items and ~927 brands** migrated from VIP
- **GP Analytics integration** via Tray.io for placements and depletions
- **VIP staging DB** at `gulfstream-db2-data.postgres.database.azure.com:5432`

## Cross-referencing

Gulf uses 9 Ohanafy SKUs. When debugging, load the relevant source indexes:
- OMS: `skills/ohanafy/ohfy-oms-expert/references/source-index.md`
- WMS: `skills/ohanafy/ohfy-wms-expert/references/source-index.md`
- REX: `skills/ohanafy/ohfy-rex-expert/references/source-index.md`
- Core: `skills/ohanafy/ohfy-core-expert/references/source-index.md`
- EDI: `skills/ohanafy/ohfy-edi-expert/references/source-index.md`

## What does NOT belong here

- Shared integration code (goes in `projects/`)
- OHFY product knowledge (goes in `skills/ohfy-*-expert/`)
- Credentials and secrets (use Named Credentials, env vars, or a vault)
