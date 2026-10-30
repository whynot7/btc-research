"""Market data for the shared test bench.

Primary source: Binance spot 1h klines (data-api.binance.vision, public market-data
mirror), resampled to 4h / 1d with a configurable session offset. One source for every
timeframe keeps results consistent and makes the bar-timing test possible.
Fallback: Yahoo daily (no intraday, so no timing shift).
Funding: Hyperliquid hourly funding where available, otherwise a constant assumption.

Everything is cached in data/ (git-ignored, cached by CI).
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

CACHE = Path(__file__).resolve().parent.parent / "data"
UA = {"User-Agent": "Mozilla/5.0 (btc-research bench)"}
BINANCE = "https://data-api.binance.vision/api/v3/klines"
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}-USD?period1=1410912000&period2={end}&interval=1d"
HL = "https://api.hyperliquid.xyz/info"

FUNDING_FALLBACK_PA = 0.10   # long pays ~10 % p.a. when no venue history is available
TF_HOURS = {"1h": 1, "4h": 4, "1d": 24}


def _get(url: str, data: dict | None = None):
    last = None
    for k in range(5):
        try:
            body = json.dumps(data).encode() if data is not None else None
            hdr = {**UA, **({"Content-Type": "application/json"} if data is not None else {})}
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=hdr), timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (k + 1))
    raise RuntimeError(f"download failed: {url} ({last})")


# ---------------------------------------------------------------- price data
def _binance_1h(asset: str) -> pd.DataFrame:
    path = CACHE / f"{asset}_1h.csv"
    old = pd.read_csv(path, index_col=0, parse_dates=True) if path.exists() else None
    st = int(old.index[-1].value // 10**6) + 1 if old is not None and len(old) else 1483228800000  # 2017-01-01
    rows = []
    while True:
        d = _get(f"{BINANCE}?symbol={asset}USDT&interval=1h&startTime={st}&limit=1000")
        if not d:
            break
        rows += d
        st = d[-1][0] + 1
        if len(d) < 1000:
            break
    new = pd.DataFrame(
        [[float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in rows],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.to_datetime([x[0] for x in rows], unit="ms"),
    )
    df = pd.concat([old, new]) if (old is not None and len(new)) else (old if old is not None else new)
    df = df[~df.index.duplicated(keep="last")].sort_index().astype(float)
    CACHE.mkdir(exist_ok=True)
    df.to_csv(path)
    return df


def _yahoo_1d(asset: str) -> pd.DataFrame:
    r = _get(YAHOO.format(sym=asset, end=int(time.time())))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")},
                      index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return df.dropna(subset=["close"])


def _complete_only(df: pd.DataFrame, hours: int) -> pd.DataFrame:
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    return df[df.index + pd.Timedelta(hours=hours) <= now]


def resample(h1: pd.DataFrame, timeframe: str, offset_h: int = 0) -> pd.DataFrame:
    """Aggregate 1h bars into `timeframe` bars starting at `offset_h` UTC. Drops incomplete bars."""
    hours = TF_HOURS[timeframe]
    if hours == 1:
        return _complete_only(h1, 1)
    g = h1.resample(f"{hours}h", offset=f"{offset_h}h")
    df = pd.DataFrame({"open": g.open.first(), "high": g.high.max(), "low": g.low.min(),
                       "close": g.close.last(), "volume": g.volume.sum(), "n": g.close.count()})
    df = df[df.n >= hours * 0.75].drop(columns="n")       # skip bars with large exchange outages
    return _complete_only(df, hours)


def load(asset: str, timeframe: str, offset_h: int = 0, source: str = "auto") -> tuple[pd.DataFrame, str]:
    """OHLCV bars (UTC, indexed by bar open time, completed bars only) and the source used."""
    if source in ("auto", "binance"):
        try:
            return resample(_binance_1h(asset), timeframe, offset_h), "binance-1h"
        except Exception as e:  # noqa: BLE001
            if source == "binance":
                raise
            print(f"[data] binance failed for {asset}: {e} -> yahoo daily fallback")
    if timeframe != "1d" or offset_h:
        raise RuntimeError("yahoo fallback only provides 1d bars at 00:00 UTC")
    return _complete_only(_yahoo_1d(asset), 24), "yahoo-1d"


# ---------------------------------------------------------------- funding
BINANCE_FUNDING_ZIP = ("https://data.binance.vision/data/futures/um/monthly/fundingRate/"
                       "{a}USDT/{a}USDT-fundingRate-{ym}.zip")


def _get_bytes(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def _binance_funding(asset: str) -> pd.Series:
    """Binance USDT-M funding events from the public monthly archive (from 2019-09)."""
    import io
    import zipfile
    path = CACHE / f"{asset}_funding_binance.csv"
    old = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0] if path.exists() else None
    done = set(old.index.strftime("%Y-%m")) if old is not None else set()
    months = pd.period_range("2019-09", pd.Timestamp.now(tz="UTC").tz_localize(None), freq="M")[:-1]  # last month complete
    parts = []
    for m in months:
        ym = str(m)
        if ym in done and ym != str(months[-1]):
            continue
        raw = _get_bytes(BINANCE_FUNDING_ZIP.format(a=asset, ym=ym))
        if raw is None:
            continue
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), header=None)
        if not str(df.iloc[0, 0]).strip().lstrip("-").isdigit():      # header row present
            df = df.iloc[1:]
        t = pd.to_numeric(df.iloc[:, 0], errors="coerce")
        r = pd.to_numeric(df.iloc[:, -1], errors="coerce")
        parts.append(pd.Series(r.values, index=pd.to_datetime(t.values, unit="ms")).dropna())
    if not parts and old is None:
        raise RuntimeError("no binance funding files")
    s = pd.concat(([old] if old is not None else []) + parts)
    s = s[~s.index.duplicated(keep="last")].sort_index().astype(float)
    CACHE.mkdir(exist_ok=True)
    s.to_frame("rate").to_csv(path)
    return s


def _hyperliquid_funding(asset: str) -> pd.Series:
    path = CACHE / f"{asset}_funding_hl.csv"
    old = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0] if path.exists() else None
    st = int(old.index[-1].value // 10**6) + 1 if old is not None and len(old) else 1672531200000
    rows = []
    while True:
        d = _get(HL, {"type": "fundingHistory", "coin": asset, "startTime": st})
        if not d:
            break
        rows += d
        st = int(d[-1]["time"]) + 1
        if len(d) < 500:
            break
    new = pd.Series([float(x["fundingRate"]) for x in rows], index=pd.to_datetime([int(x["time"]) for x in rows], unit="ms"))
    s = pd.concat([old, new]) if (old is not None and len(new)) else (old if old is not None else new)
    s = s[~s.index.duplicated(keep="last")].sort_index().astype(float)
    CACHE.mkdir(exist_ok=True)
    s.to_frame("rate").to_csv(path)
    return s


def funding(asset: str, index: pd.DatetimeIndex, timeframe: str) -> tuple[pd.Series, str]:
    """Funding rate per bar paid by a 1x long (negative = longs receive).
    NaN where no venue history exists: the engine then charges longs FUNDING_FALLBACK_PA and gives
    shorts nothing (conservative for both sides)."""
    hours = TF_HOURS[timeframe]
    events, src = None, []
    for name, fn in (("binance", _binance_funding), ("hyperliquid", _hyperliquid_funding)):
        try:
            s = fn(asset)
            if len(s):
                events = s if events is None else pd.concat([events, s[s.index > events.index[-1]]])
                src.append(f"{name} {s.index[0].date()}..{s.index[-1].date()}")
        except Exception as e:  # noqa: BLE001
            print(f"[data] {name} funding failed for {asset}: {e}")
    if events is None:
        return pd.Series(np.nan, index=index), f"none (fallback {FUNDING_FALLBACK_PA:.0%} p.a. for longs)"
    rng = pd.date_range(index[0] - pd.Timedelta(hours=1), index[-1] + pd.Timedelta(hours=hours - 1), freq="1h")
    hourly = events.resample("1h").sum().reindex(rng).fillna(0.0)
    cum = hourly.cumsum()
    out = pd.Series(cum.reindex(index + pd.Timedelta(hours=hours - 1)).values
                    - cum.reindex(index - pd.Timedelta(hours=1)).values, index=index)
    out[index < events.index[0]] = np.nan                                  # before any history
    return out, "; ".join(src) + f"; before: fallback {FUNDING_FALLBACK_PA:.0%} p.a. longs pay, shorts get 0"
