import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from build_html import render_digest
from fetch_markets import fetch_indices, fetch_watchlist
from fetch_news import fetch_all_news
from summarize import generate_digest_copy


def main():
    print("Fetching market data...")
    indices = fetch_indices()
    watchlist = fetch_watchlist()

    print("Fetching news...")
    news = fetch_all_news()

    print("Summarizing with Gemini...")
    digest_copy = generate_digest_copy(indices, watchlist, news)

    print("Rendering HTML...")
    output_path = render_digest(indices, watchlist, news, digest_copy)

    print(f"Digest written to {output_path}")


if __name__ == "__main__":
    main()
