# Registry

Central configuration for all external systems and team structure.

## Files

- `ohanafy-repos.yaml` — All Ohanafy GitHub repos, auto-discovered and categorized
- `content-sources.yaml` — Podcast and YouTube sources monitored by Content Watcher
- `team.yaml` — Team ownership map for routing and escalation
- `aws-config.yaml` — AWS account IDs and regions (created during onboarding)

## Rules

- Always check `ohanafy-repos.yaml` before touching any product repo
- Add new content sources via `python -m skills.content_watcher.commands.add_source`
- Keep `team.yaml` updated when team changes happen
