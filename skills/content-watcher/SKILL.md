# content-watcher

Monitors podcast and YouTube sources. Fetches transcripts.
Scores relevance. Creates GitHub issues for insights worth acting on.

## Commands

add-source      Add a podcast (RSS/Apple/Spotify) or YouTube channel
list-sources    Show all monitored sources and last-checked status
delete-source   Remove a source

## When to use

- User adds a podcast or YouTube channel to monitor
- Daily cron job checking for new content
- User asks what we are currently monitoring

## Transcript strategy (priority order)

1. YouTube → Data API v3 auto-captions (~95% coverage)
2. RSS podcast:transcript tag → use directly
3. No transcript → download audio, run Whisper locally (medium model)
4. Apple URL → resolve to RSS via Podcast Index API first
5. Spotify URL → resolve to RSS via Podcast Index API (works ~80% of shows)
6. Spotify exclusive (no RSS) → flag as manual_needed, create GitHub issue

## Issue creation rules

Every insight creates a GitHub issue in ohanafy/ai-ops.
Required fields (reject if missing): Source, Insight, Relevance to Ohanafy,
What It Affects, Recommended Action, Effort, Score, Category.
Agents create. Team triages alongside product roadmap.

## Errors

SourceAlreadyExists / SourceNotFound / TranscriptUnavailable
RateLimitError (YouTube quota — retry next day) / GitHubIssueError
