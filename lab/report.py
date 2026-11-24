"""Writes REPORT.md (readable on GitHub) and state/summary.json (for the dashboard)."""
import json

import pandas as pd

from . import config as C


def stats(trades: list, equity: pd.Series, start: float) -> dict:
    pnl = [t["pnl_gbp"] for t in trades]
    wins = [p for p in pnl if p > 0]
    losses = [p for p in pnl if p <= 0]
    dd = (equity / equity.cummax() - 1).min() if len(equity) else 0.0
    return {
        "return_pct": round((equity.iloc[-1] / start - 1) * 100, 2) if len(equity) else 0.0,
        "max_drawdown_pct": round(dd * 100, 2),
        "trades": len(trades),
        "win_rate_pct": round(100 * len(wins) / len(pnl), 1) if pnl else None,
        "profit_factor": round(sum(wins) / -sum(losses), 2) if losses and sum(losses) < 0 else None,
        "avg_r": round(sum(t["r_multiple"] or 0 for t in trades) / len(trades), 2) if trades else None,
        "worst_trade_gbp": min(pnl) if pnl else None,
        "best_trade_gbp": max(pnl) if pnl else None,
    }


def write(acct, meta, prices, equity_csv, log_md):
    eq = pd.read_csv(equity_csv)
    s = stats(acct.trades, eq["equity"], C.START_CAPITAL_GBP)
    now_eq = acct.equity(prices)
    basket, btc = eq["bh_basket"].iloc[-1], eq["bh_btc"].iloc[-1]

    summary = {
        "lab": C.LAB_NAME, "start": meta["start"], "end": meta["end"], "ended": meta.get("ended"),
        "updated": eq["time"].iloc[-1], "regime": meta.get("regime"),
        "equity": round(now_eq, 2), "cash": round(acct.cash, 2), "fees_paid": round(acct.fees_paid, 2),
        "bh_basket": basket, "bh_btc": btc, "halted": acct.halted, "halt_reason": acct.halt_reason,
        "stats": s, "positions": acct.positions, "trades": acct.trades,
        "prices": prices, "equity_curve": eq.to_dict("records"),
        "assumptions": {
            "fee_per_side": C.FEE_RATE, "slippage": {**C.SLIPPAGE, "others": C.SLIPPAGE_DEFAULT},
            "risk_per_trade": C.RISK_PER_TRADE, "daily_loss_limit": C.DAILY_LOSS_LIMIT,
            "kill_switch": C.KILL_SWITCH_DRAWDOWN, "leverage": C.LEVERAGE, "shorts": C.ALLOW_SHORTS,
        },
    }
    with open("state/summary.json", "w") as f:
        json.dump(summary, f, indent=1, default=str)

    def gbp(x):
        return f"£{x:,.2f}"

    L = [f"# {C.LAB_NAME}: paper trading report", "",
         "> Paper money only. Simulated fills at Kraken Pro Tier 1 taker fees (0.80% a side) plus slippage.",
         "> A one-week result is an anecdote, not evidence. See the backtest section before deciding anything.", "",
         f"**Window:** {meta['start'][:16]}Z → {meta['end'][:16]}Z "
         f"{'(finished)' if meta.get('ended') else '(running)'}  ",
         f"**Last update:** {eq['time'].iloc[-1]}  ",
         f"**Market regime:** {meta.get('regime', '—')}"
         + (f"  \n**HALTED:** {acct.halt_reason}" if acct.halted else ""), "",
         "| | Value | Return |", "|---|---:|---:|",
         f"| Bot (paper) | {gbp(now_eq)} | {now_eq / C.START_CAPITAL_GBP - 1:+.2%} |",
         f"| Buy & hold, equal-weight basket | {gbp(basket)} | {basket / C.START_CAPITAL_GBP - 1:+.2%} |",
         f"| Buy & hold, BTC only | {gbp(btc)} | {btc / C.START_CAPITAL_GBP - 1:+.2%} |", "",
         f"Max drawdown {s['max_drawdown_pct']}% · closed trades {s['trades']} · "
         f"win rate {s['win_rate_pct'] if s['win_rate_pct'] is not None else '—'}% · "
         f"profit factor {s['profit_factor'] or '—'} · avg {s['avg_r'] if s['avg_r'] is not None else '—'}R · "
         f"fees paid {gbp(acct.fees_paid)}", ""]

    L += ["## Open positions", ""]
    if acct.positions:
        L += ["| ID | Coin | Strategy | Entry | Now | Stop | Unrealised |", "|---|---|---|---:|---:|---:|---:|"]
        for c, p in acct.positions.items():
            u = p["qty"] * (prices[c] - p["entry_price"]) - p["entry_fee"]
            L.append(f"| {p['id']} | {c} | {p['strategy']} | £{p['entry_price']:,.4f} | £{prices[c]:,.4f} | "
                     f"£{p['stop']:,.4f} | {gbp(u)} |")
    else:
        L.append("None, all cash.")
    L += ["", "## Closed trades", ""]
    if acct.trades:
        L += ["| ID | Coin | Strategy | Regime | Opened | Closed | P&L | R | Fees | Why |",
              "|---|---|---|---|---|---|---:|---:|---:|---|"]
        for t in reversed(acct.trades):
            L.append(f"| {t['id']} | {t['coin']} | {t['strategy']} | {t['regime']} | {t['entry_time'][:16]} | "
                     f"{t['exit_time'][:16]} | {gbp(t['pnl_gbp'])} | {t['r_multiple']} | {gbp(t['fees_gbp'])} | "
                     f"{t['exit_reason']} |")
    else:
        L.append("None yet.")
    L += ["", "## Strategy cards", "",
          "**TREND (5-day breakout):** buy a coin breaking its 5-day high while BTC is in an uptrend.  ",
          "- Edge: herding and slow reaction to news keep trends running; late buyers pay it.  ",
          "- Rules: entry on 4h close above 30-bar high and above 200-bar EMA; stop 2.5×ATR, trailed; exit on a 15-bar low.  ",
          "- WHY THIS COULD FAIL: choppy, sideways markets; every false breakout costs ~1.8% in fees and slippage.", "",
          "**MEANREV (oversold bounce):** buy a sharp dip when BTC is range-bound.  ",
          "- Edge: forced sellers (liquidations, panic) push price below fair value; patient buyers get paid.  ",
          "- Rules: RSI(14) < 30 and close below lower Bollinger band (20, 2σ); stop 2×ATR; exit at the 20-bar average or after 2 days.  ",
          "- WHY THIS COULD FAIL: a 'dip' that's actually the start of a crash.", "",
          "**In a BTC downtrend the bot holds cash.** No shorting, no leverage.", "",
          "## Event log", ""]
    with open(log_md) as f:
        L += f.read().splitlines()[-60:][::-1]
    with open("REPORT.md", "w") as f:
        f.write("\n".join(L) + "\n")
