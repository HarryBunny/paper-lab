Synthetic (USD x implied FX) days in window: {'BTC': 0, 'ETH': 0, 'SOL': 0, 'XRP': 1924, 'ADA': 0, 'LINK': 390}
Lookahead check (truncate data after 2023-06-30, re-run, compare): PASS for all 31 strategies

## Full window 2019-01-01 -> 2026-11-23, taker 0.80% + slippage, £1,000 start

| Strategy | CAGR (0% cash) | CAGR (4% cash) | Max DD | Worst yr | Up yrs | Orders/yr | Fees £/yr (% of avg equity) | Disposals/yr | Proceeds £/yr | Acct size for £50k proceeds | CAGR maker 0.40% (0%/4% cash) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B&H BTC | +41.8% | +41.8% | -73% | -60% | 5/8 | 0.1 | 1 (0.0%) | 0.0 | 0 | never | +41.9% / +41.9% |
| B&H BTC+ETH 50/50 | +39.8% | +39.8% | -74% | -63% | 5/8 | 0.3 | 1 (0.0%) | 0.0 | 0 | never | +39.8% / +39.8% |
| EW basket (6, yearly rebal) | +42.9% | +43.1% | -73% | -61% | 5/8 | 6.5 | 48 (0.3%) | 2.4 | 2,983 | £257,950 | +43.4% / +43.6% |
| DCA BTC monthly | +15.5% | +16.8% | -59% | -44% | 5/8 | 8.6 | 1 (0.0%) | 0.0 | 0 | never | +15.5% / +16.8% |
| BTC MA200 ±2% daily | +30.6% | +32.7% | -60% | -13% | 5/8 | 3.8 | 127 (2.5%) | 1.9 | 8,481 | £30,640 | +32.6% / +34.8% |
| BTC MA200 ±2% weekly | +27.5% | +29.7% | -67% | -11% | 5/8 | 2.8 | 97 (2.1%) | 1.4 | 6,474 | £35,316 | +29.0% / +31.1% |
| BTC MA-ensemble daily | +32.6% | +35.0% | -58% | -32% | 5/8 | 26.3 | 401 (6.3%) | 14.1 | 25,768 | £12,435 | +37.0% / +39.8% |
| BTC MA-ensemble weekly | +30.9% | +33.5% | -51% | -20% | 5/8 | 13.6 | 246 (3.9%) | 7.2 | 15,976 | £19,845 | +33.7% / +36.0% |
| Own MA50 ±2% BTC+ETH | +45.5% | +48.2% | -51% | -38% | 7/8 | 21.0 | 858 (8.1%) | 10.5 | 55,197 | £9,590 | +51.8% / +54.6% |
| Own MA30 ±5% BTC+ETH | +42.7% | +45.2% | -54% | -35% | 7/8 | 17.2 | 634 (6.6%) | 8.6 | 40,916 | £11,679 | +47.7% / +50.4% |
| Own MA75 ±0% BTC+ETH | +26.6% | +28.9% | -67% | -54% | 7/8 | 34.7 | 601 (13.0%) | 17.4 | 38,206 | £6,040 | +35.4% / +37.8% |
| B&H-gate: BTC+ETH while BTC>MA200±2% | +36.3% | +38.6% | -59% | -12% | 5/8 | 7.6 | 184 (2.4%) | 3.8 | 12,235 | £31,739 | +38.4% / +40.7% |
| Lab B narrow + gate | +35.1% | +39.0% | -34% | -4% | 6/8 | 80.7 | 262 (4.7%) | 43.4 | 17,113 | £16,306 | +38.7% / +42.7% |
| Lab B narrow, no gate | +33.4% | +36.9% | -45% | -30% | 5/8 | 112.2 | 369 (6.3%) | 57.6 | 23,771 | £12,241 | +37.7% / +41.4% |
| Lab B wide + gate | +29.7% | +33.4% | -35% | -10% | 5/8 | 110.7 | 179 (3.8%) | 60.4 | 11,680 | £20,259 | +32.6% / +36.4% |
| Lab B wide, no gate | +27.6% | +31.0% | -40% | -21% | 5/8 | 185.5 | 264 (5.6%) | 96.0 | 16,984 | £13,881 | +31.4% / +35.0% |
| Lab B wide, no gate, equal-wt | +27.6% | +31.7% | -40% | -21% | 5/8 | 184.8 | 261 (5.6%) | 95.1 | 16,812 | £13,838 | +31.6% / +35.2% |
| Lab B wide, no gate, no band | +25.2% | +28.6% | -42% | -21% | 5/8 | 358.4 | 317 (7.4%) | 185.4 | 20,285 | £10,616 | +29.8% / +33.4% |
| Lab B wide, no gate, no ratchet | +27.6% | +31.0% | -40% | -21% | 5/8 | 185.5 | 264 (5.6%) | 96.0 | 16,984 | £13,881 | +31.4% / +35.0% |
| Lab B wide, no gate, BTC+ETH only | +23.0% | +25.3% | -39% | -15% | 5/8 | 67.9 | 170 (4.3%) | 34.7 | 10,941 | £18,092 | +25.2% / +27.8% |
| Lab B narrow + gate, equal-wt | +35.9% | +40.1% | -35% | -5% | 6/8 | 82.6 | 280 (4.8%) | 44.5 | 18,283 | £16,094 | +39.7% / +43.7% |
| Lab B narrow + gate, equal-wt, weekly | +30.5% | +34.2% | -44% | -4% | 5/8 | 58.9 | 180 (4.0%) | 32.2 | 11,814 | £19,278 | +33.2% / +37.0% |
| Lab B narrow + gate, equal-wt, 50% band | +36.9% | +40.9% | -36% | -3% | 6/8 | 47.0 | 224 (3.6%) | 24.3 | 14,774 | £21,228 | +39.8% / +43.7% |
| Lab B narrow + gate, BTC+ETH only | +34.8% | +38.3% | -35% | +0% | 7/8 | 33.2 | 274 (4.7%) | 17.7 | 17,847 | £16,395 | +38.1% / +41.7% |
| Gate-only basket: EW 6 while BTC>MA200±2% | +40.8% | +43.0% | -57% | -19% | 5/8 | 28.2 | 233 (2.6%) | 13.6 | 15,545 | £28,829 | +43.9% / +46.1% |
| BTC vol-target 40% | +31.5% | +32.6% | -59% | -48% | 5/8 | 7.1 | 73 (1.1%) | 3.4 | 4,632 | £71,890 | +32.5% / +33.5% |
| BTC MA200±2% x vol-target | +22.4% | +25.1% | -46% | -11% | 5/8 | 7.5 | 93 (2.7%) | 3.9 | 6,093 | £28,055 | +24.3% / +26.7% |
| BTC MA-ensemble x vol-target | +25.4% | +28.1% | -48% | -25% | 5/8 | 28.6 | 243 (5.6%) | 14.4 | 15,600 | £13,866 | +28.7% / +31.6% |
| BTC/cash 50/50, 15pt band | +24.9% | +29.8% | -45% | -32% | 5/8 | 1.0 | 5 (0.1%) | 0.8 | 447 | £467,752 | +25.0% / +29.9% |
| Core-sat: 50% B&H BTC + 50% BTC MA-ensemble | +37.7% | +38.7% | -66% | -50% | 5/8 | 26.5 | 201 (2.2%) | 14.1 | 12,884 | £34,920 | +39.6% / +40.9% |
| Core-sat: 50% B&H BTC + 50% Lab B wide no gate | +36.0% | +37.1% | -63% | -49% | 5/8 | 185.7 | 132 (1.6%) | 96.0 | 8,492 | £47,995 | +37.3% / +38.7% |

## Calendar-year returns (taker 0.80%, 0% on cash; 2026 = to 23 Nov)

| Strategy | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| B&H BTC | +83% | +290% | +61% | -60% | +144% | +124% | -13% | -28% |
| B&H BTC+ETH 50/50 | +38% | +344% | +203% | -63% | +102% | +79% | -15% | -34% |
| EW basket (6, yearly rebal) | +12% | +315% | +281% | -61% | +198% | +97% | -32% | -39% |
| DCA BTC monthly | +2% | +65% | +35% | -44% | +88% | +103% | -12% | -27% |
| BTC MA200 ±2% daily | +44% | +131% | +8% | -1% | +60% | +73% | -13% | -5% |
| BTC MA200 ±2% weekly | +69% | +78% | +6% | -1% | +59% | +69% | -9% | -11% |
| BTC MA-ensemble daily | +61% | +196% | +34% | -32% | +64% | +61% | -13% | -7% |
| BTC MA-ensemble weekly | +76% | +145% | +34% | -20% | +50% | +65% | -12% | -17% |
| Own MA50 ±2% BTC+ETH | +21% | +269% | +198% | -38% | +54% | +34% | +6% | +7% |
| Own MA30 ±5% BTC+ETH | +37% | +301% | +123% | -35% | +33% | +40% | +1% | +11% |
| Own MA75 ±0% BTC+ETH | +73% | +105% | +99% | -54% | +39% | +30% | +4% | +5% |
| B&H-gate: BTC+ETH while BTC>MA200±2% | +21% | +164% | +116% | -1% | +33% | +47% | -2% | -12% |
| Lab B narrow + gate | +32% | +90% | +82% | +0% | +36% | +77% | -4% | +3% |
| Lab B narrow, no gate | +36% | +121% | +99% | -30% | +61% | +64% | -3% | -8% |
| Lab B wide + gate | +22% | +99% | +74% | -0% | +31% | +59% | -10% | -1% |
| Lab B wide, no gate | +26% | +109% | +82% | -21% | +46% | +58% | -12% | -11% |
| Lab B wide, no gate, equal-wt | +22% | +106% | +84% | -21% | +52% | +60% | -13% | -12% |
| Lab B wide, no gate, no band | +24% | +108% | +82% | -21% | +36% | +50% | -14% | -10% |
| Lab B wide, no gate, no ratchet | +26% | +109% | +82% | -21% | +46% | +58% | -12% | -11% |
| Lab B wide, no gate, BTC+ETH only | +28% | +90% | +77% | -15% | +19% | +39% | -6% | -10% |
| Lab B narrow + gate, equal-wt | +31% | +96% | +90% | +0% | +36% | +76% | -5% | +1% |
| Lab B narrow + gate, equal-wt, weekly | +20% | +92% | +70% | -0% | +22% | +79% | -1% | -4% |
| Lab B narrow + gate, equal-wt, 50% band | +37% | +100% | +101% | +0% | +33% | +61% | -3% | +4% |
| Lab B narrow + gate, BTC+ETH only | +54% | +80% | +86% | +0% | +21% | +47% | +14% | +1% |
| Gate-only basket: EW 6 while BTC>MA200±2% | +4% | +127% | +166% | -1% | +95% | +71% | -19% | -12% |
| BTC vol-target 40% | +80% | +131% | +46% | -48% | +118% | +102% | -11% | -30% |
| BTC MA200±2% x vol-target | +32% | +94% | +5% | -0% | +39% | +57% | -11% | -5% |
| BTC MA-ensemble x vol-target | +68% | +122% | +13% | -25% | +41% | +62% | -13% | -6% |
| BTC/cash 50/50, 15pt band | +42% | +118% | +33% | -32% | +62% | +58% | -7% | -13% |
| Core-sat: 50% B&H BTC + 50% BTC MA-ensemble | +72% | +246% | +50% | -50% | +105% | +99% | -13% | -21% |
| Core-sat: 50% B&H BTC + 50% Lab B wide no gate | +54% | +216% | +67% | -49% | +99% | +102% | -13% | -23% |

## Round-trip stats (taker, 0% cash): one round trip = position opened from zero and closed to zero

| Strategy | Round trips | Mean net per trip | 95% CI ± | Win rate |
|---|---|---|---|---|
| BTC MA200 ±2% daily | 15 | +26.5% | 36.8pt | 40% |
| BTC MA200 ±2% weekly | 11 | +35.2% | 50.6pt | 55% |
| BTC MA-ensemble daily | 57 | +1.2% | 8.7pt | 12% |
| BTC MA-ensemble weekly | 21 | +11.2% | 21.6pt | 29% |
| Own MA50 ±2% BTC+ETH | 83 | +13.7% | 11.6pt | 41% |
| Own MA30 ±5% BTC+ETH | 68 | +14.3% | 11.0pt | 47% |
| Own MA75 ±0% BTC+ETH | 137 | +7.6% | 9.0pt | 20% |
| B&H-gate: BTC+ETH while BTC>MA200±2% | 30 | +46.0% | 60.2pt | 43% |
| Lab B narrow + gate | 130 | +3.0% | 4.7pt | 32% |
| Lab B narrow, no gate | 212 | -0.6% | 3.0pt | 26% |
| Lab B wide + gate | 154 | +1.9% | 4.4pt | 23% |
| Lab B wide, no gate | 313 | -2.3% | 2.0pt | 17% |
| Lab B wide, no gate, equal-wt | 313 | -2.1% | 2.3pt | 16% |
| Lab B wide, no gate, no band | 313 | -3.9% | 1.1pt | 16% |
| Lab B wide, no gate, no ratchet | 313 | -2.3% | 2.0pt | 17% |
| Lab B wide, no gate, BTC+ETH only | 90 | -0.8% | 3.7pt | 20% |
| Lab B narrow + gate, equal-wt | 130 | +3.2% | 5.6pt | 31% |
| Lab B narrow + gate, equal-wt, weekly | 104 | +4.9% | 5.7pt | 38% |
| Lab B narrow + gate, equal-wt, 50% band | 130 | +7.9% | 7.1pt | 35% |
| Lab B narrow + gate, BTC+ETH only | 41 | +2.9% | 5.2pt | 44% |
| Gate-only basket: EW 6 while BTC>MA200±2% | 76 | +27.8% | 24.9pt | 36% |
| BTC MA200±2% x vol-target | 15 | +5.9% | 13.4pt | 40% |
| BTC MA-ensemble x vol-target | 57 | -2.4% | 3.4pt | 12% |
| Core-sat: 50% B&H BTC + 50% BTC MA-ensemble | 57 | +1.2% | 8.7pt | 12% |
| Core-sat: 50% B&H BTC + 50% Lab B wide no gate | 313 | -2.3% | 2.0pt | 17% |

## Rolling 2-year runs, new start every quarter 2019Q1-2024Q4 (24 starts), taker, 0% on cash

| Strategy | Median 2y return | 10th pct | 90th pct | % starts > 0 | % starts beating B&H BTC | Median max DD | Worst max DD |
|---|---|---|---|---|---|---|---|
| B&H BTC | +145% | -26% | +550% | 71% | 0% | -53% | -73% |
| B&H BTC+ETH 50/50 | +119% | -25% | +1111% | 75% | 38% | -58% | -75% |
| EW basket (6, yearly rebal) | +184% | -16% | +1013% | 88% | 62% | -60% | -73% |
| DCA BTC monthly | +75% | -24% | +207% | 67% | 21% | -40% | -67% |
| BTC MA200 ±2% daily | +85% | +2% | +216% | 92% | 42% | -32% | -60% |
| BTC MA200 ±2% weekly | +88% | +3% | +199% | 92% | 42% | -38% | -67% |
| BTC MA-ensemble daily | +88% | -13% | +291% | 79% | 42% | -36% | -58% |
| BTC MA-ensemble weekly | +79% | -6% | +293% | 88% | 42% | -37% | -51% |
| Own MA50 ±2% BTC+ETH | +67% | -0% | +727% | 88% | 54% | -35% | -51% |
| Own MA30 ±5% BTC+ETH | +68% | -6% | +643% | 79% | 54% | -44% | -51% |
| Own MA75 ±0% BTC+ETH | +41% | -37% | +319% | 71% | 25% | -45% | -68% |
| B&H-gate: BTC+ETH while BTC>MA200±2% | +115% | +10% | +541% | 92% | 58% | -39% | -59% |
| Lab B narrow + gate | +104% | +13% | +255% | 92% | 46% | -23% | -34% |
| Lab B narrow, no gate | +87% | -3% | +328% | 88% | 42% | -28% | -45% |
| Lab B wide + gate | +85% | -2% | +250% | 88% | 46% | -24% | -31% |
| Lab B wide, no gate | +74% | -9% | +281% | 83% | 38% | -30% | -40% |
| Lab B wide, no gate, equal-wt | +80% | -7% | +280% | 88% | 33% | -31% | -39% |
| Lab B wide, no gate, no band | +58% | -11% | +275% | 83% | 38% | -30% | -39% |
| Lab B wide, no gate, no ratchet | +74% | -9% | +281% | 83% | 38% | -30% | -40% |
| Lab B wide, no gate, BTC+ETH only | +45% | -12% | +227% | 79% | 29% | -24% | -38% |
| Lab B narrow + gate, equal-wt | +108% | +13% | +279% | 96% | 46% | -25% | -33% |
| Lab B narrow + gate, equal-wt, weekly | +98% | -4% | +261% | 88% | 38% | -29% | -38% |
| Lab B narrow + gate, equal-wt, 50% band | +104% | +17% | +318% | 96% | 42% | -26% | -33% |
| Lab B narrow + gate, BTC+ETH only | +74% | +6% | +245% | 92% | 50% | -24% | -35% |
| Gate-only basket: EW 6 while BTC>MA200±2% | +115% | +21% | +496% | 92% | 50% | -42% | -57% |
| BTC vol-target 40% | +100% | -18% | +311% | 75% | 21% | -45% | -63% |
| BTC MA200±2% x vol-target | +63% | -2% | +137% | 79% | 42% | -27% | -46% |
| BTC MA-ensemble x vol-target | +65% | -20% | +151% | 79% | 25% | -27% | -47% |
| BTC/cash 50/50, 15pt band | +73% | -8% | +195% | 83% | 29% | -31% | -46% |
| Core-sat: 50% B&H BTC + 50% BTC MA-ensemble | +126% | -19% | +417% | 75% | 42% | -46% | -65% |
| Core-sat: 50% B&H BTC + 50% Lab B wide no gate | +127% | -8% | +398% | 79% | 38% | -42% | -57% |

## Rolling 2-year runs, new start every quarter 2019Q1-2024Q4 (24 starts), taker, 4% on cash

| Strategy | Median 2y return | 10th pct | 90th pct | % starts > 0 | % starts beating B&H BTC | Median max DD | Worst max DD |
|---|---|---|---|---|---|---|---|
| B&H BTC | +145% | -26% | +550% | 71% | 0% | -53% | -73% |
| B&H BTC+ETH 50/50 | +119% | -25% | +1111% | 75% | 38% | -58% | -75% |
| EW basket (6, yearly rebal) | +186% | -15% | +1015% | 88% | 62% | -60% | -73% |
| DCA BTC monthly | +80% | -21% | +215% | 75% | 21% | -39% | -67% |
| BTC MA200 ±2% daily | +89% | +7% | +224% | 92% | 46% | -31% | -59% |
| BTC MA200 ±2% weekly | +91% | +7% | +208% | 92% | 46% | -37% | -66% |
| BTC MA-ensemble daily | +95% | -9% | +301% | 79% | 46% | -35% | -57% |
| BTC MA-ensemble weekly | +86% | -1% | +307% | 88% | 42% | -35% | -49% |
| Own MA50 ±2% BTC+ETH | +73% | +4% | +751% | 88% | 58% | -34% | -50% |
| Own MA30 ±5% BTC+ETH | +75% | -1% | +664% | 88% | 54% | -43% | -49% |
| Own MA75 ±0% BTC+ETH | +46% | -35% | +329% | 79% | 25% | -44% | -66% |
| B&H-gate: BTC+ETH while BTC>MA200±2% | +119% | +15% | +556% | 96% | 62% | -39% | -59% |
| Lab B narrow + gate | +115% | +20% | +272% | 96% | 46% | -21% | -32% |
| Lab B narrow, no gate | +97% | +2% | +347% | 88% | 46% | -27% | -43% |
| Lab B wide + gate | +95% | +5% | +267% | 96% | 50% | -22% | -29% |
| Lab B wide, no gate | +82% | -3% | +297% | 88% | 50% | -28% | -37% |
| Lab B wide, no gate, equal-wt | +91% | -2% | +308% | 88% | 50% | -30% | -35% |
| Lab B wide, no gate, no band | +66% | -6% | +292% | 83% | 38% | -29% | -36% |
| Lab B wide, no gate, no ratchet | +82% | -3% | +297% | 88% | 50% | -28% | -37% |
| Lab B wide, no gate, BTC+ETH only | +51% | -6% | +226% | 83% | 33% | -22% | -35% |
| Lab B narrow + gate, equal-wt | +124% | +21% | +297% | 96% | 50% | -24% | -32% |
| Lab B narrow + gate, equal-wt, weekly | +109% | +2% | +278% | 88% | 42% | -26% | -37% |
| Lab B narrow + gate, equal-wt, 50% band | +117% | +25% | +337% | 96% | 50% | -25% | -31% |
| Lab B narrow + gate, BTC+ETH only | +83% | +12% | +260% | 100% | 50% | -23% | -33% |
| Gate-only basket: EW 6 while BTC>MA200±2% | +124% | +27% | +509% | 92% | 54% | -41% | -57% |
| BTC vol-target 40% | +106% | -17% | +323% | 79% | 21% | -45% | -63% |
| BTC MA200±2% x vol-target | +69% | +3% | +147% | 92% | 46% | -27% | -45% |
| BTC MA-ensemble x vol-target | +71% | -15% | +162% | 79% | 33% | -26% | -45% |
| BTC/cash 50/50, 15pt band | +79% | -3% | +209% | 79% | 33% | -32% | -45% |
| Core-sat: 50% B&H BTC + 50% BTC MA-ensemble | +130% | -17% | +422% | 75% | 46% | -45% | -64% |
| Core-sat: 50% B&H BTC + 50% Lab B wide no gate | +132% | -5% | +406% | 83% | 50% | -41% | -56% |

## Parameter plateau (full window, taker, 0% cash): spread across each family's grid

| Family | Variants | CAGR min | CAGR median | CAGR max | Max DD median | Max DD worst | Orders/yr median |
|---|---|---|---|---|---|---|---|
| BTC MA | 30 | +15.3% | +29.5% | +47.9% | -63% | -75% | 3.8 |
| BTC ensemble | 10 | +27.8% | +33.2% | +39.6% | -51% | -62% | 17.0 |
| Ens x vol | 12 | +21.6% | +26.5% | +31.9% | -52% | -58% | 28.2 |
| Fixed mix | 9 | +14.8% | +25.2% | +37.5% | -45% | -61% | 1.0 |
| Lab B | 20 | +22.9% | +30.0% | +37.2% | -38% | -48% | 120.3 |
| Own-MA BTC+ETH | 21 | +2.5% | +38.5% | +46.3% | -58% | -84% | 21.0 |
| Vol-target | 12 | +20.5% | +31.1% | +37.1% | -67% | -74% | 5.6 |

Detail for the main families:

| Variant | CAGR | Max DD | Worst yr | Orders/yr |
|---|---|---|---|---|
| BTC MA100 ±2% daily | +46.1% | -52% | -35% | 5.8 |
| BTC MA100 ±2% weekly | +36.9% | -58% | -35% | 4.3 |
| BTC MA150 ±2% daily | +36.8% | -47% | -26% | 4.3 |
| BTC MA150 ±2% weekly | +22.5% | -66% | -24% | 3.5 |
| BTC MA200 ±2% daily | +30.6% | -60% | -13% | 3.8 |
| BTC MA200 ±2% weekly | +27.5% | -67% | -11% | 2.8 |
| BTC MA250 ±2% daily | +19.8% | -73% | -22% | 4.8 |
| BTC MA250 ±2% weekly | +32.7% | -56% | -11% | 2.5 |
| BTC MA300 ±2% daily | +29.3% | -64% | -13% | 3.8 |
| BTC MA300 ±2% weekly | +26.3% | -69% | -14% | 2.8 |
| BTC ens x0.5 (25, 50, 75, 100, 125) daily | +33.8% | -62% | -51% | 39.0 |
| BTC ens x0.5 (25, 50, 75, 100, 125) weekly | +37.5% | -47% | -31% | 18.5 |
| BTC ens x0.75 (38, 75, 112, 150, 188) daily | +39.6% | -52% | -34% | 27.0 |
| BTC ens x0.75 (38, 75, 112, 150, 188) weekly | +33.3% | -51% | -29% | 15.1 |
| BTC ens x1.0 (50, 100, 150, 200, 250) daily | +32.6% | -58% | -32% | 26.3 |
| BTC ens x1.0 (50, 100, 150, 200, 250) weekly | +30.9% | -51% | -20% | 13.6 |
| BTC ens x1.25 (62, 125, 188, 250, 312) daily | +33.1% | -51% | -23% | 21.2 |
| BTC ens x1.25 (62, 125, 188, 250, 312) weekly | +28.5% | -53% | -15% | 11.5 |
| BTC ens x1.5 (75, 150, 225, 300, 375) daily | +35.3% | -51% | -22% | 15.5 |
| BTC ens x1.5 (75, 150, 225, 300, 375) weekly | +27.8% | -56% | -20% | 9.4 |
| Own MA25 ±0% BTC+ETH | +2.5% | -84% | -46% | 73.2 |
| Own MA25 ±2% BTC+ETH | +32.6% | -58% | -39% | 33.4 |
| Own MA25 ±5% BTC+ETH | +38.4% | -58% | -35% | 19.5 |
| Own MA30 ±0% BTC+ETH | +20.4% | -64% | -38% | 60.5 |
| Own MA30 ±2% BTC+ETH | +35.5% | -59% | -43% | 29.1 |
| Own MA30 ±5% BTC+ETH | +42.7% | -54% | -35% | 17.2 |
| Own MA40 ±0% BTC+ETH | +32.6% | -60% | -45% | 48.1 |
| Own MA40 ±2% BTC+ETH | +45.8% | -58% | -41% | 24.6 |
| Own MA40 ±5% BTC+ETH | +45.2% | -57% | -40% | 14.7 |
| Own MA50 ±0% BTC+ETH | +29.5% | -64% | -53% | 43.3 |
| Own MA50 ±2% BTC+ETH | +45.5% | -51% | -38% | 21.0 |
| Own MA50 ±5% BTC+ETH | +41.6% | -57% | -43% | 13.7 |
| Own MA63 ±0% BTC+ETH | +27.3% | -59% | -48% | 38.5 |
| Own MA63 ±2% BTC+ETH | +40.3% | -54% | -43% | 18.5 |
| Own MA63 ±5% BTC+ETH | +42.9% | -46% | -30% | 11.4 |
| Own MA75 ±0% BTC+ETH | +26.6% | -67% | -54% | 34.7 |
| Own MA75 ±2% BTC+ETH | +38.5% | -55% | -41% | 16.5 |
| Own MA75 ±5% BTC+ETH | +43.1% | -55% | -42% | 9.9 |
| Own MA100 ±0% BTC+ETH | +29.6% | -66% | -47% | 26.6 |
| Own MA100 ±2% BTC+ETH | +40.3% | -60% | -40% | 12.2 |
| Own MA100 ±5% BTC+ETH | +46.3% | -48% | -30% | 7.1 |
| Lab B narrow x0.5 nogate | +30.2% | -47% | -39% | 211.1 |
| Lab B narrow x0.5 gate | +33.6% | -32% | -8% | 137.5 |
| Lab B wide x0.5 nogate | +22.9% | -48% | -32% | 336.0 |
| Lab B wide x0.5 gate | +27.7% | -34% | -13% | 185.3 |
| Lab B narrow x0.75 nogate | +34.3% | -47% | -36% | 140.6 |
| Lab B narrow x0.75 gate | +37.2% | -32% | -4% | 96.9 |
| Lab B wide x0.75 nogate | +26.0% | -41% | -26% | 226.6 |
| Lab B wide x0.75 gate | +28.8% | -35% | -13% | 132.6 |
| Lab B narrow x1.0 nogate | +33.4% | -45% | -30% | 112.2 |
| Lab B narrow x1.0 gate | +35.1% | -34% | -4% | 80.7 |
| Lab B wide x1.0 nogate | +27.6% | -40% | -21% | 185.5 |
| Lab B wide x1.0 gate | +29.7% | -35% | -10% | 110.7 |
| Lab B narrow x1.25 nogate | +33.9% | -41% | -26% | 94.5 |
| Lab B narrow x1.25 gate | +35.3% | -32% | -8% | 71.4 |
| Lab B wide x1.25 nogate | +26.2% | -42% | -19% | 157.2 |
| Lab B wide x1.25 gate | +28.2% | -36% | -12% | 95.2 |
| Lab B narrow x1.5 nogate | +30.3% | -46% | -25% | 81.1 |
| Lab B narrow x1.5 gate | +33.1% | -37% | -8% | 63.5 |
| Lab B wide x1.5 nogate | +25.0% | -44% | -21% | 128.3 |
| Lab B wide x1.5 gate | +27.4% | -37% | -11% | 81.3 |

## Walk-forward: pick best CAGR/MaxDD on 2019-2022 within each family, then test once on 2023-01-01 -> 2026-11-23 (taker, 0% cash)

B&H BTC: train CAGR +46.4% / DD -73%; test CAGR +37.0% / DD -52%

| Family | Pick (chosen on 2019-22) | Train CAGR / DD | Test CAGR / DD | Test rank in family (by MAR) | Family median test CAGR / DD |
|---|---|---|---|---|---|
| BTC MA | BTC MA100 ±4% daily | +67.8% / -51% | +29.9% / -29% | 1 of 30 | +18.6% / -37% |
| BTC ensemble | BTC ens x0.5 (25, 50, 75, 100, 125) weekly | +60.2% / -47% | +17.5% / -39% | 9 of 10 | +20.9% / -32% |
| Ens x vol | BTC ens x vol-target 30% rv60 | +30.3% / -31% | +15.9% / -27% | 11 of 12 | +21.4% / -30% |
| Fixed mix | BTC/cash 30/70 band 20 | +22.6% / -26% | +15.5% / -18% | 1 of 9 | +20.6% / -30% |
| Lab B | Lab B narrow x1.25 gate | +52.5% / -32% | +19.6% / -22% | 3 of 20 | +16.7% / -28% |
| Own-MA BTC+ETH | Own MA63 ±5% BTC+ETH | +66.8% / -44% | +22.2% / -42% | 9 of 21 | +19.6% / -39% |
| Vol-target | BTC vol-target 40% rv30 | +33.1% / -59% | +28.4% / -50% | 7 of 12 | +30.4% / -51% |

Global pick across all 114 grid variants (best 2019-22 MAR): **Lab B narrow x1.25 gate** -> test CAGR +19.6%, DD -22%
Rank correlation of train MAR vs test MAR across all grid variants: 0.13

## Fee sweep: full-window CAGR by fee per side (slippage on top, 0% cash)

| Strategy | 0.25% | 0.40% | 0.60% | 0.80% | 1.20% |
|---|---|---|---|---|---|
| Lab B narrow + gate, equal-wt | +41.0% | +39.7% | +38.0% | +35.9% | +32.4% |
| Gate-only basket: EW 6 while BTC>MA200±2% | +45.1% | +43.9% | +42.2% | +40.8% | +38.7% |
| BTC MA200 ±2% daily | +33.3% | +32.6% | +31.6% | +30.6% | +28.6% |
| BTC MA-ensemble daily | +38.6% | +37.0% | +34.8% | +32.6% | +29.2% |
| BTC MA-ensemble weekly | +34.6% | +33.7% | +32.4% | +30.9% | +28.2% |
| Own MA50 ±2% BTC+ETH | +54.2% | +51.8% | +48.6% | +45.5% | +39.5% |
| Lab B narrow + gate | +40.1% | +38.7% | +37.0% | +35.1% | +32.3% |
| Lab B wide, no gate | +32.7% | +31.4% | +29.4% | +27.6% | +24.1% |
| BTC vol-target 40% | +32.8% | +32.5% | +32.0% | +31.5% | +30.6% |
| BTC/cash 50/50, 15pt band | +25.0% | +25.0% | +25.0% | +24.9% | +24.9% |

## Is own-MA just bear-market avoidance? Excess log return vs B&H BTC+ETH, split by BTC regime

| Strategy | Excess when BTC > MA200 | Excess when BTC < MA200 | Bull days | Bear days |
|---|---|---|---|---|
| Own MA50 ±2% BTC+ETH | -0.17 | +0.49 | 1670 | 1214 |
| Own MA30 ±5% BTC+ETH | -0.11 | +0.27 | 1670 | 1214 |
| B&H-gate: BTC+ETH while BTC>MA200±2% | -0.22 | +0.06 | 1670 | 1214 |
| Lab B wide, no gate, BTC+ETH only | -0.99 | +0.00 | 1670 | 1214 |

## Survivorship check: Lab B narrow + gate (equal-wt) with one coin removed (full window, taker, 0% cash)

| Coins | CAGR | Max DD | Worst yr |
|---|---|---|---|
| all 6 | +35.9% | -35% | -5% |
| -BTC | +29.5% | -39% | -5% |
| -ETH | +33.3% | -37% | -13% |
| -SOL | +32.2% | -37% | -3% |
| -XRP | +40.0% | -35% | -7% |
| -ADA | +37.2% | -34% | +0% |
| -LINK | +38.0% | -33% | -7% |
| BTC/ETH/XRP/LINK only (no SOL/ADA) | +32.3% | -39% | +0% |

## Candidate deep-dive: Lab B on BTC+ETH only, breakout legs {20,50,100}, BTC MA200 ±2% gate (taker, 0% cash)

Train = 2019-2022, test = 2023-01-01 -> 2026-11-23. Fee % and turnover are per year, relative to average equity (so they read directly as £ per £1,000 held). 'Legs as sleeves' = recommended form: 6 fixed slots (2 coins x 3 lookbacks), each bought once at entry and sold once at exit, never resized.

| Variant | Full CAGR | Full max DD | Worst yr | Train CAGR / DD | Test CAGR / DD | Orders/yr | Fees % equity/yr | Proceeds x equity/yr | Disposals/yr | Round trips: n, mean ± 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|
| Legs as sleeves (RECOMMENDED FORM) | +34.4% | -36% | +0% | +48.8% / -36% | +19.3% / -23% | 38.8 | 4.1% | 2.7 | 19.4 | 153, +15.0% ± 8.3 |
| Legs as sleeves, lookbacks x0.75 | +32.5% | -39% | +0% | +50.3% / -37% | +14.3% / -28% | 48.9 | 4.8% | 3.1 | 24.4 | 193, +10.6% ± 6.0 |
| Legs as sleeves, lookbacks x1.25 | +33.8% | -41% | +0% | +54.8% / -39% | +13.9% / -26% | 33.2 | 3.5% | 2.3 | 16.6 | 131, +18.4% ± 11.0 |
| Legs as sleeves, no gate | +34.8% | -43% | -28% | +50.9% / -42% | +19.9% / -31% | 50.2 | 6.1% | 3.9 | 25.1 | 198, +12.1% ± 6.6 |
| Legs as sleeves, gate MA150 | +34.5% | -37% | -16% | +52.4% / -33% | +16.4% / -23% | 41.8 | 4.3% | 2.8 | 20.9 | 165, +15.0% ± 9.5 |
| Legs as sleeves, gate MA250 | +32.3% | -42% | -5% | +47.6% / -37% | +16.4% / -25% | 41.0 | 4.2% | 2.7 | 20.5 | 162, +13.5% ± 7.9 |
| Legs as sleeves, gate ±0% | +31.6% | -47% | -1% | +43.0% / -45% | +19.4% / -23% | 46.1 | 5.2% | 3.4 | 23.0 | 182, +12.2% ± 7.1 |
| Portfolio form, 25% band | +34.8% | -35% | +0% | +50.7% / -35% | +20.2% / -24% | 33.2 | 4.7% | 3.0 | 17.7 | 41, +2.9% ± 5.2 |
| Portfolio form, 50% band | +38.7% | -36% | +0% | +57.5% / -36% | +21.7% / -22% | 15.8 | 3.0% | 2.0 | 8.5 | 41, +9.2% ± 9.0 |
| Portfolio form, lookbacks x0.5 | +28.8% | -33% | +0% | +50.8% / -33% | +9.6% / -29% | 56.5 | 8.7% | 5.5 | 30.4 | 79, -0.0% ± 2.6 |
| Portfolio form, lookbacks x1.5 | +33.2% | -41% | -1% | +55.5% / -41% | +13.7% / -24% | 24.6 | 3.3% | 2.2 | 13.2 | 36, +8.7% ± 13.2 |
| Portfolio form, wide lookbacks | +28.2% | -40% | -4% | +47.7% / -34% | +10.9% / -24% | 38.4 | 3.6% | 2.4 | 21.0 | 37, +3.6% ± 7.9 |
| Portfolio form, no gate | +37.0% | -40% | -26% | +54.7% / -39% | +21.0% / -32% | 45.5 | 6.4% | 4.1 | 22.9 | 73, +0.2% ± 3.3 |
| BTC only (3 legs) | +35.5% | -37% | -11% | +47.6% / -37% | +21.7% / -19% | 19.3 | 4.4% | 2.9 | 9.6 | 76, +15.3% ± 11.8 |
| ETH only (3 legs) | +33.4% | -48% | -1% | +50.0% / -45% | +16.7% / -30% | 19.5 | 3.8% | 2.5 | 9.8 | 77, +14.7% ± 11.9 |
| B&H BTC | +41.8% | -73% | -60% | +46.4% / -73% | +37.0% / -52% | 0.1 | 0.0% | 0.0 | 0.0 | - |
| B&H BTC+ETH 50/50 | +39.8% | -74% | -63% | +62.3% / -74% | +24.8% / -57% | 0.3 | 0.0% | 0.0 | 0.0 | - |
| BTC MA200 ±2% daily | +30.6% | -60% | -13% | +37.5% / -60% | +23.8% / -31% | 3.8 | 2.5% | 1.6 | 1.9 | 15, +26.5% ± 36.8 |

Recommended form, per year, by fee and cash rate:

| Fee / cash | CAGR | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| 0.80% / 0% | +34.4% | +55% | +81% | +75% | +0% | +27% | +55% | +6% | +2% |
| 0.80% / 4% | +37.9% | +60% | +85% | +78% | +4% | +29% | +58% | +9% | +5% |
| 0.40% / 0% | +37.4% | +58% | +88% | +80% | +0% | +30% | +57% | +9% | +3% |
| 0.40% / 4% | +40.9% | +62% | +92% | +83% | +4% | +33% | +60% | +12% | +6% |

Rolling 12-month windows, monthly starts (n=83), taker, 4% on idle cash for the trend rules:

| | Median return | 10th pct | 90th pct | Median max DD | Worst max DD | Share of windows with DD worse than -25% / -30% |
|---|---|---|---|---|---|---|
| Lab B BTC+ETH (legs) | +19% | -1% | +182% | -21% | -34% | 31% / 17% |
| B&H BTC | +46% | -36% | +240% | -49% | -69% | 89% / 75% |
| BTC MA200 ±2% | +22% | -22% | +181% | -30% | -59% | 64% / 47% |

Lab B beats B&H BTC on return in 40% of windows; on return/max-DD in 58%; beats BTC MA200 on return in 59%. Lab B lost more than 15% in 1% of windows (B&H: 28%).

Rolling 24-month windows, monthly starts (n=71), taker, 4% on idle cash for the trend rules:

| | Median return | 10th pct | 90th pct | Median max DD | Worst max DD | Share of windows with DD worse than -25% / -30% |
|---|---|---|---|---|---|---|
| Lab B BTC+ETH (legs) | +82% | +9% | +267% | -22% | -34% | 41% / 39% |
| B&H BTC | +127% | -31% | +528% | -53% | -73% | 100% / 90% |
| BTC MA200 ±2% | +96% | +6% | +221% | -30% | -59% | 87% / 76% |

Lab B beats B&H BTC on return in 48% of windows; on return/max-DD in 61%; beats BTC MA200 on return in 63%. Lab B lost more than 15% in 0% of windows (B&H: 15%).

Recommended form, fee sweep (full window, 0% cash): 0.25% -> +38.5%, 0.40% -> +37.4%, 0.60% -> +35.9%, 0.80% -> +34.4%, 1.20% -> +31.7%

Longest run of losing round trips: 4 (of 153); win rate 52%.

**Distinct strategy configurations evaluated in this script: 166** (each also run at several fee / cash-rate / window settings).
