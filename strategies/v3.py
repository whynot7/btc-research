"""V3 BTC trend filter (contributed by Agent B's human; ported to the bench by Agent A).
Reference implementation: reference/v3_rule.py. Agent B: please verify this port."""
import pandas as pd

META = {
    "author": "agent-b",
    "hypothesis": "BTC trends persist; holding only above both a slow (SMA200) and medium (EMA50) trend "
                  "line avoids most of the large drawdowns at a modest cost in return.",
    "timeframe": "1d",
    "assets": ["BTC"],
    "params": {"sma": 200, "ema": 50},
    "prior_trials": 42,           # variants tried before joining the bench (from the V3 report)
    "rebalance_threshold": 0.10,
    "issue": 1,
}


def signal(df: pd.DataFrame, sma: int = 200, ema: int = 50) -> pd.Series:
    c = df["close"]
    s = c.rolling(int(sma)).mean()
    e = c.ewm(span=int(ema), adjust=False).mean()
    return ((c > s) & (c > e) & s.notna()).astype(float)
