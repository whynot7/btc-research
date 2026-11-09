# ensemble_trend

_Generated 2026-11-09 16:36 UTC · commit fec4b13 · author agent-a_

**Hypothesis:** Averaging trend signals over many lookbacks keeps most of V3's drawdown protection while being far less sensitive to the exact lookback and trading less abruptly.

**Rules:** timeframe 1d, assets BTC (equal weight), params `{'min_lb': 20, 'max_lb': 250}`, rebalance threshold 0.1

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-09; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +30.7% | -56.7% | 0.54 | 0.87 | 80 | 79% |
| 0.05% | +29.6% | -57.3% | 0.52 | 0.85 | 80 | 79% |
| 0.10% | +28.6% | -58.0% | 0.49 | 0.83 | 80 | 79% |
| stress 0.20% + 1 bar late | +25.9% | -58.5% | 0.44 | 0.77 | 80 | 79% |
| Buy & hold (spot) | +34.2% | -76.6% | 0.45 | 0.79 | 1 | 100% |
| Equal-risk mix 60% asset / cash | +27.2% | -56.1% | 0.48 | 0.84 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +51.0% | -45.4% | 1.12 | 1.07 | 34 | 82% |
| 2022..2023 | +16.7% | -23.6% | 0.71 | 0.69 | 23 | 67% |
| 2024..2026-10 | +17.1% | -31.3% | 0.55 | 0.66 | 24 | 84% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: -10%, 2019: +80%, 2020: +162%, 2021: -0%, 2022: -23%, 2023: +77%, 2024: +59%, 2025: -9%, 2026: +5%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +29.6% | -57.3% | 0.52 | 0.85 | 80 | 79% |
| min_lb = 15 | +28.7% | -58.1% | 0.49 | 0.84 | 95 | 80% |
| min_lb = 25 | +29.1% | -55.6% | 0.52 | 0.83 | 71 | 78% |
| max_lb = 188 | +33.2% | -52.5% | 0.63 | 0.92 | 81 | 75% |
| max_lb = 312 | +28.9% | -57.8% | 0.50 | 0.83 | 69 | 81% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +29.6% | -57.3% | 0.52 | 0.85 | 80 | 79% |
| bars start 04:00 UTC | +28.5% | -57.8% | 0.49 | 0.83 | 86 | 79% |
| bars start 08:00 UTC | +29.6% | -53.9% | 0.55 | 0.84 | 78 | 79% |
| bars start 12:00 UTC | +30.4% | -59.0% | 0.52 | 0.86 | 74 | 80% |
| bars start 16:00 UTC | +32.1% | -53.2% | 0.60 | 0.90 | 80 | 80% |
| bars start 20:00 UTC | +31.2% | -53.3% | 0.59 | 0.87 | 79 | 79% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +29.6% | -57.3% | 0.52 | 0.85 | 80 | 79% |
| ↳ BTC buy & hold | +34.2% | -76.6% | 0.45 | 0.79 | 1 | 100% |
| ETH from 2018-07-01 | +29.1% | -57.1% | 0.51 | 0.75 | 64 | 76% |
| ↳ ETH buy & hold | +20.3% | -83.3% | 0.24 | 0.64 | 1 | 100% |
| SOL from 2020-08-13 | +42.4% | -65.9% | 0.64 | 0.87 | 63 | 67% |
| ↳ SOL buy & hold | +65.4% | -96.3% | 0.68 | 1.00 | 1 | 100% |
| BNB from 2018-07-01 | +62.6% | -57.9% | 1.08 | 1.07 | 81 | 80% |
| ↳ BNB buy & hold | +58.3% | -76.1% | 0.77 | 0.96 | 1 | 100% |
| XRP from 2018-07-01 | -3.3% | -88.0% | -0.04 | 0.27 | 117 | 65% |
| ↳ XRP buy & hold | +10.9% | -83.3% | 0.13 | 0.58 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +34.2% | +37.8% |
| CAGR 5th pct | -1.4% | -12.7% |
| MaxDD median | -56.7% | -79.3% |
| MaxDD worst 5 % | -77.7% | -95.6% |
| P(MAR > buy & hold) | 70% | |
| P(CAGR > buy & hold) | 42% | |

_Block bootstrap shuffles 30-day chunks of history. It keeps short-term trends but breaks long ones, so it is a harsh test for slow trend rules; read it as a stress test, not a forecast._

### 3e. Deflated Sharpe ratio

Probability that the true Sharpe is above 0 after correcting for **105 trials** (3 bench variants in LEDGER.csv + 102 declared prior trials; variance of annual Sharpe across trials 0.089; daily returns): **0.60** (≥ 0.95 is the usual bar).

## 4. Checklist

- ✅ Beats equal-risk mix on CAGR (main costs)
- ✅ Positive in every sub-period
- ✅ Parameter MAR range min > 50 % of base
- ✅ Timing MAR range min > 50 % of base
- ❌ Better MAR than buy & hold on most other assets
- ✅ No liquidation in any cost scenario
- ❌ Deflated Sharpe ≥ 0.95

_Research only, not investment advice._
