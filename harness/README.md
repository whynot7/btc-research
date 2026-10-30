# The shared test bench

Every strategy goes through exactly the same pipeline. Neither agent changes this without a proposal issue
and approval from both humans.

## Data
- **Prices:** Binance spot 1h klines from `data-api.binance.vision` (public market-data mirror, from 2017-08).
  They are resampled to 4h or 1d, which gives one consistent source for every timeframe and makes the
  bar-timing test possible. If Binance fails, the fallback is Yahoo daily (1d only, no timing test).
- **Funding:** real Binance USDT-M funding history (public monthly archive, from 2019-09), then Hyperliquid
  for the most recent weeks. **Before 2019-09 the fallback is conservative:** longs pay 10 % p.a. and shorts
  receive nothing. Assuming shorts receive funding during bear markets would flatter long/short strategies.
- **Completed bars only.** Bars are indexed by their open time in UTC.

## Execution (`engine.py`)
- `signal()` returns the target exposure at the **close** of bar t.
- **Default:** filled at the **open of bar t+1**, seconds later on 24/7 markets.
- **Stress scenario:** filled at the close of t+1, one full bar late.
- **Position model:** the account holds a quantity of the asset (linear perp or spot), so exposure drifts with price.
  It rebalances only on a sign change, an exit, or when the drift exceeds `rebalance_threshold`
  (set per strategy in META).
- **Costs:** `fee` per side on traded notional.
- **Funding:** charged on notional each bar.
- **Liquidation:** checked every bar against the **low** (longs) or **high** (shorts), with 1.2 % maintenance
  margin. A liquidation ends the run with equity 0.
- **Limits:** exposure is capped at `max_lev` (from params, default 3x).
- **Multi-asset strategies:** equal weight across the META assets, rebalanced each bar.

## Evaluation (`bench.py`)
1. **Cost scenarios:**
   - 0 % (Lighter), 0.05 % (main), 0.10 %
   - stress: 0.20 % and one bar late
2. **Benchmarks:**
   - buy & hold (spot, 0.10 %)
   - **equal-risk mix**: a constant asset/cash weight with the same max drawdown as the strategy.
     A trend filter must beat this, not just buy & hold.
3. **Sub-periods:** 2018-07..2021, 2022..2023, 2024..2026-10.
   **FORWARD from 2026-11-01** is the only data neither strategy has seen. It fills up weekly.
4. **Robustness battery:**
   - (a) each parameter ±25 %
   - (b) bar-timing shift (daily bars starting 00/04/…/20 UTC; 4h bars offset 0–3h)
   - (c) the same rule on BTC/ETH/SOL/BNB/XRP
   - (d) block bootstrap (30-day blocks, 200 paths, close-only)
   - (e) deflated Sharpe ratio. It is computed in a final pass for **all** strategies on the same basis:
     daily returns, the same trial count (`LEDGER.csv` variants plus every strategy's declared `prior_trials`)
     and the same Sharpe dispersion across trials. As a result it changes for everyone when new variants are added.
5. **Checklist:** seven pass/fail criteria at the end of each report.

## Counting trials honestly
Every new combination of strategy, params, assets and timeframe adds a row to `LEDGER.csv`.
More rows mean a stricter deflated Sharpe ratio for everyone. That is deliberate: it makes "try 50 variants
and report the best" visible and costly.

## Known limitations
- The bootstrap is close-only, with no funding and no liquidation check. It is a stress test, not a forecast.
- Funding before 2019-09 is a (conservative) constant assumption.
- Spot prices are used for perp strategies. The basis between perp and spot is ignored.
- The equal-weight portfolio is rebalanced every bar at no cost (a small optimism for multi-asset strategies).
