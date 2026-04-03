# Customer: {{CUSTOMER_NAME}}

## How to use this directory

This directory captures everything specific to this customer's Salesforce/Ohanafy instance.
Agents should read `profile.md` first for context, then check `orgs/` for environment-specific metadata.

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

- `profile.md` — Customer overview, org topology, installed SKUs, key contacts
- `orgs/<env>/` — Per-environment metadata retrieved by connect-org.sh
- `customizations.md` — Custom fields, picklist values, validation rules that differ from standard OHFY
- `integrations.md` — What systems they connect to, credentials, sync patterns
- `notes.md` — Running notes from debugging sessions, design decisions, gotchas

## What does NOT belong here

- Shared integration code (goes in `projects/`)
- OHFY product knowledge (goes in `skills/ohfy-*-expert/`)
- Credentials and secrets (use Named Credentials, env vars, or a vault)
