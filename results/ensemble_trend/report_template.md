# ensemble_trend

_Generated 2026-11-16 16:02 UTC · commit 611c124 · author agent-a_

**Hypothesis:** Averaging trend signals over many lookbacks keeps most of V3's drawdown protection while being far less sensitive to the exact lookback and trading less abruptly.

**Rules:** timeframe 1d, assets BTC (equal weight), params `{'min_lb': 20, 'max_lb': 250}`, rebalance threshold 0.1

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-16; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +30.2% | -56.7% | 0.53 | 0.86 | 80 | 79% |
| 0.05% | +29.2% | -57.3% | 0.51 | 0.84 | 80 | 79% |
| 0.10% | +28.1% | -58.0% | 0.49 | 0.82 | 80 | 79% |
| stress 0.20% + 1 bar late | +25.2% | -58.5% | 0.43 | 0.76 | 80 | 79% |
| Buy & hold (spot) | +32.0% | -76.6% | 0.42 | 0.76 | 1 | 100% |
| Equal-risk mix 60% asset / cash | +25.9% | -56.1% | 0.46 | 0.81 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +51.0% | -45.4% | 1.12 | 1.07 | 34 | 82% |
| 2022..2023 | +16.7% | -23.6% | 0.71 | 0.69 | 23 | 67% |
| 2024..2026-10 | +17.1% | -31.3% | 0.55 | 0.66 | 24 | 84% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: -10%, 2019: +80%, 2020: +162%, 2021: -0%, 2022: -23%, 2023: +77%, 2024: +59%, 2025: -9%, 2026: +2%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +29.2% | -57.3% | 0.51 | 0.84 | 80 | 79% |
| min_lb = 15 | +28.3% | -58.1% | 0.49 | 0.83 | 95 | 80% |
| min_lb = 25 | +28.6% | -55.6% | 0.51 | 0.83 | 71 | 78% |
| max_lb = 188 | +32.9% | -52.5% | 0.63 | 0.91 | 81 | 75% |
| max_lb = 312 | +28.4% | -57.8% | 0.49 | 0.82 | 69 | 81% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +29.2% | -57.3% | 0.51 | 0.84 | 80 | 79% |
| bars start 04:00 UTC | +27.8% | -57.8% | 0.48 | 0.81 | 86 | 79% |
| bars start 08:00 UTC | +28.9% | -53.9% | 0.54 | 0.83 | 78 | 79% |
| bars start 12:00 UTC | +29.9% | -59.0% | 0.51 | 0.85 | 74 | 80% |
| bars start 16:00 UTC | +31.6% | -53.2% | 0.59 | 0.89 | 80 | 80% |
| bars start 20:00 UTC | +30.7% | -53.3% | 0.58 | 0.86 | 79 | 79% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +29.2% | -57.3% | 0.51 | 0.84 | 80 | 79% |
| ↳ BTC buy & hold | +32.0% | -76.6% | 0.42 | 0.76 | 1 | 100% |
| ETH from 2018-07-01 | +29.0% | -57.1% | 0.51 | 0.75 | 64 | 76% |
| ↳ ETH buy & hold | +18.1% | -83.3% | 0.22 | 0.62 | 1 | 100% |
| SOL from 2020-08-13 | +42.2% | -65.9% | 0.64 | 0.87 | 63 | 67% |
| ↳ SOL buy & hold | +60.6% | -96.3% | 0.63 | 0.98 | 1 | 100% |
| BNB from 2018-07-01 | +61.9% | -57.9% | 1.07 | 1.07 | 81 | 80% |
| ↳ BNB buy & hold | +55.6% | -76.1% | 0.73 | 0.94 | 1 | 100% |
| XRP from 2018-07-01 | -3.3% | -88.0% | -0.04 | 0.26 | 117 | 64% |
| ↳ XRP buy & hold | +9.1% | -83.3% | 0.11 | 0.57 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +35.2% | +38.0% |
| CAGR 5th pct | -2.0% | -12.5% |
| MaxDD median | -56.9% | -80.2% |
| MaxDD worst 5 % | -76.1% | -96.1% |
| P(MAR > buy & hold) | 70% | |
| P(CAGR > buy & hold) | 44% | |

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
