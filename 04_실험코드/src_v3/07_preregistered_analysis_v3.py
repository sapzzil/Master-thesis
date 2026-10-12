# -*- coding: utf-8 -*-
"""
07_preregistered_analysis_v3.py — 사전등록 분석 (v3)
====================================================
원칙: 검정 단위는 '독립 클러스터'다. 스텝을 독립 관측으로 쓰지 않는다.
  합성   : 클러스터 = 시계열 번호 s (CRN이라 축·레벨·모델 간 같은 s끼리 대응)
  시장패널: 클러스터 = 예측 시작일 k (같은 날짜를 공유하는 자산들을 하나로 묶음)
  시장스트림: 클러스터 = (자산, 윈도우) — 30개, 연속 구간이라 서로 독립 아님(서술용)
모든 p값은 양측. 가설 '지지'는 Holm 보정 p<0.05 이고 효과 방향이 가설과 일치할 때만.
출력: results_v3/tables/*.csv, results_v3/tables/v3_report.md, results_v3/run_manifest.json
"""
import argparse
import hashlib
import itertools
import json
import subprocess
import numpy as np
import pandas as pd
from scipy import stats

import config_v3 as C

RNG = np.random.default_rng(C.BOOT_SEED)


# ------------------------------------------------------------------ 통계 도구
def boot_ratio(num, den, B=C.N_BOOT, levels=(0.95,)):
    """클러스터별 합(num)과 개수(den)로 비율 추정량의 클러스터 부트스트랩 CI."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    est = num.sum() / den.sum()
    idx = RNG.integers(0, len(num), size=(B, len(num)))
    bs = num[idx].sum(1) / den[idx].sum(1)
    out = {"est": est}
    for lv in levels:
        a = (1 - lv) / 2
        out[f"lo{int(lv*100)}"], out[f"hi{int(lv*100)}"] = np.quantile(bs, [a, 1 - a])
    return out


def boot_mean(x, B=C.N_BOOT):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    idx = RNG.integers(0, len(x), size=(B, len(x)))
    bs = x[idx].mean(1)
    return x.mean(), *np.quantile(bs, [0.025, 0.975])


def wilcox(d):
    d = np.asarray(d, float)
    d = d[~np.isnan(d)]
    if np.allclose(d, 0):
        return np.nan
    return float(stats.wilcoxon(d, zero_method="pratt", alternative="two-sided").pvalue)


def holm(p):
    p = np.asarray(p, float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    order = np.argsort(pv)
    m = len(pv)
    adj = np.empty(m)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, (m - r) * pv[i])
        adj[i] = min(run, 1.0)
    out[ok] = adj
    return out


def spearman_exact(x, y):
    x, y = np.asarray(x), np.asarray(y)
    rho = stats.spearmanr(x, y)[0]
    perms = [stats.spearmanr(x, np.array(p))[0] for p in itertools.permutations(y)]
    p = np.mean(np.abs(perms) >= abs(rho) - 1e-12)
    return float(rho), float(p)


def block_t(D):
    """날짜 블록 평균 차이 D_k 에 대한 양측 t검정 + Newey-West(lag 1) 버전."""
    D = np.asarray(D, float)
    K = len(D)
    m = D.mean()
    p_t = float(stats.ttest_1samp(D, 0.0).pvalue)
    u = D - m
    g0 = (u ** 2).mean()
    g1 = (u[1:] * u[:-1]).mean() if K > 1 else 0.0
    lrv = max(g0 + 2 * 0.5 * g1, 1e-18)
    t_nw = m / np.sqrt(lrv / K)
    p_nw = float(2 * stats.t.sf(abs(t_nw), df=K - 1))
    return m, p_t, p_nw


def fmt_ci(e, lo, hi, pct=True, d=1):
    if pct:
        return f"{e*100:.{d}f} [{lo*100:.{d}f}, {hi*100:.{d}f}]"
    return f"{e:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]"


# ------------------------------------------------------------------ 합성
def synthetic(ml, rep):
    sy = ml[ml["scenario"].str.startswith("synth_")].copy()
    sy["lv"] = sy["level"].str[1:].astype(int)
    ser = sy.groupby(["model", "axis", "lv", "s_idx"]).agg(
        cov=("cov90", "mean"), ncrps=("rel_crps", "mean"), n=("cov90", "size"), k=("cov90", "sum")).reset_index()
    models = [m for m in C.MODELS if m in ser["model"].unique()]
    tsfm = [m for m in C.TSFM if m in models]

    # 표 1: 시나리오별 커버리지·nCRPS (95% 클러스터 CI)
    rows = []
    for (m, ax, lv), g in ser.groupby(["model", "axis", "lv"]):
        c = boot_ratio(g["k"], g["n"])
        e, lo, hi = boot_mean(g["ncrps"])
        rows.append({"model": m, "axis": ax, "level": f"L{lv}", "n_series": len(g),
                     "cov90": c["est"], "cov90_lo": c["lo95"], "cov90_hi": c["hi95"],
                     "ncrps": e, "ncrps_lo": lo, "ncrps_hi": hi})
    t1 = pd.DataFrame(rows)
    t1.to_csv(C.TABLES / "T1_synth_scenarios.csv", index=False)
    piv = t1.assign(cell=[fmt_ci(r.cov90, r.cov90_lo, r.cov90_hi) for r in t1.itertuples()]) \
        .pivot(index=["axis", "level"], columns="model", values="cell")[models]
    rep.append("## T1. 합성 시나리오별 90% 커버리지(%) [95% 클러스터 부트스트랩 CI]\n")
    rep.append(piv.to_markdown() + "\n")

    # H1~H3: 레벨 효과 (같은 s의 L5 - L1 대응 차이)
    hyp = {"GARCH": "H1", "TAIL": "H2", "REGIME": "H3"}
    rows = []
    for ax, h in hyp.items():
        for m in models:
            g = ser[(ser["model"] == m) & (ser["axis"] == ax)]
            w = g.pivot(index="s_idx", columns="lv", values="cov")
            wc = g.pivot(index="s_idx", columns="lv", values="ncrps")
            d = (w[5] - w[1]).values
            dc = (wc[5] - wc[1]).values
            e, lo, hi = boot_mean(d)
            ec, loc, hic = boot_mean(dc)
            rho_s = [stats.spearmanr([1, 2, 3, 4, 5], w.loc[s, [1, 2, 3, 4, 5]].values)[0]
                     if w.loc[s].std() > 0 else np.nan for s in w.index]
            lvl_mean = g.groupby("lv")["cov"].mean()
            r5, p5 = spearman_exact(lvl_mean.index.values, lvl_mean.values)
            rows.append({"hyp": h, "axis": ax, "model": m,
                         "dcov_L5_L1": e, "dcov_lo": lo, "dcov_hi": hi, "p_wilcoxon": wilcox(d),
                         "dncrps_L5_L1": ec, "dncrps_lo": loc, "dncrps_hi": hic, "p_wilcoxon_ncrps": wilcox(dc),
                         "mean_series_rho": np.nanmean(rho_s), "n_rho_undefined": int(np.isnan(rho_s).sum()),
                         "p_series_rho": wilcox(rho_s),
                         "levelmean_rho_n5": r5, "levelmean_p_exact": p5})
    t2 = pd.DataFrame(rows)
    t2["p_holm"] = np.nan
    for ax in hyp:
        msk = (t2["axis"] == ax) & t2["model"].isin(tsfm)
        t2.loc[msk, "p_holm"] = holm(t2.loc[msk, "p_wilcoxon"].values)
    t2["supported"] = (t2["p_holm"] < C.ALPHA_TEST) & (t2["dcov_L5_L1"] < 0)
    t2.to_csv(C.TABLES / "T2_H1_H3_level_effects.csv", index=False)
    rep.append("## T2. H1~H3 레벨 효과: 같은 시계열의 L5−L1 커버리지 차이(%p) [95% CI]\n")
    rep.append("가설 방향 = 커버리지 하락(음수). Holm 보정은 축별 TSFM 4개 안에서.\n")
    show = t2.assign(dcov=[fmt_ci(r.dcov_L5_L1, r.dcov_lo, r.dcov_hi) for r in t2.itertuples()])
    rep.append(show[["hyp", "model", "dcov", "p_wilcoxon", "p_holm", "supported",
                     "mean_series_rho", "levelmean_rho_n5", "levelmean_p_exact"]].to_markdown(index=False, floatfmt=".4f") + "\n")

    # H4: 고강도(L4,L5) 축 간 결손 비교 (같은 s 대응)
    hi = ser[ser["lv"].isin([4, 5])].groupby(["model", "axis", "s_idx"])["cov"].mean().reset_index()
    hi["deficit"] = 0.90 - hi["cov"]
    rows = []
    for m in models:
        w = hi[hi["model"] == m].pivot(index="s_idx", columns="axis", values="deficit")
        for other in ["TAIL", "GARCH"]:
            d = (w["REGIME"] - w[other]).values
            e, lo, hi_ = boot_mean(d)
            rows.append({"model": m, "comparison": f"REGIME-{other}", "mean_diff": e, "lo": lo, "hi": hi_,
                         "p_wilcoxon": wilcox(d), "n": len(d)})
    t3 = pd.DataFrame(rows)
    msk = t3["model"].isin(tsfm)
    t3["p_holm"] = np.nan
    t3.loc[msk, "p_holm"] = holm(t3.loc[msk, "p_wilcoxon"].values)
    t3["sig_positive"] = (t3["p_holm"] < C.ALPHA_TEST) & (t3["mean_diff"] > 0)
    t3.to_csv(C.TABLES / "T3_H4_axis_comparison.csv", index=False)
    h4 = t3[msk].groupby("model")["sig_positive"].all()
    rep.append("## T3. H4 고강도(L4~L5) 결손 차이(%p): REGIME − 비교축 [95% CI], 같은 시계열 대응\n")
    rep.append("Holm 보정: TSFM 4개 x 비교 2개 = 8개 검정. H4 지지 = 두 비교 모두 유의하게 양수.\n")
    show = t3.assign(diff=[fmt_ci(r.mean_diff, r.lo, r.hi) for r in t3.itertuples()])
    rep.append(show[["model", "comparison", "diff", "p_wilcoxon", "p_holm", "sig_positive"]].to_markdown(index=False, floatfmt=".4f") + "\n")
    rep.append("H4 지지 모델: " + (", ".join(h4[h4].index) or "없음") + "\n")

    # 아키텍처 비교 (같은 s, 같은 데이터)
    rows = []
    for a, b in [("chronos-tiny", "moirai-small"), ("chronos-base", "moirai-base")]:
        if a not in models or b not in models:
            continue
        for ax in ["REGIME", "TAIL", "GARCH"]:
            x = hi[(hi["model"] == a) & (hi["axis"] == ax)].set_index("s_idx")["cov"]
            y = hi[(hi["model"] == b) & (hi["axis"] == ax)].set_index("s_idx")["cov"]
            d = (y - x).values
            e, lo, hi_ = boot_mean(d)
            rows.append({"pair": f"{b} - {a}", "axis": ax, "dcov_L4L5": e, "lo": lo, "hi": hi_, "p_wilcoxon": wilcox(d)})
    if rows:
        t4 = pd.DataFrame(rows)
        t4["p_holm"] = holm(t4["p_wilcoxon"].values)
        t4.to_csv(C.TABLES / "T4_architecture_pairs.csv", index=False)
        rep.append("## T4. 아키텍처 비교: Moirai − Chronos 고강도(L4~L5) 커버리지 차이(%p) [95% CI]\n")
        show = t4.assign(diff=[fmt_ci(r.dcov_L4L5, r.lo, r.hi) for r in t4.itertuples()])
        rep.append(show[["pair", "axis", "diff", "p_wilcoxon", "p_holm"]].to_markdown(index=False, floatfmt=".4f") + "\n")


# ------------------------------------------------------------------ 실측 시장 (H6)
def market(ml, rep):
    mp = ml[ml["scenario"] == "market_panel"].copy()
    if mp.empty:
        return
    win = mp.groupby(["model", "ticker", "k", "origin"]).agg(
        ncrps=("rel_crps", "mean"), k_cov=("cov90", "sum"), n=("cov90", "size")).reset_index()
    models = [m for m in C.MODELS if m in win["model"].unique()]
    panels = {"US5": C.US_TICKERS, "KR": C.KR_TICKERS, "ALL6": C.US_TICKERS + C.KR_TICKERS}
    rows = []

    def panel_stats(sub, label, period):
        rw = sub[sub["model"] == "random_walk"].set_index(["ticker", "k"])["ncrps"]
        out = []
        for m in models:
            g = sub[sub["model"] == m]
            date_cov = g.groupby("k")[["k_cov", "n"]].sum()
            cov = boot_ratio(date_cov["k_cov"], date_cov["n"])
            mean_nc = g.groupby("k")["ncrps"].mean().mean()          # 날짜별 자산 동일가중 후 평균
            rw_nc = sub[sub["model"] == "random_walk"].groupby("k")["ncrps"].mean().mean()
            r = {"panel": label, "period": period, "model": m, "n_dates": g["k"].nunique(),
                 "n_windows": len(g), "ncrps": mean_nc, "skill_vs_rw": 1 - mean_nc / rw_nc,
                 "cov90": cov["est"], "cov_lo": cov["lo95"], "cov_hi": cov["hi95"]}
            if m != "random_walk":
                d = g.set_index(["ticker", "k"])["ncrps"] - rw
                D = d.groupby(level="k").mean().values
                md, p_t, p_nw = block_t(D)
                r.update({"mean_diff_vs_rw": md, "p_block_t": p_t, "p_block_nw": p_nw})
            out.append(r)
        return out

    for label, tick in panels.items():
        sub = win[win["ticker"].isin(tick)]
        rows += panel_stats(sub, label, "all")
        org = pd.to_datetime(sub["origin"])
        rows += panel_stats(sub[org < C.LEAKAGE_SPLIT_DATE], label, "pre_2024-03")
        rows += panel_stats(sub[org >= C.LEAKAGE_SPLIT_DATE], label, "post_2024-03")
    t5 = pd.DataFrame(rows)
    t5["p_holm"] = np.nan
    for (pn, pr), g in t5.groupby(["panel", "period"]):
        msk = (t5["panel"] == pn) & (t5["period"] == pr) & (t5["model"] != "random_walk")
        t5.loc[msk, "p_holm"] = holm(t5.loc[msk, "p_block_t"].values)
    t5["better_than_rw"] = (t5["p_holm"] < C.ALPHA_TEST) & (t5["mean_diff_vs_rw"] < 0)
    t5.to_csv(C.TABLES / "T5_market_panel.csv", index=False)
    rep.append("## T5. 실측 시장 패널(2017~2026, 60거래일 간격) — nCRPS, RW 대비, 커버리지 [날짜 클러스터 95% CI]\n")
    rep.append("검정: 날짜 블록 평균 차이 D_k의 양측 t검정(주), NW lag1(보조). Holm은 패널·기간별 모델 5개.\n"
               "H6 주판정 = period 'all'. pre/post 2024-03 분리는 보조(누출 점검).\n")
    show = t5.assign(cov=[fmt_ci(r.cov90, r.cov_lo, r.cov_hi) for r in t5.itertuples()],
                     skill=[f"{r.skill_vs_rw*100:+.2f}%" for r in t5.itertuples()])
    rep.append(show[["panel", "period", "model", "n_dates", "ncrps", "skill", "cov", "p_block_t", "p_block_nw",
                     "p_holm", "better_than_rw"]].to_markdown(index=False, floatfmt=".4f") + "\n")

    # 종목별(탐색적, 보정 없음)
    rows = []
    for t in C.US_TICKERS + C.KR_TICKERS:
        sub = win[win["ticker"] == t]
        rw = sub[sub["model"] == "random_walk"].set_index("k")["ncrps"]
        for m in models:
            g = sub[sub["model"] == m].set_index("k")
            r = {"ticker": t, "model": m, "n_windows": len(g), "ncrps": g["ncrps"].mean(),
                 "skill_vs_rw": 1 - g["ncrps"].mean() / rw.mean(), "cov90": g["k_cov"].sum() / g["n"].sum()}
            if m != "random_walk":
                r["p_block_t_exploratory"] = block_t((g["ncrps"] - rw).values)[1]
            rows.append(r)
    t6 = pd.DataFrame(rows)
    t6.to_csv(C.TABLES / "T6_market_per_asset_exploratory.csv", index=False)
    rep.append("## T6. 종목별 분해 (탐색적, 다중비교 보정 없음)\n")
    rep.append(t6.to_markdown(index=False, floatfmt=".4f") + "\n")

    ms = ml[ml["scenario"] == "market_stream"]
    if not ms.empty:
        s = ms.groupby("model").agg(ncrps=("rel_crps", "mean"), cov90=("cov90", "mean")).reset_index()
        s.to_csv(C.TABLES / "T6b_market_stream_descriptive.csv", index=False)
        rep.append("## T6b. 최근 100거래일 연속 구간(서술용, 검정 없음)\n")
        rep.append(s.to_markdown(index=False, floatfmt=".4f") + "\n")


# ------------------------------------------------------------------ H5 사후보정
def calibration(cl, rep):
    cl = cl.copy()
    den = np.maximum(np.abs(cl["y_true"]), 1e-8)
    a = C.ACI_ALPHA
    for mth in ["raw", "qaci", "cqr", "const"]:
        lo, hi = cl[f"{mth}_lo"], cl[f"{mth}_hi"]
        y = cl["y_true"]
        cl[f"{mth}_in"] = ((lo <= y) & (y <= hi)).astype(int)
        cl[f"{mth}_rw"] = (hi - lo) / den * 100
        cl[f"{mth}_ris"] = ((hi - lo) + 2 / a * np.maximum(lo - y, 0) + 2 / a * np.maximum(y - hi, 0)) / den * 100
    sc = cl["scenario"]
    parts = cl["series_id"].str.split("_")
    cl["cluster"] = np.where(sc.str.startswith("synth_"), parts.str[2],
                             np.where(sc == "market_panel", parts.str[2], parts.str[1] + "_" + parts.str[2]))
    rows = []
    for (m, s), g in cl.groupby(["model", "scenario"]):
        cg = g.groupby("cluster")
        r = {"model": m, "scenario": s, "n_clusters": cg.ngroups, "const_ratio": g["const_ratio"].iloc[0]}
        for mth in ["raw", "qaci", "cqr", "const"]:
            agg = cg[f"{mth}_in"].agg(["sum", "size"])
            b = boot_ratio(agg["sum"], agg["size"], levels=(0.95, 0.90))
            r[f"{mth}_cov"], r[f"{mth}_lo95"], r[f"{mth}_hi95"] = b["est"], b["lo95"], b["hi95"]
            r[f"{mth}_lo90"], r[f"{mth}_hi90"] = b["lo90"], b["hi90"]
            r[f"{mth}_relwidth"] = g[f"{mth}_rw"].mean()
            r[f"{mth}_relIS"] = g[f"{mth}_ris"].mean()
            r[f"{mth}_equiv"] = (b["lo90"] >= 0.90 - C.EQUIV_MARGIN) and (b["hi90"] <= 0.90 + C.EQUIV_MARGIN)
            r[f"{mth}_ci95_has_090"] = b["lo95"] <= 0.90 <= b["hi95"]
        dd = (g["cqr_ris"] - g["const_ris"]).groupby(g["cluster"]).mean().values
        e, lo, hi = boot_mean(dd)
        r.update({"IS_cqr_minus_const": e, "IS_diff_lo": lo, "IS_diff_hi": hi,
                  "IS_improve_vs_raw": 1 - r["cqr_relIS"] / r["raw_relIS"]})
        rows.append(r)
    t7 = pd.DataFrame(rows)
    t7.to_csv(C.TABLES / "T7_H5_calibration_all.csv", index=False)

    rep.append("## T7. H5 사후보정 — 전 시나리오·전 모델 (선별 보고 없음)\n")
    rep.append(f"'복원' = 커버리지 90% CI가 [{0.90-C.EQUIV_MARGIN:.2f}, {0.90+C.EQUIV_MARGIN:.2f}] 안(동등성). "
               "클러스터: 합성=시계열, 패널=날짜, 스트림=윈도우(독립 아님).\n")
    show = t7.assign(raw=[fmt_ci(r.raw_cov, r.raw_lo95, r.raw_hi95) for r in t7.itertuples()],
                     qaci=[fmt_ci(r.qaci_cov, r.qaci_lo95, r.qaci_hi95) for r in t7.itertuples()],
                     cqr=[fmt_ci(r.cqr_cov, r.cqr_lo95, r.cqr_hi95) for r in t7.itertuples()],
                     const=[fmt_ci(r.const_cov, r.const_lo95, r.const_hi95) for r in t7.itertuples()],
                     IS_diff=[fmt_ci(r.IS_cqr_minus_const, r.IS_diff_lo, r.IS_diff_hi, pct=False, d=3) for r in t7.itertuples()])
    rep.append(show[["model", "scenario", "raw", "qaci", "cqr", "cqr_equiv", "const", "const_ratio",
                     "IS_diff", "IS_improve_vs_raw"]].to_markdown(index=False, floatfmt=".3f") + "\n")
    syn = t7[t7["scenario"].str.startswith("synth_") & t7["model"].isin(C.TSFM)]
    if len(syn):
        rep.append(f"합성 15개 시나리오 x TSFM: 복원(동등성) 통과 — raw {int(syn['raw_equiv'].sum())}/{len(syn)}, "
                   f"Step1 {int(syn['qaci_equiv'].sum())}/{len(syn)}, Step2 {int(syn['cqr_equiv'].sum())}/{len(syn)}\n")


# ------------------------------------------------------------------ 실행 기록
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def manifest(res_dir):
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=C.ROOT, text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "src_v3"], cwd=C.ROOT, text=True).strip()
    except Exception:
        head, dirty = None, "git 사용 불가"
    info = {"git_head": head, "src_v3_uncommitted_changes": dirty,
            "data_sha256": {k: sha(v) for k, v in C.MARKET_FILES.items()},
            "synthetic_manifest_sha256": sha(C.DATA_SYN / "_manifest.csv"),
            "config": {k: (v if isinstance(v, (int, float, str, list, tuple, dict)) else str(v))
                       for k, v in vars(C).items() if k.isupper()}}
    (res_dir / "run_manifest.json").write_text(json.dumps(info, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def main(res_dir):
    C.TABLES = res_dir / "tables"
    C.TABLES.mkdir(parents=True, exist_ok=True)
    ml = pd.read_parquet(res_dir / "metrics_long.parquet")
    ml["ticker"] = ml["ticker"].astype(str)
    rep = ["# v3 사전등록 분석 결과 (자동 생성 — 손으로 고치지 말 것)\n"]
    synthetic(ml, rep)
    market(ml, rep)
    cp = res_dir / "calibrated_long.parquet"
    if cp.exists():
        calibration(pd.read_parquet(cp), rep)
    (C.TABLES / "v3_report.md").write_text("\n".join(rep), encoding="utf-8")
    manifest(res_dir)
    print(f"[저장] {C.TABLES / 'v3_report.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    main(C.ROOT / ("results_v3_smoke" if a.smoke else "results_v3"))
