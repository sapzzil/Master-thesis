# -*- coding: utf-8 -*-
"""
07_analysis_v4.py — 사전등록 가설 검정·표 (계획서 v4 §7·§8)
==========================================================
입력: results_v4/scored_v4.parquet.  채점일(scored)만 사용.
검정 단위: 합성 = 계열 100개(같은 계열 번호끼리 대응, CRN) / 실제 = 달력 월(예측 대상일 기준)
판정:
  유의 = Holm 보정 p < 0.05 (Holm 묶음 = 가설·비교마다 TSFM 4 × 조건 4 = 16개)
  실질 = 커버리지 차이 2%p 이상 / 분위수 손실 RW 대비 2% 이상 개선
  분류: 지지(유의+방향 일치+실질) / 유의하나 작음 / 반대 방향 유의 / 미지지
  조건 규칙(TSFM별): 4조건 모두 지지 → 조건과 무관 / 일부 → 조건에 따라 다름 / 없음 → 미지지
출력: results_v4/tables/*.csv, results_v4/tables/v4_report.md, results_v4/run_manifest.json
"""
import argparse
import hashlib
import itertools
import json
import platform
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import config_v4 as C

RNG = np.random.default_rng(C.BOOT_SEED)
warnings.filterwarnings("ignore", category=UserWarning, module="scipy")
CONDS = [(L, k) for L in C.CONTEXTS for k in C.INPUTS]


# ------------------------------------------------------------------ 통계 도구
def boot_ratio(k, n, levels=(0.95,)):
    k, n = np.asarray(k, float), np.asarray(n, float)
    est = k.sum() / n.sum()
    idx = RNG.integers(0, len(k), size=(C.N_BOOT, len(k)))
    bs = k[idx].sum(1) / n[idx].sum(1)
    out = {"est": est}
    for lv in levels:
        a = (1 - lv) / 2
        out[f"lo{int(lv*100)}"], out[f"hi{int(lv*100)}"] = np.quantile(bs, [a, 1 - a])
    return out


def boot_mean(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    idx = RNG.integers(0, len(x), size=(C.N_BOOT, len(x)))
    lo, hi = np.quantile(x[idx].mean(1), [0.025, 0.975])
    return x.mean(), lo, hi


def wilcox(d):
    d = np.asarray(d, float)
    d = np.round(d[~np.isnan(d)], 10)
    if len(d) == 0 or np.all(d == 0):
        return np.nan
    return float(stats.wilcoxon(d, zero_method="pratt", alternative="two-sided").pvalue)


def holm(p):
    p = np.asarray(p, float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    order = np.argsort(pv)
    m, run, adj = len(pv), 0.0, np.empty(len(pv))
    for r, i in enumerate(order):
        run = max(run, (m - r) * pv[i])
        adj[i] = min(run, 1.0)
    out[ok] = adj
    return out


def classify_cov(mean, p_holm):
    if np.isnan(p_holm) or p_holm >= C.ALPHA_TEST:
        return "미지지"
    if mean < 0:
        return "지지" if mean <= -C.SUBST_COV else "유의하나 작음"
    return "반대 방향 유의"


def classify_ql(impr, p_holm):
    if np.isnan(p_holm) or p_holm >= C.ALPHA_TEST:
        return "차이 없음"
    if impr > 0:
        return "지지" if impr >= C.SUBST_QL else "유의하나 작음"
    return "반대(RW 우위)"


def condition_rule(t, hyp_cols, label_col="판정"):
    rows = []
    for keys, g in t[t["model"].isin(C.TSFM)].groupby(hyp_cols + ["model"]):
        ok = g[g[label_col] == "지지"]
        n = len(ok)
        if n == len(g):
            lab = "조건과 무관(4조건 모두 지지)"
        elif n > 0:
            lab = "조건에 따라 다름: " + ", ".join(f"L{r.L}·{r.input}" for r in ok.itertuples())
        else:
            lab = "미지지"
        rows.append(dict(zip(hyp_cols + ["model"], keys if isinstance(keys, tuple) else (keys,)), 조건규칙=lab))
    return pd.DataFrame(rows)


def fmt(e, lo, hi, pct=True):
    return f"{e*100:.1f} [{lo*100:.1f}, {hi*100:.1f}]" if pct else f"{e:.4f} [{lo:.4f}, {hi:.4f}]"


def md(df, **kw):
    return df.to_markdown(index=False, **kw) + "\n"


# ------------------------------------------------------------------ 합성
def series_table(sy):
    s = sy[sy["scored"]]
    return s.groupby(["model", "L", "input", "scenario", "unit"]).agg(
        cov=("cover", "mean"), cal=("cal_cover", "mean"), ctl=("ctl_cover", "mean"), n=("cover", "size"),
        k=("cover", "sum"), kc=("cal_cover", "sum"), kt=("ctl_cover", "sum"), ql=("ql", "mean"),
        width=("width", "mean"), cal_w=("cal_w", "mean")).reset_index()


def synthetic(df, rep, out):
    sy = df[df["dataset"] == "synth"].copy()
    sy["cal_w"] = sy["cal_hi"] - sy["cal_lo"]
    ser = series_table(sy)
    meta = pd.DataFrame(C.scenarios(), columns=["scenario", "axis", "level", "par"])[["scenario", "axis", "level"]]
    ser = ser.merge(meta, on="scenario")

    # T1 시나리오별 커버리지(원래·보정·대조), 정답 기준선 포함
    rows = []
    for (m, L, k, sc), g in ser.groupby(["model", "L", "input", "scenario"]):
        a, b, c = boot_ratio(g["k"], g["n"]), boot_ratio(g["kc"], g["n"], (0.90, 0.95)), boot_ratio(g["kt"], g["n"])
        rows.append({"model": m, "L": L, "input": k, "scenario": sc, "n_series": len(g),
                     "cov": a["est"], "cov_lo": a["lo95"], "cov_hi": a["hi95"],
                     "cal": b["est"], "cal_lo90": b["lo90"], "cal_hi90": b["hi90"],
                     "ctl": c["est"], "ctl_lo": c["lo95"], "ctl_hi": c["hi95"],
                     "ql": g["ql"].mean(), "width": g["width"].mean(), "cal_width": g["cal_w"].mean()})
    t1 = pd.DataFrame(rows)
    t1.to_csv(out / "T1_synth_scenarios.csv", index=False, encoding="utf-8-sig")
    rep.append("## T1. 합성 시나리오별 80% 커버리지(%) — 원래 [95% CI]\n")
    show = t1.assign(cond=lambda d: d["model"] + " L" + d["L"].astype(str) + " " + d["input"],
                     cell=[fmt(r.cov, r.cov_lo, r.cov_hi) for r in t1.itertuples()])
    rep.append(md(show.pivot(index="scenario", columns="cond", values="cell").T.reset_index()))

    # T2 H1~H3b: 같은 계열의 L5−L1, L5−L3 커버리지 차이
    rows = []
    for ax in C.AXES:
        for comp, base in [("L5-L1", None), ("L5-L3", 3)]:
            for (m, L, k), g in ser.groupby(["model", "L", "input"]):
                if m == "oracle":
                    continue
                g5 = g[(g["axis"] == ax) & (g["level"] == 5)].set_index("unit")["cov"]
                gb = g[g["scenario"] == "L1"] if base is None else g[(g["axis"] == ax) & (g["level"] == base)]
                gb = gb.set_index("unit")["cov"]
                d = (g5 - gb).dropna().values
                e, lo, hi = boot_mean(d)
                rows.append({"hyp": C.AXIS_HYP[ax], "axis": ax, "comparison": comp, "model": m, "L": L, "input": k,
                             "dcov": e, "lo": lo, "hi": hi, "p": wilcox(d), "n": len(d)})
    t2 = pd.DataFrame(rows)
    t2["p_holm"] = np.nan
    for _, idx in t2[t2["model"].isin(C.TSFM)].groupby(["axis", "comparison"]).groups.items():
        t2.loc[idx, "p_holm"] = holm(t2.loc[idx, "p"].values)
    t2["판정"] = [classify_cov(r.dcov, r.p_holm) if r.model in C.TSFM else "(기준모형·서술)" for r in t2.itertuples()]
    t2.to_csv(out / "T2_H1_H3_levels.csv", index=False, encoding="utf-8-sig")
    rep.append("## T2. H1·H2·H3a·H3b — 같은 계열의 커버리지 차이(%p) [95% CI], 가설 방향 = 음수\n")
    rep.append(md(t2.assign(diff=[fmt(r.dcov, r.lo, r.hi) for r in t2.itertuples()])
                  [["hyp", "comparison", "model", "L", "input", "diff", "p", "p_holm", "판정"]], floatfmt=".4f"))
    cr = condition_rule(t2, ["hyp", "comparison"])
    cr.to_csv(out / "T2b_condition_rule.csv", index=False, encoding="utf-8-sig")
    rep.append("### T2b. 조건 규칙\n" + md(cr))

    # T3 H4: 고강도(L4·L5 평균) 결손의 축 간 차이
    hi = ser[ser["level"].isin([4, 5])].groupby(["model", "L", "input", "axis", "unit"])["cov"].mean().reset_index()
    hi["deficit"] = C.NOMINAL - hi["cov"]
    rows, pair_rows = [], []
    for (m, L, k), g in hi.groupby(["model", "L", "input"]):
        if m == "oracle":
            continue
        w = g.pivot(index="unit", columns="axis", values="deficit")[C.AXES].dropna()
        fr = stats.friedmanchisquare(*[w[a].values for a in C.AXES])
        means = w.mean()
        rows.append({"model": m, "L": L, "input": k, **{f"deficit_{a}": means[a] for a in C.AXES},
                     "range": means.max() - means.min(), "p_friedman": float(fr.pvalue), "n": len(w)})
        for a, b in itertools.combinations(C.AXES, 2):
            d = (w[a] - w[b]).values
            e, lo, hi_ = boot_mean(d)
            pair_rows.append({"model": m, "L": L, "input": k, "pair": f"{a}-{b}", "diff": e, "lo": lo, "hi": hi_,
                              "p": wilcox(d)})
    t3 = pd.DataFrame(rows)
    msk = t3["model"].isin(C.TSFM)
    t3["p_holm"] = np.nan
    t3.loc[msk, "p_holm"] = holm(t3.loc[msk, "p_friedman"].values)
    t3["판정"] = ["축마다 다름" if (r.model in C.TSFM and r.p_holm < C.ALPHA_TEST and r.range >= C.SUBST_COV)
                 else ("유의하나 작음" if r.model in C.TSFM and r.p_holm < C.ALPHA_TEST else
                       ("미지지" if r.model in C.TSFM else "(기준모형·서술)")) for r in t3.itertuples()]
    t3p = pd.DataFrame(pair_rows)
    t3p["p_holm"] = np.nan
    for _, idx in t3p[t3p["model"].isin(C.TSFM)].groupby("pair").groups.items():
        t3p.loc[idx, "p_holm"] = holm(t3p.loc[idx, "p"].values)
    t3.to_csv(out / "T3_H4_friedman.csv", index=False, encoding="utf-8-sig")
    t3p.to_csv(out / "T3b_H4_pairs.csv", index=False, encoding="utf-8-sig")
    rep.append("## T3. H4 — 고강도(L4·L5) 커버리지 결손(80% − 커버리지)의 축 간 차이\n")
    rep.append(md(t3, floatfmt=".4f"))
    rep.append("### T3b. 축 쌍별 결손 차이(%p) [95% CI]\n")
    rep.append(md(t3p.assign(d=[fmt(r.diff, r.lo, r.hi) for r in t3p.itertuples()])
                  [["model", "L", "input", "pair", "d", "p", "p_holm"]], floatfmt=".4f"))

    # T4 H5(합성): 보정 후 커버리지 90% CI ⊂ [0.77, 0.83]
    t4 = t1.copy()
    t4["restored"] = (t4["cal_lo90"] >= C.H5_BAND[0]) & (t4["cal_hi90"] <= C.H5_BAND[1])
    t4.to_csv(out / "T4_H5_synth.csv", index=False, encoding="utf-8-sig")
    summ = t4[t4["model"] != "oracle"].groupby(["model", "L", "input"]).agg(
        복원=("restored", "sum"), 시나리오=("restored", "size"), 보정커버리지_최소=("cal", "min"),
        보정커버리지_최대=("cal", "max"), 대조_최소=("ctl", "min"), 대조_최대=("ctl", "max")).reset_index()
    rep.append("## T4. H5(합성) — 보정 후 커버리지 90% CI가 [77%, 83%] 안인 시나리오 수 (17개 중)\n")
    rep.append(md(summ, floatfmt=".3f"))

    # T5 H6(합성, 서술용): 계열별 분위수 손실 차이 TSFM − RW(같은 L)
    rows = []
    ql = ser.pivot_table(index=["scenario", "unit"], columns=["model", "L", "input"], values="ql")
    for m in C.TSFM:
        for L, k in CONDS:
            if (m, L, k) not in ql.columns or ("rw", L, "return") not in ql.columns:
                continue
            for sc in ql.index.get_level_values(0).unique():
                a, b = ql.loc[sc, (m, L, k)], ql.loc[sc, ("rw", L, "return")]
                rows.append({"model": m, "L": L, "input": k, "scenario": sc, "impr_vs_rw": 1 - a.sum() / b.sum(),
                             "p": wilcox((a - b).values)})
    t5 = pd.DataFrame(rows)
    t5.to_csv(out / "T5_H6_synth_descriptive.csv", index=False, encoding="utf-8-sig")
    rep.append("## T5. H6(합성, 서술용) — RW 대비 분위수 손실 개선율(%), 계열 단위 Wilcoxon\n")
    if len(t5):
        rep.append(md(t5.pivot_table(index=["model", "L", "input"], columns="scenario", values="impr_vs_rw")
                      .mul(100).round(1).reset_index()))
    return t2, t3, t4


# ------------------------------------------------------------------ 실제 주식
def real(df, rep, out):
    rl = df[(df["dataset"] == "real")].copy()
    rl["month"] = pd.to_datetime(rl["date"]).dt.to_period("M").astype(str)
    s = rl[rl["scored"]]

    # T6 커버리지(원래·보정·대조·연속보정), 월 클러스터 CI
    rows = []
    for (m, L, k), g in s.groupby(["model", "L", "input"]):
        for panel, gg in [("ALL", g), ("US", g[g["scenario"] == "US"]), ("KR", g[g["scenario"] == "KR"])]:
            mo = gg.groupby("month").agg(k=("cover", "sum"), kc=("cal_cover", "sum"), kt=("ctl_cover", "sum"),
                                         n=("cover", "size"))
            a, b, c = boot_ratio(mo["k"], mo["n"]), boot_ratio(mo["kc"], mo["n"], (0.90, 0.95)), boot_ratio(mo["kt"], mo["n"])
            rows.append({"model": m, "L": L, "input": k, "panel": panel, "n": len(gg), "months": len(mo),
                         "cov": a["est"], "cov_lo": a["lo95"], "cov_hi": a["hi95"],
                         "cal": b["est"], "cal_lo90": b["lo90"], "cal_hi90": b["hi90"],
                         "ctl": c["est"], "ql": gg["ql"].mean(), "width": gg["width"].mean()})
    t6 = pd.DataFrame(rows)
    t6["restored"] = (t6["cal_lo90"] >= C.H5_BAND[0]) & (t6["cal_hi90"] <= C.H5_BAND[1])
    t6.to_csv(out / "T6_real_coverage_H5.csv", index=False, encoding="utf-8-sig")
    rep.append("## T6. 실제 주식 커버리지(%) [월 클러스터 CI] — 원래 95% CI, 보정 90% CI(H5), 대조\n")
    rep.append(md(t6.assign(원래=[fmt(r.cov, r.cov_lo, r.cov_hi) for r in t6.itertuples()],
                            보정=[fmt(r.cal, r.cal_lo90, r.cal_hi90) for r in t6.itertuples()])
                  [["model", "L", "input", "panel", "n", "원래", "보정", "restored", "ctl"]], floatfmt=".3f"))

    # 보조: 연속 보정, 종목별
    cs = rl[rl["cont_scored"]]
    aux = cs.groupby(["model", "L", "input"]).agg(cont_cov=("cont_cover", "mean"), n=("cont_cover", "size")).reset_index()
    aux.to_csv(out / "T6b_real_continuous_aux.csv", index=False, encoding="utf-8-sig")
    per = s.groupby(["model", "L", "input", "unit"])["cover"].mean().unstack("unit")
    per.to_csv(out / "T6c_real_coverage_by_stock.csv", encoding="utf-8-sig")
    rep.append("### T6b. 보조: 끊지 않는 연속 보정 커버리지\n" + md(aux, floatfmt=".3f"))

    # T7 H6: TSFM vs RW(같은 L) 분위수 손실, 월 블록 t검정
    key = ["unit", "date"]
    rows = []
    for m in C.TSFM:
        for L, k in CONDS:
            a = s[(s["model"] == m) & (s["L"] == L) & (s["input"] == k)].set_index(key)
            b = s[(s["model"] == "rw") & (s["L"] == L)].set_index(key)
            if a.empty or b.empty:
                continue
            j = a[["ql", "month"]].join(b[["ql"]], rsuffix="_rw", how="inner").dropna()
            D = (j["ql"] - j["ql_rw"]).groupby(j["month"]).mean()
            p = float(stats.ttest_1samp(D.values, 0.0).pvalue) if len(D) > 1 else np.nan
            e, lo, hi = boot_mean(D.values)
            rows.append({"model": m, "L": L, "input": k, "n": len(j), "months": len(D),
                         "impr_vs_rw": 1 - j["ql"].sum() / j["ql_rw"].sum(), "mean_month_diff": e,
                         "diff_lo": lo, "diff_hi": hi, "p": p})
    t7 = pd.DataFrame(rows)
    if len(t7):
        t7["p_holm"] = holm(t7["p"].values)
        t7["판정"] = [classify_ql(r.impr_vs_rw, r.p_holm) for r in t7.itertuples()]
        cr = condition_rule(t7.assign(hyp="H6"), ["hyp"])
    else:
        cr = pd.DataFrame()
    t7.to_csv(out / "T7_H6_real.csv", index=False, encoding="utf-8-sig")
    rep.append("## T7. H6 — 실제 주식 RW 대비 분위수 손실 개선율, 월 블록 t검정(양측), Holm 16\n")
    rep.append(md(t7, floatfmt=".4f") + "### T7b. 조건 규칙\n" + md(cr))

    # T8 보조: 모델 공개 이후 구간만 (학습 데이터 누출 점검)
    rows = []
    for m, d0 in C.RELEASE_AFTER.items():
        for L, k in CONDS:
            a = s[(s["model"] == m) & (s["L"] == L) & (s["input"] == k) & (pd.to_datetime(s["date"]) >= d0)]
            b = s[(s["model"] == "rw") & (s["L"] == L) & (pd.to_datetime(s["date"]) >= d0)]
            if a.empty:
                continue
            j = a.set_index(key)[["ql", "cover"]].join(b.set_index(key)[["ql"]], rsuffix="_rw", how="inner")
            rows.append({"model": m, "after": d0, "L": L, "input": k, "n": len(j), "cov": j["cover"].mean(),
                         "impr_vs_rw": 1 - j["ql"].sum() / j["ql_rw"].sum()})
    t8 = pd.DataFrame(rows)
    t8.to_csv(out / "T8_real_post_release.csv", index=False, encoding="utf-8-sig")
    rep.append("## T8. 보조 — 모델 공개 이후 구간만 (서술용)\n" + md(t8, floatfmt=".4f"))
    return t6, t7


# ------------------------------------------------------------------ 무결성
def integrity(df, rep, out, smoke):
    g = df.groupby(["model", "L", "input", "dataset"]).agg(
        n=("y", "size"), scored=("scored", "sum"), crossed=("crossed", "mean"), nonfinite=("nonfinite", "sum"),
        fallback=("fallback", "sum")).reset_index()
    g.to_csv(out / "T0_integrity.csv", index=False, encoding="utf-8-sig")
    rep.append("## T0. 무결성 — 예측 수, 채점 수, 분위수 교차 비율, 유한값 아님, GARCH 대체\n")
    rep.append(md(g, floatfmt=".4f"))
    exp_syn = (3 if smoke else C.N_SERIES) * len(C.scenarios()) * C.EP_LEN
    bad = g[(g["dataset"] == "synth") & (g["n"] != exp_syn)]
    if len(bad):
        raise AssertionError(f"합성 예측 수가 기대값({exp_syn})과 다름:\n{bad}")
    real_n = g[g["dataset"] == "real"]["n"]
    if real_n.nunique() > 1:
        raise AssertionError(f"실제 주식 예측 수가 모델·조건마다 다름:\n{g[g['dataset']=='real']}")


def manifest(rd):
    files = sorted(Path(__file__).parent.glob("*.py")) + sorted(Path(__file__).parent.glob("*.json"))
    man = {"python": platform.python_version(),
           "code_sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
           "inputs_sha256": C.EXPECTED_SHA256}
    try:
        man["git_head"] = __import__("subprocess").run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                                                       cwd=C.ROOT).stdout.strip()
    except Exception:  # noqa: BLE001
        man["git_head"] = None
    log = rd / "run_log.jsonl"
    if log.exists():
        man["run_log"] = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()]
    (rd / "run_manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def main(smoke):
    rd = C.res_dir(smoke)
    out = rd / "tables"
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(rd / "scored_v4.parquet")
    rep = ["# v4 사전등록 분석 결과" + (" (스모크 — 해석 금지)" if smoke else "") + "\n"]
    integrity(df, rep, out, smoke)
    synthetic(df, rep, out)
    real(df, rep, out)
    (out / "v4_report.md").write_text("\n".join(rep), encoding="utf-8")
    manifest(rd)
    print(f"[저장] {out / 'v4_report.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    main(ap.parse_args().smoke)
