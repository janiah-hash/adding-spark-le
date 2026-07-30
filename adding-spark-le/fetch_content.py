"""
Pulls candidate stories for each vertical from:
  1. Direct RSS feeds (config.VERTICALS[v]["feeds"])
  2. NewsAPI.org discovery search (config.VERTICALS[v]["keywords"])

Then filters to the lookback window, dedupes, scores by keyword relevance,
and returns the top N per vertical.
"""

import html
import os
import re
import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests

import config


def _strip_html(text):
    """Remove any HTML tags (e.g. embedded <img>, <a>, <div> from RSS
    descriptions) and decode HTML entities, leaving plain text only.
    This prevents raw markup — most commonly lead-image <img> tags some
    feeds embed directly in their summary/description field — from
    rendering unstyled and oversized inside the newsletter."""
    if not text:
        return text
    text = re.sub(r"<[^>]+>", " ", text)  # strip tags
    text = html.unescape(text)  # decode &amp; etc.
    text = re.sub(r"\s+", " ", text).strip()  # collapse whitespace
    return text


def _parse_entry_date(entry):
    """Best-effort parse of an RSS entry's published date to a UTC datetime."""
    for field in ("published_parsed", "updated_parsed"):
        val = getattr(entry, field, None)
        if val:
            return datetime.fromtimestamp(time.mktime(val), tz=timezone.utc)
    return None


def _fetch_rss(feed_url, cutoff):
    """Return list of dicts: title, link, source, published, summary."""
    items = []
    try:
        parsed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"  [warn] failed to parse feed {feed_url}: {e}")
        return items

    source_name = parsed.feed.get("title", feed_url)

    for entry in parsed.entries:
        pub_date = _parse_entry_date(entry)
        if pub_date and pub_date < cutoff:
            continue  # too old
        items.append({
            "title": _strip_html(entry.get("title", "").strip()),
            "link": entry.get("link", "").strip(),
            "source": source_name,
            "published": pub_date,
            "summary": _strip_html(entry.get("summary", "").strip()),
        })
    return items


def _fetch_newsapi(keywords, cutoff, api_key):
    """Query NewsAPI.org /v2/everything for the given keywords."""
    if not api_key:
        return []

    query = " OR ".join(f'"{k}"' for k in keywords[:5])  # keep query short
    params = {
        "q": query,
        "from": cutoff.strftime("%Y-%m-%dT%H:%M:%S"),
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": config.NEWSAPI_PAGE_SIZE,
        "apiKey": api_key,
    }
    try:
        resp = requests.get(config.NEWSAPI_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [warn] NewsAPI request failed: {e}")
        return []

    items = []
    for article in data.get("articles", []):
        pub_str = article.get("publishedAt")
        pub_date = None
        if pub_str:
            try:
                pub_date = datetime.strptime(pub_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                pass
        items.append({
            "title": _strip_html((article.get("title") or "").strip()),
            "link": (article.get("url") or "").strip(),
            "source": (article.get("source") or {}).get("name", "Unknown"),
            "published": pub_date,
            "summary": _strip_html((article.get("description") or "").strip()),
        })
    return items


def _score(item, keywords):
    """Very simple relevance score: count of keyword hits in title+summary."""
    text = f"{item['title']} {item['summary']}".lower()
    return sum(1 for kw in keywords if kw.lower() in text)


def _dedupe(items):
    seen_links = set()
    seen_titles = set()
    out = []
    for item in items:
        key_link = item["link"]
        key_title = item["title"].lower().strip()
        if key_link in seen_links or key_title in seen_titles:
            continue
        seen_links.add(key_link)
        seen_titles.add(key_title)
        out.append(item)
    return out


def get_lookback_cutoff():
    """Widen the lookback window automatically on Mondays to cover the weekend."""
    now = datetime.now(timezone.utc)
    hours = config.LOOKBACK_HOURS_MONDAY if now.weekday() == 0 else config.LOOKBACK_HOURS_WEEKDAY
    return now - timedelta(hours=hours)


def fetch_all_verticals(newsapi_key=None):
    """
    Returns: { vertical_key: [ {title, link, source, published, summary, score}, ... ] }
    Each list is sorted by score (desc) and trimmed to MAX_STORIES_PER_VERTICAL.
    """
    cutoff = get_lookback_cutoff()
    results = {}

    for vkey, vconf in config.VERTICALS.items():
        print(f"Fetching: {vconf['label']}...")
        items = []

        for feed_url in vconf.get("feeds", []):
            items.extend(_fetch_rss(feed_url, cutoff))

        items.extend(_fetch_newsapi(vconf["keywords"], cutoff, newsapi_key))

        items = _dedupe(items)

        for item in items:
            item["score"] = _score(item, vconf["keywords"])

        # Keep only items with at least one keyword hit (avoid irrelevant noise
        # from broad RSS feeds like a full Utility Dive firehose)
        items = [i for i in items if i["score"] > 0]
        items.sort(key=lambda i: i["score"], reverse=True)

        results[vkey] = items[: config.MAX_STORIES_PER_VERTICAL]
        print(f"  -> kept {len(results[vkey])} stories")

    return results


if __name__ == "__main__":
    # Quick manual test: python fetch_content.py
    key = os.environ.get("NEWSAPI_KEY")
    all_results = fetch_all_verticals(newsapi_key=key)
    for vkey, stories in all_results.items():
        print(f"\n=== {vkey} ===")
        for s in stories:
            print(f"- {s['title']} ({s['source']}, score={s['score']})")
