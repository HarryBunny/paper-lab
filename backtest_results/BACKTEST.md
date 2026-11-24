# Backtest: 730 days of GBP crypto, same engine as the live bot

Data: Coinbase Exchange 1h candles, downloaded 2026-11-24T11:57Z. Fees 0.80% a side + slippage.
Parameters were chosen before seeing this data and not tuned, so this whole period is out-of-sample.

**Pass bar** (profitable after costs, beats buy & hold, survives double fees, 50+ trades): **FAIL**

## Headline and stress tests

| run | return_pct | max_dd_pct | sharpe | trades | win_rate_pct | profit_factor | fees_gbp | bh_basket_return_pct | bh_basket_max_dd_pct | kill_switch_would_fire |
|---|---|---|---|---|---|---|---|---|---|---|
| base | -31.9 | -35.3 | -1.17 | 208 | 30.3 | 0.61 | 487.94 | -55.6 | -70.7 | 2025-07-03 |
| double fees | -51.7 | -53.2 | -2.66 | 208 | 23.6 | 0.35 | 648.04 | -55.6 | -70.7 | 2025-02-03 |
| maker fees (0.40%) | -10.9 | -27.5 | -0.26 | 208 | 37.0 | 0.87 | 311.84 | -55.6 | -70.7 | 2026-07-28 |
| breakout 20 bars | -46.7 | -49.4 | -1.85 | 244 | 27.0 | 0.52 | 517.3 | -55.6 | -70.7 | 2025-05-02 |
| breakout 45 bars | -31.3 | -35.2 | -1.19 | 198 | 31.3 | 0.61 | 453.91 | -55.6 | -70.7 | 2025-06-30 |
| stop 2.0 ATR | -39.6 | -43.0 | -1.46 | 229 | 29.7 | 0.59 | 586.24 | -55.6 | -70.7 | 2025-05-08 |
| stop 3.0 ATR | -22.0 | -29.2 | -0.76 | 190 | 33.2 | 0.69 | 410.15 | -55.6 | -70.7 | 2025-07-01 |
| trend only | -27.4 | -31.4 | -1.11 | 138 | 22.5 | 0.56 | 331.62 | -55.6 | -70.7 | 2025-05-08 |
| meanrev only | -6.2 | -14.0 | -0.42 | 70 | 45.7 | 0.73 | 181.35 | -55.6 | -70.7 | never |

## What one week tells you

Every rolling 7-day window in the backtest:

```
{
 "windows": 4362,
 "pct_weeks_positive": 16.2,
 "median_week_pct": 0.0,
 "best_week_pct": 12.7,
 "worst_week_pct": -5.99,
 "p10_p90_pct": [
  -2.93,
  1.16
 ]
}
```

## Quarter by quarter

| quarter | bot_pct | bh_basket_pct |
|---|---|---|
| 2024-Q4 | -0.6 | 9.7 |
| 2025-Q1 | -3.6 | -31.3 |
| 2025-Q2 | -4.4 | 7.6 |
| 2025-Q3 | 2.7 | 42.8 |
| 2025-Q4 | -2.1 | -38.4 |
| 2026-Q1 | -8.9 | -26.4 |
| 2026-Q2 | -10.3 | -20.6 |
| 2026-Q3 | -7.6 | 66.4 |
| 2026-Q4 | -1.8 | -34.3 |

## By strategy

| strategy | count | sum | mean |
|---|---|---|---|
| meanrev | 70 | -61.4 | -0.88 |
| trend | 138 | -257.88 | -1.87 |

Time in each regime (%): {'trend_down': 45.4, 'trend_up': 42.4, 'range': 12.2}

Data notes: BTC: 2 gap(s) in 60m candles; ETH: 2 gap(s) in 60m candles; SOL: 2 gap(s) in 60m candles; XRP: not enough Coinbase GBP history, left out of the backtest; ADA: 73 gap(s) in 60m candles; LINK: 461 gap(s) in 60m candles
