#!/usr/bin/env python3
"""
Round-3 independent assessment for the Bunny paper-trading lab.

Run from the repo root:  python3 research/2026-11-24-round3/assess3.py
Writes: research/2026-11-24-round3/assess3_results.json and trial_ledger.csv

All parameters below were written down BEFORE looking at any result
(they are the ones in the round-3 brief / digest).  Every variant that is
run is appended to the TRIAL LEDGER.  Nothing here is investment advice.

Conventions
- Daily bars are Coinbase GBP candles, 00:00 UTC.  A signal is computed on a
  bar's close and executed at the NEXT bar's open (or by a limit order that
  only becomes active on the next bar).
- Costs per fill: fee (maker 0.40% base where a post-only limit is realistic;
  taker 0.80% stress) + slippage (0.05% BTC/ETH, 0.10% others).
- Maker fills: a post-only limit at the next open only fills if the bar trades
  THROUGH it by eps=0.10% (buy: low <= px*(1-eps); sell: high >= px*(1+eps)).
  If it doesn't fill, it is re-posted at the following open (no chasing).
- Idle GBP earns 4.0%/yr (reported as a separate line).  Hurdle = 4.5%/yr.
"""
import json, math, os, sys
import numpy as np, pandas as pd
from scipy import stats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D = os.path.join(ROOT, 'research', 'data', 'daily')
H = os.path.join(ROOT, 'backtest_results', 'data')
OUT = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20261124)

CASH_RATE = 0.04
HURDLE = 0.045
PRIOR_TRIALS = 195
SLIP = {'BTC': 0.0005, 'ETH': 0.0005, 'LINK': 0.001, 'ADA': 0.001, 'SOL': 0.001, 'XRP': 0.001}
MAKER, TAKER, EPS = 0.004, 0.008, 0.001

LEDGER = []
SERIES = {}      # name -> daily equity series (for DSR / rolling)


def log_trial(cand, variant, period, fee, m, note=''):
    row = dict(id=len(LEDGER) + 1, candidate=cand, variant=variant, period=period, fee=fee, note=note)
    for k in ('cagr', 'maxdd', 'sharpe', 'trades', 'n', 'mean', 'total'):
        if k in m:
            row[k] = m[k]
    LEDGER.append(row)
    return row


# ----------------------------------------------------------------- data
def load(path):
    d = pd.read_csv(path, parse_dates=['t']).set_index('t')
    d.index = d.index.tz_convert(None) if d.index.tz is not None else d.index
    return d[['open', 'high', 'low', 'close']].astype(float)


def daily_gbp():
    """GBP daily OHLC.  Where only USD exists (ETH 2017-01..2018-09, XRP), build a
    synthetic GBP price using GBPUSD implied by BTC_USD/BTC_GBP closes (flagged)."""
    out = {}
    bu = load(f'{D}/BTC_USD_1d.csv'); bg = load(f'{D}/BTC_GBP_1d.csv')
    fx = (bu.close / bg.close).rename('gbpusd')          # USD per GBP
    fx_o = (bu.open / bg.open)
    for c in ['BTC', 'ETH', 'LINK', 'ADA', 'SOL']:
        out[c] = load(f'{D}/{c}_GBP_1d.csv')
    eu = load(f'{D}/ETH_USD_1d.csv')
    syn = pd.DataFrame({'open': eu.open / fx_o, 'high': eu.high / fx, 'low': eu.low / fx, 'close': eu.close / fx}).dropna()
    out['ETH_SYN'] = pd.concat([syn[syn.index < out['ETH'].index[0]], out['ETH']])
    return out, fx


def panel(dfs, names, start=None, end=None):
    idx = dfs[names[0]].index
    for n in names[1:]:
        idx = idx.union(dfs[n].index)
    if start: idx = idx[idx >= pd.Timestamp(start)]
    if end: idx = idx[idx <= pd.Timestamp(end)]
    P = {f: np.column_stack([dfs[n][f].reindex(idx).values for n in names]) for f in ['open', 'high', 'low', 'close']}
    return idx, P


# ----------------------------------------------------------------- metrics
def metrics(eq, ppy=365):
    eq = eq.dropna()
    r = eq.pct_change().dropna()
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else np.nan
    rf = (1 + CASH_RATE) ** (1 / ppy) - 1
    ex = r - rf
    sh = ex.mean() / ex.std() * math.sqrt(ppy) if ex.std() > 0 else np.nan
    dd = (eq / eq.cummax() - 1).min()
    return dict(cagr=round(100 * cagr, 2), vol=round(100 * r.std() * math.sqrt(ppy), 1), sharpe=round(sh, 3),
                maxdd=round(100 * dd, 1), total=round(100 * (eq.iloc[-1] / eq.iloc[0] - 1), 1),
                start=str(eq.index[0].date()), end=str(eq.index[-1].date()))


def yearly(eq):
    eq = eq.dropna()
    out = {}
    for y in sorted(set(eq.index.year)):
        e = eq[eq.index.year == y]
        prev = eq[eq.index.year < y]
        base = prev.iloc[-1] if len(prev) else e.iloc[0]
        out[str(y)] = round(100 * (e.iloc[-1] / base - 1), 1)
    return out


def rolling_beat(eq, years, hurdle=HURDLE):
    eq = eq.dropna()
    d = int(round(365 * years))
    if len(eq) <= d + 30:
        return None
    v = eq.values
    rr = v[d:] / v[:-d]
    need = (1 + hurdle) ** years
    return dict(windows=len(rr), p_beat=round(float((rr > need).mean()), 3),
                median=round(100 * (np.median(rr) - 1), 1), p10=round(100 * (np.percentile(rr, 10) - 1), 1),
                p90=round(100 * (np.percentile(rr, 90) - 1), 1), p_loss=round(float((rr < 1).mean()), 3),
                independent_windows=round(len(v) / d, 1))


def dsr(eq, n_trials, sr_var_daily, ppy=365):
    """Deflated Sharpe ratio (Bailey & Lopez de Prado 2014) on daily excess returns."""
    r = eq.pct_change().dropna() - ((1 + CASH_RATE) ** (1 / ppy) - 1)
    T = len(r)
    sr = r.mean() / r.std()
    g3 = stats.skew(r); g4 = stats.kurtosis(r, fisher=False)
    emc = 0.5772156649
    sr0 = math.sqrt(sr_var_daily) * ((1 - emc) * stats.norm.ppf(1 - 1 / n_trials) + emc * stats.norm.ppf(1 - 1 / (n_trials * math.e)))
    z = (sr - sr0) * math.sqrt(T - 1) / math.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    return dict(sr_ann=round(sr * math.sqrt(ppy), 3), sr0_ann=round(sr0 * math.sqrt(ppy), 3), dsr=round(float(stats.norm.cdf(z)), 4),
                psr_vs0=round(float(stats.norm.cdf(sr * math.sqrt(T - 1) / math.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2)))), 4), T=T)


def uk_tax(trades, eq, scale_to=(1000, 5000)):
    """trades: list of dicts(date, asset, side, value).  Disposals = sells (incl. crypto->crypto)."""
    if not trades:
        return dict(disposals_per_yr=0)
    df = pd.DataFrame(trades)
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    sells = df[df.side == 'sell']
    buys = df[df.side == 'buy']
    # 30-day (bed & breakfast) rule: a sell followed by a re-buy of the same asset within 30 days
    bb = 0
    for _, s in sells.iterrows():
        b = buys[(buys.asset == s.asset) & (buys.date > s.date) & (buys.date <= s.date + pd.Timedelta(days=30))]
        bb += len(b) > 0
    start_cap = eq.iloc[0]
    proc_per_yr = sells.value.sum() / yrs
    by_year = sells.groupby(sells.date.dt.year).value.sum()
    turnover = proc_per_yr / float(eq.mean())          # annual sale proceeds as a multiple of average account value
    return dict(disposals_per_yr=round(len(sells) / yrs, 1), fills_per_yr=round(len(df) / yrs, 1),
                sale_proceeds_x_avg_equity_per_yr=round(turnover, 2),
                proceeds_per_yr_if_account_stays_1k=round(1000 * turnover), proceeds_per_yr_if_account_stays_5k=round(5000 * turnover),
                sells_rebought_within_30d_pct=round(100 * bb / max(1, len(sells)), 0),
                proceeds_per_yr_at_1k=round(proc_per_yr * 1000 / start_cap), proceeds_per_yr_at_5k=round(proc_per_yr * 5000 / start_cap),
                max_calendar_year_proceeds_at_5k=round(float(by_year.max()) * 5000 / start_cap) if len(by_year) else 0,
                start_cap_needed_to_hit_50k_proceeds=round(50000 * start_cap / max(1, float(by_year.max()))) if len(by_year) else None)


# ----------------------------------------------------------------- generic daily engine
def simulate(idx, P, names, policy, fee, maker=True, eps=EPS, cash0=1000.0, cash_rate=CASH_RATE, state=None):
    """policy(i, w_now, eq_close, state) -> dict{asset_j: target_weight} or None, called at close of bar i.
    Orders execute from bar i+1: taker at the open; maker = post-only limit at the open that fills only if
    the bar trades through by eps, else it is re-posted at the next open."""
    O, Hh, L, C = P['open'], P['high'], P['low'], P['close']
    n, k = C.shape
    slip = np.array([SLIP[x.split('_')[0]] for x in names])
    units = np.zeros(k); cash = cash0
    rd = (1 + cash_rate) ** (1 / 365) - 1
    eq = np.full(n, np.nan); W = np.zeros((n, k))
    pending = {}
    trades = []; fees = 0.0; interest = 0.0
    state = state if state is not None else {}
    for i in range(n):
        it = cash * rd if cash > 0 else 0.0
        cash += it; interest += it
        if pending:
            px_o = np.nan_to_num(O[i]); E_o = cash + np.nansum(units * px_o)
            # sells first, then buys
            for side in ('sell', 'buy'):
                for j, tw in list(pending.items()):
                    if np.isnan(O[i, j]):
                        continue
                    cur = units[j] * O[i, j]
                    delta = tw * E_o - cur
                    if abs(delta) < 1e-6 * E_o or abs(delta) < 0.5:
                        pending.pop(j); continue
                    if (delta < 0) != (side == 'sell'):
                        continue
                    if maker:
                        ok = (L[i, j] <= O[i, j] * (1 - eps)) if delta > 0 else (Hh[i, j] >= O[i, j] * (1 + eps))
                        if not ok:
                            continue
                    c = fee + slip[j]
                    if delta > 0:
                        delta = min(delta, max(0.0, cash / (1 + c)))
                        if delta < 0.5:
                            continue
                        units[j] += delta / O[i, j]; cash -= delta * (1 + c)
                        trades.append(dict(date=idx[i], asset=names[j].split('_')[0], side='buy', value=delta))
                        # still short of target because of missing cash? keep pending
                        if tw * E_o - units[j] * O[i, j] < 0.01 * E_o:
                            pending.pop(j)
                    else:
                        d = min(-delta, cur)
                        units[j] -= d / O[i, j]; cash += d * (1 - c)
                        trades.append(dict(date=idx[i], asset=names[j].split('_')[0], side='sell', value=d))
                        pending.pop(j)
                    fees += abs(delta if delta > 0 else d) * c
        px = np.nan_to_num(C[i])
        hold = units * px
        eq[i] = cash + hold.sum()
        W[i] = hold / eq[i]
        tg = policy(i, W[i], eq[i], state)
        if tg:
            for j, tw in tg.items():
                pending[j] = tw
    eqs = pd.Series(eq, index=idx)
    return dict(eq=eqs, W=pd.DataFrame(W, index=idx, columns=names), trades=trades, fees=round(fees, 2),
                interest=round(interest, 2), exposure=round(float(W.sum(1).mean()), 3))


def summarize(res, label):
    m = metrics(res['eq'])
    m.update(dict(fees=res['fees'], interest=res['interest'], avg_exposure=res['exposure'],
                  trades=len(res['trades']), trades_per_yr=round(len(res['trades']) / ((res['eq'].index[-1] - res['eq'].index[0]).days / 365.25), 1)))
    m['years'] = yearly(res['eq'])
    m['uk'] = uk_tax(res['trades'], res['eq'])
    return m


# ----------------------------------------------------------------- G: baselines
def savings_curve(idx, rate=HURDLE):
    t = np.array([(d - idx[0]).days for d in idx]) / 365.0
    return pd.Series(1000 * (1 + rate) ** t, index=idx)


def pol_const(w, band=None, min_gap=7, monthly=False, idx=None):
    def f(i, wn, e, s):
        last = s.get('last', -999)
        if i == 0 or 'init' not in s:
            s['init'] = 1; s['last'] = i
            return {j: w[j] for j in range(len(w))}
        if monthly:
            if i + 1 < len(idx) and idx[i + 1].month != idx[i].month:
                s['last'] = i
                return {j: w[j] for j in range(len(w))}
            return None
        if band is not None and abs(wn.sum() - sum(w)) > band and i - last >= min_gap:
            s['last'] = i
            return {j: w[j] for j in range(len(w))}
        return None
    return f


def dca_rolling(btc_close, fee=TAKER + SLIP['BTC']):
    """£1k drip-fed into BTC over 12 monthly instalments (cash at 4% meanwhile), then held.
    Returns 1y and 3y outcomes for every monthly start date."""
    c = btc_close
    month_starts = c.groupby([c.index.year, c.index.month]).head(1).index
    res1, res3 = [], []
    for si, s in enumerate(month_starts):
        dates = month_starts[si:si + 12]
        if len(dates) < 12:
            break
        for horizon, store in ((365, res1), (1095, res3)):
            end = s + pd.Timedelta(days=horizon)
            if end > c.index[-1]:
                continue
            cash = 1000.0; units = 0.0; last = s
            for d in dates:
                if d > end:
                    break
                cash *= (1 + CASH_RATE) ** ((d - last).days / 365); last = d
                amt = 1000 / 12
                cash -= amt; units += amt * (1 - fee) / c.loc[d]
            cash *= (1 + CASH_RATE) ** ((end - last).days / 365)
            pe = c[c.index <= end].iloc[-1]
            store.append(cash + units * pe)
    out = {}
    for name, store, yrs in (('1y', res1, 1), ('3y', res3, 3)):
        a = np.array(store) / 1000
        out[name] = dict(windows=len(a), p_beat=round(float((a > (1 + HURDLE) ** yrs).mean()), 3), median=round(100 * (np.median(a) - 1), 1),
                         p10=round(100 * (np.percentile(a, 10) - 1), 1), p90=round(100 * (np.percentile(a, 90) - 1), 1))
    return out


# ----------------------------------------------------------------- A: vol-scaled exposure
def ewma_vol(ret, lam=0.94):
    v = np.full(len(ret), np.nan)
    r = np.nan_to_num(ret)
    seed = np.nanvar(ret[1:31]) if len(ret) > 31 else np.nanvar(ret)
    var = seed
    for i in range(len(ret)):
        if not np.isnan(ret[i]):
            var = lam * var + (1 - lam) * r[i] ** 2
        v[i] = math.sqrt(var * 365)
    v[:30] = np.nan
    return v


def pol_volscale(sig_total, n_assets_avail, target=0.40, band=0.20, min_gap=7):
    """sig_total: annualised vol of the (basket) return, per bar.  Weight = min(1,target/sig) spread equally
    over assets available.  Trade only if |w_target - w_now| > band and >= min_gap days since last trade."""
    def f(i, wn, e, s):
        if np.isnan(sig_total[i]):
            return None
        wt = min(1.0, target / sig_total[i])
        avail = n_assets_avail[i]
        last = s.get('last', -999)
        if 'init' not in s or (abs(wt - wn.sum()) > band and i - last >= min_gap):
            s['init'] = 1; s['last'] = i
            out = {j: (wt / len(avail) if j in avail else 0.0) for j in range(len(wn))}
            return out
        return None
    return f


def run_A(dfs):
    res = {}
    configs = [('BTC', ['BTC'], '2017-01-01'), ('BASKET', ['BTC', 'ETH_SYN', 'LINK', 'ADA', 'SOL'], '2017-01-01')]
    for label, names, start in configs:
        idx, P = panel(dfs, names, start)
        C = P['close']
        lr = np.log(C[1:] / C[:-1]); lr = np.vstack([np.full(len(names), np.nan), lr])
        basket = np.nanmean(np.where(np.isnan(lr), np.nan, lr), axis=1) if len(names) > 1 else lr[:, 0]
        avail = [[j for j in range(len(names)) if not np.isnan(C[i, j]) and (i >= 30 and not np.isnan(C[i - 30, j]))] or [0] for i in range(len(idx))]

        def go(target=0.40, band=0.20, gap=7, lam=0.94, fee=MAKER, maker=True, tag='base'):
            sig = ewma_vol(basket, lam)
            r = simulate(idx, P, names, pol_volscale(sig, avail, target, band, gap), fee, maker)
            m = summarize(r, label)
            log_trial('A', f'{label} tgt={target} band={band} gap={gap} lam={lam} {tag}', f'{start}..', fee, m)
            return r, m

        r, m = go()
        SERIES[f'A_{label}'] = r['eq']
        avgw = r['exposure']
        # exposure-matched constant-weight benchmark, same band/gap logic (band 0.10)
        wconst = [avgw / len(names)] * len(names)
        # constant: equal weights over available assets -> use the same avail logic with constant sigma
        sig_c = np.full(len(idx), 0.40 / avgw); sig_c[:30] = np.nan
        rc = simulate(idx, P, names, pol_volscale(sig_c, avail, 0.40, 0.10, 7), MAKER, True)
        mc = summarize(rc, label + '_const')
        log_trial('A', f'{label} constant-weight benchmark w={avgw}', f'{start}..', MAKER, mc, 'benchmark')
        SERIES[f'A_{label}_const'] = rc['eq']
        # stress taker
        rt, mt = go(fee=TAKER, maker=False, tag='taker-stress')
        rct = simulate(idx, P, names, pol_volscale(sig_c, avail, 0.40, 0.10, 7), TAKER, False)
        mct = summarize(rct, 'c')
        # sensitivity +-25/50%
        sens = {}
        for nm, kw in [('target0.30', dict(target=0.30)), ('target0.50', dict(target=0.50)), ('target0.20', dict(target=0.20)), ('target0.60', dict(target=0.60)),
                       ('band0.15', dict(band=0.15)), ('band0.25', dict(band=0.25)), ('band0.10', dict(band=0.10)), ('band0.30', dict(band=0.30)),
                       ('gap5', dict(gap=5)), ('gap10', dict(gap=10)), ('lam0.90', dict(lam=0.90)), ('lam0.97', dict(lam=0.97))]:
            rs, ms = go(tag='sens', **kw)
            # its own exposure-matched constant benchmark
            sc = np.full(len(idx), 0.40 / rs['exposure']); sc[:30] = np.nan
            rcs = simulate(idx, P, names, pol_volscale(sc, avail, 0.40, 0.10, 7), MAKER, True)
            mcs = metrics(rcs['eq'])
            sens[nm] = dict(cagr=ms['cagr'], maxdd=ms['maxdd'], sharpe=ms['sharpe'], exposure=rs['exposure'],
                            const_cagr=mcs['cagr'], const_maxdd=mcs['maxdd'], const_sharpe=mcs['sharpe'],
                            excess_vs_const=round(ms['cagr'] - mcs['cagr'], 2))
        # split: 2017-21 vs 2022-26 (fixed params, so both are "out of sample" for us; report both)
        split = {}
        for a, b in (('2017-01-01', '2021-12-31'), ('2022-01-01', '2026-12-31')):
            e1 = r['eq'][a:b]; e2 = rc['eq'][a:b]
            split[f'{a[:4]}-{b[:4]}'] = dict(strategy=metrics(e1), constant=metrics(e2))
        # circular-shift null: does the TIMING of the weight path matter vs a random timing with same weights?
        null = circ_null(r['W'].sum(axis=1).values, basket, idx, cost=MAKER + 0.0005, nsim=500)
        res[label] = dict(base=m, constant_benchmark=mc, avg_weight=avgw, taker=dict(strategy=mt, constant=mct),
                          sensitivity=sens, split=split, timing_null=null)
    return res


def circ_null(w, lr_basket, idx, cost, nsim=500):
    """Approximate daily-return model: ret = w_{t-1}*(e^r-1) + (1-w_{t-1})*cash - |dw|*cost.
    Compare the actual weight path with circularly shifted copies (same exposure distribution and turnover)."""
    r = np.nan_to_num(np.exp(np.nan_to_num(lr_basket)) - 1)
    rd = (1 + CASH_RATE) ** (1 / 365) - 1
    def perf(ww):
        wl = np.concatenate([[0], ww[:-1]])
        ret = wl * r + (1 - wl) * rd - np.abs(np.diff(np.concatenate([[0], wl]))) * cost
        return np.log1p(ret).sum() / (len(ret) / 365)
    ok = ~np.isnan(w)
    w = np.nan_to_num(w)
    act = perf(w)
    sims = np.array([perf(np.roll(w, RNG.integers(60, len(w) - 60))) for _ in range(nsim)])
    return dict(actual_log_cagr=round(100 * act, 2), null_median=round(100 * np.median(sims), 2),
                pct_rank=round(float((sims < act).mean()), 3))


# ----------------------------------------------------------------- B: cross-sectional momentum
def pol_xsmom(C, idx, lookback=14, top=2, keep_rank=3, hold_state=None):
    def f(i, wn, e, s):
        # rank at Sunday's close (bar dated Sunday closes at Monday 00:00), trade at Monday open
        if idx[i].weekday() != 6 or i < lookback:
            return None
        avail = [j for j in range(C.shape[1]) if not np.isnan(C[i - lookback, j])]
        if len(avail) < top + 1:
            return None
        ret = {j: C[i, j] / C[i - lookback, j] - 1 for j in avail}
        ranked = sorted(avail, key=lambda j: -ret[j])
        rank = {j: r + 1 for r, j in enumerate(ranked)}
        held = s.get('held', [])
        if not held:
            new = ranked[:top]
            s['held'] = new
            s.setdefault('switches', 0)
            return {j: 1.0 / top for j in new}
        keep = [j for j in held if rank.get(j, 99) <= keep_rank]
        drop = [j for j in held if j not in keep]
        if not drop:
            return None
        cands = [j for j in ranked if j not in keep]
        new = cands[:len(drop)]
        s['held'] = keep + new
        s['switches'] = s.get('switches', 0) + len(drop)
        tg = {j: 0.0 for j in drop}
        for d_, n_ in zip(drop, new):
            tg[n_] = tg.get(n_, 0) + wn[d_]          # proceeds of the outgoing coin go to the incoming coin
        return tg
    return f


def pol_ew_weekly(C, idx):
    def f(i, wn, e, s):
        if idx[i].weekday() != 6:
            return None
        avail = [j for j in range(C.shape[1]) if not np.isnan(C[i, j])]
        return {j: (1.0 / len(avail) if j in avail else 0.0) for j in range(C.shape[1])}
    return f


def run_B(dfs):
    names = ['BTC', 'ETH', 'LINK', 'ADA', 'SOL']
    start = '2021-06-17'           # first day all 5 coins exist on Coinbase GBP
    idx, P = panel(dfs, names, start)
    C = P['close']
    out = {}
    for lb in (14, 7):
        for fee, mk, tag in ((MAKER, True, 'maker'), (TAKER, False, 'taker')):
            st = {}
            r = simulate(idx, P, names, pol_xsmom(C, idx, lb), fee, mk, state=st)
            m = summarize(r, 'B'); m['switches'] = st.get('switches')
            log_trial('B', f'lb={lb} top2 keep<=3 {tag}', f'{start}..', fee, m)
            out[f'lb{lb}_{tag}'] = m
            if lb == 14 and tag == 'maker':
                SERIES['B_mom14'] = r['eq']; base_r = r; base_st = st
            if lb == 7 and tag == 'maker':
                SERIES['B_mom7'] = r['eq']
    for fee, mk, tag in ((MAKER, True, 'maker'), (TAKER, False, 'taker')):
        rb = simulate(idx, P, names, pol_ew_weekly(C, idx), fee, mk)
        mb = summarize(rb, 'EW'); log_trial('B', f'EW weekly benchmark {tag}', f'{start}..', fee, mb, 'benchmark')
        out[f'benchmark_EW_weekly_{tag}'] = mb
        if tag == 'maker':
            SERIES['B_EW'] = rb['eq']
    # EW buy-and-hold (no rebalance) as a cheaper benchmark
    def pol_bh(i, wn, e, s):
        if 'init' in s: return None
        s['init'] = 1; return {j: 0.2 for j in range(5)}
    rbh = simulate(idx, P, names, pol_bh, MAKER, True)
    out['benchmark_EW_buyhold'] = summarize(rbh, 'EWbh')
    SERIES['B_EW_bh'] = rbh['eq']
    # sensitivity
    sens = {}
    for lb in (10, 21, 28):
        r = simulate(idx, P, names, pol_xsmom(C, idx, lb), MAKER, True)
        m = metrics(r['eq']); log_trial('B', f'lb={lb} sens', f'{start}..', MAKER, m)
        sens[f'lb{lb}'] = dict(cagr=m['cagr'], maxdd=m['maxdd'], sharpe=m['sharpe'])
    for kr in (2, 4):
        r = simulate(idx, P, names, pol_xsmom(C, idx, 14, 2, kr), MAKER, True)
        m = metrics(r['eq']); log_trial('B', f'lb=14 keep<={kr} sens', f'{start}..', MAKER, m)
        sens[f'keep_rank<={kr}'] = dict(cagr=m['cagr'], maxdd=m['maxdd'], sharpe=m['sharpe'])
    out['sensitivity'] = sens
    # random-switch null: same switch dates and counts, random replacement coin
    out['random_null'] = xsmom_null(idx, P, names, C, nsim=300)
    # split halves
    e = SERIES['B_mom14']; b = SERIES['B_EW']
    out['split'] = {p: dict(strategy=metrics(e[a:z]), ew=metrics(b[a:z])) for p, a, z in
                    (('2021H2-2023', '2021-06-17', '2023-12-31'), ('2024-2026', '2024-01-01', '2026-12-31'))}
    # weekly gross diagnostic: average next-week return of top-2 vs basket (no costs)
    out['gross_weekly_spread'] = xs_gross(idx, C)
    return out


def xs_gross(idx, C, lb=14):
    sp = []
    for i in range(lb, len(idx) - 8):
        if idx[i].weekday() != 6: continue
        ret = C[i] / C[i - lb] - 1
        fwd = C[i + 7] / C[i] - 1
        order = np.argsort(-ret)
        sp.append(fwd[order[:2]].mean() - fwd.mean())
    sp = np.array(sp)
    return dict(weeks=len(sp), mean_pct=round(100 * sp.mean(), 3), ci95=[round(100 * (sp.mean() - 1.96 * sp.std(ddof=1) / math.sqrt(len(sp))), 3), round(100 * (sp.mean() + 1.96 * sp.std(ddof=1) / math.sqrt(len(sp))), 3)],
                t=round(sp.mean() / (sp.std(ddof=1) / math.sqrt(len(sp))), 2))


def xsmom_null(idx, P, names, C, nsim=300):
    st = {}
    r = simulate(idx, P, names, pol_xsmom(C, idx, 14), MAKER, True, state=st)
    act = metrics(r['eq'])['cagr']
    # Faster approximate null with daily close-to-close returns and switch costs
    R = np.vstack([np.zeros(C.shape[1]), C[1:] / C[:-1] - 1])
    sw_days = []
    st2 = {}
    pol = pol_xsmom(C, idx, 14)
    wn = np.zeros(C.shape[1]); held_hist = []
    for i in range(len(idx)):
        before = list(st2.get('held', []))
        pol(i, wn, 0, st2)
        if st2.get('held', []) != before:
            sw_days.append((i, len([x for x in before if x not in st2['held']])))
    cost = MAKER + 0.001
    sims = []
    for _ in range(nsim):
        held = list(RNG.choice(5, 2, replace=False)); val = np.zeros(5); val[held] = 0.5
        sd = dict(sw_days)
        logv = 0.0
        for i in range(1, len(idx)):
            val = val * (1 + R[i])
            tot = val.sum(); logv += math.log(tot); val /= tot
            if i in sd and i > sw_days[0][0]:
                for _k in range(sd[i]):
                    out_ = held[RNG.integers(len(held))]
                    inn = RNG.choice([j for j in range(5) if j not in held])
                    v = val[out_] * (1 - 2 * cost); val[out_] = 0; val[inn] += v
                    held = [h for h in held if h != out_] + [inn]
                val /= val.sum() if val.sum() > 0 else 1
        yrs = (idx[-1] - idx[0]).days / 365.25
        sims.append(100 * (math.exp(logv / yrs) - 1))
    sims = np.array(sims)
    return dict(actual_cagr=act, null_median_cagr=round(float(np.median(sims)), 2), pct_rank=round(float((sims < act).mean()), 3),
                switches=len(sw_days), note='random replacement coin on the same switch dates; close-to-close approx, 2 fills per switch at maker+0.1%')


# ----------------------------------------------------------------- C: grid
def grid_sim(df, s=0.015, fee=MAKER, slip=0.0005, pen=0.001, eps=EPS, lot=50.0, cap=0.5, nlev=10, stop_steps=3,
             dd_stop=0.15, exit_cost=TAKER + 0.003, pause=168, wick=0.05, ambig='adverse', cash0=1000.0, ppy=8760):
    O, Hh, L, C = (df[c].values for c in ('open', 'high', 'low', 'close'))
    n = len(C)
    rd = (1 + CASH_RATE) ** (1 / ppy) - 1
    cash = cash0; interest = 0.0; capture = 0.0; stop_loss = 0.0
    P0 = C[0]
    lv = [dict(px=P0 * (1 - s) ** (k + 1), st='buy', act=1, u=0.0, cost=0.0) for k in range(nlev)]
    peak = cash0; paused_until = -1
    eq = np.empty(n); trades = []; nfill = 0; nstop = 0; amb_bars = 0; fees = 0.0
    for i in range(n):
        it = cash * rd; cash += it; interest += it
        o, h, l, c = O[i], Hh[i], L[i], C[i]
        if i < paused_until:
            eq[i] = cash; continue
        if i == paused_until:
            P0 = c
            lv = [dict(px=P0 * (1 - s) ** (k + 1), st='buy', act=i + 1, u=0.0, cost=0.0) for k in range(nlev)]
            peak = cash
            eq[i] = cash; continue
        el = max(l, min(o, c) * (1 - wick)); eh = min(h, max(o, c) * (1 + wick))
        buys = [x for x in lv if x['st'] == 'buy' and x['act'] <= i and el <= x['px'] * (1 - eps)]
        sells = [x for x in lv if x['st'] == 'hold' and x['act'] <= i and eh >= x['px'] * (1 + s) * (1 + eps)]
        if buys and sells:
            amb_bars += 1
            if ambig == 'adverse':
                sells = []
        for x in sells:
            spx = x['px'] * (1 + s) * (1 - pen)
            proceeds = x['u'] * spx; f = proceeds * (fee + slip)
            cash += proceeds - f; fees += f
            capture += proceeds - f - x['cost']
            trades.append(dict(date=df.index[i], asset='BTC', side='sell', value=proceeds)); nfill += 1
            x.update(st='buy', act=i + 1, u=0.0, cost=0.0)
        inv_u = sum(x['u'] for x in lv)
        for x in sorted(buys, key=lambda z: -z['px']):
            bpx = x['px'] * (1 + pen)
            E = cash + inv_u * x['px']
            if inv_u * x['px'] + lot > cap * E or cash < lot * (1 + fee + slip):
                continue
            u = lot / bpx; f = lot * (fee + slip)
            cash -= lot + f; fees += f; inv_u += u
            x.update(st='hold', act=i + 1, u=u, cost=lot + f)
            trades.append(dict(date=df.index[i], asset='BTC', side='buy', value=lot)); nfill += 1
        inv_u = sum(x['u'] for x in lv)
        e = cash + inv_u * c
        peak = max(peak, e)
        if inv_u > 0 and (c < lv[-1]['px'] * (1 - s) ** stop_steps or e / peak - 1 <= -dd_stop):
            proceeds = inv_u * c * (1 - exit_cost)
            basis = sum(x['cost'] for x in lv)
            stop_loss += proceeds - basis
            fees += inv_u * c * TAKER
            cash += proceeds
            trades.append(dict(date=df.index[i], asset='BTC', side='sell', value=inv_u * c)); nstop += 1
            for x in lv: x.update(st='off', u=0.0, cost=0.0)
            paused_until = i + pause
            e = cash
        elif inv_u == 0 and c > P0 * (1 + s):
            P0 = c
            lv = [dict(px=P0 * (1 - s) ** (k + 1), st='buy', act=i + 1, u=0.0, cost=0.0) for k in range(nlev)]
        eq[i] = e
    eqs = pd.Series(eq, index=df.index)
    inv_u = sum(x['u'] for x in lv)
    open_basis = sum(x['cost'] for x in lv)
    unreal = inv_u * C[-1] - open_basis
    return dict(eq=eqs, trades=trades, fills=nfill, stops=nstop, ambiguous_bars=amb_bars, fees=round(fees, 2),
                capture=round(capture, 2), stop_loss=round(stop_loss, 2), unrealised=round(unreal, 2), interest=round(interest, 2),
                final=round(eq[-1], 2), exposure=None)


def run_C(dfs):
    out = {}
    btc_h = load(f'{H}/BTC_1h.csv'); eth_h = load(f'{H}/ETH_1h.csv')
    def daily_of(e):
        return e.resample('1D').last().dropna()
    def summ(r, ppy=8760):
        ed = daily_of(r['eq'])
        m = metrics(ed)
        m.update(dict(fills=r['fills'], stops=r['stops'], ambiguous_bars=r['ambiguous_bars'], fees=r['fees'],
                      grid_capture=r['capture'], stop_losses=r['stop_loss'], open_inventory_mtm=r['unrealised'], interest=r['interest'],
                      years=yearly(ed), uk=uk_tax(r['trades'], ed)))
        m['regimes'] = {k: round(100 * (ed[a:b].iloc[-1] / ed[:a].iloc[-1] - 1) if len(ed[:a]) else 100 * (ed[a:b].iloc[-1] / ed[a:b].iloc[0] - 1), 1)
                        for k, a, b in (('2024H2', '2024-07-17', '2024-12-31'), ('2025', '2025-01-01', '2025-12-31'), ('2026', '2026-01-01', '2026-12-31'))}
        m['ret_over_dd'] = round(m['cagr'] / abs(m['maxdd']), 3) if m['maxdd'] else None
        return m
    # benchmark 25/75 monthly on daily bars over same period
    idx, P = panel(dfs, ['BTC'], '2024-07-17')
    bm = simulate(idx, P, ['BTC'], pol_const([0.25], monthly=True, idx=idx), MAKER, True)
    mb = summarize(bm, '25/75'); mb['ret_over_dd'] = round(mb['cagr'] / abs(mb['maxdd']), 3)
    mb['regimes'] = {k: round(100 * (bm['eq'][a:b].iloc[-1] / bm['eq'][:a].iloc[-1] - 1) if len(bm['eq'][:a]) else 100 * (bm['eq'][a:b].iloc[-1] / bm['eq'][a:b].iloc[0] - 1), 1)
                     for k, a, b in (('2024H2', '2024-07-17', '2024-12-31'), ('2025', '2025-01-01', '2025-12-31'), ('2026', '2026-01-01', '2026-12-31'))}
    log_trial('C', '25/75 monthly benchmark', '2024-07..', MAKER, mb, 'benchmark')
    out['benchmark_25_75_monthly'] = mb
    SERIES['C_bench_25_75'] = bm['eq']
    bh = btc_h.close
    out['btc_buyhold_same_period'] = metrics(daily_of(bh / bh.iloc[0] * 1000))
    rows = {}
    for s in (0.01, 0.015, 0.02, 0.03):
        for fee in (MAKER, TAKER):
            r = grid_sim(btc_h, s=s, fee=fee)
            m = summ(r); log_trial('C', f'BTC hourly grid s={s}', '2024-07..', fee, m)
            rows[f's={s} fee={fee}'] = m
            if s == 0.015 and fee == MAKER:
                SERIES['C_grid_BTC_1.5'] = daily_of(r['eq'])
    out['btc_hourly'] = rows
    # robustness at base step
    rob = {}
    for nm, kw in [('pen0.05', dict(pen=0.0005)), ('pen0.20', dict(pen=0.002)), ('eps0.20+pen0.20', dict(eps=0.002, pen=0.002)),
                   ('optimistic_ambiguous', dict(ambig='optimistic')), ('no_wick_filter', dict(wick=10.0)),
                   ('lot37.5', dict(lot=37.5)), ('lot62.5', dict(lot=62.5)), ('dd_stop0.10', dict(dd_stop=0.10)), ('dd_stop0.20', dict(dd_stop=0.20))]:
        r = grid_sim(btc_h, s=0.015, **kw)
        m = summ(r); log_trial('C', f'BTC grid s=0.015 {nm}', '2024-07..', MAKER, m)
        rob[nm] = {k: m[k] for k in ('cagr', 'maxdd', 'grid_capture', 'stop_losses', 'open_inventory_mtm', 'fills', 'stops', 'regimes')}
    out['btc_robustness_s1.5'] = rob
    base = rows[f's=0.015 fee={MAKER}']
    opt = rob['optimistic_ambiguous']
    out['ambiguous_share_of_pnl'] = dict(adverse_final_minus_start=base['total'], optimistic=opt['cagr'], note='compare total P&L under adverse vs optimistic ambiguous-bar handling')
    # ETH secondary
    r = grid_sim(eth_h, s=0.015, fee=MAKER, slip=0.0005)
    m = summ(r); log_trial('C', 'ETH hourly grid s=0.015', '2024-07..', MAKER, m)
    out['eth_hourly_s1.5'] = m
    out['eth_buyhold_same_period'] = metrics(daily_of(eth_h.close / eth_h.close.iloc[0] * 1000))
    # daily stress since 2017 (upper bound: intrabar path unknown)
    dly = {}
    bd = dfs['BTC']
    for s in (0.03, 0.04, 0.05):
        r = grid_sim(bd, s=s, fee=MAKER, pause=7, ppy=365)
        ed = r['eq']; m = metrics(ed)
        m.update(dict(fills=r['fills'], stops=r['stops'], grid_capture=r['capture'], stop_losses=r['stop_loss'], open_inventory_mtm=r['unrealised'],
                      interest=r['interest'], years=yearly(ed), ambiguous_bars=r['ambiguous_bars']))
        log_trial('C', f'BTC daily grid s={s} (upper bound)', '2017..', MAKER, m)
        dly[f's={s}'] = m
        if s == 0.03:
            SERIES['C_grid_BTC_daily_3'] = ed
    out['btc_daily_since2017_upper_bound'] = dly
    # diagnostic: same grid with no stop at all (shows how much the stop rule costs vs holding inventory)
    r = grid_sim(btc_h, s=0.015, stop_steps=99, dd_stop=0.99)
    m = summ(r); log_trial('C', 'BTC grid s=0.015 NO STOP (diagnostic)', '2024-07..', MAKER, m)
    out['diagnostic_no_stop_s1.5'] = {k: m[k] for k in ('cagr', 'maxdd', 'grid_capture', 'stop_losses', 'open_inventory_mtm', 'fills', 'regimes')}
    # mean-reversion diagnostic: variance ratio of hourly log returns at 1-3% scales
    lr = np.log(bh).diff().dropna()
    vr = {}
    for q in (4, 12, 24, 72):
        vq = np.log(bh).diff(q).dropna().var()
        vr[f'VR({q}h)'] = round(float(vq / (q * lr.var())), 3)
    out['variance_ratios_hourly'] = vr
    return out


# ----------------------------------------------------------------- D: washout bounce
def washout_events(dfs, coin, k, kb, confirm=False, start=None, end=None, hold=5, target=0.06, maker_entry=True,
                   fee_entry=MAKER, fee_exit_tgt=MAKER, fee_exit_time=TAKER):
    d = dfs[coin]; b = dfs['BTC']
    idx = d.index.intersection(b.index)
    d = d.loc[idx]; b = b.loc[idx]
    r = np.log(d.close).diff(); rb = np.log(b.close).diff()
    sd = r.rolling(30).std().shift(1); sdb = rb.rolling(30).std().shift(1)
    sig = (r <= -k * sd) & (rb <= -kb * sdb)
    slip = SLIP[coin.split('_')[0]]
    O, Hh, L, C = d.open.values, d.high.values, d.low.values, d.close.values
    ev = []; busy_until = -1
    for t in np.where(sig.values)[0]:
        if start and idx[t] < pd.Timestamp(start): continue
        if end and idx[t] > pd.Timestamp(end): continue
        if t <= busy_until: continue
        e = t + 1
        if confirm:
            if t + 2 >= len(C) or not C[t + 1] > C[t]:
                continue
            e = t + 2
        if e + hold >= len(C): continue
        ep = O[e]
        if maker_entry and not (L[e] <= ep * (1 - EPS)):
            ev.append(dict(date=idx[t], filled=False)); continue
        cost_in = fee_entry + slip
        tp = ep * (1 + target); ex = None
        for j in range(e + 1, e + hold + 1):       # target active from the bar after the fill
            if Hh[j] >= tp * (1 + EPS):
                ex = (tp, fee_exit_tgt + slip, j); break
        if ex is None:
            j = e + hold
            ex = (O[j + 1] if j + 1 < len(O) else C[j], fee_exit_time + slip, j + 1)
        net = (ex[0] / ep) * (1 - ex[1]) / (1 + cost_in) - 1
        gross = ex[0] / ep - 1
        ev.append(dict(date=idx[t], filled=True, net=net, gross=gross, days=ex[2] - e))
        busy_until = ex[2]
    return ev


def ev_stats(ev):
    f = [x for x in ev if x.get('filled')]
    if not f:
        return dict(n=0, signals=len(ev))
    a = np.array([x['net'] for x in f])
    se = a.std(ddof=1) / math.sqrt(len(a)) if len(a) > 1 else np.nan
    return dict(signals=len(ev), n=len(a), mean=round(100 * a.mean(), 2), median=round(100 * np.median(a), 2),
                ci95=[round(100 * (a.mean() - 1.96 * se), 2), round(100 * (a.mean() + 1.96 * se), 2)] if len(a) > 1 else None,
                t=round(a.mean() / se, 2) if len(a) > 1 and se > 0 else None, win=round(float((a > 0).mean()), 2),
                gross_mean=round(100 * np.mean([x['gross'] for x in f]), 2), total=round(100 * (np.prod(1 + a) - 1), 1))


def random_entry_null(dfs, coin, n, start, end, hold=5, target=0.06, nsim=2000):
    d = dfs[coin][start:end]
    O, Hh, C = d.open.values, d.high.values, d.close.values
    slip = SLIP[coin.split('_')[0]]
    outs = []
    for e in range(1, len(C) - hold - 2):
        ep = O[e]; tp = ep * (1 + target); ex = None
        for j in range(e + 1, e + hold + 1):
            if Hh[j] >= tp * (1 + EPS): ex = (tp, MAKER + slip); break
        if ex is None: ex = (O[e + hold + 1], TAKER + slip)
        outs.append((ex[0] / ep) * (1 - ex[1]) / (1 + MAKER + slip) - 1)
    outs = np.array(outs)
    if n == 0: return None
    means = np.array([RNG.choice(outs, n).mean() for _ in range(nsim)])
    return outs, means


def run_D(dfs):
    out = {}
    coins = ['BTC', 'ETH_SYN', 'SOL']
    # 1) fit on 2017-2021 only
    grid = []
    for k in (2.5, 3.0, 3.5):
        for kb in (1.5, 2.0, 2.5):
            for conf in (False, True):
                evs = []
                for c in coins:
                    evs += washout_events(dfs, c, k, kb, conf, end='2021-12-31')
                st = ev_stats(evs)
                log_trial('D', f'train k={k} kb={kb} confirm={conf}', '2017-2021', MAKER, st)
                grid.append(dict(k=k, kb=kb, confirm=conf, **st))
    out['train_grid'] = grid
    elig = [g for g in grid if g.get('n', 0) >= 8]
    best = max(elig, key=lambda g: g['mean']) if elig else None
    out['chosen_on_train'] = best
    # 2) test ONCE on 2022-2026: chosen + pre-registered (3, 2) base and confirm
    test = {}
    tests = [('preregistered k=3 kb=2', 3.0, 2.0, False), ('preregistered confirm k=3 kb=2', 3.0, 2.0, True)]
    if best:
        tests.append((f"train-chosen k={best['k']} kb={best['kb']} confirm={best['confirm']}", best['k'], best['kb'], best['confirm']))
    for nm, k, kb, conf in tests:
        per = {}; allev = []
        for c in coins:
            ev = washout_events(dfs, c, k, kb, conf, start='2022-01-01'); allev += ev
            per[c] = ev_stats(ev)
        st = ev_stats(allev)
        log_trial('D', f'TEST {nm}', '2022-2026', MAKER, st)
        evt = [x for x in allev if x.get('filled')]
        st['events'] = [dict(date=str(x['date'].date()), net=round(100 * x['net'], 2)) for x in evt]
        # all-taker stress
        allt = []
        for c in coins:
            allt += washout_events(dfs, c, k, kb, conf, start='2022-01-01', maker_entry=False, fee_entry=TAKER, fee_exit_tgt=TAKER, fee_exit_time=TAKER)
        st['taker_stress'] = ev_stats(allt)
        test[nm] = dict(pooled=st, per_coin=per)
    out['test_2022_2026'] = test
    # 3) random-entry null on the test period for the pre-registered rule (pooled by coin counts)
    pre = test['preregistered k=3 kb=2']
    nulls = {}
    for c in coins:
        n = pre['per_coin'][c].get('n', 0)
        if n:
            outs, means = random_entry_null(dfs, c, n, '2022-01-01', '2026-12-31')
            nulls[c] = dict(n=n, random_mean=round(100 * outs.mean(), 2), strategy_mean=pre['per_coin'][c]['mean'],
                            pct_rank=round(float((means < pre['per_coin'][c]['mean'] / 100).mean()), 3))
    out['random_entry_null'] = nulls
    # 4) sensitivity (on test, reported only; not used for selection)
    sens = {}
    for nm, kw in [('target4.5', dict(target=0.045)), ('target7.5', dict(target=0.075)), ('hold3', dict(hold=3)), ('hold7', dict(hold=7)),
                   ('k2.25', dict(k=2.25)), ('k3.75', dict(k=3.75)), ('kb1.5', dict(kb=1.5)), ('kb2.5', dict(kb=2.5))]:
        k = kw.pop('k', 3.0); kb = kw.pop('kb', 2.0)
        evs = []
        for c in coins:
            evs += washout_events(dfs, c, k, kb, False, start='2022-01-01', **kw)
        st = ev_stats(evs); log_trial('D', f'sens {nm}', '2022-2026', MAKER, st)
        sens[nm] = {x: st.get(x) for x in ('n', 'mean', 'ci95', 't', 'win')}
    out['sensitivity_test_period'] = sens
    # 5) whole-period equity curve (3 sleeves of 1/3, cash at 4% while flat) for the pre-registered rule
    out['equity'] = washout_equity(dfs, coins, 3.0, 2.0)
    return out


def washout_equity(dfs, coins, k, kb):
    idx = dfs['BTC'].index
    rd = (1 + CASH_RATE) ** (1 / 365) - 1
    sleeves = {}
    for c in coins:
        ev = [x for x in washout_events(dfs, c, k, kb, False) if x.get('filled')]
        v = pd.Series(1.0, index=idx)
        start = dfs[c].index[0]
        val = 1000 / len(coins); vals = []
        evmap = {}
        for x in ev:
            exit_day = dfs[c].index.get_loc(x['date']) + 1 + x['days']
            evmap[dfs[c].index[min(exit_day, len(dfs[c]) - 1)]] = x['net']
        # mark at exit only (no intra-trade marking) -> drawdowns understated; flagged
        for d in idx:
            val *= (1 + rd)
            if d in evmap: val *= (1 + evmap[d])
            vals.append(val)
        sleeves[c] = pd.Series(vals, index=idx)
    eq = sum(sleeves.values())
    SERIES['D_washout'] = eq
    m = metrics(eq); m['years'] = yearly(eq); m['note'] = 'trade P&L booked at exit; intra-trade drawdowns not marked; idle sleeves earn 4%'
    log_trial('D', 'equity curve preregistered', '2017..', MAKER, m)
    return m


# ----------------------------------------------------------------- E: ETH/BTC rotation
def run_E(dfs, fx):
    bu = load(f'{D}/BTC_USD_1d.csv'); eu = load(f'{D}/ETH_USD_1d.csv')
    idx = bu.index.intersection(eu.index)
    bo, bc = bu.open[idx].values, bu.close[idx].values
    eo, ec = eu.open[idx].values, eu.close[idx].values
    fxx = fx.reindex(idx).ffill().values
    lr = np.log(ec / bc)

    def zser(W):
        s = pd.Series(lr)
        return ((s - s.rolling(W).mean()) / s.rolling(W).std()).values

    def run(W=60, ent=1.5, ex=0.5, mirror=False, fee=MAKER, a=None, b=None):
        z = zser(W)
        # state 0=BTC, 1=ETH. default (non-mirror): sit in BTC, go ETH when ETH cheap (z<-ent), back when z>+ex
        st = 1 if mirror else 0
        val = 1000.0; vals = []; sw = 0; trades = []
        ii = range(len(idx))
        units_asset = st
        cur_val_usd = None
        held = st
        u = 1000.0 * fxx[0] / (eo[0] if held else bo[0])
        pending = None
        for i in ii:
            if pending is not None:
                # switch at open of i via the ETH/BTC cross: one fill
                v = u * (eo[i] if held else bo[i])
                v *= (1 - fee - 0.0005)
                trades.append(dict(date=idx[i], asset='ETH' if held else 'BTC', side='sell', value=v / fxx[i]))
                held = pending; pending = None; sw += 1
                u = v / (eo[i] if held else bo[i])
                trades.append(dict(date=idx[i], asset='ETH' if held else 'BTC', side='buy', value=v / fxx[i]))
            vals.append(u * (ec[i] if held else bc[i]) / fxx[i])
            if np.isnan(z[i]): continue
            if not mirror:
                if held == 0 and z[i] < -ent: pending = 1
                elif held == 1 and z[i] > ex: pending = 0
            else:
                if held == 1 and z[i] > ent: pending = 0
                elif held == 0 and z[i] < -ex: pending = 1
        eq = pd.Series(vals, index=idx)
        return eq, sw, trades

    def static(rebal=False, fee=MAKER):
        ub = 500 * fxx[0] / bo[0]; ue = 500 * fxx[0] / eo[0]; vals = []
        for i in range(len(idx)):
            vb, ve = ub * bc[i], ue * ec[i]
            if rebal and i + 1 < len(idx) and idx[i + 1].month != idx[i].month:
                tot = vb + ve; d = abs(vb - tot / 2); tot -= d * (fee + 0.0005)
                ub = tot / 2 / bc[i]; ue = tot / 2 / ec[i]; vb, ve = tot / 2, tot / 2
            vals.append((vb + ve) / fxx[i])
        return pd.Series(vals, index=idx)

    out = {}
    s50 = static(); s50r = static(True)
    SERIES['E_static5050'] = s50
    for mirror in (False, True):
        for fee in (MAKER, TAKER):
            eq, sw, tr = run(mirror=mirror, fee=fee)
            m = metrics(eq); m['switches'] = sw; m['years'] = yearly(eq)
            m['uk'] = uk_tax(tr, eq)
            log_trial('E', f'fixed W=60 ent=1.5 ex=0.5 mirror={mirror}', '2017..', fee, m)
            m['oos_2022_2026'] = metrics(eq['2022':]); m['is_2017_2021'] = metrics(eq[:'2021'])
            out[f'fixed mirror={mirror} fee={fee}'] = m
            if fee == MAKER:
                SERIES[f'E_fixed_mirror{mirror}'] = eq
    out['static_5050_hold'] = dict(full=metrics(s50), oos_2022_2026=metrics(s50['2022':]), years=yearly(s50))
    out['static_5050_monthly'] = dict(full=metrics(s50r), oos_2022_2026=metrics(s50r['2022':]))
    # walk-forward: each year from 2020, choose (W, ent, mirror) on all data before it by CAGR; trade that year
    grid = [(W, ent, mir) for W in (30, 60, 90) for ent in (1.0, 1.5, 2.0) for mir in (False, True)]
    cache = {}
    for g in grid:
        eq, sw, _ = run(W=g[0], ent=g[1], mirror=g[2])
        cache[g] = eq
        log_trial('E', f'WF grid W={g[0]} ent={g[1]} mirror={g[2]}', '2017..', MAKER, metrics(eq), 'walk-forward candidate')
    wf_rets = []; picks = {}
    for y in range(2020, 2027):
        train_end = f'{y - 1}-12-31'
        best = max(grid, key=lambda g: cache[g][:train_end].iloc[-1] / cache[g][:train_end].iloc[0])
        picks[y] = best
        e = cache[best]
        seg = e[f'{y}']
        prev = e[:train_end].iloc[-1]
        r = seg / prev
        wf_rets.append(r)
    # chain yearly segments (note: switching config at year start ignores the switch cost of changing state -> small optimism)
    chained = []; lvl = 1000.0
    for r in wf_rets:
        chained.append(r * lvl); lvl = float((r * lvl).iloc[-1])
    wf = pd.concat(chained)
    SERIES['E_walkforward'] = wf
    out['walk_forward'] = dict(picks={str(k): list(v) for k, v in picks.items()}, metrics=metrics(wf), years=yearly(wf),
                               static_hold_same_period=metrics(s50['2020':]), static_monthly_same_period=metrics(s50r['2020':]),
                               oos_2022_2026=metrics(wf['2022':]), static_hold_2022_2026=metrics(s50['2022':]),
                               static_monthly_2022_2026=metrics(s50r['2022':]), btc_only_2022_2026=metrics(pd.Series(bc / fxx, index=idx)['2022':]))
    SERIES['E_static5050_monthly'] = s50r
    # circular null for fixed rule: shift ETH-state path
    return out


# ----------------------------------------------------------------- F: XRP / LINK supply-event study
def run_F():
    xu = load(f'{D}/XRP_USD_1d.csv'); bu = load(f'{D}/BTC_USD_1d.csv'); lu = load(f'{D}/LINK_USD_1d.csv')
    out = {}
    for coin, df, months in (('XRP', xu, list(range(1, 13))), ('LINK_quarter_start_proxy', lu, [1, 4, 7, 10])):
        full = pd.date_range(df.index[0], df.index[-1], freq='1D')
        r = np.log(df.close.reindex(full)).diff() - np.log(bu.close.reindex(full)).diff()
        res = {}
        windows = {'[-5,-1]': (-5, -1), '[0,+2]': (0, 2), '[+3,+14]': (3, 14)}
        anchors_all = [d for d in full if d.day == 1 and d.month in months]
        for wn, (a, b) in windows.items():
            def car(d):
                seg = r.reindex(pd.date_range(d + pd.Timedelta(days=a), d + pd.Timedelta(days=b)))
                return seg.sum() if seg.notna().all() and len(seg) == b - a + 1 else np.nan
            ev = np.array([car(d) for d in anchors_all]); ev = ev[~np.isnan(ev)]
            # null: same window anchored on every other day
            others = [d for d in full[30:-20] if d.day != 1]
            nul = np.array([car(d) for d in others[::1]]); nul = nul[~np.isnan(nul)]
            t, p = stats.ttest_ind(ev, nul, equal_var=False)
            # permutation: random day-of-month anchors, one per month (same count)
            perm = []
            for _ in range(1000):
                perm.append(RNG.choice(nul, len(ev)).mean())
            perm = np.array(perm)
            p_perm = float(2 * min((perm <= ev.mean()).mean(), (perm >= ev.mean()).mean()))
            se = ev.std(ddof=1) / math.sqrt(len(ev))
            res[wn] = dict(n=len(ev), mean_excess_pct=round(100 * ev.mean(), 2), ci95=[round(100 * (ev.mean() - 1.96 * se), 2), round(100 * (ev.mean() + 1.96 * se), 2)],
                           all_days_mean_pct=round(100 * nul.mean(), 2), welch_p=round(float(p), 3), perm_p=round(p_perm, 3))
            log_trial('F', f'{coin} window {wn}', 'USD since 2019', 0, dict(n=len(ev), mean=res[wn]['mean_excess_pct']))
        out[coin] = res
    out['note'] = 'XRP-USD has a Coinbase gap Jan 2021 - Jun 2023 (delisting); those months are excluded. LINK unlock dates are inferred (quarter starts) -> exploratory only.'
    return out


# ----------------------------------------------------------------- main
def main():
    dfs, fx = daily_gbp()
    R = {}
    # ---- G baselines
    idx, P = panel(dfs, ['BTC'], '2017-01-01')
    bh = simulate(idx, P, ['BTC'], pol_const([1.0], band=99), TAKER, False)
    R['G_buyhold_BTC'] = summarize(bh, 'BH'); log_trial('G', 'buy&hold BTC', '2017..', TAKER, R['G_buyhold_BTC'])
    SERIES['G_BH_BTC'] = bh['eq']
    mix = simulate(idx, P, ['BTC'], pol_const([0.25], band=0.10, min_gap=1), MAKER, True)
    R['G_25_75_band10'] = summarize(mix, 'mix'); log_trial('G', '25/75 BTC/cash band 10pt', '2017..', MAKER, R['G_25_75_band10'])
    SERIES['G_25_75'] = mix['eq']
    for w in (0.10, 0.50):
        mx = simulate(idx, P, ['BTC'], pol_const([w], band=0.4 * w, min_gap=1), MAKER, True)
        R[f'G_{int(w*100)}_{100-int(w*100)}_band'] = summarize(mx, 'mix'); log_trial('G', f'{w} BTC/cash band', '2017..', MAKER, R[f'G_{int(w*100)}_{100-int(w*100)}_band'])
        SERIES[f'G_{int(w*100)}'] = mx['eq']
    sav = savings_curve(idx); SERIES['G_savings_4.5'] = sav
    R['G_savings_4.5'] = metrics(sav)
    R['G_DCA_12m'] = dca_rolling(dfs['BTC'].close)
    # basket buy & hold for context (ETH synthetic pre-2018-09)
    print('G done', flush=True)
    R['A'] = run_A(dfs); print('A done', flush=True)
    R['B'] = run_B(dfs); print('B done', flush=True)
    R['C'] = run_C(dfs); print('C done', flush=True)
    R['D'] = run_D(dfs); print('D done', flush=True)
    R['E'] = run_E(dfs, fx); print('E done', flush=True)
    R['F'] = run_F(); print('F done', flush=True)

    # ---- rolling windows & DSR
    roll = {}
    for k, e in SERIES.items():
        roll[k] = {'1y': rolling_beat(e, 1), '3y': rolling_beat(e, 3)}
    R['rolling_vs_savings_4.5'] = roll
    # rolling windows starting 2021 or later only (excludes the 2017-2020 bull run that flatters everything)
    R['rolling_vs_savings_4.5_from2021'] = {k: {'1y': rolling_beat(SERIES[k]['2021':], 1), '3y': rolling_beat(SERIES[k]['2021':], 3)}
                                              for k in ('G_BH_BTC', 'G_25_75', 'G_10', 'G_50', 'A_BTC', 'A_BTC_const', 'E_static5050_monthly')}
    N = len(LEDGER) + PRIOR_TRIALS
    fam = {}
    for r in LEDGER:
        if isinstance(r.get('sharpe'), (int, float)) and not np.isnan(r['sharpe']):
            fam.setdefault(r['candidate'], []).append(r['sharpe'])
    allsh = [x for v in fam.values() for x in v]
    var_all = float(np.var(allsh))
    # lenient: variance of Sharpe within each candidate's own family of variants (floor 0.01)
    var_fam = {c: max(0.01, float(np.var(v))) for c, v in fam.items()}
    R['dsr'] = {}
    for k in SERIES:
        if k.startswith('G_savings'):
            continue
        c = k.split('_')[0]
        R['dsr'][k] = dict(harsh_all_trials=dsr(SERIES[k], N, var_all / 365), lenient_family=dsr(SERIES[k], N, var_fam.get(c, 0.01) / 365))
    R['dsr_meta'] = dict(N_trials=N, this_round=len(LEDGER), prior=PRIOR_TRIALS, var_annual_sharpe_all=round(var_all, 4),
                         var_annual_sharpe_family={c: round(v, 4) for c, v in var_fam.items()}, n_sharpes=len(allsh))
    # does the timing add anything over its own benchmark?  PSR of the daily return DIFFERENCE (>0?)
    def diff_psr(a, b):
        ra = SERIES[a].pct_change(); rb = SERIES[b].reindex(SERIES[a].index).pct_change()
        d = (ra - rb).dropna(); T = len(d); sr = d.mean() / d.std()
        g3 = stats.skew(d); g4 = stats.kurtosis(d, fisher=False)
        z = sr * math.sqrt(T - 1) / math.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
        return dict(ann_mean_diff_pct=round(100 * 365 * d.mean(), 2), sr_diff_ann=round(sr * math.sqrt(365), 3), psr=round(float(stats.norm.cdf(z)), 4), T=T)
    R['edge_vs_benchmark'] = {f'{a} - {b}': diff_psr(a, b) for a, b in (('A_BTC', 'A_BTC_const'), ('A_BASKET', 'A_BASKET_const'), ('B_mom14', 'B_EW'), ('B_mom7', 'B_EW'),
                                                                         ('E_fixed_mirrorFalse', 'E_static5050'), ('E_walkforward', 'E_static5050_monthly'),
                                                                         ('C_grid_BTC_1.5', 'C_bench_25_75'))}
    pd.DataFrame(LEDGER).to_csv(os.path.join(OUT, 'trial_ledger.csv'), index=False)
    with open(os.path.join(OUT, 'assess3_results.json'), 'w') as f:
        json.dump(R, f, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print('trials this round:', len(LEDGER), ' total incl. prior:', N)


if __name__ == '__main__':
    main()
