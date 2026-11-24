"""Independent assessment of trend / risk-control rules for the paper lab (round 2).

Run from the repo root:   python3 research/2026-11-24-round2/assess.py
Writes: research/2026-11-24-round2/assess_results.json and assess_tables.md

Conventions (all strategies):
- Daily UTC bars. A decision uses closes up to and including day t; it is filled at the
  OPEN of day t+1 (never the same bar).
- Costs per side: fee (0.80% taker, or 0.40% maker run) + slippage (0.05% BTC/ETH,
  0.10% others), applied as a worse fill price plus the fee on notional.
- Long-only spot, never more than 100% invested, no leverage, no shorts.
- Idle cash: two runs, 0% and 4%/yr (UK savings), credited daily on cash only.
- Equity is marked to market at each close; no forced sale at the end.
- Prices: Coinbase GBP candles where they exist. Before a coin's GBP history starts
  (ETH before Sep 2018, LINK before Jul 2020) and for XRP throughout (the GBP file is
  unusable), USD candles are converted at the implied GBP/USD rate
  (BTC-GBP close / BTC-USD close, 7-day rolling median). These are flagged "synthetic".
- Coin universe = the live bot's six coins, picked with hindsight (survivorship bias).
"""
import json
import os
import sys
from itertools import product

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "research", "data", "daily")
OUT = os.path.join(ROOT, "research", "2026-11-24-round2")

COINS = ["BTC", "ETH", "SOL", "XRP", "ADA", "LINK"]
SLIP = {"BTC": 0.0005, "ETH": 0.0005}
SLIP_OTHER = 0.0010
TAKER, MAKER = 0.0080, 0.0040
CASH_RATE = 0.04
START, END = "2019-01-01", "2026-11-23"
CAP = 1000.0
MIN_TRADE_FRAC = 0.005          # ignore trades smaller than 0.5% of equity (dust)

VARIANTS = set()                 # every distinct strategy configuration evaluated


# ============================================================== data
class Data:
    def __init__(self, cutoff=None):
        g, u = {}, {}
        for c in COINS:
            for q, store in (("GBP", g), ("USD", u)):
                p = os.path.join(DATA, f"{c}_{q}_1d.csv")
                if os.path.exists(p):
                    d = pd.read_csv(p, index_col=0, parse_dates=True)[["open", "close"]].astype(float)
                    store[c] = d
        g.pop("XRP", None)                                       # unusable (ends Jan 2021)
        idx = pd.date_range(g["BTC"].index[0], g["BTC"].index[-1], freq="D")
        fx = (g["BTC"]["close"] / u["BTC"]["close"]).reindex(idx).ffill().rolling(7, min_periods=1).median()
        O, C, syn = {}, {}, {}
        for c in COINS:
            gb = g[c].reindex(idx) if c in g else pd.DataFrame(index=idx, columns=["open", "close"], dtype=float)
            us = u[c].reindex(idx).mul(fx, axis=0)
            O[c] = gb["open"].combine_first(us["open"])
            C[c] = gb["close"].combine_first(us["close"])
            syn[c] = gb["close"].isna() & us["close"].notna()
        self.idx = idx
        self.O = pd.DataFrame(O)[COINS]
        self.C = pd.DataFrame(C)[COINS]
        self.synthetic = pd.DataFrame(syn)[COINS]
        if cutoff is not None:                                   # lookahead test: hide the future
            cut = pd.Timestamp(cutoff, tz="UTC")
            self.O.loc[self.O.index > cut] = np.nan
            self.C.loc[self.C.index > cut] = np.nan
        self.o = self.O.values
        self.c = self.C.values
        self.k = {c: i for i, c in enumerate(COINS)}
        self._cache = {}

    def pos(self, date):
        return int(self.idx.get_indexer([pd.Timestamp(date, tz="UTC")])[0])

    def cached(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    # ---- indicators (each value at row t uses closes <= t only)
    def sma(self, coin, n):
        return self.cached(("sma", coin, n), lambda: self.C[coin].rolling(n, min_periods=n).mean().values)

    def vol(self, coin, n):
        return self.cached(("vol", coin, n), lambda: (np.log(self.C[coin]).diff()
                                                      .rolling(n, min_periods=n).std() * np.sqrt(365)).values)

    def ma_switch(self, coin, n, buf, weekly=False):
        """1 once close > MA*(1+buf); back to 0 once close < MA*(1-buf). Weekly: only on Friday closes."""
        def f():
            c, m = self.C[coin].values, self.sma(coin, n)
            fri = (self.idx.dayofweek == 4)
            out, s = np.full(len(c), np.nan), 0.0
            for i in range(len(c)):
                if np.isnan(m[i]) or np.isnan(c[i]):
                    out[i] = s if not np.isnan(m[i]) else np.nan
                    continue
                if not weekly or fri[i]:
                    if s == 0 and c[i] > m[i] * (1 + buf):
                        s = 1.0
                    elif s == 1 and c[i] < m[i] * (1 - buf):
                        s = 0.0
                out[i] = s
            return out
        return self.cached(("maswitch", coin, n, buf, weekly), f)

    def ma_ensemble(self, coin, lens, weekly=False):
        """Fraction of MAs in `lens` that the close is above (0, 1/k, ..., 1)."""
        def f():
            c = self.C[coin].values
            mats = np.array([self.sma(coin, n) for n in lens])
            frac = np.where(np.isnan(mats).any(0), np.nan, (c[None, :] > mats).mean(0))
            if weekly:
                fri = (self.idx.dayofweek == 4)
                frac = pd.Series(np.where(fri, frac, np.nan)).ffill().values
            return frac
        return self.cached(("maens", coin, tuple(lens), weekly), f)

    def donchian(self, coin, n, ratchet=True):
        """Long-only breakout leg: on when close > highest close of previous n days;
        off when close < stop, stop = midpoint of previous-n-day range, ratcheted up while on."""
        def f():
            s = self.C[coin]
            hi = s.shift(1).rolling(n, min_periods=n).max().values
            lo = s.shift(1).rolling(n, min_periods=n).min().values
            mid = (hi + lo) / 2
            c = s.values
            out, on, stop = np.zeros(len(c)), False, -np.inf
            for i in range(len(c)):
                if np.isnan(hi[i]) or np.isnan(c[i]):
                    out[i] = 1.0 if on else 0.0
                    continue
                if on:
                    stop = max(stop, mid[i]) if ratchet else mid[i]
                    if c[i] < stop:
                        on, stop = False, -np.inf
                elif c[i] > hi[i]:
                    on, stop = True, mid[i]
                out[i] = 1.0 if on else 0.0
            return out
        return self.cached(("don", coin, n, ratchet), f)

    def age(self, coin):
        return self.cached(("age", coin), lambda: self.C[coin].notna().cumsum().values)


# ============================================================== engine
def simulate(D, decide, start, end, fee, rate, coins, cap=CAP):
    """decide(i, w, eq) -> array of target weights (NaN = leave coin alone) or None.
    Called at the close of row i; executed at the open of row i+1."""
    ks = [D.k[c] for c in coins]
    slip = np.array([SLIP.get(c, SLIP_OTHER) for c in coins])
    i0, i1 = D.pos(start), D.pos(end)
    units, cash = np.zeros(len(ks)), cap
    daily_int = (1 + rate) ** (1 / 365) - 1
    eq_s, fees, slips, orders, disp, proceeds = [], [], [], [], [], []
    ep_cost, ep_proc, episodes = np.zeros(len(ks)), np.zeros(len(ks)), []
    lastc = np.nan_to_num(D.c[i0 - 1, ks])
    pending = decide(i0 - 1, np.zeros(len(ks)), cap)
    for i in range(i0, i1 + 1):
        o = D.o[i, ks]
        f_day = s_day = n_ord = n_disp = p_day = 0.0
        if pending is not None:
            px = np.where(np.isnan(o), lastc, o)
            val = units * px
            eq = cash + val.sum()
            tgt = np.where(np.isnan(pending), val / eq if eq > 0 else 0, pending)
            tgt = np.where(np.isnan(o), val / eq, tgt)          # no price, no trade
            delta = tgt * eq - val
            for j in np.argsort(delta):                            # sells first
                d = delta[j]
                if abs(d) < MIN_TRADE_FRAC * eq and not (tgt[j] == 0 and units[j] > 0):
                    continue
                if d < 0:
                    q = units[j] if tgt[j] == 0 else min(units[j], -d / px[j])
                    gross = q * px[j] * (1 - slip[j])
                    cash += gross * (1 - fee)
                    units[j] -= q
                    f_day += gross * fee; s_day += q * px[j] * slip[j]; p_day += gross
                    n_ord += 1; n_disp += 1
                    ep_proc[j] += gross * (1 - fee)
                    if units[j] <= 1e-15:
                        units[j] = 0.0
                        if ep_cost[j] > 0:
                            episodes.append(ep_proc[j] / ep_cost[j] - 1)
                        ep_cost[j] = ep_proc[j] = 0.0
                elif d > 0:
                    spend = min(d * (1 + fee), cash)
                    if spend <= 0:
                        continue
                    notional = spend / (1 + fee)
                    units[j] += notional / (px[j] * (1 + slip[j]))
                    cash -= spend
                    f_day += notional * fee; s_day += notional * slip[j] / (1 + slip[j])
                    n_ord += 1
                    ep_cost[j] += spend
        cash *= 1 + daily_int
        c = D.c[i, ks]
        lastc = np.where(np.isnan(c), lastc, c)
        val = units * lastc
        eq = cash + val.sum()
        eq_s.append(eq); fees.append(f_day); slips.append(s_day)
        orders.append(n_ord); disp.append(n_disp); proceeds.append(p_day)
        w = val / eq if eq > 0 else val * 0
        pending = decide(i, w, eq) if i < i1 else None
    ix = D.idx[i0:i1 + 1]
    return pd.DataFrame({"eq": eq_s, "fee": fees, "slip": slips, "orders": orders,
                         "disp": disp, "proc": proceeds}, index=ix), episodes


def banded(target, w, band, relative=False):
    """Trade a coin only on entry, full exit, or when off target by >= band."""
    out = np.full(len(target), np.nan)
    for j in range(len(target)):
        t = target[j]
        if np.isnan(t):
            continue
        if t <= 0:
            if w[j] > 1e-9:
                out[j] = 0.0
        elif w[j] <= 1e-9:
            out[j] = t
        else:
            thr = band * max(t, w[j]) if relative else band
            if abs(t - w[j]) >= thr - 1e-12:
                out[j] = t
    return None if np.isnan(out).all() else out


# ============================================================== strategies
# A strategy = list of sleeves (capital share, coins, factory). factory(D, start, end) -> decide fn.

def S_hold(weights):
    """Buy once at the start, never trade again."""
    def fac(D, start, end):
        done = [False]
        def decide(i, w, eq):
            if not done[0]:
                done[0] = True
                return np.array(weights, float)
            return None
        return decide
    return fac


def S_ew_basket(coins):
    """Equal weight of coins with >= 30 days of data; rebalance on a new coin and each 1 Jan."""
    def fac(D, start, end):
        last = [None]
        def decide(i, w, eq):
            elig = tuple(c for c in coins if D.age(c)[i] >= 30)
            newyear = D.idx[i + 1].dayofyear == 1 if i + 1 < len(D.idx) else False
            if elig != last[0] or newyear:
                last[0] = elig
                return np.array([1 / len(elig) if c in elig else 0.0 for c in coins])
            return None
        return decide
    return fac


def S_dca():
    """Invest the starting cash in equal monthly slices (1st of each month) over the window."""
    def fac(D, start, end):
        months = pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq="MS")
        n = len(months)
        k = [0]
        def decide(i, w, eq):
            nxt = D.idx[i + 1] if i + 1 < len(D.idx) else None
            if nxt is not None and nxt.day == 1 and k[0] < n:
                rem = n - k[0]
                k[0] += 1
                return np.array([w[0] + (1 - w[0]) / rem])
            return None
        return decide
    return fac


def S_btc_ma(n=200, buf=0.02, weekly=False, coin="BTC"):
    def fac(D, start, end):
        sig = D.ma_switch(coin, n, buf, weekly)
        def decide(i, w, eq):
            s = sig[i]
            return banded(np.array([0.0 if np.isnan(s) else s]), w, 0.2)
        return decide
    return fac


def S_btc_ens(lens=(50, 100, 150, 200, 250), weekly=False, band=0.2):
    def fac(D, start, end):
        fr = D.ma_ensemble("BTC", lens, weekly)
        def decide(i, w, eq):
            s = fr[i]
            return banded(np.array([0.0 if np.isnan(s) else s]), w, band)
        return decide
    return fac


def S_volscaled(target=0.40, n=30, band=0.2, base=None):
    """BTC weight = min(1, target / realised vol); optional base = (kind, params) trend overlay."""
    def fac(D, start, end):
        v = D.vol("BTC", n)
        if base is None:
            b = np.ones(len(v))
        elif base[0] == "ma":
            b = D.ma_switch("BTC", *base[1])
        else:
            b = D.ma_ensemble("BTC", *base[1])
        def decide(i, w, eq):
            if np.isnan(v[i]) or np.isnan(b[i]):
                return None
            t = b[i] * min(1.0, target / v[i])
            return banded(np.array([t]), w, band)
        return decide
    return fac


def S_fixed_mix(wt=0.5, band=0.15):
    def fac(D, start, end):
        def decide(i, w, eq):
            return banded(np.array([wt]), w, band)
        return decide
    return fac


def S_labb(coins, lens, gate=True, invvol=True, cap=0.40, band=0.25, ratchet=True, gate_n=200, gate_buf=0.02,
           vol_n=60):
    def fac(D, start, end):
        legs = {c: np.array([D.donchian(c, n, ratchet) for n in lens]) for c in coins}
        ages = {c: D.age(c) for c in coins}
        vols = {c: D.vol(c, vol_n) for c in coins}
        g = D.ma_switch("BTC", gate_n, gate_buf) if gate else None
        def decide(i, w, eq):
            elig = [j for j, c in enumerate(coins) if not np.isnan(vols[c][i])]
            if not elig:
                return None
            if invvol:
                inv = np.array([1 / vols[coins[j]][i] for j in elig])
                base = inv / inv.sum()
            else:
                base = np.full(len(elig), 1 / len(elig))
            base = np.minimum(base, cap)
            tgt = np.zeros(len(coins))
            for b, j in zip(base, elig):
                c = coins[j]
                active = [k for k, n in enumerate(lens) if ages[c][i] > n]
                sig = legs[c][active, i].sum() / len(lens) if active else 0.0
                tgt[j] = b * sig
            if gate and not (g[i] == 1):
                tgt[:] = 0.0
            return banded(tgt, w, band, relative=True)
        return decide
    return fac


def S_weekly(fac):
    """Wrap a strategy so it only acts on Friday closes (plus the very first decision)."""
    def fac2(D, start, end):
        inner, first = fac(D, start, end), [True]
        def decide(i, w, eq):
            t = inner(i, w, eq)                     # keep any inner state up to date
            if first[0]:
                first[0] = False
                return t
            return t if D.idx[i].dayofweek == 4 else None
        return decide
    return fac2


def S_gated_basket(coins, n=200, buf=0.02):
    """Equal weight of coins with >= 30 days of data, only while BTC is above its MA (with buffer)."""
    def fac(D, start, end):
        g = D.ma_switch("BTC", n, buf)
        def decide(i, w, eq):
            elig = [c for c in coins if D.age(c)[i] >= 30]
            on = g[i] == 1
            tgt = np.array([1 / len(elig) if (on and c in elig) else 0.0 for c in coins])
            return banded(tgt, w, 0.25, relative=True)
        return decide
    return fac


# ============================================================== registry
ALL6 = COINS
BE = ["BTC", "ETH"]
NARROW, WIDE = (20, 50, 100), (10, 20, 50, 100, 150, 250, 360)
ENS = (50, 100, 150, 200, 250)


def own_ma(n, buf, coins=BE):
    return [(1 / len(coins), [c], S_btc_ma(n, buf, False, coin=c)) for c in coins]


STRATS = {
    # 1 benchmarks
    "B&H BTC": [(1, ["BTC"], S_hold([1]))],
    "B&H BTC+ETH 50/50": [(1, BE, S_hold([0.5, 0.5]))],
    "EW basket (6, yearly rebal)": [(1, ALL6, S_ew_basket(ALL6))],
    "DCA BTC monthly": [(1, ["BTC"], S_dca())],
    # 2 BTC trend
    "BTC MA200 ±2% daily": [(1, ["BTC"], S_btc_ma(200, 0.02))],
    "BTC MA200 ±2% weekly": [(1, ["BTC"], S_btc_ma(200, 0.02, True))],
    "BTC MA-ensemble daily": [(1, ["BTC"], S_btc_ens(ENS))],
    "BTC MA-ensemble weekly": [(1, ["BTC"], S_btc_ens(ENS, True))],
    # 3 own-MA BTC+ETH
    "Own MA50 ±2% BTC+ETH": own_ma(50, 0.02),
    "Own MA30 ±5% BTC+ETH": own_ma(30, 0.05),
    "Own MA75 ±0% BTC+ETH": own_ma(75, 0.0),
    "B&H-gate: BTC+ETH while BTC>MA200±2%": [(0.5, ["BTC"], S_btc_ma(200, 0.02)),
                                              (0.5, ["ETH"], lambda D, s, e: (lambda sig: (lambda i, w, eq: banded(
                                                  np.array([0.0 if np.isnan(sig[i]) else sig[i]]), w, 0.2)))(
                                                  D.ma_switch("BTC", 200, 0.02)))],
    # 4 Lab B
    "Lab B narrow + gate": [(1, ALL6, S_labb(ALL6, NARROW, gate=True))],
    "Lab B narrow, no gate": [(1, ALL6, S_labb(ALL6, NARROW, gate=False))],
    "Lab B wide + gate": [(1, ALL6, S_labb(ALL6, WIDE, gate=True))],
    "Lab B wide, no gate": [(1, ALL6, S_labb(ALL6, WIDE, gate=False))],
    "Lab B wide, no gate, equal-wt": [(1, ALL6, S_labb(ALL6, WIDE, gate=False, invvol=False))],
    "Lab B wide, no gate, no band": [(1, ALL6, S_labb(ALL6, WIDE, gate=False, band=0.0))],
    "Lab B wide, no gate, no ratchet": [(1, ALL6, S_labb(ALL6, WIDE, gate=False, ratchet=False))],
    "Lab B wide, no gate, BTC+ETH only": [(1, BE, S_labb(BE, WIDE, gate=False))],
    "Lab B narrow + gate, equal-wt": [(1, ALL6, S_labb(ALL6, NARROW, gate=True, invvol=False))],
    "Lab B narrow + gate, equal-wt, weekly": [(1, ALL6, S_weekly(S_labb(ALL6, NARROW, gate=True, invvol=False)))],
    "Lab B narrow + gate, equal-wt, 50% band": [(1, ALL6, S_labb(ALL6, NARROW, gate=True, invvol=False, band=0.5))],
    "Lab B narrow + gate, BTC+ETH only": [(1, BE, S_labb(BE, NARROW, gate=True, invvol=False, cap=0.5))],
    "Gate-only basket: EW 6 while BTC>MA200±2%": [(1, ALL6, S_gated_basket(ALL6))],
    # 5 vol scaling
    "BTC vol-target 40%": [(1, ["BTC"], S_volscaled(0.40))],
    "BTC MA200±2% x vol-target": [(1, ["BTC"], S_volscaled(0.40, base=("ma", (200, 0.02))))],
    "BTC MA-ensemble x vol-target": [(1, ["BTC"], S_volscaled(0.40, base=("ens", (ENS,))))],
    # 6 rebalanced mix
    "BTC/cash 50/50, 15pt band": [(1, ["BTC"], S_fixed_mix(0.5, 0.15))],
    # 7 core-satellite
    "Core-sat: 50% B&H BTC + 50% BTC MA-ensemble": [(0.5, ["BTC"], S_hold([1])), (0.5, ["BTC"], S_btc_ens(ENS))],
    "Core-sat: 50% B&H BTC + 50% Lab B wide no gate": [(0.5, ["BTC"], S_hold([1])),
                                                       (0.5, ALL6, S_labb(ALL6, WIDE, gate=False))],
}
BENCH = "B&H BTC"


def run_strategy(D, sleeves, start, end, fee, rate):
    parts, eps = [], []
    for share, coins, fac in sleeves:
        df, ep = simulate(D, fac(D, start, end), start, end, fee, rate, coins, cap=CAP * share)
        parts.append(df)
        eps += ep
    tot = parts[0].copy()
    for p in parts[1:]:
        tot += p
    return tot, eps


def metrics(df, eps=None):
    eq = df["eq"]
    days = (eq.index[-1] - eq.index[0]).days + 1
    yrs = days / 365.25
    cagr = (eq.iloc[-1] / CAP) ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1).min()
    ye = eq.groupby(eq.index.year).last()
    prev = pd.concat([pd.Series([CAP]), ye.iloc[:-1]]).values
    yr = ye.values / prev - 1
    m = {"end_value": eq.iloc[-1], "total_ret": eq.iloc[-1] / CAP - 1, "cagr": cagr, "max_dd": dd,
         "years": dict(zip(ye.index.astype(int).tolist(), yr.tolist())),
         "worst_year": yr.min(), "up_years": f"{int((yr > 0).sum())}/{len(yr)}",
         "orders_py": df["orders"].sum() / yrs, "fees_py": df["fee"].sum() / yrs,
         "costs_py": (df["fee"].sum() + df["slip"].sum()) / yrs,
         "disp_py": df["disp"].sum() / yrs, "proc_py": df["proc"].sum() / yrs,
         "avg_eq": eq.mean()}
    m["turnover_x"] = m["proc_py"] / m["avg_eq"]
    m["fee_pct_eq"] = m["fees_py"] / m["avg_eq"]
    m["acct_for_50k"] = 50000 / m["turnover_x"] if m["turnover_x"] > 0 else float("inf")
    if eps is not None:
        e = np.array(eps)
        m["round_trips"] = len(e)
        if len(e):
            m["rt_mean"] = e.mean(); m["rt_win"] = (e > 0).mean()
            m["rt_ci95"] = 1.96 * e.std(ddof=1) / np.sqrt(len(e)) if len(e) > 1 else np.nan
    return m


def key(name, fee, rate, start=START, end=END):
    VARIANTS.add(name)
    return f"{name}|{fee}|{rate}|{start}|{end}"


# ============================================================== tests
def main_table(D):
    res = {}
    for name, sl in STRATS.items():
        for fee, rate in product((TAKER, MAKER), (0.0, CASH_RATE)):
            df, eps = run_strategy(D, sl, START, END, fee, rate)
            key(name, fee, rate)
            res[(name, fee, rate)] = metrics(df, eps)
    return res


def rolling(D, names, rate=0.0, fee=TAKER):
    starts = pd.date_range("2019-01-01", "2024-10-01", freq="QS")
    out = {n: [] for n in names}
    bh = {}
    for s in starts:
        e = (s + pd.DateOffset(years=2) - pd.Timedelta(days=1))
        s_, e_ = s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")
        for n in names:
            df, _ = run_strategy(D, STRATS[n], s_, e_, fee, rate)
            r = df["eq"].iloc[-1] / CAP - 1
            ddv = (df["eq"] / df["eq"].cummax() - 1).min()
            out[n].append((s_, r, ddv))
    b = {s: r for s, r, _ in out[BENCH]}
    summ = {}
    for n in names:
        rs = np.array([r for _, r, _ in out[n]])
        dds = np.array([d for _, _, d in out[n]])
        beat = np.mean([r > b[s] for s, r, _ in out[n]])
        summ[n] = {"median": np.median(rs), "p10": np.percentile(rs, 10), "p90": np.percentile(rs, 90),
                   "pct_beat_bh": beat, "pct_positive": np.mean(rs > 0), "median_dd": np.median(dds),
                   "worst_dd": dds.min(), "n": len(rs)}
    return summ, out


def plateau_grid():
    g = {}
    for n, b in product((100, 150, 200, 250, 300), (0.0, 0.02, 0.04)):
        for wk in (False, True):
            g[f"BTC MA{n} ±{int(b*100)}% {'weekly' if wk else 'daily'}"] = ("BTC MA", [(1, ["BTC"], S_btc_ma(n, b, wk))])
    for sc in (0.5, 0.75, 1.0, 1.25, 1.5):
        lens = tuple(int(round(x * sc)) for x in ENS)
        for wk in (False, True):
            g[f"BTC ens x{sc} {lens} {'weekly' if wk else 'daily'}"] = ("BTC ensemble", [(1, ["BTC"], S_btc_ens(lens, wk))])
    for n, b in product((25, 30, 40, 50, 63, 75, 100), (0.0, 0.02, 0.05)):
        g[f"Own MA{n} ±{int(b*100)}% BTC+ETH"] = ("Own-MA BTC+ETH", own_ma(n, b))
    for sc in (0.5, 0.75, 1.0, 1.25, 1.5):
        for lname, base in (("narrow", NARROW), ("wide", WIDE)):
            lens = tuple(max(5, int(round(x * sc))) for x in base)
            for gate in (False, True):
                g[f"Lab B {lname} x{sc} {'gate' if gate else 'nogate'}"] = (
                    "Lab B", [(1, ALL6, S_labb(ALL6, lens, gate=gate))])
    for tv in (0.3, 0.4, 0.5, 0.6):
        for n in (20, 30, 60):
            g[f"BTC vol-target {int(tv*100)}% rv{n}"] = ("Vol-target", [(1, ["BTC"], S_volscaled(tv, n))])
            g[f"BTC ens x vol-target {int(tv*100)}% rv{n}"] = ("Ens x vol", [(1, ["BTC"], S_volscaled(tv, n, base=("ens", (ENS,))))])
    for wt, bd in product((0.3, 0.5, 0.7), (0.10, 0.15, 0.20)):
        g[f"BTC/cash {int(wt*100)}/{100-int(wt*100)} band {int(bd*100)}"] = ("Fixed mix", [(1, ["BTC"], S_fixed_mix(wt, bd))])
    return g


def run_grid(D, grid, start, end, fee=TAKER, rate=0.0):
    out = {}
    for name, (fam, sl) in grid.items():
        key(name, fee, rate, start, end)
        df, _ = run_strategy(D, sl, start, end, fee, rate)
        m = metrics(df)
        out[name] = {"family": fam, "cagr": m["cagr"], "max_dd": m["max_dd"], "total": m["total_ret"],
                     "worst_year": m["worst_year"], "orders_py": m["orders_py"],
                     "mar": m["cagr"] / abs(m["max_dd"]) if m["max_dd"] < 0 else np.nan}
    return out


def walk_forward(D, grid):
    tr = run_grid(D, grid, "2019-01-01", "2022-12-31")
    te = run_grid(D, grid, "2023-01-01", END)
    df = pd.DataFrame({n: {"family": tr[n]["family"], "train_cagr": tr[n]["cagr"], "train_dd": tr[n]["max_dd"],
                           "train_mar": tr[n]["mar"], "test_cagr": te[n]["cagr"], "test_dd": te[n]["max_dd"],
                           "test_mar": te[n]["mar"]} for n in grid}).T
    for c in df.columns[1:]:
        df[c] = df[c].astype(float)
    picks = {}
    for fam, sub in df.groupby("family"):
        best = sub["train_mar"].idxmax()
        picks[fam] = {"pick": best, **sub.loc[best].drop("family").to_dict(),
                      "test_rank": int((sub["test_mar"] > sub.loc[best, "test_mar"]).sum()) + 1, "n": len(sub),
                      "family_test_cagr_median": sub["test_cagr"].median(),
                      "family_test_dd_median": sub["test_dd"].median()}
    glob = df["train_mar"].idxmax()
    bh = {}
    for s, e in (("2019-01-01", "2022-12-31"), ("2023-01-01", END)):
        d, _ = run_strategy(D, STRATS[BENCH], s, e, TAKER, 0.0)
        bh[s] = metrics(d)
    return df, picks, glob, bh


def fee_sweep(D, names):
    out = {}
    for n in names:
        for f in (0.0025, 0.004, 0.006, 0.008, 0.012):
            df, _ = run_strategy(D, STRATS[n], START, END, f, 0.0)
            key(n, f, 0.0)
            out[(n, f)] = metrics(df)["cagr"]
    return out


def bear_attribution(D, name, bench="B&H BTC+ETH 50/50"):
    """Split strategy-minus-benchmark daily log returns by BTC regime at the previous close."""
    a, _ = run_strategy(D, STRATS[name], START, END, TAKER, 0.0)
    b, _ = run_strategy(D, STRATS[bench], START, END, TAKER, 0.0)
    ex = np.log(a["eq"]).diff() - np.log(b["eq"]).diff()
    m = pd.Series(D.sma("BTC", 200), index=D.idx).shift(1)
    c = D.C["BTC"].shift(1)
    reg = (c > m).reindex(ex.index)
    return {"excess_bull_log": float(ex[reg].sum()), "excess_bear_log": float(ex[~reg].sum()),
            "bull_days": int(reg.sum()), "bear_days": int((~reg).sum())}


def lookahead_check(names, cutoff="2023-06-30"):
    full, cut = Data(), Data(cutoff=cutoff)
    bad = []
    for n in names:
        a, _ = run_strategy(full, STRATS[n], START, cutoff, TAKER, 0.0)
        b, _ = run_strategy(cut, STRATS[n], START, cutoff, TAKER, 0.0)
        if not np.allclose(a["eq"].values, b["eq"].values, rtol=1e-12, atol=1e-9):
            bad.append(n)
    return bad


# ============================================================== recommended candidate: deep checks
def S_leg(coin, n, gate=True, gate_n=200, gate_buf=0.02):
    """One breakout leg on one coin, sized once (it is its own sleeve); off when the BTC gate is off."""
    def fac(D, start, end):
        sig, g = D.donchian(coin, n), D.ma_switch("BTC", gate_n, gate_buf)
        def decide(i, w, eq):
            t = sig[i] * (1.0 if (g[i] == 1 or not gate) else 0.0)
            return banded(np.array([t]), w, 0.5)
        return decide
    return fac


def legs(coins, lens=NARROW, gate=True, gate_n=200, gate_buf=0.02):
    k = len(coins) * len(lens)
    return [(1 / k, [c], S_leg(c, n, gate, gate_n, gate_buf)) for c in coins for n in lens]


def lb(coins, lens=NARROW, gn=200, gb=0.02, band=0.25, gate=True):
    return [(1, coins, S_labb(coins, lens, gate=gate, invvol=False, cap=1 / len(coins), band=band, gate_n=gn, gate_buf=gb))]


def candidate_checks(D, P):
    def go(sl, s=START, e=END, fee=TAKER, rate=0.0, name=None):
        if name:
            key(name, fee, rate, s, e)
        df, ep = run_strategy(D, sl, s, e, fee, rate)
        return metrics(df, ep)
    P("\n## Candidate deep-dive: Lab B on BTC+ETH only, breakout legs {20,50,100}, BTC MA200 ±2% gate (taker, 0% cash)\n")
    P("Train = 2019-2022, test = 2023-01-01 -> 2026-11-23. Fee % and turnover are per year, relative to average equity "
      "(so they read directly as £ per £1,000 held). 'Legs as sleeves' = recommended form: 6 fixed slots "
      "(2 coins x 3 lookbacks), each bought once at entry and sold once at exit, never resized.\n")
    P("| Variant | Full CAGR | Full max DD | Worst yr | Train CAGR / DD | Test CAGR / DD | Orders/yr | Fees % equity/yr | Proceeds x equity/yr | Disposals/yr | Round trips: n, mean ± 95% CI |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    rows = [("Legs as sleeves (RECOMMENDED FORM)", legs(BE)),
            ("Legs as sleeves, lookbacks x0.75", legs(BE, (15, 38, 75))),
            ("Legs as sleeves, lookbacks x1.25", legs(BE, (25, 62, 125))),
            ("Legs as sleeves, no gate", legs(BE, gate=False)),
            ("Legs as sleeves, gate MA150", legs(BE, gate_n=150)),
            ("Legs as sleeves, gate MA250", legs(BE, gate_n=250)),
            ("Legs as sleeves, gate ±0%", legs(BE, gate_buf=0.0)),
            ("Portfolio form, 25% band", lb(BE)),
            ("Portfolio form, 50% band", lb(BE, band=0.5)),
            ("Portfolio form, lookbacks x0.5", lb(BE, (10, 25, 50))),
            ("Portfolio form, lookbacks x1.5", lb(BE, (30, 75, 150))),
            ("Portfolio form, wide lookbacks", lb(BE, WIDE)),
            ("Portfolio form, no gate", lb(BE, gate=False)),
            ("BTC only (3 legs)", legs(["BTC"])),
            ("ETH only (3 legs)", legs(["ETH"])),
            ("B&H BTC", STRATS["B&H BTC"]), ("B&H BTC+ETH 50/50", STRATS["B&H BTC+ETH 50/50"]),
            ("BTC MA200 ±2% daily", STRATS["BTC MA200 ±2% daily"])]
    for name, sl in rows:
        f = go(sl, name="cand " + name)
        tr = go(sl, "2019-01-01", "2022-12-31")
        te = go(sl, "2023-01-01", END)
        rt = f"{f.get('round_trips', 0)}, {f.get('rt_mean', 0)*100:+.1f}% ± {f.get('rt_ci95', 0)*100:.1f}" if f.get("round_trips", 0) > 1 else "-"
        P(f"| {name} | {pct(f['cagr'])} | {pct(f['max_dd'],0)} | {pct(f['worst_year'],0)} | {pct(tr['cagr'])} / {pct(tr['max_dd'],0)} | "
          f"{pct(te['cagr'])} / {pct(te['max_dd'],0)} | {f['orders_py']:.1f} | {f['fee_pct_eq']*100:.1f}% | {f['turnover_x']:.1f} | {f['disp_py']:.1f} | {rt} |")
    P("\nRecommended form, per year, by fee and cash rate:\n")
    P("| Fee / cash | CAGR | " + " | ".join(str(y) for y in range(2019, 2027)) + " |")
    P("|---|---|" + "---|" * 8)
    for fee in (TAKER, MAKER):
        for r in (0.0, CASH_RATE):
            m = go(legs(BE), fee=fee, rate=r)
            P(f"| {fee*100:.2f}% / {int(r*100)}% | {pct(m['cagr'])} | " + " | ".join(f"{m['years'][y]*100:+.0f}%" for y in range(2019, 2027)) + " |")
    # rolling windows for the judging horizon
    for months in (12, 24):
        rows = []
        for s in pd.date_range("2019-01-01", (pd.Timestamp(END) - pd.DateOffset(months=months)).strftime("%Y-%m-01"), freq="MS"):
            e = (s + pd.DateOffset(months=months) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            s_ = s.strftime("%Y-%m-%d")
            out = []
            for sl, rate in ((legs(BE), CASH_RATE), (STRATS["B&H BTC"], 0.0), (STRATS["BTC MA200 ±2% daily"], CASH_RATE)):
                d, _ = run_strategy(D, sl, s_, e, TAKER, rate)
                r = d["eq"].iloc[-1] / CAP - 1
                dd = (d["eq"] / d["eq"].cummax() - 1).min()
                out += [r, dd, r / abs(dd) if dd < 0 else np.inf]
            rows.append(out)
        a = np.array(rows)
        P(f"\nRolling {months}-month windows, monthly starts (n={len(a)}), taker, 4% on idle cash for the trend rules:\n")
        P("| | Median return | 10th pct | 90th pct | Median max DD | Worst max DD | Share of windows with DD worse than -25% / -30% |")
        P("|---|---|---|---|---|---|---|")
        for k, nm in ((0, "Lab B BTC+ETH (legs)"), (3, "B&H BTC"), (6, "BTC MA200 ±2%")):
            P(f"| {nm} | {pct(np.median(a[:, k]),0)} | {pct(np.percentile(a[:, k], 10),0)} | {pct(np.percentile(a[:, k], 90),0)} | "
              f"{pct(np.median(a[:, k+1]),0)} | {pct(a[:, k+1].min(),0)} | {np.mean(a[:, k+1] < -0.25)*100:.0f}% / {np.mean(a[:, k+1] < -0.30)*100:.0f}% |")
        P(f"\nLab B beats B&H BTC on return in {np.mean(a[:,0] > a[:,3])*100:.0f}% of windows; on return/max-DD in "
          f"{np.mean(a[:,2] > a[:,5])*100:.0f}%; beats BTC MA200 on return in {np.mean(a[:,0] > a[:,6])*100:.0f}%. "
          f"Lab B lost more than 15% in {np.mean(a[:,0] < -0.15)*100:.0f}% of windows (B&H: {np.mean(a[:,3] < -0.15)*100:.0f}%).")
    P("\nRecommended form, fee sweep (full window, 0% cash): " + ", ".join(
        f"{f*100:.2f}% -> {pct(go(legs(BE), fee=f)['cagr'])}" for f in (0.0025, 0.004, 0.006, 0.008, 0.012)))
    df, ep = run_strategy(D, legs(BE), START, END, TAKER, 0.0)
    st = mx = 0
    for x in ep:
        st = st + 1 if x <= 0 else 0
        mx = max(mx, st)
    P(f"\nLongest run of losing round trips: {mx} (of {len(ep)}); win rate {np.mean(np.array(ep) > 0)*100:.0f}%.")


# ============================================================== output
def pct(x, d=1):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x*100:+.{d}f}%"


def main():
    D = Data()
    lines = []
    P = lines.append
    syn = D.synthetic.loc[START:END].sum()
    P(f"Synthetic (USD x implied FX) days in window: {syn.to_dict()}")

    bad = lookahead_check(list(STRATS))
    P(f"Lookahead check (truncate data after 2023-06-30, re-run, compare): "
      f"{'PASS for all ' + str(len(STRATS)) + ' strategies' if not bad else 'FAIL: ' + str(bad)}")

    res = main_table(D)
    yrs = list(range(2019, 2027))
    P("\n## Full window 2019-01-01 -> 2026-11-23, taker 0.80% + slippage, £1,000 start\n")
    P("| Strategy | CAGR (0% cash) | CAGR (4% cash) | Max DD | Worst yr | Up yrs | Orders/yr | Fees £/yr (% of avg equity) | Disposals/yr | Proceeds £/yr | Acct size for £50k proceeds | CAGR maker 0.40% (0%/4% cash) |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n in STRATS:
        a, b = res[(n, TAKER, 0.0)], res[(n, TAKER, CASH_RATE)]
        mk0, mk4 = res[(n, MAKER, 0.0)], res[(n, MAKER, CASH_RATE)]
        acct = "never" if np.isinf(a["acct_for_50k"]) else f"£{a['acct_for_50k']:,.0f}"
        P(f"| {n} | {pct(a['cagr'])} | {pct(b['cagr'])} | {pct(a['max_dd'],0)} | {pct(a['worst_year'],0)} | "
          f"{a['up_years']} | {a['orders_py']:.1f} | {a['fees_py']:.0f} ({a['fee_pct_eq']*100:.1f}%) | {a['disp_py']:.1f} | {a['proc_py']:,.0f} | "
          f"{acct} | {pct(mk0['cagr'])} / {pct(mk4['cagr'])} |")
    P("\n## Calendar-year returns (taker 0.80%, 0% on cash; 2026 = to 23 Nov)\n")
    P("| Strategy | " + " | ".join(str(y) for y in yrs) + " |")
    P("|---|" + "---|" * len(yrs))
    for n in STRATS:
        a = res[(n, TAKER, 0.0)]["years"]
        P(f"| {n} | " + " | ".join(f"{a[y]*100:+.0f}%" for y in yrs) + " |")
    P("\n## Round-trip stats (taker, 0% cash): one round trip = position opened from zero and closed to zero\n")
    P("| Strategy | Round trips | Mean net per trip | 95% CI ± | Win rate |")
    P("|---|---|---|---|---|")
    for n in STRATS:
        a = res[(n, TAKER, 0.0)]
        if a.get("round_trips", 0) >= 2:
            P(f"| {n} | {a['round_trips']} | {pct(a['rt_mean'])} | {a['rt_ci95']*100:.1f}pt | {a['rt_win']*100:.0f}% |")

    roll_names = list(STRATS)
    for rate in (0.0, CASH_RATE):
        rs, _ = rolling(D, roll_names, rate=rate)
        for n in roll_names:
            VARIANTS.add(n)
        P(f"\n## Rolling 2-year runs, new start every quarter 2019Q1-2024Q4 (24 starts), taker, {int(rate*100)}% on cash\n")
        P("| Strategy | Median 2y return | 10th pct | 90th pct | % starts > 0 | % starts beating B&H BTC | Median max DD | Worst max DD |")
        P("|---|---|---|---|---|---|---|---|")
        for n in roll_names:
            s = rs[n]
            P(f"| {n} | {pct(s['median'],0)} | {pct(s['p10'],0)} | {pct(s['p90'],0)} | {s['pct_positive']*100:.0f}% | "
              f"{s['pct_beat_bh']*100:.0f}% | {pct(s['median_dd'],0)} | {pct(s['worst_dd'],0)} |")
        if rate == 0.0:
            roll0 = rs

    grid = plateau_grid()
    full = run_grid(D, grid, START, END)
    P("\n## Parameter plateau (full window, taker, 0% cash): spread across each family's grid\n")
    P("| Family | Variants | CAGR min | CAGR median | CAGR max | Max DD median | Max DD worst | Orders/yr median |")
    P("|---|---|---|---|---|---|---|---|")
    fdf = pd.DataFrame(full).T
    for fam, sub in fdf.groupby("family"):
        P(f"| {fam} | {len(sub)} | {pct(sub.cagr.min())} | {pct(sub.cagr.median())} | {pct(sub.cagr.max())} | "
          f"{pct(sub.max_dd.median(),0)} | {pct(sub.max_dd.min(),0)} | {sub.orders_py.median():.1f} |")
    P("\nDetail for the main families:\n")
    P("| Variant | CAGR | Max DD | Worst yr | Orders/yr |")
    P("|---|---|---|---|---|")
    for n, r in full.items():
        if r["family"] in ("BTC ensemble", "Lab B", "Own-MA BTC+ETH") or n.startswith("BTC MA") and "±2%" in n:
            P(f"| {n} | {pct(r['cagr'])} | {pct(r['max_dd'],0)} | {pct(r['worst_year'],0)} | {r['orders_py']:.1f} |")

    wf, picks, glob, bh = walk_forward(D, grid)
    P("\n## Walk-forward: pick best CAGR/MaxDD on 2019-2022 within each family, then test once on 2023-01-01 -> 2026-11-23 (taker, 0% cash)\n")
    P(f"B&H BTC: train CAGR {pct(bh['2019-01-01']['cagr'])} / DD {pct(bh['2019-01-01']['max_dd'],0)}; "
      f"test CAGR {pct(bh['2023-01-01']['cagr'])} / DD {pct(bh['2023-01-01']['max_dd'],0)}\n")
    P("| Family | Pick (chosen on 2019-22) | Train CAGR / DD | Test CAGR / DD | Test rank in family (by MAR) | Family median test CAGR / DD |")
    P("|---|---|---|---|---|---|")
    for fam, p in picks.items():
        P(f"| {fam} | {p['pick']} | {pct(p['train_cagr'])} / {pct(p['train_dd'],0)} | {pct(p['test_cagr'])} / "
          f"{pct(p['test_dd'],0)} | {p['test_rank']} of {p['n']} | {pct(p['family_test_cagr_median'])} / {pct(p['family_test_dd_median'],0)} |")
    P(f"\nGlobal pick across all {len(wf)} grid variants (best 2019-22 MAR): **{glob}** -> test CAGR "
      f"{pct(wf.loc[glob,'test_cagr'])}, DD {pct(wf.loc[glob,'test_dd'],0)}")
    corr = wf[["train_mar", "test_mar"]].corr(method="spearman").iloc[0, 1]
    P(f"Rank correlation of train MAR vs test MAR across all grid variants: {corr:.2f}")

    sweep_names = ["Lab B narrow + gate, equal-wt", "Gate-only basket: EW 6 while BTC>MA200±2%", "BTC MA200 ±2% daily", "BTC MA-ensemble daily", "BTC MA-ensemble weekly", "Own MA50 ±2% BTC+ETH",
                   "Lab B narrow + gate", "Lab B wide, no gate", "BTC vol-target 40%", "BTC/cash 50/50, 15pt band"]
    fs = fee_sweep(D, sweep_names)
    P("\n## Fee sweep: full-window CAGR by fee per side (slippage on top, 0% cash)\n")
    P("| Strategy | 0.25% | 0.40% | 0.60% | 0.80% | 1.20% |")
    P("|---|---|---|---|---|---|")
    for n in sweep_names:
        P(f"| {n} | " + " | ".join(pct(fs[(n, f)]) for f in (0.0025, 0.004, 0.006, 0.008, 0.012)) + " |")

    P("\n## Is own-MA just bear-market avoidance? Excess log return vs B&H BTC+ETH, split by BTC regime\n")
    P("| Strategy | Excess when BTC > MA200 | Excess when BTC < MA200 | Bull days | Bear days |")
    P("|---|---|---|---|---|")
    for n in ["Own MA50 ±2% BTC+ETH", "Own MA30 ±5% BTC+ETH", "B&H-gate: BTC+ETH while BTC>MA200±2%",
              "Lab B wide, no gate, BTC+ETH only"]:
        a = bear_attribution(D, n)
        P(f"| {n} | {a['excess_bull_log']:+.2f} | {a['excess_bear_log']:+.2f} | {a['bull_days']} | {a['bear_days']} |")

    P("\n## Survivorship check: Lab B narrow + gate (equal-wt) with one coin removed (full window, taker, 0% cash)\n")
    P("| Coins | CAGR | Max DD | Worst yr |")
    P("|---|---|---|---|")
    for drop in [None] + ALL6:
        cs = [c for c in ALL6 if c != drop]
        nm = f"Lab B narrow+gate EW without {drop}" if drop else "Lab B narrow+gate EW, all 6"
        key(nm, TAKER, 0.0)
        df, _ = run_strategy(D, [(1, cs, S_labb(cs, NARROW, gate=True, invvol=False))], START, END, TAKER, 0.0)
        m = metrics(df)
        P(f"| {'-' + drop if drop else 'all 6'} | {pct(m['cagr'])} | {pct(m['max_dd'],0)} | {pct(m['worst_year'],0)} |")
    df, _ = run_strategy(D, [(1, ["BTC", "ETH", "XRP", "LINK"], S_labb(["BTC", "ETH", "XRP", "LINK"], NARROW, gate=True, invvol=False))], START, END, TAKER, 0.0)
    key("Lab B narrow+gate EW pre-2021 coins", TAKER, 0.0)
    m = metrics(df)
    P(f"| BTC/ETH/XRP/LINK only (no SOL/ADA) | {pct(m['cagr'])} | {pct(m['max_dd'],0)} | {pct(m['worst_year'],0)} |")

    candidate_checks(D, P)

    P(f"\n**Distinct strategy configurations evaluated in this script: {len(VARIANTS)}** "
      f"(each also run at several fee / cash-rate / window settings).")

    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(OUT, "assess_tables.md"), "w") as f:
        f.write(txt + "\n")
    dump = {"main": {f"{k[0]}|fee{k[1]}|cash{k[2]}": v for k, v in res.items()},
            "rolling_0pct": roll0, "plateau": full, "walk_forward_picks": picks, "walk_forward_global": glob,
            "variants": len(VARIANTS)}
    with open(os.path.join(OUT, "assess_results.json"), "w") as f:
        json.dump(dump, f, indent=1, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))


if __name__ == "__main__":
    main()
