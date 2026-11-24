# Research round 1 (24 Nov 2026): what similar bots do, and the "Lab B" proposal

**Status: banked, not built.** The live 7-day test (24 Nov to 1 Dec 2026) runs unchanged.

## Method
1. **Independent research.** Two researchers worked separately, one on X and one on Reddit. Each graded every claim from A to D:
   - A: a reproducible test that includes costs and was checked on data it wasn't tuned on.
   - D: a boast with no proof.
   - Anyone selling a course, bot or affiliate deal was flagged.
2. **Collation.** A separate analyst combined the findings into themes, ranked by strength of evidence × fit for a £1k UK spot-only account.
3. **Testing on our own data.** The analyst tested the best-supported ideas on the cached hourly GBP candles in `backtest_results/data/`:
   - period 25 Mar 2025 to 23 Nov 2026, coins BTC, ETH, SOL, ADA and LINK;
   - four fee levels: 0.80%, 0.60%, 0.50% and 0.25% per side;
   - signals at each day's close, trades at the next day's open, plus slippage;
   - settings varied ±25% to check they don't only work at one value.
4. **Verification.** The main session checked the benchmark returns against the raw prices and re-ran the script from this folder. It reproduces exactly.

Reproduce from the repo root: `python3 research/2026-11-24/research_backtest.py`. The full tables are in `RESULTS.md` and `research_results.json`.

## Findings
- **Fees decide the result.** The 4h bot paid £389 in fees and lost £290. Before fees it was roughly flat.
- **Slow daily rules lost far less than holding or the current bot, but none clearly made money.** In this falling period, cash (0%) did about as well as anything.
- **Best rule:** daily breakouts, allowed only while BTC is above its 200-day average:
  - +5.3% / −15.8% at the best setting; −3% to +1% at other settings.
  - About 13 new positions and about £45 of fees a year.
  - Read it as a brake on losses, not a profit engine.
- **Mean reversion / dip-buying:** negative after fees in our data and in the stronger research. Drop it.
- **Funding carry, cross-sectional momentum, intraday rules, LLM/"AI" bots:** discarded. They don't fit a £1k UK spot account, or there's no evidence they work.

## Lab B proposal (to run as a separate £1,000 paper account, judged over months)
1. Daily bars, decisions at the 00:00 UTC close.
2. **Regime:** hold only while BTC's daily close is above its 200-day average. Switch on at +2% above the average, off at −2% below.
3. **Entries:** for each coin and each lookback N in {20, 50, 100} days, hold a share while the close is above the highest close of the previous N days.
4. **Exits:** each share sells when the close falls below the midpoint of its N-day range. That midpoint only ratchets up.
5. **Sizing:** inverse 60-day volatility, total exposure capped at 100%. Rebalance only if a weight is more than 10% off target.
6. **Removed:** mean reversion, 4h breakouts, and fixed 1%-risk sizing.
7. **Kill switch:** −20%, because the best version's worst drop was −16%.
8. **Benchmarks to beat over 6–12 months:** hold BTC; and hold BTC only while it's above its 200-day average (±2%).

## Things for Harry to verify himself (facts, not advice)
- **Kraken Pro:** your actual fee tier. Tier 2 is 0.30/0.60% at $2.5k 30-day volume or by assets held.
- **Coinbase Advanced:** your real UK GBP fees. Reported at 0.25/0.50% since 16 Sep 2026, unconfirmed; an affiliate site measured 0.40/0.60%. Also check which GBP pairs exist.

## Caveats
- Only 1.7 years of data, in a market that mostly fell.
- Five hand-picked survivor coins.
- The best numbers come from picking the best of several settings.
- Limit (maker) orders only fill about 55% of the time in the research.
- The rules were built after seeing this period's data, so this is not truly out-of-sample.
