# content-watcher

Monitors content sources for insights relevant to Ohanafy. Supports podcasts,
YouTube channels, blogs, Reddit, and web pages. Fetches content, scores relevance
with Claude, and creates GitHub issues for insights worth acting on.

## Commands

add-source      Add a source (podcast, YouTube, blog, Reddit, web page)
list-sources    Show all monitored sources and last-checked status
delete-source   Remove a source

## Source types

| Type | How it works |
|------|-------------|
| youtube | YouTube Data API v3 auto-captions (~95% coverage) |
| podcast | RSS podcast:transcript tag, then Whisper fallback |
| web | RSS feed parsing + article extraction via BeautifulSoup |
| reddit | Reddit .rss feed (treated as RSS, no API needed) |

## When to use

- User adds a content source to monitor
- Daily cron job checking for new content
- User asks what we are currently monitoring

## Transcript / content strategy (priority order)

1. YouTube -> Data API v3 auto-captions
2. RSS podcast:transcript tag -> use directly
3. No transcript -> download audio, run Whisper locally (medium model)
4. Apple URL -> resolve to RSS via Podcast Index API first
5. Spotify URL -> resolve to RSS via Podcast Index API (works ~80% of shows)
6. Spotify exclusive (no RSS) -> flag as manual_needed, create GitHub issue
7. Web/blog -> RSS feed articles, fallback to page scraping
8. Reddit -> RSS feed at subreddit/.rss

## Issue creation rules

Every insight creates a GitHub issue in ohanafy/ai-ops.
Required fields (reject if missing): Source, Insight, Relevance to Ohanafy,
What It Affects, Recommended Action, Effort, Score, Category.
Agents create. Team triages alongside product roadmap.

## Categories

beverage_industry, product_strategy, salesforce, ai_dev_tools, tray_platform, integration

## Errors

SourceAlreadyExists / SourceNotFound / TranscriptUnavailable
RateLimitError (YouTube quota -- retry next day) / GitHubIssueError
