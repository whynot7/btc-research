"""Shared test bench. Usage:  python -m harness.bench <strategy> [<strategy> ...] [--quick]

Writes results/<strategy>/{report.md,metrics.json,equity.csv}, appends LEDGER.csv and, if the
strategy's META has an "issue" number and GITHUB_TOKEN is set, posts the report to that issue.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import os
import subprocess
import urllib.request
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from . import data, engine, metrics

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
LEDGER = ROOT / "LEDGER.csv"

EVAL_START = "2018-07-01"            # common start: Binance 1h data from 2017-08 + 200d warm-up
PERIODS = {                          # sub-periods reported for every strategy
    "2018-07..2021": ("2018-07-01", "2021-12-31"),
    "2022..2023": ("2022-01-01", "2023-12-31"),
    "2024..2026-10": ("2024-01-01", "2026-10-31"),
    "FORWARD (from 2026-11)": ("2026-11-01", None),
}
COSTS = {                            # name -> (fee per side, execution)
    "Lighter 0%": (0.0, "next_open"),
    "0.05%": (0.0005, "next_open"),
    "0.10%": (0.0010, "next_open"),
    "stress 0.20% + 1 bar late": (0.0020, "next_close"),
}
MAIN = "0.05%"
CROSS_ASSETS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
BENCH_FEE = 0.001                    # spot costs for benchmarks
SR_VAR_FALLBACK = 0.09               # variance of annual Sharpe across trials if the ledger has < 3 rows


# ---------------------------------------------------------------- helpers
def load_strategy(name: str):
    mod = importlib.import_module(f"strategies.{name}")
    meta = dict(mod.META)
    meta.setdefault("params", {})
    meta.setdefault("rebalance_threshold", 0.10)
    meta.setdefault("prior_trials", 0)
    return mod, meta


def cfg_for(meta, fee, execution, **kw) -> engine.Config:
    lev = float(meta["params"].get("max_lev", meta.get("max_leverage", 3.0)))
    return engine.Config(fee=fee, execution=execution, rebalance_threshold=meta["rebalance_threshold"],
                         max_leverage=max(lev, 1.0), **kw)


class Market:
    """Cached bars + funding per (asset, timeframe, offset)."""

    def __init__(self):
        self.cache = {}

    def get(self, asset, tf, offset=0):
        key = (asset, tf, offset)
        if key not in self.cache:
            df, src = data.load(asset, tf, offset)
            fnd, fsrc = data.funding(asset, df.index, tf)
            self.cache[key] = (df, fnd, f"{src}; funding {fsrc}")
        return self.cache[key]


def portfolio(mod, meta, mkt: Market, cfg, params=None, assets=None, offset=0, start=EVAL_START, end=None,
              prices=None):
    """Equal-weight portfolio over the strategy's assets. Returns (result frame, per-asset frames)."""
    params = params if params is not None else meta["params"]
    assets = assets or meta["assets"]
    parts = {}
    for a in assets:
        if prices is not None:
            df, fnd = prices[a], None
        else:
            df, fnd, _ = mkt.get(a, meta["timeframe"], offset)
        st = max(pd.Timestamp(start), df.index[0] + (df.index[1] - df.index[0]) * 2)
        if (end is not None and st > pd.Timestamp(end)) or st > df.index[-1]:
            continue
        tgt = mod.signal(df, **params)
        c_a = replace(cfg, max_leverage=max(float(params.get("max_lev", cfg.max_leverage)), 1.0))
        parts[a] = engine.run(df, tgt, c_a, fnd, st, end)
    if not parts:
        return None, {}
    idx = sorted(set().union(*[p.index for p in parts.values()]))
    rets = pd.concat({a: p["ret"] for a, p in parts.items()}, axis=1).reindex(idx).fillna(0.0)
    expo = pd.concat({a: p["expo"].abs() for a, p in parts.items()}, axis=1).reindex(idx).fillna(0.0)
    res = pd.DataFrame({"ret": rets.mean(axis=1), "expo": expo.mean(axis=1), "trade": 0.0})
    res.attrs["liquidated"] = any(p.attrs.get("liquidated") for p in parts.values())
    res.attrs["entries"] = sum(metrics.count_entries(p["expo"]) for p in parts.values())
    return res, parts


def fmt_row(name, s):
    if not s:
        return f"| {name} | – | – | – | – | – | – |"
    liq = " ⚠️liq" if s.get("Liquidated") else ""
    return (f"| {name} | {s['CAGR']:+.1%} | {s['MaxDD']:.1%} | {s['MAR']:.2f} | {s['Sharpe']:.2f} | "
            f"{s['Trades']} | {s['InMarket']:.0%}{liq} |")


HDR = "| | CAGR | MaxDD | MAR | Sharpe | Entries | In market |\n|---|---|---|---|---|---|---|"


def block_bootstrap(close: pd.Series, n_paths: int, block_days: int, seed: int = 7):
    r = np.log(close).diff().dropna().values
    bars_per_day = pd.Timedelta(days=1) / (close.index[1] - close.index[0])
    b = max(int(block_days * bars_per_day), 1)
    rng = np.random.default_rng(seed)
    n = len(r)
    for _ in range(n_paths):
        starts = rng.integers(0, n - b, size=n // b + 1)
        path = np.concatenate([r[s:s + b] for s in starts])[:n]
        px = close.iloc[0] * np.exp(np.concatenate([[0.0], np.cumsum(path)]))
        yield pd.DataFrame({"open": px, "high": px, "low": px, "close": px}, index=close.index)


def git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:  # noqa: BLE001
        return "local"


def ledger_rows():
    if not LEDGER.exists():
        return []
    with LEDGER.open() as f:
        return list(csv.DictReader(f))


def append_ledger(row: dict):
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


def post_issue(number, body):
    tok, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (tok and repo and number):
        return
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues/{number}/comments",
        data=json.dumps({"body": body[:65000]}).encode(),
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}, method="POST")
    urllib.request.urlopen(req, timeout=20)


# ---------------------------------------------------------------- main evaluation
def evaluate(name: str, quick: bool = False) -> dict:
    mod, meta = load_strategy(name)
    mkt = Market()
    tf = meta["timeframe"]
    out = {"strategy": name, "meta": meta, "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    L = [f"# {name}", "", f"_Generated {out['generated']} · commit {git_sha()} · author {meta['author']}_", "",
         f"**Hypothesis:** {meta.get('hypothesis', '–')}", "",
         f"**Rules:** timeframe {tf}, assets {', '.join(meta['assets'])} (equal weight), params `{meta['params']}`, "
         f"rebalance threshold {meta['rebalance_threshold']}", ""]
    sources = {a: mkt.get(a, tf)[2] for a in meta["assets"]}
    L += [f"**Data:** " + "; ".join(f"{a}: {s}" for a, s in sources.items()), ""]

    # 1) cost scenarios, full period + sub-periods
    main_cfg = cfg_for(meta, *COSTS[MAIN])
    L += ["## 1. Performance by cost scenario (full period from " + EVAL_START + ")", "", HDR]
    full = {}
    for cname, (fee, ex) in COSTS.items():
        res, _ = portfolio(mod, meta, mkt, cfg_for(meta, fee, ex))
        full[cname] = metrics.summary(res)
        L.append(fmt_row(cname, full[cname]))
        if cname == MAIN:
            main_res = res
    out["costs"] = full

    # benchmarks on the same assets
    bh = {}
    for a in meta["assets"]:
        df, _, _ = mkt.get(a, tf)
        bh[a] = engine.static_mix(df, 1.0, engine.Config(fee=BENCH_FEE), EVAL_START)
    bh_res = pd.DataFrame({"ret": pd.concat({a: b["ret"] for a, b in bh.items()}, axis=1).fillna(0).mean(axis=1),
                           "expo": 1.0, "trade": 0.0})
    s_bh = metrics.summary(bh_res)
    target_dd = full[MAIN]["MaxDD"]
    best_w, best_gap, s_mix = None, 9, None
    for w in np.round(np.arange(0.05, 1.0001, 0.05), 2):
        parts = [engine.static_mix(mkt.get(a, tf)[0], float(w), engine.Config(fee=BENCH_FEE), EVAL_START)
                 for a in meta["assets"]]
        r = pd.DataFrame({"ret": pd.concat([p["ret"] for p in parts], axis=1).fillna(0).mean(axis=1),
                          "expo": float(w), "trade": 0.0})
        s = metrics.summary(r)
        if abs(s["MaxDD"] - target_dd) < best_gap:
            best_w, best_gap, s_mix = w, abs(s["MaxDD"] - target_dd), s
    L += [fmt_row("Buy & hold (spot)", s_bh), fmt_row(f"Equal-risk mix {best_w:.0%} asset / cash", s_mix), "",
          "_Equal-risk mix: constant weight chosen so its max drawdown matches the strategy's (main scenario). "
          "Beating it is the real test; beating buy & hold on drawdown alone is easy for any filter._", ""]
    out["benchmarks"] = {"buy_hold": s_bh, "equal_risk": {"weight": best_w, **s_mix}}

    # sub-periods (main scenario)
    L += [f"## 2. Sub-periods ({MAIN} per side)", "", HDR]
    out["periods"] = {}
    for pname, (a, b) in PERIODS.items():
        res, _ = portfolio(mod, meta, mkt, main_cfg, start=a, end=b)
        s = metrics.summary(res) if res is not None and len(res) > 30 else {}
        out["periods"][pname] = s
        L.append(fmt_row(pname, s))
    L += ["", "Calendar years: " + ", ".join(f"{y}: {v:+.0%}" for y, v in metrics.per_year(main_res).items()), ""]

    # 2) robustness battery
    L += ["## 3. Robustness battery", ""]
    rob = {}
    # 2a parameter neighbourhood
    rows, mars = [], []
    for p, v in meta["params"].items():
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        for f in (0.75, 1.25):
            nv = type(v)(round(v * f)) if isinstance(v, int) else round(v * f, 6)
            prm = {**meta["params"], p: nv}
            res, _ = portfolio(mod, meta, mkt, main_cfg, params=prm)
            s = metrics.summary(res)
            mars.append(s["MAR"])
            rows.append(fmt_row(f"{p} = {nv}", s))
    rob["param_mar_range"] = [float(np.nanmin(mars)), float(np.nanmax(mars))] if mars else None
    L += ["### 3a. Parameter neighbourhood (each parameter ±25 %)", "", HDR, fmt_row("base", full[MAIN]), *rows, ""]

    # 2b bar-timing shift
    offsets = [0, 4, 8, 12, 16, 20] if tf == "1d" else ([0, 1, 2, 3] if tf == "4h" else [0])
    rows, tm = [], []
    for off in offsets:
        try:
            res, _ = portfolio(mod, meta, mkt, main_cfg, offset=off)
        except Exception as e:  # noqa: BLE001
            rows.append(f"| offset {off}h | failed: {e} | | | | | |")
            continue
        s = metrics.summary(res)
        tm.append(s["MAR"])
        rows.append(fmt_row(f"bars start {off:02d}:00 UTC", s))
    rob["timing_mar_range"] = [float(np.nanmin(tm)), float(np.nanmax(tm))] if tm else None
    L += ["### 3b. Bar-timing shift (same rule, bars start at a different hour)", "", HDR, *rows, ""]

    # 2c cross-asset (single asset each, unchanged rule)
    rows, ca = [], {}
    for a in CROSS_ASSETS:
        try:
            res, _ = portfolio(mod, meta, mkt, main_cfg, assets=[a])
            s = metrics.summary(res)
            df, _, _ = mkt.get(a, tf)
            st = res.index[0]
            sb = metrics.summary(engine.static_mix(df, 1.0, engine.Config(fee=BENCH_FEE), st))
            ca[a] = {"strategy": s, "buy_hold": sb}
            rows.append(fmt_row(f"{a}{' (in-sample asset)' if a in meta['assets'] else ''} from {st.date()}", s))
            rows.append(fmt_row(f"↳ {a} buy & hold", sb))
        except Exception as e:  # noqa: BLE001
            rows.append(f"| {a} | failed: {e} | | | | | |")
    rob["cross_asset"] = ca
    L += ["### 3c. Cross-asset (unchanged rule, single asset)", "", HDR, *rows, ""]

    # 2d block bootstrap (close-only paths: no intrabar liquidation check)
    n_paths = 40 if quick else 200
    boot = {"strategy": [], "buy_hold": []}
    closes = {a: mkt.get(a, tf)[0]["close"] for a in meta["assets"]}
    gens = {a: block_bootstrap(closes[a], n_paths, 30, seed=11 + i) for i, a in enumerate(meta["assets"])}
    bcfg = replace(main_cfg, use_funding=False)
    for _ in range(n_paths):
        prices = {a: next(gens[a]) for a in meta["assets"]}
        res, _ = portfolio(mod, meta, mkt, bcfg, prices=prices)
        boot["strategy"].append(metrics.summary(res))
        bh_r = pd.concat([engine.static_mix(prices[a], 1.0, engine.Config(fee=BENCH_FEE), EVAL_START)["ret"]
                          for a in meta["assets"]], axis=1).fillna(0).mean(axis=1)
        boot["buy_hold"].append(metrics.summary(pd.DataFrame({"ret": bh_r, "expo": 1.0, "trade": 0.0})))
    q = lambda k, key, p: float(np.nanpercentile([x[key] for x in boot[k]], p))  # noqa: E731
    better_mar = float(np.mean([s["MAR"] > b["MAR"] for s, b in zip(boot["strategy"], boot["buy_hold"])]))
    better_cagr = float(np.mean([s["CAGR"] > b["CAGR"] for s, b in zip(boot["strategy"], boot["buy_hold"])]))
    rob["bootstrap"] = {"paths": n_paths, "cagr_p5": q("strategy", "CAGR", 5), "cagr_p50": q("strategy", "CAGR", 50),
                        "mdd_p50": q("strategy", "MaxDD", 50), "mdd_p5": q("strategy", "MaxDD", 5),
                        "p_better_mar_than_bh": better_mar, "p_better_cagr_than_bh": better_cagr}
    b = rob["bootstrap"]
    L += [f"### 3d. Block bootstrap ({n_paths} paths, 30-day blocks, close-only, no funding)", "",
          "| | Strategy | Buy & hold |", "|---|---|---|",
          f"| CAGR median | {b['cagr_p50']:+.1%} | {q('buy_hold', 'CAGR', 50):+.1%} |",
          f"| CAGR 5th pct | {b['cagr_p5']:+.1%} | {q('buy_hold', 'CAGR', 5):+.1%} |",
          f"| MaxDD median | {b['mdd_p50']:.1%} | {q('buy_hold', 'MaxDD', 50):.1%} |",
          f"| MaxDD worst 5 % | {b['mdd_p5']:.1%} | {q('buy_hold', 'MaxDD', 5):.1%} |",
          f"| P(MAR > buy & hold) | {better_mar:.0%} | |",
          f"| P(CAGR > buy & hold) | {better_cagr:.0%} | |", "",
          "_Block bootstrap shuffles 30-day chunks of history. It keeps short-term trends but breaks long ones, "
          "so it is a harsh test for slow trend rules; read it as a stress test, not a forecast._", ""]

    # 2e deflated Sharpe with the shared ledger
    sha = git_sha()
    phash = hashlib.sha1(json.dumps([name, meta["params"], meta["assets"], tf], sort_keys=True).encode()).hexdigest()[:10]
    row = {"time": out["generated"], "commit": sha, "strategy": name, "author": meta["author"],
           "variant": phash, "params": json.dumps(meta["params"]), "timeframe": tf, "assets": "+".join(meta["assets"]),
           "sharpe": round(full[MAIN]["Sharpe"], 4), "cagr": round(full[MAIN]["CAGR"], 4),
           "maxdd": round(full[MAIN]["MaxDD"], 4), "prior_trials": meta["prior_trials"]}
    rows_l = ledger_rows()
    if not any(r["variant"] == row["variant"] for r in rows_l):
        append_ledger(row)
        rows_l.append({k: str(v) for k, v in row.items()})
    rob["deflated_sharpe"] = {"p": None}          # filled in by finalize() once all strategies ran
    L += ["### 3e. Deflated Sharpe ratio", "", "{{DSR_TEXT}}", ""]

    # verdict checklist
    chk = [
        ("Beats equal-risk mix on CAGR (main costs)", full[MAIN]["CAGR"] > s_mix["CAGR"]),
        ("Positive in every sub-period", all(s and s["CAGR"] > 0 for p, s in out["periods"].items() if "FORWARD" not in p and s)),
        ("Parameter MAR range min > 50 % of base", bool(rob["param_mar_range"] and rob["param_mar_range"][0] > 0.5 * full[MAIN]["MAR"])),
        ("Timing MAR range min > 50 % of base", bool(rob["timing_mar_range"] and rob["timing_mar_range"][0] > 0.5 * full[MAIN]["MAR"])),
        ("Better MAR than buy & hold on most other assets",
         sum(v["strategy"]["MAR"] > v["buy_hold"]["MAR"] for a, v in ca.items() if a not in meta["assets"])
         > len([a for a in ca if a not in meta["assets"]]) / 2),
        ("No liquidation in any cost scenario", not any(s.get("Liquidated") for s in full.values())),
    ]
    out["checklist"] = {k: bool(v) for k, v in chk}
    L += ["## 4. Checklist", "", *[f"- {'✅' if v else '❌'} {k}" for k, v in chk], "{{DSR_CHECK}}", "",
          "_Research only, not investment advice._"]

    d = RESULTS / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "report_template.md").write_text("\n".join(L) + "\n")
    (d / "metrics.json").write_text(json.dumps({**out, "robustness": rob}, indent=2, default=str))
    eq = (1 + main_res["ret"]).cumprod()
    eq.resample("1D").last().dropna().to_frame("equity").to_csv(d / "equity.csv")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strategies", nargs="*")
    ap.add_argument("--quick", action="store_true", help="fewer bootstrap paths")
    a = ap.parse_args()
    names = a.strategies or all_strategies()
    for n in names:
        evaluate(n, a.quick)
    finalize(post_to_issues=names)
    write_leaderboard()


def finalize(post_to_issues=()):
    """Deflated Sharpe for every benched strategy on a common basis (daily returns, one shared trial
    count and SR dispersion from the whole ledger), then render report.md and post new reports."""
    rows = ledger_rows()
    variants = {r["variant"]: r for r in rows}
    prior = {}
    for n in all_strategies():
        try:
            prior[n] = int(load_strategy(n)[1].get("prior_trials", 0))
        except Exception:  # noqa: BLE001
            pass
    n_trials = len(variants) + sum(prior.values())
    srs = np.array([float(r["sharpe"]) for r in variants.values()])
    sr_var = float(np.var(srs)) if len(srs) >= 3 else SR_VAR_FALLBACK
    for n in all_strategies():
        d = RESULTS / n
        if not (d / "report_template.md").exists():
            continue
        eq = pd.read_csv(d / "equity.csv", index_col=0, parse_dates=True)["equity"]
        r = eq.pct_change().dropna()
        dsr = metrics.deflated_sharpe(r, n_trials, sr_var / 365)
        m = json.loads((d / "metrics.json").read_text())
        m["robustness"]["deflated_sharpe"] = {"p": dsr, "n_trials": n_trials, "sr_var_annual": sr_var}
        m["checklist"]["Deflated Sharpe ≥ 0.95"] = bool(dsr >= 0.95)
        (d / "metrics.json").write_text(json.dumps(m, indent=2, default=str))
        text = (f"Probability that the true Sharpe is above 0 after correcting for **{n_trials} trials** "
                f"({len(variants)} bench variants in LEDGER.csv + {sum(prior.values())} declared prior trials; "
                f"variance of annual Sharpe across trials {sr_var:.3f}; daily returns): **{dsr:.2f}** "
                f"(≥ 0.95 is the usual bar).")
        report = ((d / "report_template.md").read_text().replace("{{DSR_TEXT}}", text)
                  .replace("{{DSR_CHECK}}", f"- {'✅' if dsr >= 0.95 else '❌'} Deflated Sharpe ≥ 0.95"))
        (d / "report.md").write_text(report)
        if n in post_to_issues:
            print(report)
            issue = m["meta"].get("issue")
            if issue:
                try:
                    post_issue(issue, report)
                except Exception as e:  # noqa: BLE001
                    print(f"[bench] could not post to issue #{issue}: {e}")


def all_strategies():
    return sorted(p.stem for p in (ROOT / "strategies").glob("*.py") if not p.stem.startswith("_"))


def write_leaderboard():
    lines = ["# Leaderboard", "", f"_Updated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} · full period from "
             f"{EVAL_START}, {MAIN} per side. Sorted by MAR. Click a name for the full report._", "",
             "| Strategy | Author | CAGR | MaxDD | MAR | Sharpe | Equal-risk mix CAGR | Deflated Sharpe | Checklist |",
             "|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for n in all_strategies():
        p = RESULTS / n / "metrics.json"
        if not p.exists():
            continue
        o = json.loads(p.read_text())
        m, rob = o["costs"][MAIN], o["robustness"]
        rows.append((m["MAR"], f"| [{n}](results/{n}/report.md) | {o['meta']['author']} | {m['CAGR']:+.1%} | "
                               f"{m['MaxDD']:.1%} | {m['MAR']:.2f} | {m['Sharpe']:.2f} | "
                               f"{o['benchmarks']['equal_risk']['CAGR']:+.1%} | {rob['deflated_sharpe']['p']:.2f} | "
                               f"{sum(o['checklist'].values())}/{len(o['checklist'])} |"))
    lines += [r for _, r in sorted(rows, key=lambda x: -(x[0] if x[0] == x[0] else -9))]
    (ROOT / "LEADERBOARD.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
