# Round 2 assessment: what should Lab B be? (24 Nov 2026)

This is an independent assessor's report. It weighs the five research reports, the main session's rule search and round 1, then re-tests the main candidates on about 8 years of daily data.

- **Code:** `research/2026-11-24-round2/assess.py`. Run it from the repo root; it takes about 70 seconds.
- **Full output:** `assess_output.txt`, `assess_tables.md` and `assess_results.json`, in the same folder.
- **Scope:** everything ran in a scratch copy. Nothing in the live bot's repo was edited, and no real money is involved.
- This report gives facts and a recommendation about the design of the paper lab. It is not financial advice, and it says nothing about whether to put real money in.

---

## 1. Summary

1. **No rule reliably beat simply holding BTC on return after 0.8% fees.** Over 2019 to Nov 2026, buy-and-hold BTC made +41.8% a year with a −73% worst fall. Every trend rule made less in strong bull runs. In rolling 2-year tests, each rule beat holding in only about 40–60% of start dates, which is close to a coin flip.
2. **What does hold up is drawdown control.** One rule (2.5 below) roughly halved the worst fall to about −35%. It kept about 80% of the long-run growth rate, and it never had a losing calendar year. The pattern held across the full window, all 24 rolling start dates, the walk-forward test and a ±25–50% change in its settings.
3. **Recommended Lab B: "BTC+ETH breakout legs with a BTC 200-day gate".**
   - 2 coins, 3 breakout lookbacks (20, 50 and 100 days), giving 6 fixed equal slots.
   - One daily check.
   - About 39 orders and 19 disposals a year.
   - Fees of about £41 a year per £1,000 at taker (0.80%), or about £20 at maker (0.40%).
4. **Several layers added nothing and should be dropped:**
   - the four extra coins (SOL, XRP, ADA, LINK),
   - inverse-volatility sizing,
   - the ratcheting stop (on daily closes it never changes anything),
   - the wide set of lookbacks,
   - weekly checks,
   - volatility targeting,
   - the MA ensemble,
   - core-satellite.

   The one filter that earned its place is the BTC 200-day gate. Removing it made the worst year −28% instead of 0%.
5. **The main session's winner (own 50-day MA, BTC+ETH) is mostly bear-market avoidance.** All of its edge over holding came in the periods when BTC was below its 200-day average. It also had a −51% drawdown and a −38% year. The recommended rule does the same job more cleanly.
6. **Run Lab B as a second £1,000 paper account from 1 Dec 2026, for at least 12 months.** Don't judge it on return against BTC before 24 months: even in the backtest it beat BTC in only 40% of 12-month windows. The success and kill rules are set out in section 4(d).

---

## 2. Assumptions (apply to every number below)

- **Data:**
  - Coinbase daily GBP candles.
  - ETH before Sep 2018 and LINK before Jul 2020 use the USD candles converted to GBP at the implied GBP/USD rate (BTC-GBP close ÷ BTC-USD close, smoothed over 7 days).
  - XRP is converted from USD for the whole period, because its GBP file is unusable.
  - BTC, ETH, SOL and ADA in the test window are real GBP data.
- **Window:** 1 Jan 2019 to 23 Nov 2026, about 7.9 years. Earlier data is used only to warm up the averages. 2026 is a part year.
- **Fills:** each signal is read at the daily close (00:00 UTC) and filled at the *next* day's open.
- **Lookahead check:** I cut off all data after a date, re-ran every strategy, and compared the results up to that date. All 31 strategies and the recommended candidate give identical results.
- **Costs:**
  - The fee is charged on every buy and sell: 0.80% taker, or 0.40% maker in the maker runs.
  - Slippage is added on top: 0.05% for BTC and ETH, 0.10% for other coins. I kept slippage in the maker runs, which is conservative.
- **Cash:** idle cash earns either 0% or 4% a year. Both are reported.
- **Trading limits:**
  - Spot only, long only, never more than 100% invested.
  - Equity is valued at market each day, and nothing is force-sold at the end.
  - Trades under 0.5% of equity are skipped.
- **Tax-style counts:**
  - Each sale of a coin on a day counts as one UK disposal.
  - "Proceeds" means gross sale proceeds.
  - "Account size for £50k" is the account size at which yearly sale proceeds would reach the £50k reporting trigger.
- **Universe:** the live bot's 6 coins, which were chosen with hindsight. That is survivorship bias.

---

## 3. Key results

### 3.1 Full window, 2019-01-01 to 2026-11-23, taker 0.80%, £1,000 start

A selection of rows; all 31 are in `assess_tables.md`.

- "Fees £/yr" is measured on a growing account. The figure in brackets is fees as a % of average equity per year, which equals £ per £1,000 held.
- "Disposals" means disposals per year.

| Strategy | CAGR 0% cash | CAGR 4% cash | Max DD | Worst yr | Up yrs | Orders/yr | Fees £/yr (% eq) | Disposals | Proceeds £/yr | Acct for £50k | CAGR maker (0%/4%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B&H BTC | +41.8% | +41.8% | −73% | −60% | 5/8 | 0.1 | 1 | 0 | 0 | never | +41.9/+41.9 |
| B&H BTC+ETH 50/50 | +39.8% | +39.8% | −74% | −63% | 5/8 | 0.3 | 1 | 0 | 0 | never | +39.8/+39.8 |
| Equal-weight 6-coin basket | +42.9% | +43.1% | −73% | −61% | 5/8 | 6.5 | 48 | 2.4 | 2,983 | £258k | +43.4/+43.6 |
| Monthly DCA into BTC | +15.5% | +16.8% | −59% | −44% | 5/8 | 8.6 | 1 | 0 | 0 | never | same |
| BTC 200-day MA ±2%, daily | +30.6% | +32.7% | −60% | −13% | 5/8 | 3.8 | 127 (2.5%) | 1.9 | 8,481 | £31k | +32.6/+34.8 |
| BTC 200-day MA ±2%, weekly | +27.5% | +29.7% | −67% | −11% | 5/8 | 2.8 | 97 | 1.4 | 6,474 | £35k | +29.0/+31.1 |
| BTC MA ensemble, daily | +32.6% | +35.0% | −58% | −32% | 5/8 | 26.3 | 401 | 14.1 | 25,768 | £12k | +37.0/+39.8 |
| BTC MA ensemble, weekly | +30.9% | +33.5% | −51% | −20% | 5/8 | 13.6 | 246 | 7.2 | 15,976 | £20k | +33.7/+36.0 |
| Own 50-day MA ±2%, BTC+ETH | +45.5% | +48.2% | −51% | −38% | 7/8 | 21.0 | 858 | 10.5 | 55,197 | £9.6k | +51.8/+54.6 |
| Own 30-day MA ±5%, BTC+ETH | +42.7% | +45.2% | −54% | −35% | 7/8 | 17.2 | 634 | 8.6 | 40,916 | £11.7k | +47.7/+50.4 |
| Own 75-day MA ±0%, BTC+ETH | +26.6% | +28.9% | −67% | −54% | 7/8 | 34.7 | 601 | 17.4 | 38,206 | £6.0k | +35.4/+37.8 |
| Lab B round-1 (6 coins, narrow, gate) | +35.1% | +39.0% | −34% | −4% | 6/8 | 80.7 | 262 (4.7%) | 43.4 | 17,113 | £16k | +38.7/+42.7 |
| Lab B, 6 coins, narrow, no gate | +33.4% | +36.9% | −45% | −30% | 5/8 | 112 | 369 | 57.6 | 23,771 | £12k | +37.7/+41.4 |
| Lab B, 6 coins, wide, gate | +29.7% | +33.4% | −35% | −10% | 5/8 | 111 | 179 | 60.4 | 11,680 | £20k | +32.6/+36.4 |
| Lab B, 6 coins, wide, no gate | +27.6% | +31.0% | −40% | −21% | 5/8 | 186 | 264 | 96.0 | 16,984 | £14k | +31.4/+35.0 |
| Gate only: equal-weight 6 coins while BTC is above its 200-day MA | +40.8% | +43.0% | −57% | −19% | 5/8 | 28.2 | 233 (2.6%) | 13.6 | 15,545 | £29k | +43.9/+46.1 |
| **Recommended: BTC+ETH legs + gate** | **+34.4%** | **+37.9%** | **−36%** | **0%** | **7/8 (+1 flat)** | **38.8** | **(4.1%)** | **19.4** | **2.7× equity** | **~£18k** | **+37.4/+40.9** |
| BTC vol-target 40% | +31.5% | +32.6% | −59% | −48% | 5/8 | 7.1 | 73 | 3.4 | 4,632 | £72k | +32.5/+33.5 |
| BTC 200-day MA × vol-target | +22.4% | +25.1% | −46% | −11% | 5/8 | 7.5 | 93 | 3.9 | 6,093 | £28k | +24.3/+26.7 |
| BTC/cash 50/50, 15-point band | +24.9% | +29.8% | −45% | −32% | 5/8 | 1.0 | 5 | 0.8 | 447 | £468k | +25.0/+29.9 |
| Core-satellite: 50% BTC + 50% MA ensemble | +37.7% | +38.7% | −66% | −50% | 5/8 | 26.5 | 201 | 14.1 | 12,884 | £35k | +39.6/+40.9 |
| Core-satellite: 50% BTC + 50% Lab B wide | +36.0% | +37.1% | −63% | −49% | 5/8 | 186 | 132 | 96.0 | 8,492 | £48k | +37.3/+38.7 |

Notes on reading this table:

- **The recommended rule's worst year is exactly 0%.** That year was 2022: the gate kept it in cash all year. With 4% on cash it was +4%.
- **The fee figures are all fees, not profit.** For trend rules, total fees are large relative to £1,000 because the account grows to several thousand pounds.

### 3.2 Calendar years (taker, 0% on cash; 2026 runs to 23 Nov)

| Strategy | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| B&H BTC | +83% | +290% | +61% | −60% | +144% | +124% | −13% | −28% |
| B&H BTC+ETH 50/50 | +38% | +344% | +203% | −63% | +102% | +79% | −15% | −34% |
| BTC 200-day MA ±2% | +44% | +131% | +8% | −1% | +60% | +73% | −13% | −5% |
| Own 50-day MA ±2%, BTC+ETH | +21% | +269% | +198% | −38% | +54% | +34% | +6% | +7% |
| Lab B round-1 (6 coins) | +32% | +90% | +82% | +0% | +36% | +77% | −4% | +3% |
| **Recommended: BTC+ETH legs + gate** | **+55%** | **+81%** | **+75%** | **+0%** | **+27%** | **+55%** | **+6%** | **+2%** |
| Same, with 4% on cash | +60% | +85% | +78% | +4% | +29% | +58% | +9% | +5% |
| Same, maker 0.40%, 4% on cash | +62% | +92% | +83% | +4% | +33% | +60% | +12% | +6% |

The pattern is a third to two-thirds of the gain in bull years, and roughly flat in bear years.

### 3.3 Rolling 2-year runs: a new start every quarter, 2019 Q1 to 2024 Q4 (24 starts), taker, 0% on cash

The 4%-on-cash version is in the tables file. It adds about 5–10 points to the median for the trend rules.

| Strategy | Median 2y | 10th pct | % of starts > 0 | % of starts beating B&H BTC | Median max DD | Worst max DD |
|---|---|---|---|---|---|---|
| B&H BTC | +145% | −26% | 71% | – | −53% | −73% |
| Equal-weight basket | +184% | −16% | 88% | 62% | −60% | −73% |
| Monthly DCA into BTC | +75% | −24% | 67% | 21% | −40% | −67% |
| BTC 200-day MA ±2% | +85% | +2% | 92% | 42% | −32% | −60% |
| BTC MA ensemble, daily | +88% | −13% | 79% | 42% | −36% | −58% |
| Own 50-day MA ±2%, BTC+ETH | +67% | 0% | 88% | 54% | −35% | −51% |
| Lab B round-1 (6 coins, gate) | +104% | +13% | 92% | 46% | −23% | −34% |
| Lab B, 6 coins, wide, no gate | +74% | −9% | 83% | 38% | −30% | −40% |
| Lab B narrow, gate, BTC+ETH (portfolio form) | +74% | +6% | 92% | 50% | −24% | −35% |
| BTC vol-target 40% | +100% | −18% | 75% | 21% | −45% | −63% |
| BTC/cash 50/50 band | +73% | −8% | 83% | 29% | −31% | −46% |
| Core-satellite with MA ensemble | +126% | −19% | 75% | 42% | −46% | −65% |

**Recommended form, rolling with a monthly start date (4% on cash):**

| Window | Median return | 10th pct | Median max DD | Worst max DD | Beats B&H BTC on return |
|---|---|---|---|---|---|
| 12 months (83 windows) | +19% | −1% | −21% | −34% | 40% of windows |
| 24 months (71 windows) | +82% | +9% | −22% | −34% | 48% |

For comparison, B&H BTC over 12 months: median +46%, 10th percentile −36%, median max DD −49%.

On its worst 12-month and 24-month windows, the recommended form lost more than 15% in at most 1% of windows. B&H BTC did so in 28% of 12-month windows.

### 3.4 Parameter plateau: full window, every setting in each family

For example, BTC MA lengths 100–300 with buffers 0/2/4%, daily and weekly; Lab B lookbacks scaled ×0.5 to ×1.5, with and without the gate.

| Family | Variants | CAGR min / median / max | Max DD median / worst |
|---|---|---|---|
| BTC single MA | 30 | +15% / +30% / +48% | −63% / −75% |
| BTC MA ensemble | 10 | +28% / +33% / +40% | −51% / −62% |
| Own MA, BTC+ETH | 21 | **+2.5%** / +39% / +46% | −58% / **−84%** |
| Lab B (6 coins) | 20 | +23% / +30% / +37% | −38% / −48% |
| Vol-target | 12 | +21% / +31% / +37% | −67% / −74% |
| Recommended BTC+ETH legs | 7 settings | +32% to +35% | −36% to −47% |
| BTC+ETH portfolio form | 7 settings | +28% to +39% | −33% to −41% |

- **Single MA and own MA are peaks, not plateaus.** The 200-day rule's neighbours range from +15% to +48%. Own-MA ranges from +2.5% to +46%, with drawdowns down to −84%.
- **The BTC+ETH breakout family with the gate is a genuine plateau.** Every setting tried gave 28–39% CAGR with drawdowns of −33% to −47%.
- **In the Lab B family, the gate improved both drawdown and worst year in all 10 gate-on/gate-off pairs.**

### 3.5 Walk-forward: choose on 2019–2022 by CAGR ÷ max DD, then test once on 2023 to Nov 2026

For reference, B&H BTC in the test period: +37.0% CAGR, −52% max DD.

| Family | Picked on 2019–22 | Test CAGR / DD | Picked variant's test rank in its family |
|---|---|---|---|
| BTC single MA | MA100 ±4% daily | +29.9% / −29% | 1 of 30 |
| BTC ensemble | ×0.5 lengths, weekly | +17.5% / −39% | 9 of 10 |
| Ensemble × vol | vol-target 30% | +15.9% / −27% | 11 of 12 |
| Fixed mix | 30/70, 20-point band | +15.5% / −18% | 1 of 9 |
| Lab B (6 coins) | narrow ×1.25, gate | +19.6% / −22% | 3 of 20 |
| Own MA BTC+ETH | MA63 ±5% | +22.2% / −42% | 9 of 21 |
| Vol-target | 40%, 30-day vol | +28.4% / −50% | 7 of 12 |
| (Recommended BTC+ETH legs, not tuned) | – | +19.3% / −23% | – |

- **Global pick across all 114 grid variants:** Lab B narrow ×1.25 with the gate. In the test period it made +19.6% a year with a −22% drawdown.
- **The rank correlation between training and test results was only 0.13.** Picking the best backtest barely predicts the next 4 years. This supports choosing on robustness and drawdown rather than on the top number.

### 3.6 Removing one layer at a time (the "stacked filters hurt" check)

| Layer | Effect of removing it | Keep? |
|---|---|---|
| BTC 200-day gate | Worst year 0% → −28%; DD −36% → −43%; fees up 50% | **Keep** |
| Inverse-vol sizing (vs equal weight) | No difference (+27.6% vs +27.6%; +35.1% vs +35.9%) | Drop |
| Ratcheting midpoint stop | Identical results; on daily closes the midpoint almost never falls while a position is open | Drop (plain midpoint is enough) |
| Wide lookbacks (10–360) vs narrow (20/50/100) | Wide is worse: 6 coins 29.7% vs 35.1%; BTC+ETH 28.2% vs 34.8% | Use narrow |
| SOL, XRP, ADA, LINK (6 coins → BTC+ETH) | Same CAGR (34.8% vs 35.1%) and DD (−35% vs −34%), at under half the disposals | Drop the alts |
| Rebalancing / resizing (no band) | No band: −2.4 points CAGR and twice the orders | Size once at entry |
| Weekly instead of daily check | Worse DD (−44% vs −35%) and worse 10th percentile | Stay daily |

**Survivorship check on the 6-coin version.** Dropping any one coin changes CAGR by −6 to +4 points, and DD stays between −33% and −39%. No single coin carries the result.

### 3.7 Is the own-MA rule's edge just bear-market avoidance?

The table splits each rule's excess over B&H BTC+ETH by whether BTC was above or below its 200-day MA. The figures are log-points; 0.49 is roughly a 63% better outcome.

| Rule | Excess with BTC above MA200 (1,670 days) | Excess with BTC below MA200 (1,214 days) |
|---|---|---|
| Own 50-day MA ±2% | −0.17 | **+0.49** |
| Own 30-day MA ±5% | −0.11 | +0.27 |

**Yes, it is bear-market avoidance.** All of its gain over holding came when BTC was below its 200-day average, and it lost ground in bull phases. Its full-window win, +45.5% against +39.8% for holding, depends on the 2021–22 ETH boom-and-bust sequence. Its rolling 2-year median (+67%) is well below holding's (+145%). Its walk-forward pick made +22% with a −42% drawdown, worse on drawdown than Lab B.

### 3.8 Fee sweep: full-window CAGR at different fee levels per side (0% cash)

| Strategy | 0.25% | 0.40% | 0.60% | 0.80% | 1.20% |
|---|---|---|---|---|---|
| **Recommended BTC+ETH legs + gate** | +38.5% | +37.4% | +35.9% | +34.4% | +31.7% |
| Lab B round-1 (6 coins) | +40.1% | +38.7% | +37.0% | +35.1% | +32.3% |
| BTC 200-day MA ±2% | +33.3% | +32.6% | +31.6% | +30.6% | +28.6% |
| Own 50-day MA ±2% | +54.2% | +51.8% | +48.6% | +45.5% | +39.5% |
| BTC/cash 50/50 | +25.0% | +25.0% | +25.0% | +24.9% | +24.9% |

Slow rules lose about 1 point of CAGR for each 0.2% of fee. **Fees don't kill these rules the way they killed the 4h bot.** The 4h bot paid £488 in fees in 2 years on £1,000.

---

## 4. Decisions

### (a) Does anything hold up after 0.8% fees?

**Yes, but only as a drawdown brake, not as a way to beat holding BTC.** The rule that survives every test is the breakout legs on BTC+ETH with the BTC 200-day gate. In its tested form:

| Test | Result |
|---|---|
| Full 2019–2026 window | +34% CAGR (+38% with 4% on cash); max DD −36%; no down year |
| All 24 two-year start dates | 92–100% positive; worst drawdown −35% |
| Walk-forward test period (2023–26) | +19% a year with −23% DD, against B&H BTC's +37% with −52% |
| Parameter plateau | Every nearby setting gave 28–39% CAGR |

For comparison, B&H BTC returned +41.8% a year over the full window with a −73% max DD.

**Realistic expectation.** This is judgement. Live results have historically come in at about half to 90% of backtest.

| | Expectation |
|---|---|
| Bull year | Perhaps a third to two-thirds of BTC's gain |
| Bear year | Roughly −10% to +5%, instead of −50% or worse |
| Drawdowns | 20–35% from a peak will happen, about every year or two |
| Over 12 months | Backtest median +19%, 10th percentile −1%. It will trail BTC in most rising years. |

Do not extrapolate the 34% CAGR. It comes from a period when crypto itself returned about 40% a year.

### (b) What Lab B should be: exact rules

**Coins:** BTC/GBP and ETH/GBP only.

**Check:** once a day, using the completed 00:00 UTC daily candle. Signals use closes only.

**Slots:** 6 fixed slots, each with £166.67 of paper capital: {BTC, ETH} × {20, 50, 100 days}. Each slot is its own pot. Slots are never resized or rebalanced, and pots never share cash.

**Gate (one shared switch):**
- Turns **ON** when BTC's close is above 1.02 × its 200-day simple moving average of closes.
- Turns **OFF** when BTC's close is below 0.98 × that average.
- Otherwise it keeps its previous state.

**Entry, for each slot (coin X, lookback N):**
- Conditions: the gate is ON, the slot is flat, and X's close is above the highest close of X's previous N days (not counting today).
- Action: buy, putting the whole slot into X.

**Exit, for each slot (coin X, lookback N):**
- Exit when X's close falls below the midpoint of the previous N days' closes: (highest + lowest) ÷ 2.
- Also exit everything when the gate turns OFF.
- Each exit sells the whole slot.
- Re-entry needs a fresh breakout while the gate is ON.

**Order type (paper simulation of maker execution):**
- The reference price is the last trade or mid-price at 00:05 UTC.
- **Buy:** a post-only limit at the best bid, never above reference × 1.005.
- **Sell:** a post-only limit at the best ask, never below reference × 0.995.
- **Simulated fill:** only if a later hourly candle trades *through* the limit price, at a 0.40% fee.
- **If not filled within 4 hours:** cancel and re-quote at the new best bid/ask, still inside the original collar. Allow up to 3 re-quotes.
- **After 24 hours:**
  - Exits: a limit IOC order at a 0.80% taker fee, still inside a ±1% collar.
  - Entries: skip until the next day's check.
- Log the maker fill rate. Never use market or stop-market orders on GBP books.

**Sizing:** fixed slot size, as above, with no leverage. The maximum exposure is 100%, when all 6 legs are on.

**Kill switch:**
- **Performance:** if paper equity falls more than **40%** from its peak, close everything and stop. That is outside the worst −36% in the backtest.
- **Review:** at −30%, review, but don't change anything.
- **Operational:** halt on any of the guard failures listed in (d).

**Expected activity (backtest, per £1,000):**

| Item | Per year |
|---|---|
| Orders | About 39 (about 19 buys, 19 sells) |
| Disposals | About 19 |
| Fees at taker | About £41 |
| Fees at maker | About £20 |
| Slippage | About £3–5 |
| Sale proceeds | About £2,700 (2.7 × equity) |

- The £50k proceeds trigger would only be reached at an account of about **£18,000** or more.
- About 153 round trips over 7.9 years, with a 52% win rate.
- The mean net result per round trip is +15%, with a 95% confidence interval of ±8 points.
- The longest losing streak was 4 round trips.

**Simpler fallback if 6 slots feel like too much:** BTC only, with the same 3 legs and the same gate.

| | Fallback (BTC only) |
|---|---|
| CAGR | +35.5% |
| Max DD | −37% |
| Worst year | −11% |
| Orders a year | About 19 |
| Disposals a year | About 10 |

### (c) What NOT to pursue

- **The current 4h regime + breakout + RSI/Bollinger bot:** about flat before fees, and fees (£488 in 2 years) turn it into a loss. Let it finish on 1 Dec and retire it.
- **Mean reversion / dip-buying:** negative after fees in round 1 and in the research.
- **Extra coins (SOL, XRP, ADA, LINK):** they add disposals, slippage and thin-book risk without adding return. They are also hindsight picks.
- **Inverse-vol sizing and the ratchet:** no measurable effect here, so they're just complexity.
- **Wide lookback set (10–360):** worse than 20/50/100, at more trades.
- **Own-MA BTC+ETH (the main session's winner):** a parameter peak (+2.5% to +46%), with −51% to −84% drawdowns. Its edge is bear avoidance, which the gate already gives more cheaply.
- **MA ensemble on BTC:** 26 trades a year, with no better drawdown (−58%) than a single MA.
- **Vol-targeting, alone or as an overlay:** alone, it barely cut the drawdown (−59%). As an overlay, it lowered return more than risk.
- **Core-satellite:** the core keeps the −63% to −66% drawdowns that Lab B exists to avoid.
- **BTC/cash 50/50 rebalancing:** cheap and honest, but −45% DD with less return. It works as a no-skill baseline, not as Lab B.
- **Weekly checks:** worse drawdowns in every family tested.
- **Sentiment, on-chain, calendar, funding and "AI" signals:** grade C–D evidence (R1, R3). Not worth paper time.

### (d) How to run it

**Setup:**
- A second, separate £1,000 paper account (Lab B), starting on the first daily close after the 4h bot finishes on 1 Dec 2026.
- The 4h bot's results are kept as the round-1 record and not continued.

**Benchmarks, tracked daily in the same report with the same fee model:**
1. B&H BTC: £1,000 of BTC bought on day 1.
2. The BTC 200-day MA ±2% switch, with 4% on cash. This is the "is the breakout part worth it?" check.
3. Cash at 4%.

**Judging horizon:**
- **12 months minimum** for a first verdict.
- **24 months** before any conclusion about return versus BTC.
- At 6 months, check mechanics only.

**Success at 12 months (written down now, before any data). Both must hold:**
1. **Return:**
   - If B&H BTC rose over the period, Lab B gained at least 25% of BTC's gain.
   - If BTC fell, Lab B lost less than half of what BTC lost.
2. **Risk:** Lab B's max drawdown is no worse than −35%.

The backtest itself passes both in 86% of 12-month windows and 97% of 24-month windows. A failure is therefore informative.

**Fidelity (also required):** every live paper signal must match a re-run of `assess.py`'s rule on the same candles. Any unexplained difference is a bug: fix it and restart the clock.

**Kill criteria, at any time:**
- Drawdown beyond −40% from peak.
- Fees running above 8% of equity a year (about double the expected level).
- Any order outside its collar.
- Any trade made on stale data.
- Two or more unreconciled ledger breaks.

**Operational must-haves:**
- **Post-only limit orders with a price collar** (±0.5% maker, ±1% taker fallback). No market or stop orders on Kraken GBP books.
- **Stale-data guard.** Don't act if the latest daily bar is more than 26 hours old, if it is missing, or if its close is more than 15% away from the live mid-price. Retry, then alert.
- **Persisted state.** Save each slot's status, the gate state, open orders, the fills log and the last processed bar to disk after every step. On restart, reconcile with the exchange (or the paper book) before doing anything. Cancel-and-replace rather than modifying orders.
- **Logging.** Record intended price vs simulated fill for every order, the maker fill rate, and a daily heartbeat alert.
- **HMRC-style disposal ledger:**
  - Each coin has its own pool.
  - Each disposal is matched first with same-day acquisitions, then with acquisitions in the next 30 days, then with the section 104 pool. Fees are allowable costs.
  - Keep running counters per tax year (6 Apr to 5 Apr): gross proceeds against £50k, net gains against the £3k allowance, and the number of disposals.
  - The 30-day rule matters here, because breakout legs often re-enter within 30 days of an exit.

### (e) What Harry should check himself

- **Kraken Pro:**
  - Your actual fee tier. The research found Tier 1 at 0.40% maker / 0.80% taker, with Tier 2 at $2.5k of 30-day volume. Check on the fee page while logged in.
  - The minimum order size and cost minimum for XBT/GBP and ETH/GBP, compared with the ~£167 slot size.
  - Whether post-only orders are allowed on these GBP pairs.
  - How deep the XBT/GBP and ETH/GBP books are at your size.
- **Coinbase Advanced (UK):** the actual GBP maker/taker fees on your account. Reports conflict (0.25/0.50% vs 0.40/0.60%). Also check that BTC-GBP and ETH-GBP are available.
- **Self Assessment:** whether you already file a return. This matters once disposals are real. Paper disposals have no tax effect.
- Cash rates, if you want the 4% assumption to match your actual savings rate.

---

## 5. Caveats

- **Number of variants tried.**
  - This assessment ran **166 distinct strategy configurations**. Each was run at several fee, cash-rate and window settings, with about 1,500+ simulations in total.
  - Across the whole project, that adds to the main session's 195-rule search and about 25 round-1 variants, so roughly **390 configurations** have been examined.
  - The best-looking number from that many tries is inflated by chance. That is why the recommendation rests on the plateau, the rolling starts and the walk-forward rather than on any top figure.
  - The rank correlation between 2019–22 and 2023–26 performance was only 0.13.
- **The BTC+ETH-only form was found after seeing the 6-coin results.** It is a simplification (fewer coins, the same rule), not a tuned parameter. BTC-only and ETH-only each held up separately, and it was never tuned on the test period. Even so, treat it as not fully out-of-sample. The 12-month paper run is the real out-of-sample test.
- **One market, one era.**
  - 2019–2026 includes two big bull runs and two bear markets.
  - Trend rules need trends. A long sideways chop, which 2025–26 partly was, gives small gains at best.
  - BTC volatility is at multi-year lows (R3), so trends are smaller relative to fixed fees.
- **Survivorship.** The coin list was chosen with hindsight. XRP is entirely synthetic (USD converted to GBP), as is LINK for 2019–mid-2020. The recommended form uses only BTC and ETH, which limits this problem.
- **Maker fills are assumed in the maker rows.** Research suggests only about 55% of limit orders fill, and the missed ones tend to be the fast-moving winners. Treat the maker rows as an upper bound, and the taker rows as the base case.
- **Simplified tax counting.** Disposal counts ignore same-day aggregation across slots and the 30-day rule. The paper ledger must do this properly.
- **Slots drift apart.** In the recommended form each slot compounds on its own. Over many years the slots would become unequal. That doesn't matter for a 12–24 month paper run.
- **Simplified model.** Daily closes only, no intraday stops, mark-to-market at the end, and fills at the next open plus slippage. The real Kraken GBP book can be worse during crashes.
- **Live results are usually worse than backtests** (R2: the Quantopian study, and post-mortems putting live at half to 90% of backtest). Plan on the lower end.
