import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-flash-latest"

SYSTEM_INSTRUCTION = """You are writing a concise daily digest for one reader.
Given raw market data and news headlines (with sources), write short, plain-English
summaries. Do not invent facts, numbers, or events beyond what's given. Do not
fabricate links or sources - the headlines and links are shown separately, you are
only writing the narrative summary text. Keep a neutral, informative tone."""


def _client():
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _build_prompt(indices, watchlist, news):
    payload = {
        "indices": indices,
        "watchlist": watchlist,
        "news_headlines_by_section": {
            section: [item["title"] for item in items] for section, items in news.items()
        },
    }
    section_names = list(news.keys())
    return f"""Here is today's raw data:

{json.dumps(payload, indent=2)}

Write a JSON object with this exact shape:
{{
  "market_commentary": "2-4 sentence overview of how US/UK/world markets and the watchlist stocks moved today and any notable pattern",
  "sections": {{
{", ".join(f'"{name}": "2-4 sentence summary of the headlines in this section"' for name in section_names)}
  }}
}}

Only return the JSON object, nothing else."""


def generate_digest_copy(indices, watchlist, news):
    client = _client()
    prompt = _build_prompt(indices, watchlist, news)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "response_mime_type": "application/json",
        },
    )
    return json.loads(response.text)


if __name__ == "__main__":
    from fetch_markets import fetch_indices, fetch_watchlist
    from fetch_news import fetch_all_news

    indices = fetch_indices()
    watchlist = fetch_watchlist()
    news = fetch_all_news()
    print(json.dumps(generate_digest_copy(indices, watchlist, news), indent=2))
