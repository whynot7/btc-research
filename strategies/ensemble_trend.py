"""Ensemble trend (Agent A proposal). Instead of betting on one lookback (e.g. 200/50), average the
trend votes of many lookbacks. Exposure moves in steps between 0 and 1, which should cut whipsaws
and parameter sensitivity without adding a tunable parameter."""
import pandas as pd

META = {
    "author": "agent-a",
    "hypothesis": "Averaging trend signals over many lookbacks keeps most of V3's drawdown protection "
                  "while being far less sensitive to the exact lookback and trading less abruptly.",
    "timeframe": "1d",
    "assets": ["BTC"],
    "params": {"min_lb": 20, "max_lb": 250},
    "prior_trials": 0,
    "rebalance_threshold": 0.10,
    "issue": 2,
}

LOOKBACKS = (20, 50, 100, 150, 200, 250)


def signal(df: pd.DataFrame, min_lb: int = 20, max_lb: int = 250) -> pd.Series:
    c = df["close"]
    scale = (max_lb - min_lb) / (LOOKBACKS[-1] - LOOKBACKS[0])
    lbs = [int(round(min_lb + (lb - LOOKBACKS[0]) * scale)) for lb in LOOKBACKS]
    votes = []
    for lb in lbs:
        sma = c.rolling(lb).mean()
        votes.append(((c > sma) & sma.notna()).astype(float))
    expo = sum(votes) / len(votes)
    expo[c.rolling(max(lbs)).mean().isna()] = 0.0
    return expo
