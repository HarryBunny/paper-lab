# Round 2 research digest (24 Nov 2026)

Five independent researchers looked at this. The digest has a section for each report. Evidence grades: **A** means tested with costs on out-of-sample data, **D** means a boast or promo.

---

## R1. Ideas other than trend-following and dip-buying

**Bottom line:** nothing here has grade-A evidence. Anything that trades often dies at 0.5–0.8% per side.

### Idle cash in GBP savings
- **Grade A** (arithmetic).
- UK Bank Rate is 4%, and the best easy-access accounts pay 4.75–5.26%.
- Stablecoin "rewards" on Kraken pay 2–6%. They are not FSCS-protected, Kraken calls them high-risk, and converting into them is a taxable disposal.
- Action: credit cash with about 4% a year in every backtest.

### Volatility-scaled exposure (B−)
- Man AHL: scaling BTC to a 30% volatility target added about 0.4 to the Sharpe ratio, 2012–2024. No costs were included.
- Johansson & Boyd (Stanford, 2024) found something similar.
- It needs a no-trade band of about 10–15 percentage points, otherwise fees eat it.

### Threshold rebalancing between BTC and GBP cash (C+)
- Bands of 10–20 percentage points; about 4–8 rebalances a year.
- Theoretical premium: about 3–4% a year at 50/50. Costs: about 0.3–1% a year.
- It lags in bull markets.
- Sources: Quantpedia 2021 (no costs); Shrimpy (sells bots; found 15% bands best).

### BTC/ETH rotation (C−)
- No credible backtests found.
- Every switch is a taxable disposal, and coming back within 30 days triggers the 30-day matching rule.

### Sentiment and positioning filters (C− to D)
- ETF flows follow price rather than lead it (DWF Labs, 694 days: correlation 0.03 with the next 5 days).
- Funding rates explain under 2% of next-period returns.
- Fear & Greed: only promotional evidence.

### On-chain valuation signals (D)
- Thresholds such as MVRV and Puell have decayed and lose out of sample (Quantpedia/Molnar Oct 2026; Shelton 2024).

### Calendar effects (D)
- Not persistent, and costs wipe them out.

### UK tax
- Every sale, and every crypto-to-crypto swap including swaps into stablecoins, is a capital gains disposal.
- HMRC matching rules apply in order: same day, then the next 30 days, then the section 104 pool.
- The annual allowance is £3k, so tax is likely nil on £1k. The real burden is the records.

---

## R2. Live track records

### Overall finding
- No verified small retail crypto bot showed an after-fee profit over 12 months or more.
- Live records found ran from weeks to 6 months and were mostly break-even or losing.

### Backtests vs live results
- **Quantopian study (A):** 888 strategies, each with at least 6 months out-of-sample. Backtest Sharpe explained under 2.5% of live variance. More backtesting meant a bigger gap. Volatility and drawdown predicted live results better than Sharpe did.
- **BIS (A):** most retail crypto app users lost money on bitcoin.
- **CMU CHI 2024 (A):** copy-trading leaderboards can be gamed, and followers lose.
- **Rule of thumb:** live returns are about half the backtest at best. If the edge per trade is smaller than costs, expect a loss.
  - The ProRealCode 5-year self-report put live at 10–20% worse.
  - The dev.to post-mortem put live at 50–70% of backtest.

### Bitwise BITC ETF (B)
- The best live analogue: a 10/20-day EMA trend switch in BTC futures, live since Mar 2023.
- About +124% over 3 years, −15.5% over 1 year, roughly flat in 2026 against a category average of −31.6%. Worst year −20.6%.
- It suffers whipsaw.

### Ideas to test
- Simulated maker fills: limit order at the next open, filled only if the bar touches it, 0.40% fee.
- Volatility-scaled position size with a 20–25 point no-trade band.
- Lookback ensemble giving 0/25/50/75/100% exposure.
- Trend-filtered DCA.
- Use 5+ years of data, log every variant tried, and prefer drawdown over Sharpe as the selection metric.

---

## R3. X round 2: quant voices

### Zarattini/Pagani/Barbon, "Catching Crypto Trends" (B)
- Design:
  - Long-only Donchian (breakout) ensemble with lookbacks of 5, 10, 20, 30, 60, 90, 150, 250 and 360 days.
  - The exit is the midpoint of the range and only ever ratchets up.
  - Positions are sized to 25% volatility.
  - Up to 20 coins from a survivorship-free universe.
- About 18% CAGR at 0.10% cost, Sharpe over 1.5 (2015–2025). Costs tested up to 0.5%.
- Lab B is this design with fewer lookbacks.
- Two of the authors run Concretum Group, a commercial research firm.

### Rob Carver, practitioner with costs (B)
- Keep at least 3 variations of each rule and lean toward the slower ones.
- Spend no more than about a third of the expected Sharpe on costs. Single-rule, single-instrument Sharpe is only about 0.24–0.40.
- Implication: about 2–4 round trips per coin per year at taker fees, about double at maker.

### Lookback sensitivity
- Grayscale 2023 (C, no fees): a single 50-day price-vs-MA rule on BTC is fairly insensitive to lookback; crossovers are sensitive.
- Cointelegraph (D): MA rankings flip year to year.
- **Standard fix:** an ensemble of lookbacks (100/150/200/250) used as a vote or as fractional exposure. Judge it by the median result.

### Mroziewicz & Ślepaczuk, arXiv 2602.10785 (B−)
- Out-of-sample EMA test on BTC. It roughly matched buy-and-hold with a lower drawdown.
- Cost break-even was about 0.4% per transaction.
- Blending with buy-and-hold roughly halved the drawdown.

### Man AHL (C)
- Trend-following on crypto works, but the benefit peaks at 10–15 coins.
- Average correlation is about 0.6, so 6 coins are worth only about 2–3 independent bets.

### Other points
- **@macrocephalopod (C):** a single market's trend Sharpe is about 0.2. Blend long-run volatility into vol-sizing.
- **XBTO trend fund (B, live):** lost in choppy 2025, then gained 13% in Jan 2026, largely from shorting.
- **BTC realised volatility at multi-year lows, 2025–26 (C):** trends are smaller relative to fixed fees. Cap inverse-vol weights at 35–40% per coin.
- **Vol-scaled vs raw momentum (C, arXiv 2602.11708):** Sharpe 1.83 vs 0.5–0.65; drawdown −16% vs −35%.
- **Monthly or weekly checks of the regime filter (D, idea only):** the cheapest way to reduce whipsaw.

### Realistic expectation for long-only, 6-coin spot at 0.4–0.8% costs
- Well below buy-and-hold in bull years.
- Much smaller losses in bear years.
- Sharpe about 0.3–0.7. This is judgement, not a sourced figure.

---

## R4. Open-source bot communities

### Backtesting and validation
- **Freqtrade docs (A):**
  - The backtester fills at the requested price with no slippage.
  - Signal exits fill at the next candle's open.
  - Only forward testing (dry-run) validates a strategy.
  - Its lookahead-analysis tool truncates the data and compares results. Biased strategies fall apart.
- **Freqtrade FAQ (A−):** 12 trades say nothing.
- **Jesse Monte Carlo (A−):** if the real backtest beats 95% of shuffled runs, it is likely overfitted. Near the median is ideal.
- **Brook Miles (B):** strategies averaging under about 0.5% net profit per trade usually lose live.

### Kraken specifics (A)
- The API returns only 720 candles.
- Kraken publishes free full-history OHLCVT download files, to 30 Jun 2026, updated quarterly.
- Fees are confirmed at Tier 1 0.40/0.80, Tier 2 0.30/0.60 (from $2.5k 30-day volume), Tier 3 0.22/0.38. Changed 9 Jul 2026.
- Post-only orders are supported.
- QuantConnect (A): order modification isn't supported, so you have to cancel and replace. A bot must persist its state and reconcile after outages.

### Community experience
- **Hummingbot (B−):** grid and market-making bots win in ranges and get hurt in trends.
- **Post-mortems (C):** the repeated failures are:
  - re-entries in chop,
  - correlated coins hitting their stops together,
  - trailing stops cutting winners early.

### Robustness checklist before trusting Lab B
1. Use full-history data, 2018–2026, reported per year.
2. Check for lookahead by truncating the data, and allow proper warm-up.
3. Sweep fees at 0.25, 0.4, 0.6 and 0.8%, plus 0.1–0.2% slippage. Also test maker-first execution with no-fill handling.
4. Compare with simpler baselines: an equal-weight basket gated by BTC's 200-day MA, and BTC-only with the same filter.
5. Check parameters form a plateau rather than a peak.
6. Run a walk-forward test.
7. Run Monte Carlo: shuffle trade order 1,000 times, and run 100 candle-noise variants.
8. Report trade count and the confidence interval on expectancy. Under 30 trades is inconclusive.
9. Measure the most positions open at once, the worst single day, and the effective number of independent bets.
10. Operational checks: persist state, a stale-data guard (no new bar in 26 hours), a log of intended vs actual fills, and heartbeat alerts.

### New ideas to test
- Ratcheting midpoint stop.
- Wider lookback ensemble.
- Maker-only execution.
- No-trade band on resizing.
- Core-satellite: 30–50% buy-and-hold plus a trend sleeve.
- Re-entry cooldown.

---

## R5. Forums

Sources: BitcoinTalk, Elite Trader, MoneySavingExpert (MSE), the HMRC Community forum and BabyPips. QuantSE, Trade2Win, Forex Factory and Wilmott were blocked.

**Overall:** no forum source had a verified, cost-inclusive live record for any retail crypto bot. The consensus is consistent with Lab B's design, but none of it shows a profit.

### Trading lessons
- **Commission:** Goomboo's journal (BitcoinTalk, 2013; C) showed a gross +2,407% falling to +571% once a 0.6% commission was included.
- **Timeframe:** veterans moved from hourly bars to daily or 2-hour bars to cut whipsaw (C).
- **Start date:** results depended heavily on when the test began. Starting one month later turned a gain into breakeven or −33% (C). → Test: run rolling start dates and report the spread of results.
- **Win rate and filters:** trend systems win only 30–40% of the time. Extra filters such as "only after a new N-day high" usually made things worse (C). → Test: ablate (remove) Lab B's filter, buffer and ensemble layers one at a time.
- **Losing streaks:** size positions to survive 20–30 losses in a row (B, arithmetic).
- **How bots die (Peanut, Elite Trader 2024–26; C):** strategy-hopping, manual overrides, delisted coins, API blocks. Also notes that ~5 trades a year doesn't need an algorithm; it could be semi-manual.
- **Other markets:** test the same rules on non-crypto data such as index ETFs and gold (C).
- **Edge vs fees:** an edge about the size of the taker fee is worthless (B). → Require gross edge per trade to be several times the ~1.6% round-trip cost.

### Kraken specifics
- **Fees (A, official):** a minimum fee applies on small trades, and cancelled orders are free. → Model Kraken's minimum order size and minimum fee for small per-coin orders.
- **Thin GBP order books (B, news):** a bot dumped BTC/GBP about 10% below market in 2019, and ETH flash-crashed in 2021. → Never use market or stop-market orders on GBP pairs. Use post-only limit orders with a price collar, plus a data sanity check.

### UK tax
- **Pooling and matching (A–B; MSE, consistent with the HMRC manual):** each coin has its own pool. Sales match same-day purchases first, then purchases in the next 30 days, then the s104 pool. Whipsaw re-entry within 30 days distorts the taxable result.
- **Partial sells (C):** frequent partial sells make pooling messy. → No mid-trade rebalancing; size once at entry.
- **Loss timing (B, HMRC forum):** a UK bot user had gains in 2020–22, then a £35.7k loss in 2022/23. Capital losses can't be carried back, and they must be claimed to be carried forward.
- **£50k reporting trigger (A; LITRG, MSE):** gains must be reported if total disposal proceeds exceed £50k, even if gains are under the allowance. The old bot's turnover was in that range; Lab B's would not be.
- **CARF (A, gov.uk Aug 2026):** UK crypto providers report customer data from Jan 2026, and HMRC receives it from 2027. → Keep a ledger that reconciles with Kraken.
- **Rates (A):** capital gains tax allowance £3k; rates 18% and 24%. Income treatment as trading is exceptional.

---

## Main session: rule search (research/2026-11-24-optimise/, script research/optimise.py)

### Setup
- 195 daily long-only rules across BTC, BTC+ETH and all coins, in GBP.
- Costs: 0.80% plus slippage. Fills at the next day's open.
- Tuned on 24 Nov 2024 – 23 Nov 2026, then tested on unseen 2018 – Nov 2024.

### Results in the tuning window
- 24 of 195 rules were profitable over the window.
- Only 4 were profitable in both years. All 4 were "own-coin MA" rules (30/50/75-day) on BTC+ETH.
- None were consistently profitable quarter to quarter: the best had 4 of 9 quarters up.

### Best rule: own 50-day MA ±2%, BTC+ETH

| Period | Rule return | Rule max drawdown | Buy & hold return | Buy & hold max drawdown |
|---|---|---|---|---|
| Tuning window | +10.3% | −34% | −46.2% | −59% |
| Unseen 2018–2024 | +1,052% | −55% | +1,021% | −76% |

- 20 trades: 7 winners averaging +18%, 13 losers averaging −7%.
- Unseen years: 2018 −35%, 2022 −36%.

### Caveat
- The other 3 survivors did much worse than buy-and-hold on the unseen period.
- Finding 4 survivors in 195 rules is consistent with chance.
