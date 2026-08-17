import json
import os
import random
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

# Tried in order of preference. Individual models pinned rather than using a
# "-latest" alias: those get hot-swapped with every new release and can point at
# preview builds, so an unattended job can be migrated without warning.
#
# The list deliberately spans both model generations and size tiers. A single
# model can return 503 "high demand" continuously for minutes at a time - on
# 2026-08-17 that hit gemini-3.7-flash and gemini-3.6-flash simultaneously for
# over five minutes, long enough to exhaust any sensible retry budget, while
# the older and lite-tier models stayed healthy throughout. Falling back across
# tiers is what actually survives that, so the last two entries are lite models:
# their copy is terser, but a shorter digest beats no digest.
#
# Every entry here was checked against the live API - note that models.list()
# advertises some models (gemini-2.5-flash) that then 404 as "no longer
# available to new users", so a name appearing there is not enough.
MODELS = (
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
)

# Each pass tries every model in turn with no delay in between, since these are
# separate backends and a model that's saturated right now says nothing about
# the next one. Only once a whole pass has failed is it worth backing off.
MAX_PASSES = 6
INITIAL_BACKOFF_SECONDS = 4
MAX_BACKOFF_SECONDS = 30
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
# A model that's been retired or renamed should be stepped over, not retried.
MODEL_UNAVAILABLE_STATUS_CODES = {404}

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


def _is_recoverable(exc):
    """Whether it's worth trying another model, or the same one again later.

    Anything else - a malformed prompt, a bad API key - would fail identically
    on every model, so it should surface immediately rather than be retried.
    """
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        return code in RETRYABLE_STATUS_CODES or code in MODEL_UNAVAILABLE_STATUS_CODES
    return isinstance(exc, json.JSONDecodeError)


def _generate_copy(client, model, prompt):
    return json.loads(
        client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
            },
        ).text
    )


def _generate_with_fallback(client, prompt):
    backoff = INITIAL_BACKOFF_SECONDS
    last_exc = None

    for pass_number in range(1, MAX_PASSES + 1):
        for model in MODELS:
            try:
                return _generate_copy(client, model, prompt)
            except Exception as exc:
                if not _is_recoverable(exc):
                    raise
                last_exc = exc
                print(
                    f"{model} unavailable ({type(exc).__name__}: {exc}) "
                    f"[pass {pass_number} of {MAX_PASSES}]",
                    flush=True,
                )

        if pass_number < MAX_PASSES:
            # Jitter so retries don't line up with other clients backing off
            # against the same overloaded models.
            delay = backoff + random.uniform(0, 1)
            print(f"All models unavailable; retrying in {delay:.1f}s", flush=True)
            time.sleep(delay)
            backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)

    raise last_exc


def generate_digest_copy(indices, watchlist, news):
    client = _client()
    prompt = _build_prompt(indices, watchlist, news)
    digest_copy = _generate_with_fallback(client, prompt)
    return _validate_clusters(digest_copy, news)


if __name__ == "__main__":
    from fetch_markets import fetch_indices, fetch_watchlist
    from fetch_news import fetch_all_news

    indices = fetch_indices()
    watchlist = fetch_watchlist()
    news = fetch_all_news()
    print(json.dumps(generate_digest_copy(indices, watchlist, news), indent=2))
