"""Download long DAILY price history for out-of-sample testing.

GBP pairs from Coinbase where they exist. USD pairs are fetched too (longer
history and XRP), for checking signals only, since their returns include GBP/USD moves.
Output: research/data/daily/<COIN>_<CCY>_1d.csv
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab import data  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "daily")
COINS = ["BTC", "ETH", "SOL", "XRP", "ADA", "LINK"]
START = datetime(2017, 1, 1, tzinfo=timezone.utc)


def main():
    os.makedirs(OUT, exist_ok=True)
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    lines = [f"Coinbase Exchange public candles API, 1d, downloaded {now.isoformat()}"]
    for coin in COINS:
        for ccy in ("GBP", "USD"):
            prod = f"{coin}-{ccy}"
            try:
                df = data.coinbase_ohlc(prod, 86400, START, now)
            except Exception as e:
                lines.append(f"{prod}: failed ({e})")
                continue
            if df.empty:
                lines.append(f"{prod}: no data")
                continue
            df.to_csv(os.path.join(OUT, f"{coin}_{ccy}_1d.csv"))
            lines.append(f"{prod}: {len(df)} days {df.index[0].date()} -> {df.index[-1].date()}")
            print(lines[-1], flush=True)
    with open(os.path.join(OUT, "sources.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
