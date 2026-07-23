import yfinance as yf

from config import INDICES, WATCHLIST


def _quote_rows(pairs):
    symbols = [s for s, _ in pairs]
    names = dict(pairs)
    data = yf.download(
        symbols,
        period="5d",
        interval="1d",
        group_by="ticker",
        progress=False,
        threads=True,
        auto_adjust=False,
    )

    rows = []
    for symbol in symbols:
        try:
            closes = data[symbol]["Close"].dropna()
            if len(closes) < 2:
                continue
            last = float(closes.iloc[-1])
            prev = float(closes.iloc[-2])
            change_pct = (last - prev) / prev * 100
            rows.append(
                {
                    "symbol": symbol,
                    "name": names[symbol],
                    "price": last,
                    "change_pct": change_pct,
                }
            )
        except (KeyError, IndexError):
            continue
    return rows


def fetch_indices():
    return {region: _quote_rows(pairs) for region, pairs in INDICES.items()}


def fetch_watchlist():
    return _quote_rows(WATCHLIST)


if __name__ == "__main__":
    import json

    print(json.dumps({"indices": fetch_indices(), "watchlist": fetch_watchlist()}, indent=2))
