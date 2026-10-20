# -*- coding: utf-8 -*-
"""v4 경제적 가치 분석(탐색). 규칙: v4_경제적가치_분석계획.md (sha256 764ff320…)."""
import glob, math, sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

RAW = Path("/mnt/user-data/uploads/논문/04_실험코드/results_v4_t5fix/raw")
OUT = Path(__file__).parent / "out"; OUT.mkdir(exist_ok=True)
US = {"AAPL", "AMZN", "GOOG", "JPM", "META"}
ALPHA, GAMMA, CLIP, WARM = 0.20, 0.05, (0.02, 0.50), 20
Z80 = 2 * stats.norm.ppf(0.9)            # 2.5631
TARGET = 0.01
NAME = {"chronos_t5_base": "Chronos-T5", "chronos2": "Chronos-2", "timesfm25": "TimesFM-2.5", "moirai2": "Moirai-2",
        "rw": "과거변동(RW)", "garch_t": "GARCH-t"}


def kr_tax(d):
    d = pd.Timestamp(d)
    if d < pd.Timestamp("2019-06-03"): return 0.0030
    if d.year <= 2020: return 0.0025
    if d.year <= 2022: return 0.0023
    return {2023: 0.0020, 2024: 0.0018, 2025: 0.0015}.get(d.year, 0.0020)


def aci_cont(lo, hi, y):
    n = len(y); cl = np.full(n, np.nan); ch = cl.copy(); a = ALPHA; h = []
    import bisect
    for t in range(n):
        w = max(hi[t] - lo[t], 1e-12)
        if t >= WARM:
            k = math.ceil((len(h) + 1) * (1 - a)); q = h[-1] if k > len(h) else h[k - 1]
            cl[t], ch[t] = lo[t] - q * w, hi[t] + q * w
            a = min(max(a + GAMMA * (ALPHA - (0.0 if cl[t] <= y[t] <= ch[t] else 1.0)), CLIP[0]), CLIP[1])
        bisect.insort(h, max(lo[t] - y[t], y[t] - hi[t]) / w)
    return cl, ch


def load():
    frames = []
    for f in sorted(RAW.glob("*__real.parquet")):
        m, cond, _ = f.stem.split("__"); L, k = cond[1:].split("_")
        d = pd.read_parquet(f, columns=["unit", "date", "y", "q1", "q5", "q9"])
        d = d.sort_values(["unit", "date"]).reset_index(drop=True)
        d["cal_lo"], d["cal_hi"] = np.nan, np.nan
        for u, idx in d.groupby("unit").indices.items():
            a, b = aci_cont(d.q1.values[idx], d.q9.values[idx], d.y.values[idx])
            d.loc[idx, "cal_lo"], d.loc[idx, "cal_hi"] = a, b
        d["pos"] = d.groupby("unit").cumcount()
        d = d[d.pos >= WARM].copy()
        d["model"], d["L"], d["input"] = m, int(L), k
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def costs(unit, dates, w, zero=False):
    """|Δw| 비례 비용. 첫날은 0에서 진입."""
    prev = np.r_[0.0, w[:-1]]; dw = w - prev
    if zero: return np.zeros_like(w)
    if unit in US: return np.abs(dw) * 0.0001
    tax = np.array([kr_tax(x) for x in dates])
    return np.abs(dw) * 0.00015 + np.maximum(-dw, 0) * tax


def strat_returns(g, wfun, zero=False):
    """종목별 전략 일수익률 DataFrame(date, unit, r, w)."""
    out = []
    for u, s in g.groupby("unit"):
        s = s.sort_values("date"); w = wfun(s)
        R = np.expm1(s.y.values)
        r = w * R - costs(u, s.date.values, w, zero)
        out.append(pd.DataFrame({"date": s.date.values, "unit": u, "r": r, "w": w}))
    return pd.concat(out)


def portfolio(sr):
    return sr.groupby("date")["r"].mean().sort_index()


def metrics(p, sr=None):
    r = p.values; n = len(r); eq = np.cumprod(1 + r)
    ann = eq[-1] ** (252 / n) - 1; vol = r.std(ddof=1) * np.sqrt(252); sh = r.mean() / r.std(ddof=1) * np.sqrt(252)
    mdd = (eq / np.maximum.accumulate(eq) - 1).min()
    d = {"연수익률%": ann * 100, "연변동성%": vol * 100, "샤프": sh, "최대낙폭%": mdd * 100, "누적배수": eq[-1]}
    if sr is not None:
        yrs = n / 252
        tw = sr.groupby("unit").apply(lambda s: np.abs(np.diff(np.r_[0, s.w.values])).sum()).mean() / yrs
        d.update({"평균비중": sr.w.mean(), "연회전율": tw})
    return d


def sharpe(r): return r.mean() / r.std(ddof=1) * np.sqrt(252)


def boot_sharpe_diff(pa, pb, B=2000, seed=7):
    j = pd.concat([pa, pb], axis=1, keys=["a", "b"]).dropna()
    mon = j.index.to_period("M"); months = mon.unique(); groups = [np.where(mon == m)[0] for m in months]
    rng = np.random.default_rng(seed); diffs = []
    for _ in range(B):
        idx = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        diffs.append(sharpe(j.a.values[idx]) - sharpe(j.b.values[idx]))
    return sharpe(j.a.values) - sharpe(j.b.values), *np.quantile(diffs, [0.025, 0.975])


def kupiec(x, n, p=0.1):
    if x == 0 or x == n: return np.nan
    ph = x / n
    lr = -2 * ((n - x) * np.log(1 - p) + x * np.log(p) - (n - x) * np.log(1 - ph) - x * np.log(ph))
    return float(stats.chi2.sf(lr, 1))


def christoffersen(v):
    v = v.astype(int); a, b = v[:-1], v[1:]
    n00 = ((a == 0) & (b == 0)).sum(); n01 = ((a == 0) & (b == 1)).sum(); n10 = ((a == 1) & (b == 0)).sum(); n11 = ((a == 1) & (b == 1)).sum()
    p01 = n01 / max(n00 + n01, 1); p11 = n11 / max(n10 + n11, 1); p = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
    def ll(x, q): return x * np.log(q) if x > 0 and q > 0 else 0.0
    l0 = ll(n00 + n10, 1 - p) + ll(n01 + n11, p)
    l1 = ll(n00, 1 - p01) + ll(n01, p01) + ll(n10, 1 - p11) + ll(n11, p11)
    return float(stats.chi2.sf(max(-2 * (l0 - l1), 0), 1))


def label(m, L, k): return f"{NAME[m]} {'한 달' if L == 21 else '1년'}·{'수익률' if k == 'return' else '가격'}"
