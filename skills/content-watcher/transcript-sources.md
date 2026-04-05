# Transcript Sources

How to get transcripts from different source types.

## YouTube

- API: YouTube Data API v3
- Method: `captions.list` → `captions.download`
- Coverage: ~95% of videos have auto-captions
- Rate limit: 10,000 units/day (list=1, download=200)
- Fallback: Whisper transcription of downloaded audio

## RSS Podcasts

- Check for `<podcast:transcript>` tag (Podcasting 2.0 standard)
- If present, download transcript directly (SRT, VTT, or plain text)
- If absent, download audio enclosure and run Whisper

## Apple Podcasts

- No direct transcript API
- Resolve to RSS feed via Podcast Index API
- Then follow RSS podcast flow

## Spotify

- Resolve to RSS via Podcast Index API (works ~80% of shows)
- Spotify exclusives have no RSS — flag as `manual_needed`
- Create GitHub issue for manual transcript processing

## Whisper Fallback

- Model: `medium` (good balance of speed and accuracy)
- Languages: English primary, Spanish secondary
- Output: Plain text with timestamps
- Storage: `skills/content-watcher/manual-transcripts/` (gitignored)
