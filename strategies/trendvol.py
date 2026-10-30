"""TrendVol (Agent A). Identical rules to the paper bot running in a separate repo."""
import math

import numpy as np
import pandas as pd

META = {
    "author": "agent-a",
    "hypothesis": "Crypto trends persist on 4h bars in both directions; volatility targeting keeps risk "
                  "roughly constant, so exposure is high in calm trends and low in turbulent markets.",
    "timeframe": "4h",
    "assets": ["BTC", "ETH"],     # equal-weight portfolio
    "params": {"ema": 200, "band": 0.01, "vol_window": 180, "vol_target": 0.60, "max_lev": 3.0},
    "prior_trials": 60,           # rough count of variants Agent A tried before the bench
    "rebalance_threshold": 0.25,
    "issue": None,
}


def signal(df: pd.DataFrame, ema: int = 200, band: float = 0.01, vol_window: int = 180,
           vol_target: float = 0.60, max_lev: float = 3.0) -> pd.Series:
    c = df["close"]
    e = c.ewm(span=int(ema), adjust=False).mean().values
    cv = c.values
    state = np.zeros(len(c))
    prev = 0.0
    for i in range(len(c)):
        if cv[i] > e[i] * (1 + band):
            prev = 1.0
        elif cv[i] < e[i] * (1 - band):
            prev = -1.0
        state[i] = prev
    ppy = 365 * 24 / ((c.index[1] - c.index[0]) / pd.Timedelta(hours=1))
    r = np.log(c).diff().fillna(0.0)
    vol = r.rolling(int(vol_window), min_periods=1).std(ddof=0).values * math.sqrt(ppy)
    vol = np.maximum(vol, 1e-6)
    expo = state * np.minimum(max_lev, vol_target / vol)
    expo[: int(ema)] = 0.0        # warm-up
    return pd.Series(expo, index=c.index)
