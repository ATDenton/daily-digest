INDICES = {
    "US": [
        ("^GSPC", "S&P 500"),
        ("^IXIC", "Nasdaq Composite"),
        ("^DJI", "Dow Jones Industrial Average"),
    ],
    "UK": [
        ("^FTSE", "FTSE 100"),
        ("^FTMC", "FTSE 250"),
    ],
    "World": [
        ("VWRL.L", "FTSE All-World (Vanguard ETF)"),
        ("^GDAXI", "DAX (Germany)"),
        ("^FCHI", "CAC 40 (France)"),
        ("^N225", "Nikkei 225 (Japan)"),
        ("^HSI", "Hang Seng (Hong Kong)"),
        ("000001.SS", "Shanghai Composite"),
    ],
}

WATCHLIST = [
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("GOOGL", "Alphabet"),
    ("AMZN", "Amazon"),
    ("NVDA", "Nvidia"),
    ("TSLA", "Tesla"),
    ("META", "Meta"),
    ("HSBA.L", "HSBC"),
    ("BP.L", "BP"),
    ("AZN.L", "AstraZeneca"),
    ("SHEL.L", "Shell"),
    ("ULVR.L", "Unilever"),
]

RSS_FEEDS = {
    "Markets": [
        "https://www.ft.com/markets?format=rss",
        "https://feeds.skynews.com/feeds/rss/business.xml",
        "https://feeds.npr.org/1006/rss.xml",
    ],
    "UK Politics": [
        "http://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://www.theguardian.com/politics/rss",
        "https://feeds.skynews.com/feeds/rss/politics.xml",
        "https://www.independent.co.uk/news/uk/politics/rss",
    ],
    "World Politics": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.theguardian.com/world/rss",
        "https://www.ft.com/world?format=rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.skynews.com/feeds/rss/world.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://feeds.npr.org/1004/rss.xml",
    ],
    "Business & Economy": [
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.theguardian.com/uk/business/rss",
        "https://www.ft.com/companies?format=rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        "https://feeds.skynews.com/feeds/rss/business.xml",
    ],
    "Science & Tech": [
        "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://www.theguardian.com/uk/technology/rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
        "https://feeds.skynews.com/feeds/rss/technology.xml",
    ],
    "Wildcard": [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.independent.co.uk/news/uk/politics/rss",
    ],
}

MAX_HEADLINES_PER_SECTION = 12

# Canonical outlet name -> rough, widely-cited editorial-lean label (e.g. per
# AllSides-style media bias charts). These are per-publication approximations
# for context, not a rigorous per-article rating - shown as a small badge next
# to each source, Ground News-style.
OUTLET_BIAS = {
    "BBC News": "Center",
    "The Guardian": "Lean Left",
    "Financial Times": "Center",
    "The New York Times": "Lean Left",
    "Sky News": "Center",
    "NPR": "Lean Left",
    "Al Jazeera English": "Center",
    "The Independent": "Lean Left",
}

# Domain substring -> canonical outlet name. Matched against the feed URL
# rather than the feed's <title>, since several outlets (FT in particular)
# use generic per-section titles like "Markets" or "World" that don't
# identify the publication.
OUTLET_BY_DOMAIN = [
    ("bbci.co.uk", "BBC News"),
    ("theguardian.com", "The Guardian"),
    ("ft.com", "Financial Times"),
    ("nytimes.com", "The New York Times"),
    ("skynews.com", "Sky News"),
    ("npr.org", "NPR"),
    ("aljazeera.com", "Al Jazeera English"),
    ("independent.co.uk", "The Independent"),
]
