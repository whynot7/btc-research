"""Offline tests of the bench with synthetic prices (no network)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from harness import bench, data, engine, metrics

ROOT = Path(__file__).resolve().parent.parent


def synth(n=3000, freq="1D", seed=1, drift=0.0012, vol=0.04, start="2017-01-01"):
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=n, freq=freq)
    c = 1000 * np.exp(np.cumsum(rng.normal(drift, vol, n)))
    o = np.concatenate([[c[0]], c[:-1]])
    hi = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.01, n)))
    lo = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.01, n)))
    return pd.DataFrame({"open": o, "high": hi, "low": lo, "close": c, "volume": 1.0}, index=idx)


def load_ref():
    spec = importlib.util.spec_from_file_location("v3_rule", ROOT / "reference" / "v3_rule.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_parity_with_reference_v3_next_close():
    from strategies import v3
    df = synth()
    sig = v3.signal(df)
    ref = load_ref()
    r_ref = ref.simulate(df, sig.astype(int), "2018-01-01", "2024-12-31", 1.0, 0.0)
    cfg = engine.Config(fee=0.0, execution="next_close", use_funding=False)
    r = engine.run(df, sig, cfg, None, "2018-01-01", "2024-12-31")["ret"]
    # the reference may already hold a position on day 1; compare after the first switch
    common = r.index[30:]
    assert np.allclose(r.loc[common].values, r_ref.loc[common].values, atol=1e-12)


def test_fees_charged_per_side():
    df = synth()
    tgt = pd.Series(0.0, index=df.index)
    tgt.iloc[500:600] = 1.0
    a = engine.run(df, tgt, engine.Config(fee=0.0, use_funding=False), None, "2017-02-01")["ret"]
    b = engine.run(df, tgt, engine.Config(fee=0.001, use_funding=False), None, "2017-02-01")["ret"]
    ratio = (1 + b).prod() / (1 + a).prod()
    assert ratio == pytest.approx((1 - 0.001) ** 2, rel=2e-3)


def test_no_lookahead():
    from strategies import ensemble_trend, trendvol, v3
    df = synth(freq="4h", n=4000)
    cut = 3000
    df2 = df.copy()
    df2.iloc[cut:, :4] *= 3.0          # change the future
    for mod in (v3, trendvol, ensemble_trend):
        s1, s2 = mod.signal(df), mod.signal(df2)
        assert np.allclose(s1.iloc[:cut].values, s2.iloc[:cut].values), mod.__name__
        cfg = engine.Config(fee=0.0005)
        r1 = engine.run(df, s1, cfg, None, df.index[300])["ret"]
        r2 = engine.run(df2, s2, cfg, None, df.index[300])["ret"]
        assert np.allclose(r1.iloc[: cut - 302].values, r2.iloc[: cut - 302].values)


def test_liquidation_on_intrabar_low():
    df = synth(n=400, vol=0.0, drift=0.0)
    df.iloc[300, df.columns.get_loc("low")] = df.close.iloc[299] * 0.62   # -38 % wick, closes flat
    tgt = pd.Series(3.0, index=df.index)
    res = engine.run(df, tgt, engine.Config(fee=0.0, use_funding=False), None, df.index[10])
    assert res.attrs["liquidated"]
    assert ((1 + res["ret"]).prod()) == pytest.approx(0.0, abs=1e-12)
    ok = engine.run(df, pd.Series(1.0, index=df.index), engine.Config(fee=0.0, use_funding=False), None, df.index[10])
    assert not ok.attrs["liquidated"]


def test_short_receives_positive_funding():
    df = synth(n=400, vol=0.0, drift=0.0)
    f = pd.Series(0.001, index=df.index)
    longs = engine.run(df, pd.Series(1.0, index=df.index), engine.Config(fee=0.0), f, df.index[10])
    shorts = engine.run(df, pd.Series(-1.0, index=df.index), engine.Config(fee=0.0), f, df.index[10])
    assert (1 + longs["ret"]).prod() < 1 < (1 + shorts["ret"]).prod()


def test_resample_offsets():
    h1 = synth(n=24 * 30, freq="1h")
    d0 = data.resample(h1, "1d", 0)
    d8 = data.resample(h1, "1d", 8)
    assert (d0.index.hour == 0).all() and (d8.index.hour == 8).all()
    assert d0["close"].iloc[0] == h1["close"].iloc[23]


def test_deflated_sharpe_drops_with_more_trials():
    r = pd.Series(np.random.default_rng(3).normal(0.001, 0.02, 2000))
    p1 = metrics.deflated_sharpe(r, 1, 0.0)
    p100 = metrics.deflated_sharpe(r, 100, 0.0005)
    assert p1 > p100


def test_bench_end_to_end_offline(tmp_path, monkeypatch):
    frames = {a: synth(n=24 * 365 * 3 + 500, freq="1h", seed=i, drift=0.00004, vol=0.008, start="2017-08-01")
              for i, a in enumerate(bench.CROSS_ASSETS)}
    monkeypatch.setattr(data, "load", lambda a, tf, off=0, source="auto": (data.resample(frames[a], tf, off), "synthetic"))
    monkeypatch.setattr(data, "funding", lambda a, idx, tf: (pd.Series(0.0, index=idx), "none"))
    monkeypatch.setattr(bench, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(bench, "LEDGER", tmp_path / "LEDGER.csv")
    monkeypatch.setattr(bench, "ROOT", tmp_path)
    monkeypatch.setattr(bench, "EVAL_START", "2018-07-01")
    monkeypatch.setattr(bench, "PERIODS", {"a": ("2018-07-01", "2019-12-31"), "b": ("2020-01-01", None)})
    monkeypatch.setattr(bench, "all_strategies", lambda: ["v3"])
    out = bench.evaluate("v3", quick=True)
    bench.finalize(post_to_issues=())
    rep = (tmp_path / "results" / "v3" / "report.md").read_text()
    assert "{{" not in rep and "Deflated Sharpe" in rep
    assert set(out["checklist"]) and (tmp_path / "LEDGER.csv").exists()
    bench.write_leaderboard()
    assert "v3" in (tmp_path / "LEADERBOARD.md").read_text()


def test_missing_funding_is_conservative():
    df = synth(n=400, vol=0.0, drift=0.0)
    f = pd.Series(np.nan, index=df.index)
    cfg = engine.Config(fee=0.0, funding_fallback_pa=0.365)
    longs = engine.run(df, pd.Series(1.0, index=df.index), cfg, f, df.index[10])
    shorts = engine.run(df, pd.Series(-1.0, index=df.index), cfg, f, df.index[10])
    assert (1 + longs["ret"]).prod() < 1
    assert (1 + shorts["ret"]).prod() == pytest.approx(1.0)
