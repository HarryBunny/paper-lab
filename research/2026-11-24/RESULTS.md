# Research backtest: slower daily rules vs the current 4h bot

Script: `/tmp/analysis/research_backtest.py` (full output in `research_output.txt`, numbers in `research_results.json`).
Scratch copy only; the live repo was not touched.

## Set-up
- Data: the cached Coinbase GBP hourly candles (BTC, ETH, SOL, ADA, LINK; no XRP), resampled to UTC daily bars.
- **Window actually scored: 25 Mar 2025 - 23 Nov 2026 (608 days, ~1.7 years)**. The first 250 days (Jul 2024 - Mar 2025) are warm-up for the longest average, so all variants start on the same day. The current bot's equity curve was cut to the same window and rescaled to £1,000.
- £1,000 start, long-only, max 100% invested, no leverage.
- Signals use the daily close; the trade fills at the **next day's open** plus slippage (0.05% BTC/ETH, 0.10% others) plus the fee. No lookahead.
- Fee scenarios (per side): Kraken T1 taker 0.80%, Kraken T2 taker 0.60%, Coinbase reported taker 0.50%, maker 0.25% (assumes every limit order fills, which is optimistic).
- "Orders" = individual buys/sells (the current bot's 158 trades = 316 orders). "Entries" = times a coin went from 0 to held.
- "Weeks up/down" = rolling 7-day windows with a gain/loss of more than 0.05%. Weeks spent in cash count as neither.
- In this window every coin fell: BTC -31%, ETH -19%, SOL -49%, LINK -41%, ADA -80%.

## Main results (Kraken T1 taker 0.80%, today's real fee)
| Variant | Net return | Max drawdown | Orders (entries) | Fees £ | Weeks up / down |
|---|---|---|---|---|---|
| Buy & hold basket (5 coins) | -44.4% | -67.9% | 5 (5) | 8 | 46% / 53% |
| Buy & hold BTC | -31.3% | -52.0% | 1 (1) | 8 | 48% / 50% |
| **Current 4h bot (same window)** | **-29.0%** | **-34.4%** | 316 (158) | **389** | 15% / 40% |
| Trend switch, basket, BTC SMA200 ±2% | +0.4% | -37.5% | 50 (10) | 41 | 22% / 26% |
| Trend switch, BTC only, SMA200 ±2% | +0.1% | -21.5% | 4 (2) | 33 | 23% / 24% |
| Trend switch, basket, SMA200 no buffer | -2.2% | -34.9% | 81 (25) | 87 | 22% / 27% |
| Breakout ensemble N=20/50/100 | -6.0% | -29.9% | 218 (49) | 116 | 29% / 46% |
| Breakout ensemble + BTC SMA200 ±2% filter | +5.3% | -15.8% | 132 (21) | 78 | 19% / 25% |

## The same variants under each fee level (net return %)
| Variant | 0.80% | 0.60% | 0.50% | 0.25% maker |
|---|---|---|---|---|
| Buy & hold basket | -44.4 | -44.3 | -44.2 | -44.1 |
| Buy & hold BTC | -31.3 | -31.1 | -31.1 | -30.9 |
| Switch basket SMA200 ±2% | +0.4 | +1.3 | +1.8 | +2.9 |
| Switch BTC SMA200 ±2% | +0.1 | +0.9 | +1.3 | +2.3 |
| Switch basket SMA200, no buffer | -2.2 | -0.1 | +1.0 | +3.7 |
| Breakout ensemble 20/50/100 | -6.0 | -3.2 | -1.8 | +1.7 |
| Breakout + BTC SMA200 filter | +5.3 | +7.2 | n/a | n/a |

For the slow rules, the fee level changes the result by only 1-4 points, because they trade rarely. (For the current bot, fees were bigger than its entire loss.)

## Sensitivity (Kraken T1 0.80%; return / max drawdown)
| Variant | SMA150 | SMA200 | SMA250 |
|---|---|---|---|
| Switch basket ±2% | -21.2 / -45.2 | +0.4 / -37.5 | -29.3 / -44.7 |
| Switch basket ±3% | -9.5 / -37.1 | +0.3 / -37.5 | -29.3 / -44.7 |
| Switch basket 3-day persist | -38.1 / -53.5 | -22.1 / -45.3 | -33.8 / -46.3 |
| Switch BTC ±2% | -18.3 / -30.2 | +0.1 / -21.5 | -17.7 / -27.7 |
| Switch BTC 3-day persist | -31.7 / -40.2 | -13.1 / -27.5 | -21.2 / -29.7 |
| Breakout 20/50/100 + BTC filter ±2% | -3.2 / -20.2 | +5.3 / -15.8 | +0.8 / -18.7 |

| Breakout lookbacks (no filter) | Return | Max DD | Orders | Fees £ |
|---|---|---|---|---|
| 10/20/50 | -17.5% | -41.5% | 399 | 226 |
| 20/50/100 | -6.0% | -29.9% | 218 | 116 |
| 50/100/200 | -13.2% | -23.6% | 120 | 55 |
| 20 only | -4.0% | -38.4% | 154 | 220 |
| 50 only | -1.4% | -28.6% | 85 | 94 |
| 100 only | -16.7% | -26.0% | 60 | 52 |
| 20/50/100/200 | -9.9% | -27.2% | 227 | 90 |
| 20/50/100, rebalance buffer 5% / 25% / 50% | -6.4 / -6.7 / -5.4% | ~-29% | 246 / 193 / 130 | 118 / 112 / 88 |

What this shows: the "~0%" trend switch at SMA200 is a lucky setting. 150 and 250 days lost 17-38%. The breakout ensemble with the BTC filter is the most stable idea tested (-3% to +5% across filter lengths, drawdown 16-20%), but it is still not clearly profitable.

## Quarter by quarter (Kraken T2 0.60%, % change)
| Quarter | B&H basket | B&H BTC | Switch basket | Switch BTC | Breakout (no filter) |
|---|---|---|---|---|---|
| 2025-Q1 (from 25 Mar) | -10.6 | -6.3 | 0.0 | 0.0 | 0.0 |
| 2025-Q2 | +8.4 | +22.2 | -0.5 | +6.8 | +1.9 |
| 2025-Q3 | +43.7 | +8.8 | +45.6 | +8.8 | +9.0 |
| 2025-Q4 | -37.5 | -23.5 | -23.1 | -8.9 | -6.8 |
| 2026-Q1 | -26.8 | -20.7 | 0.0 | 0.0 | -8.4 |
| 2026-Q2 | -20.4 | -14.2 | 0.0 | 0.0 | -5.3 |
| 2026-Q3 | +66.7 | +42.6 | +27.1 | +16.9 | +19.9 |
| 2026-Q4 | -34.1 | -25.5 | -28.5 | -18.5 | -10.1 |

The pattern: the slow filters sit in cash during long slides (Q1-Q2 2026), but they still take the first big leg of each crash (Q4 2025, Q4 2026) before switching off, and they miss part of each rally.

## Caveats
- About 1.7 years, mostly falling, one market: thin evidence. One lucky or unlucky signal flip moves the result by 10-20 points.
- The 5 coins were chosen with hindsight (survivorship); no XRP data.
- Daily rules were simplified versions of the published ones (closes only, no 25% volatility target, no leverage, 5 coins rather than 20).
- Maker 0.25% assumes every limit order fills; the research says only about half do, and the missed ones tend to be the winners.
- The current bot's line comes from its own 4h engine (with XRP, and its own risk rules), so it is close to comparable, not exactly.
