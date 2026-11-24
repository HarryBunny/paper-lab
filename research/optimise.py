"""Rule search: find daily rules that were profitable over the last 2 years,
then test the winners on 2018–2024 data they never saw.

Every rule is long-only spot, no leverage, with daily bars. The signal is read at the
day's close and the trade fills at the NEXT day's open (no lookahead).
Cost per switch = fee + slippage.

Capital is split into equal "sleeves", one per coin. Each sleeve is either
in its coin or in cash, and the sleeves never rebalance into each other. That is
the same as running one small bot per coin, and it keeps turnover honest.

Run from the repo root:  python3 research/optimise.py
"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "research", "data", "daily")
OUT = os.path.join(ROOT, "research", "2026-11-24-optimise")

FEE = 0.0080                      # Kraken Pro tier 1 taker
SLIP = {"BTC": 0.0005, "ETH": 0.0005}
SLIP_OTHER = 0.0010
TUNE = ("2024-11-24", "2026-11-23")   # the 2-year window Harry asked about
HOLD = ("2018-01-01", "2024-11-23")   # unseen
COINS = ["BTC", "ETH", "SOL", "XRP", "ADA", "LINK"]


def load():
    px = {}
    for c in COINS:
        p = os.path.join(DATA, f"{c}_GBP_1d.csv")
        if os.path.exists(p):
            d = pd.read_csv(p, index_col=0, parse_dates=True)
            d = d[["open", "high", "low", "close"]].astype(float)
            if d.index[-1] < pd.Timestamp(TUNE[0], tz="UTC"):
                print(f"{c}: GBP data ends {d.index[-1].date()}, left out")
                continue
            px[c] = d
    idx = px["BTC"].index
    return {c: d.reindex(idx) for c, d in px.items()}


# ----------------------------------------------------------------- signals
def sma(s, n):
    return s.rolling(n, min_periods=n).mean()


def hysteresis(above_on, below_off):
    """1 once above_on is true; stays 1 until below_off is true."""
    out, state = np.zeros(len(above_on)), 0
    a, b = above_on.values, below_off.values
    for i in range(len(a)):
        if state == 0 and a[i]:
            state = 1
        elif state == 1 and b[i]:
            state = 0
        out[i] = state
    return pd.Series(out, index=above_on.index)


def sig_ma(close, n, buf):
    m = sma(close, n)
    return hysteresis(close > m * (1 + buf), close < m * (1 - buf))


def sig_cross(close, f, s):
    return (sma(close, f) > sma(close, s)).astype(float)


def sig_donchian(df, n_in, n_out):
    hi = df["close"].shift(1).rolling(n_in, min_periods=n_in).max()
    lo = df["close"].shift(1).rolling(n_out, min_periods=n_out).min()
    return hysteresis(df["close"] > hi, df["close"] < lo)


def sig_mom(close, n):
    return (close / close.shift(n) - 1 > 0).astype(float)


# ----------------------------------------------------------------- engine
def sleeve(df, sig, coin, start, end):
    """Equity multiplier series for one sleeve over [start, end]."""
    c = FEE + SLIP.get(coin, SLIP_OTHER)
    o = df["open"]
    r = (o.shift(-1) / o - 1)                       # open t -> open t+1
    pos = sig.shift(1).fillna(0)                    # decided at close t-1, held from open t
    pos[df["close"].isna() | r.isna()] = 0
    w = (pos.index >= start) & (pos.index <= end)
    pos, r = pos[w], r[w].fillna(0)
    pos.iloc[0] = 0 if pos.iloc[0] == 0 else pos.iloc[0]
    prev = pos.shift(1).fillna(0)
    switch = (pos != prev)
    g = (1 + pos * r) * np.where(switch, 1 - c, 1.0)
    # a position still open at the end is sold at the last open (cost charged)
    if pos.iloc[-1] > 0:
        g.iloc[-1] *= (1 - c)
    entries = int(((pos > 0) & (prev == 0)).sum())
    return g.cumprod(), entries, int(switch.sum()) + (1 if pos.iloc[-1] > 0 else 0)


def run(px, rule, coins, start, end, cap=1000.0):
    curves, entries, fills = [], 0, 0
    live = [c for c in coins if c in px and px[c]["close"].loc[start:end].notna().any()]
    if not live:
        return None
    for c in live:
        sig = rule(px, c)
        eq, e, f = sleeve(px[c], sig, c, pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC"))
        curves.append(eq * cap / len(live))
        entries += e
        fills += f
    total = pd.concat(curves, axis=1).sum(axis=1)
    return total, entries, fills, live


def metrics(total, cap=1000.0):
    ret = total.iloc[-1] / cap - 1
    dd = (total / total.cummax() - 1).min()
    q = total.resample("QE").last()
    q0 = pd.concat([pd.Series([cap], index=[total.index[0]]), q]).pct_change().dropna()
    halves = np.array_split(total.values, 2)
    h1 = halves[0][-1] / cap - 1
    h2 = halves[1][-1] / halves[0][-1] - 1
    return {"return_pct": round(ret * 100, 1), "max_dd_pct": round(dd * 100, 1),
            "yr1_pct": round(h1 * 100, 1), "yr2_pct": round(h2 * 100, 1),
            "quarters_up": f"{int((q0 > 0).sum())}/{len(q0)}",
            "worst_quarter_pct": round(q0.min() * 100, 1)}


# ----------------------------------------------------------------- rule grid
def btc_gate(px, n, buf):
    return sig_ma(px["BTC"]["close"], n, buf)


def build_rules():
    rules = []
    for n, buf in itertools.product([20, 30, 50, 75, 100, 150, 200], [0, .02, .05]):
        rules.append((f"own MA{n} ±{int(buf*100)}%", lambda px, c, n=n, b=buf: sig_ma(px[c]["close"], n, b)))
        rules.append((f"BTC MA{n} ±{int(buf*100)}% gate", lambda px, c, n=n, b=buf: btc_gate(px, n, b)))
    for f, s in [(5, 20), (10, 30), (10, 50), (20, 50), (20, 100), (50, 200)]:
        rules.append((f"MA cross {f}/{s}", lambda px, c, f=f, s=s: sig_cross(px[c]["close"], f, s)))
    for ni, no in [(10, 5), (20, 10), (30, 15), (50, 20), (55, 20), (100, 50)]:
        rules.append((f"Donchian {ni}/{no}", lambda px, c, a=ni, b=no: sig_donchian(px[c], a, b)))
        rules.append((f"Donchian {ni}/{no} + BTC MA100 gate",
                      lambda px, c, a=ni, b=no: sig_donchian(px[c], a, b) * btc_gate(px, 100, .02)))
    for n in [14, 30, 60, 90, 120]:
        rules.append((f"momentum {n}d > 0", lambda px, c, n=n: sig_mom(px[c]["close"], n)))
    return rules


UNIVERSES = {"BTC": ["BTC"], "BTC+ETH": ["BTC", "ETH"], "all coins": COINS}


def main():
    px = load()
    os.makedirs(OUT, exist_ok=True)
    avail = {c: str(d["close"].first_valid_index().date()) for c, d in px.items()}
    print("GBP data starts:", avail)
    rows = []
    rules = build_rules()
    for (name, rule), (uname, coins) in itertools.product(rules, UNIVERSES.items()):
        res = run(px, rule, coins, *TUNE)
        if res is None:
            continue
        total, entries, fills, live = res
        m = metrics(total)
        rows.append({"rule": name, "coins": uname, **m, "entries": entries, "fills": fills})
    tune = pd.DataFrame(rows)
    n_tested = len(tune)

    # benchmarks
    bench = []
    for uname, coins in UNIVERSES.items():
        for win, (a, b) in (("tune", TUNE), ("holdout", HOLD)):
            res = run(px, lambda px, c: pd.Series(1.0, index=px[c].index), coins, a, b)
            bench.append({"benchmark": f"buy & hold {uname}", "window": win, **metrics(res[0])})

    consistent = tune[(tune.yr1_pct > 0) & (tune.yr2_pct > 0) & (tune.return_pct > 0)].copy()
    consistent["score"] = consistent.return_pct / consistent.max_dd_pct.abs().clip(lower=1)
    top = consistent.sort_values("score", ascending=False).head(15)

    # out-of-sample: same rules, same coins, unseen 2018–2024
    lookup = dict(rules)
    oos = []
    for _, t in top.iterrows():
        res = run(px, lookup[t.rule], UNIVERSES[t.coins], *HOLD)
        total, entries, fills, live = res
        m = metrics(total)
        yrs = total.resample("YE").last()
        yr = (pd.concat([pd.Series([1000.0], index=[total.index[0]]), yrs]).pct_change().dropna() * 100).round(1)
        oos.append({"rule": t.rule, "coins": t.coins, "tune_return_pct": t.return_pct,
                    "tune_max_dd_pct": t.max_dd_pct, "holdout_return_pct": m["return_pct"],
                    "holdout_max_dd_pct": m["max_dd_pct"], "holdout_entries": entries,
                    "holdout_by_year": {str(k.year): v for k, v in yr.items()},
                    "coins_live_in_holdout": live})
    oos = pd.DataFrame(oos)

    # trade list for the #1 rule in the tuning window
    best = top.iloc[0]
    trades = []
    for c in UNIVERSES[best.coins]:
        if c not in px:
            continue
        s = lookup[best.rule](px, c).shift(1).fillna(0)
        o = px[c]["open"]
        w = s.loc[TUNE[0]:TUNE[1]]
        prev = w.shift(1).fillna(0)
        buys = w.index[(w > 0) & (prev == 0)]
        sells = w.index[(w == 0) & (prev > 0)]
        for b in buys:
            sl = sells[sells > b]
            s_dt = sl[0] if len(sl) else w.index[-1]
            cst = FEE + SLIP.get(c, SLIP_OTHER)
            pnl = (o[s_dt] * (1 - cst)) / (o[b] * (1 + cst)) - 1
            trades.append({"coin": c, "buy": str(b.date()), "buy_£": round(o[b], 4),
                           "sell": str(s_dt.date()) + ("" if len(sl) else " (open)"),
                           "sell_£": round(o[s_dt], 4), "net_pct": round(pnl * 100, 1)})
    trades = pd.DataFrame(trades).sort_values("buy")

    tune.sort_values("return_pct", ascending=False).to_csv(f"{OUT}/all_rules_tune_window.csv", index=False)
    top.to_csv(f"{OUT}/top_consistent_tune.csv", index=False)
    oos.to_json(f"{OUT}/top_rules_on_unseen_2018_2024.json", orient="records", indent=1)
    trades.to_csv(f"{OUT}/best_rule_trades.csv", index=False)
    pd.DataFrame(bench).to_csv(f"{OUT}/benchmarks.csv", index=False)

    summary = {
        "rules_tested": n_tested,
        "profitable_in_tune_window": int((tune.return_pct > 0).sum()),
        "profitable_both_years": len(consistent),
        "data_start": avail,
        "top_holdout_profitable": int((oos.holdout_return_pct > 0).sum()) if len(oos) else 0,
    }
    json.dump(summary, open(f"{OUT}/summary.json", "w"), indent=1)
    pd.set_option("display.width", 250, "display.max_columns", 20, "display.max_colwidth", 40)
    print(json.dumps(summary, indent=1))
    print("\nBENCHMARKS\n", pd.DataFrame(bench).to_string(index=False))
    print("\nTOP CONSISTENT (tune window)\n", top.drop(columns="score").to_string(index=False))
    print("\nSAME RULES ON UNSEEN 2018-2024\n", oos.drop(columns=["coins_live_in_holdout"]).to_string(index=False))
    print(f"\nBEST RULE TRADES: {best.rule} / {best.coins}\n", trades.to_string(index=False))


if __name__ == "__main__":
    main()
