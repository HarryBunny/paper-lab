"""Backtest the exact same engine on ~2 years of Coinbase GBP hourly candles.

Parameters were fixed before looking at any data, so every window here is
out-of-sample for them. Also runs stress tests (double fees, nearby
parameters) and asks the key question: how much does ONE week tell you?

Usage: python backtest.py [days]   (default 730)
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from lab import config as C
from lab import data, engine

OUT = "backtest_results"
WINDOW = 720  # same number of 4h bars the live bot sees from Kraken


def load_history(days: int):
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days + 130)  # +warm-up for the 200-bar EMA
    h1, notes = {}, []
    os.makedirs(f"{OUT}/data", exist_ok=True)
    for coin, (_, prod) in C.UNIVERSE.items():
        path = f"{OUT}/data/{coin}_1h.csv"
        try:
            df = data.coinbase_ohlc(prod, 3600, start, now)
        except Exception as e:
            df, _ = None, print(f"{coin}: download failed: {e}")
        if df is None or len(df) < 24 * 200:
            notes.append(f"{coin}: not enough Coinbase GBP history, left out of the backtest")
            print(notes[-1], flush=True)
            continue
        notes += data.check(df, coin, 60)
        df.to_csv(path)
        h1[coin] = df
        print(f"{coin}: {len(df)} hourly candles {df.index[0]} → {df.index[-1]}", flush=True)
    with open(f"{OUT}/data/sources.md", "w") as f:
        f.write(f"Coinbase Exchange public candles API, 1h, downloaded {now.isoformat()}\n")
    return h1, notes


def run(h1: dict, fee_mult=1.0, overrides=None, label="base"):
    # The live kill switch would halt the bot for good; in the backtest we keep
    # trading and report *when* it would have fired instead.
    overrides = {"KILL_SWITCH_DRAWDOWN": 1.0, **(overrides or {})}
    saved = {k: getattr(C, k) for k in (overrides or {})}
    for k, v in (overrides or {}).items():
        setattr(C, k, v)
    try:
        h4 = {c: data.resample(df, C.BAR_HOURS) for c, df in h1.items()}
        idx = h4[C.REGIME_COIN].index
        for c in h4:
            h4[c] = h4[c].reindex(idx).ffill()
        acct = engine.Account(fee_mult=fee_mult)
        rows = []
        first = idx[0] + pd.Timedelta(days=125)
        bh = None
        for i, t in enumerate(idx):
            if t < first:
                continue
            close_t = t + pd.Timedelta(hours=C.BAR_HOURS)
            prices = {c: float(h4[c]["close"].iloc[i]) for c in h4}
            if bh is None:
                bh = {c: (C.START_CAPITAL_GBP / len(h4)) * (1 - C.FEE_RATE) / prices[c] for c in h4}
                bh_btc = C.START_CAPITAL_GBP * (1 - C.FEE_RATE) / prices["BTC"]
            # stops on the hourly candles inside this 4h bar
            for coin in list(acct.positions):
                hb = h1[coin][(h1[coin].index >= t) & (h1[coin].index < close_t)]
                engine.check_stops(acct, coin, hb, when_fmt=lambda ts: str(ts + pd.Timedelta(hours=1)))
            engine.new_day_check(acct, close_t, prices)
            engine.kill_switch(acct, prices, str(close_t))
            win = {c: h4[c].iloc[max(0, i - WINDOW + 1): i + 1] for c in h4}
            reg = engine.regime(win[C.REGIME_COIN])
            exits, entries = engine.decide(acct, win, reg, close_t)
            for coin, why in exits:
                if coin in acct.positions:
                    acct.sell(coin, prices[coin], str(close_t), why)
            for coin, stop, strat in entries:
                ok, _ = engine.entries_allowed(acct, prices)
                if ok and stop < prices[coin]:
                    acct.buy(coin, prices[coin], stop, strat, str(close_t), reg)
            for c, p in acct.positions.items():
                p["last"] = prices[c]
            rows.append({"time": close_t, "equity": acct.equity(prices), "regime": reg,
                         "bh_basket": sum(bh[c] * prices[c] for c in h4), "bh_btc": bh_btc * prices["BTC"]})
        eq = pd.DataFrame(rows).set_index("time")
        return acct, eq
    finally:
        for k, v in saved.items():
            setattr(C, k, v)


def summarise(acct, eq, label):
    e = eq["equity"]
    trades = pd.DataFrame(acct.trades)
    years = (e.index[-1] - e.index[0]).days / 365.25
    rets = e.pct_change().dropna()
    sharpe = rets.mean() / rets.std() * np.sqrt(6 * 365) if rets.std() > 0 else 0
    pf = None
    if len(trades):
        w, l = trades.pnl_gbp[trades.pnl_gbp > 0].sum(), trades.pnl_gbp[trades.pnl_gbp <= 0].sum()
        pf = round(w / -l, 2) if l < 0 else None
    ks = e[e < C.START_CAPITAL_GBP * (1 - 0.10)]
    return {
        "run": label,
        "kill_switch_would_fire": str(ks.index[0])[:10] if len(ks) else "never",
        "return_pct": round((e.iloc[-1] / C.START_CAPITAL_GBP - 1) * 100, 1),
        "cagr_pct": round(((e.iloc[-1] / C.START_CAPITAL_GBP) ** (1 / years) - 1) * 100, 1) if years > 0 else None,
        "max_dd_pct": round((e / e.cummax() - 1).min() * 100, 1),
        "sharpe": round(sharpe, 2),
        "trades": len(trades),
        "win_rate_pct": round((trades.pnl_gbp > 0).mean() * 100, 1) if len(trades) else None,
        "profit_factor": pf,
        "fees_gbp": round(acct.fees_paid, 2),
        "bh_basket_return_pct": round((eq["bh_basket"].iloc[-1] / C.START_CAPITAL_GBP - 1) * 100, 1),
        "bh_btc_return_pct": round((eq["bh_btc"].iloc[-1] / C.START_CAPITAL_GBP - 1) * 100, 1),
        "bh_basket_max_dd_pct": round((eq["bh_basket"] / eq["bh_basket"].cummax() - 1).min() * 100, 1),
    }


def week_windows(eq):
    """Every rolling 7-day window: how often did the bot make money, and how
    often did a good week sit inside a losing year?"""
    e = eq["equity"]
    step = 6 * 7  # 42 four-hour bars
    wk = (e.shift(-step) / e - 1).dropna() * 100
    return {
        "windows": int(len(wk)),
        "pct_weeks_positive": round((wk > 0).mean() * 100, 1),
        "median_week_pct": round(wk.median(), 2),
        "best_week_pct": round(wk.max(), 2),
        "worst_week_pct": round(wk.min(), 2),
        "p10_p90_pct": [round(wk.quantile(.1), 2), round(wk.quantile(.9), 2)],
    }


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 730
    os.makedirs(OUT, exist_ok=True)
    h1, notes = load_history(days)

    acct, eq = run(h1)
    base = summarise(acct, eq, "base")
    eq.to_csv(f"{OUT}/equity.csv")
    pd.DataFrame(acct.trades).to_csv(f"{OUT}/trades.csv", index=False)

    stress = [base]
    for label, kw in [
        ("double fees", {"fee_mult": 2.0}),
        ("maker fees (0.40%)", {"fee_mult": 0.5}),
        ("breakout 20 bars", {"overrides": {"TREND_BREAKOUT_BARS": 20}}),
        ("breakout 45 bars", {"overrides": {"TREND_BREAKOUT_BARS": 45}}),
        ("stop 2.0 ATR", {"overrides": {"TREND_STOP_ATR": 2.0, "MR_STOP_ATR": 1.5}}),
        ("stop 3.0 ATR", {"overrides": {"TREND_STOP_ATR": 3.0, "MR_STOP_ATR": 2.5}}),
        ("trend only", {"overrides": {"ENABLE_MEANREV": False}}),
        ("meanrev only", {"overrides": {"ENABLE_TREND": False}}),
    ]:
        a, e = run(h1, **kw)
        stress.append(summarise(a, e, label))
        print(label, stress[-1], flush=True)

    # quarter-by-quarter (all out-of-sample: nothing was tuned)
    q = eq.resample("QE").last()
    q_first = eq.resample("QE").first()
    quarters = [{"quarter": f"{t:%Y}-Q{(t.month - 1) // 3 + 1}",
                 "bot_pct": round((q.equity[t] / q_first.equity[t] - 1) * 100, 1),
                 "bh_basket_pct": round((q.bh_basket[t] / q_first.bh_basket[t] - 1) * 100, 1)}
                for t in q.index]

    trades = pd.DataFrame(acct.trades)
    by_strat = (trades.groupby("strategy").pnl_gbp.agg(["count", "sum", "mean"]).round(2).reset_index()
                .to_dict("records")) if len(trades) else []
    regimes = eq["regime"].value_counts(normalize=True).mul(100).round(1).to_dict()

    res = {"generated": datetime.now(timezone.utc).isoformat(), "days": days, "summary": base,
           "stress": stress, "quarters": quarters, "one_week": week_windows(eq),
           "by_strategy": by_strat, "time_in_regime_pct": regimes, "data_notes": notes[:40]}
    with open(f"{OUT}/results.json", "w") as f:
        json.dump(res, f, indent=1, default=str)

    def tbl(rows, cols):
        out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
        return out

    pass_bar = (base["return_pct"] > 0 and base["return_pct"] > base["bh_basket_return_pct"]
                and stress[1]["return_pct"] > 0 and base["trades"] >= 50)
    L = [f"# Backtest: {days} days of GBP crypto, same engine as the live bot", "",
         f"Data: Coinbase Exchange 1h candles, downloaded {res['generated'][:16]}Z. Fees 0.80% a side + slippage.",
         "Parameters were chosen before seeing this data and not tuned, so this whole period is out-of-sample.", "",
         f"**Pass bar** (profitable after costs, beats buy & hold, survives double fees, 50+ trades): "
         f"**{'PASS' if pass_bar else 'FAIL'}**", "", "## Headline and stress tests", ""]
    L += tbl(stress, ["run", "return_pct", "max_dd_pct", "sharpe", "trades", "win_rate_pct",
                      "profit_factor", "fees_gbp", "bh_basket_return_pct", "bh_basket_max_dd_pct", "kill_switch_would_fire"])
    L += ["", "## What one week tells you", "",
          "Every rolling 7-day window in the backtest:", "", "```", json.dumps(res["one_week"], indent=1), "```", "",
          "## Quarter by quarter", ""]
    L += tbl(quarters, ["quarter", "bot_pct", "bh_basket_pct"])
    L += ["", "## By strategy", ""] + tbl(by_strat, ["strategy", "count", "sum", "mean"])
    L += ["", f"Time in each regime (%): {regimes}", "",
          "Data notes: " + ("; ".join(notes[:15]) or "none")]
    with open(f"{OUT}/BACKTEST.md", "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
