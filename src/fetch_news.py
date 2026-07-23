from itertools import zip_longest

import certifi
import feedparser
import requests

from config import MAX_HEADLINES_PER_SECTION, OUTLET_BIAS, OUTLET_BY_DOMAIN, RSS_FEEDS

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; market-digest/1.0)"}


def _normalize_source(url, raw_title):
    lowered_url = url.lower()
    for domain, canonical in OUTLET_BY_DOMAIN:
        if domain in lowered_url:
            return canonical
    return raw_title


def _parse_feed(url):
    resp = requests.get(url, headers=HEADERS, verify=certifi.where(), timeout=15)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    source = _normalize_source(url, parsed.feed.get("title", url))
    items = []
    for entry in parsed.entries:
        items.append(
            {
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "source": source,
                "bias": OUTLET_BIAS.get(source, ""),
                "published": entry.get("published", entry.get("updated", "")),
            }
        )
    return items


def fetch_section_headlines(section):
    seen_titles = set()
    per_source = []
    for url in RSS_FEEDS[section]:
        try:
            items = []
            for item in _parse_feed(url):
                key = item["title"].lower()
                if key and key not in seen_titles:
                    seen_titles.add(key)
                    items.append(item)
            if items:
                per_source.append(items)
        except Exception:
            continue

    # Round-robin across sources so one high-volume feed (e.g. BBC) can't
    # crowd out the others before the per-section cap is reached.
    combined = []
    for items in zip_longest(*per_source):
        for item in items:
            if item is not None:
                combined.append(item)

    result = combined[:MAX_HEADLINES_PER_SECTION]
    for idx, item in enumerate(result):
        item["id"] = f"{section}:{idx}"
    return result


def fetch_all_news():
    return {section: fetch_section_headlines(section) for section in RSS_FEEDS}


if __name__ == "__main__":
    import json

    print(json.dumps(fetch_all_news(), indent=2))
