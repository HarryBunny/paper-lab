# Bunny Paper Lab: paper trading report

> Paper money only. Simulated fills at Kraken Pro Tier 1 taker fees (0.80% a side) plus slippage.
> A one-week result is an anecdote, not evidence. See the backtest section before deciding anything.

**Window:** 2026-11-24T11:32Z → 2026-12-01T11:32Z (running)  
**Last update:** 2026-11-24T11:32Z  
**Market regime:** trend_down

| | Value | Return |
|---|---:|---:|
| Bot (paper) | £1,000.00 | +0.00% |
| Buy & hold, equal-weight basket | £991.17 | -0.88% |
| Buy & hold, BTC only | £991.50 | -0.85% |

Max drawdown 0.0% · closed trades 0 · win rate —% · profit factor — · avg —R · fees paid £0.00

## Open positions

None, all cash.

## Closed trades

None yet.

## Strategy cards

**TREND (5-day breakout):** buy a coin breaking its 5-day high while BTC is in an uptrend.  
- Edge: herding and slow reaction to news keep trends running; late buyers pay it.  
- Rules: entry on 4h close above 30-bar high and above 200-bar EMA; stop 2.5×ATR, trailed; exit on a 15-bar low.  
- WHY THIS COULD FAIL: choppy, sideways markets; every false breakout costs ~1.8% in fees and slippage.

**MEANREV (oversold bounce):** buy a sharp dip when BTC is range-bound.  
- Edge: forced sellers (liquidations, panic) push price below fair value; patient buyers get paid.  
- Rules: RSI(14) < 30 and close below lower Bollinger band (20, 2σ); stop 2×ATR; exit at the 20-bar average or after 2 days.  
- WHY THIS COULD FAIL: a 'dip' that's actually the start of a crash.

**In a BTC downtrend the bot holds cash.** No shorting, no leverage.

## Event log

- `2026-11-24 11:32Z` 🔎 data: LINK 1h: 168 zero-volume bar(s)
- `2026-11-24 11:32Z` 🔎 data: LINK 4h: 4 zero-volume bar(s)
- `2026-11-24 11:32Z` 🔎 data: ADA 1h: 184 zero-volume bar(s)
- `2026-11-24 11:32Z` 🔎 data: ADA 4h: 2 zero-volume bar(s)
- `2026-11-24 11:32Z` 🔎 data: XRP 1h: 3 zero-volume bar(s)
- `2026-11-24 11:32Z` 🔎 data: SOL 1h: 1 zero-volume bar(s)
- `2026-11-24 11:32Z` 🔎 data: ETH 1h: 3 zero-volume bar(s)
- `2026-11-24 11:32Z` 🧭 Regime: — → **trend_down**
- `2026-11-24 11:32Z` 🟢 Lab started with £1,000 paper cash. Ends 2026-12-01T11:32Z.
