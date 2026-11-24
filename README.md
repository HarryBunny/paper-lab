# Bunny Paper Lab

A 7-day automated **paper** trading test: £1,000 of fake GBP trading crypto on real, live prices.
No exchange account, no API keys, and no real money anywhere in this repo.

## What it does

Every hour (GitHub Actions, `.github/workflows/paper-bot.yml`):

1. Pulls closed candles for BTC, ETH, SOL, XRP, ADA and LINK in GBP from Kraken's public API (falling back to Coinbase).
2. Works out the **market regime** from BTC's 4-hour chart: `trend_up`, `range` or `trend_down`.
3. Runs only the strategy that fits that regime:
   - **trend_up:** TREND, buy 5-day breakouts with a trailing ATR stop.
   - **range:** MEANREV, buy oversold dips below the lower Bollinger band and exit at the average.
   - **trend_down:** hold cash.
4. Checks stops against every hourly candle since the last run, so a missed hour can't hide a stop-out.
5. Commits `state/` and `REPORT.md` back to the repo.

After 7 days it closes everything and stops by itself.

## Risk rules (cautious)

| Rule | Setting |
|---|---|
| Risk per trade | 1% of equity (about £10), fees included |
| Max per position | 25% of equity, max 4 positions |
| Daily loss limit | -3% on the UTC day: no new entries until tomorrow |
| Kill switch | -10% from £1,000: close everything and stop for good |
| Leverage / shorting | none / none |

## Costs (checked 24 Nov 2026)

Kraken Pro Tier 1 taker fee is **0.80% a side**, plus 0.05–0.10% slippage. That makes a round trip cost about 1.7–1.8%, so the bot has to catch moves bigger than that just to break even. This is the biggest hurdle for small accounts.

## Files

| File | What |
|---|---|
| `REPORT.md` | live scoreboard: bot vs buy-and-hold, open positions, every trade with ID, event log |
| `state/` | account, equity curve (CSV), log, `summary.json` |
| `backtest_results/BACKTEST.md` | the same engine run over about 2 years of history, with stress tests |
| `lab/config.py` | every setting. **Don't change it mid-test.** |

## Running by hand

```
pip install -r requirements.txt
python backtest.py 730      # backtest
python run_live.py          # one live tick
python tests/sim_test.py    # offline self-test on synthetic prices
```
