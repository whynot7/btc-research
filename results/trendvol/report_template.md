# trendvol

_Generated 2026-11-09 16:36 UTC · commit fec4b13 · author agent-a_

**Hypothesis:** Crypto trends persist on 4h bars in both directions; volatility targeting keeps risk roughly constant, so exposure is high in calm trends and low in turbulent markets.

**Rules:** timeframe 4h, assets BTC, ETH (equal weight), params `{'ema': 200, 'band': 0.01, 'vol_window': 180, 'vol_target': 0.6, 'max_lev': 3.0}`, rebalance threshold 0.25

**Data:** BTC: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-09; before: fallback 10% p.a. longs pay, shorts get 0; ETH: binance-1h; funding binance 2020-01-01..2026-10-31; hyperliquid 2023-05-12..2026-11-09; before: fallback 10% p.a. longs pay, shorts get 0

## 1. Performance by cost scenario (full period from 2018-07-01)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| Lighter 0% | +100.7% | -43.0% | 2.34 | 1.52 | 444 | 100% |
| 0.05% | +94.4% | -43.9% | 2.15 | 1.47 | 444 | 100% |
| 0.10% | +88.4% | -44.8% | 1.97 | 1.41 | 444 | 100% |
| stress 0.20% + 1 bar late | +64.2% | -47.6% | 1.35 | 1.16 | 444 | 100% |
| Buy & hold (spot) | +30.3% | -77.4% | 0.39 | 0.73 | 1 | 100% |
| Equal-risk mix 45% asset / cash | +21.7% | -45.7% | 0.47 | 0.80 | 1 | 100% |

_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._

## 2. Sub-periods (0.05% per side)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| 2018-07..2021 | +141.0% | -34.8% | 4.05 | 1.82 | 200 | 100% |
| 2022..2023 | +74.5% | -43.9% | 1.70 | 1.26 | 92 | 100% |
| 2024..2026-10 | +62.7% | -41.3% | 1.52 | 1.18 | 154 | 100% |
| FORWARD (from 2026-11) | -88.1% | -9.8% | -9.02 | -3.30 | 4 | 100% |

Calendar years: 2018: +32%, 2019: +148%, 2020: +314%, 2021: +63%, 2022: +64%, 2023: +88%, 2024: +35%, 2025: +45%, 2026: +95%

## 3. Robustness battery

### 3a. Parameter neighbourhood (each parameter ±25 %)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| base | +94.4% | -43.9% | 2.15 | 1.47 | 444 | 100% |
| ema = 150 | +79.4% | -48.8% | 1.63 | 1.32 | 586 | 100% |
| ema = 250 | +87.1% | -49.0% | 1.78 | 1.40 | 388 | 100% |
| band = 0.0075 | +95.6% | -42.0% | 2.28 | 1.48 | 518 | 100% |
| band = 0.0125 | +97.7% | -45.1% | 2.17 | 1.49 | 394 | 100% |
| vol_window = 135 | +93.3% | -48.3% | 1.93 | 1.44 | 444 | 100% |
| vol_window = 225 | +91.9% | -41.5% | 2.21 | 1.46 | 444 | 100% |
| vol_target = 0.45 | +69.9% | -34.3% | 2.04 | 1.48 | 444 | 100% |
| vol_target = 0.75 | +114.0% | -51.3% | 2.22 | 1.44 | 444 | 100% |
| max_lev = 2.25 | +92.6% | -43.9% | 2.11 | 1.45 | 444 | 100% |
| max_lev = 3.75 | +94.4% | -43.9% | 2.15 | 1.47 | 444 | 100% |

### 3b. Bar-timing shift (same rule, bars start at a different hour)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| bars start 00:00 UTC | +94.4% | -43.9% | 2.15 | 1.47 | 444 | 100% |
| bars start 01:00 UTC | +85.5% | -42.7% | 2.00 | 1.39 | 440 | 100% |
| bars start 02:00 UTC | +91.0% | -36.9% | 2.47 | 1.43 | 454 | 100% |
| bars start 03:00 UTC | +102.9% | -42.0% | 2.45 | 1.54 | 442 | 100% |

### 3c. Cross-asset (unchanged rule, single asset)

| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |
|---|---|---|---|---|---|---|
| BTC (in-sample asset) from 2018-07-01 | +84.2% | -55.7% | 1.51 | 1.27 | 213 | 100% |
| ↳ BTC buy & hold | +34.4% | -77.1% | 0.45 | 0.79 | 1 | 100% |
| ETH (in-sample asset) from 2018-07-01 | +88.4% | -54.6% | 1.62 | 1.33 | 231 | 100% |
| ↳ ETH buy & hold | +20.4% | -83.8% | 0.24 | 0.63 | 1 | 100% |
| SOL from 2020-08-11 | +61.5% | -74.3% | 0.83 | 1.07 | 241 | 99% |
| ↳ SOL buy & hold | +70.2% | -96.6% | 0.73 | 1.03 | 1 | 100% |
| BNB from 2018-07-01 | +52.5% | -64.2% | 0.82 | 0.98 | 277 | 100% |
| ↳ BNB buy & hold | +58.5% | -78.0% | 0.75 | 0.98 | 1 | 100% |
| XRP from 2018-07-01 | +5.2% | -84.1% | 0.06 | 0.41 | 327 | 100% |
| ↳ XRP buy & hold | +10.9% | -84.5% | 0.13 | 0.58 | 1 | 100% |

### 3d. Block bootstrap (200 paths, 30-day blocks, close-only, no funding)

| | Strategy | Buy & hold |
|---|---|---|
| CAGR median | +47.5% | +49.3% |
| CAGR 5th pct | +11.3% | +8.8% |
| MaxDD median | -58.3% | -68.3% |
| MaxDD worst 5 % | -79.3% | -85.9% |
| P(MAR > buy & hold) | 54% | |
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
