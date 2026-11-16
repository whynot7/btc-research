# trendvol

_Generated 2026-11-16 16:02 UTC · commit 611c124 · author agent-a_

**Hypothesis:** Crypto trends persist on 4h bars in both directions; volatility targeting keeps risk roughly constant, so exposure is high in calm trends and low in turbulent markets.

**Rules:** timeframe 4h, assets BTC, ETH (equal weight), params `{'ema': 200, 'band': 0.01, 'vol_window': 180, 'vol_target': 0.6, 'max_lev': 3.0}`, rebalance threshold 0.25

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-16; before: fallback 10% p.a. longs pay, shorts get 0; ETH: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-16; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +104.9% | -43.0% | 2.44 | 1.56 | 444 | 100% |
| 0.05% | +98.6% | -43.9% | 2.24 | 1.50 | 444 | 100% |
| 0.10% | +92.4% | -44.8% | 2.07 | 1.45 | 444 | 100% |
| stress 0.20% + 1 bar late | +67.7% | -47.6% | 1.42 | 1.20 | 444 | 100% |
| Buy & hold (spot) | +27.8% | -77.4% | 0.36 | 0.70 | 1 | 100% |
| Equal-risk mix 45% asset / cash | +20.6% | -45.7% | 0.45 | 0.77 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +141.0% | -34.8% | 4.05 | 1.82 | 200 | 100% |
| 2022..2023 | +74.5% | -43.9% | 1.70 | 1.26 | 92 | 100% |
| 2024..2026-10 | +62.7% | -41.3% | 1.52 | 1.18 | 154 | 100% |
| FORWARD (from 2026-11) | +2371.7% | -9.8% | 242.67 | 5.41 | 4 | 100% |

Calendar years: 2018: +32%, 2019: +148%, 2020: +314%, 2021: +63%, 2022: +64%, 2023: +88%, 2024: +35%, 2025: +45%, 2026: +135%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +98.6% | -43.9% | 2.24 | 1.50 | 444 | 100% |
| ema = 150 | +83.2% | -48.8% | 1.71 | 1.36 | 586 | 100% |
| ema = 250 | +91.0% | -49.0% | 1.86 | 1.43 | 388 | 100% |
| band = 0.0075 | +99.7% | -42.0% | 2.38 | 1.52 | 518 | 100% |
| band = 0.0125 | +101.9% | -45.1% | 2.26 | 1.53 | 394 | 100% |
| vol_window = 135 | +97.3% | -48.3% | 2.01 | 1.47 | 444 | 100% |
| vol_window = 225 | +96.1% | -41.5% | 2.31 | 1.50 | 444 | 100% |
| vol_target = 0.45 | +72.6% | -34.3% | 2.12 | 1.51 | 444 | 100% |
| vol_target = 0.75 | +119.8% | -51.3% | 2.34 | 1.48 | 444 | 100% |
| max_lev = 2.25 | +96.7% | -43.9% | 2.20 | 1.49 | 444 | 100% |
| max_lev = 3.75 | +98.6% | -43.9% | 2.24 | 1.50 | 444 | 100% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +98.6% | -43.9% | 2.24 | 1.50 | 444 | 100% |
| bars start 01:00 UTC | +89.5% | -42.7% | 2.10 | 1.42 | 440 | 100% |
| bars start 02:00 UTC | +95.0% | -36.9% | 2.58 | 1.46 | 454 | 100% |
| bars start 03:00 UTC | +107.1% | -42.0% | 2.55 | 1.57 | 442 | 100% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +89.0% | -55.7% | 1.60 | 1.31 | 213 | 100% |
| ↳ BTC buy & hold | +31.8% | -77.1% | 0.41 | 0.76 | 1 | 100% |
| ETH (in-sample asset) from 2018-07-01 | +91.6% | -54.6% | 1.68 | 1.35 | 231 | 100% |
| ↳ ETH buy & hold | +18.0% | -83.8% | 0.21 | 0.61 | 1 | 100% |
| SOL from 2020-08-11 | +66.2% | -74.3% | 0.89 | 1.12 | 241 | 99% |
| ↳ SOL buy & hold | +64.1% | -96.6% | 0.66 | 1.00 | 1 | 100% |
| BNB from 2018-07-01 | +55.9% | -64.2% | 0.87 | 1.01 | 277 | 100% |
| ↳ BNB buy & hold | +55.2% | -78.0% | 0.71 | 0.95 | 1 | 100% |
| XRP from 2018-07-01 | +7.0% | -84.1% | 0.08 | 0.43 | 327 | 100% |
| ↳ XRP buy & hold | +8.8% | -84.5% | 0.10 | 0.56 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +45.2% | +45.9% |
| CAGR 5th pct | +9.2% | +8.6% |
| MaxDD median | -59.0% | -68.7% |
| MaxDD worst 5 % | -80.3% | -87.5% |
| P(MAR > buy & hold) | 57% | |
| P(CAGR > buy & hold) | 48% | |

_Block bootstrap shuffles 30-day chunks of history. It keeps short-term trends but breaks long ones, so it is a harsh test for slow trend rules; read it as a stress test, not a forecast._

### 3e. Deflated Sharpe ratio

Probability that the true Sharpe is above 0 after correcting for **105 trials** (3 bench variants in LEDGER.csv + 102 declared prior trials; variance of annual Sharpe across trials 0.089; daily returns): **0.98** (≥ 0.95 is the usual bar).

## 4. Checklist

- ✅ Beats equal-risk mix on CAGR (main costs)
- ✅ Positive in every sub-period
- ✅ Parameter MAR range min > 50 % of base
- ✅ Timing MAR range min > 50 % of base
- ✅ Better MAR than buy & hold on most other assets
- ✅ No liquidation in any cost scenario
- ✅ Deflated Sharpe ≥ 0.95

_Research only, not investment advice._
