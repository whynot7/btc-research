#!/usr/bin/env python3
"""
V3 BTC trend rule - standalone reference implementation (pandas + numpy only).

Rule: hold BTC long when the daily close (UTC) is above BOTH the 200-day SMA and the
50-day EMA (span 50, adjust=False); otherwise hold cash. The signal is computed at the
daily close of day t and executed either at the close of day t+1 ("next_close", default,
conservative) or at ~01:00 UTC on day t+1 ("next_open", close of the first 1h bar).

Simulation: constant leverage L, rebalanced daily (as a perp position would be topped up),
cost per side on traded notional, optional perp funding on long notional, optional yield
on cash days. Outputs CAGR / max drawdown / MAR / Sharpe for in-sample (2016-2021) and
out-of-sample (2022-now) windows, plus BTC buy-and-hold and an "equal-risk" static
BTC/cash mix whose weight is chosen to match the strategy's max drawdown.

Examples:
  python v3_rule.py                                  # 1x, 0.0515%/side, no funding, cash 0%
  python v3_rule.py --fee 0.000515 --funding binance # perp-style, Binance funding history
  python v3_rule.py --fee 0.001 --cash-yield 0.045   # spot, idle cash earns 4.5% p.a.
  python v3_rule.py --leverage 1.9 --funding binance
  python v3_rule.py --execution next_open            # needs Binance 1h data (from 2017-08)
Paper research only, not investment advice.
"""
import argparse, json, time, urllib.request
import numpy as np, pandas as pd

UA = {"User-Agent": "Mozilla/5.0"}
IS = ("2016-01-01", "2021-12-31")
OOS_START = "2022-01-01"


def _get(url):
    for k in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception as e:  # retry transient errors
            last = e; time.sleep(2)
    raise RuntimeError(f"download failed: {url} ({last})")


def load_daily(source="yahoo"):
    """Daily OHLC in UTC, completed days only. Yahoo BTC-USD has history from 2014-09; Binance from 2017-08."""
    if source == "yahoo":
        end = int(time.time())
        r = _get(f"https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?period1=1410912000&period2={end}&interval=1d")["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")},
                          index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    else:
        rows, st = [], 1502928000000
        while True:
            d = _get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&startTime={st}&limit=1000")
            rows += d
            if len(d) < 1000: break
            st = d[-1][0] + 1
        a = np.array([x[:5] for x in rows], float)
        df = pd.DataFrame(a[:, 1:5], columns=["open", "high", "low", "close"], index=pd.to_datetime(a[:, 0], unit="ms"))
    df = df.dropna(subset=["close"]); df = df[~df.index.duplicated(keep="last")].sort_index().asfreq("D").ffill()
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    return df[df.index < today]


def load_first_hour_close(index):
    """Close of the 00:00-01:00 UTC 1h bar per day (Binance spot BTCUSDT, from 2017-08-17)."""
    rows, st = [], 1502928000000
    while True:
        d = _get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&startTime={st}&limit=1000")
        rows += d
        if len(d) < 1000: break
        st = d[-1][0] + 1
    s = pd.Series([float(x[4]) for x in rows], index=pd.to_datetime([x[0] for x in rows], unit="ms"))
    s = s[s.index.hour == 0]; s.index = s.index.normalize()
    return s.reindex(index)


def load_funding(index, mode, const_annual):
    """Daily long funding rate (sum of 8h rates). 'binance' = Binance BTCUSDT perp history (0.01%/8h before 2019-09-10)."""
    if mode == "none":
        return pd.Series(0.0, index=index)
    if mode == "const":
        return pd.Series(const_annual / 365, index=index)
    rows, st = [], 1567900800000
    while True:
        d = _get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&startTime={st}&limit=1000")
        rows += d
        if len(d) < 1000: break
        st = d[-1]["fundingTime"] + 1
    f = pd.Series([float(x["fundingRate"]) for x in rows],
                  index=pd.to_datetime([x["fundingTime"] for x in rows], unit="ms").normalize()).groupby(level=0).sum()
    out = f.reindex(index); out[index < f.index[0]] = 0.0003
    return out.fillna(0.0)


def signal(close, sma_n=200, ema_n=50):
    sma = close.rolling(sma_n).mean(); ema = close.ewm(span=ema_n, adjust=False).mean()
    return ((close > sma) & (close > ema) & sma.notna()).astype(int)  # 1 = long, 0 = cash, known at close t


def simulate(df, sig, lo, hi, lev=1.0, fee=0.000515, funding=None, cash_yield=0.0, execution="next_close", first_hour=None):
    c = df.close; w = slice(lo, hi)
    cc, pv = c[w].values, c.shift(1)[w].values
    fd = (funding if funding is not None else pd.Series(0.0, index=c.index))[w].values
    held_prev = sig.shift(2).fillna(0)[w].values   # position during day i under next_close execution
    held_new = sig.shift(1).fillna(0)[w].values    # position decided at close i-1
    n = len(cc); R = np.zeros(n)
    if execution == "next_open":
        qq = first_hour.fillna(c.shift(1))[w].values
    for i in range(n):
        if execution == "next_close":
            if held_prev[i]:
                if i == 0: R[i] -= lev * fee                       # entry cost if already long at window start
                x = cc[i] / pv[i] - 1; fu = lev * fd[i]; g = lev * x - fu
                expo = lev * (1 + x) / (1 + g) if 1 + g > 0 else lev   # exposure drift before daily rebalance
                nxt = held_prev[i + 1] if i + 1 < n else 1
                R[i] += g - (abs(expo - lev) if nxt else expo) * fee   # rebalance or exit cost
            else:
                R[i] += cash_yield / 365
                if i + 1 < n and held_prev[i + 1]: R[i] -= lev * fee  # entry at today's close
        else:  # next_open: switch at ~01:00 UTC on day i
            a, b = held_prev[i], held_new[i]
            r1 = lev * (qq[i] / pv[i] - 1) if a else 0.0
            r2 = lev * (cc[i] / qq[i] - 1) if b else 0.0
            R[i] = ((1 + r1) * (1 + r2) - 1 - (lev * fd[i] if b else 0.0)
                    - (lev * fee if (a != b or (i == 0 and a)) else 0.0) + (cash_yield / 365 if not b else 0.0))
    return pd.Series(R, index=c[w].index)


def static_mix(df, weight, lo, hi, cash_yield=0.0, fee=0.001):
    """Constant-weight BTC/cash, rebalanced daily, fee on turnover."""
    x = df.close.pct_change()[lo:hi].values; R = np.zeros(len(x))
    for i in range(len(x)):
        g = weight * x[i] + (1 - weight) * cash_yield / 365
        R[i] = g - (weight * fee if i == 0 else 0.0)
        R[i] -= abs(weight * (1 + x[i]) / (1 + g) - weight) * fee
    return pd.Series(R, index=df.close[lo:hi].index)


def stats(R):
    eq = (1 + R).cumprod(); yrs = (R.index[-1] - R.index[0]).days / 365.25
    cagr = eq.iloc[-1] ** (1 / yrs) - 1; mdd = (eq / eq.cummax() - 1).min()
    return dict(CAGR=cagr, maxDD=mdd, MAR=cagr / abs(mdd), Sharpe=R.mean() / R.std() * np.sqrt(365))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=["yahoo", "binance"], default="yahoo")
    ap.add_argument("--fee", type=float, default=0.000515, help="cost per side as a fraction (0.000515 = 0.0515%%)")
    ap.add_argument("--leverage", type=float, default=1.0)
    ap.add_argument("--funding", choices=["none", "binance", "const"], default="none")
    ap.add_argument("--funding-annual", type=float, default=0.10, help="used with --funding const")
    ap.add_argument("--cash-yield", type=float, default=0.0, help="annual yield on cash days, e.g. 0.045")
    ap.add_argument("--execution", choices=["next_close", "next_open"], default="next_close")
    ap.add_argument("--bench-fee", type=float, default=0.001, help="spot cost per side for buy-and-hold / static mix")
    a = ap.parse_args()

    df = load_daily(a.source); sig = signal(df.close)
    fund = load_funding(df.index, a.funding, a.funding_annual)
    fh = load_first_hour_close(df.index) if a.execution == "next_open" else None
    wins = {"IS": IS, "OOS": (OOS_START, str(df.index[-1].date()))}
    if df.index[0] > pd.Timestamp(IS[0]) - pd.Timedelta(days=200):
        wins["IS"] = (str((df.index[0] + pd.Timedelta(days=200)).date()), IS[1])  # binance source: shorter IS
    res = {}
    for name, (lo, hi) in wins.items():
        res[name] = {"V3": simulate(df, sig, lo, hi, a.leverage, a.fee, fund, a.cash_yield, a.execution, fh),
                     "BTC buy&hold": static_mix(df, 1.0, lo, hi, 0.0, a.bench_fee)}
    grid = np.round(np.arange(0.05, 1.0001, 0.01), 2)
    for name in wins:   # equal-risk weight matched in each window; the IS-matched one is the honest choice
        tgt = stats(res[name]["V3"])["maxDD"]
        wgt = min(grid, key=lambda w: abs(stats(static_mix(df, w, *wins[name], 0.0, a.bench_fee))["maxDD"] - tgt))
        for nm2, (lo, hi) in wins.items():
            res[nm2][f"equal-risk {wgt:.2f} BTC (DD-matched {name})"] = static_mix(df, wgt, lo, hi, a.cash_yield, a.bench_fee)
    pd.set_option("display.float_format", "{:.3f}".format); pd.set_option("display.width", 200)
    print(f"data {df.index[0].date()}..{df.index[-1].date()} ({a.source}); fee/side {a.fee}, lev {a.leverage}, "
          f"funding {a.funding}, cash yield {a.cash_yield}, execution {a.execution}")
    for name, (lo, hi) in wins.items():
        print(f"\n{name} {lo}..{hi}")
        print(pd.DataFrame({k: stats(v) for k, v in res[name].items()}).T.to_string())
    print(f"\ncurrent signal (close {df.index[-1].date()}): {'LONG' if sig.iloc[-1] else 'CASH'}")


if __name__ == "__main__":
    main()
