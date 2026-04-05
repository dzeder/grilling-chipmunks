"""
Fetch transcripts from monitored content sources.

Priority order:
1. YouTube → Data API v3 auto-captions
2. RSS podcast:transcript tag
3. No transcript → download audio, run Whisper locally (medium model)
4. Apple URL → resolve to RSS via Podcast Index API
5. Spotify URL → resolve to RSS via Podcast Index API
6. Spotify exclusive → flag as manual_needed
"""

import yaml
from pathlib import Path

SOURCES_FILE = Path("registry/content-sources.yaml")


def fetch_youtube_transcript(video_id: str) -> str | None:
    """Fetch auto-captions from YouTube Data API v3."""
    # TODO: Implement YouTube transcript fetching
    # Uses google-api-python-client
    raise NotImplementedError


def fetch_rss_transcript(feed_url: str, episode_guid: str) -> str | None:
    """Check RSS feed for podcast:transcript tag."""
    # TODO: Implement RSS transcript extraction
    # Uses feedparser
    raise NotImplementedError


def transcribe_audio(audio_url: str) -> str:
    """Download audio and transcribe with Whisper medium model."""
    # TODO: Implement Whisper transcription
    # Uses openai-whisper
    raise NotImplementedError


def fetch_all_new() -> list[dict]:
    """Check all sources for new content and fetch transcripts.

    Returns list of {source, episode, transcript, fetched_at} dicts.
    """
    config = yaml.safe_load(SOURCES_FILE.read_text())
    sources = config.get("sources", [])
    results = []

    for source in sources:
        # TODO: Check for new episodes since last_checked
        # TODO: Fetch transcript using priority order
        # TODO: Update last_checked timestamp
        pass

    return results


if __name__ == "__main__":
    transcripts = fetch_all_new()
    print(f"Fetched {len(transcripts)} new transcripts")
