# ensemble_trend

_Generated 2026-10-30 22:29 UTC · commit 1a278d7 · author agent-a_

**Hypothesis:** Averaging trend signals over many lookbacks keeps most of V3's drawdown protection while being far less sensitive to the exact lookback and trading less abruptly.

**Rules:** timeframe 1d, assets BTC (equal weight), params `{'min_lb': 20, 'max_lb': 250}`, rebalance threshold 0.1

**Data:** BTC: binance-1h; funding hyperliquid from 2023-05-12, 10% p.a. before

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +33.0% | -52.8% | 0.62 | 0.92 | 80 | 79% |
| 0.05% | +32.0% | -53.6% | 0.60 | 0.90 | 80 | 79% |
| 0.10% | +30.9% | -54.3% | 0.57 | 0.88 | 80 | 79% |
| stress 0.20% + 1 bar late | +28.2% | -55.1% | 0.51 | 0.82 | 80 | 79% |
| Buy & hold (spot) | +35.0% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| Equal-risk mix 55% asset / cash | +24.7% | -53.1% | 0.47 | 0.82 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +65.4% | -42.4% | 1.54 | 1.26 | 34 | 82% |
| 2022..2023 | +13.7% | -23.8% | 0.57 | 0.60 | 23 | 67% |
| 2024..2026-10 | +10.8% | -34.5% | 0.31 | 0.48 | 24 | 84% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: -10%, 2019: +80%, 2020: +188%, 2021: +25%, 2022: -23%, 2023: +68%, 2024: +43%, 2025: -13%, 2026: +7%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +32.0% | -53.6% | 0.60 | 0.90 | 80 | 79% |
| min_lb = 15 | +31.0% | -54.0% | 0.57 | 0.88 | 95 | 80% |
| min_lb = 25 | +31.4% | -51.7% | 0.61 | 0.88 | 71 | 78% |
| max_lb = 188 | +35.6% | -48.0% | 0.74 | 0.97 | 81 | 75% |
| max_lb = 312 | +31.3% | -54.1% | 0.58 | 0.88 | 69 | 81% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +32.0% | -53.6% | 0.60 | 0.90 | 80 | 79% |
| bars start 04:00 UTC | +31.0% | -54.3% | 0.57 | 0.88 | 86 | 79% |
| bars start 08:00 UTC | +32.2% | -50.7% | 0.64 | 0.89 | 78 | 79% |
| bars start 12:00 UTC | +32.8% | -55.2% | 0.59 | 0.91 | 74 | 80% |
| bars start 16:00 UTC | +34.2% | -49.3% | 0.69 | 0.94 | 80 | 80% |
| bars start 20:00 UTC | +33.2% | -48.4% | 0.69 | 0.91 | 79 | 79% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +32.0% | -53.6% | 0.60 | 0.90 | 80 | 79% |
| ↳ BTC buy & hold | +35.0% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| ETH from 2018-07-01 | +34.0% | -54.5% | 0.62 | 0.82 | 64 | 76% |
| ↳ ETH buy & hold | +21.2% | -83.3% | 0.25 | 0.65 | 1 | 100% |
| SOL from 2020-08-13 | +39.2% | -66.2% | 0.59 | 0.83 | 63 | 67% |
| ↳ SOL buy & hold | +68.5% | -96.3% | 0.71 | 1.02 | 1 | 100% |
| BNB from 2018-07-01 | +59.9% | -64.9% | 0.92 | 1.05 | 81 | 80% |
| ↳ BNB buy & hold | +58.9% | -76.1% | 0.77 | 0.97 | 1 | 100% |
| XRP from 2018-07-01 | +1.4% | -86.7% | 0.02 | 0.34 | 116 | 65% |
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

Probability that the true Sharpe is above 0 after correcting for **105 trials** (bench variants in LEDGER.csv + declared prior trials): **0.13** (≥ 0.95 is the usual bar).

## 4. Checklist

- ✅ Beats equal-risk mix on CAGR (main costs)
- ✅ Positive in every sub-period
- ✅ Parameter MAR range min > 50 % of base
- ✅ Timing MAR range min > 50 % of base
- ❌ Better MAR than buy & hold on most other assets
- ✅ No liquidation in any cost scenario
- ❌ Deflated Sharpe ≥ 0.95

_Research only, not investment advice._
