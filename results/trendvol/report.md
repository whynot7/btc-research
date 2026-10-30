# trendvol

_Generated 2026-10-30 22:36 UTC · commit 1a278d7 · author agent-a_

**Hypothesis:** Crypto trends persist on 4h bars in both directions; volatility targeting keeps risk roughly constant, so exposure is high in calm trends and low in turbulent markets.

**Rules:** timeframe 4h, assets BTC, ETH (equal weight), params `{'ema': 200, 'band': 0.01, 'vol_window': 180, 'vol_target': 0.6, 'max_lev': 3.0}`, rebalance threshold 0.25

**Data:** BTC: binance-1h; funding hyperliquid from 2023-05-12, 10% p.a. before; ETH: binance-1h; funding hyperliquid from 2023-05-12, 10% p.a. before

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +107.0% | -43.5% | 2.46 | 1.58 | 442 | 100% |
| 0.05% | +100.0% | -44.4% | 2.25 | 1.52 | 442 | 100% |
| 0.10% | +93.3% | -45.3% | 2.06 | 1.46 | 442 | 100% |
| stress 0.20% + 1 bar late | +68.1% | -48.7% | 1.40 | 1.20 | 442 | 100% |
| Buy & hold (spot) | +30.9% | -77.4% | 0.40 | 0.74 | 1 | 100% |
| Equal-risk mix 45% asset / cash | +21.9% | -45.7% | 0.48 | 0.81 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +167.8% | -34.4% | 4.88 | 2.01 | 200 | 100% |
| 2022..2023 | +69.8% | -44.4% | 1.57 | 1.21 | 92 | 100% |
| 2024..2026-10 | +55.0% | -42.6% | 1.29 | 1.09 | 154 | 100% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: +36%, 2019: +157%, 2020: +366%, 2021: +95%, 2022: +71%, 2023: +71%, 2024: +22%, 2025: +41%, 2026: +101%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +100.0% | -44.4% | 2.25 | 1.52 | 442 | 100% |
| ema = 150 | +85.0% | -49.3% | 1.72 | 1.38 | 584 | 100% |
| ema = 250 | +90.3% | -50.1% | 1.80 | 1.43 | 388 | 100% |
| band = 0.0075 | +102.2% | -42.3% | 2.42 | 1.54 | 516 | 100% |
| band = 0.0125 | +101.2% | -47.8% | 2.12 | 1.53 | 394 | 100% |
| vol_window = 135 | +100.5% | -49.3% | 2.04 | 1.50 | 442 | 100% |
| vol_window = 225 | +97.7% | -43.3% | 2.26 | 1.51 | 442 | 100% |
| vol_target = 0.45 | +75.6% | -34.7% | 2.18 | 1.55 | 442 | 100% |
| vol_target = 0.75 | +121.2% | -51.9% | 2.33 | 1.49 | 442 | 100% |
| max_lev = 2.25 | +98.1% | -44.4% | 2.21 | 1.50 | 442 | 100% |
| max_lev = 3.75 | +100.1% | -44.4% | 2.26 | 1.52 | 442 | 100% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +100.0% | -44.4% | 2.25 | 1.52 | 442 | 100% |
| bars start 01:00 UTC | +91.2% | -42.9% | 2.13 | 1.44 | 438 | 100% |
| bars start 02:00 UTC | +98.7% | -38.8% | 2.54 | 1.50 | 452 | 100% |
| bars start 03:00 UTC | +109.0% | -43.2% | 2.52 | 1.59 | 440 | 100% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +85.8% | -54.7% | 1.57 | 1.29 | 213 | 100% |
| ↳ BTC buy & hold | +34.8% | -77.1% | 0.45 | 0.80 | 1 | 100% |
| ETH (in-sample asset) from 2018-07-01 | +98.0% | -54.2% | 1.81 | 1.41 | 229 | 100% |
| ↳ ETH buy & hold | +21.1% | -83.8% | 0.25 | 0.64 | 1 | 100% |
| SOL from 2020-08-11 | +62.0% | -70.9% | 0.87 | 1.08 | 241 | 99% |
| ↳ SOL buy & hold | +72.7% | -96.6% | 0.75 | 1.05 | 1 | 100% |
| BNB from 2018-07-01 | +52.4% | -67.3% | 0.78 | 0.98 | 277 | 100% |
| ↳ BNB buy & hold | +59.0% | -78.0% | 0.76 | 0.98 | 1 | 100% |
| XRP from 2018-07-01 | +7.7% | -84.4% | 0.09 | 0.44 | 327 | 100% |
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

Probability that the true Sharpe is above 0 after correcting for **105 trials** (bench variants in LEDGER.csv + declared prior trials): **0.76** (≥ 0.95 is the usual bar).

## 4. Checklist

- ✅ Beats equal-risk mix on CAGR (main costs)
- ✅ Positive in every sub-period
- ✅ Parameter MAR range min > 50 % of base
- ✅ Timing MAR range min > 50 % of base
- ✅ Better MAR than buy & hold on most other assets
- ✅ No liquidation in any cost scenario
- ❌ Deflated Sharpe ≥ 0.95

_Research only, not investment advice._
