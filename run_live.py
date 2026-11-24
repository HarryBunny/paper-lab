"""One hourly tick of the paper-trading bot. Run by GitHub Actions.

Reads state/, pulls fresh public candles, manages stops, acts on any newly
closed 4h bar, writes state/ and REPORT.md back. No exchange account, no
API keys, no real money anywhere.
"""
import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

from lab import config as C
from lab import data, engine, report

STATE = "state"
ACCT = os.path.join(STATE, "account.json")
META = os.path.join(STATE, "meta.json")
EQUITY = os.path.join(STATE, "equity.csv")
LOG = os.path.join(STATE, "log.md")


def load(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)


def log(lines, now):
    if not lines:
        return
    with open(LOG, "a") as f:
        for l in lines:
            f.write(f"- `{now:%Y-%m-%d %H:%M}Z` {l}\n")


def bh_values(meta, prices):
    basket = sum(meta["bh_units"][c] * prices[c] for c in meta["bh_units"])
    btc = meta["bh_btc_units"] * prices["BTC"]
    return basket, btc


def main(now=None, snapshot=None):
    now = now or datetime.now(timezone.utc)
    os.makedirs(STATE, exist_ok=True)
    meta = load(META, {})
    acct = engine.Account(load(ACCT, None))
    events = []

    if meta.get("ended"):
        print("Test already finished. Nothing to do.")
        return

    bars4, bars1, notes, sources = snapshot or data.live_snapshot(now)
    prices = {c: float(df["close"].iloc[-1]) for c, df in bars1.items() if len(df)}
    if set(prices) != set(C.UNIVERSE):
        missing = set(C.UNIVERSE) - set(prices)
        log([f"⚠️ no price for {', '.join(missing)}; skipping this tick"], now)
        return
    price_time = max(df.index[-1] for df in bars1.values()) + pd.Timedelta(hours=1)

    if not meta:  # first ever run
        fee = C.FEE_RATE
        each = C.START_CAPITAL_GBP / len(C.UNIVERSE)
        meta = {
            "lab": C.LAB_NAME,
            "start": now.isoformat(),
            "end": (now + timedelta(days=C.TEST_DAYS)).isoformat(),
            "start_prices": prices,
            "bh_units": {c: each * (1 - fee) / (prices[c] * (1 + engine.slip(c))) for c in prices},
            "bh_btc_units": C.START_CAPITAL_GBP * (1 - fee) / (prices["BTC"] * (1 + engine.slip("BTC"))),
            "last_bar": None,
            "last_stop_check": price_time.isoformat(),
            "fee_rate": C.FEE_RATE,
            "data_sources": sources,
        }
        events.append(f"🟢 Lab started with £{C.START_CAPITAL_GBP:,.0f} paper cash. Ends {meta['end'][:16]}Z.")

    engine.new_day_check(acct, now, prices)

    # 1) stops, using every hourly candle since the last check
    since = pd.Timestamp(meta["last_stop_check"]) - pd.Timedelta(hours=1)
    for coin in list(acct.positions):
        b = bars1[coin][bars1[coin].index >= since]
        t = engine.check_stops(acct, coin, b, when_fmt=lambda ts: (ts + pd.Timedelta(hours=1)).isoformat())
        if t:
            events.append(f"🔴 {t['id']} {coin} stopped out at £{t['exit_price']:,.4f}: "
                          f"£{t['pnl_gbp']:+.2f} ({t['r_multiple']:+.2f}R)")
    meta["last_stop_check"] = price_time.isoformat()

    # 2) kill switch
    for t in engine.kill_switch(acct, prices, now.isoformat()):
        events.append(f"🛑 KILL SWITCH closed {t['id']} {t['coin']}: £{t['pnl_gbp']:+.2f}")
    if acct.halted and not meta.get("halt_logged"):
        events.append(f"🛑 Trading halted: {acct.halt_reason}")
        meta["halt_logged"] = True

    # 3) act on a newly closed 4h bar
    latest_bar = bars4[C.REGIME_COIN].index[-1]
    reg = engine.regime(bars4[C.REGIME_COIN])
    if meta["last_bar"] is None or pd.Timestamp(meta["last_bar"]) < latest_bar:
        meta["last_bar"] = latest_bar.isoformat()
        if reg != meta.get("regime"):
            events.append(f"🧭 Regime: {meta.get('regime') or '—'} → **{reg}**")
            meta["regime"] = reg
        exits, entries = engine.decide(acct, bars4, reg, latest_bar + pd.Timedelta(hours=C.BAR_HOURS))
        for coin, why in exits:
            if coin in acct.positions:
                t = acct.sell(coin, prices[coin], now.isoformat(), why)
                events.append(f"⚪ {t['id']} {coin} closed ({why}): £{t['pnl_gbp']:+.2f} ({t['r_multiple']:+.2f}R)")
        for coin, stop, strat in entries:
            ok, why = engine.entries_allowed(acct, prices)
            if not ok:
                events.append(f"⏸️ Skipped {strat} entry on {coin}: {why}")
                continue
            if stop >= prices[coin]:
                continue  # price already below the stop: setup is gone
            p = acct.buy(coin, prices[coin], stop, strat, now.isoformat(), reg)
            if p:
                events.append(f"🟢 {p['id']} BUY {coin} ({strat}) £{p['qty'] * p['entry_price']:,.2f} "
                              f"@ £{p['entry_price']:,.4f}, stop £{p['stop']:,.4f}, risking £{p['risk_gbp']:.2f}")

    for c, p in acct.positions.items():
        p["last"] = prices[c]

    # 4) end of test: close everything
    if now >= pd.Timestamp(meta["end"]):
        for coin in list(acct.positions):
            t = acct.sell(coin, prices[coin], now.isoformat(), "end of test")
            events.append(f"🏁 {t['id']} {coin} closed at end of test: £{t['pnl_gbp']:+.2f}")
        meta["ended"] = now.isoformat()
        events.append(f"🏁 Test finished. Final equity £{acct.equity(prices):,.2f}")


    # 5) record
    eq = acct.equity(prices)
    basket, btc = bh_values(meta, prices)
    new_file = not os.path.exists(EQUITY)
    with open(EQUITY, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["time", "equity", "cash", "positions", "regime", "bh_basket", "bh_btc"])
        w.writerow([now.strftime("%Y-%m-%dT%H:%MZ"), round(eq, 2), round(acct.cash, 2),
                    len(acct.positions), meta.get("regime", reg), round(basket, 2), round(btc, 2)])

    # only log data-quality notes when they change, so the log stays readable
    note_key = sorted(n.split(":")[0] for n in notes)
    if note_key != meta.get("data_note_key"):
        meta["data_note_key"] = note_key
        for n in notes:
            events.append(f"🔎 data: {n}")

    log(events, now)
    save(ACCT, acct.to_dict())
    save(META, meta)
    report.write(acct, meta, prices, EQUITY, LOG)
    print("\n".join(events) or "No trades this tick.")
    print(f"Equity £{acct.equity(prices):,.2f} | regime {reg}")


if __name__ == "__main__":
    main()
