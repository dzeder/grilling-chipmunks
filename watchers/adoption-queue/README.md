# Adoption Queue

High-relevance items from Repo Watcher are surfaced here as GitHub issues for team review.

## How It Works

1. Repo Watcher scans all repos in `watchers/repos.yaml` on schedule
2. New releases and patterns are scored for relevance to Ohanafy
3. Items scoring > 0.85 are filed as GitHub issues with label `ai-ops-adoption`
4. Team reviews alongside product roadmap

## Thresholds

- Auto-PR above: 0.85
- Notify above: 0.60
- Ignore below: 0.60

## The Compounding Loop

Upstream changes flow through a three-layer system that ensures we always learn but never lose our own work:

```
UPSTREAM (read-only mirrors)              YOUR SKILLS (never overwritten)
references/agent-skills/                  skills/salesforce/sf-apex/
references/claude-code-best-practices/    skills/ohanafy/ohfy-oms-expert/
references/sf-skills/                     skills/tray/tray-expert/
.claude/skills/gstack/                    integrations/patterns/

        |                                         |
        +---- WATCHER (weekly discovery) ---------+
              detects upstream changes,
              checks learned_from lineage,
              flags YOUR skills for review
```

### Lineage tracking

Skills can declare `learned_from` in their frontmatter to trace which upstream patterns inspired them:

```yaml
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/error-recovery.md
    adapted: "2026-04-04"
```

When the watcher detects changes in a tracked repo, it checks which of our skills cite that repo via `learned_from`. The PR/issue then includes: "These skills may benefit from the upstream update."

### Adoption types by repo

| Repo | Sync method | Overwrites? | How to adopt |
|------|-------------|-------------|--------------|
| `garrytan/gstack` | Full rsync | Yes (safe — never edit directly) | Auto-PR, merge when ready |
| `shanraisshan/claude-code-best-practice` | Selective copy | Yes (read-only mirror) | Auto-PR, merge when ready |
| `addyosmani/agent-skills` | Full vendor | Yes (read-only mirror) | Auto-PR, review for adaptable patterns |
| `Jaganpro/sf-skills` | Cherry-pick | No (manual only) | Issue created, cherry-pick what you want |
| All other watched repos | Digest only | No (no file sync) | Issue/notification, manual review |

### Your improvements are safe

Local skills in `skills/` are **never touched** by any sync process. When you learn something from upstream and adapt it into your skill, that adaptation lives in your skill file forever. The `learned_from` field just keeps the connection alive so future upstream improvements get surfaced back to you.
