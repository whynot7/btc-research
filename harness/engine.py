"""Backtest engine shared by all strategies.

Execution model (identical for everyone):
  * target[t] = exposure decided at the CLOSE of bar t (from data up to and including t).
  * execution="next_open" (default): filled at the open of bar t+1 (seconds after the close
    for 24/7 markets; what an automated bot does). "next_close": filled at the close of bar
    t+1 (one full bar late; conservative stress test).
  * The account holds a quantity of the asset (linear perp / spot). Exposure drifts with
    price; we rebalance only when the target changes sign, goes to 0, or deviates from the
    current exposure by more than `rebalance_threshold` (fraction of equity).
  * Costs: `fee` per side on traded notional. Funding: per-bar rate * notional (longs pay
    positive funding, shorts receive it).
  * Liquidation: checked every bar against the bar's LOW (longs) / HIGH (shorts) with a
    maintenance margin of `mmr` of notional. A liquidation sets equity to 0 and ends the run.
  * Idle equity earns `cash_yield` only while flat (conservative; margin is not lent out).
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Config:
    fee: float = 0.0005                 # per side
    execution: str = "next_open"        # or "next_close"
    rebalance_threshold: float = 0.10
    max_leverage: float = 3.0           # hard cap on |target|
    mmr: float = 0.012                  # maintenance margin (Lighter BTC/ETH: 1.2 % of notional)
    cash_yield: float = 0.0             # annual yield while flat
    use_funding: bool = True


def bars_per_year(index: pd.DatetimeIndex) -> float:
    return pd.Timedelta(days=365) / pd.Series(index).diff().median()


def run(df: pd.DataFrame, target: pd.Series, cfg: Config, funding: pd.Series | None = None,
        start=None, end=None) -> pd.DataFrame:
    """Per-bar result frame: ret (strategy return), expo (exposure held), trade (traded notional / equity).
    `start`/`end` select the evaluation window; the strategy starts flat at `start`."""
    idx = df.index
    tgt = target.reindex(idx).fillna(0.0).clip(-cfg.max_leverage, cfg.max_leverage).values
    o, h, l, c = (df[k].values.astype(float) for k in ("open", "high", "low", "close"))
    fnd = (funding.reindex(idx).fillna(0.0).values if (funding is not None and cfg.use_funding)
           else np.zeros(len(idx)))
    sel = np.ones(len(idx), bool)
    if start is not None:
        sel &= idx >= pd.Timestamp(start)
    if end is not None:
        sel &= idx <= pd.Timestamp(end)
    sel[0] = False                                   # need a previous close
    pos = np.flatnonzero(sel)
    if len(pos) == 0:
        raise ValueError("empty evaluation window")
    cash_bar = cfg.cash_yield / bars_per_year(idx)

    R = np.zeros(len(pos)); E = np.zeros(len(pos)); T = np.zeros(len(pos))
    cash, qty, dead = 1.0, 0.0, False

    def rebalance(want, px):
        nonlocal cash, qty
        eq = cash + qty * px
        cur = qty * px / eq if eq > 0 else 0.0
        need = (np.sign(want) != np.sign(cur)) or abs(want - cur) > cfg.rebalance_threshold
        if not need or eq <= 0:
            return 0.0
        new_qty = want * eq / px
        traded = abs(new_qty - qty) * px
        cash -= (new_qty - qty) * px + traded * cfg.fee
        qty = new_qty
        return traded

    for k, i in enumerate(pos):
        if dead:
            break
        eq_start = cash + qty * c[i - 1]
        want = tgt[i - 1]
        traded = rebalance(want, o[i]) if cfg.execution == "next_open" else 0.0
        notional = qty * (o[i] if cfg.execution == "next_open" else c[i - 1])
        E[k] = notional / eq_start if eq_start > 0 else 0.0
        if qty != 0:                                  # liquidation over the bar
            worst = l[i] if qty > 0 else h[i]
            if cash + qty * worst <= cfg.mmr * abs(qty) * worst:
                R[k] = -1.0
                dead = True
                break
        cash -= notional * fnd[i]
        if qty == 0 and cash > 0:
            cash *= 1 + cash_bar
        if cfg.execution == "next_close":
            traded = rebalance(want, c[i])
        eq_end = cash + qty * c[i]
        R[k] = eq_end / eq_start - 1 if eq_start > 0 else 0.0
        T[k] = traded / eq_start if eq_start > 0 else 0.0
        if eq_end <= 0:
            R[k] = -1.0
            dead = True
            break
    out = pd.DataFrame({"ret": R, "expo": E, "trade": T}, index=idx[pos])
    out.attrs["liquidated"] = dead
    return out


def static_mix(df: pd.DataFrame, weight: float, cfg: Config, start=None, end=None) -> pd.DataFrame:
    """Constant-weight asset/cash benchmark (spot, no funding, same costs and rebalance rule)."""
    return run(df, pd.Series(weight, index=df.index), replace(cfg, use_funding=False), None, start, end)
