"""Performance metrics and the deflated Sharpe ratio (Bailey & López de Prado, 2014)."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats as st

from .engine import bars_per_year


def summary(res: pd.DataFrame) -> dict:
    r = res["ret"]
    if len(r) < 2:
        return {}
    eq = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]) / pd.Timedelta(days=365.25)
    final = float(eq.iloc[-1])
    cagr = final ** (1 / yrs) - 1 if final > 0 and yrs > 0 else -1.0
    mdd = float((eq / eq.cummax() - 1).min())
    ppy = bars_per_year(r.index)
    sd = r.std()
    down = r[r < 0].std()
    expo = res["expo"]
    entries = res.attrs.get("entries", count_entries(expo))
    return {
        "CAGR": cagr,
        "MaxDD": mdd,
        "MAR": cagr / abs(mdd) if mdd < 0 else float("nan"),
        "Sharpe": float(r.mean() / sd * math.sqrt(ppy)) if sd > 0 else float("nan"),
        "Sortino": float(r.mean() / down * math.sqrt(ppy)) if down and down > 0 else float("nan"),
        "Final": final,
        "Trades": entries,
        "InMarket": float((expo != 0).mean()),
        "AvgGross": float(expo.abs().mean()),
        "WorstBar": float(r.min()),
        "Liquidated": bool(res.attrs.get("liquidated", False)),
        "Years": float(yrs),
    }


def count_entries(expo: pd.Series) -> int:
    """Number of new positions: flat -> in market, plus direction flips."""
    prev = expo.shift(1).fillna(0.0)
    return int(((prev == 0) & (expo != 0)).sum() + ((np.sign(prev) * np.sign(expo)) < 0).sum())


def per_year(res: pd.DataFrame) -> pd.Series:
    return (1 + res["ret"]).groupby(res.index.year).prod() - 1


def deflated_sharpe(returns: pd.Series, n_trials: int, sr_trials_var: float) -> float:
    """Probability that the true (per-bar) Sharpe > 0 after correcting for `n_trials` tried
    variants whose (per-bar) Sharpe ratios have variance `sr_trials_var`.
    Returns a probability in [0, 1]; >= 0.95 is the usual bar."""
    r = returns.dropna()
    T = len(r)
    if T < 30 or r.std() == 0:
        return float("nan")
    sr = r.mean() / r.std()
    g3 = st.skew(r)
    g4 = st.kurtosis(r, fisher=False)
    n = max(int(n_trials), 1)
    if n > 1 and sr_trials_var > 0:
        emc = 0.5772156649
        sr0 = math.sqrt(sr_trials_var) * ((1 - emc) * st.norm.ppf(1 - 1 / n) + emc * st.norm.ppf(1 - 1 / (n * math.e)))
    else:
        sr0 = 0.0
    denom = math.sqrt(max(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2, 1e-12))
    return float(st.norm.cdf((sr - sr0) * math.sqrt(T - 1) / denom))
