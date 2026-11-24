# Round 3 assessment: is there a strategy we could trust with real money?

Independent assessor, 24 Nov 2026. These are facts about the paper lab and a recommendation for the lab. It is not financial advice.

- Code: `research/2026-11-24-round3/assess3.py`. Run it from the repo root; it takes about 20 seconds.
- Outputs: `assess3_results.json` (every number in this document) and `trial_ledger.csv` (one row per variant run).
- Data: only the cached Coinbase candles in the repo. There was no internet access.

## Verdict

**No candidate passes. No timing or trading rule we tested clears the bar of "confident enough to invest real money and see a return".**

Every candidate failed in at least one of these ways:
- it lost to its exposure-matched or "do-nothing" benchmark;
- it lost money outright after costs in 2022–26;
- its advantage was statistically indistinguishable from luck.

Several failed in all three. The parameters were fixed in advance and I did not tune anything to rescue them.

The best honest alternative is not a trading strategy. It is GBP savings plus, optionally, a small fixed long-term crypto holding (10–25% BTC) that is rebalanced rarely. Any return from that comes from owning BTC, not from skill. Its history is flattered by 2017–2021, and since mid-2024 a 25% BTC mix has earned less than savings.

---

## 1. How the round-3 research holds up

The research is consistent and, in my view, correct. For a £1k UK spot account, every professional source of profit is either closed or is really just market exposure:
- **Closed:** market making, carry, arbitrage, venture allocations and options.
- **Just exposure:** concentrated holding, and fund indices that match the risk of simply holding crypto.

The only ideas with grade-A or B evidence are weekly cross-sectional momentum and volatility sizing. Both were measured on long-short books of hundreds of coins, at costs 2–8× lower than ours. The digest's own quick check on options-expiry weeks failed to reproduce the paper. That was a useful early warning about how fragile published crypto anomalies are.

## 2. Pros and cons of every method in the digest

Grades: A = tested out of sample with costs, or audited; D = narrative or promotional. "Tested here" means I ran it on our data this round.

| # | Method | Edge mechanism (one line) | Evidence | Feasible at £1k UK spot? | Main risk | Status |
|---|---|---|---|---|---|---|
| 1 | Market making at the touch | Earn the bid-ask spread | B+ against retail | No: 0.40% maker fee is far above the GBP spread | Adverse selection; retail is the slowest quote | Drop |
| 2 | Funding/basis carry | Collect futures premium over spot | B (yield now 2–4%) | No: FCA derivatives ban | Below T-bill yield anyway | Drop |
| 3 | VC/private token allocations | Buy below market before listing | B | No access | Illiquidity, fraud | Drop |
| 4 | Concentrated long holding | Owning the asset class | B (survivors only) | Yes | −70% to −90% drawdowns | **Baseline G** |
| 5 | Trend / moving-average holding | Persistence of trends | B | Yes, but out of scope (Harry's instruction) | Whipsaw, decay | Excluded |
| 6 | Macro liquidity (M2, US net liquidity) | Liquidity drives risk assets | C (sign unstable) | Yes, with monthly data | About 107 observations; lag fitted in-sample | Not tested (no FRED data offline) |
| 7 | On-chain valuation (MVRV, Puell, Pi-cycle) | Cycle valuation | B against (failed out of sample) | Yes | Silent at the 2025 top | Drop |
| 8 | Pundit models (stock-to-flow, etc.) | Narrative | D | Yes | Failed publicly | Drop |
| 9 | Copy-trading leaderboards | Follow "skilled" traders | A against | Yes | Rankings don't persist; can be gamed | Drop |
| 10 | Prop-firm challenges | Trade someone else's capital | B against (~7% paid) | Yes | Firms profit from fees | Drop |
| 11 | Weekly cross-sectional momentum | Winners keep winning for 1–4 weeks | A/B (long-short, many coins, low cost) | Yes | Turnover costs; only 5 coins | **Tested (B): fail** |
| 12 | BTC weekly momentum / Google attention shock | Attention leads flows | B, in-sample, gross | Partly; Trends data is manual | 20–25 switches a year kill it | Not tested (no data) |
| 13 | ML / LSTM / LLM signals | Pattern recognition | B against (~52% accuracy; loses at 10 bp) | Yes | Overfitting, memorisation | Drop |
| 14 | Volatility-scaled exposure | Cut exposure when volatility is high | B (improves risk, not return) | Yes | Turnover; vol spikes often come after the fall | **Tested (A): fail** |
| 15 | Daily reversal / illiquidity | Liquidity premium in small coins | B (fails value-weighted) | No, for majors | Costs | Drop |
| 16 | New listings | Exchange-listing pop | C | No; happens in minutes | Speed | Drop |
| 17 | Token unlocks (XRP monthly, LINK) | Supply pressure | C/D (vendor) | Only as a filter | Inferred dates; small sample | **Tested (F): nothing there** |
| 18 | FOMC/CPI/NFP days | Event drift | B (drift ~0) | Only as a caution flag | None (no edge) | Caution windows only |
| 19 | ETF flows | Flow momentum | C/D | Data refused | Doesn't survive taker costs | Drop |
| 20 | Options-expiry week | Pre-expiry drift | C; failed to reproduce in main session | Yes | Not present even before costs | Drop |
| 21 | Liquidation washout bounce | Forced sellers overshoot | C/D (K33 says no) | Yes | Catching a falling knife | **Tested (D): significantly negative** |
| 22 | Stablecoin mints / exchange flows | Flow signals | C | No (paid data; minutes) | Speed | Drop |
| 23 | Weekend/session timing | Liquidity | None | Execution tip only | Thin weekend GBP books | Use for execution only |
| 24 | Grid / limit-order ladder | Capture back-and-forth price moves | B− (zero expected value on a random walk; short volatility) | Yes, but hundreds of disposals | Trends and stops | **Tested (C): fail** |
| 25 | Staking (ETH/SOL/ADA) | Protocol rewards | A (yields ~1.5–4.5%) | Yes | Coin price; taxed as income; lock-ups | Not a return edge |
| 26 | Crypto lending / "Earn" | Lending yield | A against (Celsius) | Mostly blocked in UK | Platform failure | Drop |
| 27 | Stablecoin yield | USD yield | B | Yes | FX, depeg, no FSCS; not better than savings | Drop |
| 28 | DCA / value averaging / dip ladders | Behavioural smoothing | A (lump sum wins 62–74% of the time) | Yes | None beyond the asset itself | Behavioural tool only |
| 29 | Tax wrappers (SIPP ETNs) | Tax shelter | A (rules) | Yes; locked until age 57 | Product availability | Outside the lab |
| 30 | Cross-exchange / triangular arbitrage | Price gaps | B against | No (~1.3–1.8% cost vs 0.01–0.2% gaps) | Speed, withdrawal halts | Drop |
| 31 | GBP vs USD-implied price | Routing | B (gross only) | As an execution router only | — | Execution tool |
| 32 | Stablecoin depeg trades | Credit/event bet | C | Barely (tiny tGBP book) | Coin fails outright | Drop |
| 33 | ETH/BTC ratio rotation | Mean reversion of the ratio | C/D | Yes | Ratio trends (it fell for years) | **Tested (E): fail** |
| 34 | GBP easy-access savings | Interest | A | Yes | Inflation only | **The hurdle (4.5–5.25%)** |

## 3. Test set-up (common to all candidates)

- **Signals and fills:** each signal uses a daily close, and the trade happens at the next open.
  - Taker fills happen at the open.
  - Maker fills use a post-only limit at the open. It fills only if the day trades 0.10% through the price; otherwise it is re-posted the next day, with no chasing.
- **Costs:** fee of 0.40% (maker, base case) or 0.80% (taker, stress case), plus slippage of 0.05% for BTC/ETH and 0.10% for the others. Slippage is also charged on maker fills, which is conservative.
- **Idle cash** earns 4% a year, booked as a separate "interest" line. The hurdle is savings at 4.5% a year.
- **ETH before Sep 2018** is a synthetic GBP series (ETH-USD divided by the GBP/USD rate implied by BTC). XRP-USD has a Coinbase gap from Jan 2021 to Jun 2023, so XRP is used only in the event study.
- **Trial ledger:** 126 variants this round, plus 195 already spent, gives **N = 321**. All are listed in `trial_ledger.csv`.

## 4. Results

### 4.1 Headline table (base case = maker 0.40% where realistic; full period of each test)

| Candidate | Period | CAGR | Max DD | Benchmark (same period) | Bench CAGR / DD | Beats benchmark? | 2022–26 out of sample |
|---|---|---|---|---|---|---|---|
| A. Vol-scaled BTC | 2017–26 | 32.4% | −61% | Constant 68% BTC (exposure-matched) | 44.4% / −68% | **No**, −10.9%/yr; PSR of the difference 0.02 | 6.4% vs const 8.7% |
| A. Vol-scaled basket | 2017–26 | 36.5% | −62% | Constant 56% basket | 45.8% / −63% | **No**, −7.4%/yr | 3.6% vs const −0.3% (only sub-period it wins) |
| B. Weekly momentum, 14-day | Jun 2021–26 | **−5.1%** | −78% | EW basket, weekly rebalance | 1.0% / −83% | **No** | 2024–26: −33%/yr vs EW −11% |
| B. Weekly momentum, 7-day | Jun 2021–26 | −3.2% | −88% | EW basket, weekly rebalance | 1.0% / −83% | No (PSR 0.61, noise) | — |
| C. BTC hourly grid, s = 1.5% | Jul 2024–26 | **−11.1%** | −24% | 25/75 BTC/cash, monthly | 4.3% / −14% | **No** | All three regimes negative |
| C. Best step (s = 3%) | Jul 2024–26 | −3.5% | −16% | 25/75 | 4.3% / −14% | No | 1 of 3 regimes positive |
| C. Daily grid since 2017 (upper bound) | 2017–26 | −9.8% / −2.2% / +1.0% at s = 3/4/5% | −75% / −51% / −37% | Cash at 4% | 4.0% | No | — |
| D. Washout bounce (pre-registered k=3, kb=2) | Test 2022–26 | **−3.95% per trade** (n=46, t = −2.8) | — | Random entry, same exits | −1.2% per trade | **No; worse than random** | Also negative in 2017–21 training |
| E. ETH/BTC z-score, fixed rule | 2017–26 | 23.3% | −93% | Static 50/50 (hold) | 63.1% / −92% | **No** | −11.2% vs −11.4% (hold) / −3.1% (monthly rebalance) |
| E. ETH/BTC walk-forward | 2020–26 | 47.7% | −75% | 50/50, monthly rebalance | 45.3% / −73% | Not significant (PSR 0.71) | **−10.2% vs −3.1%: loses** |
| F. XRP supply event | 2019–26 (62 months) | — | — | Same windows on all other days | — | **No effect** (p = 0.67 / 0.98 / 0.86) | — |
| G. GBP savings | — | 4.5% | 0% | — | — | — | 4.5% |
| G. Buy and hold BTC | 2017–26 | 50.6% | −83% | — | — | — | 6.0% / −63% |
| G. 25/75 BTC/cash, 10-point band | 2017–26 | 20.1% | −26% | — | — | — | 6.5% / −17% |
| G. 10/90 BTC/cash, 4-point band | 2017–26 | 10.8% | −11% | — | — | — | 5.7% / −6% |

### 4.2 Year by year (%)

| Year | BTC B&H | 25/75 band | 10/90 band | A: vol BTC | A: const 68% | B: mom14 | B: EW weekly | C: daily grid 5% (upper bound) | D: washout sleeves | E: ETH/BTC fixed | E: static 50/50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | +1173 | +122 | +41 | +316 | +630 | — | — | +17 | +15 | +713 | +4676 |
| 2018 | −72 | −15 | −6 | −47 | −54 | — | — | −10 | −13 | −86 | −80 |
| 2019 | +84 | +23 | +13 | +65 | +67 | — | — | −3 | +8 | +30 | +11 |
| 2020 | +290 | +61 | +24 | +136 | +187 | — | — | −6 | −21 | +317 | +401 |
| 2021 | +62 | +20 | +13 | +37 | +53 | +136 (from Jun) | +68 | −3 | +2 | +129 | +320 |
| 2022 | −60 | −14 | −3 | −49 | −43 | −65 | −75 | −16 | −22 | −62 | −63 |
| 2023 | +144 | +31 | +15 | +110 | +90 | +171 | +228 | +28 | −6 | +115 | +88 |
| 2024 | +124 | +30 | +14 | +98 | +83 | 0 | +80 | +12 | +6 | +96 | +58 |
| 2025 | −13 | −1 | +2 | −13 | −6 | −23 | −34 | +6 | +6 | −42 | −17 |
| 2026 (to 23 Nov) | −28 | −5 | +1 | −25 | −18 | −57 | −37 | −8 | −29 | −39 | −38 |

Hourly grid C (s = 1.5%, maker): 2024 H2 −3.8%, 2025 −11.6%, 2026 −10.9%. The 25/75 benchmark made +13.8%, +0.7% and −3.6%.

### 4.3 Candidate details

**A. Volatility-scaled exposure**
- Lower volatility trimmed the drawdown slightly (−61% vs −68%) but cost about 11 points a year against a constant weight with the same average exposure.
- The return per unit of drawdown is worse: 0.53 vs 0.66.
- **Sensitivity:** 12 of 12 one-at-a-time changes (±25–50%) leave BTC behind its own constant benchmark, by 6 to 12 points a year. For the basket, 10 of 12 lose; the two that "win" (target 0.60: +2.6; λ 0.97: +0.05) are isolated.
- **Timing null:** shifting the weight path to random dates does as well or better. The actual path ranks at the 30th percentile for BTC and the 39th for the basket.
- **Why it loses:** in crypto, volatility spikes on rallies as well as crashes, so the rule cuts exposure in the best months (e.g. 2017, 2020).
- **Fees:** fees were 4× those of the constant mix (£775 vs £175 on BTC). The 30-day rule hits 41% of BTC sells.
- The stress case (taker 0.80%) gives the same verdict.

**B. Weekly cross-sectional momentum**
- There is a gross signal, but it is not significant: the top 2 beat the basket by +0.38% a week (95% CI −0.10 to +0.86, t = 1.5, 281 weeks).
- Turnover destroyed it: about 29 disposals a year and about 12.7× the account value sold each year.
- It beat the basket in 2021–23 and lost badly in 2024–26 (−33%/yr vs −11%).
- **Sensitivity:** lookbacks of 10, 21 and 28 days are all negative. Only "keep until rank ≥ 5" was positive (+7.5%, −79% drawdown). That is a lone post-hoc variant and I do not count it.
- **Random-coin null:** swapping in a random coin on the same dates ranks the real strategy at the 45th percentile, which is pure chance.
- With taker fees it falls to −13%/yr.

**C. Long-only grid**
- **Grid capture is positive at maker fees:** +£126 per £1k at s = 1.5% and +£181 at s = 3%.
- **But stops realise the inventory losses:** −£428 and −£339 respectively.
- **Without a stop** (diagnostic only) it still loses: −4.7%/yr, with the inventory down −£234.
- **At taker fees, grid capture itself turns negative** (−£122 at s = 1.5%).
- **Hourly variance ratios are below 1** (0.86 at 24h), so there is some short-term mean reversion. It is far too small to pay 0.4–0.8% fees plus an adverse-selection haircut.
- **Ambiguous bars barely matter:** CAGR −11.12% adverse vs −11.08% optimistic.
- **Robustness:** a 0.2% penalty makes it worse (−14.4%); smaller lots lose less only because they hold less.
- **ETH grid:** −34%/yr.
- **UK practicality:** about 277 disposals a year at s = 1.5%. 100% of sells are re-bought within 30 days, so every gain needs 30-day matching. Proceeds are about 17× the account value per year, which passes the £50k reporting trigger at an account of about £3k.
- **Pre-registered pass criteria:**

  | Criterion | Result |
  |---|---|
  | Positive in ≥2 of 3 regimes | Fails (0 of 3) |
  | Beats 25/75 on return per unit of drawdown | Fails |
  | Survives a 0.2% penalty | Fails |
  | No more than 20% of P&L from ambiguous bars | Passes, but moot |

**D. Washout bounce**
- **Training (2017–21):** all 18 threshold combinations had a negative average net return.
- **Selection rule:** the "best" combination, picked by the pre-set rule (k 3.5, kb 1.5, with confirmation), was still negative at −0.8% per trade.
- **Single test on 2022–26:**

  | Variant | Mean net return per trade | n | 95% CI | t | Win rate |
  |---|---|---|---|---|---|
  | Pre-registered | −3.95% | 46 | −6.7 to −1.2 | −2.8 | 37% |
  | Confirm (higher-close) variant | −8.6% | 33 | — | — | — |
  | Train-chosen | −8.7% | 22 | — | — | — |

- **Against a random entry with the same exits,** BTC ranks at the 2.5th percentile and SOL at the 4th: worse than random. Buying after crashes caught further falls (e.g. Nov 2022, Jan 2026).
- **Caveat:** events cluster on the same days across coins, so the t-statistics overstate independence. The direction is still clearly negative.

**E. ETH/BTC rotation**
- **Out of sample (2022–26):** the fixed rule made −11.2%/yr, a tie with static 50/50 held (−11.4%), and lost to 50/50 rebalanced monthly (−3.1%) and to BTC alone (+6.0%).
- **Walk-forward:** it picked the same setting every year (90-day window, ±2.0, "mirror"). From 2022 it made −10.2%/yr, against −3.1% for 50/50 rebalanced monthly. It fails the stated test of beating static 50/50 out of sample.
- **Before 2022 it looks good only because ETH's 2017 run dominates.**
- **UK practicality:** each switch is a disposal; there are about 5 a year.

**F. XRP supply-event filter**
- 62–63 monthly events.
- XRP-minus-BTC excess return in each window, compared with the same windows on all other days:

  | Window | Event mean | All other days |
  |---|---|---|
  | [−5, −1] | −1.1% | −0.7% |
  | [0, +2] | −0.5% | −0.4% |
  | [+3, +14] | −1.5% | −1.8% |

- Permutation p-values are 0.69, 0.98 and 0.90. There is no detectable escrow effect, so there is no reason to use it even as a filter.
- LINK, using quarter starts as a proxy for unlock dates (the dates are inferred): nothing significant after the permutation test (p ≥ 0.16).

### 4.4 Overfitting checks (deflated Sharpe ratio, N = 321)

- **Harsh version** (variance of Sharpe ratios across all 91 trials with an equity curve; the expected best Sharpe from luck is 3.4 a year): **everything fails, including buy-and-hold.** This version is too strict to be informative.
- **Lenient version** (variance within each candidate's own family; floor 0.01): buy-and-hold BTC and the cash mixes "pass" at about 0.97. That only shows crypto beta had a positive Sharpe ratio from 2017 to 2026; it is not timing skill. A (0.95 vs its constant benchmark's 0.98), B (0.43) and E (0.75–0.89) are all **below** their own benchmarks. C and D score 0.
- **The test that matters is whether the timing beats its own benchmark day by day** (probabilistic Sharpe ratio of the daily return difference):

  | Comparison | Annual difference | PSR |
  |---|---|---|
  | A BTC vs constant | −10.9% | 0.02 |
  | A basket vs constant | −7.4% | 0.06 |
  | B mom14 vs EW | −5.4% | 0.36 |
  | B mom7 vs EW | +5.0% | 0.61 |
  | E walk-forward vs 50/50 monthly | +4.9% | 0.71 (loses out of sample) |
  | C grid vs 25/75 | −15.9% | 0.002 |

  **None reaches 0.95, and none would survive deflation for 321 trials.**

### 4.5 How often each approach beat savings (4.5%), rolling windows

| Series | 1-yr windows beating savings | 1-yr chance of a loss | 3-yr windows beating savings | Independent 3-yr windows |
|---|---|---|---|---|
| BTC buy & hold (2017+) | 65% | 34% | 99% | 3.3 |
| BTC buy & hold (windows starting 2021+) | 52% | 48% | 99% | 2.0 |
| 25/75 band (2017+) | 68% | 29% | 100% | 3.3 |
| 25/75 band (2021+) | 52% | 43% | 100% | 2.0 |
| 10/90 band (2017+) | 70% | 11% | 100% | 3.3 |
| 10/90 band (2021+) | 56% | 13% | 100% | 2.0 |
| A vol-scaled BTC | 63% | 35% | 100% | 3.3 |
| B momentum (14-day) | 39% | 59% | 36% | 1.8 |
| C hourly grid | 0% | 100% | n/a | 2.4 one-year windows |
| C daily grid, 3% (upper bound) | 33% | 61% | 22% | 3.3 |
| D washout sleeves | 33% | 49% | 0% | 3.3 |
| E walk-forward | 60% | 39% | 82% | 2.3 |

The 3-year figures rest on only 2–3 non-overlapping periods. They should be read as "it happened in this sample", not as a probability.

### 4.6 UK practicality (base case)

The proceeds column assumes the account stays at £5k, and is set against the £50k reporting trigger.

| Strategy | Disposals per year | Sales as × account per year | Proceeds per year at £5k | Sells re-bought within 30 days |
|---|---|---|---|---|
| 10/90 band | 1.9 | 0.07 | ~£370 | 0% |
| 25/75 band | 1.3 | 0.10 | ~£520 | 0% |
| A vol BTC | 3.9 | 0.84 | ~£4.2k | 41% |
| A basket | 14.3 | 1.0 | ~£5.0k | 28% |
| E ETH/BTC | 5.2 | 5.9 | ~£29k | 22% |
| B momentum | 28.5 | 12.7 | **~£63k (over trigger)** | 55% |
| C grid | 277 | 17.1 | **~£85k (over trigger)** | 100% |

## 5. "Our own strategy"

**None qualifies.** I won't put together a trading strategy from parts that each failed: combining failed parts does not create an edge, and calling one would be relaxing the bar.

What survives is not a timing method. It is the factual non-trading alternative below, described concretely so it can serve as the lab's benchmark. That is not a recommendation to buy crypto.

**Core-and-cash benchmark (non-trading):**
- **Holdings:** GBP in an FSCS-protected easy-access account (4.5–5.25%) or cash ISA (4.9%), plus optionally a fixed BTC sleeve of 10% (lower risk) or 25% (higher risk). BTC only: it has the longest history and the tightest GBP book.
- **Schedule:** check once a week (Monday, 12:00–16:00 UK, during the London/NY overlap). Rebalance only when the BTC weight leaves its band: 6–14% for the 10% target, or 15–35% for the 25% target.
- **Orders:** post-only limit at the mid-price, with a 0.5% price collar. Re-post daily for up to 5 days. Never use a market order, and never trade at weekends.
- **Risk limits:** the crypto sleeve is never more than 35% of the account. No leverage, no alts, no staking.
- **Kill switch:** this is a hold-and-rebalance plan. The only "stop" is an operational one: if the exchange halts withdrawals or there is a security issue, withdraw everything to GBP.
- **Expected activity** (from 2017–26 history):

  | Sleeve | Rebalances per year | Disposals per year | Fees (on £1k) |
  |---|---|---|---|
  | 25/75 | ~2 | ~1.3 | under £3 a year |
  | 10/90 | ~3 | ~2 | ~£1 a year |

  Gains are almost certainly within the £3k annual exempt amount at this size, and there are no 30-day-rule matches.

**Expected outcome (history, not a forecast):**

| | 10/90 | 25/75 |
|---|---|---|
| CAGR 2017–26 | 10.8% | 20.1% |
| CAGR 2022–26 | 5.7% | 6.5% |
| CAGR since Jul 2024 | 4.3% (below savings) | 2.7% (below savings) |
| Worst calendar year | −6% | −15% |
| Max drawdown | −11% | −26% |
| 1-yr windows beating 4.5% (2021+) | 56% | 52% |
| 1-yr chance of a loss | 13% | 43% |
| 3-yr windows beating savings | 100% in sample (2–3 independent windows; not a real probability) | 100% in sample (same caveat) |

- **What the evidence shows:** a small BTC sleeve has historically added return at moderate drawdown, and rebalancing kept the risk bounded.
- **What it does not show:** that the next 3 years will resemble 2017–2024. BTC is down about 28% in 2026 and about 13% in 2025, and the sample includes one of the best-performing assets of the decade (survivorship). Since 2021, the middle 80% of 1-year outcomes ran from about −10% to +32% for 25/75 and from about −1% to +15% for 10/90; the worst calendar years were −15% and −6%. Underperforming savings for several years is entirely plausible.

## 6. Validation path before any real money

**Timing strategies: stop the search for now.** Three rounds and at least 321 trials have found no rule that beats a simple exposure-matched benchmark after realistic UK retail costs. A future idea is worth paper-testing only if it meets all of these:
1. Grade-A/B published evidence that survives costs of at least 0.4% per side.
2. A pre-registered test on our data in which it beats its exposure-matched benchmark in 2022–26 with a PSR of at least 0.95, after deflation for the full trial count.
3. No more than 12 disposals a year.

**If the lab continues, paper-trade the core-and-cash benchmark as an operational rehearsal:**
- **Length:** 3 months (Dec 2026 – Feb 2027), with criteria fixed now.
- **Pass:**
  - at least 90% of post-only orders fill within 5 days inside the collar;
  - realised costs are at most 0.6% per fill;
  - the tracked weight stays inside the band;
  - records are good enough to produce an HMRC-style disposal log.
- **Return is not a pass/fail criterion.** Three months cannot tell skill from luck, and this plan claims no skill.
- **Benchmark:** a GBP savings account at 4.5%, compounding, shown alongside.
- **What would justify a small real-money pilot:** passing the operational criteria and nothing else. A real pilot would mean accepting BTC's risk, not exploiting an edge. Size it so the crypto part is an amount Harry would accept losing entirely; for a £1k account, that is the £100–£250 sleeve, with the rest in savings. That is a personal decision, not something the backtest can justify.
- **What would mean stopping:** any operational failure (unfilled orders, outside the collar, a missed rebalance, unreconcilable records), or Harry deciding a −25% year on the sleeve is unacceptable. Then the alternative is simply 100% GBP savings, which earns 4.5%/yr with zero drawdown. From 2022 to 2026 savings beat every timing rule tested here (B, C, D, E and the A basket) except vol-scaled BTC (6.4%/yr, −50% drawdown); that rule and the plain BTC mixes beat savings only through BTC exposure.

## 7. Caveats

- **Trials:** 126 variants this round, plus 195 from the earlier search, gives N = 321. Rounds 1–2 also tested about 20 more rules, so the true number is higher, which makes every result look worse, not better.
- **Data:**
  - Only Coinbase candles were available. Kraken GBP books may differ.
  - ETH before Sep 2018 is synthetic GBP.
  - XRP has a 2.5-year gap.
  - The coin universe was chosen with hindsight (survivorship), which flatters the basket and momentum results.
- **Daily-bar limitations:**
  - Fill rules (open plus 0.10% trade-through) cannot see intraday order-queue position. Maker no-fill rules make results path-dependent; the A basket did slightly better at taker fees than maker for that reason.
  - The daily grid results are upper bounds.
  - The D equity curve books each trade at exit, so drawdowns during a trade are understated.
  - The E walk-forward ignores the cost of changing settings (none occurred).
- **Interest:** idle cash is credited at 4%. The real hurdle is 4.5–5.25%, which makes cash-heavy plans look slightly worse than they would really be.
- **Rolling windows** overlap heavily, so the 3-year "probabilities" rest on 2–3 independent periods.
- **Not tested:**
  - Macro liquidity filters, Google attention and ETF flows: no data offline.
  - Expiry week: already failed in the main session.
- **Not advice:** this is a paper-lab assessment, not financial advice.
