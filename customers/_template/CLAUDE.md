# Customer: {{CUSTOMER_NAME}}

## READ-ONLY ACCESS — HARD RULE

Customer orgs are **read-only by default**. Do not write to this org unless the user explicitly authorizes it in the current conversation.

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

When working on this customer, read files in this order:

1. **`profile.md`** — Org topology, installed SKUs, data profile, external systems, customization delta
2. **`orgs/<env>/org-snapshot.md`** — Deployed metadata state (packages, objects, flows, validation rules)
3. **`integrations.md`** — Integration inventory, Tray projects, named credentials
4. **`known-issues.md`** — Open issues, workarounds, recurring patterns
5. **`notes.md`** — Running notes from debugging sessions

## Connected orgs

Check which orgs are connected:
```bash
sf org list | grep {{alias}}
```

Connect to an org:
```bash
bash scripts/connect-org.sh {{customer-name}} --production --type customer
bash scripts/connect-org.sh {{customer-name}} --sandbox --type sandbox
```

After connecting, read `orgs/<env>/org-snapshot.md` for metadata counts and quick commands.

## What belongs here

- `profile.md` — Customer overview, org topology, installed SKUs, data profile, customization delta
- `orgs/<env>/` — Per-environment metadata retrieved by connect-org.sh
- `integrations.md` — Integration inventory, Tray projects, credentials, sync patterns
- `known-issues.md` — Open issues, workarounds, recurring patterns
- `notes.md` — Running notes from debugging sessions, design decisions, gotchas
- `customizations.md` — Custom fields, picklist values, validation rules that differ from standard OHFY

## What does NOT belong here

- Shared integration code (goes in `projects/`)
- OHFY product knowledge (goes in `skills/ohfy-*-expert/`)
- Credentials and secrets (use Named Credentials, env vars, or a vault)

## Cross-referencing

When debugging this customer, also load the relevant OHFY package source indexes:
- Check which SKUs are installed in `profile.md`
- Read `skills/ohanafy/ohfy-<package>-expert/references/source-index.md` for trigger maps, service graphs, and patterns
