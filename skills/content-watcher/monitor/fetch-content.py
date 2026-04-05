"""
Fetch content from all monitored sources.

Source types and strategies:
1. YouTube → Data API v3 auto-captions
2. Podcast (RSS) → podcast:transcript tag, then Whisper fallback
3. Web/Blog → RSS feed parsing, article extraction
4. Reddit → RSS feed (.rss suffix)
5. Apple Podcast → resolve to RSS via Podcast Index API
6. Spotify → resolve to RSS via Podcast Index API
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import feedparser
import httpx
import yaml

SOURCES_FILE = Path("registry/content-sources.yaml")

logger = logging.getLogger(__name__)


def fetch_youtube_transcript(video_id: str) -> str | None:
    """Fetch auto-captions from YouTube Data API v3.

    Uses the captions.list endpoint to find available caption tracks,
    then downloads the auto-generated English captions.
    """
    import os

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        logger.warning("YOUTUBE_API_KEY not set, skipping YouTube transcript fetch")
        return None

    # List caption tracks for the video
    list_url = "https://www.googleapis.com/youtube/v3/captions"
    params = {"part": "snippet", "videoId": video_id, "key": api_key}

    try:
        resp = httpx.get(list_url, params=params, timeout=30)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except httpx.HTTPError as e:
        logger.error("Failed to list captions for %s: %s", video_id, e)
        return None

    # Find English auto-generated or manual captions
    caption_id = None
    for item in items:
        snippet = item.get("snippet", {})
        lang = snippet.get("language", "")
        track_kind = snippet.get("trackKind", "")
        if lang.startswith("en"):
            caption_id = item["id"]
            if track_kind == "standard":
                break  # Prefer manual captions over auto-generated

    if not caption_id:
        logger.info("No English captions found for video %s", video_id)
        return None

    # Download the caption track
    download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}"
    download_params = {"tfmt": "srt", "key": api_key}

    try:
        resp = httpx.get(download_url, params=download_params, timeout=30)
        resp.raise_for_status()
        # Strip SRT formatting (timestamps, sequence numbers) to get plain text
        lines = resp.text.split("\n")
        text_lines = []
        for line in lines:
            line = line.strip()
            # Skip empty lines, sequence numbers, and timestamp lines
            if not line or line.isdigit() or re.match(r"\d{2}:\d{2}:\d{2}", line):
                continue
            text_lines.append(line)
        return " ".join(text_lines)
    except httpx.HTTPError as e:
        logger.error("Failed to download captions for %s: %s", video_id, e)
        return None


def fetch_rss_transcript(feed_url: str, episode_guid: str) -> str | None:
    """Check RSS feed for podcast:transcript tag.

    Looks for the Podcasting 2.0 <podcast:transcript> tag in the episode entry.
    If found, downloads the transcript (SRT, VTT, or plain text).
    """
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        guid = entry.get("id", entry.get("link", ""))
        if guid != episode_guid:
            continue

        # Check for podcast:transcript tag
        # feedparser exposes namespace tags via entry.get("podcast_transcript", ...)
        transcript_url = None
        for link in entry.get("links", []):
            if link.get("rel") == "transcript" or "transcript" in link.get("type", ""):
                transcript_url = link.get("href")
                break

        # Also check for podcast:transcript as a direct attribute
        if not transcript_url:
            transcript_tag = entry.get("podcast_transcript", {})
            if isinstance(transcript_tag, dict):
                transcript_url = transcript_tag.get("url")
            elif isinstance(transcript_tag, str):
                transcript_url = transcript_tag

        if not transcript_url:
            return None

        try:
            resp = httpx.get(transcript_url, timeout=30)
            resp.raise_for_status()
            text = resp.text
            # Strip SRT/VTT formatting if needed
            if transcript_url.endswith((".srt", ".vtt")):
                lines = text.split("\n")
                text_lines = []
                for line in lines:
                    line = line.strip()
                    if not line or line.isdigit() or re.match(r"\d{2}:\d{2}:\d{2}", line) or line.startswith("WEBVTT"):
                        continue
                    text_lines.append(line)
                return " ".join(text_lines)
            return text
        except httpx.HTTPError as e:
            logger.error("Failed to download transcript from %s: %s", transcript_url, e)
            return None

    return None


def transcribe_audio(audio_url: str) -> str:
    """Download audio and transcribe with Whisper medium model.

    Falls back to flagging as manual_needed if Whisper is not installed.
    """
    try:
        import whisper
    except ImportError:
        logger.warning("openai-whisper not installed, flagging as manual_needed")
        raise RuntimeError("TranscriptUnavailable: Whisper not installed. Install with: pip install openai-whisper")

    import tempfile

    # Download audio to temp file
    try:
        resp = httpx.get(audio_url, timeout=120, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise RuntimeError(f"TranscriptUnavailable: Failed to download audio: {e}")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(resp.content)
        temp_path = f.name

    try:
        model = whisper.load_model("medium")
        result = model.transcribe(temp_path)
        return result["text"]
    finally:
        Path(temp_path).unlink(missing_ok=True)


def _get_youtube_channel_videos(channel_url: str, api_key: str, max_results: int = 5) -> list[dict]:
    """Get recent videos from a YouTube channel."""
    # Extract channel ID or handle from URL
    parsed = urlparse(channel_url)
    path_parts = parsed.path.strip("/").split("/")

    channel_id = None
    if len(path_parts) >= 2 and path_parts[0] == "channel":
        channel_id = path_parts[1]
    elif path_parts[0].startswith("@"):
        # Handle format: resolve via search
        handle = path_parts[0]
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {"part": "snippet", "q": handle, "type": "channel", "key": api_key, "maxResults": 1}
        try:
            resp = httpx.get(search_url, params=params, timeout=30)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            if items:
                channel_id = items[0]["snippet"]["channelId"]
        except httpx.HTTPError:
            pass

    if not channel_id:
        logger.warning("Could not resolve channel ID from %s", channel_url)
        return []

    # Search for recent videos from this channel
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
    }

    try:
        resp = httpx.get(search_url, params=params, timeout=30)
        resp.raise_for_status()
        return [
            {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "published": item["snippet"]["publishedAt"],
                "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            }
            for item in resp.json().get("items", [])
            if item["id"].get("videoId")
        ]
    except httpx.HTTPError as e:
        logger.error("Failed to fetch channel videos: %s", e)
        return []


def _get_rss_episodes(feed_url: str, max_results: int = 5) -> list[dict]:
    """Get recent episodes from an RSS feed."""
    feed = feedparser.parse(feed_url)
    episodes = []
    for entry in feed.entries[:max_results]:
        # Get audio enclosure URL if available
        audio_url = None
        for enc in entry.get("enclosures", []):
            if enc.get("type", "").startswith("audio/"):
                audio_url = enc.get("href")
                break

        published = entry.get("published", entry.get("updated", ""))

        episodes.append(
            {
                "guid": entry.get("id", entry.get("link", "")),
                "title": entry.get("title", "Unknown"),
                "published": published,
                "link": entry.get("link", ""),
                "audio_url": audio_url,
            }
        )
    return episodes


def fetch_all_new() -> list[dict]:
    """Check all sources for new content and fetch transcripts.

    Returns list of {source, episode, content, fetched_at} dicts.
    """
    import os

    config = yaml.safe_load(SOURCES_FILE.read_text())
    sources = config.get("sources", [])
    results = []

    for source in sources:
        source_type = source.get("type", "podcast")
        source_url = source.get("url", "")
        last_checked = source.get("last_checked")

        logger.info("Checking source: %s (%s)", source.get("name", source_url), source_type)

        try:
            if source_type == "youtube":
                api_key = os.environ.get("YOUTUBE_API_KEY", "")
                if not api_key:
                    logger.warning("YOUTUBE_API_KEY not set, skipping %s", source.get("name"))
                    continue

                videos = _get_youtube_channel_videos(source_url, api_key)
                for video in videos:
                    # Skip if published before last_checked
                    if last_checked and video["published"] < last_checked:
                        continue

                    transcript = fetch_youtube_transcript(video["video_id"])
                    if transcript:
                        results.append(
                            {
                                "source": source,
                                "episode": video["title"],
                                "content": transcript,
                                "link": video["link"],
                                "published": video["published"],
                                "fetched_at": datetime.now(timezone.utc).isoformat(),
                            }
                        )

            elif source_type == "podcast":
                episodes = _get_rss_episodes(source_url)
                for ep in episodes:
                    if last_checked and ep["published"] < last_checked:
                        continue

                    # Try podcast:transcript tag first
                    transcript = fetch_rss_transcript(source_url, ep["guid"])
                    if not transcript and ep.get("audio_url"):
                        try:
                            transcript = transcribe_audio(ep["audio_url"])
                        except RuntimeError as e:
                            logger.warning("Whisper fallback failed for %s: %s", ep["title"], e)
                            continue

                    if transcript:
                        results.append(
                            {
                                "source": source,
                                "episode": ep["title"],
                                "content": transcript,
                                "link": ep["link"],
                                "published": ep["published"],
                                "fetched_at": datetime.now(timezone.utc).isoformat(),
                            }
                        )

            elif source_type in ("web", "reddit"):
                from skills.content_watcher.monitor.fetch_web import fetch_web_content

                web_items = fetch_web_content(source, last_checked)
                results.extend(web_items)

            else:
                logger.warning("Unknown source type: %s for %s", source_type, source.get("name"))

        except Exception as e:
            logger.error("Error processing source %s: %s", source.get("name", source_url), e)
            continue

        # Update last_checked timestamp
        source["last_checked"] = datetime.now(timezone.utc).isoformat()

    # Save updated timestamps back to config
    SOURCES_FILE.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    transcripts = fetch_all_new()
    print(f"Fetched {len(transcripts)} new items")
    for t in transcripts:
        print(f"  - [{t['source'].get('category', '?')}] {t['episode'][:60]}")
