"""Offline test on synthetic prices: runs the backtest and ~2 weeks of live
ticks with fake data, checking the accounting adds up."""
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab import config as C, data  # noqa: E402

rng = np.random.default_rng(7)
END = datetime(2026, 11, 24, 10, tzinfo=timezone.utc)
HOURS = 24 * 900
idx = pd.date_range(END - timedelta(hours=HOURS), periods=HOURS, freq="h", tz="UTC")
drift = np.repeat(rng.normal(0, 0.0004, HOURS // 500 + 1), 500)[:HOURS]  # regime-like drifts
mkt = rng.normal(0, 0.007, HOURS) + drift
start = {"BTC": 70000, "ETH": 2500, "SOL": 120, "XRP": 1.8, "ADA": 0.5, "LINK": 12}
SYN = {}
for c, p0 in start.items():
    r = mkt * (1.0 if c == "BTC" else 1.3) + rng.normal(0, 0.006, HOURS)
    close = p0 * np.exp(np.cumsum(r))
    open_ = np.r_[p0, close[:-1]]
    hi = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.003, HOURS)))
    lo = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.003, HOURS)))
    SYN[c] = pd.DataFrame({"open": open_, "high": hi, "low": lo, "close": close,
                           "volume": rng.uniform(1, 10, HOURS)}, index=idx)


def fake_coinbase(prod, seconds, s, e):
    coin = prod.split("-")[0]
    df = SYN[coin]
    return df[(df.index >= s) & (df.index + pd.Timedelta(hours=1) <= e)]


def fake_snapshot(now):
    b1 = {c: df[df.index + pd.Timedelta(hours=1) <= now].iloc[-720:] for c, df in SYN.items()}
    b4 = {c: data.resample(df[df.index + pd.Timedelta(hours=1) <= now], 4).iloc[-720:] for c, df in SYN.items()}
    return b4, b1, [], {c: "synthetic" for c in SYN}


if __name__ == "__main__":
    work = "/tmp/simrun"
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    os.chdir(work)
    data.coinbase_ohlc = fake_coinbase

    import backtest
    sys.argv = ["backtest.py", os.environ.get("SIM_DAYS", "700")]
    backtest.main()

    # live: simulate 14 days of hourly ticks (bot should stop itself after 7)
    import run_live
    t0 = END - timedelta(days=20)
    for h in range(14 * 24):
        now = t0 + timedelta(hours=h, minutes=7)
        run_live.main(now=now, snapshot=fake_snapshot(now))
    import json
    acct = json.load(open("state/account.json"))
    meta = json.load(open("state/meta.json"))
    eq = pd.read_csv("state/equity.csv")
    print("ticks recorded:", len(eq), "ended:", meta.get("ended"))
    print("final equity", eq.equity.iloc[-1], "cash", acct["cash"], "open", acct["positions"])
    pnl = sum(t["pnl_gbp"] for t in acct["trades"])
    print("sum trade pnl", round(pnl, 2), "equity-start", round(acct["cash"] - 1000, 2))
    assert not acct["positions"], "positions should be closed at end"
    assert abs(pnl - (acct["cash"] - 1000)) < 0.2, "P&L doesn't reconcile with cash"
    assert len(eq) == 7 * 24 + 1 or len(eq) == 7 * 24, len(eq)
    print("OK")
