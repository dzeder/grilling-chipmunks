# Ohanafy Source Sync Roadmap

How skills and agents access the Ohanafy product codebase — current state and evolution path.

## Current State: Option 1 — Clone on Demand

Each SKU expert skill (`ohfy-oms-expert`, `ohfy-wms-expert`, etc.) clones the relevant Ohanafy repo to `/tmp/` when first needed in a session.

```bash
# Example from ohfy-oms-expert/SKILL.md
if [ ! -d /tmp/ohfy-oms ]; then
  gh repo clone Ohanafy/OHFY-OMS /tmp/ohfy-oms -- --depth 1
fi
```

**Pros:**
- Zero maintenance — always gets latest code
- No storage overhead in daniels-ohanafy
- Works immediately, no setup required

**Cons:**
- Slow on first use (~5-10s per repo clone)
- Requires GitHub access and Ohanafy org membership
- Context window cost — agent must read raw source files each session
- No offline capability

**When to evolve:** When you find yourself repeatedly cloning the same repos and waiting, or when the context window cost of reading raw Apex files is slowing down sessions.

---

## Option 2: Reference Index (Next Step)

A scheduled script clones each Ohanafy repo, extracts a condensed index, and commits it to daniels-ohanafy. Skills read the pre-built index instead of raw source.

### What the index contains per SKU

```
skills/ohfy-oms-expert/references/
├── class-index.md          # All Apex class names + first-line descriptions
├── trigger-index.md        # All triggers + objects they fire on
├── lwc-index.md            # All LWC component names + descriptions
├── object-fields.md        # Key object field lists (from .object-meta.xml)
├── service-methods.md      # Public method signatures from service classes
└── last-synced.txt         # Timestamp + commit SHA
```

### The sync script

```bash
#!/bin/bash
# scripts/sync-ohanafy-index.sh
# Run weekly via cron or GitHub Actions

REPOS=(
  "OHFY-Core"
  "OHFY-Data_Model"
  "OHFY-Platform"
  "OHFY-OMS"
  "OHFY-OMS-UI"
  "OHFY-WMS"
  "OHFY-WMS-UI"
  "OHFY-REX"
  "OHFY-REX-UI"
  "OHFY-Ecom"
  "OHFY-Payments"
  "OHFY-EDI"
  "OHFY-Configure"
  "OHFY-Planogram"
  "OHFY-PLTFM-UI"
  "OHFY-Service_Locator"
  "OHFY-Utilities"
  "OHFY-AI"
)

SKU_MAP=(
  "OHFY-Core:ohfy-core-expert"
  "OHFY-Data_Model:ohfy-data-model-expert"
  "OHFY-Platform:ohfy-platform-expert"
  "OHFY-OMS:ohfy-oms-expert"
  "OHFY-WMS:ohfy-wms-expert"
  "OHFY-REX:ohfy-rex-expert"
  "OHFY-Ecom:ohfy-ecom-expert"
  "OHFY-Payments:ohfy-payments-expert"
  "OHFY-EDI:ohfy-edi-expert"
  "OHFY-Configure:ohfy-configure-expert"
)

for entry in "${SKU_MAP[@]}"; do
  REPO="${entry%%:*}"
  SKILL="${entry##*:}"
  
  echo "Syncing $REPO -> skills/$SKILL/references/"
  
  # Clone to tmp
  gh repo clone "Ohanafy/$REPO" "/tmp/sync-$REPO" -- --depth 1 2>/dev/null
  
  # Extract class index
  find "/tmp/sync-$REPO" -name "*.cls" -not -name "*Test*" | while read f; do
    basename "$f" .cls
  done | sort > "skills/$SKILL/references/class-index.md"
  
  # Extract trigger index
  find "/tmp/sync-$REPO" -name "*.trigger" | while read f; do
    basename "$f" .trigger
  done | sort > "skills/$SKILL/references/trigger-index.md"
  
  # Extract LWC component index
  find "/tmp/sync-$REPO" -path "*/lwc/*" -name "*.js" -not -name "*.test.js" | while read f; do
    dirname "$f" | xargs basename
  done | sort -u > "skills/$SKILL/references/lwc-index.md"
  
  # Record sync metadata
  cd "/tmp/sync-$REPO"
  echo "Last synced: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "../../skills/$SKILL/references/last-synced.txt"
  echo "Commit: $(git rev-parse HEAD)" >> "../../skills/$SKILL/references/last-synced.txt"
  cd -
  
  # Cleanup
  rm -rf "/tmp/sync-$REPO"
done

echo "Index sync complete."
```

### Automation

Run via GitHub Actions on a schedule:

```yaml
# .github/workflows/sync-ohanafy-index.yml
name: Sync Ohanafy Source Index
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 6am UTC
  workflow_dispatch:       # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/sync-ohanafy-index.sh
      - run: |
          git add skills/*/references/
          git diff --cached --quiet || git commit -m "chore: sync Ohanafy source index"
          git push
```

**Pros:**
- Fast skill activation (no clone needed, index is local)
- Works offline (index is committed)
- Smaller context window cost (summaries, not raw source)
- Searchable (grep across all indexes)

**Cons:**
- Up to 1 week stale (or whatever the cron frequency is)
- Maintenance of sync script
- Index may miss nuance (method signatures yes, implementation details no)
- Still need clone-on-demand as fallback for deep dives

**When to evolve:** When you need real-time awareness of code changes (e.g., a CI webhook that triggers skill updates on every push to main).

---

## Option 3: Git Submodules (Most Integrated)

Add each Ohanafy repo as a git submodule under a `.ohanafy/` directory.

### Setup

```bash
git submodule add https://github.com/Ohanafy/OHFY-Core.git .ohanafy/OHFY-Core
git submodule add https://github.com/Ohanafy/OHFY-OMS.git .ohanafy/OHFY-OMS
git submodule add https://github.com/Ohanafy/OHFY-WMS.git .ohanafy/OHFY-WMS
# ... etc for each repo
```

### Update

```bash
git submodule update --remote --merge
```

### Skill references change from:

```bash
gh repo clone Ohanafy/OHFY-OMS /tmp/ohfy-oms -- --depth 1
```

To:

```
Read directly from .ohanafy/OHFY-OMS/force-app/main/default/classes/
```

**Pros:**
- Always available locally (after initial clone)
- Fast reads (no network needed)
- Standard git workflow — `git submodule update` pulls latest
- Full source available (not just indexes)

**Cons:**
- Adds significant repo size (each submodule is a full clone)
- Git submodules have notoriously painful UX (detached HEAD, forgotten updates)
- Every team member needs Ohanafy org access
- `.ohanafy/` directory clutters the repo

**When to use:** Only if Option 2 isn't sufficient and you need real-time, full-source access without network latency. Most teams find Option 2 with a good sync frequency is enough.

---

## Option 4: Webhook-Driven Sync (Future State)

A GitHub webhook fires on every push to any Ohanafy repo's main branch. A Lambda/Action receives the webhook, extracts the changed files, updates the relevant skill's references, and commits.

This gives you **near-real-time** skill awareness without submodules.

**Prerequisites:**
- GitHub App or webhook configured on the Ohanafy org
- A handler (GitHub Action or AWS Lambda) that processes pushes
- Write access to daniels-ohanafy from the handler

**This is Option 2 with a webhook trigger instead of a cron schedule.**

---

## Recommended Evolution Path

```
NOW:        Option 1 (clone on demand)
            Zero effort, works today
                ↓
MONTH 1-2:  Option 2 (weekly index sync)
            When you're tired of waiting for clones
                ↓
IF NEEDED:  Option 4 (webhook-driven sync)
            When weekly staleness matters
                ↓
PROBABLY    Option 3 (submodules)
NEVER:      Only if you need full offline source access
```

The key insight: **you can always fall back to clone-on-demand** for deep dives, even when using Option 2 or 3 for quick lookups. The options layer on top of each other, they don't replace each other.
