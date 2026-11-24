"""Strategy + paper broker. Shared by the live bot and the backtest so they
can't drift apart."""
from __future__ import annotations

import pandas as pd

from . import config as C
from .indicators import atr, bollinger, ema, rsi


# ---------------------------------------------------------------- regime
def regime(btc4: pd.DataFrame) -> str:
    """trend_up / trend_down / range, from BTC's 4h chart."""
    if len(btc4) < C.REGIME_EMA_SLOW + 5:
        return "unknown"
    c = btc4["close"]
    f, s = ema(c, C.REGIME_EMA_FAST).iloc[-1], ema(c, C.REGIME_EMA_SLOW).iloc[-1]
    px = c.iloc[-1]
    if px > s and f > s:
        return "trend_up"
    if px < s and f < s:
        return "trend_down"
    return "range"


def features(df: pd.DataFrame) -> dict:
    """Latest indicator values for one coin's closed 4h bars."""
    c = df["close"]
    lo, mid, _ = bollinger(c, C.MR_BB_LEN, C.MR_BB_STD)
    prior = df.iloc[:-1]
    return {
        "close": c.iloc[-1],
        "atr": atr(df, C.ATR_LEN).iloc[-1],
        "ema_slow": ema(c, C.REGIME_EMA_SLOW).iloc[-1] if len(df) > C.REGIME_EMA_SLOW else float("nan"),
        "hh": prior["high"].iloc[-C.TREND_BREAKOUT_BARS:].max(),
        "ll": prior["low"].iloc[-C.TREND_EXIT_BARS:].min(),
        "rsi": rsi(c, C.MR_RSI_LEN).iloc[-1],
        "bb_lo": lo.iloc[-1],
        "bb_mid": mid.iloc[-1],
    }


# ---------------------------------------------------------------- account
def slip(coin: str) -> float:
    return C.SLIPPAGE.get(coin, C.SLIPPAGE_DEFAULT)


class Account:
    def __init__(self, d: dict | None = None, fee_mult: float = 1.0):
        d = d or {}
        self.cash = d.get("cash", C.START_CAPITAL_GBP)
        self.positions: dict = d.get("positions", {})
        self.trades: list = d.get("trades", [])
        self.next_id = d.get("next_id", 1)
        self.day = d.get("day")
        self.day_start_equity = d.get("day_start_equity", C.START_CAPITAL_GBP)
        self.halted = d.get("halted", False)
        self.halt_reason = d.get("halt_reason")
        self.fees_paid = d.get("fees_paid", 0.0)
        self.fee_rate = C.FEE_RATE * fee_mult

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "cash", "positions", "trades", "next_id", "day", "day_start_equity",
            "halted", "halt_reason", "fees_paid")}

    def equity(self, prices: dict) -> float:
        return self.cash + sum(p["qty"] * prices.get(c, p["entry_price"]) for c, p in self.positions.items())

    # -- fills
    def buy(self, coin, ref_price, stop, strategy, when, regime_name):
        px = ref_price * (1 + slip(coin))
        if stop >= px:
            return None
        eq = self.equity({coin: ref_price, **{c: p.get("last", p["entry_price"]) for c, p in self.positions.items()}})
        risk_gbp = eq * C.RISK_PER_TRADE
        per_unit_loss = (px - stop) + px * self.fee_rate * 2  # include both fees in the risk
        qty = risk_gbp / per_unit_loss
        notional = min(qty * px, eq * C.MAX_POSITION_FRACTION * C.LEVERAGE, self.cash / (1 + self.fee_rate))
        if notional < C.MIN_ORDER_GBP:
            return None
        qty = notional / px
        fee = notional * self.fee_rate
        self.cash -= notional + fee
        self.fees_paid += fee
        tid = f"T{self.next_id:04d}"
        self.next_id += 1
        self.positions[coin] = {
            "id": tid, "qty": qty, "entry_price": px, "entry_time": str(when), "stop": stop,
            "strategy": strategy, "regime": regime_name, "entry_fee": fee,
            "risk_gbp": round(qty * per_unit_loss, 2), "last": ref_price,
        }
        return self.positions[coin]

    def sell(self, coin, ref_price, when, reason):
        p = self.positions.pop(coin)
        px = ref_price * (1 - slip(coin))
        gross = p["qty"] * px
        fee = gross * self.fee_rate
        self.cash += gross - fee
        self.fees_paid += fee
        pnl = gross - fee - (p["qty"] * p["entry_price"] + p["entry_fee"])
        t = {
            "id": p["id"], "coin": coin, "strategy": p["strategy"], "regime": p["regime"],
            "entry_time": p["entry_time"], "exit_time": str(when),
            "entry_price": round(p["entry_price"], 6), "exit_price": round(px, 6),
            "qty": p["qty"], "pnl_gbp": round(pnl, 2),
            "r_multiple": round(pnl / p["risk_gbp"], 2) if p["risk_gbp"] else None,
            "fees_gbp": round(p["entry_fee"] + fee, 2), "exit_reason": reason,
        }
        self.trades.append(t)
        return t


# ---------------------------------------------------------------- risk
def new_day_check(acct: Account, when: pd.Timestamp, prices: dict):
    day = when.strftime("%Y-%m-%d")
    if acct.day != day:
        acct.day = day
        acct.day_start_equity = acct.equity(prices)


def entries_allowed(acct: Account, prices: dict) -> tuple[bool, str]:
    eq = acct.equity(prices)
    if acct.halted:
        return False, f"halted: {acct.halt_reason}"
    if eq < acct.day_start_equity * (1 - C.DAILY_LOSS_LIMIT):
        return False, "daily loss limit hit"
    if len(acct.positions) >= C.MAX_POSITIONS:
        return False, "max positions"
    return True, ""


def kill_switch(acct: Account, prices: dict, when) -> list:
    if acct.halted:
        return []
    if acct.equity(prices) < C.START_CAPITAL_GBP * (1 - C.KILL_SWITCH_DRAWDOWN):
        out = [acct.sell(c, prices[c], when, "kill switch") for c in list(acct.positions)]
        acct.halted, acct.halt_reason = True, f"equity below -{C.KILL_SWITCH_DRAWDOWN:.0%}"
        return out
    return []


# ---------------------------------------------------------------- stops
def check_stops(acct: Account, coin: str, bars: pd.DataFrame, when_fmt=str,
                bar_len=pd.Timedelta(hours=1)) -> dict | None:
    """Walk bars (oldest first) that happened since the last check; fill the
    stop if a bar's low touched it (at the open if it gapped through)."""
    p = acct.positions.get(coin)
    if not p:
        return None
    for ts, b in bars.iterrows():
        if pd.Timestamp(ts) + bar_len <= pd.Timestamp(p["entry_time"]):
            continue
        if b["low"] <= p["stop"]:
            fill = min(b["open"], p["stop"])
            return acct.sell(coin, fill, when_fmt(ts), "stop")
    return None


# ---------------------------------------------------------------- signals
def decide(acct: Account, bars4: dict, reg: str, bar_time) -> tuple[list, list]:
    """On a freshly closed 4h bar: returns (exits, entries).
    exits:   [(coin, reason)]
    entries: [(coin, stop, strategy)]  -- filled at the next price
    """
    exits, entries = [], []
    feats = {c: features(df) for c, df in bars4.items() if len(df) > C.REGIME_EMA_SLOW}

    for coin, p in acct.positions.items():
        f = feats.get(coin)
        if not f:
            continue
        p["last"] = f["close"]
        if p["strategy"] == "trend":
            # trailing stop ratchets up, never down
            p["stop"] = max(p["stop"], f["close"] - C.TREND_STOP_ATR * f["atr"])
            if f["close"] < f["ll"]:
                exits.append((coin, "trend exit: 2.5-day low"))
        elif p["strategy"] == "meanrev":
            held = (pd.Timestamp(bar_time) - pd.Timestamp(p["entry_time"])) / pd.Timedelta(hours=C.BAR_HOURS)
            if f["close"] >= f["bb_mid"]:
                exits.append((coin, "meanrev target: back to average"))
            elif held >= C.MR_MAX_BARS:
                exits.append((coin, "meanrev time stop"))

    for coin, f in feats.items():
        if coin in acct.positions:
            continue
        if C.ENABLE_TREND and reg == "trend_up" and f["close"] > f["hh"] and f["close"] > f["ema_slow"]:
            entries.append((coin, f["close"] - C.TREND_STOP_ATR * f["atr"], "trend"))
        elif C.ENABLE_MEANREV and reg == "range" and f["rsi"] < C.MR_RSI_ENTRY and f["close"] < f["bb_lo"]:
            entries.append((coin, f["close"] - C.MR_STOP_ATR * f["atr"], "meanrev"))
    # strongest signals first: biggest breakout / deepest oversold
    entries.sort(key=lambda e: (feats[e[0]]["close"] / feats[e[0]]["hh"]) if e[2] == "trend"
                 else (100 - feats[e[0]]["rsi"]) / 100, reverse=True)
    return exits, entries
