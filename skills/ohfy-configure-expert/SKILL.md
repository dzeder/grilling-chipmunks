---
name: ohfy-configure-expert
description: |
  Expert knowledge of the Ohanafy Configuration system (OHFY-Configure). Apply when:
  - Setting up or modifying system configuration
  - Working with metadata-driven feature flags or settings
  - Understanding post-install setup and configuration UI
  - Debugging configuration-related behavior across packages
  Covers: System configuration, setup wizards, feature flags, custom metadata
  settings, and the OHFY_Configuration Lightning page.
---

# OHFY-Configure Expert Skill

## Source Repository

**Repo:** `Ohanafy/OHFY-Configure`
**Version:** 0.20.0
**Languages:** Apex, CSS, HTML, JavaScript
**Dependencies:** OHFY-Core
**Setup UI:** `/lightning/n/ohfy__OHFY_Configuration`
**Post-Install:** `OHFYPackageInstallHandler` (auto-configures on install)

### Quick Reference (auto-synced)

Read `references/source-index.md` for a pre-built index of all classes, triggers,
service methods, object fields, and LWC components. Check `references/last-synced.txt` —
if older than 7 days, refresh:

```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-Configure
```

### Deep Dive (clone for full source)

When the index isn't enough (need implementation details, method bodies, test patterns):

```bash
if [ ! -d /tmp/ohfy-configure ]; then
  gh repo clone Ohanafy/OHFY-Configure /tmp/ohfy-configure -- --depth 1
fi
```

## Domain Coverage

- System configuration and admin settings
- Post-install auto-configuration
- Feature flag management
- Metadata-driven behavior configuration
- Configuration UI (Lightning page)
- Package installation handlers
- Environment-specific settings

## Delegates To

- **ohfy-core-expert** — For core package behavior
- **ohfy-data-model-expert** — For configuration metadata types
- **sf-metadata** — For custom metadata patterns
