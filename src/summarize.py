import json
import os
import random
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

# Pinned deliberately rather than using a "-latest" alias: those get hot-swapped
# with every new release and can point at preview builds, so an unattended job
# can be migrated onto a different model without warning.
MODEL = "gemini-3.7-flash"

# The API returns transient 503s when a model is under load, and a single one
# used to fail the whole digest. This is a once-a-day job with nobody watching,
# so it's worth waiting out a spike. Backoff is ~4s, 8s, 16s, 32s between five
# attempts - roughly a minute of total waiting in the worst case.
MAX_ATTEMPTS = 5
INITIAL_BACKOFF_SECONDS = 4
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

SYSTEM_INSTRUCTION = """You are writing a concise daily digest for one reader.
Given raw market data and news headlines (with sources and ids), write short,
plain-English summaries and group headlines that cover the same underlying story
across different outlets, Ground News-style. Do not invent facts, numbers, or
events beyond what's given. Never invent a headline id - only use ids that were
given to you. Keep a neutral, informative tone."""


def _client():
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _build_prompt(indices, watchlist, news):
    payload = {
        "indices": indices,
        "watchlist": watchlist,
        "news_headlines_by_section": {
            section: [
                {"id": item["id"], "source": item["source"], "title": item["title"]}
                for item in items
            ]
            for section, items in news.items()
        },
    }
    section_names = list(news.keys())
    return f"""Here is today's raw data:

{json.dumps(payload, indent=2)}

Write a JSON object with this exact shape:
{{
  "market_commentary": "2-4 sentence overview of how US/UK/world markets and the watchlist stocks moved today and any notable pattern",
  "sections": {{
{", ".join(
        f'"{name}": {{"summary": "2-4 sentence summary of the headlines in this section", '
        f'"clusters": [{{"headline": "short neutral label for a story reported by 2+ different sources in this section", '
        f'"item_ids": ["id1", "id2"]}}]}}'
        for name in section_names
    )}
  }}
}}

For each section's "clusters": only include a cluster when 2 or more DIFFERENT sources
in that section report the same underlying story. Every item_id must be copied exactly
from the input data - never invent one. Skip clusters entirely for a section if none of
its headlines overlap across sources. A headline id must not appear in more than one
cluster. Only return the JSON object, nothing else."""


def _validate_clusters(digest_copy, news):
    valid_ids_by_section = {
        section: {item["id"] for item in items} for section, items in news.items()
    }
    for section, section_copy in digest_copy.get("sections", {}).items():
        valid_ids = valid_ids_by_section.get(section, set())
        clusters = section_copy.get("clusters", [])
        cleaned = []
        for cluster in clusters:
            ids = [i for i in cluster.get("item_ids", []) if i in valid_ids]
            if len(ids) >= 2:
                cleaned.append({"headline": cluster.get("headline", ""), "item_ids": ids})
        section_copy["clusters"] = cleaned
    return digest_copy


def _is_retryable(exc):
    """Transient server-side errors, plus the occasional truncated response."""
    if isinstance(exc, errors.APIError):
        return getattr(exc, "code", None) in RETRYABLE_STATUS_CODES
    return isinstance(exc, json.JSONDecodeError)


def _generate_copy(client, prompt):
    return json.loads(
        client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
            },
        ).text
    )


def generate_digest_copy(indices, watchlist, news):
    client = _client()
    prompt = _build_prompt(indices, watchlist, news)

    backoff = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            digest_copy = _generate_copy(client, prompt)
            break
        except Exception as exc:
            if not _is_retryable(exc) or attempt == MAX_ATTEMPTS:
                raise
            # Jitter so retries don't line up with other clients backing off
            # against the same overloaded model.
            delay = backoff + random.uniform(0, 1)
            print(
                f"Gemini call failed ({type(exc).__name__}: {exc}); "
                f"retrying in {delay:.1f}s "
                f"(attempt {attempt} of {MAX_ATTEMPTS})",
                flush=True,
            )
            time.sleep(delay)
            backoff *= 2

    return _validate_clusters(digest_copy, news)


if __name__ == "__main__":
    from fetch_markets import fetch_indices, fetch_watchlist
    from fetch_news import fetch_all_news

    indices = fetch_indices()
    watchlist = fetch_watchlist()
    news = fetch_all_news()
    print(json.dumps(generate_digest_copy(indices, watchlist, news), indent=2))
