import certifi
import feedparser
import requests

from config import MAX_HEADLINES_PER_SECTION, RSS_FEEDS

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; market-digest/1.0)"}


def _parse_feed(url):
    resp = requests.get(url, headers=HEADERS, verify=certifi.where(), timeout=15)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    source = parsed.feed.get("title", url)
    items = []
    for entry in parsed.entries:
        items.append(
            {
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "source": source,
                "published": entry.get("published", entry.get("updated", "")),
            }
        )
    return items


def fetch_section_headlines(section):
    seen_titles = set()
    combined = []
    for url in RSS_FEEDS[section]:
        try:
            for item in _parse_feed(url):
                key = item["title"].lower()
                if key and key not in seen_titles:
                    seen_titles.add(key)
                    combined.append(item)
        except Exception:
            continue
    return combined[:MAX_HEADLINES_PER_SECTION]


def fetch_all_news():
    return {section: fetch_section_headlines(section) for section in RSS_FEEDS}


if __name__ == "__main__":
    import json

    print(json.dumps(fetch_all_news(), indent=2))
