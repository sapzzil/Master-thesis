# -*- coding: utf-8 -*-
"""
post_b_checks_v4.py — 추가 점검 b1~b3 (CPU, 새 예측 없음). 본문 표의 결과 파일만 읽는다.
  b1: 합성 L1 커버리지와 실제 커버리지의 대응 — 상관(전체, TimesFM 1년·가격 제외), 평균 절대 차이,
      '모든 조건을 80%로 예측'하는 단순 기준의 평균 절대 차이
  b2: 모델 공개 이후 기간의 기준 모형(RW, GARCH-t) 커버리지 (표 5-3의 같은 기간과 대조)
  b3: 종목·달력 월별 실현 변동성 5분위로 나눈 보정 전후 커버리지(연속 보정, 실제 10종목)
입력: results_v4_t5fix/tables/T1_synth_scenarios.csv, T6_real_coverage_H5.csv,
      results_v4_t5fix_econ/real_all.parquet (src_v4_econ/econ_v4.py 산출물, git 제외)
출력: results_v4_post/b1_correspondence.csv, b2_post_release_baselines.csv, b3_vol_quintile.csv
실행: python post_b_checks_v4.py
"""
from pathlib import Path

from scipy import stats

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "results_v4_t5fix" / "tables"
RA = ROOT / "results_v4_t5fix_econ" / "real_all.parquet"
OUT = ROOT / "results_v4_post"
RELEASE = {"chronos_t5_base": "2024-04-01", "chronos2": "2025-11-01", "timesfm25": "2025-10-01",
           "moirai2": "2025-09-01"}


def b1():
    t1 = pd.read_csv(TAB / "T1_synth_scenarios.csv")
    t6 = pd.read_csv(TAB / "T6_real_coverage_H5.csv")
    syn = t1[t1["scenario"] == "L1"][["model", "L", "input", "cov"]]
    real = t6[t6["panel"] == "ALL"][["model", "L", "input", "cov"]]
    j = syn.merge(real, on=["model", "L", "input"], suffixes=("_syn", "_real"))
    j = j[j["model"] != "oracle"]
    s, r = j["cov_syn"].to_numpy() * 100, j["cov_real"].to_numpy() * 100
    out = j[~((j.model == "timesfm25") & (j.L == 252) & (j.input == "price"))]
    s2, r2 = out["cov_syn"].to_numpy() * 100, out["cov_real"].to_numpy() * 100
    def row(name, a, b):
        e1, e0 = np.abs(a - b), np.abs(b - 80)
        return {"set": name, "n": len(a), "corr": np.corrcoef(a, b)[0, 1], "mad_l1": e1.mean(), "max_l1": e1.max(),
                "mad_80": e0.mean(), "l1_closer": int((e1 < e0).sum()), "wilcoxon_p": stats.wilcoxon(e1, e0).pvalue}
    res = pd.DataFrame([row("전체", s, r), row("TimesFM 1년·가격 제외", s2, r2)])
    res.to_csv(OUT / "b1_correspondence.csv", index=False, encoding="utf-8-sig")
    print("[b1]\n" + res.round(3).to_string(index=False))


def scored_real():
    d = pd.read_parquet(RA)
    d["date"] = pd.to_datetime(d["date"])
    d = d.sort_values(["model", "L", "input", "unit", "date"])
    g = d.groupby(["model", "L", "input", "unit"])
    d["k"] = g.cumcount() + 20                       # real_all은 종목별 첫 20일(준비 기간)이 빠져 있음
    d["ntot"] = g["k"].transform("max") + 1
    d["day"] = d["k"] % 80 + 1
    d["in_main"] = (d["k"] // 80) < (d["ntot"] // 80)
    return d


def b2(d):
    s = d[d["in_main"] & (d["day"] > 20)].copy()
    s["cover"] = (s["y"] >= s["q1"]) & (s["y"] <= s["q9"])
    rows = []
    for m, L in [("rw", 21), ("rw", 252), ("garch_t", 252)]:
        a = s[(s["model"] == m) & (s["L"] == L)]
        for tsfm, d0 in RELEASE.items():
            b = a[a["date"] >= d0]
            rows.append({"baseline": m, "L": L, "after": d0, "for_model": tsfm, "n": len(b),
                         "cov_full": a["cover"].mean() * 100, "cov_after": b["cover"].mean() * 100})
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "b2_post_release_baselines.csv", index=False, encoding="utf-8-sig")
    print("[b2]\n" + res.round(2).to_string(index=False))


def b3(d):
    d = d.copy()
    d["ym"] = d["date"].dt.to_period("M")
    ref = d[(d["model"] == "rw") & (d["L"] == 21)]
    mv = ref.groupby(["unit", "ym"])["y"].std().rename("mvol").reset_index()
    mv["q"] = pd.qcut(mv["mvol"], 5, labels=[1, 2, 3, 4, 5])
    d = d.merge(mv[["unit", "ym", "q"]], on=["unit", "ym"])
    d["c0"] = (d["y"] >= d["q1"]) & (d["y"] <= d["q9"])
    d["c1"] = (d["y"] >= d["cal_lo"]) & (d["y"] <= d["cal_hi"])
    res = d.groupby(["model", "L", "input", "q"], observed=True)[["c0", "c1"]].mean().mul(100).reset_index()
    res = res.rename(columns={"c0": "cov_raw", "c1": "cov_cal"})
    res.to_csv(OUT / "b3_vol_quintile.csv", index=False, encoding="utf-8-sig")
    cut = mv.groupby("q", observed=True)["mvol"].agg(["min", "max"]).mul(100)
    print("[b3] 5분위 경계(일별 표준편차 %)\n" + cut.round(2).to_string())
    p = res.pivot_table(index=["model", "L", "input"], columns="q", values=["cov_raw", "cov_cal"], observed=True)
    gap0 = p[("cov_raw", 1)] - p[("cov_raw", 5)]
    gap1 = p[("cov_cal", 1)] - p[("cov_cal", 5)]
    print(f"저변동−고변동 차이(%p): 보정 전 {gap0.min():.1f}~{gap0.max():.1f}(평균 {gap0.mean():.1f}), "
          f"보정 후 {gap1.min():.1f}~{gap1.max():.1f}(평균 {gap1.mean():.1f})")
    print(p.round(1).to_string())


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    b1()
    d = scored_real()
    b2(d)
    b3(d)
