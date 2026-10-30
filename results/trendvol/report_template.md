# trendvol

_Generated 2026-10-30 22:43 UTC · commit 3691fc7 · author agent-a_

**Hypothesis:** Crypto trends persist on 4h bars in both directions; volatility targeting keeps risk roughly constant, so exposure is high in calm trends and low in turbulent markets.

**Rules:** timeframe 4h, assets BTC, ETH (equal weight), params `{'ema': 200, 'band': 0.01, 'vol_window': 180, 'vol_target': 0.6, 'max_lev': 3.0}`, rebalance threshold 0.25

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-09-30; hyperliquid 2023-05-12..2026-10-30; before: fallback 10% p.a. longs pay, shorts get 0; ETH: binance-1h; funding binance 2020-01-01..2026-09-30; hyperliquid 2023-05-12..2026-10-30; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +102.1% | -43.0% | 2.37 | 1.53 | 442 | 100% |
| 0.05% | +95.8% | -43.9% | 2.18 | 1.48 | 442 | 100% |
| 0.10% | +89.8% | -44.8% | 2.01 | 1.43 | 442 | 100% |
| stress 0.20% + 1 bar late | +65.3% | -47.6% | 1.37 | 1.17 | 442 | 100% |
| Buy & hold (spot) | +30.9% | -77.4% | 0.40 | 0.74 | 1 | 100% |
| Equal-risk mix 45% asset / cash | +21.9% | -45.7% | 0.48 | 0.81 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +141.0% | -34.8% | 4.05 | 1.82 | 200 | 100% |
| 2022..2023 | +74.5% | -43.9% | 1.70 | 1.26 | 92 | 100% |
| 2024..2026-10 | +62.7% | -41.3% | 1.52 | 1.18 | 154 | 100% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: +32%, 2019: +148%, 2020: +314%, 2021: +63%, 2022: +64%, 2023: +88%, 2024: +35%, 2025: +45%, 2026: +103%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +95.8% | -43.9% | 2.18 | 1.48 | 442 | 100% |
| ema = 150 | +80.6% | -48.8% | 1.65 | 1.34 | 584 | 100% |
| ema = 250 | +86.6% | -49.0% | 1.77 | 1.39 | 388 | 100% |
| band = 0.0075 | +97.0% | -42.0% | 2.31 | 1.49 | 516 | 100% |
| band = 0.0125 | +97.1% | -45.1% | 2.15 | 1.49 | 394 | 100% |
| vol_window = 135 | +94.8% | -48.3% | 1.96 | 1.45 | 442 | 100% |
| vol_window = 225 | +93.5% | -41.5% | 2.25 | 1.47 | 442 | 100% |
| vol_target = 0.45 | +70.8% | -34.3% | 2.07 | 1.49 | 442 | 100% |
| vol_target = 0.75 | +116.4% | -51.3% | 2.27 | 1.46 | 442 | 100% |
| max_lev = 2.25 | +94.0% | -43.9% | 2.14 | 1.47 | 442 | 100% |
| max_lev = 3.75 | +95.8% | -43.9% | 2.18 | 1.48 | 442 | 100% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +95.8% | -43.9% | 2.18 | 1.48 | 442 | 100% |
| bars start 01:00 UTC | +86.5% | -42.7% | 2.03 | 1.40 | 438 | 100% |
| bars start 02:00 UTC | +92.5% | -36.9% | 2.51 | 1.44 | 452 | 100% |
| bars start 03:00 UTC | +103.4% | -42.0% | 2.46 | 1.54 | 440 | 100% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +83.7% | -55.7% | 1.50 | 1.27 | 213 | 100% |
| ↳ BTC buy & hold | +34.8% | -77.1% | 0.45 | 0.80 | 1 | 100% |
| ETH (in-sample asset) from 2018-07-01 | +91.9% | -54.6% | 1.68 | 1.35 | 229 | 100% |
| ↳ ETH buy & hold | +21.1% | -83.8% | 0.25 | 0.64 | 1 | 100% |
| SOL from 2020-08-11 | +59.9% | -74.3% | 0.81 | 1.05 | 241 | 99% |
| ↳ SOL buy & hold | +72.7% | -96.6% | 0.75 | 1.05 | 1 | 100% |
| BNB from 2018-07-01 | +52.3% | -64.2% | 0.81 | 0.98 | 277 | 100% |
| ↳ BNB buy & hold | +59.0% | -78.0% | 0.76 | 0.98 | 1 | 100% |
| XRP from 2018-07-01 | +3.7% | -84.1% | 0.04 | 0.39 | 327 | 100% |
| ↳ XRP buy & hold | +12.5% | -84.5% | 0.15 | 0.59 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +46.3% | +51.9% |
| CAGR 5th pct | +12.0% | +10.9% |
| MaxDD median | -59.5% | -67.3% |
| MaxDD worst 5 % | -77.3% | -86.1% |
| P(MAR > buy & hold) | 51% | |
| P(CAGR > buy & hold) | 43% | |

_Block bootstrap shuffles 30-day chunks of history. It keeps short-term trends but breaks long ones, so it is a harsh test for slow trend rules; read it as a stress test, not a forecast._

### 3e. Deflated Sharpe ratio

{{DSR_TEXT}}

## 4. Checklist

- ✅ Beats equal-risk mix on CAGR (main costs)
- ✅ Positive in every sub-period
- ✅ Parameter MAR range min > 50 % of base
- ✅ Timing MAR range min > 50 % of base
- ✅ Better MAR than buy & hold on most other assets
- ✅ No liquidation in any cost scenario
{{DSR_CHECK}}

_Research only, not investment advice._
