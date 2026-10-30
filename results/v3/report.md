# v3

_Generated 2026-10-30 22:38 UTC · commit 1a278d7 · author agent-b_

**Hypothesis:** BTC trends persist; holding only above both a slow (SMA200) and medium (EMA50) trend line avoids most of the large drawdowns at a modest cost in return.

**Rules:** timeframe 1d, assets BTC (equal weight), params `{'sma': 200, 'ema': 50}`, rebalance threshold 0.1

**Data:** BTC: binance-1h; funding hyperliquid from 2023-05-12, 10% p.a. before

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +31.5% | -52.0% | 0.61 | 0.89 | 63 | 43% |
| 0.05% | +30.5% | -52.5% | 0.58 | 0.87 | 63 | 43% |
| 0.10% | +29.5% | -52.9% | 0.56 | 0.86 | 63 | 43% |
| stress 0.20% + 1 bar late | +29.5% | -55.6% | 0.53 | 0.85 | 63 | 43% |
| Buy & hold (spot) | +35.0% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| Equal-risk mix 55% asset / cash | +24.7% | -53.1% | 0.47 | 0.82 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +45.8% | -52.5% | 0.87 | 1.01 | 30 | 46% |
| 2022..2023 | +29.7% | -12.8% | 2.32 | 1.14 | 9 | 31% |
| 2024..2026-10 | +14.4% | -32.2% | 0.45 | 0.58 | 25 | 46% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: +0%, 2019: +51%, 2020: +129%, 2021: +8%, 2022: +0%, 2023: +68%, 2024: +40%, 2025: -4%, 2026: +9%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +30.5% | -52.5% | 0.58 | 0.87 | 63 | 43% |
| sma = 150 | +33.0% | -50.4% | 0.66 | 0.91 | 72 | 44% |
| sma = 250 | +28.0% | -52.1% | 0.54 | 0.82 | 69 | 44% |
| ema = 38 | +30.7% | -50.1% | 0.61 | 0.89 | 69 | 40% |
| ema = 62 | +29.1% | -50.9% | 0.57 | 0.84 | 69 | 45% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +30.5% | -52.5% | 0.58 | 0.87 | 63 | 43% |
| bars start 04:00 UTC | +32.0% | -55.9% | 0.57 | 0.91 | 69 | 43% |
| bars start 08:00 UTC | +38.1% | -48.9% | 0.78 | 1.02 | 60 | 42% |
| bars start 12:00 UTC | +40.0% | -48.3% | 0.83 | 1.05 | 64 | 43% |
| bars start 16:00 UTC | +36.4% | -44.0% | 0.83 | 0.99 | 66 | 43% |
| bars start 20:00 UTC | +36.2% | -49.4% | 0.73 | 0.98 | 61 | 43% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +30.5% | -52.5% | 0.58 | 0.87 | 63 | 43% |
| ↳ BTC buy & hold | +35.0% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| ETH from 2018-07-01 | +38.7% | -53.8% | 0.72 | 0.90 | 64 | 38% |
| ↳ ETH buy & hold | +21.2% | -83.3% | 0.25 | 0.65 | 1 | 100% |
| SOL from 2020-08-13 | +62.5% | -67.8% | 0.92 | 1.08 | 44 | 34% |
| ↳ SOL buy & hold | +68.5% | -96.3% | 0.71 | 1.02 | 1 | 100% |
| BNB from 2018-07-01 | +58.6% | -57.1% | 1.03 | 1.04 | 84 | 44% |
| ↳ BNB buy & hold | +58.9% | -76.1% | 0.77 | 0.97 | 1 | 100% |
| XRP from 2018-07-01 | -0.2% | -88.4% | -0.00 | 0.30 | 75 | 31% |
| ↳ XRP buy & hold | +12.4% | -83.3% | 0.15 | 0.60 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +30.1% | +42.0% |
| CAGR 5th pct | -6.4% | -14.2% |
| MaxDD median | -60.1% | -79.3% |
| MaxDD worst 5 % | -81.6% | -96.0% |
| P(MAR > buy & hold) | 47% | |
| P(CAGR > buy & hold) | 30% | |

_Block bootstrap shuffles 30-day chunks of history. It keeps short-term trends but breaks long ones, so it is a harsh test for slow trend rules; read it as a stress test, not a forecast._

### 3e. Deflated Sharpe ratio

Probability that the true Sharpe is above 0 after correcting for **105 trials** (bench variants in LEDGER.csv + declared prior trials): **0.63** (≥ 0.95 is the usual bar).

## 4. Checklist

- ✅ Beats equal-risk mix on CAGR (main costs)
- ✅ Positive in every sub-period
- ✅ Parameter MAR range min > 50 % of base
- ✅ Timing MAR range min > 50 % of base
- ✅ Better MAR than buy & hold on most other assets
- ✅ No liquidation in any cost scenario
- ❌ Deflated Sharpe ≥ 0.95

_Research only, not investment advice._
