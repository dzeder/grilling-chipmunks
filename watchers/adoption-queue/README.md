# Adoption Queue

High-relevance items (score > 0.85) from Repo Watcher are auto-PR'd here as GitHub issues.

## How It Works

1. Repo Watcher scans all repos in `watchers/repos.yaml` every Monday
2. New releases and patterns are scored for relevance to Ohanafy
3. Items scoring > 0.85 are filed as GitHub issues with label `ai-ops-adoption`
4. Team reviews alongside product roadmap

## Thresholds

- Auto-PR above: 0.85
- Notify above: 0.60
- Ignore below: 0.60
