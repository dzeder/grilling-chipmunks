# References (Read-Only Mirrors)

Auto-synced upstream repos. **Never edit directly** — changes will be overwritten on next sync.

| Directory | Source | Update Script | Schedule |
|-----------|--------|---------------|----------|
| `claude-code-best-practices/` | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | `bash scripts/update-best-practices.sh` | Wednesdays |
| `agent-skills/` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `bash scripts/update-agent-skills.sh` | Thursdays |
| `ohanafy-index/` | Ohanafy product repos | `bash scripts/sync-ohanafy-index.sh` | On demand |
| `ecosystem-watch/` | Multiple watched repos | `bash scripts/check-ecosystem.sh` | On demand |

gstack skills are synced separately to `.claude/skills/gstack/` via `bash scripts/update-gstack.sh` (Mondays).

Cherry-pick source (issue-based, no auto-overwrite):
- [Jaganpro/sf-skills](https://github.com/Jaganpro/sf-skills) — `bash scripts/update-sf-skills.sh` (Fridays)

## Key References

In `claude-code-best-practices/`:
- `best-practice/claude-skills.md` — Skill authoring patterns
- `best-practice/claude-subagents.md` — Subagent design
- `best-practice/claude-commands.md` — Command patterns
- `reports/claude-skills-for-larger-mono-repos.md` — Monorepo skill organization

## Freshness

Check `ohanafy-index/last-synced.txt` for source index staleness. If >7 days, refresh with:
```bash
bash scripts/sync-ohanafy-index.sh --repo OHFY-<Package>
```

See `docs/upstream-dependencies.md` for full dependency tracking.
