# Customers

Per-customer knowledge about their Salesforce/Ohanafy configurations, metadata, and customizations.

## Directory structure

```
customers/
├── _template/           # Copy this to create a new customer
│   ├── CLAUDE.md        # Agent instructions for this customer
│   ├── profile.md       # Customer overview, org topology, data profile
│   └── orgs/            # Per-environment metadata (populated by connect-org.sh)
├── gulf/                # Gulf Distributing
│   ├── CLAUDE.md
│   ├── profile.md
│   ├── customizations.md   # (created as learned)
│   ├── integrations.md     # (created as learned)
│   ├── notes.md            # (created as learned)
│   └── orgs/
│       ├── production/     # (populated by connect-org.sh)
│       └── cam-sandbox/    # (populated by connect-org.sh)
└── ...
```

## Adding a new customer

```bash
cp -r customers/_template customers/<customer-name>
# Edit customers/<customer-name>/profile.md with what you know
# Connect to their org:
bash scripts/connect-org.sh <customer-name> --production --type customer
```

## How agents use this

1. Read `customers/<name>/profile.md` for customer context before any customer-specific work
2. Read `customers/<name>/orgs/<env>/org-snapshot.md` for deployed metadata state
3. Check `customizations.md`, `integrations.md`, `notes.md` if they exist
4. When you learn something customer-specific during a session, write it here — not in memory

## What goes here vs elsewhere

| Content | Location |
|---------|----------|
| Customer org config, metadata, customizations | `customers/<name>/` |
| Shared integration code (QuickBooks, NetSuite, etc.) | `projects/` |
| OHFY product knowledge (how OMS works, trigger patterns) | `skills/ohfy-*-expert/` |
| Integration patterns and templates | `integrations/patterns/` |
