# v3

_Generated 2026-11-02 16:17 UTC · commit 048ba31 · author agent-b_

**Hypothesis:** BTC trends persist; holding only above both a slow (SMA200) and medium (EMA50) trend line avoids most of the large drawdowns at a modest cost in return.

**Rules:** timeframe 1d, assets BTC (equal weight), params `{'sma': 200, 'ema': 50}`, rebalance threshold 0.1

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-02; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +29.5% | -54.5% | 0.54 | 0.85 | 63 | 43% |
| 0.05% | +28.5% | -55.0% | 0.52 | 0.83 | 63 | 43% |
| 0.10% | +27.5% | -55.4% | 0.50 | 0.81 | 63 | 43% |
| stress 0.20% + 1 bar late | +27.5% | -58.0% | 0.47 | 0.81 | 63 | 43% |
| Buy & hold (spot) | +35.1% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| Equal-risk mix 60% asset / cash | +27.7% | -56.1% | 0.49 | 0.85 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +32.3% | -55.0% | 0.59 | 0.81 | 30 | 46% |
| 2022..2023 | +33.6% | -12.6% | 2.67 | 1.25 | 9 | 31% |
| 2024..2026-10 | +20.8% | -29.1% | 0.71 | 0.76 | 25 | 46% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: +0%, 2019: +51%, 2020: +108%, 2021: -15%, 2022: +0%, 2023: +78%, 2024: +56%, 2025: -1%, 2026: +10%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +28.5% | -55.0% | 0.52 | 0.83 | 63 | 43% |
| sma = 150 | +30.9% | -54.3% | 0.57 | 0.87 | 72 | 44% |
| sma = 250 | +26.2% | -55.7% | 0.47 | 0.78 | 69 | 44% |
| ema = 38 | +29.0% | -54.0% | 0.54 | 0.86 | 69 | 40% |
| ema = 62 | +27.1% | -53.9% | 0.50 | 0.80 | 69 | 45% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +28.5% | -55.0% | 0.52 | 0.83 | 63 | 43% |
| bars start 04:00 UTC | +30.4% | -59.2% | 0.51 | 0.87 | 69 | 42% |
| bars start 08:00 UTC | +36.7% | -52.7% | 0.70 | 0.99 | 60 | 42% |
| bars start 12:00 UTC | +38.0% | -50.0% | 0.76 | 1.01 | 64 | 43% |
| bars start 16:00 UTC | +34.3% | -46.5% | 0.74 | 0.95 | 66 | 43% |
| bars start 20:00 UTC | +34.2% | -52.0% | 0.66 | 0.94 | 61 | 43% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +28.5% | -55.0% | 0.52 | 0.83 | 63 | 43% |
| ↳ BTC buy & hold | +35.1% | -76.6% | 0.46 | 0.80 | 1 | 100% |
| ETH from 2018-07-01 | +33.9% | -50.8% | 0.67 | 0.83 | 64 | 38% |
| ↳ ETH buy & hold | +21.3% | -83.3% | 0.26 | 0.65 | 1 | 100% |
| SOL from 2020-08-13 | +65.1% | -68.6% | 0.95 | 1.10 | 44 | 34% |
| ↳ SOL buy & hold | +68.0% | -96.3% | 0.71 | 1.02 | 1 | 100% |
| BNB from 2018-07-01 | +60.6% | -57.7% | 1.05 | 1.06 | 84 | 43% |
| ↳ BNB buy & hold | +59.2% | -76.1% | 0.78 | 0.97 | 1 | 100% |
| XRP from 2018-07-01 | -4.0% | -89.6% | -0.05 | 0.24 | 75 | 31% |
| ↳ XRP buy & hold | +12.5% | -83.3% | 0.15 | 0.60 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +28.4% | +42.5% |
| CAGR 5th pct | -6.9% | -13.5% |
| MaxDD median | -58.5% | -80.6% |
| MaxDD worst 5 % | -80.1% | -95.8% |
| P(MAR > buy & hold) | 51% | |
| P(CAGR > buy & hold) | 31% | |

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
