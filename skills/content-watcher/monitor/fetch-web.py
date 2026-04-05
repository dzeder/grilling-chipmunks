"""
Fetch content from web sources: blogs, Reddit RSS, and general web pages.

Supports:
- RSS/Atom feeds (blogs, Reddit .rss, news sites)
- Direct web pages (article extraction via BeautifulSoup)
"""

import logging
import re
from datetime import datetime, timezone

import feedparser
import httpx

logger = logging.getLogger(__name__)

# User-Agent for web requests (be a good citizen)
USER_AGENT = "OhanafyContentWatcher/1.0 (content monitoring for internal knowledge base)"


def fetch_rss_articles(feed_url: str, max_results: int = 10) -> list[dict]:
    """Fetch recent articles from an RSS/Atom feed.

    Returns list of {title, link, published, content} dicts.
    """
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:max_results]:
        # Extract content from entry
        content = ""
        if entry.get("content"):
            # Atom feeds store content in entry.content list
            content = entry.content[0].get("value", "")
        elif entry.get("summary"):
            content = entry.summary
        elif entry.get("description"):
            content = entry.description

        # Strip HTML tags for plain text
        content = _strip_html(content)

        published = entry.get("published", entry.get("updated", ""))

        articles.append(
            {
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", ""),
                "published": published,
                "content": content,
                "guid": entry.get("id", entry.get("link", "")),
            }
        )

    return articles


def fetch_web_page(url: str) -> str | None:
    """Fetch and extract article content from a web page.

    Uses BeautifulSoup to strip navigation, headers, footers, and ads.
    Returns plain text content.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("beautifulsoup4 not installed, skipping web page fetch")
        return None

    try:
        resp = httpx.get(
            url,
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("Failed to fetch %s: %s", url, e)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "form"]):
        tag.decompose()

    # Try to find the main article content
    article = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile(r"content|article|post"))

    if article:
        text = article.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Limit to reasonable length
    if len(text) > 15000:
        text = text[:15000]

    return text if len(text) > 100 else None  # Skip very short pages


def fetch_web_content(source: dict, last_checked: str | None = None) -> list[dict]:
    """Fetch new content from a web or Reddit source.

    Args:
        source: Source config dict with url, type, name, category
        last_checked: ISO timestamp of last check

    Returns list of {source, episode, content, link, published, fetched_at} dicts.
    """
    source_url = source.get("url", "")
    results = []

    # Try RSS first (works for Reddit, most blogs)
    articles = fetch_rss_articles(source_url)

    if articles:
        for article in articles:
            # Skip if published before last_checked
            if last_checked and article["published"] and article["published"] < last_checked:
                continue

            content = article["content"]

            # If RSS content is too short, try fetching the full page
            if len(content) < 200 and article.get("link"):
                full_content = fetch_web_page(article["link"])
                if full_content:
                    content = full_content

            if content and len(content) > 50:
                results.append(
                    {
                        "source": source,
                        "episode": article["title"],
                        "content": content,
                        "link": article["link"],
                        "published": article["published"],
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
    else:
        # Not an RSS feed — try direct page fetch
        content = fetch_web_page(source_url)
        if content:
            results.append(
                {
                    "source": source,
                    "episode": source.get("name", source_url),
                    "content": content,
                    "link": source_url,
                    "published": datetime.now(timezone.utc).isoformat(),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    return results


def _strip_html(html: str) -> str:
    """Strip HTML tags and return plain text."""
    # Simple HTML stripping without BeautifulSoup dependency
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&\w+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
