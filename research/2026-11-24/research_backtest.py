"""Standalone daily-bar backtest of the research ideas (scratch analysis, not the live bot).

Run:  python3 research_backtest.py            (from the repo root: python3 research/2026-11-24/research_backtest.py)

Conventions (no lookahead):
  * Hourly GBP candles are resampled to UTC daily bars (open = first hour's open, close = last hour's close).
  * Every signal for day t uses only closes up to and including day t.
  * The resulting trade is filled at the OPEN of day t+1, plus slippage (BTC/ETH 0.05%, others 0.10%)
    plus the fee for the scenario. Costs are charged on the traded value, every side.
  * Equity is marked at each day's close. Long-only, never more than 100% invested, no leverage.
  * All variants are scored over ONE common window that starts after the longest warm-up used (250 days),
    so the numbers are comparable. The current bot's equity curve (backtest_results/equity.csv) is cut to
    the same window.
"""
import os
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
DATA = os.path.join(HERE, "backtest_results", "data")
COINS = ["BTC", "ETH", "SOL", "ADA", "LINK"]
SLIP = {"BTC": 0.0005, "ETH": 0.0005, "SOL": 0.0010, "ADA": 0.0010, "LINK": 0.0010}
FEES = {"Kraken T1 taker 0.80%": 0.0080, "Kraken T2 taker 0.60%": 0.0060,
        "Coinbase reported taker 0.50%": 0.0050, "maker 0.25%": 0.0025}
START_GBP = 1000.0
WARMUP_DAYS = 250
MIN_ORDER = 10.0


# ---------------------------------------------------------------- data
def load_daily():
    opens, closes = {}, {}
    for c in COINS:
        h = pd.read_csv(os.path.join(DATA, f"{c}_1h.csv"), parse_dates=["t"]).set_index("t").sort_index()
        d = h.resample("1D").agg({"open": "first", "close": "last"})
        opens[c], closes[c] = d["open"], d["close"]
    o, cl = pd.DataFrame(opens), pd.DataFrame(closes)
    # drop the partial first and last day, forward-fill any day with no candles at all
    o, cl = o.iloc[1:-1], cl.iloc[1:-1]
    cl = cl.ffill()
    o = o.fillna(cl.shift(1)).ffill()
    return o, cl


# ---------------------------------------------------------------- engine
def simulate(open_, close, target, fee, buffer_rel=0.10, start=None):
    """target: DataFrame of desired weights decided at day t's close (index = day t).
    Rebalanced at day t+1's open. A coin is traded if it moves to/from zero, or its weight
    differs from target by more than buffer_rel x the larger of the two weights."""
    days = close.index[close.index >= start]
    cash, qty = START_GBP, {c: 0.0 for c in COINS}
    eq, fills, fees_paid, entries = [], 0, 0.0, 0
    prev_day = close.index[close.index.get_loc(days[0]) - 1]
    for d in days:
        tw = target.loc[prev_day]  # decided at yesterday's close -> no lookahead
        px = open_.loc[d]
        val = {c: qty[c] * px[c] for c in COINS}
        equity = cash + sum(val.values())
        # sells first, then buys, so cash is available
        order = sorted(COINS, key=lambda c: tw[c] * equity - val[c])
        for c in order:
            cur_w, tgt_w = val[c] / equity, float(tw[c])
            delta = tgt_w * equity - val[c]
            to_or_from_zero = (tgt_w == 0) != (cur_w < 1e-9)
            big = abs(tgt_w - cur_w) > buffer_rel * max(tgt_w, cur_w)
            if not (to_or_from_zero or big) or abs(delta) < MIN_ORDER:
                continue
            cost_rate = fee + SLIP[c]
            if delta > 0:
                spend = min(delta, cash)
                if spend < MIN_ORDER:
                    continue
                q = spend / (px[c] * (1 + SLIP[c])) / (1 + fee)
                fees_paid += spend - q * px[c] * (1 + SLIP[c])  # fee part
                cash -= spend
                if qty[c] < 1e-12:
                    entries += 1
                qty[c] += q
            else:
                q = min(-delta / px[c], qty[c]) if tgt_w > 0 else qty[c]
                gross = q * px[c] * (1 - SLIP[c])
                fees_paid += gross * fee
                cash += gross * (1 - fee)
                qty[c] -= q
            fills += 1
        eq.append(cash + sum(qty[c] * close.loc[d, c] for c in COINS))
        prev_day = d
    return pd.Series(eq, index=days), fills, entries, fees_paid


def buy_and_hold(open_, close, weights, fee, start):
    tgt = pd.DataFrame(0.0, index=close.index, columns=COINS)
    for c, w in weights.items():
        tgt[c] = w
    # huge buffer so it never rebalances after the first buy
    return simulate(open_, close, tgt, fee, buffer_rel=10.0, start=start)


# ---------------------------------------------------------------- signals
def trend_switch(close, sma_len=200, band=0.0, persist=1, coins=COINS):
    """On when BTC close > SMA*(1+band) for `persist` days in a row, off when < SMA*(1-band)
    for `persist` days in a row, otherwise keep the previous state."""
    btc = close["BTC"]
    sma = btc.rolling(sma_len).mean()
    above = (btc > sma * (1 + band)).astype(int)
    below = (btc < sma * (1 - band)).astype(int)
    up_run = above.rolling(persist).sum() == persist
    dn_run = below.rolling(persist).sum() == persist
    state, on = [], False
    for d in close.index:
        if np.isnan(sma.loc[d]):
            on = False
        elif up_run.loc[d]:
            on = True
        elif dn_run.loc[d]:
            on = False
        state.append(on)
    state = pd.Series(state, index=close.index)
    tgt = pd.DataFrame(0.0, index=close.index, columns=COINS)
    for c in coins:
        tgt[c] = state.astype(float) / len(coins)
    return tgt


def breakout_ensemble(close, lookbacks=(20, 50, 100), vol_len=60):
    """Per coin and N: go long when close > highest close of the PRIOR N days; trailing stop
    = midpoint of the prior N-day close range, ratcheted up only; exit when close < stop.
    Coin signal = average over N (0, 1/3, 2/3, 1). Weight = signal x coin's inverse-vol share
    of the 5 coins, so total exposure is at most 100%."""
    sig = pd.DataFrame(0.0, index=close.index, columns=COINS)
    for c in COINS:
        px = close[c]
        for n in lookbacks:
            hi = px.shift(1).rolling(n).max()
            lo = px.shift(1).rolling(n).min()
            mid = (hi + lo) / 2
            on, stop, out = False, np.nan, []
            for d in close.index:
                p = px.loc[d]
                if np.isnan(hi.loc[d]):
                    out.append(0.0)
                    continue
                if not on and p > hi.loc[d]:
                    on, stop = True, mid.loc[d]
                elif on:
                    stop = max(stop, mid.loc[d])
                    if p < stop:
                        on = False
                out.append(1.0 if on else 0.0)
            sig[c] += np.array(out) / len(lookbacks)
    vol = np.log(close).diff().rolling(vol_len).std()
    inv = 1 / vol
    share = inv.div(inv.sum(axis=1), axis=0).fillna(0)
    return (sig * share).fillna(0)


# ---------------------------------------------------------------- scoring
def score(eq, fills, entries, fees):
    e = eq
    wk = e.pct_change(7).dropna()
    dd = (e / e.cummax() - 1).min()
    return {"net_return_pct": round((e.iloc[-1] / START_GBP - 1) * 100, 1),
            "max_dd_pct": round(dd * 100, 1),
            "orders": fills, "entries": entries,
            "fees_gbp": round(fees, 0),
            "weeks_up_pct": round((wk > 0.0005).mean() * 100, 0),
            "weeks_down_pct": round((wk < -0.0005).mean() * 100, 0)}


def current_bot(start, end):
    eq = pd.read_csv(os.path.join(HERE, "backtest_results", "equity.csv"), parse_dates=["time"]).set_index("time")
    e = eq["equity"].resample("1D").last().dropna()
    e = e[(e.index >= start) & (e.index <= end)]
    e = e / e.iloc[0] * START_GBP
    tr = pd.read_csv(os.path.join(HERE, "backtest_results", "trades.csv"), parse_dates=["entry_time"])
    tr = tr[(tr.entry_time >= start) & (tr.entry_time <= end + pd.Timedelta(days=1))]
    s = score(e, 2 * len(tr), len(tr), tr.fees_gbp.sum())
    s["note"] = "4h bot, Kraken T1 taker, rescaled to £1,000 at window start; has 6 coins incl. XRP"
    return s


def main():
    o, c = load_daily()
    start = c.index[WARMUP_DAYS]
    end = c.index[-1]
    rows = []

    def run(name, tgt, fee_name, fee, **kw):
        eq, f, e, fe = simulate(o, c, tgt, fee, start=start, **kw)
        r = score(eq, f, e, fe)
        rows.append({"variant": name, "fees": fee_name, **r})
        return eq

    eqs = {}
    for fn, fee in FEES.items():
        for nm, w in [("Buy & hold basket (5 coins)", {k: 0.2 for k in COINS}), ("Buy & hold BTC", {"BTC": 1.0})]:
            eq, f, e, fe = buy_and_hold(o, c, w, fee, start)
            rows.append({"variant": nm, "fees": fn, **score(eq, f, e, fe)})
            eqs[(nm, fn)] = eq
        eqs[("switch_basket", fn)] = run("Trend switch basket, SMA200 ±2%", trend_switch(c, 200, 0.02), fn, fee)
        eqs[("switch_btc", fn)] = run("Trend switch BTC only, SMA200 ±2%", trend_switch(c, 200, 0.02, coins=["BTC"]), fn, fee)
        run("Trend switch basket, SMA200 no buffer", trend_switch(c, 200, 0.0), fn, fee)
        eqs[("breakout", fn)] = run("Breakout ensemble N=20/50/100", breakout_ensemble(c), fn, fee)
    main_df = pd.DataFrame(rows)

    # sensitivity at Kraken T2 (0.60%) and Kraken T1 (0.80%)
    sens = []
    for fn in ["Kraken T1 taker 0.80%", "Kraken T2 taker 0.60%"]:
        fee = FEES[fn]
        for coins_lbl, coins in [("basket", COINS), ("BTC", ["BTC"])]:
            for sma in (150, 200, 250):
                for band, persist, lbl in [(0.0, 1, "none"), (0.02, 1, "±2%"), (0.03, 1, "±3%"),
                                           (0.0, 2, "2 days"), (0.0, 3, "3 days")]:
                    eq, f, e, fe = simulate(o, c, trend_switch(c, sma, band, persist, coins), fee, start=start)
                    sens.append({"variant": f"Switch {coins_lbl} SMA{sma} buffer {lbl}", "fees": fn, **score(eq, f, e, fe)})
        for lbs in [(20, 50, 100), (10, 20, 50), (50, 100, 200), (20,), (50,), (100,), (20, 50, 100, 200)]:
            eq, f, e, fe = simulate(o, c, breakout_ensemble(c, lbs), fee, start=start)
            sens.append({"variant": f"Breakout N={'/'.join(map(str, lbs))}", "fees": fn, **score(eq, f, e, fe)})
        for sma in (150, 200, 250):
            filt = (trend_switch(c, sma, 0.02)["BTC"] > 0).astype(float)
            eq, f, e, fe = simulate(o, c, breakout_ensemble(c).mul(filt, axis=0), fee, start=start)
            sens.append({"variant": f"Breakout N=20/50/100 only while BTC SMA{sma} ±2% switch is on", "fees": fn, **score(eq, f, e, fe)})
        for buf in (0.05, 0.25, 0.50):
            eq, f, e, fe = simulate(o, c, breakout_ensemble(c), fee, start=start, buffer_rel=buf)
            sens.append({"variant": f"Breakout N=20/50/100, rebalance buffer {int(buf*100)}%", "fees": fn, **score(eq, f, e, fe)})
    sens_df = pd.DataFrame(sens)

    bot = current_bot(start, end)

    # coin-by-coin buy & hold over the window, for context
    bh_coin = {k: round((c[k].iloc[-1] / o.loc[start, k] - 1) * 100, 1) for k in COINS}
    # half-yearly path of the main variants (T2 fees) to show where gains/losses came from
    fn = "Kraken T2 taker 0.60%"
    path = pd.DataFrame({"B&H basket": eqs[("Buy & hold basket (5 coins)", fn)],
                         "B&H BTC": eqs[("Buy & hold BTC", fn)],
                         "Switch basket": eqs[("switch_basket", fn)],
                         "Switch BTC": eqs[("switch_btc", fn)],
                         "Breakout": eqs[("breakout", fn)]})
    q = path.resample("QE").last()
    q_ret = (q / q.shift(1).fillna(START_GBP) - 1).mul(100).round(1)
    q_ret.index = [f"{d.year}-Q{(d.month - 1) // 3 + 1}" for d in q_ret.index]

    out = {"window": [str(start.date()), str(end.date())], "days": int((end - start).days),
           "first_trade_day": str(start.date()), "bh_coin_pct": bh_coin,
           "current_bot_same_window": bot}
    with open(os.path.join(HERE, "research_results.json"), "w") as f:
        json.dump({**out, "main": main_df.to_dict("records"), "sensitivity": sens_df.to_dict("records"),
                   "quarterly_T2": q_ret.reset_index().to_dict("records")}, f, indent=1, default=str)
    pd.set_option("display.width", 250, "display.max_rows", 500, "display.max_colwidth", 60)
    print(json.dumps(out, indent=1))
    print(main_df.to_string(index=False))
    print(sens_df.to_string(index=False))
    print(q_ret.to_string())


if __name__ == "__main__":
    main()
