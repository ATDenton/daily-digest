import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "index.html")


def _build_section_views(news, sections_copy):
    """For each section, split headlines into Ground News-style multi-source
    clusters (2+ outlets covering the same story) and the remaining singles."""
    views = {}
    for section, items in news.items():
        by_id = {item["id"]: item for item in items}
        section_copy = sections_copy.get(section, {})
        clustered_ids = set()
        clusters = []
        for cluster in section_copy.get("clusters", []):
            cluster_items = [by_id[i] for i in cluster["item_ids"] if i in by_id]
            if len(cluster_items) >= 2:
                clustered_ids.update(cluster["item_ids"])
                clusters.append({"headline": cluster["headline"], "sources": cluster_items})
        singles = [item for item in items if item["id"] not in clustered_ids]
        views[section] = {
            "summary": section_copy.get("summary", ""),
            "clusters": clusters,
            "singles": singles,
        }
    return views


def render_digest(indices, watchlist, news, digest_copy, now=None):
    now = now or datetime.now()
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("digest.html.jinja")
    section_views = _build_section_views(news, digest_copy.get("sections", {}))
    html = template.render(
        generated_date=now.strftime("%A %d %B %Y"),
        generated_time=now.strftime("%H:%M"),
        indices=indices,
        watchlist=watchlist,
        sections=section_views,
        market_commentary=digest_copy.get("market_commentary", ""),
    )
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)
    return OUTPUT_PATH
