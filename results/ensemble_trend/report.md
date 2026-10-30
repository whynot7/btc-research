# ensemble_trend

_Generated 2026-10-30 22:40 UTC · commit 3691fc7 · author agent-a_

**Hypothesis:** Averaging trend signals over many lookbacks keeps most of V3's drawdown protection while being far less sensitive to the exact lookback and trading less abruptly.

**Rules:** timeframe 1d, assets BTC (equal weight), params `{'min_lb': 20, 'max_lb': 250}`, rebalance threshold 0.1

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-09-30; hyperliquid 2023-05-12..2026-10-30; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +31.3% | -56.7% | 0.55 | 0.88 | 80 | 79% |
| 0.05% | +30.2% | -57.3% | 0.53 | 0.86 | 80 | 79% |
| 0.10% | +29.2% | -58.0% | 0.50 | 0.84 | 80 | 79% |
| stress 0.20% + 1 bar late | +26.4% | -58.5% | 0.45 | 0.78 | 80 | 79% |
| Buy & hold (spot) | +35.0% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| Equal-risk mix 60% asset / cash | +27.6% | -56.1% | 0.49 | 0.84 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +51.0% | -45.4% | 1.12 | 1.07 | 34 | 82% |
| 2022..2023 | +16.7% | -23.6% | 0.71 | 0.69 | 23 | 67% |
| 2024..2026-10 | +17.2% | -31.3% | 0.55 | 0.66 | 24 | 84% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: -10%, 2019: +80%, 2020: +162%, 2021: -0%, 2022: -23%, 2023: +77%, 2024: +59%, 2025: -9%, 2026: +8%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +30.2% | -57.3% | 0.53 | 0.86 | 80 | 79% |
| min_lb = 15 | +29.3% | -58.1% | 0.50 | 0.85 | 95 | 80% |
| min_lb = 25 | +29.5% | -55.6% | 0.53 | 0.84 | 71 | 78% |
| max_lb = 188 | +33.8% | -52.5% | 0.64 | 0.93 | 81 | 75% |
| max_lb = 312 | +29.6% | -57.8% | 0.51 | 0.85 | 69 | 81% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +30.2% | -57.3% | 0.53 | 0.86 | 80 | 79% |
| bars start 04:00 UTC | +29.3% | -57.8% | 0.51 | 0.84 | 86 | 79% |
| bars start 08:00 UTC | +30.3% | -53.9% | 0.56 | 0.86 | 78 | 79% |
| bars start 12:00 UTC | +31.0% | -59.0% | 0.53 | 0.87 | 74 | 80% |
| bars start 16:00 UTC | +32.5% | -53.2% | 0.61 | 0.90 | 80 | 80% |
| bars start 20:00 UTC | +31.4% | -53.3% | 0.59 | 0.87 | 79 | 79% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +30.2% | -57.3% | 0.53 | 0.86 | 80 | 79% |
| ↳ BTC buy & hold | +35.0% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| ETH from 2018-07-01 | +30.0% | -57.1% | 0.53 | 0.76 | 64 | 76% |
| ↳ ETH buy & hold | +21.2% | -83.3% | 0.25 | 0.65 | 1 | 100% |
| SOL from 2020-08-13 | +43.6% | -65.9% | 0.66 | 0.88 | 63 | 67% |
| ↳ SOL buy & hold | +68.5% | -96.3% | 0.71 | 1.02 | 1 | 100% |
| BNB from 2018-07-01 | +63.1% | -57.9% | 1.09 | 1.08 | 81 | 80% |
| ↳ BNB buy & hold | +58.9% | -76.1% | 0.77 | 0.97 | 1 | 100% |
| XRP from 2018-07-01 | -2.9% | -88.0% | -0.03 | 0.27 | 116 | 65% |
| ↳ XRP buy & hold | +12.4% | -83.3% | 0.15 | 0.60 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +36.0% | +42.0% |
| CAGR 5th pct | -1.4% | -14.2% |
| MaxDD median | -55.9% | -79.3% |
| MaxDD worst 5 % | -77.2% | -96.0% |
| P(MAR > buy & hold) | 64% | |
| P(CAGR > buy & hold) | 38% | |

_Block bootstrap shuffles 30-day chunks of history. It keeps short-term trends but breaks long ones, so it is a harsh test for slow trend rules; read it as a stress test, not a forecast._

### 3e. Deflated Sharpe ratio

Probability that the true Sharpe is above 0 after correcting for **105 trials** (3 bench variants in LEDGER.csv + 102 declared prior trials; variance of annual Sharpe across trials 0.089; daily returns): **0.62** (≥ 0.95 is the usual bar).

## 4. Checklist

- ✅ Beats equal-risk mix on CAGR (main costs)
- ✅ Positive in every sub-period
- ✅ Parameter MAR range min > 50 % of base
- ✅ Timing MAR range min > 50 % of base
- ❌ Better MAR than buy & hold on most other assets
- ✅ No liquidation in any cost scenario
- ❌ Deflated Sharpe ≥ 0.95

_Research only, not investment advice._
