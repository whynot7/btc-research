# v3

_Generated 2026-11-09 16:38 UTC · commit fec4b13 · author agent-b_

**Hypothesis:** BTC trends persist; holding only above both a slow (SMA200) and medium (EMA50) trend line avoids most of the large drawdowns at a modest cost in return.

**Rules:** timeframe 1d, assets BTC (equal weight), params `{'sma': 200, 'ema': 50}`, rebalance threshold 0.1

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-09; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +28.5% | -54.5% | 0.52 | 0.83 | 64 | 43% |
| 0.05% | +27.6% | -55.0% | 0.50 | 0.81 | 64 | 43% |
| 0.10% | +26.6% | -55.4% | 0.48 | 0.80 | 64 | 43% |
| stress 0.20% + 1 bar late | +27.3% | -58.0% | 0.47 | 0.81 | 64 | 43% |
| Buy & hold (spot) | +34.2% | -76.6% | 0.45 | 0.79 | 1 | 100% |
| Equal-risk mix 60% asset / cash | +27.2% | -56.1% | 0.48 | 0.84 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +32.3% | -55.0% | 0.59 | 0.81 | 30 | 46% |
| 2022..2023 | +33.6% | -12.6% | 2.67 | 1.25 | 9 | 31% |
| 2024..2026-10 | +20.8% | -29.1% | 0.71 | 0.76 | 25 | 46% |
| FORWARD (from 2026-11) | – | – | – | – | – | – |

Calendar years: 2018: +0%, 2019: +51%, 2020: +108%, 2021: -15%, 2022: +0%, 2023: +78%, 2024: +56%, 2025: -1%, 2026: +4%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +27.6% | -55.0% | 0.50 | 0.81 | 64 | 43% |
| sma = 150 | +29.9% | -54.3% | 0.55 | 0.85 | 73 | 44% |
| sma = 250 | +25.2% | -55.7% | 0.45 | 0.77 | 70 | 43% |
| ema = 38 | +28.0% | -54.0% | 0.52 | 0.84 | 70 | 40% |
| ema = 62 | +26.2% | -53.9% | 0.49 | 0.78 | 70 | 45% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +27.6% | -55.0% | 0.50 | 0.81 | 64 | 43% |
| bars start 04:00 UTC | +29.4% | -59.2% | 0.50 | 0.85 | 70 | 42% |
| bars start 08:00 UTC | +35.5% | -52.7% | 0.67 | 0.96 | 61 | 42% |
| bars start 12:00 UTC | +37.0% | -50.0% | 0.74 | 1.00 | 65 | 43% |
| bars start 16:00 UTC | +33.3% | -46.5% | 0.72 | 0.93 | 67 | 42% |
| bars start 20:00 UTC | +34.1% | -52.0% | 0.66 | 0.94 | 61 | 43% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +27.6% | -55.0% | 0.50 | 0.81 | 64 | 43% |
| ↳ BTC buy & hold | +34.2% | -76.6% | 0.45 | 0.79 | 1 | 100% |
| ETH from 2018-07-01 | +32.5% | -50.8% | 0.64 | 0.81 | 65 | 38% |
| ↳ ETH buy & hold | +20.3% | -83.3% | 0.24 | 0.64 | 1 | 100% |
| SOL from 2020-08-13 | +64.8% | -68.6% | 0.95 | 1.09 | 44 | 33% |
| ↳ SOL buy & hold | +65.4% | -96.3% | 0.68 | 1.00 | 1 | 100% |
| BNB from 2018-07-01 | +60.5% | -57.7% | 1.05 | 1.06 | 84 | 43% |
| ↳ BNB buy & hold | +58.3% | -76.1% | 0.77 | 0.96 | 1 | 100% |
| XRP from 2018-07-01 | -4.0% | -89.6% | -0.05 | 0.24 | 75 | 31% |
| ↳ XRP buy & hold | +10.9% | -83.3% | 0.13 | 0.58 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +27.5% | +37.8% |
| CAGR 5th pct | -4.9% | -12.7% |
| MaxDD median | -58.4% | -79.3% |
| MaxDD worst 5 % | -82.6% | -95.6% |
| P(MAR > buy & hold) | 55% | |
| P(CAGR > buy & hold) | 33% | |

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
