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
    ],
    "UK Politics": [
        "http://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://www.theguardian.com/politics/rss",
    ],
    "World Politics": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.theguardian.com/world/rss",
        "https://www.ft.com/world?format=rss",
    ],
    "Business & Economy": [
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.theguardian.com/uk/business/rss",
        "https://www.ft.com/companies?format=rss",
    ],
    "Science & Tech": [
        "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://www.theguardian.com/uk/technology/rss",
    ],
    "Wildcard": [
        "http://feeds.bbci.co.uk/news/rss.xml",
    ],
}

MAX_HEADLINES_PER_SECTION = 8
