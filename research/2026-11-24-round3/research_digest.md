# Round 3 research digest: methods other than trend/moving-average holding

Grades run from A (out-of-sample with costs, or audited) down to D (narrative or promotional).

## R3-4: Professionals and industry figures

### Where professional profits actually came from
The sources point to five places:
1. Market making. It needs rebates, low latency and a perp hedge. In the October 2025 auto-deleveraging ($20bn liquidated), market makers were left holding naked spot (BitMEX, B/C).
2. Funding and basis carry. Yields were about 20% in January 2024 but fell to roughly 2–4% in 2025–26, below T-bills (Fortune/Bloomberg, CoinDesk, B).
3. Venture capital and private or discounted token allocations. The Jump/Terra SEC settlement was about $123m (SEC, B).
4. Concentrated long exposure that survived drawdowns:
   - Multicoin: +9,281% since 2017, but lost 91% in 2022.
   - Pantera: essentially early buy-and-hold.
5. Quant directional strategies, mostly trend.
   - 2024 (Galaxy VisionTrack): quant directional +53.7%, market-neutral +18.5%, while BTC rose about 120% (B/C).
   - 2025 to August 2026: quant directional +30.2%, market-neutral +20%, fundamental −25%. Small funds closed quietly, which is survivorship bias (The Block, B).

### Fund index check
HFR crypto index, 5 years to February 2025: +51% a year at about 60% volatility. That is roughly the same risk profile as just holding crypto.

### Closed to a £1k UK spot account
- Market making
- Carry (FCA retail derivatives ban)
- Cross-exchange arbitrage
- Venture capital allocations
- Options volatility trading
- Leveraged premium arbitrage

### Open to a £1k UK spot account
These are risk and cost management, not an edge:
- Low-turnover long/flat positions
- Maker-only orders
- Volatility sizing
- Periodic accumulation or rebalancing
- At most one slow macro filter
- Attributing results properly (Moontower)

### Macro and liquidity figures
- **BTC vs global M2.** Levels correlate, but daily return correlation is only about 0.02, and the best lag gives r = 0.16. The rolling 180-day correlation went from 0.94 to −0.12 by late 2025. M2 hit a record in 2026 while BTC fell (CryptoSlate, C).
- **Out-of-sample indicator study (Quantpedia, October 2026, 2011–26, B).** MVRV, Mayer, Pi-cycle and Puell were silent at the October 2025 top. M2 and the yield curve are sign-unstable.
- **BG Lab on-chain rules (B, vendor).** Rules frozen in March 2024 and tested on 2024–26:
  - None passed the deflated Sharpe ratio test.
  - A plain 50-day moving average did as well.
  - The fee assumed was 0.1%.
- **Pundits (D).** PlanB's stock-to-flow failed. Pal (calling >$140k by July 2025) missed. Hayes and Woo make calls, not rules.

### Copy trading and prop firms
- **Copy-trading leaderboards (CMU CHI 2024, A).** Rankings don't predict future returns. Leaders earn 50–75% of their money from commissions, and the rankings can be gamed.
- **Prop-firm challenges (FPFX, B).** About 7% of 300,000 accounts got any payout. The firms make their money from challenge fees.

### Carver's "speed limit" on costs
- Rule: keep costs under one third of the expected Sharpe ratio before costs (B).
- At a 1.6% taker round trip, that allows roughly 3 round trips a year, or about 6 with maker-only orders.
- Anything trading hourly is uneconomic at these fees.

### Testable macro rules to pre-register (FRED data)
1. **Global M2 3-month impulse.** Hold BTC while it's positive, checked monthly. Include the publication lag.
2. **US net liquidity.** Net liquidity = WALCL − WTREGEN − RRPONTSYD×1000. Hold BTC while its 4-week change is positive, capped at about 6 switches a year.
3. **How to judge them.** Compare against a random on/off null with the same time in the market, and use the deflated Sharpe ratio. Statistical power is low: about 107 monthly observations.

### Red flags
- Commercial interests: Hayes (Maelstrom), Pal (Real Vision), Saylor (MSTR), Davey (courses), and data vendors.
- Lags fitted in-sample.
- Correlations measured on price levels rather than returns.
- Return figures that include side pockets.

## R3-5: Prediction, machine learning and sentiment

**Bottom line:** nothing published at a daily or hourly horizon survives 0.8–1.6% round-trip costs. The best evidence is for weekly-to-fortnightly cross-sectional momentum among large coins, and for vol-scaled sizing (which improves risk, not return). Both were measured at costs 2–8× lower than ours, on long-short books of hundreds of coins.

### Weekly and fortnightly momentum
- **Liu, Tsyvinski & Wu (J. Finance 2022, A):** three factors (market, size, momentum) explain the cross-section. These are gross, long-short returns, with small coins dominating.
- **Liu & Tsyvinski (RFS 2021, A/B):** BTC time-series momentum: +1 sd of return this week → +3.16% next week. Google searches: +1 sd → +1.84%. Mostly in-sample.
- **Fieberg et al., CTREND (JFQA 2025, A):**
  - Rolling 52-week out-of-sample test, 55,296 designs, costs of 30/40 bp.
  - Weekly continuation, not reversal, with alpha lasting up to 4 weeks.
  - Adding a validation sample cut the median Sharpe from 1.47 to 1.19.
  - The signals are moving-average based, so this is close to the out-of-scope line.
- **Dobrynskaya (B):** momentum peaks at a 2-week ranking with a 2-week hold, and reverses after 4–6 weeks.
- **Fičura (WP, B/C):** weekly REVERSAL only shows up in small illiquid coins. Large coins show weekly MOMENTUM. The previous week's close/high ratio predicts positively.

### Reversal and illiquidity
- **Bianchi et al. (Riksbank WP, B):** daily reversal is an illiquid-coin liquidity premium. The value-weighted version fails after costs.
- **Zhang & Li (B):** Amihud illiquidity is useless for timing the major coins.

### Sentiment and search
- **Guidolin & Ionta (JIFMIM 2026, B):** a Google search shock (search volume minus its 4-week average) gave an out-of-sample R² of 2.79% across 382 weeks. Long-short returned about 0.73%/week, gross only.

### Machine learning and statistical models
- **Review of 23 studies (B):** no model reliably beats the naive "price stays the same" forecast. LSTM direction accuracy is about 52%.
- **Walk-forward hourly ML (B):** profitable gross, but loses at just 10 bp of costs.
- **Vol timing (arXiv 2501.12841, B):** GARCH/DCC volatility timing beats an equal-weight split out of sample with costs. Simple estimators work best, and a turnover penalty helps.
- **Man Group (C):** a 30% vol target on BTC adds about 0.4 Sharpe.

### LLM and AI trading
- **LLM news signals are contaminated by memorisation:** insignificant after the model's training cutoff (Gao et al., B).
- **Alpha Arena (D):** n=1, 12–17× leverage, 4 of 6 models lost.

### Decay from paper to live
- **McLean & Pontiff (A):** returns fall about 26% out of sample and about 58% after publication.
- **Quantopian (B):** backtest Sharpe barely predicts live Sharpe.
- **Rule of thumb:** halve any backtest Sharpe, and require the edge to be at least 2× costs.

### Free data
- **alternative.me Fear & Greed:** full history, no key needed. Blocked by our sandbox; it may be reachable from GitHub Actions.
- **Google Trends:** manual export only. Each request is rescaled, and the official API requires an application.

### Shortlist of signals to test
1. **Vol-scaled exposure:**
   - Weight = min(1, 0.40/σ), with σ from an EWMA (λ 0.94).
   - Trade only if the weight changes by more than 0.20 AND at least 7 days have passed since the last trade.
   - Use maker orders.
   - Benchmark against a CONSTANT weight equal to the strategy's average exposure.
2. **Weekly cross-sectional momentum across the 6 coins:**
   - Every Monday, rank by 14-day return and hold the top 2 at 50/50.
   - Keep a coin until it falls to rank 4 or below.
   - Benchmark: an equal-weight basket rebalanced on the same schedule.
3. **Google attention shock (weekly):** low confidence. At about 20–25 switches a year, fees are likely to kill it.

### Safeguards
- A trial ledger.
- Deflated Sharpe ratio and probability of backtest overfitting (PBO).
- Expanding walk-forward, plus a locked holdout.
- Purged cross-validation for any fitted model.
- Base case at maker 0.40%; stress case at taker 0.8% + 0.1%, plus maker no-fill risk.
- Signal on the close, trade at the next open.
- Treat survivorship as an upper bound.
- Report results per year.
- Use exposure-matched and random benchmarks.

## R3-3: Event-driven and flow edges

None of these has grade-A evidence.

### Listings: drop (C)
- The jump happens within minutes of the announcement.
- The effect has faded since 2023: The Tie (vendor) found it reverts in about 2 weeks.
- None of our coins are new listings anyway.

### Token unlocks (C/D)
- Keyrock (a market maker), studying 16k unlocks, found pressure starts about 30 days before and reverts about 14 days after.
- Possible filter: XRP releases up to 1bn tokens from escrow on the 1st of each month, and LINK unlocks roughly quarterly. Measure the XRP-minus-BTC excess return over windows [−5,−1], [0,+2] and [+3,+14] days around each date.

### Macro releases (FOMC, CPI, NFP): no drift (B)
- NY Fed SR1052 and a KSE thesis (2020–25) found pre/post drift of only 0.1–0.6%. The only clear effect is higher volatility on the day itself.
- Use these dates as caution windows only.

### ETF flows (C/D)
- FalconX (Jan–Oct 2024): +1.2% peak response on days 3–4. This doesn't survive taker costs.
- Farside, the source for flow data, refused our fetch.

### Options-expiry week (C)
- Plastun et al., JRFM 2022 (2018–21, before costs): expiry weeks averaged +2.73% vs +0.50% for normal weeks, 65% positive, Sharpe 1.05.
- Deribit monthly options settle at 08:00 UTC on the last Friday of the month.
- Our 2022–26 data is a clean out-of-sample test (about 59 events).

### Liquidation washouts (C/D)
- K33: mean 30-day return after the top 5% of liquidation events was +0.78%, against a typical 5.9% (median −1.1%). That argues against buying the washout.
- Brunel WP: ETH bounced +3.96% the day after extreme down days (pre-2019 data).
- A volatility-scaled crash proxy can be tested on our own candles.

### Stablecoin mints and exchange flows: drop (C)
- The effect lasts minutes to hours and needs paid data.

### Weekend and session timing
- No return edge.
- Execution tip: trade during the London/New York overlap, and avoid weekend market orders on thin GBP books.

### Shortlist to pre-register
1. **Expiry-week long (BTC; ETH as robustness check):** buy Monday 00:00 UTC, sell Friday close (or 07:00 UTC). Pass test: net >0 at 1.6% round-trip cost, t≥2 on 2022–26, and ≥60% of weeks positive.
2. **XRP/LINK supply-event filter:** an overlay that removes trades around these dates.
3. **Vol-scaled washout bounce:**
   - Signal: the coin falls by ≥3 standard deviations (sd from the prior 30 days) and BTC falls by ≥2 sd on the same day.
   - Exit at day t+5 or a +6% target.
   - Also test a version that waits for a higher close first.
   - Set thresholds on 2017–21, test on 2022–26.
4. **ETF flows:** marginal, and depends on getting the data.

### Red flags
- Samples are small (12–100 events), so correct for multiple testing.
- Most sources are vendors.
- Regime shifts since 2021.
- GBP noise.
- Events overlap.
- Lookahead traps: daylight-saving changes, revised data, inferred dates.

### Main-session quick check: options-expiry-week long (GBP daily, Coinbase)
- **Setup:** buy at Monday's open and sell at Friday's close, in the week containing the last Friday of the month. Round-trip cost 1.6% plus slippage.
- **BTC, 2018–21 (the paper's own period):**
  - Expiry weeks: mean −0.19%, 48% up, t = −0.15.
  - Other weeks: +1.24%.
  - **The paper's +2.73% does not reproduce.** Possible reasons: a different week definition, or the paper used USD data.
- **BTC, unseen 2022–26:** expiry weeks −0.27% (net −1.97%), 45% up.
- **ETH:** negative in both periods.
- **Verdict: drop.** The effect isn't present, even before costs.
