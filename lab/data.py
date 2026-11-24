"""Public market data. Kraken first, Coinbase as a fallback. All times UTC.

Only CLOSED candles are returned, so a signal can never peek at a bar
that hasn't finished yet.
"""
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone

import pandas as pd

from . import config

UA = {"User-Agent": "bunny-paper-lab/1.0"}
COLS = ["open", "high", "low", "close", "volume"]


def _get(url: str, tries: int = 3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # network blips happen
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET failed: {url}: {last}")


def _closed(df: pd.DataFrame, minutes: int, now: datetime) -> pd.DataFrame:
    end = df.index + pd.Timedelta(minutes=minutes)
    return df[end <= now]


def kraken_ohlc(pair: str, minutes: int, now: datetime) -> pd.DataFrame:
    js = _get(f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={minutes}")
    if js.get("error"):
        raise RuntimeError(f"Kraken {pair}: {js['error']}")
    key = next(k for k in js["result"] if k != "last")
    rows = js["result"][key]
    df = pd.DataFrame(rows, columns=["t", "open", "high", "low", "close", "vwap", "volume", "n"])
    df.index = pd.to_datetime(df["t"].astype(int), unit="s", utc=True)
    df = df[COLS].astype(float)
    return _closed(df, minutes, now)


def coinbase_ohlc(product: str, seconds: int, start: datetime, end: datetime) -> pd.DataFrame:
    """Pages backwards 300 candles at a time."""
    frames, cur_end = [], end
    while cur_end > start:
        cur_start = max(start, cur_end - timedelta(seconds=seconds * 300))
        url = (f"https://api.exchange.coinbase.com/products/{product}/candles?granularity={seconds}"
               f"&start={cur_start.isoformat()}&end={cur_end.isoformat()}")
        rows = _get(url)
        if rows:
            d = pd.DataFrame(rows, columns=["t", "low", "high", "open", "close", "volume"])
            d.index = pd.to_datetime(d["t"], unit="s", utc=True)
            frames.append(d[COLS].astype(float))
        cur_end = cur_start
        time.sleep(0.15)
    if not frames:
        return pd.DataFrame(columns=COLS)
    df = pd.concat(frames).sort_index()
    df = df[~df.index.duplicated()]
    return _closed(df, seconds // 60, end)


def resample(df: pd.DataFrame, hours: int) -> pd.DataFrame:
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    out = df.resample(f"{hours}h", origin="epoch", label="left", closed="left").agg(agg)
    # only keep buckets that are complete
    counts = df["close"].resample(f"{hours}h", origin="epoch", label="left", closed="left").count()
    return out[counts == hours].dropna()


def check(df: pd.DataFrame, name: str, minutes: int) -> list[str]:
    """Data integrity notes (gaps, dupes, zero-volume, bad prints)."""
    notes = []
    if df.empty:
        return [f"{name}: no data"]
    gaps = (df.index.to_series().diff() > pd.Timedelta(minutes=minutes)).sum()
    if gaps:
        notes.append(f"{name}: {gaps} gap(s) in {minutes}m candles")
    if (df["volume"] == 0).any():
        notes.append(f"{name}: {(df['volume'] == 0).sum()} zero-volume bar(s)")
    bad = (df["high"] < df["low"]) | (df["close"] <= 0)
    if bad.any():
        notes.append(f"{name}: {bad.sum()} bad print(s) dropped")
    return notes


def live_snapshot(now: datetime | None = None):
    """Returns ({coin: 4h_df}, {coin: 1h_df}, notes, source)."""
    now = now or datetime.now(timezone.utc)
    bars4, bars1, notes, sources = {}, {}, [], {}
    for coin, (kpair, cbprod) in config.UNIVERSE.items():
        try:
            b4 = kraken_ohlc(kpair, config.BAR_HOURS * 60, now)
            b1 = kraken_ohlc(kpair, 60, now)
            sources[coin] = "kraken"
        except Exception as e:
            notes.append(f"{coin}: Kraken failed ({e}); using Coinbase")
            b1 = coinbase_ohlc(cbprod, 3600, now - timedelta(days=60), now)
            b4 = resample(b1, config.BAR_HOURS)
            sources[coin] = "coinbase"
        for d, m, label in ((b4, config.BAR_HOURS * 60, "4h"), (b1, 60, "1h")):
            notes += check(d, f"{coin} {label}", m)
        bars4[coin] = b4[(b4["high"] >= b4["low"]) & (b4["close"] > 0)]
        bars1[coin] = b1[(b1["high"] >= b1["low"]) & (b1["close"] > 0)]
    return bars4, bars1, notes, sources
