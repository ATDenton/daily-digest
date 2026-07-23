import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "index.html")


def render_digest(indices, watchlist, news, digest_copy, now=None):
    now = now or datetime.now()
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("digest.html.jinja")
    html = template.render(
        generated_date=now.strftime("%A %d %B %Y"),
        generated_time=now.strftime("%H:%M"),
        indices=indices,
        watchlist=watchlist,
        news=news,
        market_commentary=digest_copy.get("market_commentary", ""),
        section_summaries=digest_copy.get("sections", {}),
    )
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)
    return OUTPUT_PATH
