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

## R3-2: Market-making, grids and limit-order ladders

### Market-making at the touch: not viable
- **Adverse selection (B+):** "The Market Maker's Dilemma" (Oxford, 233k live Binance orders) found that resting orders fill exactly when the next move goes against them. This held even with a rebate.
- **Negative fill drift (B):** DeLise measured about −0.45 ticks after each fill.
- **Moontower (C+):** retail is the slowest quoter in the book, so it is the one that gets picked off.
- **Fees vs spread:** Kraken's GBP spreads are almost certainly far below our 40 bp maker fee, so the quoted spread can't be captured.

### What a grid really is
- **A short-volatility trade (B−):** Quantpedia notes that a grid is the mirror image of delta-hedging a short straddle.
- **Zero edge on a random walk (B):** a National Taiwan University paper proves a static grid has zero expected value on a random walk, and negative once fees are added. Its 60–70% IRR came from bull-market exposure at 0.08% fees.
- **Closest comparable test (C):** cart0ne (dev.to, July 2026) used Kraken's 0.40% fee and found:
  - lost less than holding in a bear month, but still lost;
  - sideways months returned under 1%;
  - captured about 10% of a +207% bull month.
  - The author's verdict: "an airbag, not an engine".

### Fees and spacing
- **Kraken (A):** maker fee is 0.40% at Tier 1, 0.30% at Tier 2 and 0.22% at Tier 3 ($10k).
- **Profit per day:** roughly (σ²/s²)(s/2 − f), where σ is daily volatility, s the grid step and f the fee. Steps need s > 2f to profit, and the optimum is near s ≈ 4f: about 1.6% at Tier 1 and 1.2% at Tier 2. Add an adverse-selection haircut on top.
- **Mean reversion required:** any edge needs prices to mean-revert at the 1–3% scale more than a random walk would. This has to be tested, not assumed.

### Realistic expectation for a capped grid at Tier 1–2
- About −15% to +10% a year, median near zero.
- Max drawdown roughly equals the inventory cap × the coin's drawdown before the stop triggers.

### Kraken GBP flash crashes (2019, 2021)
- Use marketable-limit stops with a slippage cap, not market orders.
- Be careful around the FX market close and at weekends.

### UK tax: the 30-day rule
In a falling market, a grid can show taxable gains while the account is down on a mark-to-market basis. It also creates hundreds of disposals that each need matching.

### Design to test: long-only ladder on hourly BTC/GBP (ETH as secondary)
- **Starting position:** £1k, all in GBP.
- **Buy levels:** 10 levels below the reference price P0, each a step s below the last, with s = 1.5% (also sweep 1, 2 and 3%).
- **Size:** £50 per level, with crypto capped at 50% of equity.
- **Sells:** each filled buy gets a paired sell one step above it (ping-pong).
- **Re-centring:** the reference price can only be moved up, and only when holding no inventory.
- **Stop:** an hourly close more than 3 steps below the lowest level, or a −15% drawdown from the high. Exit at 0.80% plus 0.3% slippage, pause 7 days, then re-centre.
- **Fill rules:**
  - price must trade 0.10% through the level;
  - an order placed in a bar can only fill from the next bar;
  - ambiguous bars take the adverse fill;
  - a 0.10% adverse-selection penalty per fill (also test 0.05% and 0.2%);
  - a wick filter that ignores spikes more than 5% beyond both the open and the close;
  - split P&L into grid capture versus inventory mark-to-market.
- **Benchmarks:** cash; buy-and-hold BTC; a constant 25% BTC / 75% GBP split rebalanced monthly.
- **Pass criteria:**
  - positive in at least 2 of 3 market regimes;
  - beats the 25/75 split on return per unit of max drawdown;
  - survives a 0.2% trade-through and 0.2% penalty;
  - no more than 20% of P&L from ambiguous bars.
- **Daily-data stress test (2017+):** only steps of 3% or more, and treat the results as upper bounds.

### When it loses
- Sustained downtrends (2022, 2025–26).
- Strong uptrends: it sits in cash and underperforms.
- Low-volatility chop: too few fills to matter.
- Flash crashes on thin GBP books.
- Any shift from mean reversion to momentum.

## R3-6: Yield, staking, accumulation and tax wrappers

### Bottom line
Nothing available to UK retail is market-neutral. The only market-neutral option, cash-and-carry, needs derivatives, which UK retail can't use.

### The benchmark to beat: GBP savings
- Easy-access accounts pay 4.5–5.25% AER (Moneyfacts, 24 Nov 2026), and a cash ISA pays 4.90%.
- That return is in GBP, with no price risk, and is FSCS-protected.
- Bank Rate is 4.00% (raised 5 Nov 2026).

### Staking: available in the UK on Kraken and Coinbase
Net yields after commission, paid in the coin itself:

| Coin | Net yield | Caveat |
|---|---|---|
| ETH | about 2.1–2.3% | |
| SOL | about 4–4.5% | About 1% in real terms, because SOL's supply inflates about 4.7% a year |
| ADA | about 1.5–1.9% | |

- **Commission:** Kraken takes 25–30%, Coinbase about 35%.
- **Lock-ups:** from none up to 28 days, and ETH exit queues can take weeks.
- **Protection:** no FSCS cover.
- **Tax:** rewards are taxed as income when you receive them, then CGT applies when you sell (A).
- **Main risk:** the coin's price. A 2–4% yield is tiny next to a ±50% price swing.

### Crypto lending and "Earn" products
- Kraken's Opt-in Rewards and DeFi Earn are blocked in the UK. Coinbase UK only offers borrowing.
- Celsius customers became unsecured creditors when it failed.
- The FCA's new regime starts 25 Oct 2027, still with no FSCS cover.

### Stablecoin yields
- Typically about 3–5% in USD.
- Risks: GBP/USD exchange-rate moves, platform failure, depegging (USDC fell to 87¢ in March 2023), and no FSCS cover.
- Not better than GBP savings.
- From 6 Apr 2027, eligible stablecoins become exempt from CGT.

### Cash-and-carry basis trades
- Not legal for UK retail: the derivatives ban still applies even though crypto ETNs are now allowed.
- Even where available, the CME basis was only about 3% (Aug 2026), below Treasury yields.

### Accumulation methods: none adds return
- **DCA:** lump-sum investing beats DCA 62–74% of the time (Vanguard). DCA's benefit is behavioural.
- **Value averaging:** no expected-return gain (Hayley).
- **Dip-buying ladders:** no evidence they help. Their only real saving is that maker orders cost less in fees.

### Tax wrappers
- Crypto ETNs could go in a stocks & shares ISA from Oct 2025, but **new purchases were removed from 6 Apr 2026**.
- They are allowed in an Innovative Finance ISA, but almost no providers offer one.
- They are allowed in a SIPP: e.g. Hargreaves Lansdown from Sep 2026 (BTC/ETH ETNs, 0.15–0.35% a year in fees), locked until age 57.
- Staking ETNs (CoinShares, 21Shares) held in a SIPP are the only route found that combines yield with a tax wrapper.

### Red flags
- Income tax is due when staking rewards arrive, even if the coin later falls in value.
- Many articles about ISA eligibility are out of date.
- Several sources are vendors or affiliate sites.

## R3-1: Arbitrage and market-neutral methods

**Bottom line:** at Kraken Tier 1–2 fees, none of these methods has evidence of a repeatable net edge.

### Kraken fees
- **Stablecoin/FX pairs** (USDC/USD, USDT/GBP, GBP/USD) have their own schedule: 0.20% maker and taker. That is 0.40% for a round trip.
- **Withdrawals:** £1.95 GBP via Faster Payments; 0.000015 BTC.
- **Coinbase Advanced UK** fees of 0.25/0.50 come from a secondary source only. Coinbase's own page refused the fetch.

### Cross-exchange gaps on GBP pairs: not viable
- Crépellière et al. (JFM 2023, B): net returns have been negative since 2019, even at 25 bp fees.
- Flowerday et al. (QFE 2026, B): 80% of mispricing involved Bitfinex. Excluding it, the median gap lasted 2 minutes, and even the 95th percentile is not profitable after 1% costs.
- Typical gaps are 0.01–0.2%, against a cost of about 1.3%.
- Gaps open during stress, which is exactly when withdrawals get paused.

### Triangular arbitrage: not viable
- Muck et al. (FRL 2025, B): 65% of opportunities lasted ≤1 second. Only 18 were profitable in a week, worth about $15 in total, and needed reactions within about 146 ms.
- Our cost per loop is about 1.8%.

### GBP pair vs USD-implied price (on Kraken)
- Old papers found deviations, but only before costs.
- Use this as an execution router (pick the cheaper path), not as a strategy.

### Stablecoin depeg trades
- The only case where the cost (0.4%) is sometimes below the move.
- In March 2023, USDC fell to $0.86 and recovered within about 2 days, but only after a US government backstop.
- Retail can't redeem with the issuer, so this is really a credit or event bet. A coin can fail outright (as TerraUSD did).
- The tGBP order book is tiny.
- Testing needs Kraken's free trade downloads.

### Long-only pairs rotation (e.g. ETH/BTC via the direct cross pair)
- Evidence (C/D): published results are long-short, minute-level, and depend on fees. The daily distance method lost money.
- **Switching cost:** 0.4–0.8% per switch via the direct cross. At 20 switches a year that is 8–16% a year.
- **Testing:** it is testable on our data. It must beat a static 50/50 split out of sample.

### Conclusion
Retail arbitrage on liquid pairs effectively no longer exists. What remains is being paid for taking on risk.

### Ranked shortlist
1. A stablecoin/FX dislocation watcher, sized small and capped.
2. ETH/BTC ratio rotation (low prior chance of working).
3. A GBP-vs-USD deviation monitor, used as an execution router.
4. A cross-exchange gap index, to measure only.
5. Triangular arbitrage: no.
